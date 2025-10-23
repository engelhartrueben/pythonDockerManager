from enum import Enum
from dataclasses import dataclass
from time import sleep
from port_controller import PortController, PortAssignment
from gh_controller import GHController, GH_SC
import asyncio
import docker


class DC_SC(Enum):
    FAILED_TO_START_DOCKER_C = -5
    FAILED_TO_KILL_DOCKER_C = -4
    BAD_GH_TEAM_NAME = -3
    BAD_GH_TEAM_MEMBER = -2
    BAD_GH_URL = -1
    OK = 1


@dataclass
class ActiveContainer:
    port_number: int
    container: docker.api.container


@dataclass
class ContainerCreation:
    status: DC_SC
    port: int = -1
    team_name: str = ""
    team_members: str = ""
    container_id: str = ""


class DockerController:
    def __init__(self):
        self.active_containers: {str: ActiveContainer} = {}
        self.pc = PortController()
        self.gh = GHController()
        self.client = docker.from_env()

    def __iter__(self):
        return self

    async def create_new_container(self, gh_url: str) -> ContainerCreation:
        """Creates a new container."""

        print("[DockerController.create_new_container] PARTIAL IMPLEMENT")

        # Get team name
        # Get team member names
        # Get available TCP port
        # THEN
        # Create Docker Container
        # Return ContainerCreation

        async with asyncio.TaskGroup() as tg:
            port_task = tg.create_task(self.pc.get_available_TCP_port())
            team_name_task = tg.create_task(self.gh.get_gh_team_name(gh_url))
            team_member_task = tg.create_task(
                self.gh.get_gh_team_member_names(gh_url))

        # If either gh task fails, return bad container?
        # Yes, I want to know which team and who is on it at all times
        # TODO: Handle GH errors and bubble back through API response
        if (team_name_task.result().status != GH_SC.OK
                or team_member_task.result().status != GH_SC.OK):
            return ContainerCreation(status=DC_SC.BAD_GH_URL)

        res = await self._run_container(
            gh_url, port_task.result())

        if res is None:
            return ContainerCreation(
                status=DC_SC.FAILED_TO_START_DOCKER_C
            )

        # python linter can suck it
        self.active_containers[
            team_name_task.result().response] = ActiveContainer(
            port_number=port_task.result().port,
            container=res
        )

        return ContainerCreation(
            status=DC_SC.OK,
            port=port_task.result().port,
            team_name=team_name_task.result().response,
            team_members=team_member_task.result().response,
            container_id=res.id
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
        print("[DockerController._kill_conatiner] UNIMPLEMENTED")
        try:
            print(f"Attempting to kill {container_id}")
            self.client.containers.get(container_id).remove()
        except docker.errors.APIError as e:
            print(e)
            return DC_SC.FAILED_TO_KILL_DOCKER_C
        print(f"Sucessfuly killed {container_id}")
        return DC_SC.OK

    async def restart_conatiner(self, container_id: str) -> DC_SC:
        """Restarts a given container"""
        sleep(1)
        print("[DockerController.restart_conatiner] UNIMPLEMENTED")
        return DC_SC.OK

    async def _run_container(
            self,
            gh_url: str,
            pa: PortAssignment) -> docker.api.container | None:
        """Starts the docker container for agent poker api"""
        print("[DockerController._run_container] INCOMPLETE")

        # Free socket.. should check for failure tbh
        pa.socket.close()

        try:
            container = self.client.containers.run(
                'eclipse-temurin',
                mem_limit="128g",
                ports={'8000/tcp': pa.port},
                restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
                detach=True
            )

            # WARN: If detach is set to False, returns the logs.
            # when detach is set to True, we get the container object!
            # We want this!
            return container
        except docker.errors.ContainerError:
            print("[_run_container] Container Error")
            return None
        except docker.errors.ImageNotFound:
            print("[_run_container] image not found!")
            return None
        except docker.errors.APIError as e:
            print(f"[_run_container] APIError: {e}")
            return None
