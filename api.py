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
import json
# from typing import Union
from docker_controller import DockerController
from pydantic import BaseModel

app = FastAPI()
dc = DockerController()


class AddAgentReq(BaseModel):
    gh_url: str


@app.post("/add_agent")
async def add_agent(req: AddAgentReq) -> str:
    task = asyncio.create_task(dc.create_new_container(req.gh_url))

    await task

    return json.dumps({"port": task.result().port})


@app.post("/get_all_agents")
def get_all_agents() -> str:
    return json.dumps({"unimplemented": "unimplemented"})


@app.post("/kill_agent")
def kill_agent() -> str:
    dc.kill_conatiner("")
    return json.dumps({"unimplemented": "unimplemented"})


@app.post("/restart_agent")
def restart_agent() -> str:
    dc.restart_conatiner("")
    return json.dumps({"unimplemented": "unimplemented"})
