import aiogram
from aiogram import filters, types
from aiogram.fsm.context import FSMContext

from bot.text import text_data


router = aiogram.Router()


@router.message(filters.Command('start'))
async def handler_start(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user is None:
        raise RuntimeError('User is None')
    await message.reply(text_data.TextData.MSG_START, reply_markup=types.ReplyKeyboardRemove())
