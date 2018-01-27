from urllib.parse import urlparse


class Song():
    """
    Represents a single song extracted by scrapers
    """
    def __init__(self, name, artists, album, source, image_link='',
                 mp3_links={}, released_date=None, lyrics=None,
                 youtube_id=None, genres=[]):
        self.name = name
        self.artists = artists
        self.album = album
        self.lyrics = lyrics
        self.source = urlparse(source).hostname
        self.image_link = image_link
        self.mp3_links = mp3_links
        self.released_date = released_date
        self.youtube_id = youtube_id
        self.genres = genres

    def __repr__(self):
        return "<name: {} artists: {}>".format(self.name, self.artists)


class Ranking():
    def __init__(self, name, artist, youtube_id,
                 source, ranking, week_start_date, genre):
        self.name = name
        self.artist = artist
        self.youtube_id = youtube_id
        self.source = source
        self.ranking = int(ranking)
        self.week = week_start_date
        self.genre = genre

    def __repr__(self):
        return "<name: {} ranking: {} week: {}>" \
            .format(self.name, self.ranking, self.week)
