from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

Base = declarative_base()

class Album(Base):
    __tablename__ = 'album'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DATETIME, default=datetime.datetime.utcnow)
    update_at = Column(DATETIME, default=datetime.datetime.utcnow)

class Artist(Base):
    __tablename__ ='artist'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(80))
    created_at = Column(DATETIME, default=datetime.datetime.utcnow)
    update_at = Column(DATETIME, default=datetime.datetime.utcnow)

class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DATETIME, default=datetime.datetime.utcnow)
    update_at = Column(DATETIME, default=datetime.datetime.utcnow)

class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    lyrics = Column(String(1000))
    album_id = Column(Integer, ForeignKey('album.id'))
    album = relationship(Album)
    poster_img_url = Column(String(500))
    local_img_url = Column(String(300))
    youtube_id = Column(Integer)
    release_date = Column(String(50))
    created_at = Column(DATETIME, default=datetime.datetime.utcnow)
    update_at = Column(DATETIME, default=datetime.datetime.utcnow)

class Mp3s(Base):
    __tablename__ = 'mp3s'
    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'))
    song = relationship(Song)
    url = Column(String(500), nullable=False)
    source = Column(String(80))
    quality = Column(String(20))
    created_at = Column(DATETIME, default=datetime.datetime.utcnow)
    update_at = Column(DATETIME, default=datetime.datetime.utcnow)

class SongArtist(Base):
    __tablename__ = 'song_artist'
    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'))
    song = relationship(Song)
    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship(Artist)
    created_at = Column(DATETIME, default=datetime.datetime.utcnow)
    update_at = Column(DATETIME, default=datetime.datetime.utcnow)

class SongGenre(Base):
    __tablename__ = 'song_genre'
    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'))
    song = relationship(Song)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)
    created_at = Column(DATETIME, default=datetime.datetime.utcnow)
    update_at = Column(DATETIME, default=datetime.datetime.utcnow)

class SongRanking(Base):
    __tablename__ = 'song_ranking'
    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'))
    song = relationship(Song)
    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship(Artist)
    source = Column(String(200))
    rank = Column(Integer)
    week = Column(String(89))
    created_at = Column(DATETIME, default=datetime.datetime.utcnow)
    update_at = Column(DATETIME, default=datetime.datetime.utcnow)

