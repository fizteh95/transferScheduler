import typing as tp
from datetime import datetime

import peewee_async
from playhouse.shortcuts import model_to_dict

import DTO
from src.models import Association
from src.models import Bot
from src.models import database
from src.models import Post
from src.models import Tg
from src.models import User
from src.models import Vk


objects = peewee_async.Manager(database)


async def create_user(user: DTO.User) -> DTO.User:
    created_user = await objects.create(User, **user.dict())
    return DTO.User.parse_obj(model_to_dict(created_user))


async def get_user(username: str) -> DTO.User:
    user = await objects.get(User, vk_login=username)
    return DTO.User.parse_obj(model_to_dict(user))


async def create_vk(vk_group: DTO.Vk) -> DTO.Vk:
    if not vk_group.last_seen:
        vk_group.last_seen = datetime(2000, 1, 1)
    created_vk = await objects.create(Vk, **vk_group.dict())
    return DTO.Vk.parse_obj(model_to_dict(created_vk))


async def get_vk(vk_link: str) -> DTO.Vk:
    vk_group = await objects.get(Vk, link=vk_link)
    return DTO.Vk.parse_obj(model_to_dict(vk_group))


async def create_tg(tg_channel: DTO.Tg) -> DTO.Tg:
    if not tg_channel.last_sending:
        tg_channel.last_sending = datetime(2000, 1, 1)
    created_tg = await objects.create(Tg, **tg_channel.dict())
    return DTO.Tg.parse_obj(model_to_dict(created_tg))


async def get_tg(channel: str) -> DTO.Tg:
    tg_channel = await objects.get(Tg, channel=channel)
    return DTO.Tg.parse_obj(model_to_dict(tg_channel))


async def get_vk_by_last_seen(less_time: datetime) -> tp.List[DTO.Vk]:
    vk_groups = await objects.execute(Vk.select().where(Vk.last_seen < less_time))
    return [DTO.Vk.parse_obj(model_to_dict(vk)) for vk in vk_groups]


async def create_bot_by_user(bot: DTO.Bot, user: DTO.User) -> DTO.Bot:
    user_from_db = await objects.get(User, vk_login=user.vk_login)
    bot.user = user_from_db
    created_bot = await objects.create(Bot, **bot.dict())
    return DTO.Bot.parse_obj(model_to_dict(created_bot))


async def get_user_bots(user: DTO.User) -> tp.List[DTO.Bot]:
    user = await objects.get(User, vk_login=user.vk_login)
    bots = user.bots
    return [DTO.Bot.parse_obj(model_to_dict(bot)) for bot in bots]


async def create_association(bot: DTO.Bot, vk: DTO.Vk, tg: DTO.Tg) -> DTO.Association:
    db_bot = await objects.get(Bot, token=bot.token)
    db_vk = await objects.get(Vk, link=vk.link)
    db_tg = await objects.get(Tg, channel=tg.channel)
    association = await objects.create(Association, bot=db_bot, vk=db_vk, tg=db_tg, last_post_time=datetime(2000, 1, 1))
    return DTO.Association.parse_obj(model_to_dict(association))


async def get_bots_by_vk(vk: DTO.Vk) -> tp.List[DTO.Bot]:
    db_vk = await objects.get(Vk, link=vk.link)
    bots = {}
    associations = db_vk.assoc
    for ass in associations:
        bots[ass.bot.token] = ass.bot
    return [DTO.Bot.parse_obj(model_to_dict(x)) for x in bots.values()]


async def get_tgs_by_bot(bot: DTO.Bot) -> tp.List[DTO.Tg]:
    db_bot = await objects.get(Bot, token=bot.token)
    tgs = {}
    associations = db_bot.assoc
    for ass in associations:
        tgs[ass.tg.channel] = ass.tg
    return [DTO.Tg.parse_obj(model_to_dict(x)) for x in tgs.values()]


async def create_post(post: DTO.Post, vk: DTO.Vk) -> DTO.Post:
    db_vk = await objects.get(Vk, link=vk.link)
    vk_dict = post.dict()
    del vk_dict['vk_group']
    created_post = await objects.create(Post, **vk_dict, vk_group=db_vk)
    return DTO.Post.parse_obj(model_to_dict(created_post))


async def get_vk_posts(vk: DTO.Vk) -> tp.List[DTO.Post]:
    vk = await objects.get(Vk, link=vk.link)
    posts = vk.posts
    return [DTO.Post.parse_obj(model_to_dict(post)) for post in posts]


async def get_new_posts_for_tg(tg: DTO.Tg) -> tp.List[DTO.Post]:
    db_tg = await objects.get(Tg, channel=tg.channel)
    times = {}
    res = []
    associations = db_tg.assoc
    for ass in associations:
        times[ass.vk.id] = ass.last_post_time
    for j, link in zip(times.values(), times.keys()):
        res += list(await objects.execute(Post.select().where(Post.vk_group == link, Post.post_time > j)))
    return [DTO.Post.parse_obj(model_to_dict(post)) for post in res]


async def change_last_post_time_in_assoc(bot: DTO.Bot, vk: DTO.Vk, tg: DTO.Tg, last_post_time: datetime) -> None:
    db_bot = await objects.get(Bot, token=bot.token)
    db_vk = await objects.get(Vk, link=vk.link)
    db_tg = await objects.get(Tg, channel=tg.channel)
    db_assoc = await objects.get(Association, bot=db_bot, vk=db_vk, tg=db_tg)
    db_assoc.last_post_time = last_post_time
    await objects.update(db_assoc)
