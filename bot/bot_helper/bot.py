import aiogram

from bot import config


_settings = config.get_settings()
bot = aiogram.Bot(token=_settings.TG_HELPER_BOT_TOKEN)
