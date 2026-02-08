import os
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

class TelegramBotService:
    def __init__(self):
        self.token = os.getenv("TG_BOT_TOKEN")
        self.group_id = os.getenv("TG_GROUP_ID")
        self.bot = telebot.TeleBot(self.token, threaded=False)
        self._setup_handlers()

    def _setup_handlers(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            text = (
                "🤖 *HomeBot v1.0 Active*\n\n"
                "Доступные команды:\n"
                "/status - Состояние системы\n"
                "/sync - Запустить принудительную синхронизацию\n"
                "/last_logs - Показать последние записи из DB"
            )
            self.bot.reply_to(message, text, parse_mode='Markdown')

        @self.bot.message_handler(commands=['status'])
        def system_status(message):
            # Здесь можно добавить логику запроса к DuckDB
            self.bot.send_message(message.chat.id, "📊 Все системы работают в штатном режиме. База network.db доступна.")

        @self.bot.message_handler(commands=['sync'])
        def trigger_sync(message):
            self.bot.send_message(message.chat.id, "🔄 Запуск синхронизации MikroTik & Shelly...")
            # В app.py мы свяжем это с логикой синхронизации

    def process_update(self, json_data):
        update = types.Update.de_json(json_data)
        self.bot.process_new_updates([update])

    def send_notification(self, text):
        """Метод для отправки алертов в группу"""
        if self.group_id:
            self.bot.send_message(self.group_id, text, parse_mode='Markdown')

# Экспортируем инстанс
tg_service = TelegramBotService()
