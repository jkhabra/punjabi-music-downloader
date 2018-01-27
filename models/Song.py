from datetime import datetime


class Song():
    def __init__(self, name, lyrics, album_id, poster_img_url, release_date,
                 youtube_id, artist_ids=[]):
        self.name = name
        self.lyrics = lyrics
        self.album_id = album_id
        self.poster_img_url = poster_img_url
        self.release_date = release_date
        self.youtube_id = youtube_id
        self.artist_ids = artist_ids

    def _absorb_db_row(self, row, cursor):
        self.id = row[0]
        self.name = row[1]
        lyrics = row[2]
        album_id = row[3]
        poster_img_url = row[4]
        release_date = row[5]
        youtube_id = row[8]

        if not lyrics and self.lyrics:
            lyrics = self.lyrics
            self.update_changes(cursor, "lyrics", self.lyrics)

        if not album_id and self.album_id:
            album_id = self.album_id
            self.update_changes(cursor, "album_id", self.album_id)

        if not poster_img_url and self.poster_img_url:
            poster_img_url = self.poster_img_url
            self.update_changes(cursor, 'poster_img_url', self.poster_img_url)

        if not release_date and self.release_date:
            release_date = self.release_date
            self.update_changes(cursor, "release_date", self.release_date)

        if not youtube_id and self.youtube_id:
            youtube_id = self.youtube_id
            self.update_changes(cursor, 'youtube_id', self.youtube_id)

        self.lyrics = lyrics
        self.album_id = album_id
        self.poster_img_url = poster_img_url
        self.release_date = release_date
        self.youtube_id = youtube_id

    def check_duplicate(self, cursor):
        """
        Returns row from database if song with same name and album_id exists.
        """
        for artist_id in self.artist_ids:
            duplicate_row = cursor.execute(
                """
                SELECT song.* FROM song
                INNER JOIN song_artist ON song_artist.song_id = song.id
                WHERE song.name = ? AND song_artist.artist_id = ?;
                """,
                (self.name, artist_id)
            ).fetchone()

            if not duplicate_row:
                return duplicate_row

        self._absorb_db_row(duplicate_row, cursor)
        return duplicate_row

    def update_changes(self, cursor, column_name, value):
        """
        Update database record with `column_name` to new `value`
        """
        try:
            cursor.execute(
                """
                UPDATE song SET {} = ?, updated_at = ? WHERE id = ?;
                """
                .format(column_name), (value, datetime.today(), self.id)
            )
        except Exception as error:
            print('Error occurred while updating song {}'
                  .format(column_name), error)
            raise error

    def insert(self, cursor):
        """
        Insert song to database. Fail if song already exists
        """
        if self.check_duplicate(cursor):
            return self

        try:
            id = cursor.execute(
                """
                INSERT INTO song (
                   name,
                   lyrics,
                   album_id,
                   poster_img_url,
                   release_date,
                   youtube_id
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """, (
                    self.name,
                    self.lyrics,
                    self.album_id,
                    self.poster_img_url,
                    self.release_date,
                    self.youtube_id
                )
            ).lastrowid
        except Exception as error:
            print("Error while inserting song: ", error)
            raise error

        self.id = id

        return self
