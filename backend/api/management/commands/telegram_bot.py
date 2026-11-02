"""Run the Telegram bot: `python manage.py telegram_bot` (keep it running; on a server use deploy/alitravel-bot.service).

The bot asks for the traveller's language on /start, shows tours, classes, prices and contacts from the website's data, and passes
requests to the team. It polls Telegram for new messages, so it works without a public web address.
"""
import json
import logging
import time
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from api.telegram_bot import Bot

log = logging.getLogger("telegram_bot")


def make_call(token):
    def call(method, payload=None, timeout=20):
        request = urllib.request.Request(f"https://api.telegram.org/bot{token}/{method}", data=json.dumps(payload or {}).encode(),
                                         headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)["result"]
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")[:300]
            raise RuntimeError(f"Telegram {method} failed: {error.code} {detail}")

    return call


class Command(BaseCommand):
    help = "Answer messages sent to the Telegram bot (runs until stopped)."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true", help="Handle the messages waiting now, then stop (useful for testing).")

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            raise CommandError("Set TELEGRAM_BOT_TOKEN in backend/.env first.")
        call = make_call(token)
        me = call("getMe")
        call("deleteWebhook")  # a webhook and polling cannot be used together
        bot = Bot(lambda method, payload=None: call(method, payload))
        self.stdout.write(self.style.SUCCESS(f"@{me['username']} is listening. Press Ctrl+C to stop."))
        offset = None
        while True:
            try:
                payload = {"timeout": 0 if options["once"] else 25, "allowed_updates": ["message", "callback_query"]}
                if offset is not None:
                    payload["offset"] = offset
                for update in call("getUpdates", payload, timeout=40):
                    offset = update["update_id"] + 1
                    try:
                        bot.handle(update)
                    except Exception:  # one bad message must not stop the bot
                        log.exception("Could not handle update %s", update.get("update_id"))
            except KeyboardInterrupt:
                break
            except Exception:
                log.exception("Telegram polling failed; retrying in 5 seconds")
                time.sleep(5)
            if options["once"]:
                break
