import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Инициализация бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# URL вашего приложения (из Ingress)
WEBAPP_URL = os.getenv("WEBHOOK_URL", "https://api.cloudpak.info")

class TelegramService:
    def __init__(self):
        self.bot = bot

    def process_update(self, json_string):
        update = telebot.types.Update.de_json(json_string)
        self.bot.process_new_updates([update])

tg_service = TelegramService()

# --- Обработчики команд ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    # ЭТА КНОПКА ДЕЛАЕТ МАГИЮ MINI APP
    # WebAppInfo открывает сайт внутри Telegram
    web_app_info = WebAppInfo(url=WEBAPP_URL)
    markup.add(InlineKeyboardButton("🚀 Открыть HomeBot", web_app=web_app_info))
    
    bot.send_message(
        message.chat.id, 
        "Привет! Нажми кнопку ниже, чтобы открыть панель управления.", 
        reply_markup=markup
    )

@bot.message_handler(commands=['sync'])
def trigger_sync(message):
    # Тут можно вызвать функцию синхронизации, если нужно
    bot.send_message(message.chat.id, "Запускаю синхронизацию...")
    # Логика вызова sync_all()
