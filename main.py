import atexit
import asyncio
from docker_controller import DockerController

dc = DockerController()


async def main():
    task1 = await dc.create_new_container(
        "https://github.com/engelhartrueben/test_repo"
    )
    # to: https://raw.githubusercontent.com/engelhartrueben/test_repo/refs/heads/main/teammembers

    print(f"Assigned port: {task1.port}")
    print(f"Team name: {task1.team_name}")
    print(f"Team members: {task1.team_members}")


def clean_up():
    print("[clean_up] UNIMPLEMENTED")


if __name__ == "__main__":
    atexit.register(clean_up)
    asyncio.run(main())
