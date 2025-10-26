import asyncio
import json
import docker
from fastapi import FastAPI
from pydantic import BaseModel

from docker_controller import DockerController, DC_SC

app = FastAPI()
dc = DockerController()


class AddAgentReq(BaseModel):
    gh_url: str


class GetLogsReq(BaseModel):
    container_id: str


class KillAgentReq(BaseModel):
    container_id: str


class CommandReq(BaseModel):
    container_id: str


@app.post("/add_agent")
async def add_agent(req: AddAgentReq) -> str:
    """
    Add an agent to the pool of existing agents.
    Takes in a gh_url to be pulled down, compiled, and
    eventually exectuted.
    """
    task = await asyncio.create_task(dc.create_new_container(req.gh_url))

    if task.status != DC_SC.OK:
        return json.dumps({"status": "bad"})

    print(task)
    return json.dumps({
        "port": task.port,
        "status": "ok",
        "container_id": task.container_id
    })


@app.post("/get_all_agents")
def get_all_agents() -> str:
    """
    [unimplemented]

    Will eventually return every agent, their name, and
    container id.
    """
    return json.dumps({"unimplemented": "unimplemented"})


@app.post("/get_all_containers")
def get_all_containers() -> str:
    """
    Returns all known containers.
    Not entirely useful at the moment.
    """
    res = {}
    print(dc.client.containers.list(all=True))
    for container in dc.active_containers.values():
        res[container.port_number] = container.container.id
    return json.dumps(res)


# TODO: Need to work on all returns!
# Should return that it failed to kill agents
@app.delete("/kill_all_agents")
def kill_all_agents():
    """
    Kills all docker containers on the machine.
    DANGEROUS AF
    """
    for container in dc.client.containers.list(all=True):
        try:
            container.remove()
        except docker.errors.APIError as e:
            print(f"failed to remove a conatiner: {e}")
    return json.dumps({"ok": "ok"})


@app.post("/kill_agent")
async def kill_agent(req: KillAgentReq) -> str:
    """
    Kills a specific docker container given a container id
    """
    res = await dc.kill_conatiner(req.container_id)

    match res:
        case DC_SC.FAILED_TO_KILL_DOCKER_C:
            return json.dumps(
                {"message": f"Failed to kill {req.container_id}"})
        case DC_SC.OK:
            return json.dumps({"message": "sucess"})
        case _:
            return json.dumps({"message": "unhandled. dummy"})


@app.post('/test/print_conatiner_logs')
def get_conatiner_logs(req: GetLogsReq) -> str:
    try:
        print(dc.client.containers.get(req.container_id).logs().decode('utf-8'))
    except docker.errors.APIError as e:
        print(f"[/test/print_conatiner_logs] ERROR: {e}")
        return json.dumps({"bad": "bad"})

    return json.dumps({"ok": "ok"})


@app.post("/restart_agent")
def restart_agent() -> str:
    """
    Will eventually restart a docker container given a 
    container id.
    """
    dc.restart_conatiner("")
    return json.dumps({"unimplemented": "unimplemented"})


@app.post("/commands")
def command(req: CommandReq) -> str:
    container = dc.client.containers.get(req.container_id)
    print(container.status)
    container.reload()
    print(container.status)
    return json.dumps({"ok": "ok"})
