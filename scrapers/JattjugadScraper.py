from urllib.parse import urlparse, urljoin
from scrapers.RootScraper import RootScraper
from .Items import Song


class JattjugadScraper(RootScraper):
    """
    Creates scraper which scraps endjatt.com
    """
    def __init__(self):
        super().__init__()
        self.whitelist = ['endjatt.com', 'jattjugad.xyz']
        self.recrapables = [
            'http://endjatt.com',
            'http://jattjugad.xyz/mu/cat/a/1/Punjabi.html',
            'http://jattjugad.xyz/mu/cat/a/1/Punjabi_SinGle_Track.html',
            'http://jattjugad.xyz/mu/cat/a/1/Hindi.html',
            'http://jattjugad.xyz/mu/cat/a/1/Hindi_Single_Track.html'
        ]
        self.done_rescrapables = False
        self.base_url = 'http://jattjugad.xyz'

    def extract_item(self, soup):
        """
        Returns Song Item from the soup if it is an item page. None otherwise
        """
        metadata_tablerow = soup.find('tr')

        image_link = urljoin(self.base_url,
                             metadata_tablerow.find('img').attrs['src'])

        metadata_rows = [
            [j.strip() for j in l.text.split(':')]
            for l in metadata_tablerow.find('table').select('td')
        ]

        song_name = None
        artists = []
        album = None

        for text in metadata_rows:
            if text[0].lower() == 'title':
                song_name = text[1]

            if text[0].lower() == 'artists':
                artists = [
                    {'name': i.strip(), 'type': 'singer'}
                    for i in text[1].split(',')
                ]

            if text[0].lower() == 'album':
                album = text[1]

        mp3_links = {}
        maybe_mp3_links = []

        for a in soup.select('a'):
            if a.attrs['href'].endswith('.mp3'):
                maybe_mp3_links.append(a)

        for mp3_link in maybe_mp3_links:
            if '48 Kbps' in mp3_link.text:
                mp3_links['48'] = mp3_link.attrs['href']

            if '128 Kbps' in mp3_link.text:
                mp3_links['128'] = mp3_link.attrs['href']

            if '320 Kbps' in mp3_link.text:
                mp3_links['320'] = mp3_link.attrs['href']

        if song_name == album:
            album = None

        return Song(song_name, artists, album, self.base_url,
                    image_link=image_link, mp3_links=mp3_links)

    def extract_next_links(self, soup, base_url):
        """
        Returns links to scrap next from the soup
        """
        next_links = set()

        for a in soup.select('a'):
            link = urljoin(base_url, a.get('href'))

            if link.endswith('.zip') or link.endswith('.mp3'):
                continue

            if urlparse(link).hostname in self.whitelist:
                next_links.add((link,))

        return next_links

    def soup_has_item(self, soup):
        """
        Returns True if has items, False otherwise
        """
        for a in soup.select('a'):
            if a.has_attr('href'):
                if (
                        a.attrs['href'].endswith('.mp3')
                        and soup.find('table') and soup.find('table').find('img')
                ):
                    return True

        return False

    def parse(self):
        """
        Returns list of songs after assigning them to ~self.songs~
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
