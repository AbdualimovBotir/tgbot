# bot/handlers/student.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.webapp.settings')

import django

django.setup()

from webapp.admin_panel.models import User, Student, PaymentSchedule, Receipt
from bot.keyboards.student_kb import (
    payment_stages_keyboard, confirmation_keyboard,
    back_to_menu_keyboard, main_student_menu
)
from bot.utils.validators import (
    validate_passport, validate_jshshir,
    validate_phone, format_phone, parse_passport
)

router = Router()


class ReceiptSubmission(StatesGroup):
    """Chek yuborish holatlari"""
    waiting_for_student_id = State()
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_patronymic = State()
    waiting_for_passport = State()
    waiting_for_jshshir = State()
    waiting_for_phone = State()
    waiting_for_stage = State()
    waiting_for_file = State()
    confirmation = State()


@router.message(F.text == "📤 Chek yuborish")
async def start_receipt_submission(message: Message, state: FSMContext):
    """Chek yuborish jarayonini boshlash"""
    telegram_id = message.from_user.id

    try:
        user = await User.objects.aget(telegram_id=telegram_id)
        if user.role != 'student':
            await message.answer("Bu funksiya faqat talabalar uchun!")
            return

        # Talaba ma'lumotlarini olish
        try:
            student = await Student.objects.aget(user=user)
            # Agar talaba ma'lumotlari bor bo'lsa, to'g'ridan-to'g'ri bosqichni tanlashga o'tkazamiz
            await state.update_data(
                student_id=student.student_id,
                first_name=student.first_name,
                last_name=student.last_name,
                patronymic=student.patronymic,
                passport_series=student.passport_series,
                passport_number=student.passport_number,
                jshshir=student.jshshir,
                phone=student.phone,
                existing_student=True
            )

            await message.answer(
                f"📋 Sizning ma'lumotlaringiz:\n\n"
                f"👤 F.I.O: {student.full_name}\n"
                f"🆔 Talaba ID: {student.student_id}\n"
                f"📱 Telefon: {student.phone}\n\n"
                f"To'lov bosqichini tanlang:",
                reply_markup=payment_stages_keyboard()
            )
            await state.set_state(ReceiptSubmission.waiting_for_stage)

        except Student.DoesNotExist:
            # Yangi talaba - barcha ma'lumotlarni so'raymiz
            await message.answer(
                "📝 Chek yuborish uchun ma'lumotlaringizni kiriting.\n\n"
                "🆔 Talaba ID raqamingizni kiriting:"
            )
            await state.set_state(ReceiptSubmission.waiting_for_student_id)

    except User.DoesNotExist:
        await message.answer("Avval /start buyrug'ini yuboring!")


@router.message(ReceiptSubmission.waiting_for_student_id)
async def process_student_id(message: Message, state: FSMContext):
    """Talaba ID ni qabul qilish"""
    student_id = message.text.strip()

    if len(student_id) < 3:
        await message.answer("❌ Talaba ID kamida 3 ta belgidan iborat bo'lishi kerak!\n\nQaytadan kiriting:")
        return

    await state.update_data(student_id=student_id)
    await message.answer("✅ Talaba ID qabul qilindi.\n\n📝 Ismingizni kiriting:")
    await state.set_state(ReceiptSubmission.waiting_for_first_name)


