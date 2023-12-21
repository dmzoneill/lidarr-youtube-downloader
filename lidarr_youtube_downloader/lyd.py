#!/usr/bin/env python3
import importlib.util
import os
import re
import signal
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from difflib import SequenceMatcher
from os.path import exists
from typing import Optional

import eyed3
import requests
import typer
from youtubesearchpython import VideosSearch

endpoint = None
api_key = None
lidarr_db = None
music_path = None
stop = False
headers = None
seen = []


def get_view_path():
    if os.path.exists("./view"):
        return ""

    submodule_search_locations = importlib.util.find_spec(
        "lidarr_youtube_downloader"
    ).submodule_search_locations
    if len(submodule_search_locations) == 1:
        return submodule_search_locations[0] + "/"
    else:
        if "site-packages" in submodule_search_locations[0]:
            return submodule_search_locations[0] + "/"
        else:
            return submodule_search_locations[1] + "/"


def save_seen():
    global seen

    with open("seen", "w+") as fp:
        fp.writelines("\n".join(seen))


def load_seen():
    global seen

    try:
        with open("seen", "r") as fp:
            seen = fp.read().splitlines()
    except:
        seen = []


def rescan(path):
    data = {"name": "RescanFolders", "folders": [path]}
    requests.post(endpoint + "/api/v1/command", json=data, headers=headers)

    data = {"name": "DownloadedAlbumsScan", "path": path, "folders": [path]}
    requests.post(endpoint + "/api/v1/command", json=data, headers=headers)


def output(**kwargs):
    template = ""
    try:
        with open(get_view_path() + "view/" + kwargs["template"]) as file:
            template = file.read()
            print(template.format(**kwargs))
    except KeyError as error:
        print("    Key error, you need to fix the template")
        print("    " + str(error))
        print("    " + template)


def format(input):
    stdio = input.decode("utf-8")
    stdio = stdio.splitlines()
    stdio = [re.sub("^", "        ", x) for x in stdio]
    stdio = "\n".join(stdio)
    return stdio


def ffmpeg_encode_mp3(path, artist, title, album, year, trackNumber, genre):
    command = 'ffmpeg -y -i "{input}"'
    command += ' -metadata artist="{artist}"'
    command += ' -metadata year="{year}"'
    command += ' -metadata title="{title}"'
    command += ' -metadata album="{album}"'
    command += ' -metadata track="{trackNumber}"'
    command += ' -metadata genre="{genre}"'
    command += " -hide_banner"
    command += ' "{output}.mp3"'
    command = command.format(
        input=path.replace('"', '\\"'),
        artist=artist.replace('"', '\\"'),
        title=title.replace('"', '\\"'),
        year=year,
        album=album.replace('"', '\\"'),
        trackNumber=trackNumber,
        genre=genre.replace('"', '\\"'),
        output=path.replace('"', '\\"'),
    )

    output(
        template="ffmpeg",
        input=path.replace('"', '\\"'),
        artist=artist.replace('"', '\\"'),
        title=title.replace('"', '\\"'),
        year=year,
        album=album.replace('"', '\\"'),
        track=trackNumber,
        genre=genre.replace('"', '\\"'),
        output=path.replace('"', '\\"'),
    )

    proc = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    res = proc.communicate()

    result = ""

    if proc.returncode == 0:
        os.remove(path)
        os.rename(path + ".mp3", path)
        result = "ffmpeg added mp3 tag" + "\n\n" + format(res[0])
    else:
        os.remove(path + ".mp3")
        result = "ffmpeg failed adding tag" + "\n\n" + format(res[1])

    output(template="ffmpeg_result", result=result.replace("\n", "        \n"))


