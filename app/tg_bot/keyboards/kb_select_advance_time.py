from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def make_kb_select_advance_time() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=str(advance_time), callback_data=str(advance_time)
            )
            for advance_time in (1, 10, 30, 60)
        ]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    return markup
