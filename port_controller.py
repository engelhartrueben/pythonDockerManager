from enum import Enum
from dataclasses import dataclass
import socket


class P_SC(Enum):
    FAILED_TO_FIND_PORT = -1
    OK = 1


@dataclass
class PortAssignment:
    """
    status: status code
    port:   port number
    socket: socket object

    WARNING Close socket before assigning to docker container
    """
    status: P_SC
    port: int
    socket: socket.socket


class PortController:
    def __init__(self):
        pass

    async def get_available_TCP_port(self) -> PortAssignment:
        """Reserves a socket"""
        s = socket.socket()
        s.bind(('', 0))
        s.listen(1)
        return PortAssignment(
            status=P_SC.OK,
            port=s.getsockname()[1],
            socket=s
        )
