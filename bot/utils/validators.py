# bot/utils/validators.py
import re

def validate_passport(passport: str) -> bool:
    """Passport seriya va raqamini tekshirish (AA1234567)"""
    pattern = r'^[A-Z]{2}\d{7}$'
    return bool(re.match(pattern, passport.upper()))

def validate_jshshir(jshshir: str) -> bool:
    """JSHSHIR tekshirish (14 ta raqam)"""
    return jshshir.isdigit() and len(jshshir) == 14

def validate_phone(phone: str) -> bool:
    """Telefon raqam tekshirish (+998xxxxxxxxx)"""
    pattern = r'^\+998\d{9}$'
    clean_phone = phone.replace(' ', '').replace('-', '')
    return bool(re.match(pattern, clean_phone))

def format_phone(phone: str) -> str:
    """Telefon raqamni formatlash"""
    clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if not clean_phone.startswith('+'):
        if clean_phone.startswith('998'):
            clean_phone = '+' + clean_phone
        else:
            clean_phone = '+998' + clean_phone
    return clean_phone

def validate_student_id(student_id: str) -> bool:
    """Talaba ID tekshirish"""
    return len(student_id) >= 3 and student_id.isalnum()

def parse_passport(passport: str) -> tuple:
    """Pasport seriya va raqamni ajratish"""
    passport = passport.upper().replace(' ', '')
    if validate_passport(passport):
        return passport[:2], passport[2:]
    return None, None