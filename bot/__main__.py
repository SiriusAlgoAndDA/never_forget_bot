import asyncio

import loguru

from bot import config, creator
from bot.bot_helper import send


async def main() -> None:
    settings = config.get_settings()

    await send.send_message_safe(
        logger=loguru.logger,
        message=f'Created bot: debug={settings.DEBUG}',
        level='info',
    )

    bot, dp = creator.get_bot()
    loguru.logger.info('Bot starting...')
    await dp.start_polling(bot)


if __name__ == '__main__':  # pragma: no cover
    asyncio.run(main())
