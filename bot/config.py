import os
from dotenv import load_dotenv

# .env faylidan sozlamalarni yuklash
load_dotenv()

# Asosiy bot sozlamalari
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]

# Timezone
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Tashkent')

# Eslatma uchun kunlar
REMINDER_DAYS = [30, 15, 7, 3, 0]