from urllib.parse import urlparse, urljoin
from scrapers.RootScraper import RootScraper
from .Items import Song


class DjjohalScraper(RootScraper):
    """
    Creates scraper which scraps djjohal.com
    """
    def __init__(self):
        super().__init__()
        self.whitelist = ['mr-johal.com']
        self.ignorelist = ['cat=New+Talent', 'cat=Bhakti+Sangeet', 'cat=Haryanavi', 'cat=English', 'cat=Non+Stop', 'cat=Khalistani', 'cat=Tamil', 'cat=Fun+Audio', 'cat=Telugu', 'cat=Arabic', 'cat=Pakistani', 'cat=Assamese', 'cat=Bengali', 'cat=Bhojpuri', 'cat=Carnatic+Movies', 'cat=Comedy', 'cat=Compilations', 'cat=Dogri', 'cat=Fusion', 'cat=Ghazals', 'cat=Gujarati', 'cat=Hindustani+Instrumental', 'cat=Jigalabandhi', 'cat=Kannada', 'cat=Kashmiri', 'cat=Kumaoni+and+Uttaranchali', 'cat=Malayalam', 'cat=Marathi', 'cat=Nepali', 'cat=Oriya', 'cat=Patriotic', 'cat=Qawwali', 'cat=Rajasthani', 'cat=Sanskrit', 'cat=Sindhi', 'cat=Unknown+Talent', 'cat=Urdu']
        self.rescrapables = [
            'http://djjohal.com',
            'https://mr-johal.com/updates.php'
        ]
        self.done_rescrapables = False
        self.base_url = 'http://djjohal.com'

    def extract_item(self, soup):
        """
        Returns Song Item form the soup if it is an item page.
        None otherwise
        """
        img = soup.select_one('.albumCover').select_one('img').get('src')

        metadata = soup.select_one('.albumInfo')

        metadata_row = [
            [j.strip() for j in i.text.split(':')]
            for i in metadata.select('p')
        ]

        name = None
        artists = []
        album = None
        genres = []
        released_date = None

        for text in metadata_row:
            if text[0].lower() == 'singer':
                artists += [{'name': i.strip(), 'type': 'singer'}
                            for i in text[1].split(',')]

            if text[0].lower() == 'album':
                album = text[1]

            if text[0].lower() == 'genre':
                genres = [i.strip() for i in text[1].split(',')]

            if text[0].lower() == 'music':
                artists += [{'name': i.strip(), 'type': 'music_composer'}
                            for i in text[1].split(',')]

            if text[0].lower() == 'lyrics':
                artists += [{'name': i.strip(), 'type': 'lyricist'}
                            for i in text[1].split(',')]

            if text[0].lower() == 'released':
                released_date = text[1]

            if text[0].lower() == 'title':
                name = text[1]

        if '' in genres:
            genres.remove('')

        if not name:
            name = album
            album = None

        mp3_links = {}
        maybe_mp3_links = []

        for a in soup.select('a'):
            if a.attrs['href'].endswith('.mp3'):
                maybe_mp3_links.append(a)

        for mp3_link in maybe_mp3_links:
            if '48 kbps' in mp3_link.text:
                mp3_links['48'] = mp3_link.attrs['href']
            if '128 kbps' in mp3_link.text:
                mp3_links['128'] = mp3_link.attrs['href']
            if '320 kbps' in mp3_link.text:
                mp3_links['320'] = mp3_link.attrs['href']

        print(released_date)
        return Song(name, artists, album, self.base_url,
                    img, mp3_links, released_date=released_date, genres=genres)

    def extract_next_links(self, soup, base_url):
        """
        Returns links to scrap next from the soup
        """
        next_links = set()

        for a in soup.select('a'):
            link = urljoin(base_url, a.get('href'))

            query = urlparse(link).query
            if urlparse(link).hostname in self.whitelist and query not in self.ignorelist:
                next_links.add((link,))

        return next_links

    def soup_has_item(self, soup):
        """
        Returns True if soup has item, False otherwise
        """
        for a in soup.find_all('a'):
            if (
                    a.attrs['href'].endswith('.mp3')
                    and soup.select_one('.albumCover')
                    and soup.select_one('.albumCover').find('img')
            ):
                return True

        return False

    def parse(self):
        """
        Returns list of `Song's` and assign them to `self.songs`
        """
        links = self.rescrapables

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
