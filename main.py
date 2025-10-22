import atexit
import asyncio
from docker_controller import DockerController

dc = DockerController()


async def main():
    task1 = await dc.create_new_container("")
    print(f"Assigned port: {task1.port}")


def clean_up():
    print("[clean_up] UNIMPLEMENTED")


if __name__ == "__main__":
    atexit.register(clean_up)
    asyncio.run(main())
