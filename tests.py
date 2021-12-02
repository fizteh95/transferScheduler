import datetime
from time import sleep

import pytest

import DAO
import DTO
from DAO import objects
from src.models import Association
from src.models import Bot
from src.models import Post
from src.models import Tg
from src.models import User
from src.models import Vk


@pytest.mark.asyncio
@pytest.fixture(autouse=False)
async def db():
    # Setup DB here

    # Yield some data, database connection or nothing at all
    yield None

    # Delete DB here when the test ends
    await objects.execute(Association.delete())

    await objects.execute(Post.delete())
    await objects.execute(Bot.delete().where(Bot.token == 'test2'))
    await objects.execute(Bot.delete().where(Bot.token == 'test1'))
    await objects.execute(Vk.delete().where(Vk.link == 'vk.com/test2'))
    await objects.execute(Vk.delete().where(Vk.link == 'vk.com/test1'))
    await objects.execute(Tg.delete().where(Tg.channel == '@test3'))
    await objects.execute(Tg.delete().where(Tg.channel == '@test2'))
    await objects.execute(Tg.delete().where(Tg.channel == '@test1'))

    await objects.execute(Tg.delete().where(Tg.channel == '@test'))
    await objects.execute(Vk.delete().where(Vk.link == 'vk.com/test'))
    await objects.execute(Bot.delete().where(Bot.token == '5555'))
    await objects.execute(User.delete().where(User.vk_login == '1234'))


@pytest.mark.asyncio
async def test_creating_user():
    user = DTO.User(vk_login='1234', password='1234', tg_user_id=1234)
    created_user = await DAO.create_user(user)
    assert user == created_user
    user_from_db = await DAO.get_user('1234')
    assert user == user_from_db


@pytest.mark.asyncio
async def test_creating_bot():
    user = await DAO.get_user('1234')
    bot = DTO.Bot(token='5555')
    new_bot = await DAO.create_bot_by_user(bot, user)
    assert new_bot.user == user
    assert bot.token == new_bot.token
    bots_from_db = await DAO.get_user_bots(user)
    assert len(bots_from_db) == 1
    assert bots_from_db[0] == new_bot


@pytest.mark.asyncio
async def test_creating_vk():
    vk = DTO.Vk(link='vk.com/test', last_seen=datetime.datetime.now())
    created_vk = await DAO.create_vk(vk)
    assert vk.link == created_vk.link
    vk_from_db = await DAO.get_vk('vk.com/test')
    assert created_vk == vk_from_db


@pytest.mark.asyncio
async def test_creating_tg():
    tg = DTO.Tg(channel='@test', last_sending=datetime.datetime.now())
    created_tg = await DAO.create_tg(tg)
    assert tg.channel == created_tg.channel
    tg_from_db = await DAO.get_tg('@test')
    assert created_tg == tg_from_db


@pytest.mark.asyncio
async def test_get_vk_by_last_seen():
    vks = await DAO.get_vk_by_last_seen(datetime.datetime.now())
    assert len(vks) == 1
    vk = await DAO.get_vk('vk.com/test')
    assert vks[0] == vk


@pytest.mark.asyncio
async def test_create_association():
    vk1 = DTO.Vk(link='vk.com/test1', last_seen=datetime.datetime.now())
    created_vk1 = await DAO.create_vk(vk1)
    vk2 = DTO.Vk(link='vk.com/test2', last_seen=datetime.datetime.now())
    created_vk2 = await DAO.create_vk(vk2)

    tg1 = DTO.Tg(channel='@test1', last_sending=datetime.datetime.now())
    created_tg1 = await DAO.create_tg(tg1)
    tg2 = DTO.Tg(channel='@test2', last_sending=datetime.datetime.now())
    created_tg2 = await DAO.create_tg(tg2)
    tg3 = DTO.Tg(channel='@test3', last_sending=datetime.datetime.now())
    created_tg3 = await DAO.create_tg(tg3)

    user = await DAO.get_user('1234')
    bot1 = DTO.Bot(token='test1')
    created_bot1 = await DAO.create_bot_by_user(bot1, user)
    bot2 = DTO.Bot(token='test2')
    created_bot2 = await DAO.create_bot_by_user(bot2, user)

    await DAO.create_association(created_bot1, created_vk1, created_tg1)
    await DAO.create_association(created_bot1, created_vk2, created_tg2)
    await DAO.create_association(created_bot2, created_vk1, created_tg3)

    bots_to_test1 = await DAO.get_bots_by_vk(created_vk1)
    assert {created_bot1.token, created_bot2.token} == set([x.token for x in bots_to_test1])
    bots_to_test2 = await DAO.get_bots_by_vk(created_vk2)
    assert {created_bot1.token} == set([x.token for x in bots_to_test2])


