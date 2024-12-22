from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram_calendar.schemas import SimpleCalAct

from sqlalchemy.exc import IntegrityError

from app.db.db_session import db_helper
from app.db.requests.notification_requests import create_notification
from app.db.requests.user_requests import get_user_by_telegram_id
from app.helpers.datetime_helpers import (
    is_event_in_past,
    to_utc,
    get_user_current_datetime,
)
from app.tg_bot.keyboards.kb_select_advance_time import (
    make_kb_select_advance_time,
)
from app.tg_bot.ru_text.ru_text import ru_message


TIME_PATTERN = r"^([01]\d|2[0-3]):([0-5]\d)$"


fsm_get_noti_router = Router()


class FSMFillNoti(StatesGroup):
    fill_date = State()
    fill_time = State()
    fill_text = State()
    fill_advance_time = State()


@fsm_get_noti_router.message(
    Command(commands="cancel"),
    StateFilter(
        FSMFillNoti.fill_date,
        FSMFillNoti.fill_text,
        FSMFillNoti.fill_time,
        FSMFillNoti.fill_advance_time,
    ),
)
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(ru_message.cancel)
    await state.clear()


@fsm_get_noti_router.message(
    Command(commands="make_notification"), StateFilter(default_state)
)
async def process_make_noti_command(message: Message, state: FSMContext):
    async with db_helper.session_factory() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)

    user_current_time = get_user_current_datetime(user.user_timezone_offset)

    await state.set_state(FSMFillNoti.fill_date)

    await message.answer(
        ru_message.fill_date.format(user_current_time),
        reply_markup=await SimpleCalendar(
            locale="ru_RU.UTF8"
        ).start_calendar(),
    )


@fsm_get_noti_router.callback_query(
    StateFilter(FSMFillNoti.fill_date), SimpleCalendarCallback.filter()
)
async def process_simple_calendar(
    callback_query: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
):
    if callback_data.act == SimpleCalAct.cancel:
        await callback_query.message.delete()
        await callback_query.message.answer(ru_message.cancel)
        await state.clear()
        return

    async with db_helper.session_factory() as session:
        user = await get_user_by_telegram_id(
            session, callback_query.from_user.id
        )

    calendar = SimpleCalendar(
        locale="ru_RU.UTF8",
        show_alerts=True,
    )

    user_current_time = get_user_current_datetime(user.user_timezone_offset)

    calendar.set_dates_range(
        user_current_time - timedelta(days=1),
        user_current_time + timedelta(weeks=52),
    )

    selected, date = await calendar.process_selection(
        callback_query, callback_data
    )

    if selected:
        date = date.strftime("%Y-%m-%d")
        await callback_query.message.delete()
        await state.update_data(date=date)
        await callback_query.message.answer(ru_message.fill_time.format(date))
        await state.set_state(FSMFillNoti.fill_time)


@fsm_get_noti_router.message(
    StateFilter(FSMFillNoti.fill_time), F.text.regexp(TIME_PATTERN)
)
async def process_time_sent(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    data = await state.get_data()

    date_time = f"{data['date']} {data['time']}"

    async with db_helper.session_factory() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)

    if is_event_in_past(date_time, user.user_timezone_offset):
        await message.answer(ru_message.date_in_past)
        return

    await message.answer(ru_message.fill_notification_text)
    await state.set_state(FSMFillNoti.fill_text)


@fsm_get_noti_router.message(StateFilter(FSMFillNoti.fill_time))
async def warning_wrong_time_format(message: Message):
    await message.answer(ru_message.wrong_time_format)


@fsm_get_noti_router.message(StateFilter(FSMFillNoti.fill_text))
async def process_notification_text_sent(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer(
        text=ru_message.notification_advance_time,
        reply_markup=make_kb_select_advance_time(),
    )
    await state.set_state(FSMFillNoti.fill_advance_time)


@fsm_get_noti_router.callback_query(StateFilter(FSMFillNoti.fill_advance_time))
async def process_fill_advance_time(
    callback: CallbackQuery, state: FSMContext
):
    await state.update_data(advance_time=callback.data)
    data = await state.get_data()
    async with db_helper.session_factory() as session:
        try:
            user = await get_user_by_telegram_id(
                session, callback.from_user.id
            )
            await create_notification(
                session=session,
                telegram_id=callback.from_user.id,
                notification_text=data["text"],
                event_time_utc=to_utc(
                    datetime.strptime(
                        f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M"
                    ),
                    user.user_timezone_offset,
                ),
                notification_advance_time=int(data["advance_time"]),
            )
            await callback.message.edit_text(
                ru_message.notification_created.format(
                    f"{data['date']} {data['time']}",
                    data["text"],
                    data["advance_time"],
                )
            )
        except IntegrityError:
            await callback.message.edit_text(ru_message.something_went_wrong)
    await state.clear()
