import peewee
import peewee_async
from playhouse.postgres_ext import JSONField

# Nothing special, just define model and database:

database = peewee_async.PostgresqlDatabase('test',
                                           user='postgres',
                                           password='postgres',
                                           host='localhost',
                                           port='5432')


class BaseModel(peewee.Model):
    class Meta:
        database = database


class User(BaseModel):
    vk_login = peewee.CharField()
    password = peewee.CharField()
    tg_id = peewee.IntegerField()


class Vk(BaseModel):
    link = peewee.CharField()
    last_seen = peewee.DateTimeField()


class Bot(BaseModel):
    token = peewee.CharField()
    user = peewee.ForeignKeyField(User, backref='bots', null=True)
    vk = peewee.ForeignKeyField(Vk, backref='bots', null=True)


class Tg(BaseModel):
    channel = peewee.CharField()
    last_sending = peewee.DateTimeField()
    bot = peewee.ForeignKeyField(Bot, backref='tg_channels', null=True)


class Post(BaseModel):
    post_id = peewee.IntegerField()
    raw_post = JSONField(default={})
    post_time = peewee.DateTimeField()
    vk_group = peewee.ForeignKeyField(Vk, backref='posts')
