class PosterImage():
    def __init__(self, cursor):
        self.cursor = cursor

    def select_urls(self):
        """
        Select poster_img_url where local_poster_img_url is null
        """
        try:
            urls = self.cursor.execute(
                """
                SELECT poster_img_url FROM song
                WHERE local_poster_img_url is null;
                """
            ).fetchall()

            return urls
        except Exception as error:
            print("None of the url found: ", error)

    def update(self, url, local_image_url):
        """
        Update LocalPosterImgUrl to database. Fail if url already exists
        """
        try:
            self.cursor.execute(
                """
                UPDATE song SET local_poster_img_url = ?
                WHERE poster_img_url = ?;
                """,
                (local_image_url, url)
            )
        except Exception as error:
            print("Error while updating local_poster_img: ", error)
            raise error
