class SongArtist():
    def __init__(self, song_id, artist_id):
        self.song_id = song_id
        self.artist_id = artist_id

    def _absorb_db_row(self, row):
        self.id = row[0]
        self.song_id = row[1]
        self.artist_id = row[2]

    def check_duplicate(self, cursor):
        """
        Returns row from database if song_artist with same song_id and artist_id exists.
        """
        duplicate_row = cursor.execute(
            """
            SELECT * FROM song_artist WHERE song_id = ? AND artist_id = ?
            """,
            (self.song_id, self.artist_id)
        ).fetchone()

        if duplicate_row:
            self._absorb_db_row(duplicate_row)

        return duplicate_row

    def insert(self, cursor):
        """
        Insert song_artist to database. Fail if song_artist already exists
        """
        if self.check_duplicate(cursor):
            return self

        try:
            id = cursor.execute(
                """
                INSERT INTO song_artist (song_id, artist_id)
                VALUES (?, ?);
                """,
                (self.song_id, self.artist_id)
            ).lastrowid
        except Exception as error:
            print("Error while inserting song_artist: ", error)
            raise error

        self.id = id

        return self
