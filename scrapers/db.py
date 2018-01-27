import sqlite3
from os import path

config = {
    'SCRAPER_DB': path.join(path.dirname(__file__), 'scraper.db')
}


def connect_db():
    """
    Connects to the scraper database.
    """
    rv = sqlite3.connect(config['SCRAPER_DB'])
    rv.row_factory = sqlite3.Row

    return rv


def get_db():
    """
    Opens and returns a new database connection
    """
    if not path.exists(config['SCRAPER_DB']):
        init_db()

    return connect_db()


def init_db():
    db = connect_db()
    print("CREATING DATABASE")

    with open('scrapers/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()
