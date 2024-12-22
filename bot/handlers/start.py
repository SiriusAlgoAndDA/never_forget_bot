import aiogram
from aiogram import filters, types
from aiogram.fsm.context import FSMContext


router = aiogram.Router()


@router.message(filters.Command('start'))
async def handler_start(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user is None:
        raise RuntimeError('User is None')
    await message.reply('Hello!', reply_markup=types.ReplyKeyboardRemove())
