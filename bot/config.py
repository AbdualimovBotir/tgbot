# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

# Database sozlamalari
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'isft_bot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# Timezone
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Tashkent')

# Eslatma kunlari
REMINDER_DAYS = [30, 15, 7, 3, 0]

# Fayl turlari
ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'application/pdf']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB