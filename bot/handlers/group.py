# bot/handlers/group.py
from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, ADMINISTRATOR
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.webapp.settings')

import django

django.setup()

from webapp.admin_panel.models import Group, User
from bot.config import ADMIN_IDS

router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> (ADMINISTRATOR | IS_MEMBER)
    )
)
async def bot_added_to_group(event: ChatMemberUpdated):
    """
    Bot guruhga qo'shilganda
    MUHIM: Bot faqat admin huquqlari bilan qo'shilishi kerak
    """
    chat = event.chat
    new_status = event.new_chat_member.status
    user_id = event.from_user.id

    # Admin ekanligini tekshirish
    if user_id not in ADMIN_IDS:
        try:
            # Adminlar ro'yxatidan tekshirish
            admin_exists = await User.objects.filter(
                telegram_id=user_id,
                role='admin'
            ).aexists()

            if not admin_exists:
                await event.bot.send_message(
                    chat_id=chat.id,
                    text="❌ Botni faqat institut adminlari qo'shishi mumkin!\n\n"
                         "Iltimos, admindan botni qo'shishni so'rang."
                )
                await event.bot.leave_chat(chat.id)
                return
        except Exception:
            await event.bot.send_message(
                chat_id=chat.id,
                text="❌ Botni faqat institut adminlari qo'shishi mumkin!"
            )
            await event.bot.leave_chat(chat.id)
            return

    # Bot admin huquqlariga ega ekanligini tekshirish
    if new_status != "administrator":
        await event.bot.send_message(
            chat_id=chat.id,
            text="⚠️ Bot to'g'ri ishlashi uchun ADMIN huquqlari kerak!\n\n"
                 "Iltimos:\n"
                 "1. Botni guruhdan chiqaring\n"
                 "2. Admin huquqlari bilan qayta qo'shing"
        )
        await event.bot.leave_chat(chat.id)
        return

    # Guruhni saqlash
    try:
        group, created = await Group.objects.aupdate_or_create(
            telegram_chat_id=chat.id,
            defaults={
                'chat_title': chat.title or 'Nomsiz guruh',
                'is_active': True
            }
        )

        welcome_message = f"""
👋 Assalomu alaykum!

✅ Bot guruhga muvaffaqiyatli qo'shildi!

📋 <b>Guruh ma'lumotlari:</b>
📌 Nom: {chat.title}
🆔 ID: <code>{chat.id}</code>

🔔 <b>Bot imkoniyatlari:</b>
• To'lov eslatmalari yuborish
• Talabalar bilan aloqa
• To'lov cheklari haqida xabarnoma

⚙️ Guruhni sozlash uchun admin panelga kiring.
"""

        await event.bot.send_message(
            chat_id=chat.id,
            text=welcome_message,
            parse_mode="HTML"
        )

        # Adminlarga xabar yuborish
        for admin_id in ADMIN_IDS:
            try:
                await event.bot.send_message(
                    chat_id=admin_id,
                    text=f"ℹ️ Bot yangi guruhga qo'shildi:\n\n"
                         f"📌 Guruh: {chat.title}\n"
                         f"🆔 ID: {chat.id}\n"
                         f"👤 Qo'shdi: {event.from_user.full_name}"
                )
            except Exception:
                pass

    except Exception as e:
        await event.bot.send_message(
            chat_id=chat.id,
            text=f"❌ Xatolik yuz berdi: {str(e)}"
        )


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=(ADMINISTRATOR | IS_MEMBER) >> IS_NOT_MEMBER
    )
)
async def bot_removed_from_group(event: ChatMemberUpdated):
    """Bot guruhdan chiqarilganda"""
    chat = event.chat

    try:
        # Guruhni nofaol qilish
        await Group.objects.filter(telegram_chat_id=chat.id).aupdate(is_active=False)

        # Adminlarga xabar yuborish
        for admin_id in ADMIN_IDS:
            try:
                await event.bot.send_message(
                    chat_id=admin_id,
                    text=f"⚠️ Bot guruhdan chiqarildi:\n\n"
                         f"📌 Guruh: {chat.title}\n"
                         f"🆔 ID: {chat.id}\n"
                         f"👤 Chiqardi: {event.from_user.full_name}"
                )
            except Exception:
                pass
    except Exception as e:
        print(f"Guruhni o'chirishda xatolik: {e}")


@router.message(F.chat.type.in_(["group", "supergroup"]))
async def handle_group_messages(message: Message):
    """Guruhdagi xabarlarga javob (minimal)"""
    # Bot faqat @mention yoki /commands ga javob beradi
    if message.text and message.text.startswith('/'):
        if message.text == '/status':
            try:
                group = await Group.objects.aget(telegram_chat_id=message.chat.id)
                student_count = await group.students.acount()

                await message.reply(
                    f"📊 <b>Guruh statistikasi</b>\n\n"
                    f"📌 Guruh: {group.name}\n"
                    f"👥 Talabalar: {student_count} ta\n"
                    f"✅ Status: {'Faol' if group.is_active else 'Nofaol'}",
                    parse_mode="HTML"
                )
            except Group.DoesNotExist:
                await message.reply("❌ Guruh ma'lumotlari topilmadi!")