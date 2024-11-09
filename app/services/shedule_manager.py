import asyncio
from datetime import datetime, timedelta
from sqlalchemy import and_
from sqlalchemy.future import select
from app.db.models import Notification
from app.db.db_session import db_helper
from app.tg_bot import bot


# TODO: разораться с тайм зоной
# TODO: отрефакторить этот шедулер, убрать костыль с датой 9999 года, убрать констрейт на базе?
async def check_reminders():
    time_now = datetime.utcnow() + timedelta(hours=3)
    async with db_helper.session_factory() as session:
        stmt = select(Notification).where(
            and_(
                (time_now + timedelta(minutes=30)) >= Notification.time_to_notify,
                Notification.is_sent == False,
            )
        )
        reminders = await session.scalars(stmt)
        for noti in reminders.unique():
            await bot.send_message(
                chat_id=noti.telegram_id,
                text=f"Время: {noti.time_to_notify}\n\nНапоминание: {noti.notification_text}",
            )
            noti.is_sent = True
            noti.time_to_notify = datetime(9999, 12, 11)
            session.add(noti)
            await session.commit()


async def reminder_scheduler():
    while True:
        await check_reminders()
        await asyncio.sleep(5)
