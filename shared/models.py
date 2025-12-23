# shared/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Foydalanuvchi modeli"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('accountant', 'Buxgalter'),
        ('student', 'Talaba'),
        ('group_admin', 'Guruh Admin'),
    ]

    telegram_id = models.BigIntegerField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'


class Student(models.Model):
    """Talaba modeli"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    patronymic = models.CharField(max_length=100)
    passport_series = models.CharField(max_length=2)
    passport_number = models.CharField(max_length=7)
    jshshir = models.CharField(max_length=14, unique=True)
    phone = models.CharField(max_length=20)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Talaba'
        verbose_name_plural = 'Talabalar'

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.student_id})"


class Group(models.Model):
    """Guruh modeli"""
    name = models.CharField(max_length=100)
    telegram_chat_id = models.BigIntegerField(unique=True, null=True, blank=True)
    chat_title = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'groups'
        verbose_name = 'Guruh'
        verbose_name_plural = 'Guruhlar'

    def __str__(self):
        return self.name


class PaymentSchedule(models.Model):
    """To'lov jadvali"""
    STAGE_CHOICES = [
        ('1/4', '1/4'),
        ('2/4', '2/4'),
        ('3/4', '3/4'),
        ('4/4', '4/4'),
    ]

    academic_year = models.CharField(max_length=20)  # 2024-2025
    stage = models.CharField(max_length=5, choices=STAGE_CHOICES)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_schedules'
        verbose_name = 'To\'lov jadvali'
        verbose_name_plural = 'To\'lov jadvallari'
        unique_together = ['academic_year', 'stage']

    def __str__(self):
        return f"{self.academic_year} - {self.stage}"


class Receipt(models.Model):
    """To'lov cheki"""
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='receipts')
    payment_schedule = models.ForeignKey(PaymentSchedule, on_delete=models.CASCADE)
    file_id = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_receipts')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'receipts'
        verbose_name = 'Chek'
        verbose_name_plural = 'Cheklar'
        unique_together = ['student', 'payment_schedule']

    def __str__(self):
        return f"{self.student.student_id} - {self.payment_schedule.stage}"


class PaymentReminder(models.Model):
    """To'lov eslatmasi"""
    payment_schedule = models.ForeignKey(PaymentSchedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    days_before = models.IntegerField()  # 30, 15, 7, 3, 0
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'payment_reminders'
        verbose_name = 'Eslatma'
        verbose_name_plural = 'Eslatmalar'
        unique_together = ['payment_schedule', 'student', 'days_before']


class AnonymousMessage(models.Model):
    """Anonim xabar"""
    sender_telegram_id = models.BigIntegerField()
    message_text = models.TextField()
    reply_text = models.TextField(blank=True)
    replied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_replied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'anonymous_messages'
        verbose_name = 'Anonim xabar'
        verbose_name_plural = 'Anonim xabarlar'


class AccountingStaff(models.Model):
    """Buxgalteriya xodimlari"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    working_hours = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'accounting_staff'
        verbose_name = 'Buxgalter'
        verbose_name_plural = 'Buxgalterlar'

    def __str__(self):
        return self.full_name


class ReminderTemplate(models.Model):
    """Eslatma shablonlari"""
    days_before = models.IntegerField(unique=True)
    message_text = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'reminder_templates'
        verbose_name = 'Eslatma shabloni'
        verbose_name_plural = 'Eslatma shablonlari'

    def __str__(self):
        return f"{self.days_before} kun oldin"