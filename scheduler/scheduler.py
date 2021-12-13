import asyncio
import datetime
import json
import uuid

import aio_pika
from aio_pika import Message
from fastapi import FastAPI  # BackgroundTasks

import DAO
import settings


app = FastAPI()


class Scheduler:
    def __init__(self):
        self.vk_value = 0
        self.tg_value = 0

    async def rabbit_connect(self):
        self.connection = await aio_pika.connect_robust(  # noQA
            settings.RABBIT_ADDRESS,  # , loop=loop
        )
        self.channel = await self.connection.channel()  # noQA
        self.queue_reading_name = settings.RABBIT_READING_QUEUE  # noQA
        self.queue_sending_name = settings.RABBIT_SENDING_QUEUE  # noQA

    async def bus_send(self, message: dict, queue: str) -> None:
        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(message).encode(),
                content_type='text/plain',
                correlation_id=str(uuid.uuid1()),
            ),
            routing_key=queue,
        )

    async def sending_reading_vk_task(self) -> None:
        updated_time = datetime.datetime.now() - datetime.timedelta(seconds=settings.VK_CHECK_INTERVAL)
        vks = await DAO.get_vk_by_last_seen(updated_time)
        message = {'vks': [vk.link for vk in vks]}
        await self.bus_send(message, self.queue_reading_name)

    async def sending_unprocessed_messages_task(self):
        # TODO: сделать как при заборе из вк, сначала смотрим каналы которые давно не обновлялись
        all_tgs = await DAO.get_all_tg()
        message = {}
        for tg in all_tgs:
            new_messages = DAO.get_new_posts_for_tg(tg)
            message[tg.channel] = new_messages
        await self.bus_send(message, self.queue_sending_name)

    async def run_vk_scheduler(self):
        while True:
            self.vk_value += 1
            await asyncio.sleep(settings.VK_UPDATE_INTERVAL)
            await self.sending_reading_vk_task()
            print(self.vk_value)

    async def run_tg_scheduler(self):
        while True:
            self.tg_value += 1
            await asyncio.sleep(settings.TG_UPDATE_INTERVAL)
            await self.sending_unprocessed_messages_task()
            print(self.tg_value)


runner = Scheduler()


@app.on_event('startup')
async def app_startup():
    await runner.rabbit_connect()
    asyncio.create_task(runner.run_vk_scheduler())
    asyncio.create_task(runner.run_tg_scheduler())


# @app.get("/")
# async def read_items():
#     return {'hi': 'its ok!', 'value': runner.value}
#
#
# @app.get("/set_value")
# def set_value(x: int):
#     runner.value = x
#     return f"set runner.value to {x}"
