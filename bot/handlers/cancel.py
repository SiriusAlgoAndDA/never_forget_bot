import aiogram
from aiogram import F, types
from aiogram.fsm import context

from bot.text import text_data


router = aiogram.Router()


@router.callback_query(F.data == 'cancel')
async def callback_handler_cancel(callback_query: types.CallbackQuery, state: context.FSMContext) -> None:
    message = callback_query.message
    await state.clear()
    if message:
        await message.answer(text_data.TextData.ACTION_CANCEL, reply_markup=types.ReplyKeyboardRemove())
    await callback_query.answer(text=text_data.TextData.ACTION_CANCEL)
