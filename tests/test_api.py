"""
Works locally but unable to get working with GH actions.

Unsure how to test this anyways at the moment. Holding off for some time.
"""

# from fastapi.testclient import TestClient
# import roker.api.main as api
# import pytest
#
# client = TestClient(api.app)
#
#
# class Test_api:
#
#     @pytest.mark.skip(reason="Not mature enough")
#     def test_get_all_agents(self):
#         res = client.get("/get_all_agents")
#         assert res.json() == {"msg": "Hello World"}
#         assert res.status_code == 200
