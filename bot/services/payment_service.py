# bot/services/payment_service.py
from datetime import datetime, date
from typing import List, Dict, Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.webapp.settings')

import django

django.setup()

from webapp.admin_panel.models import (
    Student, PaymentSchedule, Receipt, PaymentReminder
)


class PaymentService:
    """To'lovlar xizmati"""

    @staticmethod
    async def get_student_payment_status(student_id: int) -> Dict:
        """
        Talabaning to'lov statusini olish
        """
        try:
            student = await Student.objects.aget(id=student_id)
            schedules = PaymentSchedule.objects.filter(is_active=True)

            status = {
                'student': student,
                'payments': []
            }

            async for schedule in schedules:
                receipt = await Receipt.objects.filter(
                    student=student,
                    payment_schedule=schedule
                ).afirst()

                payment_info = {
                    'schedule': schedule,
                    'has_receipt': receipt is not None,
                    'receipt': receipt,
                    'status': receipt.status if receipt else 'not_submitted',
                    'is_overdue': schedule.due_date < date.today() and not receipt
                }

                status['payments'].append(payment_info)

            return status

        except Student.DoesNotExist:
            return None

    @staticmethod
    async def get_overdue_students() -> List[Student]:
        """
        To'lovni kechiktirgan talabalarni olish
        """
        today = date.today()
        overdue_schedules = PaymentSchedule.objects.filter(
            due_date__lt=today,
            is_active=True
        )

        overdue_students = []

        async for schedule in overdue_schedules:
            students = Student.objects.filter(is_active=True)

            async for student in students:
                receipt = await Receipt.objects.filter(
                    student=student,
                    payment_schedule=schedule
                ).afirst()

                if not receipt:
                    overdue_students.append({
                        'student': student,
                        'schedule': schedule,
                        'days_overdue': (today - schedule.due_date).days
                    })

        return overdue_students

    @staticmethod
    async def get_payment_statistics(academic_year: Optional[str] = None) -> Dict:
        """
        To'lovlar statistikasi
        """
        filters = {'is_active': True}
        if academic_year:
            filters['academic_year'] = academic_year

        schedules = PaymentSchedule.objects.filter(**filters)

        stats = {
            'total_students': await Student.objects.filter(is_active=True).acount(),
            'stages': []
        }

        async for schedule in schedules:
            total_receipts = await Receipt.objects.filter(
                payment_schedule=schedule
            ).acount()

            approved_receipts = await Receipt.objects.filter(
                payment_schedule=schedule,
                status='approved'
            ).acount()

            pending_receipts = await Receipt.objects.filter(
                payment_schedule=schedule,
                status='pending'
            ).acount()

            rejected_receipts = await Receipt.objects.filter(
                payment_schedule=schedule,
                status='rejected'
            ).acount()

            not_submitted = stats['total_students'] - total_receipts

            stage_stats = {
                'schedule': schedule,
                'submitted': total_receipts,
                'not_submitted': not_submitted,
                'approved': approved_receipts,
                'pending': pending_receipts,
                'rejected': rejected_receipts,
                'completion_rate': (approved_receipts / stats['total_students'] * 100) if stats[
                                                                                              'total_students'] > 0 else 0
            }

            stats['stages'].append(stage_stats)

        return stats

    @staticmethod
    async def check_duplicate_receipt(student_id: int, schedule_id: int) -> bool:
        """
        Dublikat chekni tekshirish
        """
        exists = await Receipt.objects.filter(
            student_id=student_id,
            payment_schedule_id=schedule_id
        ).aexists()

        return exists

    @staticmethod
    async def get_upcoming_payments(days: int = 30) -> List:
        """
        Yaqinlashadigan to'lovlar
        """
        from datetime import timedelta

        today = date.today()
        future_date = today + timedelta(days=days)

        schedules = PaymentSchedule.objects.filter(
            due_date__gte=today,
            due_date__lte=future_date,
            is_active=True
        ).order_by('due_date')

        upcoming = []
        async for schedule in schedules:
            days_until = (schedule.due_date - today).days

            # Chek yubormaganlar soni
            total_students = await Student.objects.filter(is_active=True).acount()
            submitted = await Receipt.objects.filter(
                payment_schedule=schedule
            ).acount()

            upcoming.append({
                'schedule': schedule,
                'days_until': days_until,
                'total_students': total_students,
                'submitted': submitted,
                'not_submitted': total_students - submitted
            })

        return upcoming