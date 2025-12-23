# bot/keyboards/inline_kb.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_pagination_keyboard(
        page: int,
        total_pages: int,
        callback_prefix: str
) -> InlineKeyboardMarkup:
    """Sahifalash klaviaturasi"""
    buttons = []

    # Navigatsiya tugmalari
    nav_buttons = []

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"{callback_prefix}_page_{page - 1}")
        )

    nav_buttons.append(
        InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="current_page")
    )

    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"{callback_prefix}_page_{page + 1}")
        )

    buttons.append(nav_buttons)

    # Orqaga qaytish
    buttons.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_student_detail_keyboard(student_id: int) -> InlineKeyboardMarkup:
    """Talaba tafsilotlari klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 To'lovlar tarixi",
                    callback_data=f"student_payments_{student_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Tahrirlash",
                    callback_data=f"edit_student_{student_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="back_to_students_list"
                )
            ]
        ]
    )
    return keyboard


def create_receipt_status_keyboard(receipt_id: int) -> InlineKeyboardMarkup:
    """Chek holati klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"approve_receipt_{receipt_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish",
                    callback_data=f"reject_receipt_{receipt_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Izoh qo'shish",
                    callback_data=f"add_note_{receipt_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="back_to_receipts"
                )
            ]
        ]
    )
    return keyboard


def create_group_actions_keyboard(group_id: int) -> InlineKeyboardMarkup:
    """Guruh amaliyotlari klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Talabalar",
                    callback_data=f"group_students_{group_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Tahrirlash",
                    callback_data=f"edit_group_{group_id}"
                ),
                InlineKeyboardButton(
                    text="🗑 O'chirish",
                    callback_data=f"delete_group_{group_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="back_to_groups"
                )
            ]
        ]
    )
    return keyboard


def create_payment_schedule_actions_keyboard(schedule_id: int) -> InlineKeyboardMarkup:
    """To'lov jadvali amaliyotlari"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data=f"schedule_stats_{schedule_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Tahrirlash",
                    callback_data=f"edit_schedule_{schedule_id}"
                ),
                InlineKeyboardButton(
                    text="🗑 O'chirish",
                    callback_data=f"delete_schedule_{schedule_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="back_to_schedules"
                )
            ]
        ]
    )
    return keyboard


def create_yes_no_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Ha/Yo'q klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ha",
                    callback_data=f"confirm_{action}_{item_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Yo'q",
                    callback_data=f"cancel_{action}_{item_id}"
                )
            ]
        ]
    )
    return keyboard


def create_filter_keyboard(filter_type: str) -> InlineKeyboardMarkup:
    """Filtr klaviaturasi"""
    if filter_type == 'receipt_status':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="⏳ Kutilmoqda", callback_data="filter_pending")
                ],
                [
                    InlineKeyboardButton(text="✅ Tasdiqlangan", callback_data="filter_approved")
                ],
                [
                    InlineKeyboardButton(text="❌ Rad etilgan", callback_data="filter_rejected")
                ],
                [
                    InlineKeyboardButton(text="🔄 Barchasi", callback_data="filter_all")
                ],
                [
                    InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")
                ]
            ]
        )
    elif filter_type == 'payment_stage':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1/4", callback_data="filter_stage_1/4")
                ],
                [
                    InlineKeyboardButton(text="2/4", callback_data="filter_stage_2/4")
                ],
                [
                    InlineKeyboardButton(text="3/4", callback_data="filter_stage_3/4")
                ],
                [
                    InlineKeyboardButton(text="4/4", callback_data="filter_stage_4/4")
                ],
                [
                    InlineKeyboardButton(text="🔄 Barchasi", callback_data="filter_all")
                ],
                [
                    InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")
                ]
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")
                ]
            ]
        )

    return keyboard