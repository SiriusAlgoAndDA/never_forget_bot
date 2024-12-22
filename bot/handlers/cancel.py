import aiogram
from aiogram import F, types
from aiogram.fsm import context

from bot.text import text_data


router = aiogram.Router()


@router.callback_query(F.data == 'cancel')
async def callback_handler_cancel(callback_query: types.CallbackQuery, state: context.FSMContext) -> None:
    await state.clear()

    message = callback_query.message
    if not isinstance(message, types.Message):
        raise RuntimeError('Action on InaccessibleMessage')
    if message and message.text:
        await message.edit_text(text_data.TextData.ACTION_CANCEL + '\n\n' + message.text)
    await callback_query.answer()
