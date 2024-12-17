from bot import config
from bot.bot_helper import bot
from bot.utils.common import get_datetime_msk_tz


MESSAGE_ID = None
DT_FORMAT = '%Y-%m-%d %H:%M:%S'


async def send_ping_status(result: dict[str, dict[str, str]]) -> None:
    settings = config.get_settings()
    all_ok = True
    message = (
        f'Server: {settings.PROJECT_NAME}'
        f'Ping status (last update: '
        f'{get_datetime_msk_tz().strftime(DT_FORMAT)}):\n'
    )
    for host, endpoints in result.items():
        message += f'\n{host}:\n'
        for endpoint, status in endpoints.items():
            all_ok = all_ok and status == 'Successful'
            emoji = '✅' if status == 'Successful' else '❌'
            message += f'{emoji}{endpoint}: {status}\n'
    global MESSAGE_ID  # pylint: disable=global-statement
    if MESSAGE_ID is None or not all_ok:
        MESSAGE_ID = await bot.bot.send_message(
            chat_id=settings.TG_ERROR_CHAT_ID,
            text=message,
        )
        await bot.bot.pin_chat_message(
            chat_id=settings.TG_ERROR_CHAT_ID,
            message_id=MESSAGE_ID.message_id,
        )
    else:
        await bot.bot.edit_message_text(
            chat_id=settings.TG_ERROR_CHAT_ID,
            message_id=MESSAGE_ID.message_id,
            text=message,
        )
