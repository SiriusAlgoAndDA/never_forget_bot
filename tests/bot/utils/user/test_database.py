from bot.utils.user import database


async def test_get_user(session):
    assert await database.get_user(session, '') is None
