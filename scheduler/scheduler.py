import asyncio
import datetime
import json
import uuid

import aio_pika
from aio_pika import Message
from fastapi import FastAPI  # BackgroundTasks

import DAO
import DTO
import settings


app = FastAPI()


class Scheduler:
    def __init__(self):
        self.vk_value = 0
        self.tg_value = 0

    async def rabbit_connect(self):
        print(settings.RABBIT_ADDRESS)
        self.connection = await aio_pika.connect_robust(  # noQA
            settings.RABBIT_ADDRESS,
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
            new_messages = await DAO.get_new_posts_for_tg(tg)
            if not new_messages:
                print('no messages')
                continue
            posts = [json.loads(x.json()) for x in new_messages]
            message[tg.channel] = sorted(posts, key=lambda x: x['post_time'])
            # print(message)

            dto_bot = await DAO.get_bot_by_tg(tg)
            dto_vk = DTO.Vk(link=posts[0]['vk_group']['link'])

            print(f'messages number: {len(posts)}')
            await DAO.change_last_post_time_in_assoc(dto_bot, dto_vk, tg, posts[0]['post_time'])
        await self.bus_send(message, self.queue_sending_name)

    async def run_vk_scheduler(self):
        while True:
            self.vk_value += 1
            await asyncio.sleep(settings.VK_UPDATE_INTERVAL)
            await self.sending_reading_vk_task()
            print('vk', self.vk_value)

    async def run_tg_scheduler(self):
        while True:
            self.tg_value += 1
            await asyncio.sleep(settings.TG_UPDATE_INTERVAL)
            await self.sending_unprocessed_messages_task()
            print('tg', self.tg_value)


runner = Scheduler()


@app.on_event('startup')
async def app_startup():
    await runner.rabbit_connect()
    asyncio.create_task(runner.run_vk_scheduler())
    asyncio.create_task(runner.run_tg_scheduler())


@app.post('/add_user')
async def add_user(user: DTO.User):
    r = await DAO.create_user(user)
    return r.dict()


@app.post('/add_vk')
async def add_vk(vk: DTO.Vk):
    r = await DAO.create_vk(vk)
    return r.dict()


@app.get('/all_tg')
async def all_tg():
    r = await DAO.get_all_tg()
    return r


@app.post('/delete_all_vk')
async def delete_all_vk():
    await DAO.delete_all_vk()
    return {'deleted': True}


@app.post('/add_bot')
async def add_bot(user_bot: DTO.UserBot):
    r = await DAO.create_bot_by_user(user_bot.bot, user_bot.user)
    return r.dict()


@app.post('/add_tg')
async def add_tg(tg: DTO.Tg):
    r = await DAO.create_tg(tg)
    return r.dict()


@app.post('/add_association')
async def add_association(ass: DTO.Association):
    r = await DAO.create_association(bot=ass.bot, tg=ass.tg, vk=ass.vk)
    return r.dict()


@app.post('/delete_all_associations')
async def delete_all_association():
    await DAO.delete_all_associations()
    return {'deleted': True}


@app.post('/delete_all_posts')
async def delete_all_posts():
    num = await DAO.delete_all_posts()
    return {'deleted': num}


@app.post('/delete_all_posted')
async def delete_all_posted():
    await DAO.delete_all_posted()
    return {'deleted': True}
