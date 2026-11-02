"""Messages sent when something happens on the site.

 * the team is told about every new booking request, contact message and review (e-mail, and Telegram when a bot is configured);
 * the traveller gets a confirmation when a request arrives and a note when the team confirms, cancels or completes it.

Nothing here may ever break the request that triggered it, so every send is wrapped, logged and (by default) done in the background.
"""
import json
import logging
import threading
import urllib.request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

log = logging.getLogger(__name__)

# Traveller e-mails in English, Uzbek and Russian; other languages receive English.
TEXT = {
    "received": {
        "en": ("We received your request {ref} — ALI TRAVEL",
               "Hello {name},\n\nThank you! We received your booking request {ref} for “{service}”{when}, for {guests} traveler(s).\n"
               "Nothing is booked or charged yet: our team will reply by e-mail to confirm availability and the final price.\n{total}\n"
               "You can cancel free of charge up to 30 days before the start. Details: {site}/legal/cancellation\n\n"
               "Questions? Reply to this e-mail or write to us on WhatsApp {phone}.\n\nALI TRAVEL"),
        "uz": ("So'rovingiz {ref} qabul qilindi — ALI TRAVEL",
               "Assalomu alaykum, {name}!\n\nRahmat! “{service}”{when} uchun {guests} kishilik {ref} raqamli bron so'rovingizni qabul qildik.\n"
               "Hozircha hech narsa band qilinmagan va to'lov olinmagan: jamoamiz joy borligini va yakuniy narxni elektron pochta orqali tasdiqlaydi.\n{total}\n"
               "Boshlanishidan 30 kun oldingacha bepul bekor qilishingiz mumkin. Batafsil: {site}/legal/cancellation\n\n"
               "Savollar bormi? Shu xatga javob yozing yoki WhatsApp {phone} ga murojaat qiling.\n\nALI TRAVEL"),
        "ru": ("Мы получили ваш запрос {ref} — ALI TRAVEL",
               "Здравствуйте, {name}!\n\nСпасибо! Мы получили ваш запрос на бронирование {ref}: «{service}»{when}, {guests} чел.\n"
               "Пока ничего не забронировано и оплата не списана: наша команда ответит по электронной почте, подтвердив наличие мест и окончательную цену.\n{total}\n"
               "Бесплатная отмена возможна за 30 дней до начала. Подробнее: {site}/legal/cancellation\n\n"
               "Есть вопросы? Ответьте на это письмо или напишите нам в WhatsApp {phone}.\n\nALI TRAVEL"),
    },
    "confirmed": {
        "en": ("Your booking {ref} is confirmed — ALI TRAVEL",
               "Hello {name},\n\nGood news: your booking {ref} for “{service}”{when} is confirmed.\nOur team will contact you with the final schedule and how to pay.\n\nQuestions? Reply to this e-mail or write to us on WhatsApp {phone}.\n\nALI TRAVEL"),
        "uz": ("{ref} bron tasdiqlandi — ALI TRAVEL",
               "Assalomu alaykum, {name}!\n\nYaxshi xabar: “{service}”{when} uchun {ref} raqamli broningiz tasdiqlandi.\nJamoamiz yakuniy jadval va to'lov usuli haqida siz bilan bog'lanadi.\n\nSavollar bormi? Shu xatga javob yozing yoki WhatsApp {phone} ga murojaat qiling.\n\nALI TRAVEL"),
        "ru": ("Ваше бронирование {ref} подтверждено — ALI TRAVEL",
               "Здравствуйте, {name}!\n\nХорошая новость: ваше бронирование {ref} — «{service}»{when} — подтверждено.\nНаша команда свяжется с вами по итоговому расписанию и способу оплаты.\n\nЕсть вопросы? Ответьте на это письмо или напишите нам в WhatsApp {phone}.\n\nALI TRAVEL"),
    },
    "cancelled": {
        "en": ("Your booking {ref} was cancelled — ALI TRAVEL",
               "Hello {name},\n\nYour booking {ref} for “{service}” has been cancelled. If this is a surprise, or you would like to travel on another date, just reply to this e-mail or write to us on WhatsApp {phone}.\n\nALI TRAVEL"),
        "uz": ("{ref} bron bekor qilindi — ALI TRAVEL",
               "Assalomu alaykum, {name}!\n\n“{service}” uchun {ref} raqamli broningiz bekor qilindi. Agar bu kutilmagan bo'lsa yoki boshqa sanada sayohat qilmoqchi bo'lsangiz, shu xatga javob yozing yoki WhatsApp {phone} ga murojaat qiling.\n\nALI TRAVEL"),
        "ru": ("Ваше бронирование {ref} отменено — ALI TRAVEL",
               "Здравствуйте, {name}!\n\nВаше бронирование {ref} — «{service}» — отменено. Если это неожиданность или вы хотите поехать в другую дату, просто ответьте на это письмо или напишите нам в WhatsApp {phone}.\n\nALI TRAVEL"),
    },
    "completed": {
        "en": ("Thank you for travelling with ALI TRAVEL",
               "Hello {name},\n\nThank you for travelling with us on “{service}”! We would love to hear how it went. Please share a short review: {review_url}\n\nSee you on the Silk Road again,\nALI TRAVEL"),
        "uz": ("ALI TRAVEL bilan sayohat qilganingiz uchun rahmat",
               "Assalomu alaykum, {name}!\n\n“{service}” safarida biz bilan bo'lganingiz uchun rahmat! Safar qanday o'tganini eshitishni istardik. Iltimos, qisqa sharh qoldiring: {review_url}\n\nIpak yo'lida yana ko'rishguncha,\nALI TRAVEL"),
        "ru": ("Спасибо, что путешествовали с ALI TRAVEL",
               "Здравствуйте, {name}!\n\nСпасибо, что были с нами в поездке «{service}»! Нам очень важно знать, как всё прошло. Пожалуйста, оставьте короткий отзыв: {review_url}\n\nДо новых встреч на Шёлковом пути,\nALI TRAVEL"),
    },
}


