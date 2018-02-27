from os import path
from flask import Flask, render_template, g, json, request, Response
from db import get_session
from models import Album, Song, Artist, SongArtist, Mp3s, Genre, SongGenre, SongRanking
from sqlalchemy import and_


app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=path.join(path.dirname(app.root_path), 'musicphreak.db')
))


@app.route('/')
def show_topsongs():
    db_session = get_session()
    data = []
    mp3_links  = {}
    song = db_session.query(SongArtist, Song, Artist, Mp3s).join(Song, Artist).limit(20).all()

    for a in song:
        mp3_links[a.Mp3s.quality] = a.Mp3s.url
        s_name = a.Song.name
        a_name = a.Artist.name
        poster = a.Song.poster_img_url
        data.append({
            's_name':s_name,
            'a_name':a_name,
            'poster':poster,
            'links':mp3_links
            })

    db_session.close()
    return render_template('topsongs.html', songs=data)

@app.route('/api/songs/', defaults={'song_id':None})
@app.route('/api/songs/<int:song_id>')
def json_songs(song_id):
    db_session = get_session()
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 30))
    total = db_session.query(Song).count()
    songs = []
    mp3_links = {}

    query = db_session \
            .query(SongArtist, Song, Artist) \
            .join(Song, Artist)

    if song_id:
        query = query.filter(Song.id == song_id)
    else:
        query = query.slice(skip, limit).limit(limit)

    data = query.all()

    for song in data:
        link = db_session.query(Mp3s).filter(song.Song.id==Mp3s.song_id).all()
        for m in link:
            mp3_links[m.quality] = m.url

        artist = {'id': song.Artist.id, 'name': song.Artist.name}
        song_dic = {
            'url': mp3_links,
            'songId': song.Song.id,
            'name': song.Song.name,
            'thumb': song.Song.poster_img_url,
            'releaseDate': song.Song.release_date,
            'artist': artist,
            'albumId': song.Song.album_id
        }

        songs.append(song_dic)

    d = {'data': songs,
         'total':total}

    db_session.close()

    return Response(json.dumps(d), mimetype='application/json')

@app.route('/api/artists/', defaults={'artist_id':None})
@app.route('/api/artists/<int:artist_id>')
def json_artist(artist_id):
    db_session = get_session()
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 30))
    total = db_session.query(Artist).count()
    artist = []
    query = db_session.query(Artist)

    if artist_id:
        query = query.filter(Artist.id == artist_id)
    else:
        query = query.slice(skip,limit).limit(limit)

    db_data = query.all()
    for i in db_data:
        artist_song = {
            'artistId': i.id,
            'artistName': i.name,
        }

        artist.append(artist_song)

    data = {'total': total,
         'data': artist}

    db_session.close()

    return Response(json.dumps(data), mimetype='application/json')

@app.route('/api/artists/<int:artist_id>')
@app.route('/api/artists/<int:artist_id>/songs')
def json_artist_song(artist_id):
    db_session = get_session()
    skip = int(request.args.get('skip',0))
    limit = int(request.args.get('limit', 10))
    mp3_links = {}
    artist_id = db_session.query(Artist).filter(Artist.id == artist_id).one()
    artist = {'id': artist_id.id, 'name': artist_id.name}
    s = [artist]
    get_songs = db_session.query(SongArtist)\
                          .filter(SongArtist.artist_id == artist_id.id)\
                          .slice(skip,limit).limit(limit).all()
    total= db_session.query(SongArtist).filter(SongArtist.artist_id == artist_id.id).count()

    for i in get_songs:
        data = db_session.query(Song).filter(Song.id == i.song_id).all()
        for song in data:
            link = db_session.query(Mp3s).filter(song.id==Mp3s.song_id).all()

        for m in link:
            mp3_links[m.quality] = m.url

        song_dic = {
            'url': mp3_links,
            'songId': song.id,
            'name': song.name,
            'thumb': song.poster_img_url,
            'releaseDate': song.release_date,
            'albumId': song.album_id
        }

        s.append(song_dic)

    data = {'total': total,
            'data': s}

    db_session.close()
    return Response(json.dumps(data), mimetype='application/json')

