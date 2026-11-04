"""Run the Telegram bot: `python manage.py telegram_bot` (keep it running; on a server use deploy/alitravel-bot.service).

The bot asks for the traveller's language on /start, shows tours, classes, prices and contacts from the website's data, and passes
requests to the team.

Two ways to run it:
  * polling (default): asks Telegram for new messages, so it works without a public web address (your own computer);
  * `--webhook`: for the live server with https. Telegram sends every message to SITE_URL/api/telegram/webhook/ and the website
    answers it. This command then only keeps the webhook registered (it checks every few minutes and sets it again if needed).

Polling refuses to start while a webhook is registered, so a copy on another computer cannot take the bot away from the server
(pass --force to take it over on purpose).
"""
import logging
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from api.telegram_bot import Bot, make_call, webhook_secret, webhook_url

log = logging.getLogger("telegram_bot")
ALLOWED_UPDATES = ["message", "callback_query"]
WEBHOOK_CHECK_SECONDS = 300


class Command(BaseCommand):
    help = "Answer messages sent to the Telegram bot (runs until stopped)."

    def add_arguments(self, parser):
        parser.add_argument("--once", action="store_true", help="Handle the messages waiting now, then stop (useful for testing).")
        parser.add_argument("--webhook", action="store_true", help="Live server: register the website's webhook and keep it registered.")
        parser.add_argument("--force", action="store_true", help="Poll even when a webhook is registered (takes the bot over from the server).")

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            raise CommandError("Set TELEGRAM_BOT_TOKEN in backend/.env first.")
        call = make_call(token)
        me = call("getMe")
        if options["webhook"]:
            return self.keep_webhook(call, me, options["once"])
        hook = (call("getWebhookInfo") or {}).get("url")
        if hook and not options["force"]:
            raise CommandError(f"@{me['username']} is answered by the website ({hook}), so it is not started here. "
                               "Use --force to take it over (the server then stops receiving messages until it sets the webhook again).")
        call("deleteWebhook")  # a webhook and polling cannot be used together
        self.poll(call, me, options["once"])

    def keep_webhook(self, call, me, once):
        url = webhook_url()
        if not url.startswith("https://"):
            raise CommandError(f"A webhook needs an https address; SITE_URL is {settings.SITE_URL}. Run without --webhook instead.")
        self.stdout.write(self.style.SUCCESS(f"@{me['username']} is answered by the website at {url}."))
        while True:
            try:
                info = call("getWebhookInfo") or {}
                if info.get("url") != url:
                    call("setWebhook", {"url": url, "secret_token": webhook_secret(), "allowed_updates": ALLOWED_UPDATES,
                                        "max_connections": 10})
                    log.warning("Telegram webhook set to %s (it was %r)", url, info.get("url"))
                elif info.get("last_error_message"):
                    log.warning("Telegram reports a webhook problem: %s", info["last_error_message"])
            except Exception:
                log.exception("Could not check the Telegram webhook; trying again later")
            if once:
                return
            time.sleep(WEBHOOK_CHECK_SECONDS)

    def poll(self, call, me, once):
        bot = Bot(lambda method, payload=None: call(method, payload))
        self.stdout.write(self.style.SUCCESS(f"@{me['username']} is listening. Press Ctrl+C to stop."))
        offset = None
        while True:
            try:
                payload = {"timeout": 0 if once else 25, "allowed_updates": ALLOWED_UPDATES}
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
            except Exception as error:
                if "can't use getUpdates method while webhook is active" in str(error):
                    log.error("The website now answers the bot (a webhook was registered): polling stops here.")
                    break
                log.exception("Telegram polling failed; retrying in 5 seconds")
                time.sleep(5)
            if once:
                break
