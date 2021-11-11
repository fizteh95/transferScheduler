import peewee
import peewee_async

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

