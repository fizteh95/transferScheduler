"""Peewee migrations -- 001_migration_name.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import datetime as dt
import peewee as pw
from decimal import ROUND_HALF_EVEN

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class User(pw.Model):
        id = pw.AutoField()
        vk_login = pw.CharField(max_length=255)
        password = pw.CharField(max_length=255)
        tg_id = pw.IntegerField()

        class Meta:
            table_name = "user"

    @migrator.create_model
    class Bot(pw.Model):
        id = pw.AutoField()
        token = pw.CharField(max_length=255)
        user = pw.ForeignKeyField(backref='bots', column_name='user_id', field='id', model=migrator.orm['user'], null=True)

        class Meta:
            table_name = "bot"

    @migrator.create_model
    class Vk(pw.Model):
        id = pw.AutoField()
        link = pw.CharField(max_length=255)
        last_seen = pw.DateTimeField()

        class Meta:
            table_name = "vk"

    @migrator.create_model
    class Post(pw.Model):
        id = pw.AutoField()
        vk_group = pw.ForeignKeyField(backref='vk', column_name='vk_group_id', field='id', model=migrator.orm['vk'])
        post_id = pw.IntegerField()
        raw_post = pw_pext.JSONField(constraints=[SQL("DEFAULT '{}'")], default={})
        post_time = pw.DateTimeField()

        class Meta:
            table_name = "post"

    @migrator.create_model
    class Tg(pw.Model):
        id = pw.AutoField()
        channel = pw.CharField(max_length=255)
        last_sending = pw.DateTimeField()

        class Meta:
            table_name = "tg"



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('tg')

    migrator.remove_model('post')

    migrator.remove_model('vk')

    migrator.remove_model('bot')

    migrator.remove_model('user')
