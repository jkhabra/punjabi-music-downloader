from datetime import datetime


class Artist():
    def __init__(self, name, artist_type):
        self.name = name
        self.artist_type = artist_type

    def _absorb_db_row(self, row, cursor):
        self.id = row[0]
        name = row[1]

        if name is None and self.name is not None:
            name = self.name
            self.update_name(cursor)

        self.name = name

    def update_name(self, cursor):
        """
        Update row with new name and id
        """
        try:
            cursor.execute(
                """
                UPDATE artist SET name=?, updated_at = ? WHERE id=?
                """, (self.name, datetime.today(), self.id))
        except Exception as error:
            print('Error occurred while updating Artist name', error)
            raise error

    def check_duplicate(self, cursor):
        """
        Returns row from database if artist with same name exists.
        """
        duplicate_row = cursor.execute(
            """
            SELECT * FROM artist WHERE name = ? AND type = ?
            """,
            (self.name, self.artist_type)
        ).fetchone()

        if duplicate_row:
            self._absorb_db_row(duplicate_row, cursor)

        return duplicate_row

    def insert(self, cursor):
        """
        Insert artist to database. Fail if artist already exists
        """
        if self.check_duplicate(cursor):
            return self

        try:
            id = cursor.execute(
                """
                INSERT INTO artist (name, type)
                VALUES (?, ?);
                """,
                (self.name, self.artist_type)
            ).lastrowid
        except Exception as error:
            print("Error while inserting artist: ", error)
            raise error

        self.id = id

        return self
