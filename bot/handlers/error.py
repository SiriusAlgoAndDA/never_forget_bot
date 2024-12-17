import aiogram
import loguru
from aiogram import types


router = aiogram.Router()


@router.error()
async def error_handler(event: types.ErrorEvent) -> None:
    loguru.logger.critical('Critical error caused by %s', event.exception, exc_info=True)
