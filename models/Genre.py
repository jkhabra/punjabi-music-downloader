class Genre():
    def __init__(self, name):
        self.name = name

    def _absorb_db_row(self, row):
        self.id = row[0]
        self.name = row[1]

    def check_duplicate(self, cursor):
        """
        Returns row from database if genre with same name exists.
        """
        duplicate_row = cursor.execute(
            """
            SELECT * FROM genre WHERE name = ?;
            """,
            (self.name,)
        ).fetchone()

        if duplicate_row:
            self._absorb_db_row(duplicate_row)

        return duplicate_row

    def insert(self, cursor):
        """
        INSERT genre to database. Fail if genre already exists
        """
        if self.check_duplicate(cursor):
            return self

        try:
            id = cursor.execute(
                """
                INSERT INTO genre (name)
                VALUES (?);
                """,
                (self.name,)
            ).lastrowid
        except Exception as error:
            print("Error While inserting genre: ", error)
            raise error

        self.id = id

        return self
