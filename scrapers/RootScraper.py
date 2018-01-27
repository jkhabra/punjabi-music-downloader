from bs4 import BeautifulSoup
from requests import get
import re
import random
from datetime import date
from scrapers.db import get_db

user_agents = [
    'Googlebot/2.1 (+http://www.google.com/bot.html)',
    'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 (FM Scene 4.6.1) ',
    'AltaVista Intranet V2.0 AVS EVAL search@freeit.com',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
]


class RootScraper():
    """
    Root class to be subclassed by other scrapers. Provide common functionality
    for all scrapers.
    """
    def __init__(self):
        self.songs = []
        self.ranking = []
        self.ignorelist = []

    def is_scraped(self, url):
        db = get_db()
        already_scraped = False

        try:
            cursor = db.cursor()
            available = cursor.execute(
                """
                SELECT url FROM urls WHERE url = ? and scraped_at is not null;
                """,
                (url,)
            ).fetchone()

            if available and available[0]:
                already_scraped = True

        except Exception as error:
            print("Error while checking if url is already scraped: " + error)
        finally:
            db.close()

        return already_scraped

    def make_soup(self, url):
        """
        Takes a url, and return BeautifulSoup for that Url
        """
        header = {
            'user-agent': random.choice(user_agents)
        }
        print("Downloading page: " + url)

        return BeautifulSoup(get(url, headers=header, verify=False)
                             .content, 'html.parser')

    def parse(self):
        """
        Should return list of songs after assigning them to ~self.songs~.
        To be implemented by child scrapers.
        """
        raise Exception("Implement it dumbfuck")

    def on_success(self, url):
        db = get_db()
        print('Done with', url)
        print("------------------")

        try:
            cursor = db.cursor()
            cursor.execute(
                """
                UPDATE urls set scraped_at = ? where url = ?;
                """,
                (date.today(), url)
            )
        except Exception as error:
            print("Error while inserting url: ", error)
        finally:
            db.commit()
            db.close()

    def scrap_in_future(self, urls):
        """
        Insert next scrap link in scraper database
        """
        db = get_db()

        try:
            cursor = db.cursor()
            cursor.executemany(
                """
                INSERT OR IGNORE INTO urls (url, scraped_at) VALUES (?, null);
                """,
                (urls)
            )
        except Exception as error:
            print("error while inserting scraped url: ", error)
        finally:
            db.commit()
            db.close()

    def get_next_links(self):
        """
        Returns next link from scraper database
        """
        def regexp(expr, item):
            reg = re.compile(expr)
            return reg.search(item) is not None

        db = get_db()
        db.create_function("REGEXP", 2, regexp)

        try:
            while True:
                cursor = db.cursor()
                whitelist = '|'.join(self.whitelist)
                ignorelist = '|'.join(self.ignorelist)

                urls = cursor.execute(
                    """
                    SELECT url FROM urls WHERE scraped_at is null AND url REGEXP ? AND url not REGEXP ?;
                    """,
                    (whitelist, ignorelist)
                ).fetchmany(100)

                for url in urls:
                    db.close()
                    yield url[0]
        except Exception as error:
            print("Error while fetching url from scraper database: ", error)
