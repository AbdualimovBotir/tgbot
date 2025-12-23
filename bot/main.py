# bot/main.py
import asyncio
import logging
import sys
import os
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Django sozlamalari
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.webapp.settings')

import django

django.setup()

from bot.config import BOT_TOKEN, TIMEZONE
from bot.handlers import common, student, admin, group
from bot.services.reminder_service import ReminderService

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot va dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Handlerlarni ro'yxatdan o'tkazish
dp.include_router(common.router)
dp.include_router(student.router)
dp.include_router(admin.router)
dp.include_router(group.router)

# Scheduler
scheduler = AsyncIOScheduler(timezone=TIMEZONE)


async def send_daily_reminders():
    """Har kuni eslatmalarni yuborish"""
    logger.info("Eslatmalar yuborish boshlandi...")
    try:
        sent_count = await ReminderService.check_and_send_reminders(bot)
        logger.info(f"{sent_count} ta eslatma yuborildi")
    except Exception as e:
        logger.error(f"Eslatma yuborishda xatolik: {e}")


async def on_startup():
    """Bot ishga tushganda"""
    logger.info("Bot ishga tushmoqda...")

    # Scheduler ishga tushirish
    scheduler.add_job(
        send_daily_reminders,
        'cron',
        hour=9,  # Har kuni soat 9:00 da
        minute=0,
        id='daily_reminders'
    )

    # Test uchun har soatda ham tekshirish
    scheduler.add_job(
        send_daily_reminders,
        'cron',
        hour='*/1',  # Har soat
        id='hourly_check'
    )

    scheduler.start()
    logger.info("Scheduler ishga tushdi")

    # Bot haqida ma'lumot
    bot_info = await bot.get_me()
    logger.info(f"Bot @{bot_info.username} ishga tushdi!")


async def on_shutdown():
    """Bot to'xtaganda"""
    logger.info("Bot to'xtatilmoqda...")
    scheduler.shutdown()
    await bot.session.close()
    logger.info("Bot to'xtatildi")


async def main():
    """Asosiy funksiya"""
    # Startup
    await on_startup()

    try:
        # Botni ishga tushirish
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        # Shutdown
        await on_shutdown()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi (KeyboardInterrupt)")
    except Exception as e:
        logger.error(f"Xatolik: {e}")