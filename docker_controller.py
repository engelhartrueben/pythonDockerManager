from enum import IntEnum
from dataclasses import dataclass
from time import sleep
from port_controller import PortController, PortAssignment
import docker


class DC_SC(IntEnum):
    FAILED_TO_START_DOCKER_C = -5
    FAILED_TO_KILL_DOCKER_C = -4
    BAD_GH_TEAM_NAME = -3
    BAD_GH_TEAM_MEMBER = -2
    BAD_GH_URL = -1
    OK = 0


@dataclass
class ActiveContainer:
    port_number: int
    container: docker.api.container


@dataclass
class ContainerCreation:
    status: DC_SC
    port: int = -1
    container_id: str = ""


class DockerController:
    def __init__(self):
        self.active_containers: {str: ActiveContainer} = {}
        self.pc = PortController()
        self.client = docker.from_env()

    def __iter__(self):
        return self

    async def create_new_container(self, gh_url: str) -> ContainerCreation:
        """Creates a new container."""
        print("Attempting to build new agent.")
        # Get available TCP port
        # THEN
        # Create Docker Container
        #   Copy over some bash script to pull down repo, compile, and run jar
        #   ^^ This will use the "volume" paramater
        # Return ContainerCreation

        port_task = await self.pc.get_available_TCP_port()
        # team_name_task = tg.create_task(self.gh.get_gh_team_name(gh_url))
        # team_member_task = tg.create_task(
        #     self.gh.get_gh_team_member_names(gh_url))

        # # ... this will be going away lol
        # if (team_name_task.result().status != GH_SC.OK
        #         or team_member_task.result().status != GH_SC.OK):
        #     return ContainerCreation(status=DC_SC.BAD_GH_URL)

        res = await self._run_container(
            gh_url, port_task)

        if res is None:
            print("FAILED to build new agent")
            return ContainerCreation(
                status=DC_SC.FAILED_TO_START_DOCKER_C
            )

        # # TODO: Change this to db
        # self.active_containers[
        #     team_name_task.result().response] = ActiveContainer(
        #     port_number=port_task.result().port,
        #     container=res
        # )

        return ContainerCreation(
            status=DC_SC.OK,
            port=port_task.port,
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
            self.client.containers.get(container_id).kill()
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
            pa: PortAssignment) -> docker.api.container:
        """Starts the docker container for agent poker api"""
        print("[DockerController._run_container] INCOMPLETE")

        # Free socket.. should check for failure tbh
        pa.socket.close()

        try:
            return self.client.containers.run(
                'alpine',
                auto_remove=False,
                command=['./test.sh'],
                detach=True,
                environment=[f"GH_REPO_URL={gh_url}"],
                mem_limit="128g",
                network_mode="bridge",
                ports={
                    '8080/tcp':
                    pa.port
                },
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 1
                },
                volumes={
                    '/home/ruby/development/ruby_poker/python_docker/test.sh': {
                        'bind': '/home/test.sh',
                        'mode': 'ro'
                    }
                },
                working_dir="/home/",
            )
        except docker.errors.ContainerError as e:
            print(f"[_run_container] Container Error: {e}")
            return None
        except docker.errors.ImageNotFound as e:
            print(f"[_run_container] image not found: {e}")
            return None
        except docker.errors.APIError as e:
            print(f"[_run_container] APIError: {e}")
            return None
