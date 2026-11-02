"""Set up the Telegram bot: `python manage.py telegram_setup`.

1. Put TELEGRAM_BOT_TOKEN in backend/.env and name the team account(s) in TELEGRAM_TEAM_USERNAMES (default: Al1_travel).
2. Run this command: it gives the bot its description and command list.
3. Open the bot from the team account and press Start (the bot must be running: `manage.py telegram_bot`). From then on that account,
   and only that account, receives every new booking and message from the website and from the bot.
4. Run this command again: it shows who is registered and sends them a test message.
"""
import json
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from api import notifications

DESCRIPTIONS = {
    "": "ALI TRAVEL: tours, cooking classes, prices and bookings in Uzbekistan. Press Start and choose your language.",
    "uz": "ALI TRAVEL: Oʻzbekistondagi turlar, oshpazlik darslari, narxlar va bronlar. Start ni bosing va tilni tanlang.",
    "ru": "ALI TRAVEL: туры, кулинарные занятия, цены и бронирование в Узбекистане. Нажмите Start и выберите язык.",
}
SHORT = {"": "ALI TRAVEL tours and bookings", "uz": "ALI TRAVEL turlar va bronlar", "ru": "ALI TRAVEL: туры и бронирование"}
COMMANDS = {
    "": [("start", "Start / choose language"), ("menu", "Show the menu"), ("language", "Change language"), ("contact", "Contact us")],
    "uz": [("start", "Boshlash / tilni tanlash"), ("menu", "Menyuni koʻrsatish"), ("language", "Tilni oʻzgartirish"), ("contact", "Aloqa")],
    "ru": [("start", "Начать / выбрать язык"), ("menu", "Показать меню"), ("language", "Сменить язык"), ("contact", "Контакты")],
}


def call(token, method, payload=None):
    request = urllib.request.Request(f"https://api.telegram.org/bot{token}/{method}", data=json.dumps(payload or {}).encode(),
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)["result"]
    except urllib.error.HTTPError as error:
        detail = json.loads(error.read().decode() or "{}").get("description", error.reason)
        raise CommandError(f"Telegram said: {detail}")


class Command(BaseCommand):
    help = "Describe the Telegram bot, register its commands and check that the team account is connected."

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
        self.stdout.write("Bot description and commands set (English, Uzbek, Russian).")

        team = ", ".join(f"@{name.lstrip('@')}" for name in settings.TELEGRAM_TEAM_USERNAMES)
        chats = notifications.team_chat_ids()
        if not chats:
            self.stdout.write(self.style.WARNING(
                f"Team account(s) {team} have not started the bot yet. Open https://t.me/{me['username']} from that account, press Start "
                "(with `manage.py telegram_bot` running), then run this command again."))
            return
        for chat in chats:
            notifications.telegram_send(chat, "✅ ALI TRAVEL: this account receives every new booking and message from the website and from the Telegram bot.")
        self.stdout.write(self.style.SUCCESS(f"Test message sent to {len(chats)} team chat(s) ({team})."))