@pytest.mark.asyncio
async def test_creating_post():
    vk = await DAO.get_vk('vk.com/test')
    post1 = DTO.Post(post_id=1, raw_post={'a': 'b'}, post_time=datetime.datetime.now())
    created_post1 = await DAO.create_post(post1, vk)
    sleep(0.1)
    post2 = DTO.Post(post_id=2, raw_post={'a': 'b'}, post_time=datetime.datetime.now())
    created_post2 = await DAO.create_post(post2, vk)
    sleep(0.1)
    post3 = DTO.Post(post_id=3, raw_post={'a': 'b'}, post_time=datetime.datetime.now())
    created_post3 = await DAO.create_post(post3, vk)
    assert created_post1.post_id == post1.post_id
    assert created_post3.post_id == post3.post_id
    posts_from_db = await DAO.get_vk_posts(vk)
    assert len(posts_from_db) == 3
    assert posts_from_db[0] in [created_post1, created_post2, created_post3]
    assert posts_from_db[1] in [created_post1, created_post2, created_post3]
    assert posts_from_db[2] in [created_post1, created_post2, created_post3]


@pytest.mark.asyncio
async def test_getting_posts():
    vk1 = await DAO.get_vk('vk.com/test1')
    post1 = DTO.Post(post_id=4, raw_post={'a': 'b'}, post_time=datetime.datetime(2010, 1, 1))
    created_post1 = await DAO.create_post(post1, vk1)
    post2 = DTO.Post(post_id=5, raw_post={'a': 'b'}, post_time=datetime.datetime(2012, 1, 1))
    created_post2 = await DAO.create_post(post2, vk1)
    post3 = DTO.Post(post_id=6, raw_post={'a': 'b'}, post_time=datetime.datetime(2013, 1, 1))
    created_post3 = await DAO.create_post(post3, vk1)

    vk2 = await DAO.get_vk('vk.com/test2')
    post1 = DTO.Post(post_id=7, raw_post={'a': 'b'}, post_time=datetime.datetime.now())
    created_post4 = await DAO.create_post(post1, vk2)
    sleep(0.1)
    post2 = DTO.Post(post_id=8, raw_post={'a': 'b'}, post_time=datetime.datetime.now())
    created_post5 = await DAO.create_post(post2, vk2)

    tg1 = DTO.Tg(channel='@test1')
    posts_for_tg1 = await DAO.get_new_posts_for_tg(tg1)
    assert len(posts_for_tg1) == 3
    assert posts_for_tg1[0] in [created_post1, created_post2, created_post3]
    assert posts_for_tg1[1] in [created_post1, created_post2, created_post3]
    assert posts_for_tg1[2] in [created_post1, created_post2, created_post3]

    tg2 = DTO.Tg(channel='@test2')
    posts_for_tg2 = await DAO.get_new_posts_for_tg(tg2)
    assert len(posts_for_tg2) == 2
    assert posts_for_tg2[0] in [created_post4, created_post5]
    assert posts_for_tg2[1] in [created_post4, created_post5]


@pytest.mark.asyncio
async def test_getting_posts_check_timing():
    db_bot = DTO.Bot(token='test1')
    db_tg1 = DTO.Tg(channel='@test1')
    db_vk = await DAO.get_vk(vk_link='vk.com/test1')
    await DAO.change_last_post_time_in_assoc(db_bot, db_vk, db_tg1, datetime.datetime(2011, 1, 1))

    posts_for_tg1 = await DAO.get_new_posts_for_tg(db_tg1)
    assert len(posts_for_tg1) == 2
    assert posts_for_tg1[0].post_id in [5, 6]
    assert posts_for_tg1[1].post_id in [5, 6]

    db_tg2 = DTO.Tg(channel='@test3')
    posts_for_tg2 = await DAO.get_new_posts_for_tg(db_tg2)
    assert len(posts_for_tg2) == 3
    assert posts_for_tg2[0].post_id in [4, 5, 6]
    assert posts_for_tg2[1].post_id in [4, 5, 6]
    assert posts_for_tg2[2].post_id in [4, 5, 6]


@pytest.mark.asyncio
async def test_cleanup(db):
    pass
