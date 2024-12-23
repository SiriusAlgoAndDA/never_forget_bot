import uuid

from aiogram.filters import callback_data
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NotifyKeyboardData(callback_data.CallbackData, prefix='event'):
    action: str
    event_id: str
    delay_time: str | None = None


def get_keyboard(event_id: str | uuid.UUID) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text='+10 min',
        callback_data=NotifyKeyboardData(action='delay', event_id=str(event_id), delay_time='10m'),
    )
    builder.button(
        text='+1 hour',
        callback_data=NotifyKeyboardData(action='delay', event_id=str(event_id), delay_time='1h'),
    )
    builder.button(
        text='+1 day',
        callback_data=NotifyKeyboardData(action='delay', event_id=str(event_id), delay_time='1d'),
    )
    builder.button(
        text='🕘Отложить на другое время', callback_data=NotifyKeyboardData(action='delay', event_id=str(event_id))
    )
    builder.button(text='✅Сделано', callback_data=NotifyKeyboardData(action='complete', event_id=str(event_id)))
    builder.button(text='🚫Удалить', callback_data=NotifyKeyboardData(action='delete', event_id=str(event_id)))
    builder.button(text='❌Не сделано', callback_data=NotifyKeyboardData(action='not_complete', event_id=str(event_id)))

    builder.adjust(3, 1, 1, 1, 1)
    return builder.as_markup()
