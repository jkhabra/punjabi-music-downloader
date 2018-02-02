from os import path
from flask import Flask, render_template, g, json
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
    song = db_session.query(SongArtist, Song, Artist, Mp3s).join(Song, Artist).filter(and_(SongArtist.song_id == Song.id, SongArtist.artist_id == Artist.id)).join(Mp3s).filter(Mp3s.song_id == Song.id).all()
    for a in song:
        #if a.Song.id == a.Mp3s.song_id and a.Mp3s.quality == '48':
        l = a.Mp3s.url
        s_name = a.Song.name
        a_name = a.Artist.name
        poster = a.Song.poster_img_url
        links = [a.Mp3s.url]
        quality = a.Mp3s.quality

        data.append({
            's_name':s_name,
            'a_name':a_name,
            'poster':poster,
            'links':links,
            'quality':quality,
            'l':l
            })

    db_session.close()
    return render_template('topsongs.html', songs=data)


@app.route('/api/songs')
def json_songs():
    db_session = get_session()
    songs = []
    data = db_session.query(SongArtist, Song, Artist, Mp3s, Album).join(Song, Artist).filter(and_(SongArtist.song_id == Song.id, SongArtist.artist_id == Artist.id)).join(Mp3s).filter(Mp3s.song_id == Song.id).join(Album).filter(Album.id == Song.id).all()

    for song in data:
        song_dic = {
            'Song_id': song.Song.id,
            'Name': song.Song.name,
            'Artist': song.Artist.name,
            'Album': song.Album.name,
            'Mp3_links': song.Mp3s.url,
            'Image_link': song.Song.poster_img_url,
            'Release_date': song.Song.release_date
        }
        songs.append(song_dic)
    db_session.close()
    return json.dumps(songs)
