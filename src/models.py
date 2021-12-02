import peewee
import peewee_async
from playhouse.postgres_ext import JSONField

# Nothing special, just define model and database:

database = peewee_async.PostgresqlDatabase(
    'postgres',
    user='postgres',
    password='postgres',
    host='localhost',
    port='5432',
)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class User(BaseModel):
    vk_login = peewee.CharField(unique=True)
    password = peewee.CharField()
    tg_user_id = peewee.IntegerField(unique=True)


class Bot(BaseModel):
    token = peewee.CharField(unique=True)
    user = peewee.ForeignKeyField(User, backref='bots', null=True)


class Vk(BaseModel):
    link = peewee.CharField(unique=True)
    last_seen = peewee.DateTimeField()


class Tg(BaseModel):
    channel = peewee.CharField(unique=True)
    last_sending = peewee.DateTimeField()


class Association(BaseModel):
    bot = peewee.ForeignKeyField(Bot, backref='assoc')
    vk = peewee.ForeignKeyField(Vk, backref='assoc')
    tg = peewee.ForeignKeyField(Tg, backref='assoc')
    last_post_time = peewee.DateTimeField()


class Post(BaseModel):
    post_id = peewee.IntegerField(unique=True)
    raw_post = JSONField(default={})
    post_time = peewee.DateTimeField()
    vk_group = peewee.ForeignKeyField(Vk, backref='posts')
