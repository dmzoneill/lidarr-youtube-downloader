#!/usr/bin/env python3
import eyed3
import os
import requests
import signal
import subprocess
import sqlite3
import sys
import time
from datetime import datetime
from difflib import SequenceMatcher
from os.path import exists
from youtubesearchpython import VideosSearch


endpoint = os.environ.get('LIDARR_URL', "http://127.0.0.1:8686")
api_key = os.environ.get('LIDARR_API_KEY', "771de60596e946f6b3e5e6f5fb6fd729")
lidar_db = os.environ.get(
    'LIDARR_DB',
    "/home/dave/src/docker-media-center/config/lidarr/lidarr.db")
music_path = os.environ.get('LIDARR_MUSIC_PATH', "/music")
stop = False


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def rescan(path):
    data = {
        'name': 'RescanFolders',
        'folders': [path]
    }
    requests.post(
        endpoint +
        "/api/v1/command",
        json=data,
        headers={
            "X-Api-Key": api_key})
    data = {
        'name': 'DownloadedAlbumsScan',
        'path': path,
        'folders': [path]
    }
    requests.post(
        endpoint +
        "/api/v1/command",
        json=data,
        headers={
            "X-Api-Key": api_key})


def ffmpeg_reencode_mp3(path, artist, title, album, year, trackNumber, genre):
    ffmpeg = " -metadata artist=\"{artist}\""
    ffmpeg += " -metadata year=\"{year}\""
    ffmpeg += " -metadata title=\"{title}\""
    ffmpeg += " -metadata album=\"{album}\""
    ffmpeg += " -metadata track=\"{trackNumber}\""
    ffmpeg += " -metadata genre=\"{genre}\""
    ffmpeg += " -hide_banner -loglevel error"
    ffmpeg = ffmpeg.format(path=path.replace('"', '\\"'),
                           artist=artist.replace('"', '\\"'),
                           title=title.replace('"', '\\"'),
                           year=year,
                           album=album.replace('"', '\\"'),
                           trackNumber=trackNumber,
                           genre=genre.replace('"', '\\"'),
                           )

    print("")
    print("ffmpeg")
    print("=" * 40)
    print("ffmpeg -i \"{path}\"".format(path=path))
    print(" " + ffmpeg.replace(" -", "\n -").lstrip())
    print(" \"{path}\"".format(path=path))
    ffmpeg += " \"{path}.mp3\"".format(path=path.replace('"', '\\"'))
    ffmpeg = "ffmpeg -y -i \"{path}\"".format(path=path) + ffmpeg
    print("")

    proc = subprocess.Popen(ffmpeg, shell=True, stdout=subprocess.DEVNULL)
    proc.wait()

    if proc.returncode == 0:
        os.remove(path)
        os.rename(path + ".mp3", path)
        print("Added mp3 tag")
    else:
        print("Failed adding tag")    


def update_mp3tag(
        artistName,
        albumName,
        title,
        trackNumber,
        trackTotal,
        year,
        disc,
        discTotal,
        genre):
    path = music_path + "/" + artistName + "/" + albumName
    filePath = path + "/" + artistName + " - "
    filePath += albumName + " - " + title + ".mp3"

    file_exists = exists(filePath)

    if file_exists:
        try:
            audiofile = eyed3.load(filePath)

            if audiofile is None:
                ffmpeg_reencode_mp3(
                    filePath,
                    artistName,
                    title,
                    albumName,
                    year,
                    trackNumber,
                    genre)
                audiofile = eyed3.load(filePath)
                if audiofile is None:
                    print("Failed adding tag")
                    print("")
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
                print("Updated tag")
                print("")
                return True
        except Exception as e:
            print("Not updated, corrupt " + str(e))
            print("")
            os.remove(filePath)
            return False
    else:
        print("File does not exist")
        print("")
        return False


def add_lidarr_trackfile(cur, album_id, filePath, artistName, albumName):
    # insert
    filesize = os.path.getsize(filePath)
    taglib = "{\"quality\": 2, \"revision\": {\"version\": 1, "
    taglib += "\"real\": 0, \"isRepack\": false }, "
    taglib += "\"qualityDetectionSource\": \"tagLib\"}"
    quality = "{\"audioFormat\": \"MPEG Version 1 Audio, Layer 3 VBR\","
    quality += "\"audioBitrate\": 154, \"audioChannels\": 2, \"audioBits\": 0,"
    quality += "\"audioSampleRate\": 44100}"
    screenname = artistName + " " + albumName

    query = "INSERT INTO TrackFiles "
    query += "(AlbumId, Quality, Size, SceneName, DateAdded, "
    query += "ReleaseGroup, MediaInfo, Modified, Path)"
    query += " VALUES(?, ?, ?, ?, ?, NULL, ?, ?, ?)"
    cur.execute(
        query,
        (album_id,
         taglib,
         filesize,
         screenname,
         datetime.now(),
         quality,
         datetime.now(),
         filePath,
         ))
    print("Updated the db")
    return cur.lastrowid


def set_lidarr_track_trackfield(cur, TrackFileId, track_id):
    # update
    cur.execute("UPDATE Tracks SET TrackFileId=? WHERE id = ?",
                (track_id, TrackFileId,))


def get_lidarr_album_id(cur, albumName, year):
    cur.execute(
        "SELECT id FROM Albums WHERE Title LIKE ? and ReleaseDate like ?",
        ('%' +
         albumName +
         '%',
         year +
         '%',
         ))
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


