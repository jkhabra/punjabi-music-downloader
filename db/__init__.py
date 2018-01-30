from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Album, Artist, Genre, Mp3s, Song, SongArtist, SongGenre, SongRanking, Base
import os

def get_session():
    engine = create_engine('sqlite:///db/musicphreak.db')

    if os.path.exists('db/musicphreak.db'):
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        return session
    else:
        Base.metadata.create_all(engine)
        return get_session
