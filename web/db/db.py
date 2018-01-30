from os import path
from flask import g
import sqlite3
from itertools import groupby
from datetime import timedelta, date
from subprocess import call


def connect_db(app):
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db(app):
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    if not path.exists(app.config['DATABASE']):
        init_db(app)

    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db(app)

    return g.sqlite_db


def init_db(app):
    db = connect_db(app)
    print("CREATING DATABASE")

    with app.open_resource('db/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()


def normalize_data(data):
    """
    Returns list of songs after removing the duplicate items
    """
    songs = []

    for (name, duplicates) in groupby(data, lambda row: row[0]):
        artist = []
        album = None
        release_date = None
        image_link = None
        mp3_links = {}
        sorted_mp3_links = {}

        for row in duplicates:
            if row[1] not in artist:
                artist.append(row[1])

            album = album or row[2]
            release_date = release_date or row[3]
            image_link = image_link or row[4]

            if row[6] not in mp3_links:
                mp3_links[row[6]] = row[5]

        for quality in sorted(mp3_links):
            sorted_mp3_links[quality] = mp3_links.get(quality)

        songs.append({
            "name": name,
            "artist": artist,
            "album": album,
            "release_date": release_date,
            "image_link": image_link,
            "mp3_links": sorted_mp3_links
        })

    return songs


def get_data(db):
    """
    Returns latest `limit` rows from database, all if latest is not given
    """
    cursor = db.cursor()

    today = date.today()
    idx = (today.weekday()) + 1 % 7
    sat = str(today - timedelta(7 + idx - 6))

    rows = cursor.execute(
        """
        SELECT  song.name AS "song_name", artist.name AS "artist_name",
               (SELECT name FROM album
                       WHERE id = song.album_id) AS "album_name",
               song.release_date,
               song.poster_img_url,
               mp3s.url,
               mp3s.quality
        FROM song
               INNER JOIN song_artist ON song.id = song_artist.song_id
               INNER JOIN artist ON artist.id = song_artist.artist_id
               INNER JOIN mp3s ON mp3s.song_id = song.id
               INNER JOIN song_rankings ON song_rankings.song_id = song.id
        WHERE artist.type = 'singer' AND song_rankings.week LIKE ?
        ORDER BY song_rankings.rank;
        """, ('{}%'.format(sat),)
    ).fetchall()

    if not rows:
        rows= cursor.execute(
            """
             SELECT song.name AS "song_name", song.id AS "song_id",  artist.name AS "artist_name",
               (SELECT name FROM album
                       WHERE id = song.album_id) AS "album_name",
               song.release_date,
               song.poster_img_url,
               mp3s.url,
               mp3s.quality
        FROM song
               INNER JOIN song_artist ON song.id = song_artist.song_id
               INNER JOIN artist ON artist.id = song_artist.artist_id
               INNER JOIN mp3s ON mp3s.song_id = song.id
            """
        ).fetchall()
        #call(['./run.py', 'run_ranking_scraper'])
        #get_data(db)

    return normalize_data(rows)
