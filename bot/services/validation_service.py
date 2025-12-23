# bot/services/validation_service.py
from typing import Tuple, Optional
import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.webapp.settings')

import django

django.setup()

from webapp.admin_panel.models import Student


class ValidationService:
    """Ma'lumotlarni tekshirish xizmati"""

    @staticmethod
    def validate_student_data(data: dict) -> Tuple[bool, Optional[str]]:
        """
        Talaba ma'lumotlarini to'liq tekshirish
        Returns: (is_valid, error_message)
        """
        # Student ID
        if not data.get('student_id') or len(data['student_id']) < 3:
            return False, "Talaba ID kamida 3 ta belgidan iborat bo'lishi kerak"

        # Ism
        if not data.get('first_name') or len(data['first_name']) < 2:
            return False, "Ism kamida 2 ta belgidan iborat bo'lishi kerak"

        # Familiya
        if not data.get('last_name') or len(data['last_name']) < 2:
            return False, "Familiya kamida 2 ta belgidan iborat bo'lishi kerak"

        # Otasining ismi
        if not data.get('patronymic') or len(data['patronymic']) < 2:
            return False, "Otasining ismi kamida 2 ta belgidan iborat bo'lishi kerak"

        # Pasport
        passport = f"{data.get('passport_series', '')}{data.get('passport_number', '')}"
        if not ValidationService.validate_passport_format(passport):
            return False, "Pasport noto'g'ri formatda (masalan: AA1234567)"

        # JSHSHIR
        if not ValidationService.validate_jshshir_format(data.get('jshshir', '')):
            return False, "JSHSHIR 14 ta raqamdan iborat bo'lishi kerak"

        # Telefon
        if not ValidationService.validate_phone_format(data.get('phone', '')):
            return False, "Telefon raqam noto'g'ri formatda (+998XXXXXXXXX)"

        return True, None

    @staticmethod
    def validate_passport_format(passport: str) -> bool:
        """Pasport formatini tekshirish"""
        pattern = r'^[A-Z]{2}\d{7}$'
        return bool(re.match(pattern, passport.upper().replace(' ', '')))

    @staticmethod
    def validate_jshshir_format(jshshir: str) -> bool:
        """JSHSHIR formatini tekshirish"""
        return jshshir.isdigit() and len(jshshir) == 14

    @staticmethod
    def validate_phone_format(phone: str) -> bool:
        """Telefon raqam formatini tekshirish"""
        pattern = r'^\+998\d{9}$'
        clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        return bool(re.match(pattern, clean_phone))

    @staticmethod
    async def check_student_id_exists(student_id: str) -> bool:
        """Talaba ID mavjudligini tekshirish"""
        return await Student.objects.filter(student_id=student_id).aexists()

    @staticmethod
    async def check_jshshir_exists(jshshir: str) -> bool:
        """JSHSHIR mavjudligini tekshirish"""
        return await Student.objects.filter(jshshir=jshshir).aexists()

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Kiritilgan ma'lumotni tozalash"""
        # HTML teglarni olib tashlash
        text = re.sub(r'<[^>]+>', '', text)
        # Ortiqcha bo'sh joylarni olib tashlash
        text = ' '.join(text.split())
        return text.strip()

    @staticmethod
    def format_phone_number(phone: str) -> str:
        """Telefon raqamni formatlash"""
        # Faqat raqamlarni qoldirish
        digits = re.sub(r'\D', '', phone)

        # +998 bilan boshlash
        if digits.startswith('998'):
            return f'+{digits}'
        elif len(digits) == 9:
            return f'+998{digits}'

        return phone

    @staticmethod
    def parse_passport(passport: str) -> Tuple[Optional[str], Optional[str]]:
        """Pasportni seriya va raqamga ajratish"""
        passport = passport.upper().replace(' ', '')
        if ValidationService.validate_passport_format(passport):
            return passport[:2], passport[2:]
        return None, None

    @staticmethod
    def validate_file_type(mime_type: str) -> bool:
        """Fayl turini tekshirish"""
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        return mime_type in allowed_types

    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
        """Fayl hajmini tekshirish"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes