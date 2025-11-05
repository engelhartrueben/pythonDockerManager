import roker.controllers.port_controller as pc
import socket
import pytest


class Test_PortController:

    @pytest.mark.asyncio
    async def test_get_a_TCP_port(self):
        """
        Simple test ensure we get a reserved port
        """
        PC = pc.PortController()
        res: pc.PortAssignment = await PC.get_available_TCP_port()
        print(res)
        assert res.status == pc.P_SC.OK
        assert isinstance(res.port, int)
        assert isinstance(res.socket, socket.socket)
