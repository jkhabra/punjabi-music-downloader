from os import path
from flask import Flask, render_template, g, json, request, Response
from db import get_session
from models import Album, Song, Artist, SongArtist, Mp3s, Genre, SongGenre, SongRanking
from sqlalchemy import and_, func

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
        link={a.Mp3s.quality: a.Mp3s.url}
        for i in sorted(link):
            mp3_links[i] = link.get(i)
        s_name = a.Song.name
        a_name = a.Artist.name
        poster = a.Song.poster_img_url
        u = min(mp3_links.keys())
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
        artist = {'id': song.Artist.id, 'name': song.Artist.name}
        song_dic = {
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
    artist = []
    data = db_session.query(SongArtist, Song, Artist).join(Song, Artist).all()

    for i in data:
        artist_song = {
            'artistId': i.SongArtist.artist_id,
            'artistName': i.Artist.name
        }
        if artist_song['artistId'] == artist_id:
            artist = artist_song
        if artist_id is None:
            artist.append(artist_song)
    db_session.close()
    return Response(json.dumps(artist), mimetype='application/json')
