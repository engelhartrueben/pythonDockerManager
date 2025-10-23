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
from docker_controller import DockerController, DC_SC
from pydantic import BaseModel
import docker

app = FastAPI()
dc = DockerController()


class AddAgentReq(BaseModel):
    gh_url: str


class KillAgentReq(BaseModel):
    container_id: str


@app.post("/add_agent")
async def add_agent(req: AddAgentReq) -> str:
    task = asyncio.create_task(dc.create_new_container(req.gh_url))

    await task

    if task.result().status != DC_SC.OK:
        return json.dumps({"status": "bad"})

    print(task.result())
    return json.dumps({
        "port": task.result().port,
        "status": "ok",
        "container_id": task.result().container_id
    })


@app.post("/get_all_agents")
def get_all_agents() -> str:
    return json.dumps({"unimplemented": "unimplemented"})


@app.post("/get_all_containers")
def get_all_containers() -> str:
    """Returns all known containers"""
    res = {}
    print(dc.client.containers.list(all=True))
    for container in dc.active_containers.values():
        res[container.port_number] = container.container.id
    return json.dumps(res)


@app.delete("/kill_all_agents")
def kill_all_agents():
    for container in dc.client.containers.list(all=True):
        try:
            container.remove()
        except docker.errors.APIError as e:
            print(f"failed to remove a conatiner: {e}")
    return json.dumps({"ok": "ok"})


@app.post("/kill_agent")
async def kill_agent(req: KillAgentReq) -> str:
    res = await dc.kill_conatiner(req.container_id)

    match res:
        case DC_SC.FAILED_TO_KILL_DOCKER_C:
            return json.dumps(
                {"message": f"Failed to kill {req.container_id}"})
        case DC_SC.OK:
            return json.dumps({"message": "sucess"})
        case _:
            return json.dumps({"message": "unhandled. dummy"})


@app.post("/restart_agent")
def restart_agent() -> str:
    dc.restart_conatiner("")
    return json.dumps({"unimplemented": "unimplemented"})
