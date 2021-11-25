from pydantic import BaseModel, Json
from datetime import datetime
from typing import Optional, List


class User(BaseModel):
    vk_login: str
    password: str
    tg_id: int
    bots: Optional[List]


class Vk(BaseModel):
    link: str
    last_seen: Optional[datetime]
    posts: Optional[List]


class Bot(BaseModel):
    token: str
    user: Optional[User]
    vk: Optional[List[Vk]]
    tg_channels: Optional[List]


class Tg(BaseModel):
    channel: str
    last_sending: Optional[datetime]
    bot: Optional[List[Bot]]


class Post(BaseModel):
    post_id: int
    raw_post: Json
    post_time: datetime
    vk_group: Optional[List[Vk]]
