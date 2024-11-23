import asyncio

from app.services.reminder.shedule_manager import reminder_scheduler
from app.tg_bot import bot, dp


async def main():
    polling_task = asyncio.create_task(dp.start_polling(bot))
    reminders_task = asyncio.create_task(reminder_scheduler())

    await asyncio.gather(polling_task, reminders_task)


if __name__ == "__main__":
    asyncio.run(main())
