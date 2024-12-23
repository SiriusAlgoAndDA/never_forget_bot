import aiogram
from aiogram import filters, types
from aiogram.fsm.context import FSMContext

from bot.database import models
from bot.database.connection import SessionManager
from bot.markups import notify_markup
from bot.middlewares.check_user import CheckUserMiddleware
from bot.utils import notification_utils


router = aiogram.Router()
router.message.middleware(CheckUserMiddleware())


@router.message(filters.Command('show_events'))
async def show_events(message: types.Message, user: models.User, state: FSMContext) -> None:
    await state.clear()

    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        data = await notification_utils.get_active_notifications_by_user(
            session=session,
            user_id=user.id,
        )

    await message.reply(text=str(data), reply_markup=notify_markup.get_keyboard(event_id='123'))
