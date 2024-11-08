from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.types import Message
from app.db.db_session import db_helper
from datetime import datetime
from app.db.requests import create_notification


fsm_router = Router()

DATE_TIME_PATTERN = (
    r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4} ([01]\d|2[0-3]):[0-5]\d$"
)


class FSMFillNoti(StatesGroup):
    fill_date = State()
    fill_text = State()


# cancel вне состояния заполнения напоминалки
@fsm_router.message(Command(commands="cancel"), StateFilter(default_state))
async def process_wrong_cancel_command(message: Message):
    await message.answer(
        text="Отменять нечего. Вы вне процесса создания напоминалки\n\n"
        "Чтобы перейти к созданию напоминалки - "
        "отправьте команду /make_noti"
    )


# cancel во время состояния заполнения напоминалки
@fsm_router.message(Command(commands="cancel"), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text="Вы вышли из создания напоминалки\n\n"
        "Чтобы снова перейти к заполнению напоминалки - "
        "отправьте команду /make_noti"
    )
    await state.clear()


# инициирует создание напоминалки, переводим в состояние заполнения даты и времени
@fsm_router.message(Command(commands="make_noti"), StateFilter(default_state))
async def process_make_noti_command(message: Message, state: FSMContext):
    await message.answer(
        text="Пожалуйста, введите дату и время в формате: ДД.ММ.ГГГГ ЧЧ:ММ"
    )
    await state.set_state(FSMFillNoti.fill_date)


# дата и время введены корректно, переводим в состояние заполнения текста напоминалки
@fsm_router.message(
    StateFilter(FSMFillNoti.fill_date), F.text.regexp(DATE_TIME_PATTERN)
)
async def process_date_sent(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    data = await state.get_data()
    if datetime.strptime(data["date"], "%d.%m.%Y %H:%M") <= datetime.utcnow():
        await message.answer("Укажите дату в будущем :)\n\nПопробуйте еще раз")
        return
    await state.update_data(date=message.text)
    await message.answer(text="Спасибо!\n\nА теперь введите текст вашей напоминалки")
    await state.set_state(FSMFillNoti.fill_text)


# дата и время введены некорректно
@fsm_router.message(StateFilter(FSMFillNoti.fill_date))
async def warning_wrong_date(message: Message):
    await message.answer(
        text="То, что вы отправили не похоже на дату со временем или вы ошиблись с форматом ввода\n\n"
        "Пожалуйста, введите дату и время в формате: ДД.ММ.ГГГГ ЧЧ:ММ\n\n"
        "Если вы хотите прервать заполнение - "
        "отправьте команду /cancel"
    )


# текст напоминалки получен, записываем в БД полученные данные. Выводим из машины состояний
@fsm_router.message(StateFilter(FSMFillNoti.fill_text))
async def process_text_sent(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    async with db_helper.session_factory() as session:
        result = await create_notification(
            session=session,
            telegram_id=message.from_user.id,
            notification_text=data["text"],
            time_to_notify=datetime.strptime(data["date"], "%d.%m.%Y %H:%M"),
        )
        if result:
            await message.answer(
                "Спасибо! Ваша напоминалка создана:\n\n"
                f"Время: {data['date']}\n"
                f"Текст: {data['text']}\n\n"
                "Посмотреть ваши напоминалки: /get_all_noti"
            )
        else:
            await message.answer(
                "Упппс, что-то пошло не так :(\n\nПопробуйте еще раз /make_noti"
            )

    await state.clear()


@fsm_router.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text="Извините, моя твоя не понимать")
