import aiogram
from aiogram import types
from aiogram.fsm.storage import memory

from bot import config, handlers, logger_config, middlewares


def bind_routers(dp: aiogram.Dispatcher) -> None:
    """
    Bind all routers to dispatcher.
    """
    for router in handlers.list_of_routers:
        dp.include_router(router)


async def get_bot(set_up_logger: bool = True) -> tuple[aiogram.Bot, aiogram.Dispatcher]:
    """
    Creates bot and all dependable objects.
    """
    settings = config.get_settings()

    bot = aiogram.Bot(token=settings.TG_BOT_TOKEN.get_secret_value())
    dp = aiogram.Dispatcher(storage=memory.MemoryStorage())

    dp.update.outer_middleware(middlewares.UniqueIDMiddleware())

    bind_routers(dp)

    if set_up_logger:
        logger_config.configure_logger(settings, log_file=settings.LOGGING_BOT_FILE, application='bot')

    await bot.set_my_commands(
        commands=[
            types.BotCommand(command='/start', description='Начать'),
            types.BotCommand(command='/help', description='Помощь'),
            types.BotCommand(command='/change_timezone', description='Поменять часовой пояс'),
            types.BotCommand(command='/upcoming_events', description='Показать ближайшие события'),
            types.BotCommand(command='/upcoming_notifications', description='Показать предстоящие уведомления'),
        ]
    )

    return bot, dp
