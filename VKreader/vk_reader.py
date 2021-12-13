# import asyncio
# import datetime
# import json
# import uuid
from functools import partial

import aio_pika
from fastapi import FastAPI  # BackgroundTasks

import settings
# from aio_pika import Message
# import DAO


app = FastAPI()


class Scheduler:
    def __init__(self):
        # self.stopped = False
        pass

    async def rabbit_connect(self):
        self.connection = await aio_pika.connect_robust(  # noQA
            settings.RABBIT_ADDRESS,  # , loop=loop
        )
        self.channel = await self.connection.channel()  # noQA
        self.queue = await self.channel.declare_queue(settings.RABBIT_READING_QUEUE)  # noQA

    async def message_waiting(self):
        await self.queue.consume(
            partial(
                self.message_handle, self.channel.default_exchange,
            ),
        )

    async def message_handle(self, _, message):
        with message.process():
            print(message.body)


runner = Scheduler()


@app.on_event('startup')
async def app_startup():
    await runner.rabbit_connect()
    await runner.message_waiting()


# @app.on_event('shutdown')
# async def app_shutdown():
#     runner.stopped = True


# @app.get("/")
# async def read_items():
#     return {'hi': 'its ok!', 'value': runner.value}
#
#
# @app.get("/set_value")
# def set_value(x: int):
#     runner.value = x
#     return f"set runner.value to {x}"
