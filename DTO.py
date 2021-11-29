from pydantic import BaseModel, Json
from datetime import datetime
from typing import Optional, List


class User(BaseModel):
    vk_login: str
    password: str
    tg_user_id: int
    bots: Optional[List]


class Bot(BaseModel):
    token: str
    user: Optional[User]
    assocs: Optional[List]


class Vk(BaseModel):
    link: str
    last_seen: datetime
    posts: Optional[List]
    assocs: Optional[List]


class Tg(BaseModel):
    channel: str
    last_sending: Optional[datetime]
    assocs: Optional[List]


class Association(BaseModel):
    bot: Bot
    vk: Vk
    tg: Tg
    last_post_time: datetime


class Post(BaseModel):
    post_id: int
    raw_post: dict
    post_time: datetime
    vk_group: Optional[Vk]
