"""The small booking deposit (for example $1): a traveller pays it right after sending a booking request, which keeps fake
requests away; it is refunded when the trip is cancelled (automatically or by the team, as set in the admin panel).

Payments go through Octo (https://help.octo.uz): ``prepare_payment`` gives a payment page, Octo tells the site the result at
``notify_url`` (signed with SHA-1 of unique key + payment UUID + status) and ``refund`` returns the money. Until the shop's keys
are in backend/.env (OCTO_SHOP_ID, OCTO_SECRET, OCTO_UNIQUE_KEY) the deposit works in test mode: the payment page is the site's
own and no money moves.
"""
import hashlib
import hmac
import json
import logging
import secrets
import urllib.request
from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from . import models
from .market import LOCAL, use

log = logging.getLogger(__name__)
OCTO = "https://secure.octo.uz"


class PaymentError(Exception):
    pass


def octo_ready():
    return bool(settings.OCTO_SHOP_ID and settings.OCTO_SECRET)


def provider():
    return "octo" if octo_ready() else "test"


def _octo(path, body):
    request = urllib.request.Request(f"{OCTO}/{path}", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    if data.get("error") not in (0, "0", None):
        raise PaymentError(data.get("errMessage") or data.get("errorMessage") or f"Octo error {data.get('error')}")
    return data.get("data") or data


def start(booking, site):
    """Ask the traveller for the deposit: returns the address of the payment page."""
    booking.deposit_status = "pending"
    booking.deposit_amount = site.deposit_amount
    booking.deposit_currency = "UZS" if booking.market == LOCAL else "USD"
    booking.deposit_txn = f"{booking.reference}-{secrets.token_hex(3)}"   # a new id for every attempt (Octo refuses repeats)
    booking.save(update_fields=["deposit_status", "deposit_amount", "deposit_currency", "deposit_txn"])
    if not octo_ready():
        return f"{settings.SITE_URL}/pay/test/{booking.reference}"
    data = _octo("prepare_payment", {
        "octo_shop_id": int(settings.OCTO_SHOP_ID), "octo_secret": settings.OCTO_SECRET, "shop_transaction_id": booking.deposit_txn,
        "auto_capture": True, "test": settings.OCTO_TEST, "init_time": timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"),
        "user_data": {"user_id": str(booking.user_id or ""), "phone": booking.phone, "email": booking.email},
        "total_sum": float(booking.deposit_amount), "currency": booking.deposit_currency,
        "description": f"ALI TRAVEL booking deposit {booking.reference}"[:120],
        "return_url": f"{settings.SITE_URL}/trips?payment={booking.reference}", "notify_url": f"{settings.SITE_URL}/api/deposits/octo/notify/",
        "language": (booking.lang or "en")[:2] if (booking.lang or "en")[:2] in ("en", "uz", "ru") else "en", "ttl": 30,
    })
    booking.deposit_payment_id = str(data.get("octo_payment_UUID") or "")[:64]
    booking.save(update_fields=["deposit_payment_id"])
    url = data.get("octo_pay_url")
    if not url:
        raise PaymentError("Octo did not return a payment page")
    return url


def mark_paid(booking):
    """The deposit arrived: record it for accounting and tell the team and the traveller about the booking (they were waiting for it)."""
    from . import notifications
    if booking.deposit_status == "paid":
        return
    booking.deposit_status, booking.deposit_paid_at = "paid", timezone.now()
    booking.save(update_fields=["deposit_status", "deposit_paid_at"])
    with use(booking.market):
        models.Payment.objects.create(booking=booking, amount_usd=booking.deposit_amount, method="card", note=f"Booking deposit ({provider()})")
        notifications.booking_created(booking)


def refund(booking):
    """Give the deposit back. Raises PaymentError when Octo refuses."""
    if booking.deposit_status != "paid":
        raise PaymentError("Only a paid deposit can be refunded.")
    if octo_ready() and booking.deposit_payment_id:
        data = _octo("refund", {"octo_shop_id": int(settings.OCTO_SHOP_ID), "octo_secret": settings.OCTO_SECRET, "shop_refund_id": f"{booking.deposit_txn}-r",
                                "octo_payment_UUID": booking.deposit_payment_id, "amount": float(booking.deposit_amount)})
        if data.get("status") == "failed":
            raise PaymentError("Octo could not refund this payment.")
    booking.deposit_status, booking.deposit_refunded_at = "refunded", timezone.now()
    booking.save(update_fields=["deposit_status", "deposit_refunded_at"])
    with use(booking.market):
        models.Payment.objects.create(booking=booking, amount_usd=-booking.deposit_amount, method="card", note="Booking deposit refunded")


def keep(booking):
    if booking.deposit_status != "paid":
        raise PaymentError("Only a paid deposit can be kept.")
    booking.deposit_status = "kept"
    booking.save(update_fields=["deposit_status"])


def valid_signature(uuid, status, signature):
    """Octo signs a callback with sha1(unique_key + payment UUID + status)."""
    if not settings.OCTO_UNIQUE_KEY:
        return False
    expected = hashlib.sha1(f"{settings.OCTO_UNIQUE_KEY}{uuid}{status}".encode()).hexdigest()
    return hmac.compare_digest(expected.lower(), str(signature or "").lower())


def deposit_text(amount, market):
    from .market import money
    return money(Decimal(str(amount or 0)), market, decimals=False)
