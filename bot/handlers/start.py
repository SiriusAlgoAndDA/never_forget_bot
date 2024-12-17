import aiogram
from aiogram import filters, types


router = aiogram.Router()


@router.message(filters.Command('start'))
async def handler_start(message: types.Message) -> None:
    await message.reply('Hello!')