def update_mp3tag(
    artistName, albumName, title, trackNumber, trackTotal, year, disc, discTotal, genre
):
    path = music_path + "/" + artistName + "/" + albumName
    filePath = path + "/" + artistName + " - "
    filePath += albumName + " - " + title + ".mp3"

    file_exists = exists(filePath)

    if file_exists is False:
        output(template="tagging", result="File does not exist")
        return False

    try:
        audiofile = eyed3.load(filePath)

        if audiofile is None:
            ffmpeg_encode_mp3(
                filePath, artistName, title, albumName, year, trackNumber, genre
            )
            audiofile = eyed3.load(filePath)
            if audiofile is None:
                output(template="tagging", result="Failed adding tag")
                return False

        if audiofile.tag is None:
            audiofile.initTag()
            audiofile.tag.clear()

            audiofile.tag.artist = artistName
            audiofile.tag.album = albumName
            audiofile.tag.title = title
            audiofile.tag.track_num = trackNumber
            if trackTotal:
                audiofile.tag.track_total = trackTotal
            audiofile.tag.year = year
            audiofile.tag.disc_num = disc
            if discTotal:
                audiofile.tag.disc_total = discTotal
            audiofile.tag.genre = genre
            audiofile.tag.save()
            output(template="tagging", result="Updated tag")
            return True
    except Exception as e:
        output(template="tagging", result="Not updated, corrupt " + str(e))
        os.remove(filePath)
        return False


def add_lidarr_trackfile(con, cur, album_id, filePath, artistName, albumName):
    # insert
    filesize = os.path.getsize(filePath)
    taglib = '{"quality": 2, "revision": {"version": 1, '
    taglib += '"real": 0, "isRepack": false }, '
    taglib += '"qualityDetectionSource": "tagLib"}'
    quality = '{"audioFormat": "MPEG Version 1 Audio, Layer 3 VBR",'
    quality += '"audioBitrate": 154, "audioChannels": 2, "audioBits": 0,'
    quality += '"audioSampleRate": 44100}'
    screenname = artistName + " " + albumName

    query = "INSERT INTO TrackFiles "
    query += "(AlbumId, Quality, Size, SceneName, DateAdded, "
    query += "ReleaseGroup, MediaInfo, Modified, Path)"
    query += " VALUES(?, ?, ?, ?, ?, NULL, ?, ?, ?)"
    cur.execute(
        query,
        (
            album_id,
            taglib,
            filesize,
            screenname,
            datetime.now(),
            quality,
            datetime.now(),
            filePath,
        ),
    )
    con.commit()
    output(template="lidarr", result="Updated the db")
    return cur.lastrowid


def set_lidarr_track_trackfield(con, cur, TrackFileId, track_id):
    # update
    cur.execute(
        "UPDATE Tracks SET TrackFileId=? WHERE id = ?",
        (
            track_id,
            TrackFileId,
        ),
    )
    con.commit()


def get_lidarr_album_id(cur, albumName, year):
    cur.execute(
        "SELECT id FROM Albums WHERE Title LIKE ? and ReleaseDate like ?",
        (
            "%" + albumName + "%",
            year + "%",
        ),
    )
    result = cur.fetchall()
    if len(result) == 0:
        return -1
    return result[0][0]


def get_lidarr_trackfile_id(cur, filePath):
    cur.execute("SELECT id FROM TrackFiles WHERE Path = ?", (filePath,))
    result = cur.fetchall()
    if len(result) == 0:
        return -1
    return result[0][0]


def get_lidarr_track_ids(cur, artist, album, track):
    sql = """
        select Tracks.Id from ArtistMetadata, Artists, Tracks, Albums, AlbumReleases
        where ArtistMetadata.id = Artists.ArtistMetadataId
        and Artists.ArtistMetadataId = Tracks.ArtistMetadataId
        and Tracks.AlbumReleaseId = AlbumReleases.Id
        and Albums.id = AlbumReleases.AlbumId
        and ArtistMetadata.Name = ?
        and AlbumReleases.Title = ?
        and Tracks.Title = ?
    """
    # get track id
    cur.execute(
        sql,
        (
            artist,
            album,
            track,
        ),
    )
    result = cur.fetchall()
    if len(result) == 0:
        return -1
    return [X[0] for X in result]


