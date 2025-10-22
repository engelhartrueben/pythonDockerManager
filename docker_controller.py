from enum import Enum
from dataclasses import dataclass
from time import sleep
from port_controller import PortController
from socket import socket
import asyncio


class DC_SC(Enum):
    BAD_GH_URL = -1
    OK = 1


@dataclass
class ActiveContainer:
    socket: socket
    port_number: int
    container_name: str


@dataclass
class ContainerCreation:
    status: DC_SC
    port: int = -1


class DockerController:
    def __init__(self):
        self.active_containers: {str: ActiveContainer} = {}
        self.pc = PortController()

    def __iter__(self):
        return self

    async def create_new_container(self, gh_url: str) -> ContainerCreation:
        """Creates a new container."""

        sleep(1)
        print("[DockerController.create_new_container] UNIMPLEMENTED")

        async with asyncio.TaskGroup() as tg:
            port_task = tg.create_task(self.pc.get_available_TCP_port())
        # Get team name
        # Get team member names
        # Get available TCP port
        # THEN
        # Create Docker Container
        # Return ContainerCreation
        self.active_containers.update({'test': ActiveContainer(
            socket=port_task.result().socket,
            port_number=port_task.result().port,
            container_name='test'
        )})

        return ContainerCreation(
            status=DC_SC.OK,
            port=port_task.result().port
        )

    def get_active_containers(self) -> {ActiveContainer}:
        """
        Returns a dictionary of all active containers
        """
        print(
            "[DockerController.get_active_containers]"
            " ActiveContainers is probably empty"
        )
        return self.active_containers

    # unsure if I want this private or not
    async def kill_conatiner(self, container_id: str) -> DC_SC:
        """Kills a given container"""
        sleep(1)
        print("[DockerController._kill_conatiner] UNIMPLEMENTED")
        return DC_SC.OK

    async def restart_conatiner(self, container_id: str) -> DC_SC:
        """Restarts a given container"""
        sleep(1)
        print("[DockerController.restart_conatiner] UNIMPLEMENTED")
        return DC_SC.OK
