"""The ALI TRAVEL Telegram bot.

`/start` asks for a language (the six languages of the website); after that the bot shows a menu with destinations, tours, cooking
classes, prices and group sizes, the cancellation policy and contact details, all taken live from the website's own data, and lets the
traveller send a request that arrives in the team's Telegram and in the admin panel (Enquiries).

`Bot` only needs a function `call(method, payload)` that talks to Telegram, so it is easy to test; `manage.py telegram_bot` runs it.
"""
import datetime
import html
import logging
import re

from django.conf import settings

from . import models, notifications
from . import telegram_tour as tour_view
from .serializers import effective_discount
from .telegram_texts import CHOOSE, LANGS, T, text as tx

log = logging.getLogger(__name__)
LANG_CODES = [code for code, _ in LANGS]


def esc(value):
    return html.escape(str(value or ""), quote=False)


def loc(obj, field, lang):
    """A field in the traveller's language (the admin's translation), or the English original."""
    return (getattr(obj, "i18n", None) or {}).get(lang, {}).get(field) or getattr(obj, field, "")


def money(amount):
    amount = float(amount)
    return f"${int(amount):,}" if amount == int(amount) else f"${amount:,.2f}"


def is_public_url(url):
    """Telegram refuses link buttons that point to a computer on a private network."""
    return bool(url) and url.startswith("https://") and "localhost" not in url and "127.0.0.1" not in url


def site(path=""):
    return settings.SITE_URL + path


def loc_uz(tour):
    """The Uzbek title of a tour, for the team that reads the requests."""
    return (tour.i18n or {}).get("uz", {}).get("title") or tour.title


def main_tours():
    return models.Tour.objects.filter(status="published", parent_slug="", price_from_usd__gt=0).exclude(tour_type="workshop")


def class_tours():
    return models.Tour.objects.filter(status="published", tour_type="workshop", price_from_usd__gt=0)


def price_html(tour, lang, cache):
    base = float(tour.price_from_usd)
    percent, _ = effective_discount(tour, cache, lang)
    if percent > 0:
        return f"<s>{money(base)}</s> <b>{money(base * (100 - percent) / 100)}</b> (−{percent}%)"
    return f"<b>{money(base)}</b>"


BOOK_STATES = ("book_date", "book_guests", "book_phone", "book_arrival")


# first letters of the month names in the six languages of the bot
MONTH_STEMS = {
    1: ("jan", "yan", "янв", "ene"), 2: ("feb", "fev", "фев", "fév", "févr"), 3: ("mar", "mär", "мар"), 4: ("apr", "авр", "апр", "abr", "avr"), 5: ("may", "mai", "мая", "май"),
    6: ("jun", "iyun", "июн", "juin"), 7: ("jul", "iyul", "июл", "juil"), 8: ("aug", "avg", "авг", "ago", "aoû", "aou"), 9: ("sep", "sen", "сен"),
    10: ("oct", "okt", "окт"), 11: ("nov", "noy", "ноя"), 12: ("dec", "dek", "дек", "déc", "dic"),
}
TODAY_WORDS = ("today", "bugun", "сегодня", "aujourd", "heute", "hoy")
TOMORROW_WORDS = ("tomorrow", "ertaga", "завтра", "demain", "morgen", "mañana", "manana")


def month_of(word):
    word = word.lower()
    best = None
    for number, stems in MONTH_STEMS.items():
        for stem in stems:
            if word.startswith(stem) and (best is None or len(stem) > best[1]):
                best = (number, len(stem))
    return best[0] if best else None


