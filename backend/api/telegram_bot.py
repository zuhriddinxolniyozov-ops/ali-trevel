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


BOOK_STATES = ("book_date", "book_guests", "book_phone")


def parse_date(value):
    """A future date written as 2027-05-01, 01.05.2027, 01/05/2027 or 01-05-2027; otherwise None."""
    for pattern in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            day = datetime.datetime.strptime(value.strip(), pattern).date()
        except ValueError:
            continue
        return day if day >= datetime.date.today() else None
    return None


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


class Bot:
    def __init__(self, call):
        self.call = call

    # ---- sending -----------------------------------------------------------------
    def send(self, chat, body, rows=None, reply_markup=None):
        payload = {"chat_id": chat, "text": body[:4000], "parse_mode": "HTML", "disable_web_page_preview": True}
        if rows is not None:
            payload["reply_markup"] = {"inline_keyboard": rows}
        elif reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return self.call("sendMessage", payload)

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
        if "callback_query" in update:
            self.on_callback(update["callback_query"])
        elif "message" in update:
            self.on_message(update["message"])

    def user_for(self, chat_id, sender):
        user, _ = models.TelegramUser.objects.get_or_create(chat_id=chat_id)
        user.first_name = (sender.get("first_name") or "")[:120]
        user.username = (sender.get("username") or "")[:80]
        user.save()
        return user

    # ---- menus -------------------------------------------------------------------
    def choose_language(self, chat):
        buttons = [button(label, f"lang:{code}") for code, label in LANGS]
        self.send(chat, CHOOSE, rows=[buttons[i:i + 2] for i in range(0, len(buttons), 2)])

    def menu(self, chat, lang, head=None):
        rows = [
            [button(tx("menu_dest", lang), "dests"), button(tx("menu_tours", lang), "tours")],
            [button(tx("menu_classes", lang), "classes"), button(tx("menu_prices", lang), "prices")],
            [button(tx("menu_policy", lang), "policy"), button(tx("menu_contact", lang), "contact")],
            [button(tx("menu_mine", lang), "mine"), button(tx("menu_ask", lang), "ask")],
            [button(tx("menu_lang", lang), "lang")],
        ]
        if is_public_url(site()):
            rows.insert(4, [{"text": tx("open_site", lang), "url": site()}])
        self.send(chat, head or tx("welcome", lang), rows=rows)

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
            user.state = user.state_data = ""
            user.save()
            if is_team(user):
                self.send(chat, tx("team_note", user.lang or "en"))
            return self.choose_language(chat)
        lang = user.lang
        if user.state in ("asking", "review") or user.state in BOOK_STATES:
            return self.collect_request(user, message, body)
        if command == "/contact":
            return self.show_contact(chat, lang)
        if command not in ("/menu", "/help"):
            self.send(chat, tx("unknown", lang))
        self.menu(chat, lang)

    def collect_request(self, user, message, body):
        chat, lang = user.chat_id, user.lang
        if body == tx("cancel", lang) or body.lower() in ("/cancel", "/menu"):
            user.state = user.state_data = ""
            user.save()
            self.send(chat, "👌", reply_markup={"remove_keyboard": True})
            return self.menu(chat, lang)
        if user.state == "review":
            return self.finish_review(user, body)
        contact = message.get("contact") or {}
        phone = contact.get("phone_number", "")
        if user.state in BOOK_STATES:
            return self.continue_booking(user, body, phone)
        if not (body or phone):
            return self.send(chat, tx("ask_prompt", lang))
        tour = models.Tour.objects.filter(slug=user.state_data).first() if user.state_data else None
        who = f"@{user.username}" if user.username else user.first_name or str(user.chat_id)
        lines = [body or "(phone number shared, please call)", "", f"Telegram: {who} · chat {user.chat_id} · language {lang}"]
        if tour:
            lines.insert(0, f"Tour: {tour.title} ({site('/tours/' + tour.slug)})")
        request = models.ContactMessage.objects.create(
            full_name=user.first_name or who, email=f"telegram-{user.chat_id}@telegram.invalid", phone=phone,
            subject=f"Telegram: {tour.title if tour else 'request'}"[:200], message="\n".join(lines))
        notifications.message_received(request)
        user.state = user.state_data = ""
        user.save()
        self.send(chat, tx("ask_thanks", lang), reply_markup={"remove_keyboard": True})
        self.menu(chat, lang)

    # ---- booking in the chat -----------------------------------------------------
    def start_booking(self, user, slug, cache):
        chat, lang = user.chat_id, user.lang
        tour = models.Tour.objects.filter(slug=slug, status="published", price_from_usd__gt=0).first()
        if not tour:
            return self.list_tours(chat, lang, main_tours(), tx("pick_tour", lang), cache)
        user.state, user.state_data = "book_date", slug
        user.save()
        self.send(chat, tx("book_date", lang, title=esc(loc(tour, "title", lang))), reply_markup=self.cancel_keyboard(lang))

    def cancel_keyboard(self, lang, phone=False):
        rows = ([[{"text": tx("share_phone", lang), "request_contact": True}]] if phone else []) + [[{"text": tx("cancel", lang)}]]
        return {"keyboard": rows, "resize_keyboard": True, "one_time_keyboard": True}

    def continue_booking(self, user, body, phone):
        chat, lang = user.chat_id, user.lang
        slug, *rest = user.state_data.split("|")
        tour = models.Tour.objects.filter(slug=slug, status="published", price_from_usd__gt=0).first()
        if not tour:
            user.state = user.state_data = ""
            user.save()
            return self.menu(chat, lang)
        if user.state == "book_date":
            day = parse_date(body)
            if not day:
                return self.send(chat, tx("book_date_bad", lang))
            user.state, user.state_data = "book_guests", f"{slug}|{day.isoformat()}"
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
            return self.send(chat, tx("book_phone", lang, guests=guests, per=money(each), total=money(each * guests)),
                             reply_markup=self.cancel_keyboard(lang, phone=True))
        number = phone or body
        if len(re.sub(r"\D", "", number)) < 7:
            return self.send(chat, tx("book_phone_bad", lang))
        day, guests = datetime.date.fromisoformat(rest[0]), int(rest[1])
        each = per_person(tour, guests, lang, {})
        who = f"@{user.username}" if user.username else user.first_name or str(chat)
        booking = models.BookingRequest.objects.create(
            service_type="tour", service_slug=tour.slug, service_title=tour.title, full_name=user.first_name or who,
            email=f"telegram-{chat}@telegram.invalid", phone=number.strip(), travel_date=day, guests=guests, estimated_total_usd=round(each * guests, 2),
            details_summary=f"Booked in the Telegram bot by {who} (chat {chat}, language {lang}).\nGroup price: {money(each)} per person for {guests} traveler(s).",
            lang=lang, telegram_chat_id=chat)
        notifications.booking_created(booking)
        user.state = user.state_data = ""
        user.save()
        self.send(chat, tx("book_done", lang, ref=booking.reference, title=esc(loc(tour, "title", lang))), reply_markup={"remove_keyboard": True})
        self.suggest_social(chat, lang)
        self.menu(chat, lang)

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
        if booking and text and text != tx("review_skip", lang) and not models.Review.objects.filter(reference=reference).exists():
            review = models.Review.objects.create(
                tour_slug=booking.service_slug, tour_title=booking.service_title, name=user.first_name or user.username or "Traveller", rating=int(stars),
                text=text[:2000], email=booking.email, reference=reference, verified=True, status="pending", lang=lang)
            notifications.review_received(review)  # the team is told; the review is published after a quick check
            self.send(chat, tx("review_done", lang), reply_markup={"remove_keyboard": True})
        else:
            self.send(chat, "👌", reply_markup={"remove_keyboard": True})
        rows = social_rows()
        self.send(chat, tx("social_follow", lang) + "\n\n" + tx("come_again", lang), rows=rows or None)
        self.menu(chat, lang)

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
        if data.startswith("lang:") and data[5:] in LANG_CODES:
            user.lang, user.state, user.state_data = data[5:], "", ""
            user.save()
            self.send(chat, tx("lang_set", user.lang))
            return self.menu(chat, user.lang)
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
        self.photo(chat, destination.image_url)
        tours = models.Tour.objects.filter(status="published", destination_slug=slug)
        places = [loc(t, "title", lang).removesuffix(" Tour") for t in tours if t.parent_slug]
        body = f"<b>{esc(loc(destination, 'name', lang))}</b>\n<i>{esc(loc(destination, 'region', lang))}</i> · ⏱ {esc(loc(destination, 'suggested_duration', lang))}\n\n{esc(loc(destination, 'summary', lang))}"
        if places:
            body += "\n\n📍 " + ", ".join(esc(p) for p in places[:12])
        body += f"\n\n🌐 {esc(tx('web_line', lang))}: {site('/destinations/' + slug)}"
        rows = [[button(self.tour_label(t, lang, cache), f"t:{t.slug}")] for t in tours.filter(parent_slug="", price_from_usd__gt=0)]
        self.send(chat, body, rows=rows + [[button(tx("menu_dest", lang), "dests")], self.back_row(lang)])

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
        self.photo(chat, tour.image_url)
        lines = [f"<b>{esc(loc(tour, 'title', lang))}</b>", f"📍 {esc(loc(tour, 'destination_name', lang))} · ⏱ {esc(loc(tour, 'duration_label', lang))}", "", esc(loc(tour, "summary", lang)), ""]
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
        back = [button(tx("menu_tours", lang), "classes" if tour.tour_type == "workshop" else "tours")]
        self.send(chat, "\n".join(lines), rows=rows + [back, self.back_row(lang)])
        self.suggest_social(chat, lang)

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
            for label, value in (("Instagram", content.instagram_url), ("Telegram", content.telegram_url), ("Facebook", content.facebook_url), ("YouTube", content.youtube_url)):
                if value:
                    lines.append(f"{label}: {esc(value)}")
        lines.append(f"🌐 {site()}")
        self.send(chat, "\n".join(lines), rows=[[button(tx("menu_ask", lang), "ask")], self.back_row(lang)])
