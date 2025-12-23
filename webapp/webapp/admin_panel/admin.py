from django.contrib import admin

# Register your models here.
# webapp/admin_panel/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Student, Group, PaymentSchedule, Receipt,
    PaymentReminder, AnonymousMessage, AccountingStaff, ReminderTemplate
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'telegram_id', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'telegram_id', 'phone']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo\'shimcha ma\'lumotlar', {'fields': ('telegram_id', 'role', 'phone')}),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'group', 'phone', 'is_active']
    list_filter = ['group', 'is_active', 'created_at']
    search_fields = ['student_id', 'first_name', 'last_name', 'jshshir', 'passport_number']
    list_per_page = 50

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('user', 'student_id', 'group', 'is_active')
        }),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'patronymic')
        }),
        ('Hujjatlar', {
            'fields': ('passport_series', 'passport_number', 'jshshir')
        }),
        ('Aloqa', {
            'fields': ('phone',)
        }),
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'chat_title', 'telegram_chat_id', 'is_active', 'student_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'chat_title']

    def student_count(self, obj):
        return obj.students.count()

    student_count.short_description = 'Talabalar soni'


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ['academic_year', 'stage', 'due_date', 'amount', 'is_active']
    list_filter = ['academic_year', 'stage', 'is_active']
    search_fields = ['academic_year']
    ordering = ['-academic_year', 'stage']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['student', 'payment_schedule', 'status', 'submitted_at', 'reviewed_by']
    list_filter = ['status', 'submitted_at', 'payment_schedule__stage']
    search_fields = ['student__student_id', 'student__first_name', 'student__last_name']
    readonly_fields = ['submitted_at', 'reviewed_at']

    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('student', 'payment_schedule', 'status')
        }),
        ('Fayl', {
            'fields': ('file_id', 'file_path')
        }),
        ('Ko\'rib chiqish', {
            'fields': ('reviewed_by', 'reviewed_at', 'notes')
        }),
        ('Vaqt', {
            'fields': ('submitted_at',)
        }),
    )


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ['student', 'payment_schedule', 'days_before', 'is_sent', 'sent_at']
    list_filter = ['is_sent', 'days_before', 'payment_schedule']
    search_fields = ['student__student_id', 'student__first_name']
    readonly_fields = ['sent_at']


@admin.register(AnonymousMessage)
class AnonymousMessageAdmin(admin.ModelAdmin):
    list_display = ['sender_telegram_id', 'is_replied', 'created_at', 'replied_by']
    list_filter = ['is_replied', 'created_at']
    search_fields = ['message_text', 'reply_text']
    readonly_fields = ['created_at', 'replied_at']

    fieldsets = (
        ('Xabar', {
            'fields': ('sender_telegram_id', 'message_text')
        }),
        ('Javob', {
            'fields': ('is_replied', 'reply_text', 'replied_by', 'replied_at')
        }),
        ('Vaqt', {
            'fields': ('created_at',)
        }),
    )


@admin.register(AccountingStaff)
class AccountingStaffAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'working_hours', 'is_active']
    list_filter = ['is_active', 'position']
    search_fields = ['full_name', 'position']


@admin.register(ReminderTemplate)
class ReminderTemplateAdmin(admin.ModelAdmin):
    list_display = ['days_before', 'is_active']
    list_filter = ['is_active', 'days_before']
    ordering = ['-days_before']