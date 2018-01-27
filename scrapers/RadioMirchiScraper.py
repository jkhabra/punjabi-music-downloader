from datetime import datetime, date
from scrapers.RootScraper import RootScraper
from .Items import Ranking
from urllib.parse import urlparse


class RadioMirchiScraper(RootScraper):
    """
    Create scraper which scrapes radiomirchi.com for top 10 songs
    """
    def __init__(self):
        super().__init__()
        self.urls_to_scrap = {
            'Punjabi': 'http://www.radiomirchi.com/more/punjabi-top-10/',
            'Bollywood': 'http://www.radiomirchi.com/more/mirchi-top-20/'
        }
        self.base_url = 'http://www.radiomirchi.com'

    def parse(self):
        """
        Returns list of `Song`s and assign them to `self.Song`
        """
        for (genre, link) in self.urls_to_scrap.items():
            try:
                soup = self.make_soup(link)
            except Exception:
                continue

            song_date = soup.find(
                'a', {'class': 'select'}
            ).text.split('-')[0].strip() + ' ' + str(date.today().year)

            week = datetime.strptime(song_date, '%b %d %Y')

            song_containers = soup.select('.top01')

            for song in song_containers:
                youtube_id = None
                song_name = None
                artist = []
                rank = None

                try:
                    youtube_id = urlparse(
                        song.select_one('.palyicon').select_one('img').attrs['data-vid-src']
                    ).path.rpartition('/')[-1]
                except KeyError:
                    youtube_id = ''

                song_name = song.find('h2').text
                name_artist_pair = song.find('h3').text
                name_artist_pair = [
                    i.strip() for i in name_artist_pair.split('\n')
                ]
                artists = [
                    i.strip() for i in name_artist_pair[1].split(',')
                ]

                artist = []

                for a in artists:
                    artist.extend([j.strip() for j in a.split('&')])

                rank = song.select_one('.circle').text

                song_ranking = Ranking(
                    song_name,
                    artist,
                    youtube_id,
                    self.base_url,
                    rank,
                    week,
                    genre
                )
                self.ranking.append(song_ranking)

        return self.ranking
