from aiogram import types


def get_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text='Отмена', callback_data='cancel'),
            ]
        ]
    )