def read_date(value):
    """What the traveller wrote as a date: ("ok", date), ("past", None) for a day that has gone, or ("text", None) when it is not a date.

    Understands 2027-05-01, 01.05.2027, 1/5/27, 15.05 (this year, or next when it has passed), "15 may", "may 15 2027", "ertaga", "tomorrow"…
    """
    text = (value or "").strip().lower()
    today = datetime.date.today()
    if any(text.startswith(w) for w in TODAY_WORDS):
        return "ok", today
    if any(text.startswith(w) for w in TOMORROW_WORDS):
        return "ok", today + datetime.timedelta(days=1)
    text = re.sub(r"\b(de|del|of|the|am|le|el)\b", " ", text).strip()  # "15 de mayo", "the 15th of May"
    day = month = year = None
    m = re.fullmatch(r"(\d{4})[./-](\d{1,2})[./-](\d{1,2})", text)
    if m:
        year, month, day = (int(x) for x in m.groups())
    else:
        m = re.fullmatch(r"(\d{1,2})[./\-\s](\d{1,2})(?:[./\-\s](\d{2}|\d{4}))?", text)
        if m:
            day, month = int(m.group(1)), int(m.group(2))
            year = int(m.group(3)) if m.group(3) else None
        else:
            m = re.search(r"(\d{1,2})(?:st|nd|rd|th|er|-?(?:ga|да))?\W*([^\W\d_]{3,})\W*(\d{2,4})?", text) or None
            if m and month_of(m.group(2)):
                day, month, year = int(m.group(1)), month_of(m.group(2)), int(m.group(3)) if m.group(3) else None
            else:
                m = re.search(r"([^\W\d_]{3,})\W+(\d{1,2})(?!\d)(?:\W+(\d{2,4}))?", text)
                if m and month_of(m.group(1)):
                    day, month, year = int(m.group(2)), month_of(m.group(1)), int(m.group(3)) if m.group(3) else None
    if not (day and month):
        return "text", None
    explicit = year is not None
    if year is not None and year < 100:
        year += 2000
    try:
        found = datetime.date(year or today.year, month, day)
        if not explicit and found < today:
            found = datetime.date(today.year + 1, month, day)
    except ValueError:
        return "text", None
    return ("ok", found) if found >= today else ("past", None)


def parse_date(value):
    """A future date the traveller wrote (see read_date), otherwise None."""
    kind, day = read_date(value)
    return day if kind == "ok" else None


def tier_percent(tiers, guests):
    ordered = sorted(tiers or models.default_group_tiers(), key=lambda t: -t["min"])
    return next((t["percent"] for t in ordered if guests >= t["min"]), ordered[-1]["percent"])


def per_person(tour, guests, lang, cache):
    """What one traveller pays in a group of `guests`: the listed price, any discount, and the group-size percentage."""
    percent, _ = effective_discount(tour, cache, lang)
    price = float(tour.price_from_usd) * (100 - percent) / 100
    if tour.group_pricing:
        content = models.SiteContent.objects.filter(pk=1).first()
        price *= tier_percent(content.group_pricing_tiers if content else None, guests) / 100
    return round(price, 2)


def social_rows(per_row=2):
    """Link buttons to the company's Instagram, YouTube, Telegram and Facebook (from Contact & settings); only real https links."""
    content = models.SiteContent.objects.filter(pk=1).first()
    if not content:
        return []
    links = [(label, url) for label, url in (("📸 Instagram", content.instagram_url), ("▶️ YouTube", content.youtube_url),
                                             ("✈️ Telegram", content.telegram_url), ("👍 Facebook", content.facebook_url)) if url.startswith("https://")]
    buttons = [{"text": label, "url": url} for label, url in links]
    return [buttons[i:i + per_row] for i in range(0, len(buttons), per_row)]


def is_team(user):
    return bool(user.username) and user.username.lower() in {n.lstrip("@").lower() for n in settings.TELEGRAM_TEAM_USERNAMES}


def button(label, data):
    return {"text": label, "callback_data": data}


BLANK = "⠀"  # an invisible character: a message with buttons only


