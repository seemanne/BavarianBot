import asyncio
import logging

from fastapi import FastAPI
import discord
import src.client
import src.orm
import src.crud
from src.models import Status

LOG = logging.getLogger("uvicorn")
client = src.client.Maggus(intents=discord.Intents.all(), log=LOG)
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/service/status")
async def status():
    return Status(
        is_closed=client.is_closed(),
        is_ready=client.is_ready(),
    )


@app.get("/service/init_db")
async def init_db():
    src.orm.init_db(client.sql_engine)
    return {"message": "Initialized db"}


@app.put("/service/start")
async def start_client():
    loop = asyncio.get_event_loop()
    task = loop.create_task(client.start(src.auth.AUTH))
    task.add_done_callback(
        lambda x: log_callback(
            x, "discord_client_callback", "Discord client terminated"
        )
    )

    timeout = 0
    while not client.is_ready():
        await asyncio.sleep(0.5)
        timeout += 1
        if timeout >= 10:
            return {"message": "Client startup failed to connect"}

    return {"message": "Client started"}


@app.put("/service/stop")
async def stop_client():
    await client.close()

    while client.is_ready():
        await asyncio.sleep(0.5)
    client.__init__(intents=discord.Intents.all(), log=LOG)
    return {"message": "Client stopped and reset sucessfully"}


@app.put("/client/deactivate")
async def deactivate_client():
    await client.deactivate()
    return {"message": "Client deactivated, no longer receiving messages"}


@app.put("/client/activate")
async def activate_client():
    await client.activate()
    return {"message": "CLient activated, receiving messages"}


@app.get("/poast")
async def send_clown(channel: int, message: str):
    chan = client.get_channel(channel)
    await chan.send(message)
    return {"message": "Poasted successfully"}


@app.get("/data")
async def get_data(channel: int, n: int):
    data = await client.get_history(channel, n)
    return {"data": data}


@app.get("/pond/fishers")
async def get_pond_info():
    data = client.pond.fishers
    return {"fishers": data}


@app.get("/pond/catches/{user_name}")
async def get_catches(user_name):
    return {
        "fishes": src.crud.get_all_catches_by_username(
            user_name=user_name, engine=client.sql_engine
        )
    }


def log_callback(fut, coroutine_name, additional_message=""):
    try:
        result = fut.result()
        LOG.info(f"{coroutine_name} {additional_message} Coroutine result: {result}")
    except Exception as e:
        LOG.info(f"{coroutine_name} Coroutine raised an exception: {str(e)}")
