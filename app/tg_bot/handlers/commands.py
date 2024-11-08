from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message
from app.db.db_session import db_helper
from app.db.requests import (
    create_user_if_not_exist,
    get_all_notifications,
)

commands_router = Router()


# TODO: нужны команды с хелпом, и вынести текст сообщения в отдельный модуль
# TODO: сделать красивее, убрать проверки, запросы в бд в хелперы / отедельно, подумать
@commands_router.message(CommandStart(), StateFilter(default_state))
async def start_command(message: Message):
    await message.answer(
        "Привет, я бот Noti!\n"
        "Я помогу тебе создать напоминалки о предстоящих событиях\n\n"
        "Используй команду /make_noti для создания напоминалки!"
    )
    async with db_helper.session_factory() as session:
        await create_user_if_not_exist(
            session=session, telegram_id=message.from_user.id
        )


@commands_router.message(Command(commands="get_all_noti"), StateFilter(default_state))
async def get_all_noti_command(message: Message):
    async with db_helper.session_factory() as session:
        await create_user_if_not_exist(
            session=session, telegram_id=message.from_user.id
        )
        notis = await get_all_notifications(
            session=session, telegram_id=message.from_user.id
        )
    if not notis:
        await message.answer(
            "Похоже что у тебя еще нет нотификаций\n\nИспользуй команду /make_noti чтобы создать"
        )
    for text, date in notis:
        await message.answer(f"Время: {date}\nТекст: {text}")
    await message.answer("Создать еще нотификацию /make_noti")
