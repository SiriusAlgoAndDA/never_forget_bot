import json

import aiogram
from aiogram import F, types

from bot.database import models
from bot.middlewares.check_user import CheckUserMiddleware
from bot.utils.common import yandex_utils
from bot.utils.gpt import yandex_gpt
from bot.utils.stt import yandex_stt


router = aiogram.Router()
router.message.middleware(CheckUserMiddleware())


@router.message(F.voice)
async def voice_message(message: types.Message, user: models.User) -> None:
    if not message.voice or not message.bot:
        raise RuntimeError('No voice or bot')
    file_id = message.voice.file_id
    file = await message.bot.get_file(file_id)
    if not file.file_path:
        raise RuntimeError('No file_path')
    file_path = file.file_path
    file_object = await message.bot.download_file(file_path)
    if not file_object:
        raise RuntimeError('Failed to get file object')
    iam_token = await yandex_utils.get_iam_token()
    text = await yandex_stt.speech_request(file_object, iam_token=iam_token)
    data = await yandex_gpt.request_to_gpt(text, user, iam_token=iam_token)
    try:
        t = json.loads(data)
        await message.reply(json.dumps(t, ensure_ascii=False))
    except json.JSONDecodeError:
        await message.reply('При обработке запроса произошла ошибка. Повторите запрос в ближайшее время')
