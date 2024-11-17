from aiogram import Dispatcher, Bot
from app.tg_bot.handlers.fsm_get_notification import fsm_get_noti_router
from config_data.config import settings
from app.tg_bot.handlers.defoult_state_commands import defoult_state_commands_router
from app.tg_bot.handlers.fsm_start_edit_profile import fsm_edit_profile

bot = Bot(token=settings.bot_token)

dp = Dispatcher()

dp.include_router(fsm_get_noti_router)
dp.include_router(fsm_edit_profile)
dp.include_router(defoult_state_commands_router)
