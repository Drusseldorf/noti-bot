from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import Message
from app.db.db_session import db_helper
from app.db.requests.notification_requests import get_all_unsent_notifications
from app.db.requests.user_requests import get_user_by_telegram_id
from app.helpers.datetime_helpers import to_user_time
from app.tg_bot.ru_text.ru_text import ru_message

defoult_state_commands_router = Router()


# TODO: добавить обработчкики для получения всех отправленных уведомлений,
# для редактирования уведомлений, для удаления уведомлений
# TODO: нужны команды с хелпом
# TODO: передавать сессию бд через мидлвари


@defoult_state_commands_router.message(
    Command(commands="cancel"), StateFilter(default_state)
)
async def process_wrong_cancel_command(message: Message):
    await message.answer(text=ru_message.cancel_wrong)


@defoult_state_commands_router.message(
    Command(commands="my_notifications"), StateFilter(default_state)
)
async def process_my_notifications_command(message: Message):
    async with db_helper.session_factory() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        notifications = await get_all_unsent_notifications(
            session=session, telegram_id=message.from_user.id
        )
        if not notifications:
            await message.answer(ru_message.no_notifications_yet)
        else:
            if user:
                for notification_message in notifications:
                    notification_message = ru_message.notifications.format(
                        to_user_time(
                            notification_message.event_time_utc,
                            user.user_timezone_offset,
                        ),
                        notification_message.notification_text,
                        notification_message.notification_advance_time,
                    )
                    await message.answer(notification_message)


@defoult_state_commands_router.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply("такой команды я пока не знаю :(")
