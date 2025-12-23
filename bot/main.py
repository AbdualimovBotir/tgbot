import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import BOT_TOKEN
from bot.handlers import common, student, admin
from bot.services.reminder_service import ReminderService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot"""
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Include routers
    dp.include_router(common.router)
    dp.include_router(student.router)
    dp.include_router(admin.router)

    # Start reminder service
    reminder_service = ReminderService(bot)
    reminder_service.start()

    try:
        logger.info("Bot is starting...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())