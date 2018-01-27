from urllib.parse import urlparse, urljoin
from datetime import datetime
from scrapers.RootScraper import RootScraper
from .Items import Song


class MrjattScraper(RootScraper):
    """
     Creates scraper which scraps mr-jatt.com
    """
    def __init__(self):
        super().__init__()
        self.whitelist = ['mr-jatt.com']
        self.recrapables = [
            'https://mr-jatt.com',
            'https://mr-jatt.com/punjabisong-top20-singletracks.html',
            'https://mr-jatt.com/punjabisongs-top20.html',
            'https://mr-jatt.com/hindisongs-top20.html',
            'https://mr-jatt.com/category.php?c=Single%20Tracks',
            'https://mr-jatt.com/category.php?c=Hindi+Single+Track',
            'https://mr-jatt.com/category.php?c=HindiSongs'
        ]
        self.done_rescrapables = False
        self.base_url = 'https://mr-jatt.com'

    def extract_youtube_id(self, soup):
        """
        Returns youtube_id from soup, None otherwise
        """
        frame = soup.select_one('iframe')

        if frame:
            return urlparse(
                frame.get('src')
            ).path.rpartition('/')[-1]

        return frame

    def soup_has_lyrics_link(self, soup, song_name):
        """
        Return True if soup has lyrics link, False otherwise
        """
        has_lyrics = soup.select_one('.lyrics')

        if has_lyrics:
            lyrics_link = 'read {} lyrics'.format(song_name.lower())

            if lyrics_link in has_lyrics.select_one('a').text.lower():
                return True

        return False

    def extract_item(self, soup):
        """
        Returns Song Item from the soup if it is an item page.
        None otherwise
        """
        metadata_div = soup.find('div', {'class': 'albumCoverSmall'})

        img = metadata_div.find('img').get('src')

        matadata = soup.find('div', {'class': 'albumInfo'})

        matadata_rows = [
            [j.strip() for j in i.text.split(':')]
            for i in matadata.find_all('p')
        ]

        name = None
        artists = []
        album = None
        released_date = None
        genre = []

        for text in matadata_rows:
            if text[0].lower() == 'title':
                name = text[1]

            if text[0].lower() == 'album':
                album = text[1]

            if text[0].lower() == 'artists':
                artists += [{'name': i.strip(), 'type': 'singer'}
                            for i in text[1].split(',')]

            if text[0].lower() == 'singer':
                artists += [{'name': i.strip(), 'type': 'singer'}
                            for i in text[1].split(',')]

            if text[0].lower() == 'music':
                artists += [{'name': i.strip(), 'type': 'music_composer'}
                            for i in text[1].split(',')]

            if text[0].lower() == 'lyrics':
                artists += [{'name': i.strip(), 'type': 'lyricist'}
                            for i in text[1].split(',')]

            if text[0].lower() == 'released':
                rel_date = ' '.join(text[1].split(','))
                released_date = datetime.strptime(rel_date, '%d %b %Y')

            if text[0].lower() == 'category':
                genre = [i.replace('songs', '').strip()
                         for i in text[1].split(',')]

        if not name:
            name = album

        if name == album:
            album = None

        mp3_links = {}
        maybe_mp3_links = []

        for a in soup.findAll('a', {'class': 'touch'}):
            if a.get('href').endswith('.mp3'):
                maybe_mp3_links.append(a)

        maybe_mp3_links = [
            i for i in maybe_mp3_links if 'Download in' in i.text
        ]

        for mp3 in maybe_mp3_links:
            if '48 kbps' in mp3.text:
                mp3_links['48'] = mp3.get('href')
            if '128 kbps' in mp3.text:
                mp3_links['128'] = mp3.get('href')
            if '192 kbps' in mp3.text:
                mp3_links['192'] = mp3.get('href')
            if '320 kbps' in mp3.text:
                mp3_links['320'] = mp3.get('href')

        lyrics_soup = None
        youtube_id = None

        if self.soup_has_lyrics_link(soup, name):
            lyrics_soup = self.make_soup(
                soup.select_one('.lyrics').select_one('a').attrs['href']
            )

        if lyrics_soup:
            youtube_id = self.extract_youtube_id(lyrics_soup)

        return Song(name, artists, album, self.base_url, img, mp3_links,
                    released_date=released_date, youtube_id=youtube_id,
                    genres=genre)

    def extract_next_links(self, soup, base_url):
        """
        Returns links to scrap next from the soup
        """
        next_links = set()

        for a in soup.select('a'):
            link = urljoin(self.base_url, a.get('href'))

            if urlparse(link).hostname in self.whitelist:
                next_links.add((link,))

        return next_links

    def soup_has_item(self, soup):
        """
        Returns True if soup has Item, False otherwise
        """
        img = soup.find('div', {'class': 'albumCoverSmall'})

        for i in soup.findAll('a', {'class': 'touch'}):
            if (
                    i.get('href').endswith('.mp3')
                    and img and img.find('img').get('src')
            ):
                return True

        return False

    def parse(self):
        """
        Returns list of `Song`s and assign them to `self.songs`
        """
        links = self.recrapables

        while links:
            if self.done_rescrapables:
                links = self.get_next_links()
            else:
                self.done_rescrapables = True

            for link in links:
                next_links = []
                song = None

                try:
                    soup = self.make_soup(link)
                except Exception:
                    continue

                if self.soup_has_item(soup):
                    song = self.extract_item(soup)
                    self.songs.append(song)

                next_links = self.extract_next_links(soup, link)

                self.scrap_in_future(list(next_links))
                self.on_success(link)

                yield song

        return self.songs
