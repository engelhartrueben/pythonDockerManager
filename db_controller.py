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
        in_memory_db: bool = False
    ):
        self._db_name: str = db_name
        self._con: sqlite3.Connection = None
        self._in_memory_db: bool = in_memory_db

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

        if self._in_memory_db:
            try:
                self._con = sqlite3.connect(":memory:")
            except Exception as e:
                print(f"DB connection error: {e}")
                return DB_connect_status.H_FAIL
        else:
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
            DB_new_agent_status, str | int | None):
        """
        Adds a new agent to the agent table. Requires Agent object.

        Checks for strict typing and expected attributes.

        @return a tuple, where the first index is the enum DB_new_agent_status,
        and the secont index is either None, an error message, or the id of
        the agent.

        Potential return structures:
        (DB_new_agent_status.SUBMITTED, int):
            Sucessfuly submitted new agent. Is returned with an int
            referencing, its id in the agents table.

        (DB_new_agent_status.SQLITE3_NOT_CONNECT, None):
            Connection object does not exist

        (DB_new_agent_status.NOT_A_SQLITE_CONNECTION_OBJ, None):
            Expected connection object, got something else

        (DB_new_agent_status.MISSING_ATTRIBUTE, str):
            There is a missing attribute. Is returned with a str
            with a message referring to the attribute missing.

        (DB_new_agent_status.BAD_ATTRIBUTE_TYPE, str):
            An Agent attribute was the wrong type. Is returned with
            a str with a message referring to the attribute with the
            wrone type.

        (DB_new_agent_status.FAILED_EXECUTION, str):
            Adding an agent to the agents table failed. Is returned with
            str with a message as to what failed.
        """
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
            DB_query_status, int | str | None):
        """
        Gets agent data from sqlite3 database from agent it.
        Expects only ever one result

        TODO: Implement
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

        # if not (type(agent_id) is int or type(agent_id) is str):
        #     return (DB_query_status.BAD_PARAM_TYPE,
        #             "bad 'agent_id' type, expected (int | str) but got: "
        #             f"{type(agent_id)}")

        cur: sqlite3.Cursor = self._con.cursor()
        query_str: str

        match agent_id:
            case str():
                query_str = f"SELECT * FROM agents WHERE container_id='{
                    agent_id}';"
            case int():
                query_str = f"SELECT * FROM agents WHERE id={
                    agent_id};"
            case _:
                return (DB_query_status.BAD_PARAM_TYPE,
                        "bad 'agent_id' type, expected (int | str) but got: "
                        f"{type(agent_id)}")

        try:
            data = cur.execute(query_str).fetchall()
        except Exception as e:
            cur.close()
            return (DB_query_status.QUERY_FAILED, e)

        cur.close()

        match len(data):
            case 0: return (DB_query_status.NO_RESULT,
                            None)
            case 1: return (DB_query_status.SUCCESS,
                            self._parse_agent_data(data[0]))
            case _: return (DB_query_status.TOO_MANY_RESULTS,
                            None)

    def update_agent_data(self, agent_id: int | str, data: dict) -> (
            DB_query_status, None | str):
        """
        Updates an agents data under the agent table.
        Can be queried by either `id`, or `container_id`.
        If `agent_id` is of type `int`, it is queried by `id`.
        If `agent_id` is of type `str`, it is queried by `container_id`.

        @return a tuple, with the first index always being `DB_query_status`,
        and the second index either being `None`, or an
        error message depening.

        Potential return structures:
        `(DB_query_status.SUCCESS, None)`:
            Query suceeded.
            It is returned with an Agent dataclass

        `(DB_query_status.SQLITE3_NOT_CONNECT, None)`:
            connection object does not exist

        `(DB_query_status.NOT_A_SQLITE_CONNECTION_OBJ, None)`:
            expected connection object, got something else

        `(DB_query_stats.MISSING PARAM, str)`:
            Missing a necessary parameter.
            It is returned with a str stating what param is missing.

        `(DB_query_status.BAD_PARAM_TYPE, str)`:
            Param has unexpected type.
            It is returned with a str stating unexpected param type.

        `(DB_query_status.QUERY_FAILED, str)`:
            Query failed for some reason.
            It is returned wiht a str stating query error.
        """
        if self._con is None:
            return (DB_query_status.SQLITE3_NOT_CONNECT, None)

        if not isinstance(self._con, sqlite3.Connection):
            return (DB_query_status.NOT_A_SQLITE_CONNECTION_OBJ, None)

        if agent_id is None:
            return (DB_query_status.MISSING_PARAM, "missing agent_id")

        if data is None:
            return (DB_query_status.MISSING_PARAM, "missing data")

        if not isinstance(data, dict):
            return (DB_query_status.BAD_PARAM_TYPE,
                    "bad 'data' type, expected dict but got:"
                    f" {type(data)}")

        cur: sqlite3.Cursor = self._con.cursor()

        # The string to be executed. Built on top of.
        query_str: str = "UPDATE agents SET "

        # Part of query_str; What the query is matching on (container_id | id)
        match_str: str

        # The amount of columns we are updating in a row
        # Needed for comma formatting during SET
        update_count: int = 0

        match agent_id:
            case str():
                match_str = f"WHERE container_id='{agent_id}'"
            case int():
                match_str = f"WHERE id={agent_id}"
            case _:
                return (DB_query_status.BAD_PARAM_TYPE,
                        "bad 'agent_id' type, expected (int | str) but got: "
                        f"{type(agent_id)}")

        for k, v in data.items():
            if update_count >= 1 and update_count != len(data):
                query_str += ", "
            match k:
                case "team_members":
                    query_str += f"team_members='{v}'"
                case "team_name":
                    query_str += f"team_name='{v}'"
                case "active":
                    query_str += f"active={v}"
                case "port_number":
                    query_str += f"port_number={v}"
                case _:
                    return (DB_query_status.BAD_PARAM_TYPE,
                            f"Bad 'data', unexpected key. Got '{k} : {v}'")
            update_count += 1

        query_str += f" {match_str};"

        try:
            cur.execute(query_str)
        except Exception as e:
            self._con.rollback()
            return (DB_query_status.QUERY_FAILED, e)

        cur.close()
        match cur.rowcount:
            case 0:
                self._con.rollback()
                return (DB_query_status.QUERY_FAILED,
                        "Failed to update. Most likely caused by the agent "
                        f"'{agent_id}' not existing in the agents table.")
            case 1:
                self._con.commit()
                return (DB_query_status.SUCCESS, None)

    def agent_to_json(self, agent: Agent) -> str:
        pass

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

    def _parse_agent_data(self, data: tuple) -> Agent:
        """
        Parses the return from querying the agents table for an agent into
        an Agent object.

        Does not have strict typing.

        @returns the Agent object.

        Can return an empty agent for two reasons:
            1) data is not of type tuple
            2) len of data is not 8
        """
        agent: Agent = Agent()

        if type(data) is not tuple:
            print("Failed to parse Agent data."
                  f"Expected data to be of type tuple, but got {type(data)}.")
            return agent

        if len(data) != 8:
            print("Failed to parse Agent data."
                  f"Expect len of 8, got {len(data)}.")
            return agent

        agent.id = data[0]
        agent.container_name = data[1]
        agent.container_id = data[2]
        agent.start_time = data[3]
        agent.team_name = data[4]
        agent.team_members = data[5]
        agent.port_number = data[6]
        agent.active = data[7]
        return agent


if __name__ == "__main__":
    db = DB_Controller(in_memory_db=True)
    db.connect()

    agent: Agent = Agent()
    agent.container_id = "test"
    agent.container_name = "a container"
    agent.port_number = 1234
    agent.start_time = datetime.now()

    print(db.add_new_agent(agent))

    agent_data: (DB_query_status, Agent | str) = db.get_agent_data(1)
    print(agent_data)
    agent_data = db.get_agent_data("test")
    print(agent_data)

    print(db.update_agent_data(
        "test", {"team_members": "Ruby Engelhart, Tom",
                 "team_name": "Peaches", "active": 1, "port_number": 5432}))

    agent_data = db.get_agent_data("test")
    print(agent_data)
