import aiogram
from aiogram import filters, types
from bot.temporal.send_notify import new_event
import datetime


router = aiogram.Router()


@router.message(filters.Command('start'))
async def handler_start(message: types.Message) -> None:
    send_timestamp = (datetime.datetime.now() + datetime.timedelta(seconds=10)).timestamp()
    await new_event(message.from_user.id, "Hello from Temporal!", send_timestamp)
    await message.reply('Hello!')
