import pytest
import DAO
import DTO


@pytest.mark.asyncio
async def test_creating_user():
    user = DTO.User(vk_login='1234', password='1234', tg_id=1234)
    created_user = await DAO.create_user(user)
    assert user == created_user
    user_from_db = await DAO.get_user('1234')
    assert user == user_from_db


@pytest.mark.asyncio
async def test_creating_bot():
    pass


@pytest.mark.asyncio
async def test_creating_vk():
    pass


@pytest.mark.asyncio
async def test_creating_tg():
    pass


@pytest.mark.asyncio
async def test_creating_post():
    pass


@pytest.mark.asyncio
async def test_get_vk_by_last_seen():
    pass


@pytest.mark.asyncio
async def test_get_vk_bots():
    pass


@pytest.mark.asyncio
async def test_get_tg_channels_by_bot():
    pass
