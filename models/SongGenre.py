class SongGenre():
    def __init__(self, song_id, genre_id):
        self.song_id = song_id
        self.genre_id = genre_id

    def _absorb_db_row(self, row):
        self.id = row[0]
        self.song_id = row[1]
        self.genre_id = row[2]

    def check_duplicate(self, cursor):
        """
        Returns row form database if song_genre with same
        song_id and genre_id exists.
        """
        duplicate_row = cursor.execute(
            """
            SELECT * FROM song_genre
            WHERE song_id = ? AND genre_id = ?
            """,
            (self.song_id, self.genre_id)
        ).fetchone()

        if duplicate_row:
            self._absorb_db_row(duplicate_row)

        return duplicate_row

    def insert(self, cursor):
        """
        Insert song_genre to database.
        Fail if song_genre already exists
        """
        if self.check_duplicate(cursor):
            return self

        try:
            id = cursor.execute(
                """
                INSERT INTO song_genre (song_id, genre_id)
                VALUES (?, ?);
                """,
                (self.song_id, self.genre_id)
            ).lastrowid
        except Exception as error:
            print("Error while inserting song_genre: ", error)
            raise error

        self.id = id

        return self
