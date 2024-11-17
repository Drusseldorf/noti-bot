from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import Message, CallbackQuery
from sqlalchemy.exc import IntegrityError
from app.db.db_session import db_helper
import datetime as dt
from app.db.requests.notification_requests import create_notification
from app.db.requests.user_requests import get_user_by_telegram_id
from app.helpers.datetime_helpers import get_user_current_datetime, is_event_in_past
from app.tg_bot.keyboards.kb_select_advance_time import make_kb_select_advance_time
from app.tg_bot.ru_text.ru_text import ru_message

fsm_get_noti_router = Router()

DATE_TIME_PATTERN = (
    r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4} ([01]\d|2[0-3]):[0-5]\d$"
)


class FSMFillNoti(StatesGroup):
    fill_date = State()
    fill_text = State()
    fill_advance_time = State()


@fsm_get_noti_router.message(
    Command(commands="cancel"),
    StateFilter(FSMFillNoti.fill_date, FSMFillNoti.fill_text),
)
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(ru_message.cancel)
    await state.clear()


@fsm_get_noti_router.message(
    Command(commands="make_notification"), StateFilter(default_state)
)
async def process_make_noti_command(message: Message, state: FSMContext):
    await message.answer(ru_message.fill_date_and_time)
    await state.set_state(FSMFillNoti.fill_date)


@fsm_get_noti_router.message(
    StateFilter(FSMFillNoti.fill_date), F.text.regexp(DATE_TIME_PATTERN)
)
async def process_date_sent(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    data = await state.get_data()

    async with db_helper.session_factory() as session:
        user = await get_user_by_telegram_id(
            session=session, telegram_id=message.from_user.id
        )

    if is_event_in_past(data["date"], user.user_timezone_offset):
        await message.answer(ru_message.date_in_past)
        return

    await message.answer(ru_message.fill_notification_text)
    await state.set_state(FSMFillNoti.fill_text)


@fsm_get_noti_router.message(StateFilter(FSMFillNoti.fill_date))
async def warning_wrong_date(message: Message):
    await message.answer(ru_message.wrong_date_format)


@fsm_get_noti_router.message(StateFilter(FSMFillNoti.fill_text))
async def process_notification_text_sent(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        text=ru_message.notification_advance_time,
        reply_markup=make_kb_select_advance_time(),
    )
    await state.set_state(FSMFillNoti.fill_advance_time)


@fsm_get_noti_router.callback_query(StateFilter(FSMFillNoti.fill_advance_time))
async def process_fill_advance_time(callback: CallbackQuery, state: FSMContext):
    await state.update_data(advance_time=callback.data)
    data = await state.get_data()
    async with db_helper.session_factory() as session:
        try:
            await create_notification(
                session=session,
                telegram_id=callback.from_user.id,
                notification_text=data["text"],
                event_time_utc=dt.datetime.strptime(data["date"], "%d.%m.%Y %H:%M"),
                notification_advance_time=int(data["advance_time"]),
            )
            await callback.message.edit_text(
                ru_message.notification_created.format(
                    data["date"], data["text"], data["advance_time"]
                )
            )
        except IntegrityError:
            await callback.message.edit_text(ru_message.something_went_wrong)
    await state.clear()
