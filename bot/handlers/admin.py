# bot/handlers/admin.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.webapp.settings')

import django

django.setup()

from webapp.admin_panel.models import User, Student, Group, Receipt, PaymentSchedule
from bot.keyboards.admin_kb import (
    main_admin_menu, student_management_keyboard,
    group_management_keyboard, payment_schedule_keyboard
)
from bot.config import ADMIN_IDS

router = Router()


def is_admin(telegram_id: int) -> bool:
    """Admin ekanligini tekshirish"""
    return telegram_id in ADMIN_IDS


@router.message(F.text == "👨‍🎓 Talabalar")
async def show_student_management(message: Message):
    """Talabalarni boshqarish"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu bo'lim faqat adminlar uchun!")
        return

    await message.answer(
        "👨‍🎓 <b>Talabalarni boshqarish</b>\n\n"
        "Kerakli amaliyotni tanlang:",
        reply_markup=student_management_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_list_students")
async def list_students(callback: CallbackQuery):
    """Talabalar ro'yxati"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    students = Student.objects.select_related('group').order_by('last_name')[:50]

    text = "👨‍🎓 <b>Talabalar ro'yxati</b>\n\n"

    count = 0
    async for student in students:
        count += 1
        text += f"{count}. {student.full_name}\n"
        text += f"   🆔 {student.student_id}\n"
        text += f"   👥 {student.group.name if student.group else '—'}\n"
        text += f"   📱 {student.phone}\n\n"

    if count == 0:
        text += "Talabalar topilmadi."
    elif count == 50:
        text += "\n⚠️ Faqat 50 ta talaba ko'rsatildi."

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "👥 Guruhlar")
async def show_group_management(message: Message):
    """Guruhlarni boshqarish"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu bo'lim faqat adminlar uchun!")
        return

    await message.answer(
        "👥 <b>Guruhlarni boshqarish</b>\n\n"
        "Kerakli amaliyotni tanlang:",
        reply_markup=group_management_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_list_groups")
async def list_groups(callback: CallbackQuery):
    """Guruhlar ro'yxati"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    groups = Group.objects.order_by('name')

    text = "👥 <b>Guruhlar ro'yxati</b>\n\n"

    count = 0
    async for group in groups:
        count += 1
        student_count = await group.students.acount()
        status = "✅" if group.is_active else "❌"

        text += f"{count}. {status} <b>{group.name}</b>\n"
        text += f"   👥 Talabalar: {student_count}\n"
        if group.telegram_chat_id:
            text += f"   🆔 Chat ID: <code>{group.telegram_chat_id}</code>\n"
        text += "\n"

    if count == 0:
        text += "Guruhlar topilmadi."

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "📅 To'lov jadvali")
async def show_schedule_management(message: Message):
    """To'lov jadvalini boshqarish"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu bo'lim faqat adminlar uchun!")
        return

    await message.answer(
        "📅 <b>To'lov jadvali</b>\n\n"
        "Kerakli amaliyotni tanlang:",
        reply_markup=payment_schedule_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_list_schedules")
async def list_schedules(callback: CallbackQuery):
    """To'lov jadvallari ro'yxati"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    schedules = PaymentSchedule.objects.order_by('-academic_year', 'stage')

    text = "📅 <b>To'lov jadvallari</b>\n\n"

    count = 0
    async for schedule in schedules:
        count += 1
        status = "✅" if schedule.is_active else "❌"

        text += f"{count}. {status} <b>{schedule.academic_year} - {schedule.stage}</b>\n"
        text += f"   📆 Muddat: {schedule.due_date.strftime('%d.%m.%Y')}\n"
        text += f"   💰 Summa: {schedule.amount} so'm\n\n"

    if count == 0:
        text += "To'lov jadvallari topilmadi."

    await callback.message.edit_text(text, parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "📋 Cheklar")