def update_lidarr_db(artistName, albumName, title, trackNumber, year):
    global lidar_db, music_path

    path = music_path + "/" + artistName + "/" + albumName
    filePath = path + "/" + artistName + " - " + albumName
    filePath += " - " + title + ".mp3"

    con = sqlite3.connect(lidar_db)
    cur = con.cursor()

    album_id = get_lidarr_album_id(cur, albumName, year)
    trackfile_id = get_lidarr_trackfile_id(cur, filePath)

    if trackfile_id == -1:
        add_lidarr_trackfile(con, cur, album_id, filePath, artistName, albumName)

    track_ids = get_lidarr_track_ids(cur, artistName, albumName, title)
    trackfile_id = get_lidarr_trackfile_id(cur, filePath)

    if track_ids == -1:
        con.close()
        return

    for x in track_ids:
        set_lidarr_track_trackfield(con, cur, trackfile_id, x)

    con.close()

    output(
        template="lidarrdb_update",
        result="Updated {artist} - {albumName} - {title}".format(
            artist=artistName, albumName=albumName, title=title
        ),
    )


def skip_youtube_download(link):
    try:
        with open(".skip", "r") as file_object:
            lines = file_object.readlines()
            file_object.close()
            for line in lines:
                if link.strip() == line.strip():
                    return True
    except Exception:
        return False
    return False


def append_to_skip_file(link):
    with open(".skip", "a+") as file_object:
        file_object.seek(0)
        data = file_object.read(100)
        if len(data) > 0:
            file_object.write("\n")
        file_object.write(link)


