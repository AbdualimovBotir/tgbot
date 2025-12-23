# webapp/admin_panel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import (
    Student, Group, PaymentSchedule, Receipt,
    PaymentReminder, User
)


@login_required
def dashboard(request):
    """Dashboard - asosiy sahifa"""
    # Statistika
    total_students = Student.objects.filter(is_active=True).count()
    total_groups = Group.objects.filter(is_active=True).count()

    pending_receipts = Receipt.objects.filter(status='pending').count()
    approved_receipts = Receipt.objects.filter(status='approved').count()
    rejected_receipts = Receipt.objects.filter(status='rejected').count()

    # Yaqin kunlardagi to'lovlar
    today = datetime.now().date()
    upcoming_payments = PaymentSchedule.objects.filter(
        due_date__gte=today,
        due_date__lte=today + timedelta(days=30),
        is_active=True
    ).order_by('due_date')

    # Oxirgi cheklar
    recent_receipts = Receipt.objects.select_related(
        'student', 'payment_schedule'
    ).order_by('-submitted_at')[:10]

    context = {
        'total_students': total_students,
        'total_groups': total_groups,
        'pending_receipts': pending_receipts,
        'approved_receipts': approved_receipts,
        'rejected_receipts': rejected_receipts,
        'upcoming_payments': upcoming_payments,
        'recent_receipts': recent_receipts,
    }

    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def students_list(request):
    """Talabalar ro'yxati"""
    students = Student.objects.select_related('group').order_by('last_name')

    # Qidiruv
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            Q(student_id__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(jshshir__icontains=search)
        )

    # Guruh bo'yicha filtr
    group_id = request.GET.get('group', '')
    if group_id:
        students = students.filter(group_id=group_id)

    groups = Group.objects.filter(is_active=True).order_by('name')

    context = {
        'students': students,
        'groups': groups,
        'search': search,
        'selected_group': group_id,
    }

    return render(request, 'admin_panel/students.html', context)


@login_required
def student_detail(request, student_id):
    """Talaba tafsilotlari"""
    student = get_object_or_404(
        Student.objects.select_related('group'),
        id=student_id
    )

    # Talabaning cheklari
    receipts = Receipt.objects.filter(
        student=student
    ).select_related('payment_schedule').order_by('-submitted_at')

    context = {
        'student': student,
        'receipts': receipts,
    }

    return render(request, 'admin_panel/student_detail.html', context)


@login_required
def groups_list(request):
    """Guruhlar ro'yxati"""
    groups = Group.objects.annotate(
        student_count=Count('students')
    ).order_by('name')

    context = {
        'groups': groups,
    }

    return render(request, 'admin_panel/groups.html', context)


@login_required
def payments_schedule(request):
    """To'lov jadvali"""
    schedules = PaymentSchedule.objects.order_by('-academic_year', 'stage')

    context = {
        'schedules': schedules,
    }

    return render(request, 'admin_panel/payments.html', context)


@login_required
def receipts_list(request):
    """Cheklar ro'yxati"""
    receipts = Receipt.objects.select_related(
        'student', 'payment_schedule', 'reviewed_by'
    ).order_by('-submitted_at')

    # Status bo'yicha filtr
    status = request.GET.get('status', '')
    if status:
        receipts = receipts.filter(status=status)

    # To'lov bosqichi bo'yicha filtr
    stage = request.GET.get('stage', '')
    if stage:
        receipts = receipts.filter(payment_schedule__stage=stage)

    context = {
        'receipts': receipts,
        'selected_status': status,
        'selected_stage': stage,
    }

    return render(request, 'admin_panel/receipts.html', context)


@login_required
def receipt_review(request, receipt_id):
    """Chekni ko'rib chiqish"""
    receipt = get_object_or_404(
        Receipt.objects.select_related('student', 'payment_schedule'),
        id=receipt_id
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        if action in ['approved', 'rejected']:
            receipt.status = action
            receipt.reviewed_by = request.user
            receipt.reviewed_at = datetime.now()
            receipt.notes = notes
            receipt.save()

            status_text = 'tasdiqlandi' if action == 'approved' else 'rad etildi'
            messages.success(request, f'Chek {status_text}!')

            return redirect('admin_panel:receipts_list')

    context = {
        'receipt': receipt,
    }

    return render(request, 'admin_panel/receipt_review.html', context)