import os
from pathlib import Path
from dotenv import load_dotenv
import sqlite3
from enum import IntEnum

load_dotenv()

DEFAULT_SQLITE3_DB_DIR = "/.ruby_poker/"
DEFAULT_SQLITE3_DB_NAME = "database.db"

# https://docs.python.org/3/library/sqlite3.html#sqlite3.threadsafety
sqlite3.threadsafety = 3


class DB_initialize_status(IntEnum):
    FAILED_TABLE_INTIALIZATION = -3
    NOT_A_SQLITE_CONNECTION_OBJ = -2
    SQLITE3_NOT_CONNECT = -1
    READY = 0


class DB_connect_status(IntEnum):
    H_FAIL = -1
    OK = 0


class DB_Controller:
    def __init__(
        self,
        db_name: str = DEFAULT_SQLITE3_DB_NAME,
    ):
        self._db_name: str = db_name
        self._con: sqlite3.Connection = None

    # PUBLIC

    def connect(self) -> DB_connect_status:
        """
        Attempt to connect to sqlite3 database.

        In the event that the db file does not exist, it will be automatically
        created.

        @return: DB_connect_status
            DB_connect_status.H_FAIL is a program terminating failure
        """
        home_dir = os.path.expanduser("~")

        # Create .ruby_poker directory to store database
        Path(home_dir +
             DEFAULT_SQLITE3_DB_DIR).mkdir(parents=True, exist_ok=True)

        try:
            self._con = sqlite3.connect(
                home_dir + DEFAULT_SQLITE3_DB_DIR + self._db_name)
        except Exception as e:
            print(f"DB connection error: {e}")
            return DB_connect_status.H_FAIL

        init: (DB_initialize_status, None | str) = self._initialize_db()

        # Match case, but we need to preserve the second indx of the tuple
        if init[0] is DB_initialize_status.SQLITE3_NOT_CONNECT:
            """
            self.con should be a con object at this point.
            If not, something has gone horribly wrong.
            """
            print("sqlite3 db is not connected.\n"
                  "Something has gone horribly wrong.")
            return DB_connect_status.H_FAIL

        elif init[0] is DB_initialize_status.NOT_A_SQLITE_CONNECTION_OBJ:
            """type checking."""
            print("Not a connection object.\n"
                  "Something has gone horribly wrong.")
            return DB_connect_status.H_FAIL

        elif init[0] is DB_initialize_status.FAILED_TABLE_INTIALIZATION:
            print(f"Failed to initialize table: {init.index(1)}")
            return DB_connect_status.H_FAIL

        elif init[0] is DB_initialize_status.READY:
            print("sqlite3 db is ready")
            return DB_connect_status.OK

    def get_db_name(self) -> str:
        return self._db_name

    def get_db_dir(self) -> str:
        return self._db_dir

        # PRIVATE

    def _initialize_db(self) -> (DB_initialize_status, str | None):
        """
        Initializes the database file and creates the 'agents' table
        if it does not exist.

        @reaturn a tuple containing the status of the intialization,
        and any relevant error message

        DB_initialize_status.SQLITE3_NOT_CONNECT:
            connection object does not exist
        DB_initialize_status.NOT_A_SQLITE_CONNECTION_OBJ:
            expected connection object, got something else
        DB_initialize_status.FAILED_TABLE_INTIALIZATION:
            Failed to intialize the table(s).
            Is returned with a relevant error message.
        DB_initialize_status.READY:
            sqlite3 db and tables are ready
        """
        if self._con is None:
            return (DB_initialize_status.SQLITE3_NOT_CONNECT, None)

        if type(self._con) is not sqlite3.Connection:
            return (DB_initialize_status.NOT_A_SQLITE_CONNECTION_OBJ, None)

        cur = self._con.cursor()

        try:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS agents\
                    (\
                        id              INTEGER PRIMARY KEY,\
                        container_name  TEXT NOT NULL,\
                        container_id    TEXT NOT NULL,\
                        start_time      TEXT NOT NULL,\
                        team_name       TEXT,\
                        team_members    TEXT,\
                        port_number     INT NOT NULL,\
                        active          INT\
                     )"
            )
            return (DB_initialize_status.READY, None)
        except Exception as e:
            return (DB_initialize_status.FAILED_TABLE_INTIALIZATION, e)


if __name__ == "__main__":
    db = DB_Controller()
    db.connect()