class Bot:
    def __init__(self, call):
        self.call = call
        self._edit = None  # (chat, message id) of the message a navigation button was pressed on: the next answer replaces it

    # ---- sending -----------------------------------------------------------------
    def send(self, chat, body, rows=None, reply_markup=None, preview=None):
        """Send a message. When it answers a navigation button it edits that message instead (no pile of old messages).
        `preview` is a public picture link shown above the text."""
        if len(body) > 4000:  # cut between lines so no HTML tag is left open
            body = body[:body.rfind("\n", 0, 3990)] + "\n…"
        payload = {"chat_id": chat, "text": body, "parse_mode": "HTML"}
        if preview:
            payload["link_preview_options"] = {"url": preview, "show_above_text": True, "prefer_large_media": True}
        else:
            payload["disable_web_page_preview"] = True
        if rows is not None:
            payload["reply_markup"] = {"inline_keyboard": rows}
        elif reply_markup is not None:
            payload["reply_markup"] = reply_markup
        if rows is not None and self._edit and self._edit[0] == chat:
            message_id, self._edit = self._edit[1], None
            try:
                self.call("editMessageText", dict(payload, message_id=message_id))
                return {"message_id": message_id}
            except Exception as error:
                if "not modified" in str(error):
                    return {"message_id": message_id}
                log.info("Could not edit message %s, sending a new one: %s", message_id, error)
        return self.call("sendMessage", payload)

    def picture(self, url):
        """A public link for a picture (the site's own uploads get the site address in front), or None."""
        if url and url.startswith("/"):
            url = site(url)
        return url if is_public_url(url) else None

    def photo(self, chat, url):
        if url and url.startswith("/"):
            url = site(url)
        if not is_public_url(url):
            return
        try:
            self.call("sendPhoto", {"chat_id": chat, "photo": url})
        except Exception:  # a photo Telegram cannot fetch must not stop the answer
            log.info("Telegram could not fetch %s", url)

    # ---- entry point -------------------------------------------------------------
    def handle(self, update):
        self._edit = None
        if "callback_query" in update:
            self.on_callback(update["callback_query"])
        elif "message" in update:
            self.on_message(update["message"])

    def user_for(self, chat_id, sender):
        user, _ = models.TelegramUser.objects.get_or_create(chat_id=chat_id)
        user.first_name = (sender.get("first_name") or "")[:120]
        user.last_name = (sender.get("last_name") or "")[:120]
        user.username = (sender.get("username") or "")[:80]
        user.save()
        return user

    # ---- menus -------------------------------------------------------------------
    def choose_language(self, chat):
        buttons = [button(label, f"lang:{code}") for code, label in LANGS]
        self.send(chat, CHOOSE, rows=[buttons[i:i + 2] for i in range(0, len(buttons), 2)])

    def menu_rows(self, lang):
        rows = [
            [button(tx("menu_dest", lang), "dests"), button(tx("menu_tours", lang), "tours")],
            [button(tx("menu_classes", lang), "classes"), button(tx("menu_prices", lang), "prices")],
            [button(tx("menu_policy", lang), "policy"), button(tx("menu_contact", lang), "contact")],
            [button(tx("menu_mine", lang), "mine"), button(tx("menu_ask", lang), "ask")],
            [button(tx("menu_lang", lang), "lang")],
        ]
        if is_public_url(site()):
            rows.insert(4, [{"text": tx("open_site", lang), "url": site()}])
        return rows

    def menu(self, chat, lang, head=None, welcome=False):
        """The main menu. The welcome text is shown only right after /start; later the menu carries a short title."""
        self.send(chat, head or tx("welcome" if welcome else "menu_head", lang), rows=self.menu_rows(lang))

    def end_flow(self, chat, lang, text, follow=None):
        """The last message of a task (it also takes the answer keyboard away), then the invitation to follow us whose four buttons lead only to the
        social networks. No menu is sent here: the menu is the bot's Menu button or /menu."""
        try:
            self.send(chat, text, reply_markup={"remove_keyboard": True})
        except Exception:
            log.exception("Could not send the last message of a task")
        rows = social_rows() if follow else []
        if rows:
            try:
                self.send(chat, follow, rows=rows)
            except Exception:
                log.exception("Could not send the invitation to follow us")

    def back_row(self, lang):
        return [button(tx("back", lang), "menu")]

    # ---- messages ----------------------------------------------------------------
    def on_message(self, message):
        chat = message["chat"]["id"]
        user = self.user_for(chat, message.get("from") or message["chat"])
        body = (message.get("text") or "").strip()
        command = body.split()[0].split("@")[0].lower() if body.startswith("/") else ""
        if command in ("/start", "/language") or not user.lang:
            if user.state == "asking":  # take the "share my phone" keyboard away
                self.send(chat, "…", reply_markup={"remove_keyboard": True})
            user.state, user.state_data = "welcome", ""  # the welcome text follows the language choice
            user.save()
            if is_team(user):
                self.send(chat, tx("team_note", user.lang or "en"))
            return self.choose_language(chat)
        lang = user.lang
        if user.state in ("asking", "review") or user.state in BOOK_STATES:
            return self.collect_request(user, message, body)
        if command == "/contact":
            return self.show_contact(chat, lang)
        self.menu(chat, lang, head=tx("unknown", lang) if command not in ("/menu", "/help") else None)

    def collect_request(self, user, message, body):
        chat, lang = user.chat_id, user.lang
        if user.state == "book_arrival" and body.lower() in ("/cancel", "/menu"):
            return self.save_arrival(user, tx("skip", lang))
        if body == tx("cancel", lang) or body.lower() in ("/cancel", "/menu"):
            user.state = user.state_data = ""
            user.save()
            return self.end_flow(chat, lang, "👌")
        if user.state == "review":
            return self.finish_review(user, body)
        contact = message.get("contact") or {}
        phone = contact.get("phone_number", "")
        if contact:  # a shared contact brings the number and the name the traveller uses: both are kept with the customer
            user.phone = phone[:40]
            user.contact_name = " ".join(x for x in (contact.get("first_name"), contact.get("last_name")) if x)[:160]
            user.save()
        if user.state in BOOK_STATES:
            return self.continue_booking(user, body, phone)
        if not (body or phone):
            return self.send(chat, tx("ask_prompt", lang))
        tour = models.Tour.objects.filter(slug=user.state_data).first() if user.state_data else None
        tour_name = loc_uz(tour) if tour else ""
        who = f"@{user.username}" if user.username else user.display_name or str(user.chat_id)
        lines = [body or "(telefon raqami ulashildi, qo'ng'iroq qiling)", "", f"Telegram: {who} · chat {user.chat_id} · til: {lang}"]
        if tour:
            lines.insert(0, f"Tur: {tour_name} ({site('/tours/' + tour.slug)})")
        request = models.ContactMessage.objects.create(
            full_name=user.display_name or who, email=f"telegram-{user.chat_id}@telegram.invalid", phone=phone or user.phone,
            subject=f"Telegram: {tour_name or 'savol'}"[:200], message="\n".join(lines))
        notifications.message_received(request)
        user.state = user.state_data = ""
        user.save()
        self.end_flow(chat, lang, tx("ask_thanks", lang))

    # ---- booking in the chat -----------------------------------------------------
    def start_booking(self, user, slug, cache):
        chat, lang = user.chat_id, user.lang
        tour = models.Tour.objects.filter(slug=slug, status="published", price_from_usd__gt=0).first()
        if not tour:
            return self.list_tours(chat, lang, main_tours(), tx("pick_tour", lang), cache)
        user.state, user.state_data = "book_date", slug
        user.save()
        keyboard = {"keyboard": [[{"text": tx("book_date_later", lang)}], [{"text": tx("cancel", lang)}]], "resize_keyboard": True, "one_time_keyboard": True}
        self.send(chat, tx("book_date", lang, title=esc(loc(tour, "title", lang))), reply_markup=keyboard)

    def cancel_keyboard(self, lang, phone=False):
        rows = ([[{"text": tx("share_phone", lang), "request_contact": True}]] if phone else []) + [[{"text": tx("cancel", lang)}]]
        return {"keyboard": rows, "resize_keyboard": True, "one_time_keyboard": True}

    def continue_booking(self, user, body, phone):
        chat, lang = user.chat_id, user.lang
        if user.state == "book_arrival":
            return self.save_arrival(user, body)
        slug, *rest = user.state_data.split("|")
        tour = models.Tour.objects.filter(slug=slug, status="published", price_from_usd__gt=0).first()
        if not tour:
            user.state = user.state_data = ""
            user.save()
            return self.menu(chat, lang)
        if user.state == "book_date":
            kind, day = read_date(body)
            if kind == "past":
                return self.send(chat, tx("book_date_bad", lang))
            later = body == tx("book_date_later", lang)
            typed = "" if (kind == "ok" or later) else re.sub(r"[|\n]", " ", body)[:60]  # not a date we can read: kept as the traveller wrote it, the team asks
            user.state, user.state_data = "book_guests", f"{slug}|{day.isoformat() if day else ''}|{typed}"
            user.save()
            return self.send(chat, tx("book_guests", lang), reply_markup=self.cancel_keyboard(lang))
        if user.state == "book_guests":
            digits = re.sub(r"\D", "", body)
            guests = int(digits) if digits else 0
            if not 1 <= guests <= 50:
                return self.send(chat, tx("book_guests_bad", lang))
            each = per_person(tour, guests, lang, {})
            user.state, user.state_data = "book_phone", f"{user.state_data}|{guests}"
            user.save()
            note = tx("stay_note", lang) if len(tour.itinerary or []) >= 2 else ""  # multi-day tours include the most affordable hotels
            return self.send(chat, tx("book_phone", lang, guests=guests, per=money(each), total=money(each * guests)) + note,
                             reply_markup=self.cancel_keyboard(lang, phone=True))
        number = phone or body
        if len(re.sub(r"\D", "", number)) < 7:
            return self.send(chat, tx("book_phone_bad", lang))
        user.phone = number.strip()[:40]  # kept with the customer
        user.save(update_fields=["phone"])
        day, typed, guests = (datetime.date.fromisoformat(rest[0]) if rest[0] else None), rest[1], int(rest[2])
        each = per_person(tour, guests, lang, {})
        who = f"@{user.username}" if user.username else user.display_name or str(chat)
        date_line = f"\nSanani sayohatchi shunday yozdi: “{typed}”. Iltimos, tasdiqlang." if typed else "" if day else "\nSana hali yo'q: sayohatchi keyinroq aytadi. Iltimos, so'rang."
        booking = models.BookingRequest.objects.create(
            service_type="tour", service_slug=tour.slug, service_title=tour.title, full_name=user.display_name or who,
            email=f"telegram-{chat}@telegram.invalid", phone=number.strip(), travel_date=day, guests=guests, estimated_total_usd=round(each * guests, 2),
            details_summary=f"Telegram botda {who} bron qildi (chat {chat}, til: {lang}).\nGuruh narxi: bir kishiga {money(each)}, {guests} kishi.{date_line}",
            lang=lang, telegram_chat_id=chat)
        notifications.booking_created(booking)
        user.state, user.state_data = "book_arrival", booking.reference  # next: when does the traveller reach Samarkand airport?
        user.save()
        self.send(chat, tx("book_done", lang, ref=booking.reference, title=esc(loc(tour, "title", lang))), reply_markup={"remove_keyboard": True})
        self.send(chat, tx("arrival_ask", lang), reply_markup={"keyboard": [[{"text": tx("skip", lang)}]], "resize_keyboard": True, "one_time_keyboard": True})

    def save_arrival(self, user, body):
        """The traveller's answer (date, time, flight in their own words) is saved with the booking and sent to the team."""
        chat, lang = user.chat_id, user.lang
        booking = models.BookingRequest.objects.filter(reference=user.state_data, telegram_chat_id=chat).first()
        user.state = user.state_data = ""
        user.save()
        thanks = "👌"
        if booking and body and body != tx("skip", lang):
            booking.arrival_note = body[:300]
            booking.save(update_fields=["arrival_note"])
            notifications.arrival_received(booking)
            thanks = tx("arrival_thanks", lang)
        self.end_flow(chat, lang, thanks, follow=tx("social_follow", lang))

    # ---- rating a finished trip ----------------------------------------------------
    def start_review(self, user, data):
        """The traveller tapped a star under the "thank you for travelling" message: `rv:<reference>:<stars>`."""
        chat, lang = user.chat_id, user.lang
        try:
            _, reference, stars = data.split(":")
            stars = int(stars)
        except ValueError:
            return self.menu(chat, lang)
        booking = models.BookingRequest.objects.filter(reference=reference, telegram_chat_id=chat, status="completed").first()
        if not booking or not 1 <= stars <= 5:
            return self.menu(chat, lang)
        if models.Review.objects.filter(reference=reference).exists():
            return self.send(chat, tx("review_already", lang), rows=[self.back_row(lang)])
        user.state, user.state_data = "review", f"{reference}|{stars}"
        user.save()
        keyboard = {"keyboard": [[{"text": tx("review_skip", lang)}]], "resize_keyboard": True, "one_time_keyboard": True}
        self.send(chat, tx("review_ask", lang, stars="⭐" * stars), reply_markup=keyboard)

    def finish_review(self, user, body):
        chat, lang = user.chat_id, user.lang
        reference, stars = user.state_data.split("|")
        user.state = user.state_data = ""
        user.save()
        booking = models.BookingRequest.objects.filter(reference=reference, telegram_chat_id=chat, status="completed").first()
        text = body.strip()
        done = "👌"
        if booking and text and text != tx("review_skip", lang) and not models.Review.objects.filter(reference=reference).exists():
            review = models.Review.objects.create(
                tour_slug=booking.service_slug, tour_title=booking.service_title, name=user.display_name or "Traveller", rating=int(stars),
                text=text[:2000], email=booking.email, reference=reference, verified=True, status="pending", lang=lang)
            notifications.review_received(review)  # the team is told; the review is published after a quick check
            done = tx("review_done", lang)
        self.end_flow(chat, lang, done, follow=tx("social_follow", lang) + "\n\n" + tx("come_again", lang))

    def suggest_social(self, chat, lang):
        rows = social_rows()
        if rows:
            self.send(chat, tx("social_follow", lang), rows=rows)

    def show_bookings(self, chat, lang):
        bookings = models.BookingRequest.objects.filter(telegram_chat_id=chat).order_by("-created")[:10]
        if not bookings:
            return self.send(chat, tx("mine_none", lang), rows=[self.back_row(lang)])
        lines = [tx("mine_head", lang), ""]
        for b in bookings:
            when = f" · {b.travel_date.isoformat()}" if b.travel_date else ""
            lines.append(f"• <b>{esc(b.reference)}</b> — {esc(b.service_title)}{when} · {b.guests} · {esc(tx('status_' + b.status, lang))}")
        self.send(chat, "\n".join(lines), rows=[self.back_row(lang)])

    # ---- buttons -----------------------------------------------------------------
    def on_callback(self, query):
        chat = query["message"]["chat"]["id"]
        data = query.get("data", "")
        try:
            self.call("answerCallbackQuery", {"callback_query_id": query["id"]})
        except Exception:
            log.info("Could not answer callback query")
        user = self.user_for(chat, query.get("from") or {})
        if data.startswith("bk:"):
            return self.decide_booking(user, query, data)
        message_id = (query.get("message") or {}).get("message_id")
        if message_id and (data in ("menu", "dests", "tours", "classes", "prices", "policy", "contact", "mine", "lang") or data.startswith(("d:", "t:", "lang:", "ti:", "tp:", "tl:", "tg:"))):
            self._edit = (chat, message_id)  # the answer replaces the message the button is under
        if data.startswith("lang:") and data[5:] in LANG_CODES:
            first = user.state == "welcome" or not user.lang  # chosen right after /start, not changed later from the menu
            user.lang, user.state, user.state_data = data[5:], "", ""
            user.save()
            return self.menu(chat, user.lang, head=None if first else tx("lang_set", user.lang), welcome=first)
        if not user.lang or data == "lang":
            return self.choose_language(chat)
        lang, cache = user.lang, {}
        if data == "menu":
            return self.menu(chat, lang)
        if data == "dests":
            return self.list_destinations(chat, lang)
        if data.startswith("d:"):
            return self.show_destination(chat, lang, data[2:], cache)
        if data == "tours":
            return self.list_tours(chat, lang, main_tours(), tx("pick_tour", lang), cache)
        if data == "classes":
            return self.list_tours(chat, lang, class_tours(), tx("classes_intro", lang), cache)
        if data.startswith("t:"):
            return self.show_tour(chat, lang, data[2:], cache)
        if data[:3] in ("ti:", "tp:", "tl:", "tg:"):
            return self.show_tour_part(chat, lang, data, cache)
        if data == "prices":
            return self.show_prices(chat, lang)
        if data == "policy":
            return self.show_policy(chat, lang)
        if data == "contact":
            return self.show_contact(chat, lang)
        if data.startswith("rv:"):
            return self.start_review(user, data)
        if data == "mine":
            return self.show_bookings(chat, lang)
        if data.startswith("b:"):
            return self.start_booking(user, data[2:], cache)
        if data == "ask" or data.startswith("r:"):
            user.state, user.state_data = "asking", data[2:] if data.startswith("r:") else ""
            user.save()
            keyboard = {"keyboard": [[{"text": tx("share_phone", lang), "request_contact": True}], [{"text": tx("cancel", lang)}]], "resize_keyboard": True, "one_time_keyboard": True}
            return self.send(chat, tx("ask_prompt", lang), reply_markup=keyboard)

    # ---- the team answers a booking in the chat -------------------------------------
    def decide_booking(self, user, query, data):
        """Confirm or decline a booking with the buttons under the alert; only team accounts may. The traveller is told by e-mail and Telegram."""
        chat, lang = user.chat_id, "uz"  # the team reads the alerts in Uzbek
        if not is_team(user):
            return
        _, answer, ref = data.split(":", 2)
        booking = models.BookingRequest.objects.filter(reference=ref).first()
        if not booking:
            return self.send(chat, tx("bk_missing", lang))
        if booking.status != "pending":
            return self.send(chat, tx("bk_already", lang, ref=ref, status=booking.status))
        booking.status = "confirmed" if answer == "ok" else "cancelled"
        booking.save(update_fields=["status"])
        notifications.booking_status_changed(booking)
        try:  # take the buttons away so the answer cannot be given twice
            self.call("editMessageReplyMarkup", {"chat_id": chat, "message_id": query["message"]["message_id"], "reply_markup": {"inline_keyboard": []}})
        except Exception:
            log.info("Could not remove the booking buttons")
        self.send(chat, tx("bk_done_ok" if answer == "ok" else "bk_done_no", lang, ref=ref))

    # ---- content -----------------------------------------------------------------
    def list_destinations(self, chat, lang):
        places = models.Destination.objects.filter(status="published")
        if not places:
            return self.send(chat, tx("no_items", lang), rows=[self.back_row(lang)])
        rows = [[button(loc(d, "name", lang), f"d:{d.slug}")] for d in places]
        self.send(chat, tx("pick_dest", lang), rows=rows + [self.back_row(lang)])

    def show_destination(self, chat, lang, slug, cache):
        destination = models.Destination.objects.filter(slug=slug, status="published").first()
        if not destination:
            return self.list_destinations(chat, lang)
        tours = models.Tour.objects.filter(status="published", destination_slug=slug)
        places = [loc(t, "title", lang).removesuffix(" Tour") for t in tours if t.parent_slug]
        body = f"<b>{esc(loc(destination, 'name', lang))}</b>\n<i>{esc(loc(destination, 'region', lang))}</i> · ⏱ {esc(loc(destination, 'suggested_duration', lang))}\n\n{esc(loc(destination, 'summary', lang))}"
        if places:
            body += "\n\n📍 " + ", ".join(esc(p) for p in places[:12])
        body += f"\n\n🌐 {esc(tx('web_line', lang))}: {site('/destinations/' + slug)}"
        rows = [[button(self.tour_label(t, lang, cache), f"t:{t.slug}")] for t in tours.filter(parent_slug="", price_from_usd__gt=0)]
        self.send(chat, body, rows=rows + [[button(tx("menu_dest", lang), "dests")], self.back_row(lang)], preview=self.picture(destination.image_url))

    def tour_label(self, tour, lang, cache):
        percent, _ = effective_discount(tour, cache, lang)
        price = float(tour.price_from_usd) * (100 - percent) / 100
        return f"{loc(tour, 'title', lang)} · {money(price)}"[:60]

    def list_tours(self, chat, lang, tours, head, cache):
        tours = list(tours)
        if not tours:
            return self.send(chat, tx("no_items", lang), rows=[self.back_row(lang)])
        rows = [[button(self.tour_label(t, lang, cache), f"t:{t.slug}")] for t in tours[:40]]
        self.send(chat, head, rows=rows + [self.back_row(lang)])

    def show_tour(self, chat, lang, slug, cache):
        tour = models.Tour.objects.filter(slug=slug, status="published").first()
        if not tour:
            return self.list_tours(chat, lang, main_tours(), tx("pick_tour", lang), cache)
        if tour.parent_slug:  # a single place: its note, ticket and exact location; it is visited only as part of its tour
            parent = models.Tour.objects.filter(slug=tour.parent_slug, status="published").first()
            rows = [[button(tour_view.lab("full_tour", lang) + f" · {loc(parent, 'title', lang)[:30]}", f"t:{parent.slug}")]] if parent else []
            return self.send(chat, tour_view.place_text(tour, lang, parent), rows=rows + [self.back_row(lang)], preview=self.picture(tour.image_url))
        about = loc(tour, "description", lang) or loc(tour, "summary", lang)
        if len(about) > 650:
            about = about[:650].rsplit(" ", 1)[0] + "…"
        lines = [f"<b>{esc(loc(tour, 'title', lang))}</b>", f"📍 {esc(loc(tour, 'destination_name', lang))} · ⏱ {esc(loc(tour, 'duration_label', lang))}", "", esc(about), ""]
        if float(tour.price_from_usd) > 0:
            lines.append(f"💵 {esc(tx('from', lang))} {price_html(tour, lang, cache)} {esc(tx('per_person', lang))}")
            if tour.group_pricing:
                lines.append(f"<i>{esc(tx('group_note', lang))}</i>")
        elif tour.entrance_fee_usd:
            lines.append(f"🎫 {money(tour.entrance_fee_usd)}")
        highlights = loc(tour, "highlights", lang)
        if highlights:
            lines += ["", f"✨ <b>{esc(tx('highlights', lang))}</b>"] + [f"• {esc(h)}" for h in highlights[:5]]
        lines += ["", f"🌐 {esc(tx('web_line', lang))}: {site('/tours/' + tour.slug)}"]
        rows = [[button(tx("request_tour", lang), f"r:{tour.slug}")]]
        if float(tour.price_from_usd) > 0:
            rows.insert(0, [button(tx("book_tour", lang), f"b:{tour.slug}")])
        if is_public_url(site()):
            rows.insert(0, [{"text": tx("open_site", lang), "url": site("/tours/" + tour.slug)}])
        sections = [[button(tour_view.lab("details", lang), f"ti:{tour.slug}"), button(tour_view.lab("plan", lang), f"tp:{tour.slug}:0")],
                    [button(tour_view.lab("places", lang), f"tl:{tour.slug}")]]
        if float(tour.price_from_usd) > 0:
            sections[1].append(button(tour_view.lab("group", lang), f"tg:{tour.slug}"))
        back = [button(tx("menu_tours", lang), "classes" if tour.tour_type == "workshop" else "tours")]
        self.send(chat, "\n".join(lines), rows=sections + rows + [back, self.back_row(lang)], preview=self.picture(tour.image_url))

    def show_tour_part(self, chat, lang, data, cache):
        """One part of a tour: details (ti), day-by-day plan (tp, in pages), places with map links (tl) or the price by group size (tg)."""
        kind, _, rest = data.partition(":")
        slug, _, page = rest.partition(":")
        tour = models.Tour.objects.filter(slug=slug, status="published").first()
        if not tour:
            return self.menu(chat, lang)
        back = [button(tour_view.lab("back_tour", lang), f"t:{tour.slug}")]
        rows = []
        if kind == "ti":
            body = tour_view.details_text(tour, lang)
        elif kind == "tp":
            pages = tour_view.plan_pages(tour, lang)
            index = min(max(int(page or 0), 0), len(pages) - 1)
            body = f"<b>{esc(loc(tour, 'title', lang))}</b>\n<i>{tour_view.lab('plan', lang)[2:].strip()}</i>\n\n{pages[index]}\n\n<i>{esc(tour_view.lab('plan_note', lang))}</i>"
            if len(pages) > 1:
                nav = ([button("◀️", f"tp:{tour.slug}:{index - 1}")] if index else []) + [button(f"{index + 1}/{len(pages)}", f"tp:{tour.slug}:{index}")] + ([button("▶️", f"tp:{tour.slug}:{index + 1}")] if index < len(pages) - 1 else [])
                rows.append(nav)
        elif kind == "tl":
            body, pins = tour_view.places_text(tour, lang)
            if len(pins) > 1:
                rows.append([{"text": tour_view.lab("whole_route", lang), "url": tour_view.route_url(pins)}])
        else:
            content = models.SiteContent.objects.filter(pk=1).first()
            tiers = (content.group_pricing_tiers if content else None) or models.default_group_tiers()
            body = tour_view.group_text(tour, lang, lambda guests: per_person(tour, guests, lang, cache), tiers)
            if float(tour.price_from_usd) > 0:
                rows.append([button(tx("book_tour", lang), f"b:{tour.slug}")])
        self.send(chat, body, rows=rows + [back, self.back_row(lang)])

    def show_prices(self, chat, lang):
        content = models.SiteContent.objects.filter(pk=1).first()
        tiers = sorted((content.group_pricing_tiers if content else None) or models.default_group_tiers(), key=lambda t: -t["min"])
        lines = [tx("prices_head", lang), ""]
        for index, tier in enumerate(tiers):
            low = tier["min"]
            label = f"{low}+" if index == 0 else (str(low) if low == tiers[index - 1]["min"] - 1 else f"{low}–{tiers[index - 1]['min'] - 1}")
            lines.append(f"• {label} {tx('travelers', lang)} — {tier['percent']}%")
        lines += ["", tx("prices_tail", lang)]
        self.send(chat, "\n".join(lines), rows=[self.back_row(lang)])

    def show_policy(self, chat, lang):
        body = tx("policy", lang) + f"\n{site('/legal/cancellation')}\n{site('/legal/terms')}\n{site('/legal/privacy')}"
        self.send(chat, body, rows=[self.back_row(lang)])

    def show_contact(self, chat, lang):
        content = models.SiteContent.objects.filter(pk=1).first()
        lines = [tx("contact_head", lang)]
        if content:
            for value in (content.phone_primary, content.phone_secondary):
                if value:
                    lines.append(f"📞 {esc(value)}")
            if content.email:
                lines.append(f"✉️ {esc(content.email)}")
            if content.address:
                lines.append(f"📍 {esc(loc(content, 'address', lang))}")
            if content.hours:
                lines.append(f"🕘 {esc(loc(content, 'hours', lang))}")
            for label, value in (("Instagram", content.instagram_url), ("Telegram", content.telegram_url), ("Facebook", content.facebook_url), ("YouTube", content.youtube_url), ("X", content.x_url)):
                if value:
                    lines.append(f"{label}: {esc(value)}")
        lines.append(f"🌐 {site()}")
        self.send(chat, "\n".join(lines), rows=[[button(tx("menu_ask", lang), "ask")], self.back_row(lang)])


# ---- talking to Telegram (shared by polling and the webhook) ------------------------
def make_call(token):
    """A `call(method, payload)` function for the Telegram Bot API."""
    import json
    import urllib.error
    import urllib.request

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


WEBHOOK_PATH = "/api/telegram/webhook/"


def webhook_secret():
    """The secret Telegram sends back with every webhook call, derived from SECRET_KEY (letters, digits, _ and - only)."""
    import hashlib
    return hashlib.sha256(f"telegram-webhook:{settings.TELEGRAM_BOT_TOKEN}:{settings.SECRET_KEY}".encode()).hexdigest()


def webhook_url():
    return site(WEBHOOK_PATH)
