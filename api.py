'''
agents: dictionary = {}

Endpoints:
   async add_agent(github_repo_url: string) -> Port Number
       asyncio.create_task(create_new_container(port))
       return "{ port: port }"

   get_all_agengts() -> [agent names]
      return JSON.stringify(agents)
'''
import asyncio
from fastapi import FastAPI
import JSON
# from typing import Union
from docker_controller import DockerController

app = FastAPI()
dc = DockerController()

port = 5000

agents = {}


@app.get("/add_agent")
def add_agent(github_repo_url: str) -> str:
    task = asyncio.create_task(dc.create_new_container())

    # agent_name = await get_agent_name()
    # agents[agent_name] = this_port
    await task

    return JSON.stringify({"port": task.result().port})


@app.get("/get_all_agents")
def get_all_agengts() -> str:
    return JSON.stringify(agents)
