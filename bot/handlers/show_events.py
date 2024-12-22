import aiogram
from aiogram import filters, types
from aiogram.fsm.context import FSMContext

from bot.markups import notify_markup


router = aiogram.Router()


@router.message(filters.Command('show_events'))
async def show_events(message: types.Message, state: FSMContext) -> None:
    await state.clear()

    # TODO get 5 events from db
    # TODO send one by one with markups

    await message.reply(text='Событие 1:...', reply_markup=notify_markup.get_keyboard(event_id='123'))
