class Mp3s():
    def __init__(self, song_id, url, source, quality):
        self.song_id = song_id
        self.url = url
        self.source = source
        self.quality = quality

    def _absorb_db_row(self, row):
        self.id = row[0]
        self.song_id = row[1]
        self.url = row[2]
        self.source = row[3]
        self.quality = row[4]

    def check_duplicate(self, cursor):
        """
        Returns row from database if mp3s with same url exists.
        """
        duplicate_row = cursor.execute(
            """
            SELECT * FROM mp3s WHERE url = ?
            """,
            (self.url,)
        ).fetchone()

        if duplicate_row:
            self._absorb_db_row(duplicate_row)

        return duplicate_row

    def insert(self, cursor):
        """
        Insert mp3s to database. Fail if mp3s already exists
        """
        if self.check_duplicate(cursor):
            return self

        try:
            id = cursor.execute(
                """
                INSERT INTO mp3s (song_id, url, source, quality)
                VALUES (?,?,?,?);
                """,
                (self.song_id, self.url, self.source, self.quality)
            ).lastrowid
        except Exception as error:
            print("Error while inserting mp3s: ", error)
            raise error

        self.id = id

        return self
