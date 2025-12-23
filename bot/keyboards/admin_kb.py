# bot/keyboards/admin_kb.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_admin_menu():
    """Admin asosiy menyu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👨‍🎓 Talabalar"), KeyboardButton(text="👥 Guruhlar")],
            [KeyboardButton(text="📅 To'lov jadvali"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="✉️ Eslatma shablonlari"), KeyboardButton(text="📋 Cheklar")],
            [KeyboardButton(text="⚙️ Sozlamalar")],
        ],
        resize_keyboard=True
    )
    return keyboard

def student_management_keyboard():
    """Talabalarni boshqarish"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Talaba qo'shish", callback_data="admin_add_student")],
            [InlineKeyboardButton(text="📋 Talabalar ro'yxati", callback_data="admin_list_students")],
            [InlineKeyboardButton(text="🔍 Talaba qidirish", callback_data="admin_search_student")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
        ]
    )
    return keyboard

def group_management_keyboard():
    """Guruhlarni boshqarish"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Guruh qo'shish", callback_data="admin_add_group")],
            [InlineKeyboardButton(text="📋 Guruhlar ro'yxati", callback_data="admin_list_groups")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
        ]
    )
    return keyboard

def payment_schedule_keyboard():
    """To'lov jadvali boshqaruvi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Jadval qo'shish", callback_data="admin_add_schedule")],
            [InlineKeyboardButton(text="📋 Jadvallar ro'yxati", callback_data="admin_list_schedules")],
            [InlineKeyboardButton(text="✏️ Jadval tahrirlash", callback_data="admin_edit_schedule")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
        ]
    )
    return keyboard

def receipt_action_keyboard(receipt_id: int):
    """Chek tasdiqlash/rad etish"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_receipt_{receipt_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_receipt_{receipt_id}")
            ],
            [InlineKeyboardButton(text="📝 Izoh qo'shish", callback_data=f"note_receipt_{receipt_id}")]
        ]
    )
    return keyboard