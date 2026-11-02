"""Connect the Telegram bot: `python manage.py telegram_setup`.

1. Put TELEGRAM_BOT_TOKEN in backend/.env.
2. Open the bot in Telegram and press Start (or send it any message). For a group: add the bot to the group and write a message there.
3. Run this command. It names the bot, finds your chat, saves TELEGRAM_CHAT_ID in .env and sends a test message.
"""
import json
import re
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

DESCRIPTIONS = {
    "": "ALI TRAVEL alerts: this bot tells the team about new booking requests, messages and reviews from the website.",
    "uz": "ALI TRAVEL xabarnomalari: bot saytdan kelgan yangi bron so'rovlari, xabarlar va sharhlar haqida jamoani xabardor qiladi.",
    "ru": "Уведомления ALI TRAVEL: бот сообщает команде о новых запросах на бронирование, сообщениях и отзывах с сайта.",
}
COMMANDS = {
    "": [("start", "Start / choose language"), ("menu", "Show the menu"), ("language", "Change language"), ("contact", "Contact us")],
    "uz": [("start", "Boshlash / tilni tanlash"), ("menu", "Menyuni koʻrsatish"), ("language", "Tilni oʻzgartirish"), ("contact", "Aloqa")],
    "ru": [("start", "Начать / выбрать язык"), ("menu", "Показать меню"), ("language", "Сменить язык"), ("contact", "Контакты")],
}
SHORT = {"": "ALI TRAVEL booking alerts", "uz": "ALI TRAVEL bron xabarnomalari", "ru": "Уведомления о бронированиях ALI TRAVEL"}


def call(token, method, payload=None):
    request = urllib.request.Request(f"https://api.telegram.org/bot{token}/{method}", data=json.dumps(payload or {}).encode(),
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)["result"]
    except urllib.error.HTTPError as error:
        detail = json.loads(error.read().decode() or "{}").get("description", error.reason)
        raise CommandError(f"Telegram said: {detail}")


def save_chat_id(chat_id):
    path = settings.BASE_DIR / ".env"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    line = f"TELEGRAM_CHAT_ID={chat_id}"
    text = re.sub(r"^TELEGRAM_CHAT_ID=.*$", line, text, flags=re.M) if re.search(r"^TELEGRAM_CHAT_ID=", text, flags=re.M) else text.rstrip("\n") + f"\n{line}\n"
    path.write_text(text, encoding="utf-8")


class Command(BaseCommand):
    help = "Name the Telegram bot, find the chat to alert and send a test message."

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            raise CommandError("Set TELEGRAM_BOT_TOKEN in backend/.env first.")
        me = call(token, "getMe")
        self.stdout.write(f"Bot: @{me['username']}")
        for code, text in DESCRIPTIONS.items():
            call(token, "setMyDescription", {"description": text, "language_code": code})
            call(token, "setMyShortDescription", {"short_description": SHORT[code], "language_code": code})
        for code, commands in COMMANDS.items():
            call(token, "setMyCommands", {"commands": [{"command": c, "description": d} for c, d in commands], "language_code": code})
        self.stdout.write("Bot description set (English, Uzbek, Russian).")

        chat_id = settings.TELEGRAM_CHAT_ID
        if not chat_id:
            updates = call(token, "getUpdates")
            chats = [(u.get("message") or u.get("my_chat_member") or u.get("channel_post") or {}).get("chat") for u in updates]
            chats = [c for c in chats if c]
            if not chats:
                self.stdout.write(self.style.WARNING(f"No chat found yet. Open https://t.me/{me['username']} in Telegram, press Start, then run this command again."))
                return
            chat = chats[-1]
            chat_id = str(chat["id"])
            save_chat_id(chat_id)
            name = str(chat.get('title') or chat.get('first_name') or chat_id).encode('ascii', 'replace').decode()  # Windows consoles cannot print every alphabet
            self.stdout.write(f"Chat found: {name} ({chat_id}); saved in .env.")
        call(token, "sendMessage", {"chat_id": chat_id, "text": "✅ ALI TRAVEL: Telegram alerts are connected. New booking requests, messages and reviews will appear here."})
        self.stdout.write(self.style.SUCCESS("Test message sent."))
