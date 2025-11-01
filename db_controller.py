import os
import sqlite3

from enum import IntEnum
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DEFAULT_SQLITE3_DB_DIR = "/.ruby_poker/"
DEFAULT_SQLITE3_DB_NAME = "database.db"


@dataclass
class Agent:
    id: int = -1
    container_name: str = None
    container_id: str = None
    start_time: datetime = None
    team_name: str = None
    team_members: str = None
    port_number: int = -1
    active: bool = -1


# https://docs.python.org/3/library/sqlite3.html#sqlite3.threadsafety
sqlite3.threadsafety = 3


class DB_new_agent_status(IntEnum):
    FAILED_EXECUTION = -5
    BAD_ATTRIBUTE_TYPE = -4
    MISSING_ATTRIBUTE = -3
    NOT_A_SQLITE_CONNECTION_OBJ = -2
    SQLITE3_NOT_CONNECT = -1
    SUBMITTED = 0


class DB_initialize_status(IntEnum):
    FAILED_TABLE_INTIALIZATION = -3
    NOT_A_SQLITE_CONNECTION_OBJ = -2
    SQLITE3_NOT_CONNECT = -1
    READY = 0


class DB_query_status(IntEnum):
    TOO_MANY_RESULTS = -6
    QUERY_FAILED = -5
    BAD_PARAM_TYPE = -4
    MISSING_PARAM = -3
    NOT_A_SQLITE_CONNECTION_OBJ = -2
    SQLITE3_NOT_CONNECT = -1
    SUCCESS = 0
    NO_RESULT = 1


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

    def add_new_agent(self, new_agent: Agent) -> (
            DB_new_agent_status, str | None):

        if self._con is None:
            return (DB_new_agent_status.SQLITE3_NOT_CONNECT, None)

        if type(self._con) is not sqlite3.Connection:
            return (DB_new_agent_status.NOT_A_SQLITE_CONNECTION_OBJ, None)

        # Check that values are there
        if new_agent.container_name is None:
            return (DB_new_agent_status.MISSING_ATTRIBUTE,
                    "missing container_name")
        elif new_agent.container_id is None:
            return (DB_new_agent_status.MISSING_ATTRIBUTE,
                    "missing container_id")
        elif new_agent.start_time is None:
            return (DB_new_agent_status.MISSING_ATTRIBUTE,
                    "missing start_time")
        elif new_agent.port_number is None:
            return (DB_new_agent_status.MISSING_ATTRIBUTE,
                    "missing port_number")

        # Check if values are appropriate type
        if type(new_agent.container_name) is not str:
            return (DB_new_agent_status.BAD_ATTRIBUTE_TYPE,
                    "bad 'container_name' type, expected str but got: "
                    f"{type(new_agent.container_name)}")
        elif type(new_agent.container_id) is not str:
            return (DB_new_agent_status.BAD_ATTRIBUTE_TYPE,
                    "bad 'container_id' type, expected str but got: "
                    f"{type(new_agent.container_id)}")
        elif type(new_agent.start_time) is not datetime:
            return (DB_new_agent_status.BAD_ATTRIBUTE_TYPE,
                    "bad 'start_time' type, expected datetime but got: "
                    f"{type(new_agent.start_time)}")
        elif type(new_agent.port_number) is not int:
            return (DB_new_agent_status.BAD_ATTRIBUTE_TYPE,
                    "bad 'port_number' type, expected int but got: "
                    f"{type(new_agent.port_number)}")

        # check if team name or team members is populated
        if new_agent.team_members is not None:
            print("team_members is populated when it shouldn't be."
                  f"Got: {new_agent.team_members}")
            new_agent.team_members = ""

        if new_agent.team_name is not None:
            print("team_name is populated when it shouldn't be."
                  f"Got: {new_agent.team_name}")
            new_agent.team_name = ""

        if new_agent.active != -1:
            print("active is populated when it shouldn't be."
                  f"Got: {new_agent.active}")

        new_agent.active = int(False)

        cur: sqlite3.Cursor = self._con.cursor()

        try:
            cur.execute("INSERT INTO agents(\
                    container_name, container_id,\
                    start_time, team_name, team_members,\
                    port_number, active)\
                    VALUES(?,?,?,?,?,?,?)", (
                new_agent.container_name,
                new_agent.container_id,
                new_agent.start_time.isoformat(),
                new_agent.team_name,
                new_agent.team_members,
                new_agent.port_number,
                new_agent.active
            ))
        except Exception as e:
            cur.close()
            return (DB_new_agent_status.FAILED_EXECUTION, e)

        self._con.commit()
        id = cur.lastrowid
        cur.close()
        return (DB_new_agent_status.SUBMITTED, id)

    def get_agent_data(self, agent_id: int) -> (
            DB_query_status, int | None):
        """
        Gets agent data from sqlite3 database from agent it.
        Expects only ever one result

        if agent_id is Agent dataclass, query by id = agent_id.id.
        if agent_id is int, query by id = int.
        if agent_id is str, query by container_id = str.

        Future feature: query using agent_id, container_name, or
        container_id.

        @return a tuple, with the first index always being DB_query_status,
        and the second index either being a Agent dataclass, or an
        error message depening.

        Potential return structures:
        (DB_query_status.SUCCESS, Agent):
            Query suceeded.
            It is returned with an Agent dataclass

        (DB_query_status.SQLITE3_NOT_CONNECT, None):
            connection object does not exist

        (DB_query_status.NOT_A_SQLITE_CONNECTION_OBJ, None):
            expected connection object, got something else

        (DB_query_stats.MISSING PARAM, str):
            Missing a necessary parameter.
            It is returned with a str stating what param is missing.

        (DB_query_status.BAD_PARAM_TYPE, str):
            Param has unexpected type.
            It is returned with a str stating unexpected param type.

        (DB_query_status.QUERY_FAILED, str):
            Query failed for some reason.
            It is returned wiht a str stating query error.

        (DB_query_status.NO_RESULT, None):
            Query suceeded, but had no result.

        (DB_query_status.TOO_MANY_RESULTS, None):
            Query produced too many results.
            If seen, something has gone horribly wrong.
        """
        if self._con is None:
            return (DB_query_status.SQLITE3_NOT_CONNECT, None)

        if type(self._con) is not sqlite3.Connection:
            return (DB_query_status.NOT_A_SQLITE_CONNECTION_OBJ, None)

        if agent_id is None:
            return (DB_query_status.MISSING_PARAM, "missing agent_id")

        if type(agent_id) is not int:
            return (DB_query_status.BAD_PARAM_TYPE,
                    "bad 'agent_id' type, expected int but got: "
                    f"{type(agent_id)}")

        cur: sqlite3.Cursor = self._con.cursor()
        try:
            data = cur.execute(
                "SELECT * "
                "FROM agents "
                f"WHERE id = {agent_id};").fetchall()
        except Exception as e:
            cur.close()
            return (DB_query_status.QUERY_FAILED, e)

        cur.close()

        match len(data):
            case 0: return (DB_query_status.NO_RESULT,
                            None)
            case 1: return (DB_query_status.SUCCESS,
                            self._parse_agent_data(data))
            case _: return (DB_query_status.TOO_MANY_RESULTS,
                            None)

        return (DB_query_status.SUCCESS, agent_data)

    def get_db_name(self) -> str:
        return self._db_name

    def get_db_dir(self) -> str:
        return self._db_dir

        # PRIVATE

    def _initialize_db(self) -> (DB_initialize_status, int | str | None):
        """
        Initializes the database file and creates the 'agents' table
        if it does not exist.

        @reaturn a tuple containing the status of the intialization,
        and any relevant error message

        Potential return structures:
        (DB_initialize_status.READY, int):
            sqlite3 db and tables are ready
            It is returned with the id of the agent

        (DB_initialize_status.SQLITE3_NOT_CONNECT, None):
            connection object does not exist

        (DB_initialize_status.NOT_A_SQLITE_CONNECTION_OBJ, None):
            expected connection object, got something else

        (DB_initialize_status.FAILED_TABLE_INTIALIZATION, str):
            Failed to intialize the table(s).
            Is returned with a relevant error message.
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
                        container_name  TEXT NOT NULL UNIQUE,\
                        container_id    TEXT NOT NULL UNIQUE,\
                        start_time      TEXT NOT NULL,\
                        team_name       TEXT,\
                        team_members    TEXT,\
                        port_number     INT NOT NULL,\
                        active          INT\
                     )"
            )
        except Exception as e:
            cur.close(0)
            return (DB_initialize_status.FAILED_TABLE_INTIALIZATION, e)

        # Do i need to commit?
        self._con.commit()
        last_id = cur.lastrowid

        cur.close()
        return (DB_initialize_status.READY, last_id)

    def _parse_agent_data(self, data: list) -> Agent:
        # TODO: Test data is correct format first...
        agent: Agent = Agent()
        agent.container_name = data[0][1]
        agent.container_id = data[0][2]
        agent.start_time = data[0][3]
        agent.team_name = data[0][4]
        agent.team_members = data[0][5]
        agent.port_number = data[0][6]
        agent.active = data[0][7]
        return agent


if __name__ == "__main__":
    db = DB_Controller()
    db.connect()

    agent_data: (DB_query_status, Agent | str) = db.get_agent_data(6)
    print(agent_data)