def get_lidarr_track_id(cur, title, trackNumber):
    # get track id
    cur.execute(
        "SELECT id FROM Tracks WHERE Title LIKE ? and TrackNumber=? LIMIT 1;",
        ('%' +
         title +
         '%',
         trackNumber,
         ))
    result = cur.fetchall()
    if len(result) == 0:
        return -1
    return result[0][0]


def update_lidarr_db(artistName, albumName, title, trackNumber, year):
    path = music_path + "/" + artistName + "/" + albumName
    filePath = path + "/" + artistName + " - " + albumName
    filePath += " - " + title + ".mp3"

    con = sqlite3.connect(lidar_db)
    cur = con.cursor()

    album_id = get_lidarr_album_id(cur, albumName, year)
    trackfile_id = get_lidarr_trackfile_id(cur, filePath)

    if trackfile_id == -1:
        add_lidarr_trackfile(cur, album_id, filePath, artistName, albumName)

    track_id = get_lidarr_track_id(cur, title, trackNumber)
    trackfile_id = get_lidarr_trackfile_id(cur, filePath)

    set_lidarr_track_trackfield(cur, trackfile_id, track_id)

    con.close()


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
        artistName,
        albumName,
        title,
        trackNumber,
        trackTotal,
        year,
        disc,
        discTotal,
        genre):
    best = 0
    bestLink = ""
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
            genre)
        update_lidarr_db(artistName, albumName, title, trackNumber, year)
        rescan(path)
        return

    print("youtube search")
    print("=" * 40)

    videosSearch = VideosSearch(searchFor)

    if videosSearch is None:
        print("Failed searching youtube")
        return

    for song in videosSearch.result()['result']:
        if similar(searchFor, song['title']) > best:
            if skip_youtube_download(song['link']) is False:
                best = similar(searchFor, song['title'])
                bestLink = song['link']

    print("Best match: " + str(best))

    if best < 0.8:
        print("Unable to find " + searchFor)
        return

    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    downloader = "youtube-dl --no-progress -x"
    downloader += " --audio-format mp3 \"{link}\" -o "
    downloader = downloader.format(link=bestLink)

    print("")
    print("youtube-dl")
    print("=" * 40)
    print(downloader.replace(" -", "\n -"))
    downloader += "\"{trackname}\"".format(
        trackname=filePath.replace(
            '"',
            '\\"'))
    print(" \"{trackname}\"".format(trackname=filePath.replace('"', '\\"')))

    proc = subprocess.Popen(downloader, shell=True, stdout=subprocess.PIPE)
    proc.wait()

    if proc.returncode == 0:
        print("Downloaded successfully")
        tagged = update_mp3tag(
            artistName,
            albumName,
            title,
            trackNumber,
            trackTotal,
            year,
            disc,
            discTotal,
            genre)        
        if tagged:
            update_lidarr_db(artistName, albumName, title, trackNumber, year)
            rescan(path)
        else:
            append_to_skip_file(bestLink)
    else:
        append_to_skip_file(bestLink)


def get_missing():
    global stop
    page_num = 0
    counter = 1

    def signal_handler(sig, frame):
        global stop
        print("Cancelling after current track, standby..")
        stop = True

    signal.signal(signal.SIGINT, signal_handler)

    while True:
        response = requests.get(
            endpoint +
            "/api/v1/wanted/missing?page=" +
            str(page_num) +
            "&pageSize=50",
            headers={
                "X-Api-Key": api_key})
        if response.status_code != 200:
            continue
        json = response.json()

        if 'records' not in json or len(json['records']) == 0:
            page_num = 0
            time.sleep(60)

        for album in json['records']:
            tracksRequest = requests.get(endpoint +
                                         "/api/v1/track?artistid=" +
                                         str(album['artist']['id']) +
                                         "&albumid=" +
                                         str(album['id']),
                                         headers={"X-Api-Key": api_key})
            if tracksRequest.status_code != 200:
                continue

            tracks = tracksRequest.json()

            for track in tracks:
                if stop:
                    sys.exit(0)

                date = album['releaseDate'][0:4]
                genre = album['genres'][0] if len(album['genres']) > 0 else ""

                print("")
                print(counter)
                print("=" * 80)
                print(
                    "{key}: {val}".format(
                        key='{:15}'.format('Path'),
                        val=album['artist']['path']))
                print(
                    "{key}: {val}".format(
                        key='{:15}'.format('Artist'),
                        val=album['artist']['artistName']))
                print(
                    "{key}: {val}".format(
                        key='{:15}'.format('Album'),
                        val=album['title']))
                print(
                    "{key}: {val}".format(
                        key='{:15}'.format('Track'),
                        val=track['title']))
                print(
                    "{key}: {val}".format(
                        key='{:15}'.format('Genre'),
                        val=genre))
                print(
                    "{key}: {val}".format(
                        key='{:15}'.format('Date'),
                        val=date))
                print(
                    "{key}: {val}".format(
                        key='{:15}'.format('CD Count'),
                        val=album['mediumCount']))
                print(
                    "{key}: {val}".format(
                        key='{:15}'.format('CD No'),
                        val=track['mediumNumber']))
                print("{key}: {val}".format(key='{:15}'.format('Track No'),
                      val=track['trackNumber'] + "/" + str(len(track))))

                print("")

                get_song(album['artist']['artistName'],
                         album['title'],
                         track['title'],
                         track['trackNumber'],
                         len(track),
                         date,
                         track['mediumNumber'],
                         album['mediumCount'],
                         genre)

                counter += 1
        page_num += 1


if __name__ == "__main__":
    get_missing()
