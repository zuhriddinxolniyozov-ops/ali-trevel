"""Messages sent when something happens on the site.

 * the team is told about every new booking request, contact message and review (e-mail, and Telegram when a bot is configured);
 * the traveller gets a confirmation when a request arrives and a note when the team confirms, cancels or completes it.

Nothing here may ever break the request that triggered it, so every send is wrapped, logged and (by default) done in the background.
"""
import html
import json
import logging
import threading
import urllib.request

from django.conf import settings
from django.db import connection
from django.core.mail import EmailMultiAlternatives

log = logging.getLogger(__name__)

# Traveller e-mails in English, Uzbek and Russian; other languages receive English.
TEXT = {
    "received": {
        "en": ("We received your request {ref} — ALI TRAVEL",
               "Hello {name},\n\nThank you! We received your booking request {ref} for “{service}”{when}, for {guests} traveler(s).\n"
               "Nothing is booked or charged yet: our team will reply by e-mail to confirm availability and the final price.\n{total}\n"
               "You can cancel free of charge up to 30 days before the start. Details: {site}/legal/cancellation\n\n"
               "Questions? Reply to this e-mail or contact us:\n📞 {phone}\n✈️ Telegram: {telegram}\n✉️ {email}\n\nALI TRAVEL"),
        "uz": ("So'rovingiz {ref} qabul qilindi — ALI TRAVEL",
               "Assalomu alaykum, {name}!\n\nRahmat! “{service}”{when} uchun {guests} kishilik {ref} raqamli bron so'rovingizni qabul qildik.\n"
               "Hozircha hech narsa band qilinmagan va to'lov olinmagan: jamoamiz joy borligini va yakuniy narxni elektron pochta orqali tasdiqlaydi.\n{total}\n"
               "Boshlanishidan 30 kun oldingacha bepul bekor qilishingiz mumkin. Batafsil: {site}/legal/cancellation\n\n"
               "Savollar bormi? Bizga yozing yoki qo'ng'iroq qiling:\n📞 {phone}\n✈️ Telegram: {telegram}\n✉️ {email}\n\nALI TRAVEL"),
        "ru": ("Мы получили ваш запрос {ref} — ALI TRAVEL",
               "Здравствуйте, {name}!\n\nСпасибо! Мы получили ваш запрос на бронирование {ref}: «{service}»{when}, {guests} чел.\n"
               "Пока ничего не забронировано и оплата не списана: наша команда ответит по электронной почте, подтвердив наличие мест и окончательную цену.\n{total}\n"
               "Бесплатная отмена возможна за 30 дней до начала. Подробнее: {site}/legal/cancellation\n\n"
               "Есть вопросы? Ответьте на это письмо или свяжитесь с нами:\n📞 {phone}\n✈️ Telegram: {telegram}\n✉️ {email}\n\nALI TRAVEL"),
    },
    "confirmed": {
        "en": ("Your booking {ref} is confirmed — ALI TRAVEL",
               "Hello {name},\n\nGood news: your booking {ref} for “{service}”{when} is confirmed.\nOur team will contact you with the final schedule and how to pay.\n\nQuestions? Reply to this e-mail or contact us:\n📞 {phone}\n✈️ Telegram: {telegram}\n✉️ {email}\n\nALI TRAVEL"),
        "uz": ("{ref} bron tasdiqlandi — ALI TRAVEL",
               "Assalomu alaykum, {name}!\n\nYaxshi xabar: “{service}”{when} uchun {ref} raqamli broningiz tasdiqlandi.\nJamoamiz yakuniy jadval va to'lov usuli haqida siz bilan bog'lanadi.\n\nSavollar bormi? Bizga yozing yoki qo'ng'iroq qiling:\n📞 {phone}\n✈️ Telegram: {telegram}\n✉️ {email}\n\nALI TRAVEL"),
        "ru": ("Ваше бронирование {ref} подтверждено — ALI TRAVEL",
               "Здравствуйте, {name}!\n\nХорошая новость: ваше бронирование {ref} — «{service}»{when} — подтверждено.\nНаша команда свяжется с вами по итоговому расписанию и способу оплаты.\n\nЕсть вопросы? Ответьте на это письмо или свяжитесь с нами:\n📞 {phone}\n✈️ Telegram: {telegram}\n✉️ {email}\n\nALI TRAVEL"),
    },
    "cancelled": {
        "en": ("Your booking {ref} was cancelled — ALI TRAVEL",
               "Hello {name},\n\nYour booking {ref} for “{service}” has been cancelled. If this is a surprise, or you would like to travel on another date, just reply to this e-mail or contact us:\n📞 {phone}\n✈️ Telegram: {telegram}\n✉️ {email}\n\nALI TRAVEL"),
        "uz": ("{ref} bron bekor qilindi — ALI TRAVEL",
               "Assalomu alaykum, {name}!\n\n“{service}” uchun {ref} raqamli broningiz bekor qilindi. Agar bu kutilmagan bo'lsa yoki boshqa sanada sayohat qilmoqchi bo'lsangiz, bizga yozing yoki qo'ng'iroq qiling:\n📞 {phone}\n✈️ Telegram: {telegram}\n✉️ {email}\n\nALI TRAVEL"),
        "ru": ("Ваше бронирование {ref} отменено — ALI TRAVEL",
               "Здравствуйте, {name}!\n\nВаше бронирование {ref} — «{service}» — отменено. Если это неожиданность или вы хотите поехать в другую дату, просто ответьте на это письмо или свяжитесь с нами:\n📞 {phone}\n✈️ Telegram: {telegram}\n✉️ {email}\n\nALI TRAVEL"),
    },
    "completed_tg": {
        "en": ("Thank you for travelling with ALI TRAVEL",
               "Hello {name},\n\nThank you for being with us on “{service}”! We would love to hear how it went. Tap the stars below to rate your trip, then write a short comment."),
        "uz": ("ALI TRAVEL bilan sayohat qilganingiz uchun rahmat",
               "Assalomu alaykum, {name}!\n\n“{service}” safarida biz bilan bo'lganingiz uchun rahmat! Safar qanday o'tganini eshitishni istardik. Quyidagi yulduzlarni bosib safarni baholang, so'ng qisqa izoh yozing."),
        "ru": ("Спасибо, что путешествовали с ALI TRAVEL",
               "Здравствуйте, {name}!\n\nСпасибо, что были с нами в поездке «{service}»! Нам очень важно знать, как всё прошло. Нажмите на звёзды ниже, чтобы оценить поездку, и напишите короткий комментарий."),
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


def _background(fn, *args, **kwargs):
    def safe():
        try:
            fn(*args, **kwargs)
        except Exception:  # a failed notification must never break the site
            log.exception("Notification failed")

    def in_thread():
        try:
            safe()
        finally:
            connection.close()  # a thread must give its own database connection back

    if settings.NOTIFY_ASYNC:
        threading.Thread(target=in_thread, daemon=True).start()
    else:
        safe()


def _send_email(subject, body, to, reply_to=None):
    to = [address for address in to if address]
    if not to:
        return
    EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, to, reply_to=reply_to or None).send()


def telegram_send(chat_id, text, markup=None, as_html=False):
    """Send one Telegram message from the bot (with an inline keyboard when `markup` is given; `as_html` allows <b>, <i>, <code>, <blockquote>)."""
    payload = {"chat_id": chat_id, "text": text[:3900], "disable_web_page_preview": True}
    if as_html:
        payload["parse_mode"] = "HTML"
    if markup:
        payload["reply_markup"] = markup
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(request, timeout=6).read()


def team_chat_ids():
    """Telegram chats of the team: the accounts named in TELEGRAM_TEAM_USERNAMES that have started the bot (plus TELEGRAM_CHAT_ID if set)."""
    from .models import TelegramUser
    names = {name.lstrip("@").lower() for name in settings.TELEGRAM_TEAM_USERNAMES}
    ids = [str(settings.TELEGRAM_CHAT_ID)] if settings.TELEGRAM_CHAT_ID else []
    ids += [str(u.chat_id) for u in TelegramUser.objects.exclude(username="") if u.username.lower() in names]
    return list(dict.fromkeys(ids))


def _send_telegram(text, markup=None, as_html=False):
    """Alert the team (and nobody else) in Telegram."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    for chat in team_chat_ids():
        try:
            telegram_send(chat, text, markup, as_html)
        except Exception:
            log.exception("Telegram alert to %s failed", chat)


def _tell_the_team(subject, text, reply_to=None, markup=None, telegram_html=None):
    """E-mail the team in plain English; in Telegram send `telegram_html` (Uzbek, formatted) when given, else the same plain text."""
    telegram = (lambda: _send_telegram(telegram_html, markup, True)) if telegram_html else (lambda: _send_telegram(f"{subject}\n\n{text}", markup))
    for send in (lambda: _send_email(subject, text, settings.NOTIFY_EMAILS, [reply_to] if reply_to else None), telegram):
        try:
            send()
        except Exception:
            log.exception("Could not notify the team")


def _template(kind, lang):
    texts = TEXT[kind]
    return texts.get(lang) or texts["en"]


THANKS = {
    "en": ("Thank you for your review — ALI TRAVEL",
           "Hello {name},\n\nThank you for sharing your experience of “{tour}”! We read every review, and yours will help other travellers choose with confidence. It will appear on the website after a quick check.\n\n"
           "If you enjoyed travelling with us, follow us for more photos, videos and travel stories from Uzbekistan:\n{links}\n\nSee you on the Silk Road,\nALI TRAVEL"),
    "uz": ("Sharhingiz uchun rahmat — ALI TRAVEL",
           "Assalomu alaykum, {name}!\n\n“{tour}” bo'yicha tajribangizni ulashganingiz uchun rahmat! Biz har bir sharhni o'qiymiz, sizniki esa boshqa sayyohlarga ishonch bilan tanlashga yordam beradi. U qisqa tekshiruvdan so'ng saytda ko'rinadi.\n\n"
           "Biz bilan sayohat yoqqan bo'lsa, O'zbekistondan ko'proq surat, video va sayohat hikoyalari uchun bizni kuzatib boring:\n{links}\n\nIpak yo'lida ko'rishguncha,\nALI TRAVEL"),
    "ru": ("Спасибо за ваш отзыв — ALI TRAVEL",
           "Здравствуйте, {name}!\n\nСпасибо, что поделились впечатлениями о «{tour}»! Мы читаем каждый отзыв, и ваш поможет другим путешественникам выбирать с уверенностью. Он появится на сайте после короткой проверки.\n\n"
           "Если вам понравилось путешествовать с нами, подписывайтесь — больше фото, видео и историй об Узбекистане:\n{links}\n\nДо встречи на Шёлковом пути,\nALI TRAVEL"),
}

WHEN = {"en": " on {d}", "uz": " ({d} sanasi)", "ru": " на {d}"}


def _fields(booking):
    when = WHEN.get(booking["lang"], WHEN["en"]).format(d=booking["date"]) if booking["date"] else ""
    return dict(ref=booking["ref"], name=booking["name"], service=booking["service"], guests=booking["guests"], site=settings.SITE_URL,
                phone=booking["phone_team"], telegram=booking["telegram_link"], email=booking["team_email"], when=when, review_url=booking["review_url"], total=booking["total_line"])


def _booking_data(booking):
    """Copy what the messages need into plain values, so a background thread never touches the database."""
    from .models import SiteContent
    site = SiteContent.current()
    phone = (site.phone_primary if site else "") or "+998942222498"
    telegram_link = (site.telegram_url if site and site.telegram_url else "") or "https://t.me/al1_travel1"
    team_email = (site.email if site and site.email else "") or "alitravel004@gmail.com"
    from .market import LOCAL, money
    local = getattr(booking, "market", "") == LOCAL
    total = f"\nEstimated total: {money(booking.estimated_total_usd, booking.market)} (sample rate, confirmed by our team).\n" if booking.estimated_total_usd else ""
    return {
        "ref": booking.reference, "name": booking.full_name, "email": booking.email, "phone": booking.phone, "service": booking.service_title,
        "date": booking.travel_date.isoformat() if booking.travel_date else "", "guests": booking.guests, "lang": booking.lang or "en",
        "details": (booking.details_summary or "")[:1500], "requests": (booking.special_requests or "")[:600], "status": booking.status,
        "total": money(booking.estimated_total_usd, booking.market) if booking.estimated_total_usd else "-", "phone_team": phone, "telegram_link": telegram_link, "team_email": team_email, "total_line": total,
        "review_url": f"{settings.SITE_URL}/tours/{booking.service_slug}" if booking.service_slug else settings.SITE_URL,
        "chat": booking.telegram_chat_id, "source": "Telegram bot" if booking.telegram_chat_id else ("Local website (so'm)" if local else "Website"), "local": local,
        "type": booking.service_type, "end": booking.end_date.strftime("%d.%m.%Y") if booking.end_date else "",
        "service_uz": uz_name(booking.service_type, booking.service_slug, booking.service_title),
        "estimate": money(booking.estimated_total_usd, booking.market, decimals=False) if booking.estimated_total_usd else "",
        "meeting": " ".join(x for x in (booking.arrival_date.strftime("%d.%m.%Y") if booking.arrival_date else "", booking.arrival_time.strftime("%H:%M") if booking.arrival_time else "") if x)
                   + (f" · {booking.meeting_place}" if booking.meeting_place else "") if booking.meeting_place else "",
    }


def _traveller_text(kind, data):
    subject, body = _template(kind, data["lang"])
    fields = _fields(data)
    if data["lang"] != "en" and data["lang"] in TEXT[kind]:
        fields["total"] = fields["total"].replace("Estimated total", {"uz": "Taxminiy jami", "ru": "Ориентировочная сумма"}.get(data["lang"], "Estimated total")).replace(
            "(sample rate, confirmed by our team)", {"uz": "(namunaviy tarif, jamoamiz tasdiqlaydi)", "ru": "(примерный тариф, подтверждается нашей командой)"}.get(data["lang"], ""))
    return subject.format(**fields), body.format(**fields)


def _traveller_email(kind, data):
    if data["email"].endswith(".invalid"):  # bookings made in the Telegram bot have no real e-mail address
        return
    _send_email(*_traveller_text(kind, data), [data["email"]])


def _traveller_telegram(kind, data):
    if not (data["chat"] and settings.TELEGRAM_BOT_TOKEN):
        return
    if kind == "completed":  # in Telegram the traveller rates the trip with a tap on the stars, right in the chat
        subject, body = _traveller_text("completed_tg", data)
        stars = {"inline_keyboard": [[{"text": f"{n}⭐", "callback_data": f"rv:{data['ref']}:{n}"} for n in range(1, 6)]]}
        return telegram_send(data["chat"], f"{subject}\n\n{body}", stars)
    subject, body = _traveller_text(kind, data)
    body = body.replace("Reply to this e-mail or contact us:", "Contact us:").replace("reply to this e-mail or contact us:", "contact us:")
    body = body.replace("Ответьте на это письмо или свяжитесь с нами:", "Свяжитесь с нами:").replace("просто ответьте на это письмо или свяжитесь с нами:", "просто свяжитесь с нами:")
    telegram_send(data["chat"], f"{subject}\n\n{body}")


KINDS = {"tour": "🧳 Tur", "hotel": "🏨 Mehmonxona", "transport": "🚗 Transport", "plan": "🗺 Sayohat rejasi", "selection": "🧳 Tanlangan turlar"}
LANGUAGES_UZ = {"uz": "O'zbekcha", "en": "Inglizcha", "ru": "Ruscha", "fr": "Fransuzcha", "de": "Nemischa", "es": "Ispancha"}


def _uz_date(value):
    return value.strftime("%d.%m.%Y") if value else "—"


def _booking_html(data):
    """The new-booking alert for the team's Telegram: in Uzbek, with bold labels and a few emojis."""
    e = lambda value: html.escape(str(value), quote=False)
    date = data["date"] and f"{data['date'][8:10]}.{data['date'][5:7]}.{data['date'][:4]}"
    when = f"{date} → {data['end']}" if date and data["end"] else (date or "—")
    lines = [f"🆕 <b>Yangi bron so'rovi</b>   <code>{e(data['ref'])}</code>",
             f"📍 Manba: {'🤖 Telegram bot' if data['chat'] else ('🇺🇿 Mahalliy sayt (so‘m)' if data.get('local') else '🌐 Sayt')}", "",
             f"<b>{KINDS.get(data['type'], '🧳 Xizmat')}:</b> {e(data['service_uz'])}",
             f"📅 <b>Sana:</b> {e(when)}",
             f"👥 <b>Mehmonlar:</b> {data['guests']}"]
    if data["estimate"]:
        lines.append(f"💵 <b>Taxminiy jami:</b> {data['estimate']} <i>(namunaviy narx, jamoa tasdiqlaydi)</i>")
    if data.get("meeting"):
        lines.append(f"📍 <b>Uchrashuv:</b> {e(data['meeting'])}")
    lines += ["", f"👤 <b>Ism:</b> {e(data['name'])}", f"📞 <b>Telefon:</b> {e(data['phone'])}"]
    if not data["email"].endswith(".invalid"):
        lines.append(f"✉️ <b>Email:</b> {e(data['email'])}")
    lines.append(f"🌐 <b>Til:</b> {LANGUAGES_UZ.get(data['lang'], data['lang'])}")
    if data["details"]:
        lines += ["", "📝 <b>Tafsilotlar</b>", f"<blockquote expandable>{e(data['details'][:1100])}</blockquote>"]
    if data["requests"]:
        lines += ["", "💬 <b>Maxsus so'rovlar</b>", f"<blockquote>{e(data['requests'][:500])}</blockquote>"]
    lines += ["", f"🔗 <a href=\"{e(settings.SITE_URL)}/admin/bookings\">Admin panelda ochish</a>"]
    return "\n".join(lines)


def uz_name(kind, slug, fallback):
    """The Uzbek name of a booked service for the team's alerts (the booking stores the English title)."""
    from .names import service_name
    return service_name(kind, slug, fallback, "uz")


def _tell_about_booking(data):
    text = (f"Source: {data['source']}\nReference: {data['ref']}\nTour / service: {data['service']}\nName: {data['name']}\nE-mail: {data['email']}\nPhone: {data['phone']}\n"
            f"Date: {data['date'] or '-'}\nGuests: {data['guests']}\nEstimated total: {data['total']}\n")
    if data["details"]:
        text += f"\nDetails:\n{data['details']}\n"
    if data["requests"]:
        text += f"\nSpecial requests:\n{data['requests']}\n"
    text += f"\nOpen: {settings.SITE_URL}/admin/bookings"
    decide = {"inline_keyboard": [[{"text": "✅ Tasdiqlash", "callback_data": f"bk:ok:{data['ref']}"}, {"text": "❌ Rad etish", "callback_data": f"bk:no:{data['ref']}"}]]}  # the team answers in the bot
    _tell_the_team(f"New booking request {data['ref']} ({data['source']})", text, reply_to=None if data["email"].endswith(".invalid") else data["email"], markup=decide, telegram_html=_booking_html(data))


VERIFICATION_MAIL = {
    "en": ("Confirm your booking {ref} - ALI TRAVEL",
           "Hello {name},\n\nTo confirm your booking request {ref}, enter this code in the booking form:\n\n    {code}\n\n"
           "The code works for 15 minutes. If you did not make this request, ignore this e-mail.\n\nALI TRAVEL"),
    "uz": ("{ref} broningizni tasdiqlang - ALI TRAVEL",
           "Assalomu alaykum, {name}!\n\n{ref} raqamli bron so'rovingizni tasdiqlash uchun ushbu kodni bron formaga kiriting:\n\n    {code}\n\n"
           "Kod 15 daqiqa amal qiladi. Agar bu so'rovni siz yubormagan bo'lsangiz, bu xatga e'tibor bermang.\n\nALI TRAVEL"),
    "ru": ("Podtverdite bronirovanie {ref} - ALI TRAVEL",
           "Zdravstvuyte, {name}!\n\nChtoby podtverdit' zapros bronirovaniya {ref}, vvedite etot kod v forme bronirovaniya:\n\n    {code}\n\n"
           "Kod deystvitelen 15 minut. Esli vy ne otpravlyali etot zapros, prosto ignorirujte pis'mo.\n\nALI TRAVEL"),
}


def booking_verification_code(booking, code):
    """E-mail the six-digit code that confirms a booking request. Raises when the mail could not be sent."""
    lang = booking.lang if booking.lang in VERIFICATION_MAIL else "en"
    subject, body = VERIFICATION_MAIL[lang]
    if booking.email.endswith(".invalid"):
        return
    _send_email(subject.format(ref=booking.reference), body.format(ref=booking.reference, name=booking.full_name, code=code), [booking.email])   # at once: the traveller waits for it


def booking_created(booking):
    data = _booking_data(booking)
    _background(_tell_about_booking, data)
    _background(_traveller_email, "received", data)  # skipped for Telegram bookings: the bot answers in the chat itself


def booking_status_changed(booking):
    """Tell the traveller when the team confirms, cancels or completes a request."""
    if booking.status in ("confirmed", "cancelled", "completed"):
        data = _booking_data(booking)
        _background(_traveller_email, booking.status, data)
        _background(_traveller_telegram, booking.status, data)


def arrival_received(booking):
    """Tell the team when and how a traveller reaches Samarkand airport (global site), or when and where to meet them (local site)."""
    when = " ".join(x for x in (booking.arrival_date.isoformat() if booking.arrival_date else "", booking.arrival_time.strftime("%H:%M") if booking.arrival_time else "") if x)
    if booking.meeting_place:
        e = lambda value: html.escape(str(value), quote=False)
        text = (f"Booking: {booking.reference} ({booking.service_title})\nTraveller: {booking.full_name} · {booking.phone}\nTour date: {booking.travel_date or '-'}\n"
                f"Meeting: {when or '-'} at {booking.meeting_place}\n\nOpen: {settings.SITE_URL}/admin/bookings")
        card = ["📍 <b>Uchrashuv joyi va vaqti</b>   <code>" + e(booking.reference) + "</code>", "",
                f"<b>{e(uz_name(booking.service_type, booking.service_slug, booking.service_title))}</b>", f"👤 {e(booking.full_name)} · 📞 {e(booking.phone)}",
                f"📅 Tur sanasi: {_uz_date(booking.travel_date)}", "",
                f"🗓 <b>Uchrashuv:</b> {e(_uz_date(booking.arrival_date))}" + (f", soat {booking.arrival_time.strftime('%H:%M')}" if booking.arrival_time else ""),
                f"📍 <b>Joy:</b> {e(booking.meeting_place)}"]
        _background(_tell_the_team, f"Meeting details for {booking.reference}", text, None if booking.email.endswith(".invalid") else booking.email, telegram_html="\n".join(card))
        return
    lines = [f"Booking: {booking.reference} ({booking.service_title})", f"Traveller: {booking.full_name} · {booking.phone}", f"Tour date: {booking.travel_date or '-'}",
             f"Arrives at Samarkand airport: {when or '-'}", f"Flight / train: {booking.arrival_flight or '-'}"]
    if booking.arrival_note:
        lines.append(booking.arrival_note)
    text = "\n".join(lines) + f"\n\nOpen: {settings.SITE_URL}/admin/bookings"
    e = lambda value: html.escape(str(value), quote=False)
    card = ["✈️ <b>Yetib kelish ma'lumoti</b>   <code>" + e(booking.reference) + "</code>", "",
            f"<b>{e(uz_name(booking.service_type, booking.service_slug, booking.service_title))}</b>", f"👤 {e(booking.full_name)} · 📞 {e(booking.phone)}", f"📅 Tur sanasi: {_uz_date(booking.travel_date)}", "",
            f"🛬 <b>Samarqand aeroportiga:</b> {e(_uz_date(booking.arrival_date))}" + (f", {booking.arrival_time.strftime('%H:%M')}" if booking.arrival_time else ""),
            f"🎫 <b>Reys / poyezd:</b> {e(booking.arrival_flight or '—')}"]
    if booking.arrival_note:
        card.append(f"💬 {e(booking.arrival_note)}")
    _background(_tell_the_team, f"Arrival details for {booking.reference}", text, None if booking.email.endswith(".invalid") else booking.email, telegram_html="\n".join(card))


def booking_cancelled_by_traveller(booking):
    data = _booking_data(booking)
    _background(_tell_the_team, f"Booking {data['ref']} was cancelled by the traveller",
                f"{data['name']} <{data['email']}> cancelled {data['service']} ({data['date'] or 'no date'}).\n\nOpen: {settings.SITE_URL}/admin/bookings", data["email"],
                telegram_html=f"❌ <b>Bron bekor qilindi</b>   <code>{html.escape(data['ref'])}</code>\n\nSayohatchi o'z so'rovini bekor qildi:\n<b>{html.escape(data['service_uz'])}</b>\n👤 {html.escape(data['name'])} · 📞 {html.escape(data['phone'])}\n📅 {html.escape(data['date'] or '—')}")
    booking_status_changed(booking)


def message_received(message):
    text = f"From: {message.full_name} <{message.email}>\nPhone: {message.phone or '-'}\nSubject: {message.subject or '-'}\n\n{message.message[:2000]}\n\nOpen: {settings.SITE_URL}/admin/enquiries"
    synthetic = message.email.endswith(".invalid")  # messages typed into the Telegram bot have no real e-mail address
    e = lambda value: html.escape(str(value), quote=False)
    card = ["✉️ <b>Yangi xabar</b>", "", f"👤 <b>{e(message.full_name)}</b>" + (" · 🤖 Telegram bot" if synthetic else ""), f"📞 {e(message.phone or '—')}"]
    if not synthetic:
        card.append(f"📧 {e(message.email)}")
    if message.subject:
        card.append(f"📌 {e(message.subject)}")
    card += ["", f"💬 <blockquote>{e(message.message[:1500])}</blockquote>", "", f"🔗 <a href=\"{e(settings.SITE_URL)}/admin/enquiries\">Murojaatlarni ochish</a>"]
    _background(_tell_the_team, f"New message from {message.full_name}", text, None if synthetic else message.email, telegram_html="\n".join(card))


def _thank_reviewer(data):
    subject, body = THANKS.get(data["lang"]) or THANKS["en"]
    _send_email(subject, body.format(name=data["name"], tour=data["tour"], links=data["links"]), [data["email"]])


def _social_links():
    """The company's social networks from Contact & settings, one per line."""
    from .models import SiteContent
    content = SiteContent.current()
    if not content:
        return settings.SITE_URL
    pairs = (("Instagram", content.instagram_url), ("YouTube", content.youtube_url), ("Telegram", content.telegram_url), ("Facebook", content.facebook_url), ("X", content.x_url))
    return "\n".join(f"{label}: {url}" for label, url in pairs if url.startswith("https://")) or settings.SITE_URL


def review_received(review):
    text = (f"{'★' * review.rating} {review.name}{', ' + review.country if review.country else ''}\nTour: {review.tour_title or review.tour_slug}\n"
            f"{'Verified traveller' if review.verified else 'Not verified'}\n\n{review.text[:1500]}\n\nPublish it: {settings.SITE_URL}/admin/reviews")
    stars = "⭐" * review.rating
    e = lambda value: html.escape(str(value), quote=False)
    card = [f"📝 <b>Yangi sharh tasdiq kutmoqda</b>", "", f"{stars}  <b>{e(review.name)}</b>{', ' + e(review.country) if review.country else ''}",
            f"🧳 <b>Tur:</b> {e(uz_name('tour', review.tour_slug, review.tour_title or review.tour_slug))}",
            "✅ Tasdiqlangan sayohatchi" if review.verified else "⚪ Tasdiqlanmagan", "", f"💬 <blockquote>{e(review.text[:1200])}</blockquote>", "",
            f"🔗 <a href=\"{e(settings.SITE_URL)}/admin/reviews\">Sharhlarni ochish va nashr qilish</a>"]
    _background(_tell_the_team, "New review waiting for your approval", text, telegram_html="\n".join(card))
    if review.email and not review.email.endswith(".invalid"):  # thank the reviewer at once and suggest following us
        _background(_thank_reviewer, {"name": review.name, "email": review.email, "tour": review.tour_title or review.tour_slug,
                                      "lang": review.lang or "en", "links": _social_links()})