@router.message(ReceiptSubmission.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    """Ismni qabul qilish"""
    first_name = message.text.strip()

    if len(first_name) < 2:
        await message.answer("❌ Ism kamida 2 ta belgidan iborat bo'lishi kerak!\n\nQaytadan kiriting:")
        return

    await state.update_data(first_name=first_name)
    await message.answer("✅ Ism qabul qilindi.\n\n📝 Familiyangizni kiriting:")
    await state.set_state(ReceiptSubmission.waiting_for_last_name)


@router.message(ReceiptSubmission.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    """Familiyani qabul qilish"""
    last_name = message.text.strip()

    if len(last_name) < 2:
        await message.answer("❌ Familiya kamida 2 ta belgidan iborat bo'lishi kerak!\n\nQaytadan kiriting:")
        return

    await state.update_data(last_name=last_name)
    await message.answer("✅ Familiya qabul qilindi.\n\n📝 Otangizning ismini kiriting:")
    await state.set_state(ReceiptSubmission.waiting_for_patronymic)


@router.message(ReceiptSubmission.waiting_for_patronymic)
async def process_patronymic(message: Message, state: FSMContext):
    """Otasining ismini qabul qilish"""
    patronymic = message.text.strip()

    if len(patronymic) < 2:
        await message.answer("❌ Otangizning ismi kamida 2 ta belgidan iborat bo'lishi kerak!\n\nQaytadan kiriting:")
        return

    await state.update_data(patronymic=patronymic)
    await message.answer(
        "✅ Otangizning ismi qabul qilindi.\n\n"
        "📄 Pasport seriya va raqamingizni kiriting\n"
        "Misol: AA1234567"
    )
    await state.set_state(ReceiptSubmission.waiting_for_passport)


@router.message(ReceiptSubmission.waiting_for_passport)
async def process_passport(message: Message, state: FSMContext):
    """Pasport ma'lumotlarini qabul qilish"""
    passport = message.text.strip().upper().replace(" ", "")

    if not validate_passport(passport):
        await message.answer(
            "❌ Pasport noto'g'ri formatda!\n\n"
            "To'g'ri format: AA1234567\n"
            "Qaytadan kiriting:"
        )
        return

    series, number = parse_passport(passport)
    await state.update_data(passport_series=series, passport_number=number)
    await message.answer(
        "✅ Pasport ma'lumotlari qabul qilindi.\n\n"
        "🔢 JSHSHIR raqamingizni kiriting (14 raqam):"
    )
    await state.set_state(ReceiptSubmission.waiting_for_jshshir)


@router.message(ReceiptSubmission.waiting_for_jshshir)
async def process_jshshir(message: Message, state: FSMContext):
    """JSHSHIR ni qabul qilish"""
    jshshir = message.text.strip()

    if not validate_jshshir(jshshir):
        await message.answer(
            "❌ JSHSHIR noto'g'ri formatda!\n\n"
            "JSHSHIR 14 ta raqamdan iborat bo'lishi kerak.\n"
            "Qaytadan kiriting:"
        )
        return

    await state.update_data(jshshir=jshshir)
    await message.answer(
        "✅ JSHSHIR qabul qilindi.\n\n"
        "📱 Telefon raqamingizni kiriting\n"
        "Misol: +998901234567"
    )
    await state.set_state(ReceiptSubmission.waiting_for_phone)


@router.message(ReceiptSubmission.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Telefon raqamni qabul qilish"""
    phone = message.text.strip()

    formatted_phone = format_phone(phone)
    if not validate_phone(formatted_phone):
        await message.answer(
            "❌ Telefon raqam noto'g'ri formatda!\n\n"
            "To'g'ri format: +998901234567\n"
            "Qaytadan kiriting:"
        )
        return

    await state.update_data(phone=formatted_phone)
    await message.answer(
        "✅ Telefon raqam qabul qilindi.\n\n"
        "📊 To'lov bosqichini tanlang:",
        reply_markup=payment_stages_keyboard()
    )
    await state.set_state(ReceiptSubmission.waiting_for_stage)


@router.callback_query(F.data.startswith("stage_"), ReceiptSubmission.waiting_for_stage)
async def process_payment_stage(callback: CallbackQuery, state: FSMContext):
    """To'lov bosqichini tanlash"""
    stage = callback.data.replace("stage_", "")

    # To'lov jadvalini tekshirish
    try:
        schedule = await PaymentSchedule.objects.filter(
            stage=stage,
            is_active=True
        ).afirst()

        if not schedule:
            await callback.answer("Bu bosqich uchun to'lov jadvali topilmadi!", show_alert=True)
            return

        await state.update_data(stage=stage, schedule_id=schedule.id)
        await callback.message.edit_text(
            f"✅ To'lov bosqichi: {stage}\n\n"
            f"📎 Endi to'lov chekingizni yuboring (rasm yoki PDF fayl)"
        )
        await state.set_state(ReceiptSubmission.waiting_for_file)
        await callback.answer()

    except Exception as e:
        await callback.answer(f"Xatolik: {str(e)}", show_alert=True)


@router.callback_query(F.data == "cancel")
async def cancel_submission(callback: CallbackQuery, state: FSMContext):
    """Jarayonni bekor qilish"""
    await state.clear()
    await callback.message.edit_text("❌ Jarayon bekor qilindi.")
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=main_student_menu()
    )
    await callback.answer()

    # bot/handlers/student.py (davomi)
    # Yuqoridagi kodga qo'shib yozing

    @router.message(ReceiptSubmission.waiting_for_file, F.photo | F.document)
    async def process_receipt_file(message: Message, state: FSMContext):
        """Chek faylini qabul qilish"""
        file_id = None

        if message.photo:
            file_id = message.photo[-1].file_id
        elif message.document:
            if message.document.mime_type not in ['image/jpeg', 'image/png', 'application/pdf']:
                await message.answer(
                    "❌ Faqat rasm (JPG, PNG) yoki PDF fayl yuborishingiz mumkin!\n\n"
                    "Qaytadan yuboring:"
                )
                return
            file_id = message.document.file_id

        if not file_id:
            await message.answer("❌ Fayl topilmadi! Qaytadan yuboring:")
            return

        await state.update_data(file_id=file_id)

        # Ma'lumotlarni olish
        data = await state.get_data()

        # Tasdiqlash uchun ko'rsatish
        confirmation_text = f"""
    📋 <b>Ma'lumotlarni tekshiring:</b>

    🆔 Talaba ID: {data['student_id']}
    👤 F.I.O: {data['last_name']} {data['first_name']} {data['patronymic']}
    📄 Pasport: {data['passport_series']}{data['passport_number']}
    🔢 JSHSHIR: {data['jshshir']}
    📱 Telefon: {data['phone']}
    📊 To'lov bosqichi: {data['stage']}
    ✅ Chek: Yuklandi

    Barcha ma'lumotlar to'g'rimi?
    """

        await message.answer(
            confirmation_text,
            reply_markup=confirmation_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(ReceiptSubmission.confirmation)

    @router.callback_query(F.data == "confirm_receipt", ReceiptSubmission.confirmation)
    async def confirm_receipt(callback: CallbackQuery, state: FSMContext):
        """Chekni tasdiqlash va saqlash"""
        data = await state.get_data()
        telegram_id = callback.from_user.id

        try:
            # Foydalanuvchini olish yoki yaratish
            user, created = await User.objects.aget_or_create(
                telegram_id=telegram_id,
                defaults={
                    'username': callback.from_user.username or f'user_{telegram_id}',
                    'role': 'student'
                }
            )

            # Talabani olish yoki yaratish
            student, created = await Student.objects.aget_or_create(
                student_id=data['student_id'],
                defaults={
                    'user': user,
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'patronymic': data['patronymic'],
                    'passport_series': data['passport_series'],
                    'passport_number': data['passport_number'],
                    'jshshir': data['jshshir'],
                    'phone': data['phone']
                }
            )

            # To'lov jadvalini olish
            schedule = await PaymentSchedule.objects.aget(id=data['schedule_id'])

            # Dublikat tekshirish
            existing_receipt = await Receipt.objects.filter(
                student=student,
                payment_schedule=schedule
            ).afirst()

            if existing_receipt:
                await callback.message.edit_text(
                    "⚠️ Siz bu to'lov bosqichi uchun allaqachon chek yuborgan ekansiz!\n\n"
                    f"Status: {existing_receipt.get_status_display()}"
                )
                await state.clear()
                await callback.answer()
                return

            # Chekni saqlash
            receipt = await Receipt.objects.acreate(
                student=student,
                payment_schedule=schedule,
                file_id=data['file_id'],
                status='pending'
            )

            await callback.message.edit_text(
                "✅ Chek muvaffaqiyatli yuborildi!\n\n"
                "📨 Sizning chekingiz admin va buxgalteriya bo'limiga yuborildi.\n"
                "⏳ Ko'rib chiqilishi kutilmoqda..."
            )

            # Admin va buxgalterlarga yuborish
            await send_receipt_to_admins(callback.bot, receipt, student, schedule, data['file_id'])

            await state.clear()
            await callback.answer("✅ Muvaffaqiyatli!")

            # Asosiy menyuga qaytarish
            await callback.message.answer(
                "Asosiy menyu:",
                reply_markup=main_student_menu()
            )

        except Exception as e:
            await callback.message.edit_text(f"❌ Xatolik yuz berdi: {str(e)}")
            await state.clear()
            await callback.answer()

    @router.callback_query(F.data == "cancel_receipt", ReceiptSubmission.confirmation)
    async def cancel_receipt_confirmation(callback: CallbackQuery, state: FSMContext):
        """Chekni bekor qilish"""
        await state.clear()
        await callback.message.edit_text("❌ Chek yuborish bekor qilindi.")
        await callback.message.answer(
            "Asosiy menyu:",
            reply_markup=main_student_menu()
        )
        await callback.answer()

    async def send_receipt_to_admins(bot, receipt, student, schedule, file_id):
        """Chekni adminlar va buxgalterlarga yuborish"""
        from webapp.admin_panel.models import User, AccountingStaff
        from bot.keyboards.admin_kb import receipt_action_keyboard

        message_text = f"""
    📨 <b>YANGI CHEK KELDI</b>

    🆔 Talaba ID: {student.student_id}
    👤 F.I.O: {student.full_name}
    📄 Pasport: {student.passport_full}
    🔢 JSHSHIR: {student.jshshir}
    📱 Telefon: {student.phone}
    👥 Guruh: {student.group.name if student.group else 'Biriktirilmagan'}

    📊 To'lov bosqichi: {schedule.stage}
    📅 To'lov muddati: {schedule.due_date.strftime('%d.%m.%Y')}
    💰 Summa: {schedule.amount} so'm

    ⏰ Yuborilgan vaqt: {receipt.submitted_at.strftime('%d.%m.%Y %H:%M')}
    """

        # Adminlarga yuborish
        admins = User.objects.filter(role__in=['admin', 'accountant'], telegram_id__isnull=False)
        async for admin in admins:
            try:
                await bot.send_photo(
                    chat_id=admin.telegram_id,
                    photo=file_id,
                    caption=message_text,
                    reply_markup=receipt_action_keyboard(receipt.id),
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Admin {admin.telegram_id} ga yuborishda xatolik: {e}")

    @router.message(F.text == "📊 To'lovlar tarixi")
    async def show_payment_history(message: Message):
        """To'lovlar tarixini ko'rsatish"""
        telegram_id = message.from_user.id

        try:
            user = await User.objects.aget(telegram_id=telegram_id)
            student = await Student.objects.aget(user=user)

            receipts = Receipt.objects.filter(student=student).select_related('payment_schedule').order_by(
                '-submitted_at')

            history_text = "📊 <b>To'lovlar tarixi</b>\n\n"

            has_receipts = False
            async for receipt in receipts:
                has_receipts = True
                status_emoji = {
                    'pending': '⏳',
                    'approved': '✅',
                    'rejected': '❌'
                }.get(receipt.status, '❓')

                history_text += f"{status_emoji} <b>{receipt.payment_schedule.stage}</b>\n"
                history_text += f"   Sana: {receipt.submitted_at.strftime('%d.%m.%Y')}\n"
                history_text += f"   Status: {receipt.get_status_display()}\n"
                if receipt.notes:
                    history_text += f"   Izoh: {receipt.notes}\n"
                history_text += "\n"

            if not has_receipts:
                history_text += "Hozircha hech qanday to'lov cheki yuborilmagan."

            await message.answer(history_text, parse_mode="HTML")

        except (User.DoesNotExist, Student.DoesNotExist):
            await message.answer("❌ Sizning ma'lumotlaringiz topilmadi!")

    @router.message(F.text == "📅 To'lov jadvali")
    async def show_payment_schedule(message: Message):
        """To'lov jadvalini ko'rsatish"""
        schedules = PaymentSchedule.objects.filter(is_active=True).order_by('due_date')

        schedule_text = "📅 <b>To'lov jadvali</b>\n\n"

        has_schedules = False
        async for schedule in schedules:
            has_schedules = True
            schedule_text += f"📌 <b>{schedule.stage}</b>\n"
            schedule_text += f"   📅 Muddat: {schedule.due_date.strftime('%d.%m.%Y')}\n"
            schedule_text += f"   💰 Summa: {schedule.amount} so'm\n\n"

        if not has_schedules:
            schedule_text += "To'lov jadvali hali e'lon qilinmagan."

        await message.answer(schedule_text, parse_mode="HTML")

    # FAQ callbacklari
    @router.callback_query(F.data == "faq_payment_methods")
    async def faq_payment_methods(callback: CallbackQuery):
        """To'lov usullari"""
        text = """
    💳 <b>To'lov usullari</b>

    1️⃣ <b>Bank orqali</b>
       • Payme
       • Click
       • Uzum

    2️⃣ <b>Bank kartasi</b>
       • Humo
       • Uzcard
       • Visa/MasterCard

    3️⃣ <b>Naqd pul</b>
       • Institut kassasida

    ⚠️ To'lovdan keyin chekni botga yuborishni unutmang!
    """
        await callback.message.edit_text(text, reply_markup=back_to_menu_keyboard(), parse_mode="HTML")
        await callback.answer()

    @router.callback_query(F.data == "faq_requisites")
    async def faq_requisites(callback: CallbackQuery):
        """Bank rekvizitlari"""
        text = """
    🏦 <b>Bank rekvizitlari</b>

    🏛 Bank: Xalq banki
    🔢 Hisob raqam: 20208000000000000001
    🏢 Tashkilot: ISFT Institut
    📝 INN: 123456789
    📮 MFO: 00014

    💬 Izoh: Shartnoma raqamingizni ko'rsating
    """
        await callback.message.edit_text(text, reply_markup=back_to_menu_keyboard(), parse_mode="HTML")
        await callback.answer()

    @router.callback_query(F.data == "faq_deadlines")
    async def faq_deadlines(callback: CallbackQuery):
        """To'lov muddatlari"""
        text = """
    📅 <b>To'lov muddatlari</b>

    Yillik to'lov 4 qismga bo'lingan:

    1️⃣ Birinchi to'lov (1/4)
    2️⃣ Ikkinchi to'lov (2/4)
    3️⃣ Uchinchi to'lov (3/4)
    4️⃣ To'rtinchi to'lov (4/4)

    Aniq sanalar "📅 To'lov jadvali" bo'limida ko'rsatilgan.

    ⏰ Bot sizga vaqtida eslatma yuboradi!
    """
        await callback.message.edit_text(text, reply_markup=back_to_menu_keyboard(), parse_mode="HTML")
        await callback.answer()

    @router.callback_query(F.data == "faq_late_rules")
    async def faq_late_rules(callback: CallbackQuery):
        """Kechikish qoidalari"""
        text = """
    ⏰ <b>Kechikish qoidalari</b>

    ⚠️ To'lovni kechiktirish:
    • 7 kun gacha - ogohlantirish
    • 7-14 kun - jarima 2%
    • 14-30 kun - jarima 5%
    • 30 kundan ortiq - maxsus komissiya

    📞 Qiyin vaziyatda:
    Buxgalteriya bilan bog'laning va to'lov muddatini uzaytirish haqida gaplashing.

    💡 Maslahat: To'lovni muddatidan oldin bajaring!
    """
        await callback.message.edit_text(text, reply_markup=back_to_menu_keyboard(), parse_mode="HTML")
        await callback.answer()

    @router.callback_query(F.data == "back_to_menu")
    async def back_to_main_menu(callback: CallbackQuery):
        """Asosiy menyuga qaytish"""
        await callback.message.delete()
        await callback.message.answer(
            "Asosiy menyu:",
            reply_markup=main_student_menu()
        )
        await callback.answer()