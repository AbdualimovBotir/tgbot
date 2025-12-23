# bot/handlers/accountant.py
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

from webapp.admin_panel.models import User, AnonymousMessage, AccountingStaff
from bot.keyboards.admin_kb import main_admin_menu

router = Router()


class ReplyToAnonymous(StatesGroup):
    """Anonim xabarga javob berish"""
    waiting_for_reply = State()


@router.message(F.text == "💬 Buxgalteriya")
async def show_accounting_info(message: Message):
    """Buxgalteriya ma'lumotlarini ko'rsatish"""
    staff_list = AccountingStaff.objects.filter(is_active=True).select_related('user')

    text = "📊 <b>BUXGALTERIYA BO'LIMI</b>\n\n"

    has_staff = False
    async for staff in staff_list:
        has_staff = True
        text += f"👤 <b>{staff.full_name}</b>\n"
        text += f"   📋 Lavozim: {staff.position}\n"
        text += f"   🕐 Ish vaqti: {staff.working_hours}\n\n"

    if not has_staff:
        text += "Ma'lumot topilmadi.\n\n"

    text += "💬 <b>Anonim savol yuborish</b>\n"
    text += "Savol yoki murojaatingizni yozing, biz javob beramiz.\n"
    text += "Sizning ma'lumotlaringiz maxfiy saqlanadi."

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📨 Anonim xabarlar")
async def show_anonymous_messages(message: Message):
    """Anonim xabarlar ro'yxati (buxgalterlar uchun)"""
    telegram_id = message.from_user.id

    try:
        user = await User.objects.aget(telegram_id=telegram_id)
        if user.role not in ['admin', 'accountant']:
            await message.answer("❌ Bu bo'lim faqat buxgalteriya xodimlari uchun!")
            return

        # Javoblanmagan xabarlar
        unanswered = AnonymousMessage.objects.filter(is_replied=False).order_by('-created_at')

        text = "📨 <b>ANONIM XABARLAR</b>\n\n"
        text += "⏳ <b>Javoblanmagan xabarlar:</b>\n\n"

        count = 0
        async for msg in unanswered:
            count += 1
            text += f"{count}. ID: {msg.id}\n"
            text += f"   📅 {msg.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            text += f"   💬 {msg.message_text[:50]}...\n"
            text += f"   🔗 /reply_{msg.id}\n\n"

        if count == 0:
            text += "Javoblanmagan xabarlar yo'q.\n\n"

        # Javoblangan xabarlar
        answered = AnonymousMessage.objects.filter(is_replied=True).order_by('-replied_at')[:5]

        text += "\n✅ <b>Oxirgi javoblangan:</b>\n\n"

        count = 0
        async for msg in answered:
            count += 1
            text += f"{count}. ID: {msg.id}\n"
            text += f"   📅 {msg.replied_at.strftime('%d.%m.%Y %H:%M')}\n"
            text += f"   👤 {msg.replied_by.get_full_name() if msg.replied_by else 'Noma\'lum'}\n\n"

        await message.answer(text, parse_mode="HTML")

    except User.DoesNotExist:
        await message.answer("❌ Sizning ma'lumotlaringiz topilmadi!")


@router.message(F.text.startswith("/reply_"))
async def start_reply_to_anonymous(message: Message, state: FSMContext):
    """Anonim xabarga javob berishni boshlash"""
    telegram_id = message.from_user.id

    try:
        user = await User.objects.aget(telegram_id=telegram_id)
        if user.role not in ['admin', 'accountant']:
            await message.answer("❌ Ruxsat yo'q!")
            return

        # Message ID ni olish
        msg_id = int(message.text.replace("/reply_", ""))

        # Xabarni topish
        anon_msg = await AnonymousMessage.objects.aget(id=msg_id)

        if anon_msg.is_replied:
            await message.answer(
                f"ℹ️ Bu xabarga allaqachon javob berilgan.\n\n"
                f"Javob: {anon_msg.reply_text}"
            )
            return

        # State ga saqlash
        await state.update_data(
            message_id=msg_id,
            sender_telegram_id=anon_msg.sender_telegram_id
        )

        await message.answer(
            f"📨 <b>Anonim xabar:</b>\n\n"
            f"{anon_msg.message_text}\n\n"
            f"📝 Javobingizni yozing:",
            parse_mode="HTML"
        )
        await state.set_state(ReplyToAnonymous.waiting_for_reply)

    except (User.DoesNotExist, AnonymousMessage.DoesNotExist):
        await message.answer("❌ Xabar topilmadi!")
    except ValueError:
        await message.answer("❌ Noto'g'ri format!")


