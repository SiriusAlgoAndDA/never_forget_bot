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

    main_message = await message.reply('Парсим текст...')
    await event_utils.process_message(text=message.text, user=user, message_id=main_message.message_id)
    await main_message.edit_text('Сообщение отправлено в обработку...')
