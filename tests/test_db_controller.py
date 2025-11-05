import roker.controllers.db_controller as d
from datetime import datetime

start_time_1 = datetime.now()
start_time_2 = datetime.now()

agent_1: d.Agent = d.Agent(
    container_name="test name 1",
    container_id="test id 1",
    port_number=1234,
    start_time=start_time_1)

agent_2: d.Agent = d.Agent(
    container_name="test name 2",
    container_id=" test name 2",
    port_number=5678,
    start_time=start_time_2)


class Test_DB_controller:
    def test_connection(self):
        """
        Basic connection test
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

    def test_add_new_agent_not_connected(self):
        """
        Ensures DB_Controller.add_new_agent fails appropriately
        when not connected to DB
        """
        db = d.DB_Controller(in_memory_db=True)
        # missing db.connect() here intentionally
        agent: d.Agent = d.Agent()
        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.SQLITE3_NOT_CONNECT
        assert res[1] is None

    def test_add_new_agent_missing_params(self):
        """
        Ensures that DB_Controller.add_new_agent catches when
        not all parameters have been passed
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        agent: d.Agent = d.Agent()
        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.MISSING_ATTRIBUTE
        assert res[1] == "missing container_name"

        agent.container_name = "test container name"
        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.MISSING_ATTRIBUTE
        assert res[1] == "missing container_id"

        agent.container_id = "test conatiner id"
        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.MISSING_ATTRIBUTE
        assert res[1] == "missing start_time"

        agent.start_time = datetime.now()
        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.MISSING_ATTRIBUTE
        assert res[1] == "missing port_number"

        agent.port_number = 1234
        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] != d.DB_new_agent_status.MISSING_ATTRIBUTE

    def test_add_new_agent_bad_attribute_types(self):
        """
        Ensures that DB_Controller.add_new_agent catches when a param
        is of the wrong type.
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        agent: d.Agent = d.Agent(
            container_name=1234,
            container_id=1234,
            port_number="1234",
            start_time=1234)

        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.BAD_ATTRIBUTE_TYPE
        assert res[1] == ("bad 'container_name' type, expected"
                          " str but got: <class 'int'>")

        agent.container_name = "test"
        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.BAD_ATTRIBUTE_TYPE
        assert res[1] == ("bad 'container_id' type, expected"
                          " str but got: <class 'int'>")

        agent.container_id = "test"
        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.BAD_ATTRIBUTE_TYPE
        assert res[1] == ("bad 'start_time' type, expected"
                          " datetime but got: <class 'int'>")

        agent.start_time = datetime.now()
        res = db.add_new_agent(agent)

        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.BAD_ATTRIBUTE_TYPE
        assert res[1] == ("bad 'port_number' type, expected"
                          " int but got: <class 'str'>")

    def test_add_new_agent(self):
        """
        Assert DB_Controller.add_new_agent Sucessfuly adds agent
        to db.
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        res = db.add_new_agent(agent_1)
        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.SUBMITTED
        assert type(res[1]) is type(int())
        assert res[1] == 1  # row id

        res = db.add_new_agent(agent_2)
        assert len(res) == 2
        assert res[0] == d.DB_new_agent_status.SUBMITTED
        assert type(res[1]) is type(int())
        assert res[1] == 2  # row id

    def test_no_result_get_agent_data_w_int(self):
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        res = db.get_agent_data(1)
        assert res[0] == d.DB_query_status.NO_RESULT
        assert res[1] is None

    def test_no_result_get_agent_data_w_str(self):
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        res = db.get_agent_data("test name 1")
        assert res[0] == d.DB_query_status.NO_RESULT
        assert res[1] is None

    def test_successfuly_get_agent_data_with_int(self):
        """
        ROW ID TEST

        Asserts that DB_Controller.add_new_agent adds Agent data
        to the DB correctly, then DB_Controller.get_agent_data gets
        Agnet data via row id and parses DB query correctly.

        Full DB pipeline test.
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        id = db.add_new_agent(agent_1)[1]
        res: (d.DB_query_status, d.Agent) = db.get_agent_data(id)
        res_status = res[0]
        res_agent = res[1]

        assert res_status == d.DB_query_status.SUCCESS
        assert isinstance(res_agent, d.Agent)
        assert res_agent.id == 1
        assert res_agent.container_name == "test name 1"
        assert res_agent.container_id == "test id 1"
        assert res_agent.port_number == 1234
        assert res_agent.port_number == 1234
        assert res_agent.start_time == start_time_1.isoformat()
        assert not res_agent.active
        assert res_agent.team_members is None
        assert res_agent.team_name is None

    def test_successfuly_get_agent_data_with_str(self):
        """
        CONTAINER ID TEST

        Asserts that DB_Controller.add_new_agent adds Agent data
        to the DB correctly, then DB_Controller.get_agent_data gets
        Agnet data via container id and parses DB query correctly.

        Full DB pipeline test.
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        db.add_new_agent(agent_1)
        res: (d.DB_query_status, d.Agent) = db.get_agent_data("test id 1")
        res_status = res[0]
        res_agent = res[1]

        assert res_status == d.DB_query_status.SUCCESS
        assert isinstance(res_agent, d.Agent)
        assert res_agent.id == 1
        assert res_agent.container_name == "test name 1"
        assert res_agent.container_id == "test id 1"
        assert res_agent.port_number == 1234
        assert res_agent.port_number == 1234
        assert res_agent.start_time == start_time_1.isoformat()
        assert not res_agent.active
        assert res_agent.team_members is None
        assert res_agent.team_name is None

    def test_update_agent_data_team_members(self):
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        id = db.add_new_agent(agent_1)[1]
        assert id == 1

        # Assert team_members is in fact None
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS
        assert get_body.team_members is None

        # Upate
        (res_status, res_body) = db.update_agent_data(id, {
            "team_members": "test"
        })
        assert res_status == d.DB_query_status.SUCCESS
        assert res_body is None

        # Assert team_members has been updated
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS
        assert get_body.team_members == "test"

    def test_update_agent_data_team_name(self):
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        id = db.add_new_agent(agent_1)[1]
        assert id == 1

        # Assert team_name is in fact None
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS
        assert get_body.team_name is None

        # Upate
        (res_status, res_body) = db.update_agent_data(id, {
            "team_name": "test"
        })
        assert res_status == d.DB_query_status.SUCCESS
        assert res_body is None

        # Assert team_name has been updated
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS
        assert get_body.team_name == "test"

    def test_update_agent_data_active(self):
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        id = db.add_new_agent(agent_1)[1]
        assert id == 1

        # Assert active is in fact False
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS
        assert not get_body.active

        # Upate
        (res_status, res_body) = db.update_agent_data(id, {
            "active": True
        })
        assert res_status == d.DB_query_status.SUCCESS
        assert res_body is None

        # Assert active has been updated
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS
        assert get_body.active

    def test_update_agent_data_port_number(self):
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        id = db.add_new_agent(agent_1)[1]
        assert id == 1

        # Assert port_number is in fact False
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS
        assert get_body.port_number == agent_1.port_number

        # Upate
        (res_status, res_body) = db.update_agent_data(id, {
            "port_number": 5678
        })
        assert res_status == d.DB_query_status.SUCCESS
        assert res_body is None

        # Assert port_number has been updated
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS
        assert get_body.port_number == 5678

    def test_update_agent_data_mult_w_int_id(self):
        """
        ROW ID TEST

        Tests DB_Controller.update_agent_data updates multiple
        fields with the row id.
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        id = db.add_new_agent(agent_1)[1]
        assert id == 1

        # Assert default input
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS

        assert get_body.team_members is None
        assert get_body.team_name is None
        assert not get_body.active
        assert get_body.port_number == agent_1.port_number

        # Upate
        (res_status, res_body) = db.update_agent_data(id, {
            "team_members": "test members",
            "team_name": "test name",
            "active": True,
            "port_number": 5678
        })
        assert res_status == d.DB_query_status.SUCCESS
        assert res_body is None

        # Assert port_number has been updated
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS
        assert get_body.team_members == "test members"
        assert get_body.team_name == "test name"
        assert get_body.active
        assert get_body.port_number == 5678

    def test_update_agent_data_mult_w_str_id(self):
        """
        CONTAINER ID TEST

        Tests DB_Controller.update_agent_data updates multiple
        fields with the container id.
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        db.add_new_agent(agent_1)

        # Assert default input
        (get_status, get_body) = db.get_agent_data("test id 1")
        assert get_status == d.DB_query_status.SUCCESS

        assert get_body.team_members is None
        assert get_body.team_name is None
        assert not get_body.active
        assert get_body.port_number == agent_1.port_number

        # Upate
        (res_status, res_body) = db.update_agent_data("test id 1", {
            "team_members": "test members",
            "team_name": "test name",
            "active": True,
            "port_number": 5678
        })
        assert res_status == d.DB_query_status.SUCCESS
        assert res_body is None

        # Assert port_number has been updated
        (get_status, get_body) = db.get_agent_data("test id 1")
        assert get_status == d.DB_query_status.SUCCESS
        assert get_body.team_members == "test members"
        assert get_body.team_name == "test name"
        assert get_body.active
        assert get_body.port_number == 5678

    def test_update_agent_data_extra_failure(self):
        """
        Ensures DB_Controller.update_agent_data fails when passed
        additional entries into the data dict.
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        id = db.add_new_agent(agent_1)[1]
        assert id == 1

        # Assert default input
        (get_status, get_body) = db.get_agent_data(id)
        assert get_status == d.DB_query_status.SUCCESS

        (res_status, res_body) = db.update_agent_data(id, {
            "team_members": "test members",
            "team_name": "test name",
            "active": True,
            "port_number": 5678,
            "extra_attribute": "test"
        })

        assert res_status == d.DB_query_status.BAD_PARAM_TYPE
        assert res_body == ("Bad 'data', unexpected key. Got"
                            " 'extra_attribute : test'")

    def test_update_agent_data_no_param_failure(self):
        """
        Ensures DB_Controller.update_agent_data fails appropriately when
        not given the proper parameters.
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        (res_status, res_body) = db.update_agent_data(1, {})

        assert res_status == d.DB_query_status.MISSING_PARAM

        (res_status, res_body) = db.update_agent_data(1, data=None)

        assert res_status == d.DB_query_status.MISSING_PARAM

    def test_update_agent_data_wrong_id(self):
        """
        Ensures DB_Controller.update_agent_data fails appropriately when
        given a bad (non existent) id.
        """
        db = d.DB_Controller(in_memory_db=True)
        assert db.connect() == d.DB_connect_status.OK

        (res_status, res_body) = db.update_agent_data(
            1, {"team_members": "test"})

        assert res_status == d.DB_query_status.QUERY_FAILED
        assert res_body == ("Failed to update. Most likely caused by the agent"
                            " '1' not existing in the agents table.")
