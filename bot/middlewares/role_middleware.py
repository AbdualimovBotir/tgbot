# bot/middlewares/role_middleware.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.webapp.settings')

import django

django.setup()

from webapp.admin_panel.models import User


class RoleMiddleware(BaseMiddleware):
    """Foydalanuvchi rolini tekshirish middleware"""

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        telegram_id = event.from_user.id

        # Foydalanuvchini tekshirish
        try:
            user = await User.objects.aget(telegram_id=telegram_id)
            data['user'] = user
            data['role'] = user.role
        except User.DoesNotExist:
            data['user'] = None
            data['role'] = 'guest'

        # Handlerga o'tkazish
        return await handler(event, data)


class AdminOnlyMiddleware(BaseMiddleware):
    """Faqat adminlar uchun middleware"""

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        telegram_id = event.from_user.id

        try:
            user = await User.objects.aget(telegram_id=telegram_id)
            if user.role not in ['admin', 'accountant']:
                await event.answer("❌ Bu funksiya faqat adminlar uchun!")
                return
        except User.DoesNotExist:
            await event.answer("❌ Sizda ruxsat yo'q!")
            return

        return await handler(event, data)