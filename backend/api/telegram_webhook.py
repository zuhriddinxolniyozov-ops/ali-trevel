"""Telegram sends every bot message here when the live server runs `manage.py telegram_bot --webhook`."""
import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from .telegram_bot import Bot, make_call, webhook_secret

log = logging.getLogger("telegram_bot")


@csrf_exempt
def telegram_webhook(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    token = settings.TELEGRAM_BOT_TOKEN
    given = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if not token or not hmac.compare_digest(given, webhook_secret()):
        return HttpResponseForbidden("forbidden")
    try:
        update = json.loads(request.body or b"{}")
    except ValueError:
        return HttpResponse(status=400)
    call = make_call(token)
    try:
        Bot(lambda method, payload=None: call(method, payload)).handle(update)
    except Exception:  # answer 200 anyway: Telegram would otherwise resend the same message again and again
        log.exception("Could not handle update %s", update.get("update_id"))
    return HttpResponse("ok")
