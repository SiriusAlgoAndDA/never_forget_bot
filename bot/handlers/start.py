import datetime

import aiogram
from aiogram import filters, types

from bot.temporal.ReminderWorkflow import new_event


router = aiogram.Router()


@router.message(filters.Command('start'))
async def handler_start(message: types.Message) -> None:
    send_timestamp = (datetime.datetime.now() + datetime.timedelta(seconds=10)).timestamp()
    if message.from_user is None:
        raise RuntimeError("User is None")
    await new_event(message.from_user.id, 'Hello from Temporal!', send_timestamp)
    await message.reply('Hello!')
