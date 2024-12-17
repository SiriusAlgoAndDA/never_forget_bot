import pathlib

from aiogram import types

from bot.bot_helper import bot
from bot.config import get_settings


async def send_file(filename: str | pathlib.Path, caption: str, chat_id: str | None = None) -> None:
    chat_id = chat_id or get_settings().TG_ERROR_CHAT_ID
    await bot.bot.send_document(
        chat_id=chat_id,
        document=types.FSInputFile(filename, filename=caption),
        caption=caption,
        disable_notification=True,
    )
    # TODO: pyrogram
    # except aiogram_exceptions.NetworkError as exc:
    #     if str(exc).startswith('File too large for uploading'):
    #         with open(filename, 'rb') as f:
    #             async with bot.bot_client:
    #                 await bot.bot_client.send_document(
    #                     chat_id=int(chat_id),
    #                     document=f,
    #                     caption=caption,
    #                     disable_notification=True,
    #                 )
    #     else:
    #         raise exc