async def show_receipts(message: Message):
    """Cheklar ro'yxati"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu bo'lim faqat adminlar uchun!")
        return

    # Oxirgi 20 ta chekni olish
    receipts = Receipt.objects.select_related('student', 'payment_schedule').order_by('-submitted_at')[:20]

    text = "📋 <b>Oxirgi cheklar</b>\n\n"

    count = 0
    async for receipt in receipts:
        count += 1
        status_emoji = {
            'pending': '⏳',
            'approved': '✅',
            'rejected': '❌'
        }.get(receipt.status, '❓')

        text += f"{count}. {status_emoji} {receipt.student.full_name}\n"
        text += f"   🆔 {receipt.student.student_id}\n"
        text += f"   📊 {receipt.payment_schedule.stage}\n"
        text += f"   📅 {receipt.submitted_at.strftime('%d.%m.%Y %H:%M')}\n\n"

    if count == 0:
        text += "Cheklar topilmadi."

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    """Statistika ko'rsatish"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu bo'lim faqat adminlar uchun!")
        return

    # Statistika to'plash
    total_students = await Student.objects.acount()
    active_students = await Student.objects.filter(is_active=True).acount()
    total_groups = await Group.objects.acount()
    active_groups = await Group.objects.filter(is_active=True).acount()

    pending_receipts = await Receipt.objects.filter(status='pending').acount()
    approved_receipts = await Receipt.objects.filter(status='approved').acount()
    rejected_receipts = await Receipt.objects.filter(status='rejected').acount()

    text = f"""
📊 <b>STATISTIKA</b>

👨‍🎓 <b>Talabalar:</b>
   • Jami: {total_students}
   • Faol: {active_students}

👥 <b>Guruhlar:</b>
   • Jami: {total_groups}
   • Faol: {active_groups}

📋 <b>Cheklar:</b>
   • ⏳ Kutilmoqda: {pending_receipts}
   • ✅ Tasdiqlangan: {approved_receipts}
   • ❌ Rad etilgan: {rejected_receipts}
   • Jami: {pending_receipts + approved_receipts + rejected_receipts}
"""

    await message.answer(text, parse_mode="HTML")


# Chekni tasdiqlash/rad etish
@router.callback_query(F.data.startswith("approve_receipt_"))
async def approve_receipt(callback: CallbackQuery):
    """Chekni tasdiqlash"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    receipt_id = int(callback.data.replace("approve_receipt_", ""))

    try:
        user = await User.objects.aget(telegram_id=callback.from_user.id)
        receipt = await Receipt.objects.select_related('student').aget(id=receipt_id)

        receipt.status = 'approved'
        receipt.reviewed_by = user
        receipt.reviewed_at = datetime.now()
        await receipt.asave()

        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
            parse_mode="HTML"
        )

        # Talabaga xabar yuborish
        if receipt.student.user and receipt.student.user.telegram_id:
            try:
                await callback.bot.send_message(
                    chat_id=receipt.student.user.telegram_id,
                    text=f"✅ Sizning chekingiz tasdiqlandi!\n\n"
                         f"📊 To'lov: {receipt.payment_schedule.stage}\n"
                         f"👤 Tasdiqladi: {user.get_full_name() or 'Admin'}"
                )
            except Exception:
                pass

        await callback.answer("✅ Tasdiqlandi!", show_alert=True)

    except Exception as e:
        await callback.answer(f"❌ Xatolik: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("reject_receipt_"))
async def reject_receipt(callback: CallbackQuery):
    """Chekni rad etish"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return

    receipt_id = int(callback.data.replace("reject_receipt_", ""))

    try:
        user = await User.objects.aget(telegram_id=callback.from_user.id)
        receipt = await Receipt.objects.select_related('student').aget(id=receipt_id)

        receipt.status = 'rejected'
        receipt.reviewed_by = user
        receipt.reviewed_at = datetime.now()
        await receipt.asave()

        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n❌ <b>RAD ETILDI</b>",
            parse_mode="HTML"
        )

        # Talabaga xabar yuborish
        if receipt.student.user and receipt.student.user.telegram_id:
            try:
                await callback.bot.send_message(
                    chat_id=receipt.student.user.telegram_id,
                    text=f"❌ Sizning chekingiz rad etildi!\n\n"
                         f"📊 To'lov: {receipt.payment_schedule.stage}\n"
                         f"📝 Iltimos, to'g'ri chek yuboring yoki buxgalteriya bilan bog'laning."
                )
            except Exception:
                pass

        await callback.answer("❌ Rad etildi!", show_alert=True)

    except Exception as e:
        await callback.answer(f"❌ Xatolik: {str(e)}", show_alert=True)


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    """Orqaga qaytish"""
    await callback.message.delete()
    await callback.message.answer(
        "Admin panel:",
        reply_markup=main_admin_menu()
    )
    await callback.answer()