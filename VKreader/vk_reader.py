# import asyncio
# import datetime
# import json
# import uuid
import json
import re
from functools import partial
from typing import List

import aio_pika
import httpx
from fastapi import FastAPI  # BackgroundTasks

import DAO
import DTO
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
            port=5673,
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
            vks = json.loads(message.body.decode())['vks']
            print(vks)
            for vk in vks:
                dto_vk = DTO.Vk(link=vk)
                token = await DAO.get_token_for_vk(DTO.Vk(link=vk))
                # raw_posts = []
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                                        'https://api.vk.com/method/wall.get',
                                        params=[
                                            ('access_token', token),
                                            ('domain', vk),
                                            ('offset', '0'),
                                            ('count', '2'),
                                            ('v', '5.95'),
                                        ],
                                        headers={
                                            'User-Agent':
                                            'KateMobileAndroid/56 lite-460 (Android 4.4.2; SDK 19; x86; \
                                            unknown Android SDK built for x86; en)',
                                        },
                    )
                posts = json.loads(response.content.decode())['response']['items']
                for post in posts:
                    r = DTO.RawPost(
                        text=post.get('text'), timestamp=post['date'],
                        marked_as_ads=post.get('marked_as_ads'),
                    )

                    for a in post['attachments']:
                        if a.get('type') == 'photo':
                            p = a['photo']
                            vk_p = DTO.VkPhoto(id=p['id'], text=p['text'], url=self.get_biggest_size(p['sizes']))
                            r.photos.append(vk_p)
                        elif a.get('type') == 'audio':
                            m = a['audio']
                            vk_m = DTO.VkAudio(id=m['id'], url=m['url'], title=m['title'], artist=m['artist'])
                            r.audios.append(vk_m)

                    r.text = self.preprocess_text(r.text)
                    post_id = int(str(post['id']) + str(post['from_id'])[1:])
                    # TODO: добавить проверку наличия данного поста в базе
                    dto_post = DTO.Post(post_id=post_id, raw_post=r.dict(), post_time=post['date'], vk_group=dto_vk)
                    await DAO.create_post(dto_post, dto_vk)
                await DAO.refresh_vk_last_seen(dto_vk)

    def get_biggest_size(self, sizes: List) -> str:  # noQA
        biggest = 0
        url = ''
        for s in sizes:
            if s['height'] > biggest:
                biggest = s['height']
                url = s['url']
        return url

    def preprocess_text(self, text: str) -> str:  # noQA
        inplaces = re.findall(r'\[.*?\]', text)
        for i in inplaces:
            club = i.split('[')[1].split('|')[0]
            name = i.split('|')[1].split(']')[0]
            text = text.replace(i, f'<a href="http://vk.com/{club}">{name}</a>')
        return text


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
