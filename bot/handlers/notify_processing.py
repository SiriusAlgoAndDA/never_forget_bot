import datetime

import aiogram
import loguru
from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.database.connection import SessionManager
from bot.markups import cancel_markup, notify_markup
from bot.utils.event_utils.database import EventStatus
from bot.utils.event_utils.service import set_finish_status


router = aiogram.Router()


class ChoosingDelayTime(StatesGroup):
    choosing_delay_time = State()


@router.callback_query(notify_markup.NotifyKeyboardData.filter(F.action == 'delay'))
async def delay(
    callback: types.CallbackQuery, callback_data: notify_markup.NotifyKeyboardData, state: FSMContext
) -> None:
    loguru.logger.info('Delay event {}', callback_data.event_id)

    if not isinstance(callback.message, types.Message):
        raise RuntimeError('Action on InaccessibleMessage')
    if not callback.message.text:
        raise RuntimeError('No message text')

    if callback_data.delay_time is None:
        await callback.message.edit_text('Откладываем событие.\n\n' + callback.message.text)
        await callback.message.reply(
            'Пришлите на сколько отложить напоминание, например: 1min, 1h, 1d, 2w',
            reply_markup=cancel_markup.get_keyboard(),
        )
        await state.set_state(ChoosingDelayTime.choosing_delay_time)
        await callback.answer()
        return

    seconds_delta = 10  # TODO pytimeparse callback_data.delay_time
    delta = datetime.timedelta(seconds=seconds_delta)

    # TODO run delay workflow:
    # TODO check event pending status
    # TODO cancel old notify workflow
    # TODO set terminated notification status in db
    # TODO add new notify workflow

    await callback.message.edit_text(
        f'Напомним о событии еще раз через {delta.total_seconds() / 60} минут.\n\n' + callback.message.text
    )
    await callback.answer()


@router.message(ChoosingDelayTime.choosing_delay_time, F.text)
async def delay_another(message: types.Message, state: FSMContext) -> None:
    seconds_delta = 10  # TODO pytimeparse callback_data.delay_time
    delta = datetime.timedelta(seconds=seconds_delta)

    # TODO run delay workflow:
    # TODO check event pending status
    # TODO cancel old notify workflow
    # TODO set terminated notification status in db
    # TODO add new notify workflow

    await message.reply(f'Напомним о событии еще раз через {delta.total_seconds() / 60} минут')
    await state.clear()


@router.callback_query(notify_markup.NotifyKeyboardData.filter(F.action == 'complete'))
async def complete(callback: types.CallbackQuery, callback_data: notify_markup.NotifyKeyboardData) -> None:
    loguru.logger.info('Complete event {}', callback_data.event_id)

    if not isinstance(callback.message, types.Message):
        raise RuntimeError('Action on InaccessibleMessage')
    if not callback.message.text:
        raise RuntimeError('No message text')

    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        await set_finish_status(session, callback_data.event_id, EventStatus.COMPLETED)

    await callback.message.edit_text('Событие выполнено.\n\n' + callback.message.text)
    await callback.answer()


@router.callback_query(notify_markup.NotifyKeyboardData.filter(F.action == 'not_complete'))
async def not_complete(callback: types.CallbackQuery, callback_data: notify_markup.NotifyKeyboardData) -> None:
    loguru.logger.info("Don't complete event {}", callback_data.event_id)

    if not isinstance(callback.message, types.Message):
        raise RuntimeError('Action on InaccessibleMessage')
    if not callback.message.text:
        raise RuntimeError('No message text')

    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        await set_finish_status(session, callback_data.event_id, EventStatus.NOT_COMPLETED)

    await callback.message.edit_text('Событие не сделано.\n\n' + callback.message.text)
    await callback.answer()


@router.callback_query(notify_markup.NotifyKeyboardData.filter(F.action == 'delete'))
async def delete(callback: types.CallbackQuery, callback_data: notify_markup.NotifyKeyboardData) -> None:
    loguru.logger.info('Deleting event {}', callback_data.event_id)

    if not isinstance(callback.message, types.Message):
        raise RuntimeError('Action on InaccessibleMessage')
    if not callback.message.text:
        raise RuntimeError('No message text')

    async with SessionManager().create_async_session(expire_on_commit=False) as session:
        await set_finish_status(session, callback_data.event_id, EventStatus.DELETED)

    await callback.message.edit_text('Событие удалено.\n\n' + callback.message.text)
    await callback.answer()