def _background(fn, *args):
    def safe():
        try:
            fn(*args)
        except Exception:  # a failed notification must never break the site
            log.exception("Notification failed")

    if settings.NOTIFY_ASYNC:
        threading.Thread(target=safe, daemon=True).start()
    else:
        safe()


def _send_email(subject, body, to, reply_to=None):
    to = [address for address in to if address]
    if not to:
        return
    EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, to, reply_to=reply_to or None).send()


def _send_telegram(text):
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
        data=json.dumps({"chat_id": settings.TELEGRAM_CHAT_ID, "text": text[:3900], "disable_web_page_preview": True}).encode(),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(request, timeout=6).read()


def _tell_the_team(subject, text, reply_to=None):
    for send in (lambda: _send_email(subject, text, settings.NOTIFY_EMAILS, [reply_to] if reply_to else None), lambda: _send_telegram(f"{subject}\n\n{text}")):
        try:
            send()
        except Exception:
            log.exception("Could not notify the team")


def _template(kind, lang):
    texts = TEXT[kind]
    return texts.get(lang) or texts["en"]


WHEN = {"en": " on {d}", "uz": " ({d} sanasi)", "ru": " на {d}"}


def _fields(booking):
    when = WHEN.get(booking["lang"], WHEN["en"]).format(d=booking["date"]) if booking["date"] else ""
    return dict(ref=booking["ref"], name=booking["name"], service=booking["service"], guests=booking["guests"], site=settings.SITE_URL,
                phone=booking["phone_team"], when=when, review_url=booking["review_url"], total=booking["total_line"])


def _booking_data(booking):
    """Copy what the messages need into plain values, so a background thread never touches the database."""
    from .models import SiteContent
    phone = (SiteContent.objects.filter(pk=1).values_list("phone_primary", flat=True).first() or "+998942222498")
    total = f"\nEstimated total: ${booking.estimated_total_usd:,.2f} (sample rate, confirmed by our team).\n" if booking.estimated_total_usd else ""
    return {
        "ref": booking.reference, "name": booking.full_name, "email": booking.email, "phone": booking.phone, "service": booking.service_title,
        "date": booking.travel_date.isoformat() if booking.travel_date else "", "guests": booking.guests, "lang": booking.lang or "en",
        "details": (booking.details_summary or "")[:1500], "requests": (booking.special_requests or "")[:600], "status": booking.status,
        "total": f"${booking.estimated_total_usd:,.2f}" if booking.estimated_total_usd else "-", "phone_team": phone, "total_line": total,
        "review_url": f"{settings.SITE_URL}/tours/{booking.service_slug}" if booking.service_slug else settings.SITE_URL,
    }


def _traveller_email(kind, data):
    subject, body = _template(kind, data["lang"])
    fields = _fields(data)
    if data["lang"] != "en" and data["lang"] in TEXT[kind]:
        fields["total"] = fields["total"].replace("Estimated total", {"uz": "Taxminiy jami", "ru": "Ориентировочная сумма"}.get(data["lang"], "Estimated total")).replace(
            "(sample rate, confirmed by our team)", {"uz": "(namunaviy tarif, jamoamiz tasdiqlaydi)", "ru": "(примерный тариф, подтверждается нашей командой)"}.get(data["lang"], ""))
    _send_email(subject.format(**fields), body.format(**fields), [data["email"]])


def _tell_about_booking(data):
    text = (f"Reference: {data['ref']}\nTour / service: {data['service']}\nName: {data['name']}\nE-mail: {data['email']}\nPhone: {data['phone']}\n"
            f"Date: {data['date'] or '-'}\nGuests: {data['guests']}\nEstimated total: {data['total']}\n")
    if data["details"]:
        text += f"\nDetails:\n{data['details']}\n"
    if data["requests"]:
        text += f"\nSpecial requests:\n{data['requests']}\n"
    text += f"\nOpen: {settings.SITE_URL}/admin/bookings"
    _tell_the_team(f"New booking request {data['ref']}", text, reply_to=data["email"])


def booking_created(booking):
    data = _booking_data(booking)
    _background(_tell_about_booking, data)
    _background(_traveller_email, "received", data)


def booking_status_changed(booking):
    """Tell the traveller when the team confirms, cancels or completes a request."""
    if booking.status in ("confirmed", "cancelled", "completed"):
        _background(_traveller_email, booking.status, _booking_data(booking))


def booking_cancelled_by_traveller(booking):
    data = _booking_data(booking)
    _background(_tell_the_team, f"Booking {data['ref']} was cancelled by the traveller",
                f"{data['name']} <{data['email']}> cancelled {data['service']} ({data['date'] or 'no date'}).\n\nOpen: {settings.SITE_URL}/admin/bookings", data["email"])
    booking_status_changed(booking)


def message_received(message):
    text = f"From: {message.full_name} <{message.email}>\nPhone: {message.phone or '-'}\nSubject: {message.subject or '-'}\n\n{message.message[:2000]}\n\nOpen: {settings.SITE_URL}/admin/enquiries"
    _background(_tell_the_team, f"New message from {message.full_name}", text, message.email)


def review_received(review):
    text = (f"{'★' * review.rating} {review.name}{', ' + review.country if review.country else ''}\nTour: {review.tour_title or review.tour_slug}\n"
            f"{'Verified traveller' if review.verified else 'Not verified'}\n\n{review.text[:1500]}\n\nPublish it: {settings.SITE_URL}/admin/reviews")
    _background(_tell_the_team, "New review waiting for your approval", text)
