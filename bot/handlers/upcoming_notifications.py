import datetime

import aiogram
from aiogram import filters, types
from aiogram.fsm.context import FSMContext

from bot.database import models
from bot.database.connection import SessionManager
from bot.markups import notify_markup
from bot.middlewares.check_user import CheckUserMiddleware
from bot.text import text_data
from bot.utils import event_utils


router = aiogram.Router()
router.message.middleware(middleware=CheckUserMiddleware())


@router.message(filters.Command('upcoming_notifications'))
async def upcoming_notifications(message: types.Message, user: models.User, state: FSMContext) -> None:
    await state.clear()

    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        data = await event_utils.get_events_by_user_sorted(
            session=session,
            user_id=user.id,
            sort_by=event_utils.EventSortType.BY_NOTIFICATION_TIME,
        )

    for row in data:
        event_ts = row[2].astimezone(tz=datetime.timezone(offset=datetime.timedelta(hours=user.timezone)))
        next_notify_ts = row[3].astimezone(tz=datetime.timezone(offset=datetime.timedelta(hours=user.timezone)))

        text = text_data.TextData.EVENT_INFO.format(
            name=row[1].capitalize(),
            event_time=event_ts.strftime('%H:%M:%S %d.%m.%Y'),
            next_notify_time=next_notify_ts.strftime('%H:%M:%S %d.%m.%Y'),
        )
        await message.reply(text=text, reply_markup=notify_markup.get_keyboard(event_id=row[0]))

    if not data:
        await message.reply(text='Нет предстоящих уведомлений')
