from datetime import datetime

import aiogram
import dateutil.tz
import timezonefinder
from aiogram import F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.database import models
from bot.database.connection import SessionManager
from bot.markups import cancel_markup
from bot.middlewares.check_user import CheckUserMiddleware
from bot.text import text_data
from bot.utils.user_utils import change_timezone


class ChoosingTimezone(StatesGroup):
    choosing_timezone = State()


router = aiogram.Router()
router.message.middleware(CheckUserMiddleware())


@router.message(StateFilter(None), F.text, Command('change_timezone'))
async def change_timezone_tg(message: types.Message, user: models.User, state: FSMContext) -> None:
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text='Определить по геолокации', request_location=True))
    await message.reply(
        f'Текущий часовой пояс: {user.timezone}',
        reply_markup=builder.as_markup(one_time_keyboard=True),
    )
    await message.reply(
        'Пришлите новый часовой пояс относительно UTC (целую и дробную части таймзоны следует разделять точкой)',
        reply_markup=cancel_markup.get_keyboard(),
    )
    await state.set_state(ChoosingTimezone.choosing_timezone)


@router.message(ChoosingTimezone.choosing_timezone, F.text)
async def set_timezone(message: types.Message, state: FSMContext) -> None:
    if not message.text or not message.from_user:
        raise RuntimeError('No text or user')
    try:
        new_timezone = float(message.text)
    except ValueError:
        await message.reply('Некорректная таймзона')
        return
    if abs(new_timezone) > 12:
        await message.reply('Некорректная таймзона')
        return
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        await change_timezone(session, str(message.from_user.id), new_timezone)
    await state.clear()
    await message.reply(
        f'Таймзона успешно обновлена. Текущий часовой пояс: {new_timezone}', reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(ChoosingTimezone.choosing_timezone, F.location)
async def set_location_timezone(message: types.Message, state: FSMContext) -> None:
    if not message.location:
        raise RuntimeError('No message location')
    width = message.location.latitude
    length = message.location.longitude
    loc = timezonefinder.TimezoneFinder().timezone_at(lat=width, lng=length)
    if loc is None:
        await message.reply(text_data.TextData.MSG_TIMEZONE_LOC_ERROR)
        return
    new_timezone = dateutil.tz.gettz(loc)
    if new_timezone is None:
        await message.reply(text_data.TextData.MSG_TIMEZONE_LOC_ERROR)
        return
    offset = new_timezone.utcoffset(datetime.now()).total_seconds() / 3600  # type: ignore[union-attr]
    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        if not message.from_user:
            raise RuntimeError('No user id')
        await change_timezone(session, str(message.from_user.id), float(offset))
    await state.clear()
    await message.reply(
        text_data.TextData.MSG_TIMEZONE_CHANGE_OK.format(offset=float(offset)), reply_markup=types.ReplyKeyboardRemove()
    )
