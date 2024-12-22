import aiogram
from aiogram import F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.database import models
from bot.database.connection import SessionManager
from bot.markups import cancel_markup
from bot.middlewares.check_user import CheckUserMiddleware
from bot.utils.user_utils import change_timezone


class ChoosingTimezone(StatesGroup):
    choosing_timezone = State()


router = aiogram.Router()
router.message.middleware(CheckUserMiddleware())


@router.message(StateFilter(None), F.text, Command('change_timezone'))
async def change_timezone_tg(message: types.Message, user: models.User, state: FSMContext) -> None:
    await message.reply(
        f'Текущий часовой пояс: {user.timezone}\n'
        f'Пришлите новый часовой пояс (целую и дробную части таймзоны следует разделять точкой)',
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
    await message.reply(f'Таймзона успешно обновлена. Текущий часовой пояс: {new_timezone}')
