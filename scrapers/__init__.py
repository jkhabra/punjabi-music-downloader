from os import path, mkdir
from wget import download
from flask import url_for
from scrapers.DjpunjabScraper import DjpunjabScraper
from scrapers.JattjugadScraper import JattjugadScraper
from scrapers.MrjattScraper import MrjattScraper
from scrapers.DjjohalScraper import DjjohalScraper
from scrapers.RadioMirchiScraper import RadioMirchiScraper
from sqlalchemy import and_
from models import Album, Song, Artist, SongArtist, Mp3s, Genre, SongGenre, SongRanking
from db import get_session


def run_scrapers(app):
    """
    Returns list of songs after running scrapers.
    """
    song_count = 0
    db_session = get_session()

    # try:
    #     dj = DjpunjabScraper()

    #     for song in dj.parse():
    #         if song:
    #             print("Got a song {}".format(song))
    #             print('--------------------')
    #             song_count += 1

    #             save_song_to_db(song)
    # except Exception as e:
    #     print("DjpunjabScraper failed: ", e)

    try:
         jo = DjjohalScraper()

         for song in jo.parse():
             if song:
                 print("Got a song {}". format(song))
                 print('--------------------')
                 song_count += 1

                 save_song_to_db(song)
    except Exception as e:
         print("DjjohalScraper failed: ", e)


    # try:
    #     jt = JattjugadScraper()

    #     for song in jt.parse():
    #         if song:
    #             print("Got a song {}".format())
    #             print('---------------------')
    #             song_count += 1

    #             save_song_to_db(song, db)
    # except Exception as e:
    #  print("JattjugadScraper failed: ", e)

    #try:
     #   mr = MrjattScraper()

      #  for song in mr.parse():
       #     if song:
        #        print("Got a song {}".format(song))
         #       print('---------------------')
          #      song_count += 1

           #     save_song_to_db(song)
   # except Exception as e:
    #    print("MrjattScraper failed: ", e)

    print('******************************')
    print('**  SAVED {} SONGS TO DB  ***'.format(song_count))
    print('******************************')


def save_song_to_db(song):
    """
    Save song in database
    """
    try:
        db_session = get_session()

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

        if album_name is not None:
            if not db_session.query(Album).filter(Album.name == album_name).all():
                new_album = Album(name=album_name)
                db_session.add(new_album)
            else:
                album_name = None

        for artist in (artists or [{'name': None, type: None}]):
            if db_session.query(Artist).filter(and_(Artist.name != artist['name'], Artist.type != artist['type'])).all():
                new_artist = Artist(name=artist['name'],type=artist['type'])
                db_session.add(new_artist)
            else:
                new_artist = db_session.query(Artist).filter(Artist.name == artist['name']).one()
        print(new_artist.id)
        if db_session.query(Song).filter(Song.name != song_name).all:
            if album_name is not None:
                new_song = Song(name=song_name, poster_img_url=poster_url,album_id=new_album.id, lyrics=lyrics,youtube_id=youtube_id,release_date=release_date)
            else:
                new_song = Song(name=song_name, poster_img_url=poster_url,lyrics=lyrics,youtube_id=youtube_id,release_date=release_date)
            db_session.add(new_song)

        if db_session.query(SongArtist).filter(and_(SongArtist.song_id !=new_song.id, SongArtist.artist_id != new_artist.id)).all():
            print('in here up\\\\')
            new_song_artist = SongArtist(artist_id=new_artist.id, song_id=new_song.id)
            db_session.add(new_song_artist)

        if genres:
            for genre in genres:
                if not db_session.query(Genre).filter(Genre.name == genre).all(): 
                    new_g = Genre(name=genre)
                    db_session.add(new_g)
                else:
                    new_g= db_session.query(Genre).filter(Genre.name == genre).one()

        if db_session.query(SongGenre).filter(and_(SongGenre.song_id!=new_song.id, SongGenre.genre_id!=new_g.id)):
            new_song_genre = SongGenre(song_id=new_song.id, genre_id=new_g.id)
            db_session.add(new_song_genre)

        if len(mp3_links) != 0:
            for quality in mp3_links:
                url = mp3_links.get(quality)
                if db_session.query(Mp3s).filter(Mp3s.url != url):
                    new_mp3s = Mp3s(song_id=new_song.id,source=source,url=url,quality=quality)
                    db_session.add(new_mp3s)
                    db_session.commit()

        db_session.commit()

        db_session.close()
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

    return save_rankings_to_db(rankings)


def save_rankings_to_db(ranking):
    """
    Save ranking in song_rankings table
    """
    db_session = get_session()

    try:

        for rank in ranking:
            song_name = rank.name
            artist_name = rank.artist
            youtube_id = rank.youtube_id
            source = rank.source
            song_rank = rank.ranking
            week = rank.week
            genre = rank.genre
            artist_ids = []

            song = db_session.query(Song).filter(Song.name == song_name).all()
            if not song:
                new_song = Song(name=song_name, youtube_id=youtube_id)
                db_session.add(new_song)
            else:
                for i in song:
                    new_song = i

            for artist in artist_name:
                if not db_session.query(Artist).filter(Artist.name == artist).all():
                    new_artist = Artist(name=artist,type='singer')
                    db_session.add(new_artist)
                else:
                    new_artist = db_session.query(Artist).filter(Artist.name == artist).one()

            if db_session.query(SongRanking).filter(and_(SongRanking.week == week,SongRanking.song_id == new_song.id,SongRanking.artist_id == new_artist.id)):
                new_ranking = SongRanking(song_id=new_song.id, artist_id=new_artist.id, source=source, rank=song_rank, week=week)
                db_session.add(new_ranking)
                db_session.commit()
        db_session.close()
    except IOError as error:
        print('Error while inserting new ranking ', error)

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
