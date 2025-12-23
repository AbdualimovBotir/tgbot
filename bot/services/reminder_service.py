# bot/services/reminder_service.py
from datetime import datetime, timedelta
from typing import List
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.webapp.settings')

import django

django.setup()

from webapp.admin_panel.models import (
    PaymentSchedule, Student, PaymentReminder,
    ReminderTemplate, Group
)
from bot.config import REMINDER_DAYS


class ReminderService:
    """To'lov eslatmalari xizmati"""

    @staticmethod
    async def create_reminders_for_schedule(schedule_id: int):
        """
        To'lov jadvali uchun eslatmalarni yaratish
        """
        try:
            schedule = await PaymentSchedule.objects.aget(id=schedule_id)
            students = Student.objects.filter(is_active=True)

            created_count = 0
            async for student in students:
                for days in REMINDER_DAYS:
                    reminder, created = await PaymentReminder.objects.aget_or_create(
                        payment_schedule=schedule,
                        student=student,
                        days_before=days
                    )
                    if created:
                        created_count += 1

            return created_count
        except Exception as e:
            print(f"Eslatma yaratishda xatolik: {e}")
            return 0

    @staticmethod
    async def get_due_reminders() -> List[PaymentReminder]:
        """
        Yuborish kerak bo'lgan eslatmalarni olish
        """
        today = datetime.now().date()

        reminders = []

        async for reminder in PaymentReminder.objects.filter(
                is_sent=False
        ).select_related('payment_schedule', 'student', 'student__user', 'student__group'):

            schedule = reminder.payment_schedule
            days_until_due = (schedule.due_date - today).days

            # Agar belgilangan kun bo'lsa
            if days_until_due == reminder.days_before:
                reminders.append(reminder)

        return reminders

    @staticmethod
    async def send_reminder(bot, reminder: PaymentReminder):
        """
        Eslatmani yuborish
        """
        try:
            student = reminder.student
            schedule = reminder.payment_schedule

            # Shablon olish
            template = await ReminderTemplate.objects.filter(
                days_before=reminder.days_before,
                is_active=True
            ).afirst()

            if not template:
                # Default xabar
                message_text = ReminderService._get_default_message(reminder)
            else:
                message_text = template.message_text.format(
                    student_name=student.first_name,
                    stage=schedule.stage,
                    due_date=schedule.due_date.strftime('%d.%m.%Y'),
                    days=reminder.days_before,
                    amount=schedule.amount
                )

            # Talabaga yuborish
            if student.user and student.user.telegram_id:
                try:
                    await bot.send_message(
                        chat_id=student.user.telegram_id,
                        text=message_text,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"Talabaga yuborishda xatolik: {e}")

            # Guruhga yuborish
            if student.group and student.group.telegram_chat_id and student.group.is_active:
                try:
                    group_message = f"📢 {student.full_name}\n\n{message_text}"
                    await bot.send_message(
                        chat_id=student.group.telegram_chat_id,
                        text=group_message,
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"Guruhga yuborishda xatolik: {e}")

            # Eslatmani belgilash
            reminder.is_sent = True
            reminder.sent_at = datetime.now()
            await reminder.asave()

            return True

        except Exception as e:
            print(f"Eslatma yuborishda xatolik: {e}")
            return False

    @staticmethod
    def _get_default_message(reminder: PaymentReminder) -> str:
        """Default eslatma xabari"""
        student = reminder.student
        schedule = reminder.payment_schedule
        days = reminder.days_before

        if days == 0:
            urgency = "🔴 <b>BUGUN!</b>"
            message = "Bugun to'lov kuni!"
        elif days <= 3:
            urgency = "🟠 <b>SHOSHILING!</b>"
            message = f"{days} kun qoldi"
        elif days <= 7:
            urgency = "🟡 <b>DIQQAT!</b>"
            message = f"{days} kun qoldi"
        else:
            urgency = "🟢 <b>Eslatma</b>"
            message = f"{days} kun qoldi"

        return f"""
{urgency}

👤 {student.first_name}, to'lov muddati yaqinlashmoqda!

📊 To'lov bosqichi: {schedule.stage}
📅 Muddat: {schedule.due_date.strftime('%d.%m.%Y')}
⏰ {message}
💰 Summa: {schedule.amount} so'm

📤 To'lovdan keyin chekni botga yuborishni unutmang!

⚠️ Muddatida to'lash majburiy!
"""

    @staticmethod
    async def check_and_send_reminders(bot):
        """
        Barcha eslatmalarni tekshirish va yuborish
        (Har kuni avtomatik ishga tushadi)
        """
        reminders = await ReminderService.get_due_reminders()

        sent_count = 0
        for reminder in reminders:
            success = await ReminderService.send_reminder(bot, reminder)
            if success:
                sent_count += 1

        return sent_count