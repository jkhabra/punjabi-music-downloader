class SongRankings():
    def __init__(self, song_id, artist_id, source, rank, week):
        self.song_id = song_id
        self.artist_id = artist_id
        self.source = source
        self.rank = rank
        self.week = week

    def _absorb_db_row(self, row, cursor):
        self.song_id = row[1]
        self.artist_id = row[2]
        self.source = row[3]
        self.rank = row[4]
        self.week = row[5]

    def check_duplicate(self, cursor):
        """
        Returns row from database if song_rankings with same week exists
        """
        duplicate_row = cursor.execute(
            """
            SELECT * from song_rankings
            WHERE song_id = ? AND artist_id = ? AND week = ?;
            """,
            (self.song_id, self.artist_id, self.week)
        ).fetchone()

        if duplicate_row:
            self._absorb_db_row(duplicate_row, cursor)

        return duplicate_row

    def insert(self, cursor):
        """
        Insert song_rankings to database. Fail if song rankings_already exits
        """
        if self.check_duplicate(cursor):
            return self

        try:
            id = cursor.execute(
                """
                INSERT INTO song_rankings
                (song_id, artist_id, source, rank, week)
                VALUES
                (?, ?, ?, ?, ?);
                """,
                (self.song_id,
                 self.artist_id,
                 self.source,
                 self.rank,
                 self.week)
            ).lastrowid
        except Exception as error:
            print("Error while inserting song_rankings: ", error)
            raise error

        self.id = id

        return self
