# bot/handlers/common.py
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.webapp.settings')

import django

django.setup()

from webapp.admin_panel.models import User, Student
from bot.keyboards.student_kb import main_student_menu, faq_keyboard
from bot.keyboards.admin_kb import main_admin_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start komandasi"""
    await state.clear()

    telegram_id = message.from_user.id

    # Foydalanuvchini tekshirish
    try:
        user = await User.objects.aget(telegram_id=telegram_id)

        if user.role == 'admin':
            await message.answer(
                f"Assalomu alaykum, Admin!\n\n"
                f"Sizning telegram ID: {telegram_id}\n"
                f"Sizning role: {user.get_role_display()}",
                reply_markup=main_admin_menu()
            )
        elif user.role == 'accountant':
            await message.answer(
                f"Assalomu alaykum, Buxgalter!\n\n"
                f"Sizning telegram ID: {telegram_id}",
                reply_markup=main_admin_menu()
            )
        elif user.role == 'student':
            try:
                student = await Student.objects.select_related('user', 'group').aget(user=user)
                await message.answer(
                    f"Assalomu alaykum, {student.first_name}!\n\n"
                    f"👤 Talaba ID: {student.student_id}\n"
                    f"👥 Guruh: {student.group.name if student.group else 'Biriktirilmagan'}\n\n"
                    f"Quyidagi tugmalardan birini tanlang:",
                    reply_markup=main_student_menu()
                )
            except Student.DoesNotExist:
                await message.answer(
                    "Sizning profil ma'lumotlaringiz topilmadi.\n"
                    "Iltimos, administrator bilan bog'laning."
                )
        else:
            await message.answer(
                f"Assalomu alaykum!\n\n"
                f"Sizning telegram ID: {telegram_id}"
            )

    except User.DoesNotExist:
        await message.answer(
            f"Assalomu alaykum!\n\n"
            f"Siz hali ro'yxatdan o'tmagansiz.\n"
            f"Sizning telegram ID: {telegram_id}\n\n"
            f"Iltimos, bu ID ni administrator ga yuboring."
        )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam komandasi"""
    help_text = """
🤖 ISFT Bot - Yordam

📋 Asosiy komandalar:
/start - Botni ishga tushirish
/help - Yordam
/id - Telegram ID ni ko'rish

👨‍🎓 Talabalar uchun:
• Chek yuborish
• To'lovlar tarixi
• To'lov jadvali
• Buxgalteriya bilan aloqa
• FAQ

👨‍💼 Adminlar uchun:
• Talabalarni boshqarish
• Guruhlarni boshqarish
• To'lov jadvalini sozlash
• Cheklarni ko'rish va tasdiqlash
• Statistika

📞 Texnik yordam: @admin_username
"""
    await message.answer(help_text)


@router.message(Command("id"))
async def cmd_id(message: Message):
    """Telegram ID ni ko'rsatish"""
    await message.answer(
        f"📱 Sizning Telegram ID: <code>{message.from_user.id}</code>\n"
        f"👤 Username: @{message.from_user.username or 'Yo\'q'}",
        parse_mode="HTML"
    )


@router.message(F.text == "❓ FAQ")
async def show_faq(message: Message):
    """FAQ ni ko'rsatish"""
    await message.answer(
        "❓ <b>Ko'p beriladigan savollar</b>\n\n"
        "Quyidagi mavzulardan birini tanlang:",
        reply_markup=faq_keyboard(),
        parse_mode="HTML"
    )