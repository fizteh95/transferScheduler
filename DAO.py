from src.models import database, User, Vk, Tg, Bot, Post
import DTO
import peewee_async
from playhouse.shortcuts import model_to_dict
import typing as tp


objects = peewee_async.Manager(database)


async def create_user(user: DTO.User) -> DTO.User:
    created_user = await objects.create(User, **user.dict())
    return DTO.User.parse_obj(model_to_dict(created_user))


async def get_user(username: str) -> DTO.User:
    user = await objects.get(User, vk_login=username)
    return DTO.User.parse_obj(model_to_dict(user))


async def create_vk(vk_group: DTO.Vk) -> DTO.Vk:
    created_vk = await objects.create(Vk, **vk_group.dict())
    return DTO.Vk.parse_obj(model_to_dict(created_vk))


async def get_vk(vk_link: str) -> DTO.Vk:
    vk_group = await objects.get(Vk, link=vk_link)
    return DTO.Vk.parse_obj(model_to_dict(vk_group))


async def get_vk_by_last_seen(vk_link: str) -> DTO.Vk:
    raise NotImplementedError


async def create_bot_by_user(bot: DTO.Bot, user: DTO.User) -> DTO.Bot:
    user = await objects.get(User, vk_login=user.vk_login)
    created_bot = await objects.create(Bot, **bot.dict(), user=user)
    return DTO.Bot.parse_obj(model_to_dict(created_bot))


async def get_user_bots(username: str) -> tp.List[DTO.Bot]:
    user = await objects.get(User, vk_login=username)
    bots = user.bots
    return [DTO.Bot.parse_obj(model_to_dict(bot)) for bot in bots]


async def get_vk_bots(vk: DTO.Vk) -> tp.List[DTO.Bot]:
    vk = await objects.get(Vk, link=vk.link)
    bots = vk.bots
    return [DTO.Bot.parse_obj(model_to_dict(bot)) for bot in bots]


async def create_tgs_by_bot(tg: DTO.Tg, bot: DTO.Bot) -> DTO.Tg:
    bot = await objects.get(Bot, token=bot.token)
    created_tg = await objects.create(Tg, **tg.dict(), bot=bot)
    return DTO.Tg.parse_obj(model_to_dict(created_tg))


async def get_tg_channels_by_bot(bot: DTO.Bot) -> tp.List[DTO.Tg]:
    bot = await objects.get(Bot, token=bot.token)
    tg_channels = bot.tg_channels
    return [DTO.Tg.parse_obj(model_to_dict(tg)) for tg in tg_channels]


async def create_post(post: DTO.Post, vk: DTO.Vk) -> DTO.Post:
    created_post = await objects.create(Post, **post.dict(), vk_group=vk)
    return DTO.Post.parse_obj(model_to_dict(created_post))


async def get_vk_posts(vk: DTO.Vk) -> tp.List[DTO.Post]:
    vk = await objects.get(Vk, link=vk.link)
    posts = vk.posts
    return [DTO.Post.parse_obj(model_to_dict(post)) for post in posts]