@router.message(ReplyToAnonymous.waiting_for_reply)
async def process_reply_to_anonymous(message: Message, state: FSMContext):
    """Anonim xabarga javobni qayta ishlash"""
    data = await state.get_data()
    reply_text = message.text

    try:
        user = await User.objects.aget(telegram_id=message.from_user.id)
        anon_msg = await AnonymousMessage.objects.aget(id=data['message_id'])

        # Javobni saqlash
        anon_msg.reply_text = reply_text
        anon_msg.replied_by = user
        anon_msg.replied_at = datetime.now()
        anon_msg.is_replied = True
        await anon_msg.asave()

        # Yuboruvchiga javobni yuborish
        try:
            await message.bot.send_message(
                chat_id=data['sender_telegram_id'],
                text=f"📨 <b>BUXGALTERIYADAN JAVOB</b>\n\n"
                     f"Sizning savolingiz:\n{anon_msg.message_text}\n\n"
                     f"Javob:\n{reply_text}",
                parse_mode="HTML"
            )

            await message.answer(
                "✅ Javob muvaffaqiyatli yuborildi!",
                reply_markup=main_admin_menu()
            )
        except Exception as e:
            await message.answer(f"⚠️ Javob saqlandi, lekin yuboruvchiga yuborib bo'lmadi: {str(e)}")

        await state.clear()

    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
        await state.clear()


# Talabalar tomonidan anonim xabar yuborish
@router.message(F.text, F.chat.type == "private")
async def handle_anonymous_question(message: Message, state: FSMContext):
    """Oddiy xabarlarni anonim savol sifatida qabul qilish"""
    # Faqat "Buxgalteriya" bo'limidan keyin yozilgan xabarlar
    current_state = await state.get_state()

    # Agar boshqa state bo'lmasa va xabar oddiy matn bo'lsa
    if current_state is None and message.text and not message.text.startswith('/'):
        # Buyruqlar va menu tugmalari emas
        menu_buttons = [
            "📤 Chek yuborish", "📊 To'lovlar tarixi", "📅 To'lov jadvali",
            "💬 Buxgalteriya", "❓ FAQ", "👨‍🎓 Talabalar", "👥 Guruhlar",
            "📅 To'lov jadvali", "📊 Statistika", "✉️ Eslatma shablonlari",
            "📋 Cheklar", "⚙️ Sozlamalar", "📨 Anonim xabarlar"
        ]

        if message.text not in menu_buttons:
            # Anonim xabar sifatida saqlash
            try:
                user = await User.objects.filter(telegram_id=message.from_user.id).afirst()

                # Faqat talabalar uchun
                if not user or user.role != 'student':
                    return

                await AnonymousMessage.objects.acreate(
                    sender_telegram_id=message.from_user.id,
                    message_text=message.text
                )

                await message.answer(
                    "✅ Sizning xabaringiz buxgalteriyaga yuborildi.\n"
                    "Javob tez orada beriladi. Barcha ma'lumotlar maxfiy saqlanadi.",
                    reply_markup=
                from bot.keyboards.student_kb import main_student_menu
                )

                # Buxgalterlarga xabar berish
                accountants = User.objects.filter(role='accountant', telegram_id__isnull=False)
                async for acc in accountants:
                    try:
                        await message.bot.send_message(
                            chat_id=acc.telegram_id,
                            text=f"📨 <b>YANGI ANONIM XABAR</b>\n\n"
                                 f"💬 {message.text}\n\n"
                                 f"Javob berish uchun: /reply_{await AnonymousMessage.objects.filter(sender_telegram_id=message.from_user.id).alast().id}",
                            parse_mode="HTML"
                        )
                    except Exception:
                        pass

            except Exception as e:
                print(f"Anonim xabar saqlashda xatolik: {e}")