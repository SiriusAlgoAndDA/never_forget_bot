import datetime

from bot.database import models


async def current_time(user: models.User) -> str:
    cur_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=user.timezone))).strftime(
        '%H:%M:%S %d.%m.%Y'
    )
    return cur_time
