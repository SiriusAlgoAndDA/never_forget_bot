import json

import aiogram
from aiogram import F, types

from bot.database import models
from bot.middlewares.check_user import CheckUserMiddleware
from bot.utils.gpt import yandex_gpt


router = aiogram.Router()
router.message.middleware(CheckUserMiddleware())


@router.message(F.text)
async def message_for_user(message: types.Message, user: models.User) -> None:
    data = await yandex_gpt.request_to_gpt(message, user)
    try:
        t = json.loads(data)
        await message.reply(json.dumps(t, ensure_ascii=False))
    except json.JSONDecodeError:
        await message.reply('При обработке запроса произошла ошибка. Повторите запрос в ближайшее время')
