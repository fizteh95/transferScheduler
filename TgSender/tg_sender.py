import asyncio
import json
from functools import partial

import aio_pika
from aiogram import Bot
from aiogram.types import InputMediaPhoto
from aiogram.types import MediaGroup
from fastapi import FastAPI

import DAO
import DTO
import settings


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
        self.queue = await self.channel.declare_queue(settings.RABBIT_SENDING_QUEUE)  # noQA

    async def message_waiting(self):
        await self.queue.consume(
            partial(
                self.message_handle, self.channel.default_exchange,
            ),
        )

    async def message_handle(self, _, message):
        async with message.process():
            # print(message.body)
            posts_for_channels = json.loads(message.body.decode())
            print(f'Number of messages: {len(posts_for_channels)}')
            # logger.info(f'Number of messages: {len(posts_for_channels)}')
            for ch, posts in posts_for_channels.items():
                if not posts:
                    continue
                dto_tg = DTO.Tg(channel=ch)
                dto_bot = await DAO.get_bot_by_tg(dto_tg)
                bot_token = dto_bot.token
                sorted_posts = sorted(posts, key=lambda x: x['post_time'])
                try:
                    bot = Bot(token=bot_token)
                    for post in sorted_posts:

                        # dto_vk = DTO.Vk(link=post['vk_group']['link'])
                        # dto_post = DTO.Post.parse_obj(post)
                        # is_posted = await DAO.is_posted_in_asssoc(dto_post, dto_vk, dto_tg, dto_bot)
                        # if is_posted:
                        #     continue

                        counter = 0
                        success = False
                        while not success and (counter < 10):
                            try:
                                p = DTO.RawPost(**post['raw_post'])
                                if not (p.audios or p.photos):
                                    await bot.send_message(chat_id=dto_tg.channel, parse_mode='html', text=p.text)
                                # elif p.audios and p.photos:
                                #     await bot.send_media_group(chat_id='@novostibyte', parse_mode='html', media=[])
                                elif len(p.photos) == 1:
                                    await bot.send_photo(
                                        chat_id=dto_tg.channel,
                                        photo=p.photos[0].url,
                                        caption=p.text,
                                        parse_mode='html',
                                    )
                                elif len(p.photos) > 1:
                                    media_group = []
                                    for i, ph in enumerate(p.photos):
                                        imp = InputMediaPhoto(media=ph.url, parse_mode='html')
                                        media_group.append(imp)
                                        if i == 0:
                                            media_group[0].caption = p.text
                                    media_group = MediaGroup(media_group)
                                    await bot.send_media_group(chat_id=dto_tg.channel, media=media_group)
                                # await DAO.posted_in_assoc(dto_post, dto_vk, dto_tg, dto_bot)
                                # await DAO.change_last_post_time_in_assoc(dto_bot, dto_vk, dto_tg, post['post_time'])
                                await asyncio.sleep(15)
                                print('send message')
                                success = True
                            except Exception as e:
                                counter += 1
                                await asyncio.sleep(15)
                                print(f'error: {e}, counter={counter}')

                except Exception as e:
                    print(e)
                finally:
                    await bot.close()


runner = Scheduler()


@app.on_event('startup')
async def app_startup():
    await runner.rabbit_connect()
    await runner.message_waiting()
