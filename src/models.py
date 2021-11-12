import peewee
import peewee_async
from playhouse.postgres_ext import JSONField

# Nothing special, just define model and database:

database = peewee_async.PostgresqlDatabase('postgres',
                                           user='postgres',
                                           password='postgres',
                                           host='localhost',
                                           port='5432')


class BaseModel(peewee.Model):
    class Meta:
        database = database


class TestModel(BaseModel):
    text = peewee.CharField(max_length=400, default='')
    data = peewee.IntegerField(default=20000)


class User(BaseModel):
    vk_login = peewee.CharField()
    password = peewee.CharField()
    tg_id = peewee.IntegerField()


class Bot(BaseModel):
    token = peewee.CharField()


class Vk(BaseModel):
    link = peewee.CharField()
    last_seen = peewee.DateTimeField()


class Tg(BaseModel):
    channel = peewee.CharField()
    last_sending = peewee.DateTimeField()


class Post(BaseModel):
    vk_group = peewee.ForeignKeyField(Vk, backref='vk')
    post_id = peewee.IntegerField()
    raw_post = JSONField(default={})
    post_time = peewee.DateTimeField()


class UserBot(BaseModel):
    user = ForeignKeyField(User, backref='user')
    bot = ForeignKeyField(Bot, backref='favorites')

