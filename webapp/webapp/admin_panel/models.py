from django.db import models

# Create your models here.
# webapp/admin_panel/models.py
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

    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'


class Student(models.Model):
    """Talaba modeli"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    student_id = models.CharField(max_length=50, unique=True, verbose_name='Talaba ID')
    first_name = models.CharField(max_length=100, verbose_name='Ism')
    last_name = models.CharField(max_length=100, verbose_name='Familiya')
    patronymic = models.CharField(max_length=100, verbose_name='Otasining ismi')
    passport_series = models.CharField(max_length=2, verbose_name='Pasport seriyasi')
    passport_number = models.CharField(max_length=7, verbose_name='Pasport raqami')
    jshshir = models.CharField(max_length=14, unique=True, verbose_name='JSHSHIR')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='students',
                              verbose_name='Guruh')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'
        verbose_name = 'Talaba'
        verbose_name_plural = 'Talabalar'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.student_id})"

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    @property
    def passport_full(self):
        return f"{self.passport_series}{self.passport_number}"


class Group(models.Model):
    """Guruh modeli"""
    name = models.CharField(max_length=100, verbose_name='Guruh nomi')
    telegram_chat_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name='Telegram Chat ID')
    chat_title = models.CharField(max_length=255, blank=True, verbose_name='Chat nomi')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'groups'
        verbose_name = 'Guruh'
        verbose_name_plural = 'Guruhlar'
        ordering = ['name']

    def __str__(self):
        return self.name


class PaymentSchedule(models.Model):
    """To'lov jadvali"""
    STAGE_CHOICES = [
        ('1/4', '1-to\'lov'),
        ('2/4', '2-to\'lov'),
        ('3/4', '3-to\'lov'),
        ('4/4', '4-to\'lov'),
    ]

    academic_year = models.CharField(max_length=20, verbose_name='O\'quv yili')
    stage = models.CharField(max_length=5, choices=STAGE_CHOICES, verbose_name='Bosqich')
    due_date = models.DateField(verbose_name='To\'lov sanasi')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Summa')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_schedules'
        verbose_name = 'To\'lov jadvali'
        verbose_name_plural = 'To\'lov jadvallari'
        unique_together = ['academic_year', 'stage']
        ordering = ['academic_year', 'stage']

    def __str__(self):
        return f"{self.academic_year} - {self.stage}"


class Receipt(models.Model):
    """To'lov cheki"""
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('approved', 'Tasdiqlangan'),
        ('rejected', 'Rad etilgan'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='receipts', verbose_name='Talaba')
    payment_schedule = models.ForeignKey(PaymentSchedule, on_delete=models.CASCADE, verbose_name='To\'lov jadvali')
    file_id = models.CharField(max_length=255, verbose_name='Fayl ID')
    file_path = models.CharField(max_length=500, blank=True, verbose_name='Fayl yo\'li')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Holat')
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Yuborilgan vaqt')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_receipts', verbose_name='Ko\'rib chiqdi')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Ko\'rilgan vaqt')
    notes = models.TextField(blank=True, verbose_name='Izohlar')

    class Meta:
        db_table = 'receipts'
        verbose_name = 'Chek'
        verbose_name_plural = 'Cheklar'
        unique_together = ['student', 'payment_schedule']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.student_id} - {self.payment_schedule.stage}"


class PaymentReminder(models.Model):
    """To'lov eslatmasi"""
    payment_schedule = models.ForeignKey(PaymentSchedule, on_delete=models.CASCADE, verbose_name='To\'lov jadvali')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Talaba')
    days_before = models.IntegerField(verbose_name='Necha kun oldin')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Yuborilgan vaqt')
    is_sent = models.BooleanField(default=False, verbose_name='Yuborildi')

    class Meta:
        db_table = 'payment_reminders'
        verbose_name = 'Eslatma'
        verbose_name_plural = 'Eslatmalar'
        unique_together = ['payment_schedule', 'student', 'days_before']


class AnonymousMessage(models.Model):
    """Anonim xabar"""
    sender_telegram_id = models.BigIntegerField(verbose_name='Yuboruvchi ID')
    message_text = models.TextField(verbose_name='Xabar matni')
    reply_text = models.TextField(blank=True, verbose_name='Javob matni')
    replied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Javob berdi')
    is_replied = models.BooleanField(default=False, verbose_name='Javob berildi')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')
    replied_at = models.DateTimeField(null=True, blank=True, verbose_name='Javob berilgan vaqt')

    class Meta:
        db_table = 'anonymous_messages'
        verbose_name = 'Anonim xabar'
        verbose_name_plural = 'Anonim xabarlar'
        ordering = ['-created_at']


class AccountingStaff(models.Model):
    """Buxgalteriya xodimlari"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Foydalanuvchi')
    full_name = models.CharField(max_length=200, verbose_name='To\'liq ismi')
    position = models.CharField(max_length=100, verbose_name='Lavozim')
    working_hours = models.CharField(max_length=100, verbose_name='Ish vaqti')
    is_active = models.BooleanField(default=True, verbose_name='Faol')

    class Meta:
        db_table = 'accounting_staff'
        verbose_name = 'Buxgalter'
        verbose_name_plural = 'Buxgalterlar'

    def __str__(self):
        return self.full_name


class ReminderTemplate(models.Model):
    """Eslatma shablonlari"""
    days_before = models.IntegerField(unique=True, verbose_name='Necha kun oldin')
    message_text = models.TextField(verbose_name='Xabar matni')
    is_active = models.BooleanField(default=True, verbose_name='Faol')

    class Meta:
        db_table = 'reminder_templates'
        verbose_name = 'Eslatma shabloni'
        verbose_name_plural = 'Eslatma shablonlari'
        ordering = ['-days_before']

    def __str__(self):
        return f"{self.days_before} kun oldin"