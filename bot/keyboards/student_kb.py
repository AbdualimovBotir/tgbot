# bot/keyboards/student_kb.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_student_menu():
    """Talaba asosiy menyu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📤 Chek yuborish")],
            [KeyboardButton(text="📊 To'lovlar tarixi"), KeyboardButton(text="📅 To'lov jadvali")],
            [KeyboardButton(text="💬 Buxgalteriya"), KeyboardButton(text="❓ FAQ")],
        ],
        resize_keyboard=True
    )
    return keyboard

def payment_stages_keyboard():
    """To'lov bosqichlari"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1/4", callback_data="stage_1/4")],
            [InlineKeyboardButton(text="2/4", callback_data="stage_2/4")],
            [InlineKeyboardButton(text="3/4", callback_data="stage_3/4")],
            [InlineKeyboardButton(text="4/4", callback_data="stage_4/4")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel")]
        ]
    )
    return keyboard

def confirmation_keyboard():
    """Tasdiqlash klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ To'g'ri", callback_data="confirm_receipt"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_receipt")
            ]
        ]
    )
    return keyboard

def faq_keyboard():
    """FAQ klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 To'lov usullari", callback_data="faq_payment_methods")],
            [InlineKeyboardButton(text="🏦 Bank rekvizitlari", callback_data="faq_requisites")],
            [InlineKeyboardButton(text="📅 To'lov muddatlari", callback_data="faq_deadlines")],
            [InlineKeyboardButton(text="⏰ Kechikish qoidalari", callback_data="faq_late_rules")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
        ]
    )
    return keyboard

def back_to_menu_keyboard():
    """Menuga qaytish"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_menu")]
        ]
    )
    return keyboard