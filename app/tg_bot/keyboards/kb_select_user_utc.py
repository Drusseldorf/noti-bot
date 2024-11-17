from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def make_kb_select_user_utc() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text=f"+{utc_offset}", callback_data=str(utc_offset))
            for utc_offset in range(0, 4)
        ],
        [
            InlineKeyboardButton(text=str(utc_offset), callback_data=str(utc_offset))
            for utc_offset in range(-1, -4, -1)
        ],
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    return markup
