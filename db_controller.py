import asyncio
import atexit
import time
import os
from dotenv import load_dotenv
# import sqlite3
import docker
from port_controller import PortController as pc

load_dotenv()

DEFAULT_SQLITE3_CONTAINER_NAME = "ruby_poker_sqlite3"


class DB_Controller:
    def __init__(
        self,
        container_name: str = os.getenv("SQLITE3_CONTAINER_NAME")
            or DEFAULT_SQLITE3_CONTAINER_NAME
    ):
        self._conatiner_name: str = container_name
        self._container_object: docker.container = None
        self._port: int = None
        self._client = docker.from_env()

    # PUBLIC

    async def create(self):
        if await self._check_for_container():
            print(f"sqlite3 Container found: Listening on port {self._port}.")
            return None

        print("Creating sqlite3 container.")
        if await self._deploy_container():
            print(f"sqlite3 Container created: Listening on port {
                  self._port}.")
            return None
        else:
            # Figure out what happened lol
            print("Something bad happened")

    def get_logs(self) -> str:
        try:
            logs = self._container_object.logs().decode('utf-8')
        except docker.errors.APIError as e:
            print(f"Failed to get container logs: {e}")
            exit(-1)
        return logs

    def get_port(self) -> int:
        return self._port

    def get_container_name(self) -> str:
        return self._conatiner_name

    def kill(self):
        # self._container_object.kill()
        print(self._container_object.status)

    # PRIVATE

    async def _check_for_container(self) -> bool:
        """
        Checks if a sqlite docker container for this project is already
        up and running.

        Ideally, the container should be stopped atexit.
        If just stopped, start the container and run a quick test?

        TODO:
            Check if container of self._container_name exists
                If exists, find port and assign self._port
        """
        try:
            res = await self._client.containers.get(self._conatiner_name)
            self._container_object = res
            self._gather_container_attributes()
            return True
        except docker.errors.NotFound:
            return False
        except docker.errors.APIError as e:
            print(f"db_controller._check_for_container: APIError {e}")
            return False

    def _gather_container_attributes(self):
        self._port = self._container_object.ports
        print(f"self._port = {self._port}")

    async def _deploy_container(self) -> bool:
        port = await pc().get_available_TCP_port()
        port.socket.close()
        self._port = port.port

        try:
            self._container_object = self._client.containers.run(
                'alpine/sqlite',
                auto_remove=False,
                # command=['./test.sh'],
                detach=True,
                # environment=[f"GH_REPO_URL={gh_url}"],
                mem_limit="128g",  # TODO: Make this a .env
                network_mode="bridge",
                ports={
                    '8080/tcp':
                    port.port
                },
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 3
                },
                # volumes={
                #     '/home/ruby/development/ruby_poker/python_docker/test.sh': {
                #         'bind': '/home/test.sh',
                #         'mode': 'ro'
                #     }
                # },
                working_dir="/home/",
            )
            return True
        except docker.errors.ContainerError as e:
            print(f"[_run_container] Container Error: {e}")
            exit(-1)
        except docker.errors.ImageNotFound as e:
            print(f"[_run_container] image not found: {e}")
            exit(-1)
        except docker.errors.APIError as e:
            print(f"[_run_container] APIError: {e}")
            exit(-1)


async def get():
    db = DB_Controller()
    atexit.register(db.kill)
    await db.create()
    time.sleep(5)
    print(db.get_logs())


if __name__ == "__main__":
    asyncio.run(get())
