from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import Message, CallbackQuery
from app.db.db_session import db_helper
from app.db.requests.user_requests import (
    create_user,
    update_user,
    get_user_by_telegram_id,
)
from app.helpers.datetime_helpers import get_user_current_datetime
from app.tg_bot.keyboards.kb_select_user_utc import make_kb_select_user_utc
from app.tg_bot.ru_text.ru_text import ru_message

fsm_edit_profile = Router()


class FSMEditProfile(StatesGroup):
    fill_timezone = State()


@fsm_edit_profile.message(
    Command(commands="cancel"), StateFilter(FSMEditProfile.fill_timezone)
)
async def process_cancel_command_state(message: Message, state: FSMContext):
    async with db_helper.session_factory() as session:
        user = await get_user_by_telegram_id(
            session=session, telegram_id=message.from_user.id
        )

        if not user.user_timezone_offset:
            await message.answer(text=ru_message.no_timezone)
            return

    await message.answer(text=ru_message.cancel)
    await state.clear()


@fsm_edit_profile.message(
    Command(commands=("start", "edit")), StateFilter(default_state)
)
async def process_start_edit_profile(message: Message, state: FSMContext):
    async with db_helper.session_factory() as session:
        await create_user(session=session, telegram_id=message.from_user.id)

    utc_offset_markup = make_kb_select_user_utc()

    if message.text == "/start":
        await message.answer(
            text=ru_message.start_greeting, reply_markup=utc_offset_markup
        )

    elif message.text == "/edit":
        await message.answer(
            text=ru_message.edit_txt,
            reply_markup=utc_offset_markup,
        )

    await state.set_state(FSMEditProfile.fill_timezone)


@fsm_edit_profile.callback_query(StateFilter(FSMEditProfile.fill_timezone))
async def process_timezone_selection(
    callback: CallbackQuery, state: FSMContext
):
    await state.update_data(timezone_offset=callback.data)

    data = await state.get_data()

    async with db_helper.session_factory() as session:
        await update_user(
            session=session,
            telegram_id=callback.from_user.id,
            user_timezone_offset=int(data["timezone_offset"]),
        )

    await callback.message.edit_text(
        ru_message.user_timezone_set.format(
            get_user_current_datetime(int(data["timezone_offset"]))
        )
    )

    await state.clear()
