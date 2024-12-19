from bot.utils.user_utils import database


async def test_get_user(session):
    assert await database.get_user(session, '') is None