def get_song(
    artistName, albumName, title, trackNumber, trackTotal, year, disc, discTotal, genre
):

    artistName = artistName.replace("/", "+")
    title = title.replace("/", "")
    albumName = albumName.replace("/", "+")
    albumName = albumName.replace("\\", "")

    best = 0
    bestLink = ""
    bestTitle = ""
    searchFor = artistName + " - " + title
    path = music_path + "/" + artistName + "/" + albumName
    filePath = path + "/" + artistName + " - " + albumName
    filePath += " - " + title + ".mp3"
    os.makedirs(path, exist_ok=True)

    if os.path.exists(filePath):
        update_mp3tag(
            artistName,
            albumName,
            title,
            trackNumber,
            trackTotal,
            year,
            disc,
            discTotal,
            genre,
        )
        update_lidarr_db(artistName, albumName, title, trackNumber, year)
        rescan(path)
        return

    result = ""

    try:
        videosSearch = VideosSearch(searchFor)

        if videosSearch is None:
            result = "Failed searching youtube"
            return

        for song in videosSearch.result()["result"]:
            if SequenceMatcher(None, searchFor, song["title"]).ratio() > best:
                if skip_youtube_download(song["link"]) is False:
                    best = SequenceMatcher(None, searchFor, song["title"]).ratio()
                    bestLink = song["link"]
                    bestTitle = song["title"]
    except:
        return

    result = "Best match: " + str(best)

    if best < 0.8:
        result = "Unable to find " + searchFor
        return

    result = "Selected " + bestLink

    output(template="youtube-search", match=str(best), title=bestTitle, result=result)

    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    downloader = "yt-dlp --no-progress -x"
    downloader += ' --audio-format mp3 "{link}" -o '
    downloader = downloader.format(link=bestLink)
    downloader += '"{trackname}"'.format(trackname=filePath.replace('"', '\\"'))

    output(template="yt-dlp", link=bestLink, output=filePath)

    proc = subprocess.Popen(
        downloader, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    res = proc.communicate()

    if proc.returncode == 0:
        output(
            template="yt-dlp_result",
            result="Downloaded successfully" + "\n\n" + format(res[0]),
        )

        tagged = update_mp3tag(
            artistName,
            albumName,
            title,
            trackNumber,
            trackTotal,
            year,
            disc,
            discTotal,
            genre,
        )

        if tagged:
            update_lidarr_db(artistName, albumName, title, trackNumber, year)
            rescan(path)
        else:
            append_to_skip_file(bestLink)
    else:
        output(
            template="yt-dlp_result",
            result="Download failed" + "\n\n" + format(res[1]),
        )
        append_to_skip_file(bestLink)


def iterate_tracks(tracks, album, totalRecords, record_counter, artist_filter):
    global seen
    track_no = 1
    track_total = len(tracks)

    for track in tracks:
        if stop:
            sys.exit(0)

        date = album["releaseDate"][0:4]
        genre = album["genres"][0] if len(album["genres"]) > 0 else ""

        if artist_filter is not None:
            if (
                SequenceMatcher(
                    None, artist_filter, album["artist"]["artistName"]
                ).ratio()
                < 0.8
            ):
                continue

        full_trackname = album["artist"]["artistName"]
        full_trackname += " - " + album["title"] + " - "
        full_trackname += track["title"]

        if full_trackname in seen:
            track_no += 1
            continue

        output(
            template="missing",
            record_total=str(totalRecords),
            record_num=str(record_counter),
            path=album["artist"]["path"],
            artist=album["artist"]["artistName"],
            track=track["title"],
            date=date,
            album=album["title"],
            trackNumber=track["trackNumber"],
            genre=genre,
            cd_count=album["mediumCount"],
            cd_num=track["mediumNumber"],
            track_no=track["trackNumber"],
            track_count=str(len(track)),
            track_counter=str(track_no),
            track_total=str(track_total),
        )

        get_song(
            album["artist"]["artistName"],
            album["title"],
            track["title"],
            track["trackNumber"],
            len(track),
            date,
            track["mediumNumber"],
            album["mediumCount"],
            genre,
        )

        seen.append(full_trackname)
        save_seen()

        track_no += 1


def iterate_records(records, totalRecords, record_counter, artist_filter):
    global endpoint, headers
    for album in records:
        url = endpoint + "/api/v1/track?artistid=" + str(album["artist"]["id"])
        url += "&albumid=" + str(album["id"])
        tracksRequest = requests.get(url, headers=headers)

        if tracksRequest.status_code != 200:
            continue

        iterate_tracks(
            tracksRequest.json(), album, totalRecords, record_counter, artist_filter
        )
        record_counter += 1


def iterate_missing(artist_filter, iterative):
    global stop, endpoint, api_key, lidar_db, music_path, headers
    page_num = 0

    def signal_handler(sig, frame):
        global stop
        print("Cancelling after current track, standby..")
        stop = True

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        if stop:
            sys.exit(0)

        url = endpoint + "/api/v1/wanted/missing?page="
        url += str(page_num) + "&pageSize=50&sortDirection=descending"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            continue

        json = response.json()
        totalRecords = json["totalRecords"]
        record_counter = 1 + (page_num * 50)

        if totalRecords == 0:
            if iterative:
                stop = True
            time.sleep(3600)
            print("No more records, waiting 1 hr")
            continue

        if "records" not in json or len(json["records"]) == 0:
            if iterative:
                stop = True
            page_num = 0
            print("Sleeping 60 seconds")
            time.sleep(60)

        iterate_records(json["records"], totalRecords, record_counter, artist_filter)
        page_num += 1


app = typer.Typer()


@app.command()
def run(
    artist: Optional[str] = None,
    stop: Optional[str] = None,
    url: Optional[str] = os.environ.get("LIDARR_URL", "http://127.0.0.1:8686"),
    key: Optional[str] = os.environ.get(
        "LIDARR_API_KEY", "771de60596e946f6b3e5e6f5fb6fd729"
    ),
    db: Optional[str] = os.environ.get(
        "LIDARR_DB", "/home/dave/src/docker-media-center/config/lidarr/lidarr.db"
    ),
    path: Optional[str] = os.environ.get("LIDARR_MUSIC_PATH", "/music"),
):
    global endpoint, api_key, lidar_db, music_path, headers
    endpoint = url
    api_key = key
    lidar_db = db
    music_path = path
    headers = {"X-Api-Key": api_key}
    load_seen()

    iterative = True if stop is not None else False
    iterate_missing(artist, iterative)


if __name__ == "__main__":
    print("Starting Lidarr Youtube Downloader")
    app()
