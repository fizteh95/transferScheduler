from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    vk_login: str
    password: str
    token: str
    tg_user_id: int
    bots: Optional[List]


class Bot(BaseModel):
    token: str
    user: Optional[User]
    assocs: Optional[List]


class UserBot(BaseModel):
    user: User
    bot: Bot


class Vk(BaseModel):
    link: str
    last_seen: Optional[datetime]
    posts: Optional[List]
    assocs: Optional[List]

    class Config:
        json_encoders = {
            datetime: lambda v: v.timestamp(),
        }


class Tg(BaseModel):
    channel: str
    last_sending: Optional[datetime]
    assocs: Optional[List]


class Association(BaseModel):
    bot: Bot
    vk: Vk
    tg: Tg
    last_post_time: Optional[int]


class Post(BaseModel):
    post_id: int
    raw_post: dict
    post_time: int
    vk_group: Optional[Vk]


class VkAudio(BaseModel):
    id: int
    url: str
    artist: str
    title: str


class VkPhoto(BaseModel):
    id: int
    url: str
    text: str


class RawPost(BaseModel):
    text: str
    timestamp: int
    marked_as_ads: int
    audios: Optional[List[VkAudio]] = []
    photos: Optional[List[VkPhoto]] = []
