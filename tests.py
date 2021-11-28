import pytest
import DAO
import DTO
import datetime
from DAO import objects
from src.models import User, Bot, Vk, Tg, Association


@pytest.mark.asyncio
@pytest.fixture(autouse=False)
async def db():
    # Setup DB here

    # Yield some data, database connection or nothing at all
    yield None

    # Delete DB here when the test ends
    await objects.execute(Association.delete())

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
    # vk3 = DTO.Vk(link='vk.com/test3', last_seen=datetime.datetime.now())
    # created_vk3 = await DAO.create_vk(vk3)
    # vk4 = DTO.Vk(link='vk.com/test4', last_seen=datetime.datetime.now())
    # created_vk4 = await DAO.create_vk(vk4)

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


# @pytest.mark.asyncio
# async def test_creating_post():
#     vk = await DAO.get_vk('vk.com/test')
#     post = DTO.Post(post_id=1, raw_post={'a': 'b'}, post_time=datetime.datetime.now())
#     created_post = await DAO.create_post(post, vk)
#     assert created_post.post_id == post.post_id
#     posts_from_db = await DAO.get_vk_posts(vk)
#     assert len(posts_from_db) == 1
#     assert posts_from_db[0] == created_post
#     # await objects.execute(Post.delete().where(Post.post_id == 1))


@pytest.mark.asyncio
async def test_cleanup(db):
    pass
