from os import path, mkdir
from wget import download
from flask import url_for
from scrapers.DjpunjabScraper import DjpunjabScraper
from scrapers.JattjugadScraper import JattjugadScraper
from scrapers.MrjattScraper import MrjattScraper
from scrapers.DjjohalScraper import DjjohalScraper
from scrapers.RadioMirchiScraper import RadioMirchiScraper
from models.Album import Album
from models.Song import Song
from models.Artist import Artist
from models.SongArtist import SongArtist
from models.Mp3s import Mp3s
from models.Genre import Genre
from models.SongGenre import SongGenre
from models.SongRankings import SongRankings
from models.PosterImage import PosterImage
from web.db import get_db


def run_scrapers(app):
    """
    Returns list of songs after running scrapers.
    """
    song_count = 0
    db = get_db(app)

    try:
        dj = DjpunjabScraper()

        for song in dj.parse():
            if song:
                print("Got a song {}".format(song))
                print('--------------------')
                song_count += 1

                save_song_to_db(song, db)
    except Exception as e:
        print("DjpunjabScraper failed: ", e)

    try:
        jo = DjjohalScraper()

        for song in jo.parse():
            if song:
                print("Got a song {}". format(song))
                print('--------------------')
                song_count += 1

                save_song_to_db(song, db)
    except Exception as e:
        print("DjjohalScraper failed: ", e)


    db.close()

    try:
        jt = JattjugadScraper()

        for song in jt.parse():
            if song:
                print("Got a song {}".format(song))
                print('---------------------')
                song_count += 1

                save_song_to_db(song, db)
    except Exception as e:
     print("JattjugadScraper failed: ", e)

    try:
        mr = MrjattScraper()

        for song in mr.parse():
            if song:
                print("Got a song {}".format(song))
                print('---------------------')
                song_count += 1

                save_song_to_db(song, db)
    except Exception as e:
        print("MrjattScraper failed: ", e)

    print('******************************')
    print('**  SAVED {} SONGS TO DB  ***'.format(song_count))
    print('******************************')


def save_song_to_db(song, db):
    """
    Save song in database
    """
    try:
        cursor = db.cursor()

        song_name = song.name
        artists = song.artists
        lyrics = song.lyrics
        album_name = song.album
        source = song.source
        poster_url = song.image_link
        mp3_links = song.mp3_links
        release_date = song.released_date
        youtube_id = song.youtube_id
        genres = song.genres
        album_id = None
        artist_ids = []

        if album_name is not None:
            album_id = Album(album_name).insert(cursor).id

        for artist in (artists or [{'name': None, type: None}]):
            artist_id = Artist(artist['name'], artist['type']) \
                        .insert(cursor).id

            if artist['type'] == 'singer':
                artist_ids.append(artist_id)

        song_id = Song(
            song_name,
            lyrics,
            album_id,
            poster_url,
            release_date,
            youtube_id,
            artist_ids=artist_ids
        ).insert(cursor).id

        for artist_id in artist_ids:
            SongArtist(song_id, artist_id).insert(cursor)

        if genres:
            for genre in genres:
                genre_id = Genre(genre).insert(cursor).id
                SongGenre(song_id, genre_id).insert(cursor)

        for quality in mp3_links:
            url = mp3_links.get(quality)
            Mp3s(song_id, url, source, quality).insert(cursor)

        db.commit()
    except IOError as error:
        print("Error while inserting new song", error)


def run_ranking_scrapers(app):
    """
    Returns list of songs after running ranking scrapers.
    """
    rankings = []

    try:
        rm = RadioMirchiScraper()

        rankings += rm.parse()
    except Exception as e:
        print("RadioMirchiScraper failed: ", e)

    print('******************************')
    print('**  SAVING RANKINGS TO DB  ***')
    print('******************************')

    return save_rankings_to_db(rankings, app)


def save_rankings_to_db(ranking, app):
    """
    Save ranking in song_rankings table
    """
    db = get_db(app)

    try:
        cursor = db.cursor()

        for rank in ranking:
            song_name = rank.name
            artist_name = rank.artist
            youtube_id = rank.youtube_id
            source = rank.source
            song_rank = rank.ranking
            week = rank.week
            genre = rank.genre
            artist_ids = []

            for artist in artist_name:
                artist_id = Artist(artist, 'singer') \
                        .insert(cursor).id

                artist_ids.append(artist_id)

            song_id = Song(
                song_name,
                None,
                None,
                None,
                None,
                youtube_id,
                artist_ids=artist_ids
            ).insert(cursor).id

            genre_id = Genre(genre).insert(cursor).id
            SongGenre(song_id, genre_id).insert(cursor)

            for artist_id in artist_ids:
                SongArtist(song_id, artist_id).insert(cursor)

                SongRankings(
                    song_id,
                    artist_id,
                    source,
                    song_rank,
                    week,
                ).insert(cursor)
    except IOError as error:
        print('Error while inserting new ranking ', error)
    finally:
        db.commit()
        db.close()


def download_song_posters(app):
    """
    Download poster image from `image_url`
    """
    WEB_PATH = path.join(path.dirname(path.abspath('__main__')), 'web')
    DOWNLOAD_PATH = WEB_PATH + url_for('static', filename='images')
    db = get_db(app)
    cursor = db.cursor()

    if not path.exists(DOWNLOAD_PATH):
        mkdir(DOWNLOAD_PATH)

    urls = PosterImage(cursor).select_urls()

    for url in urls:
        url = url[0]
        local_url = None

        try:
            print("Downloading image: ", url)

            local_url = download(url, out=DOWNLOAD_PATH)

            local_url = path.basename(local_url)

            PosterImage(cursor).update(url, local_url)
            db.commit()
        except Exception as error:
            print("Failed to download poster image: ", url)
            print(error)

    db.close()
