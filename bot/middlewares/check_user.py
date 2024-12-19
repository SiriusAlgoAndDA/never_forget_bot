import typing

import aiogram.types

from bot.database.connection import SessionManager
from bot.utils.user_utils import add_user, get_user


class CheckUserMiddleware(aiogram.BaseMiddleware):
    async def __call__(
        self,
        handler: typing.Callable[[aiogram.types.TelegramObject, dict[str, typing.Any]], typing.Awaitable[typing.Any]],
        event: aiogram.types.Message,
        data: dict[str, typing.Any],
    ) -> typing.Any:
        async with SessionManager().create_async_session(expire_on_commit=False) as session:
            user = await get_user(session, str(event.from_user.id))
            if user is None:
                user = await add_user(session, str(event.from_user.id), str(event.from_user.username), str(event.from_user.full_name))
        data['user'] = user
        return await handler(event, data)

