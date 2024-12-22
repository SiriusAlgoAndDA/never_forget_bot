import aiogram
from aiogram import F, types
from aiogram.filters import StateFilter

from bot.database import models
from bot.middlewares.check_user import CheckUserMiddleware
from bot.utils import event_utils


router = aiogram.Router()
router.message.middleware(CheckUserMiddleware())


@router.message(F.text, StateFilter(None), ~F.text.startswith('/'))
async def message_for_user(message: types.Message, user: models.User) -> None:
    if not message.text:
        raise RuntimeError('No text')

    await message.reply('Парсим текст...')
    await event_utils.process_message(text=message.text, user=user)
    await message.reply('Сообщение отправлено в обработку...')
