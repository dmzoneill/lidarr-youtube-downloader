#!/usr/bin/env python3
import sqlite3
from typing import Optional

import typer

updated = 0
lidar_db = None


def get_lidarr_track_ids(cur, artist_name, album_name, track_name):
    # update
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
    cur.execute(
        sql,
        (
            artist_name,
            album_name,
            track_name,
        ),
    )
    result = cur.fetchall()
    if len(result) == 0:
        return -1
    return [X[0] for X in result]


def get_lidarr_album_id(cur, artist_name, album_name, track_name):
    # update
    sql = """
        select Albums.Id from ArtistMetadata, Artists, Tracks, Albums, AlbumReleases
        where ArtistMetadata.id = Artists.ArtistMetadataId
        and Artists.ArtistMetadataId = Tracks.ArtistMetadataId
        and Tracks.AlbumReleaseId = AlbumReleases.Id
        and Albums.id = AlbumReleases.AlbumId
        and ArtistMetadata.Name = ?
        and AlbumReleases.Title = ?
        and Tracks.Title = ?
        limit 1    
    """
    cur.execute(
        sql,
        (
            artist_name,
            album_name,
            track_name,
        ),
    )
    result = cur.fetchall()
    if len(result) == 0:
        return -1
    return result[0][0]


def set_lidarr_track_trackfield(con, cur, TrackFileId, track_id):
    # update
    cur.execute(
        "UPDATE Tracks SET TrackFileId=? WHERE id = ?",
        (
            TrackFileId,
            track_id,
        ),
    )
    con.commit()


def set_lidarr_trackfile_album_id(con, cur, AlbumId, Id):
    # update
    cur.execute(
        "UPDATE TrackFiles SET AlbumId=? WHERE id=?",
        (
            AlbumId,
            Id,
        ),
    )
    con.commit()


def lidarr_match_fieldtrack_id(con, cur, id, path):
    global updated
    file = path.split("/", 4)[-1]
    parts = file.split("-", 3)
    artist = parts[0].strip()
    album = parts[1].strip()
    track = parts[2].strip().replace(".mp3", "")

    track_ids = get_lidarr_track_ids(cur, artist, album, track)

    print(artist)
    print(album)
    print(track)
    print(track_ids)

    if track_ids == -1:
        return

    for x in track_ids:
        set_lidarr_track_trackfield(con, cur, id, x)
    updated += 1


def lidarr_match_album_id(con, cur, id, path):
    global updated
    file = path.split("/", 4)[-1]
    parts = file.split("-", 3)
    artist = ""
    album = ""
    track = ""

    if len(parts) == 3:
        artist = parts[0].strip()
        album = parts[1].strip()
        track = parts[2].strip()

    elif len(parts) == 4:
        artist = parts[0].strip()
        album = parts[1].strip()
        track = parts[3].strip()

    track = track.replace(".mp3", "").replace(".flac", "")

    album_id = get_lidarr_album_id(cur, artist, album, track)

    print(artist)
    print(album)
    print(track)
    print(album_id)

    if album_id == -1:
        return

    set_lidarr_trackfile_album_id(con, cur, album_id, id)
    updated += 1


def iterate_unmapped():
    global updated
    con = sqlite3.connect(lidar_db)
    cur = con.cursor()
    con.set_trace_callback(print)

    updated = 0
    cur.execute(
        "SELECT * FROM TrackFiles WHERE id NOT IN (SELECT TrackFileId FROM Tracks)"
    )
    result = cur.fetchall()
    if len(result) == 0:
        con.close()
        return

    for row in result:
        lidarr_match_fieldtrack_id(con, cur, row[0], row[9])

    print("Total : " + str(len(result)))
    print("Updated : " + str(updated))

    updated = 0
    cur.execute("SELECT * FROM TrackFiles")
    result = cur.fetchall()
    if len(result) == 0:
        con.close()
        return

    for row in result:
        lidarr_match_album_id(con, cur, row[0], row[9])

    con.close()

    print("Total : " + str(len(result)))
    print("Updated : " + str(updated))


app = typer.Typer()


@app.command()
def run(
    db: Optional[str] = os.environ.get(
        "LIDARR_DB", "/home/dave/src/docker-media-center/config/lidarr/lidarr.db"
    ),
):
    lidar_db = db
    iterate_unmapped()
