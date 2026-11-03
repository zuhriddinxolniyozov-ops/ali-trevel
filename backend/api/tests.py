from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase

from . import models


class AccountingTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)
        self.api = APIClient()
        self.api.force_authenticate(self.admin)
        self.tour = models.Tour.objects.create(
            slug="city", title="City", destination_name="Samarkand", category="Culture", duration_label="2 days", group_type="Small group",
            summary="s", image_url="", price_from_usd=289, itinerary=[{"day": 1, "items": []}, {"day": 2, "items": []}],
            cost_items=[
                {"name": "Guide", "category": "guide", "per": "group", "amount_usd": 50},
                {"name": "Taxi", "category": "transport", "per": "day", "amount_usd": 30},
                {"name": "Breakfast", "category": "meals", "per": "person", "amount_usd": 5},
            ])
        self.booking = models.BookingRequest.objects.create(
            service_type="tour", service_slug="city", service_title="City", full_name="Ann", email="a@b.co", phone="+998901234567",
            travel_date=date(2026, 10, 4), end_date=date(2026, 10, 5), guests=2, estimated_total_usd=578, status="completed")

    def ledger_row(self):
        rows = self.api.get("/api/accounting/ledger/").json()
        return next(r for r in rows if r["id"] == self.booking.id)

    def test_totals_follow_payments_costs_discount_and_agreed_price(self):
        r = self.ledger_row()
        self.assertEqual((r["total_due"], r["paid"], r["balance"], r["state"]), (578, 0, 578, "unpaid"))

        self.api.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "300", "method": "card"})
        self.api.post("/api/expenses/", {"booking": self.booking.id, "category": "guide", "description": "Guide", "amount_usd": "120"})
        r = self.ledger_row()
        self.assertEqual((r["paid"], r["balance"], r["costs"], r["profit"], r["state"]), (300, 278, 120, 458, "partial"))

        # an agreed price replaces the estimate; the discount comes off it
        self.api.patch(f"/api/accounting/bookings/{self.booking.id}/", {"final_price_usd": "600", "discount_usd": "28"}, format="json")
        r = self.ledger_row()
        self.assertEqual((r["total_due"], r["balance"]), (572, 272))

        self.api.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "272"})
        self.assertEqual(self.ledger_row()["state"], "settled")

    def test_cost_template_fills_expenses_per_person_day_and_group(self):
        response = self.api.post(f"/api/accounting/bookings/{self.booking.id}/auto-costs/")
        self.assertEqual(response.status_code, 200)
        # 50 per group + 30 x 2 days + 5 x 2 people
        self.assertEqual(response.json()["costs"], 120)
        # running it again replaces the automatic rows instead of doubling them
        self.assertEqual(self.api.post(f"/api/accounting/bookings/{self.booking.id}/auto-costs/").json()["costs"], 120)

    def test_template_missing_gives_a_clear_error(self):
        self.tour.cost_items = []
        self.tour.save()
        response = self.api.post(f"/api/accounting/bookings/{self.booking.id}/auto-costs/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("cost template", response.json()["error"])

    def test_summary_counts_only_completed_tours_and_includes_general_expenses(self):
        models.BookingRequest.objects.create(  # not completed: must not count as revenue
            service_type="tour", service_title="Other", full_name="Bo", email="b@b.co", phone="+998901234568", guests=1,
            estimated_total_usd=999, status="confirmed", travel_date=date(2026, 10, 6))
        self.api.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "200", "paid_on": "2026-10-05"})
        self.api.post("/api/expenses/", {"booking": self.booking.id, "category": "transport", "description": "Taxi", "amount_usd": "80", "spent_on": "2026-10-05"})
        self.api.post("/api/expenses/", {"category": "office", "description": "Rent", "amount_usd": "40", "spent_on": "2026-10-01"})
        s = self.api.get("/api/accounting/summary/?from=2026-10-01&to=2026-10-31").json()
        self.assertEqual((s["revenue"], s["received"], s["outstanding"]), (578, 200, 378))
        self.assertEqual((s["tour_costs"], s["general_costs"], s["expenses"], s["profit"]), (80, 40, 120, 458))
        self.assertEqual(s["margin"], round(458 / 578 * 100, 1))
        self.assertEqual({c["category"]: c["amount"] for c in s["by_category"]}, {"transport": 80, "office": 40})
        self.assertEqual(len(s["trend"]), 12)
        # outside the period nothing counts
        self.assertEqual(self.api.get("/api/accounting/summary/?from=2027-01-01").json()["revenue"], 0)

    def test_csv_exports_and_invoice(self):
        self.api.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "100"})
        csv_text = self.api.get("/api/accounting/export/").content.decode("utf-8-sig")
        self.assertIn(self.booking.reference, csv_text)
        self.assertIn("Total due USD", csv_text)
        invoice = self.api.get(f"/api/accounting/invoice/{self.booking.id}/").json()
        self.assertEqual((invoice["number"], invoice["total"], invoice["paid"], invoice["balance"]), (f"INV-{self.booking.reference}", 578, 100, 478))

    def test_only_staff_can_see_money(self):
        for path in ("/api/accounting/summary/", "/api/accounting/ledger/", "/api/payments/", "/api/expenses/", "/api/accounting/export/"):
            self.assertIn(APIClient().get(path).status_code, (401, 403), path)
        customer = get_user_model().objects.create_user("c@example.com", "c@example.com", "x")
        client = APIClient()
        client.force_authenticate(customer)
        self.assertEqual(client.get("/api/accounting/summary/").status_code, 403)
        self.assertEqual(client.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "5"}).status_code, 403)

    def test_a_payment_must_be_a_positive_amount(self):
        self.assertEqual(self.api.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "0"}).status_code, 400)
        self.assertEqual(self.api.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "-5"}).status_code, 400)

    def test_decimal_money_stays_exact(self):
        self.api.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "0.10"})
        self.api.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "0.20"})
        self.assertEqual(self.ledger_row()["paid"], 0.3)
        self.assertEqual(sum(p.amount_usd for p in models.Payment.objects.all()), Decimal("0.30"))


class PromotionAndLegalTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)
        self.tour = models.Tour.objects.create(
            slug="t", title="T", destination_name="Samarkand", category="Culture", duration_label="1 day", group_type="Small group",
            summary="s", price_from_usd=100, discount_percent=10)
        self.hotel = models.Hotel.objects.create(slug="h", name="H", destination_name="Samarkand", summary="s", price_from_usd=50)

    def listing(self, path, lang=None):
        headers = {"HTTP_X_LANG": lang} if lang else {}
        return self.client.get(path, **headers).json()

    def test_a_listing_discount_applies_on_its_own(self):
        tour = self.listing("/api/tours/t/")
        self.assertEqual((tour["effective_discount"], tour["promo_title"]), (10, ""))
        self.assertEqual(self.listing("/api/hotels/h/")["effective_discount"], 0)

    def test_the_larger_of_item_discount_and_running_promotion_wins(self):
        models.Promotion.objects.create(title="Autumn sale", percent=20, applies_to="tours", i18n={"uz": {"title": "Kuzgi chegirma"}})
        tour = self.listing("/api/tours/t/")
        self.assertEqual((tour["effective_discount"], tour["promo_title"]), (20, "Autumn sale"))
        self.assertEqual(self.listing("/api/tours/t/", "uz")["promo_title"], "Kuzgi chegirma")
        self.assertEqual(self.listing("/api/hotels/h/")["effective_discount"], 0)  # a tours-only promotion
        models.Promotion.objects.create(title="Small", percent=5, applies_to="all")
        self.assertEqual(self.listing("/api/tours/t/")["effective_discount"], 20)  # 5% does not beat 20%
        self.assertEqual(self.listing("/api/hotels/h/")["effective_discount"], 5)

    def test_inactive_and_expired_promotions_do_not_apply(self):
        past = date.today().replace(year=date.today().year - 1)
        future = date.today().replace(year=date.today().year + 1)
        models.Promotion.objects.create(title="Off", percent=50, active=False)
        models.Promotion.objects.create(title="Ended", percent=50, ends_on=past)
        models.Promotion.objects.create(title="Soon", percent=50, starts_on=future)
        self.assertEqual(self.listing("/api/tours/t/")["effective_discount"], 10)
        self.assertEqual(self.listing("/api/promotions-active/"), [])
        models.Promotion.objects.create(title="Now", percent=15, starts_on=past, ends_on=future)
        self.assertEqual([p["title"] for p in self.listing("/api/promotions-active/")], ["Now"])

    def test_only_staff_manage_promotions(self):
        self.assertIn(self.client.post("/api/promotions/", {"title": "x", "percent": 10}).status_code, (401, 403))
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.post("/api/promotions/", {"title": "x", "percent": 10}, format="json").status_code, 201)
        self.assertEqual(self.client.post("/api/promotions/", {"title": "x", "percent": 95}, format="json").status_code, 400)

    def test_legal_pages_are_public_localized_and_staff_editable(self):
        models.LegalPage.objects.create(slug="privacy", title="Privacy Policy", body="## One\nText", i18n={"uz": {"title": "Maxfiylik siyosati", "body": "## Bir\nMatn"}})
        self.assertEqual(self.listing("/api/legal/privacy/", "uz")["title"], "Maxfiylik siyosati")
        self.assertEqual(self.listing("/api/legal/privacy/", "fr")["title"], "Privacy Policy")  # falls back to English
        self.assertIn(self.client.patch("/api/legal/privacy/", {"title": "Hacked"}, format="json").status_code, (401, 403))
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.delete("/api/legal/privacy/").status_code, 405)  # the three pages cannot be deleted
        self.assertEqual(self.client.patch("/api/legal/privacy/", {"title": "Privacy notice"}, format="json").status_code, 200)
        self.assertEqual(self.listing("/api/legal/privacy/")["title"], "Privacy notice")

    def test_hotels_can_be_listed_for_a_destination(self):
        models.Hotel.objects.create(slug="h2", name="Other", destination_slug="bukhara", destination_name="Bukhara", summary="s", price_from_usd=40)
        models.Hotel.objects.filter(slug="h").update(destination_slug="samarkand")
        slugs = [h["slug"] for h in self.listing("/api/hotels/?destination_slug=samarkand")]
        self.assertEqual(slugs, ["h"])


class ReviewTests(APITestCase):
    def setUp(self):
        cache.clear()  # the rate limits are remembered between tests
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)
        self.tour = models.Tour.objects.create(
            slug="t", title="Tour T", destination_name="Samarkand", category="Food", duration_label="1 day", group_type="Small group",
            summary="s", price_from_usd=100)
        self.body = {"tour_slug": "t", "name": "Anna", "country": "Germany", "rating": 5, "text": "Wonderful day."}

    def test_a_new_review_waits_for_an_admin_and_hides_private_fields(self):
        sent = self.client.post("/api/reviews/", dict(self.body, email="a@x.com", reference="ABC"), format="json")
        self.assertEqual(sent.status_code, 201)
        self.assertNotIn("email", sent.json())
        self.assertEqual(sent.json()["status"], "pending")
        self.assertEqual(self.client.get("/api/reviews/?tour_slug=t").json(), [])

    def test_visitors_cannot_choose_the_status_or_moderate(self):
        review = self.client.post("/api/reviews/", dict(self.body, status="published", verified=True), format="json").json()
        self.assertEqual((review["status"], review["verified"]), ("pending", False))
        self.assertEqual(self.client.patch(f"/api/reviews/{review['id']}/", {"status": "published"}, format="json").status_code, 401)
        self.assertEqual(self.client.delete(f"/api/reviews/{review['id']}/").status_code, 401)

    def test_publishing_updates_the_tour_rating(self):
        first = self.client.post("/api/reviews/", self.body, format="json").json()
        second = self.client.post("/api/reviews/", dict(self.body, name="Bo", rating=4), format="json").json()
        self.client.force_authenticate(self.admin)
        for review in (first, second):
            self.assertEqual(self.client.patch(f"/api/reviews/{review['id']}/", {"status": "published"}, format="json").status_code, 200)
        self.client.force_authenticate(None)
        self.assertEqual(len(self.client.get("/api/reviews/?tour_slug=t").json()), 2)
        self.tour.refresh_from_db()
        self.assertEqual((float(self.tour.rating), self.tour.review_count), (4.5, 2))

    def test_a_matching_confirmed_booking_makes_a_verified_traveller(self):
        booking = models.BookingRequest.objects.create(
            service_type="tour", service_slug="t", service_title="Tour T", full_name="Anna", email="anna@x.com", phone="1", status="completed")
        good = self.client.post("/api/reviews/", dict(self.body, email="ANNA@x.com", reference=booking.reference.lower()), format="json").json()
        wrong = self.client.post("/api/reviews/", dict(self.body, email="other@x.com", reference=booking.reference), format="json").json()
        self.assertTrue(good["verified"])
        self.assertFalse(wrong["verified"])


class GroupPricingTests(APITestCase):
    def test_site_content_serves_the_default_tiers_and_only_admins_change_them(self):
        tiers = self.client.get("/api/site-content/").json()["group_pricing_tiers"]
        self.assertEqual((tiers[0]["min"], tiers[0]["percent"]), (20, 100))
        self.assertIn(1, [t["min"] for t in tiers])
        new = [{"min": 20, "percent": 100}, {"min": 1, "percent": 200}]
        self.assertEqual(self.client.put("/api/site-content/", {"group_pricing_tiers": new}, format="json").status_code, 403)
        self.client.force_authenticate(get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True))
        self.assertEqual(self.client.put("/api/site-content/", {"group_pricing_tiers": new}, format="json").json()["group_pricing_tiers"], new)

    def test_tours_follow_group_pricing_unless_switched_off(self):
        tour = models.Tour.objects.create(slug="g", title="G", destination_name="X", category="Culture", duration_label="1 day", group_type="Small group", summary="s", price_from_usd=100)
        self.assertTrue(self.client.get("/api/tours/g/").json()["group_pricing"])
        tour.group_pricing = False
        tour.save()
        self.assertFalse(self.client.get("/api/tours/g/").json()["group_pricing"])


class TargetedPromotionTests(APITestCase):
    def setUp(self):
        def tour(slug, destination):
            return models.Tour.objects.create(slug=slug, title=slug, destination_slug=destination, destination_name=destination, category="Culture",
                                              duration_label="1 day", group_type="Small group", summary="s", price_from_usd=100)
        tour("samarkand-city", "samarkand")
        tour("plov-class", "samarkand")
        tour("bukhara-city", "bukhara")
        models.Hotel.objects.create(slug="sam-hotel", name="H", destination_slug="samarkand", destination_name="Samarkand", summary="s", price_from_usd=50)
        models.Hotel.objects.create(slug="buk-hotel", name="H2", destination_slug="bukhara", destination_name="Bukhara", summary="s", price_from_usd=50)

    def percent(self, path):
        return self.client.get(path).json()["effective_discount"]

    def test_a_promotion_limited_to_a_destination_only_discounts_that_destination(self):
        models.Promotion.objects.create(title="Samarkand week", percent=20, applies_to="all", destinations=["samarkand"])
        self.assertEqual([self.percent(f"/api/tours/{s}/") for s in ("samarkand-city", "plov-class", "bukhara-city")], [20, 20, 0])
        self.assertEqual((self.percent("/api/hotels/sam-hotel/"), self.percent("/api/hotels/buk-hotel/")), (20, 0))

    def test_a_promotion_limited_to_chosen_tours_only_discounts_those(self):
        models.Promotion.objects.create(title="Plov week", percent=15, applies_to="tours", tours=["plov-class"])
        self.assertEqual([self.percent(f"/api/tours/{s}/") for s in ("samarkand-city", "plov-class", "bukhara-city")], [0, 15, 0])

    def test_a_promotion_without_limits_still_covers_everything(self):
        models.Promotion.objects.create(title="All", percent=10, applies_to="all")
        self.assertEqual(self.percent("/api/tours/bukhara-city/"), 10)


from django.core import mail
from django.test import override_settings


@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="")
class NotificationTests(APITestCase):
    body = {"service_type": "tour", "service_slug": "t", "service_title": "Samarkand City Tour", "full_name": "Anna Berg", "email": "anna@example.com",
            "phone": "+49 151 2345678", "travel_date": "2027-05-01", "guests": 3, "estimated_total_usd": "1200.00"}

    def setUp(self):
        cache.clear()
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)

    def booking(self, lang="en", **extra):
        return self.client.post("/api/bookings-submit/", dict(self.body, **extra), format="json", HTTP_X_LANG=lang)

    def test_a_new_booking_tells_the_team_and_the_traveller(self):
        response = self.booking()
        self.assertEqual(response.status_code, 201)
        to_team = [m for m in mail.outbox if m.to == ["team@example.com"]]
        to_traveller = [m for m in mail.outbox if m.to == ["anna@example.com"]]
        self.assertEqual((len(to_team), len(to_traveller)), (1, 1))
        self.assertIn(response.json()["reference"], to_team[0].subject)
        self.assertEqual(to_team[0].reply_to, ["anna@example.com"])
        self.assertIn("Samarkand City Tour", to_traveller[0].body)
        self.assertIn("2027-05-01", to_traveller[0].body)

    def test_the_traveller_email_follows_the_language_of_the_site(self):
        self.booking(lang="ru")
        message = [m for m in mail.outbox if m.to == ["anna@example.com"]][0]
        self.assertIn("Мы получили ваш запрос", message.subject)
        self.assertIn("на 2027-05-01", message.body)
        mail.outbox.clear()
        self.booking(lang="fr")  # no French template: English is used
        self.assertIn("We received your request", [m for m in mail.outbox if m.to == ["anna@example.com"]][0].subject)

    def test_confirming_or_cancelling_emails_the_traveller_once(self):
        ref = self.booking().json()["reference"]
        booking = models.BookingRequest.objects.get(reference=ref)
        mail.outbox.clear()
        self.client.force_authenticate(self.admin)
        url = f"/api/bookings/{booking.pk}/update_status/"
        self.client.patch(url, {"status": "confirmed"}, format="json")
        self.client.patch(url, {"status": "confirmed", "admin_notes": "called them"}, format="json")  # nothing changed: no second e-mail
        self.assertEqual([m.subject for m in mail.outbox], [f"Your booking {ref} is confirmed — ALI TRAVEL"])
        self.client.patch(url, {"status": "cancelled"}, format="json")
        self.assertEqual(len(mail.outbox), 2)
        self.assertNotIn("called them", mail.outbox[0].body)  # internal notes are never e-mailed

    def test_a_traveller_cancelling_tells_the_team(self):
        ref = self.booking().json()["reference"]
        booking = models.BookingRequest.objects.get(reference=ref)
        mail.outbox.clear()
        self.client.force_authenticate(get_user_model().objects.create_user("anna@example.com", "anna@example.com", "x"))
        self.assertEqual(self.client.post(f"/api/bookings/{booking.pk}/cancel/").status_code, 200)
        self.assertEqual(sorted(tuple(m.to) for m in mail.outbox), [("anna@example.com",), ("team@example.com",)])

    def test_messages_and_reviews_tell_the_team(self):
        models.Tour.objects.create(slug="t", title="Tour T", destination_name="X", category="Culture", duration_label="1 day", group_type="Small group", summary="s", price_from_usd=10)
        self.client.post("/api/contact/", {"full_name": "Bo", "email": "bo@example.com", "message": "Hello"}, format="json")
        self.client.post("/api/reviews/", {"tour_slug": "t", "name": "Bo", "rating": 5, "text": "Great"}, format="json")
        self.assertEqual([m.to for m in mail.outbox], [["team@example.com"], ["team@example.com"]])

    def test_a_broken_mail_server_never_breaks_a_booking(self):
        from unittest import mock
        with mock.patch("api.notifications.EmailMultiAlternatives.send", side_effect=OSError("smtp down")):
            self.assertEqual(self.booking().status_code, 201)
        self.assertEqual(models.BookingRequest.objects.count(), 1)

    def test_robots_fill_a_hidden_field_and_nothing_is_saved(self):
        self.assertEqual(self.booking(website="http://spam.example").status_code, 201)
        self.assertEqual(self.client.post("/api/contact/", {"full_name": "x", "email": "x@x.com", "message": "m", "website": "spam"}, format="json").status_code, 201)
        self.assertEqual((models.BookingRequest.objects.count(), models.ContactMessage.objects.count(), len(mail.outbox)), (0, 0, 0))


class SeoTests(APITestCase):
    def test_sitemap_lists_published_pages_only(self):
        models.Tour.objects.create(slug="live", title="L", destination_name="X", category="Culture", duration_label="1 day", group_type="Small group", summary="s", price_from_usd=10, status="published")
        models.Tour.objects.create(slug="hidden", title="H", destination_name="X", category="Culture", duration_label="1 day", group_type="Small group", summary="s", price_from_usd=10, status="draft")
        xml = self.client.get("/sitemap.xml").content.decode()
        self.assertIn("/tours/live</loc>", xml)
        self.assertNotIn("/tours/hidden", xml)
        self.assertIn("/legal/privacy</loc>", xml)

    def test_robots_keeps_the_admin_out_and_points_to_the_sitemap(self):
        text = self.client.get("/robots.txt").content.decode()
        self.assertIn("Disallow: /admin", text)
        self.assertIn("/sitemap.xml", text)


from .telegram_bot import Bot


class FakeTelegram:
    """Stands in for Telegram: remembers what the bot sent."""

    def __init__(self, fail_photos=False):
        self.sent, self.fail_photos = [], fail_photos

    def __call__(self, method, payload=None):
        if method == "sendPhoto" and self.fail_photos:
            raise RuntimeError("wrong file identifier / HTTP URL specified")
        self.sent.append((method, payload or {}))
        return {}

    def texts(self):
        return [p["text"] for m, p in self.sent if m == "sendMessage"]

    def last(self):
        return [p for m, p in self.sent if m == "sendMessage"][-1]

    def buttons(self):
        return [b for row in self.last().get("reply_markup", {}).get("inline_keyboard", []) for b in row]


@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="", SITE_URL="https://alitravel.example")
class TelegramBotTests(APITestCase):
    def setUp(self):
        self.api = FakeTelegram()
        self.bot = Bot(self.api)
        self.tour = models.Tour.objects.create(
            slug="city", title="City Tour", destination_slug="samarkand", destination_name="Samarkand", category="Culture", duration_label="2 days",
            group_type="Small group", summary="A fine tour.", price_from_usd=200, highlights=["Registan"], status="published",
            i18n={"uz": {"title": "Shahar turi", "summary": "Yaxshi tur."}})
        models.Destination.objects.create(slug="samarkand", name="Samarkand", region="Silk Road", summary="Domes.", suggested_duration="3 days", status="published")

    def say(self, text, chat=77, user="Anna"):
        self.bot.handle({"message": {"chat": {"id": chat}, "from": {"first_name": user, "username": "anna_t"}, "text": text}})

    def press(self, data, chat=77):
        self.bot.handle({"callback_query": {"id": "1", "data": data, "from": {"first_name": "Anna", "username": "anna_t"}, "message": {"chat": {"id": chat}}}})

    def choose(self, code):
        self.say("/start")
        self.press(f"lang:{code}")

    def test_start_offers_the_six_languages(self):
        self.say("/start")
        self.assertEqual([b["callback_data"] for b in self.api.buttons()], [f"lang:{c}" for c in ("en", "uz", "ru", "fr", "de", "es")])
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).lang, "")

    def test_the_chosen_language_is_remembered_and_used(self):
        self.choose("uz")
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).lang, "uz")
        self.assertIn("xush kelibsiz", self.api.last()["text"])
        self.assertEqual([b["callback_data"] for b in self.api.buttons() if "callback_data" in b][:4], ["dests", "tours", "classes", "prices"])
        self.press("tours")
        self.assertIn("Shahar turi · $200", [b["text"] for b in self.api.buttons()])  # the admin's Uzbek title

    def test_start_again_lets_the_traveller_change_language(self):
        self.choose("ru")
        self.say("/start")
        self.assertEqual(len(self.api.buttons()), 6)
        self.press("lang:de")
        self.assertIn("Willkommen", self.api.last()["text"])

    def test_a_tour_card_shows_price_discount_link_and_a_request_button(self):
        models.Promotion.objects.create(title="Sale", percent=10, applies_to="all")
        self.choose("en")
        self.press("t:city")
        card = self.api.last()["text"]
        self.assertIn("<s>$200</s> <b>$180</b>", card)
        self.assertIn("20 or more", card)
        self.assertIn("https://alitravel.example/tours/city", card)
        self.assertIn("Registan", card)
        self.assertIn("r:city", [b.get("callback_data") for b in self.api.buttons()])

    def test_the_price_page_lists_the_group_tiers(self):
        self.choose("en")
        self.press("prices")
        text = self.api.last()["text"]
        self.assertIn("20+ travelers — 100%", text)
        self.assertIn("2–3 travelers — 180%", text)
        self.assertIn("1 travelers — 220%", text)

    def test_a_request_reaches_the_team_and_the_admin_panel(self):
        self.choose("en")
        self.press("r:city")
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "asking")
        self.assertTrue(self.api.last()["reply_markup"]["keyboard"][0][0]["request_contact"])
        self.say("2 people, 5 May please")
        message = models.ContactMessage.objects.get()
        self.assertIn("2 people, 5 May please", message.message)
        self.assertIn("City Tour", message.message)
        self.assertIn("@anna_t", message.message)
        self.assertEqual(message.subject, "Telegram: City Tour")
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "")
        mail_to_team = [m for m in mail.outbox if m.to == ["team@example.com"]]
        self.assertEqual(len(mail_to_team), 1)
        self.assertEqual(mail_to_team[0].reply_to, [])  # the synthetic address is never used for replies

    def test_a_shared_phone_number_is_saved_and_cancel_sends_nothing(self):
        self.choose("en")
        self.press("ask")
        self.bot.handle({"message": {"chat": {"id": 77}, "from": {"first_name": "Anna"}, "contact": {"phone_number": "+4915112345"}}})
        self.assertEqual(models.ContactMessage.objects.get().phone, "+4915112345")
        self.press("ask")
        self.say("✖️ Cancel")
        self.assertEqual(models.ContactMessage.objects.count(), 1)
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "")

    def test_a_photo_telegram_cannot_fetch_does_not_stop_the_answer(self):
        self.api = FakeTelegram(fail_photos=True)
        self.bot = Bot(self.api)
        self.tour.image_url = "https://example.com/photo.jpg"
        self.tour.save()
        self.choose("en")
        self.press("t:city")
        self.assertIn("City Tour", self.api.last()["text"])

    def test_unknown_text_gets_a_hint_and_the_menu(self):
        self.choose("en")
        self.say("blah blah")
        texts = self.api.texts()
        self.assertIn("did not quite understand", texts[-2])
        self.assertIn("Welcome", texts[-1])

    def test_contact_details_come_from_the_site_settings(self):
        models.SiteContent.objects.update_or_create(pk=1, defaults={"phone_primary": "+998901112233", "email": "hello@example.com"})
        self.choose("en")
        self.press("contact")
        self.assertIn("+998901112233", self.api.last()["text"])
        self.assertIn("hello@example.com", self.api.last()["text"])


from unittest import mock


@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="", TELEGRAM_TEAM_USERNAMES=["Al1_travel"], SITE_URL="https://alitravel.example")
class TelegramBookingTests(APITestCase):
    def setUp(self):
        self.api = FakeTelegram()
        self.bot = Bot(self.api)
        self.tour = models.Tour.objects.create(
            slug="city", title="City Tour", destination_slug="samarkand", destination_name="Samarkand", category="Culture", duration_label="2 days",
            group_type="Small group", summary="s", price_from_usd=200, status="published")

    def say(self, text="", chat=77, username="anna_t", **extra):
        self.bot.handle({"message": dict({"chat": {"id": chat}, "from": {"first_name": "Anna", "username": username}, "text": text}, **extra)})

    def press(self, data, chat=77, username="anna_t"):
        self.bot.handle({"callback_query": {"id": "1", "data": data, "from": {"first_name": "Anna", "username": username}, "message": {"chat": {"id": chat}}}})

    def sign_up(self, chat=77, username="anna_t", lang="en"):
        self.say("/start", chat=chat, username=username)
        self.press(f"lang:{lang}", chat=chat, username=username)

    def book(self, guests="4"):
        self.sign_up()
        self.press("b:city")
        self.say("2099-05-01")
        self.say(guests)
        self.say(contact={"phone_number": "+4915112345"})

    def test_booking_in_the_bot_creates_a_real_booking_with_the_group_price(self):
        with mock.patch("api.notifications.telegram_send"):
            self.book("4")
        booking = models.BookingRequest.objects.get()
        self.assertEqual((booking.service_slug, booking.guests, booking.telegram_chat_id, booking.lang), ("city", 4, 77, "en"))
        self.assertEqual((booking.travel_date.isoformat(), booking.phone, booking.estimated_total_usd), ("2099-05-01", "+4915112345", Decimal("1200.00")))  # 200 x 150% x 4
        self.assertIn(booking.reference, self.api.texts()[-2])
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "")

    def test_the_team_hears_about_it_by_email_and_the_traveller_gets_no_email(self):
        with mock.patch("api.notifications.telegram_send"):
            self.book()
        self.assertEqual([m.to for m in mail.outbox], [["team@example.com"]])
        self.assertIn("(Telegram bot)", mail.outbox[0].subject)
        self.assertIn("Source: Telegram bot", mail.outbox[0].body)

    def test_alerts_go_only_to_the_team_account_not_to_other_users(self):
        models.TelegramUser.objects.create(chat_id=1001, username="al1_travel", lang="uz")  # the team account (any capitalisation)
        models.TelegramUser.objects.create(chat_id=2002, username="someone_else", lang="en")  # an ordinary traveller
        with mock.patch("api.notifications.telegram_send") as send:
            self.book()  # a booking made in the bot ...
            self.client.post("/api/bookings-submit/", {"service_type": "tour", "service_slug": "city", "service_title": "City Tour", "full_name": "Bo", "email": "bo@example.com",
                                                      "phone": "+998901112233", "travel_date": "2099-06-01", "guests": 2}, format="json")  # ... and one from the website
        team_alerts = [call.args for call in send.call_args_list if call.args[0] == "1001"]
        self.assertEqual(len(team_alerts), 2)
        self.assertIn("(Telegram bot)", team_alerts[0][1])
        self.assertIn("(Website)", team_alerts[1][1])
        self.assertFalse([call for call in send.call_args_list if call.args[0] in ("2002", "77")])

    def test_confirming_a_bot_booking_messages_the_traveller_in_the_chat(self):
        with mock.patch("api.notifications.telegram_send"):
            self.book()
        booking = models.BookingRequest.objects.get()
        self.client.force_authenticate(get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True))
        with mock.patch("api.notifications.telegram_send") as send:
            self.client.patch(f"/api/bookings/{booking.pk}/update_status/", {"status": "confirmed"}, format="json")
        self.assertEqual([c.args[0] for c in send.call_args_list], [77])
        self.assertIn("confirmed", send.call_args_list[0].args[1])
        self.assertFalse([m for m in mail.outbox if any(a.endswith(".invalid") for a in m.to)])

    def test_bad_answers_are_asked_again(self):
        self.sign_up()
        self.press("b:city")
        self.say("yesterday")
        self.assertIn("could not read that date", self.api.texts()[-1])
        self.say("2000-01-01")
        self.assertIn("could not read that date", self.api.texts()[-1])
        self.say("2099-05-01")
        self.say("a lot")
        self.assertIn("number from 1 to 50", self.api.texts()[-1])
        self.say("4")
        self.say("12")
        self.assertIn("does not look like a phone number", self.api.texts()[-1])
        self.assertEqual(models.BookingRequest.objects.count(), 0)

    def test_cancel_stops_a_booking_halfway(self):
        self.sign_up()
        self.press("b:city")
        self.say("2099-05-01")
        self.say("✖️ Cancel")
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "")
        self.assertEqual(models.BookingRequest.objects.count(), 0)

    def test_my_bookings_lists_only_this_chats_bookings(self):
        with mock.patch("api.notifications.telegram_send"):
            self.book()
            models.BookingRequest.objects.create(service_type="tour", service_title="Other", full_name="X", email="x@example.com", phone="1", telegram_chat_id=999)
            self.press("mine")
        text = self.api.last()["text"]
        self.assertIn("City Tour", text)
        self.assertIn("waiting for confirmation", text)
        self.assertNotIn("Other", text)

    def test_the_team_account_is_told_it_is_registered(self):
        self.say("/start", chat=1001, username="Al1_travel")
        self.assertIn("registered as the <b>ALI TRAVEL team</b>", self.api.texts()[0])
        self.say("/start", chat=2002, username="someone_else")
        self.assertNotIn("ALI TRAVEL team", self.api.texts()[-2])


@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="", SITE_URL="http://localhost:5173")
class TelegramSocialTests(APITestCase):
    def setUp(self):
        self.api = FakeTelegram()
        self.bot = Bot(self.api)
        self.tour = models.Tour.objects.create(
            slug="city", title="City Tour", destination_slug="samarkand", destination_name="Samarkand", category="Culture", duration_label="2 days",
            group_type="Small group", summary="s", price_from_usd=200, status="published")

    def start(self, lang="en"):
        self.bot.handle({"message": {"chat": {"id": 5}, "from": {"first_name": "Bo", "username": "bo"}, "text": "/start"}})
        self.bot.handle({"callback_query": {"id": "1", "data": f"lang:{lang}", "from": {"first_name": "Bo", "username": "bo"}, "message": {"chat": {"id": 5}}}})

    def press(self, data):
        self.bot.handle({"callback_query": {"id": "1", "data": data, "from": {"first_name": "Bo", "username": "bo"}, "message": {"chat": {"id": 5}}}})

    def links(self):
        return [b["url"] for b in self.api.buttons() if "url" in b]

    def test_after_a_tour_is_chosen_the_social_networks_are_suggested(self):
        models.SiteContent.objects.update_or_create(pk=1, defaults={
            "instagram_url": "https://www.instagram.com/al1_travel1", "youtube_url": "https://youtube.com/@alitravel_z", "telegram_url": "https://t.me/al1_travel1"})
        self.start("ru")
        self.press("t:city")
        self.assertIn("Подписывайтесь на ALI TRAVEL", self.api.last()["text"])
        self.assertEqual(self.links(), ["https://www.instagram.com/al1_travel1", "https://youtube.com/@alitravel_z", "https://t.me/al1_travel1"])

    def test_nothing_is_suggested_when_no_social_links_are_set(self):
        models.SiteContent.objects.update_or_create(pk=1, defaults={"instagram_url": "", "youtube_url": "", "telegram_url": "", "facebook_url": ""})
        self.start()
        self.press("t:city")
        self.assertNotIn("Follow ALI TRAVEL", " ".join(self.api.texts()))

    def test_links_that_are_not_https_are_never_offered(self):
        models.SiteContent.objects.update_or_create(pk=1, defaults={"instagram_url": "instagram.com/x", "youtube_url": "http://plain.example"})
        self.start()
        self.press("t:city")
        self.assertEqual(self.links(), [])

    def test_the_suggestion_also_follows_a_finished_booking(self):
        models.SiteContent.objects.update_or_create(pk=1, defaults={"instagram_url": "https://www.instagram.com/al1_travel1"})
        self.start()
        self.press("b:city")
        for answer in ("2099-05-01", "2"):
            self.bot.handle({"message": {"chat": {"id": 5}, "from": {"first_name": "Bo", "username": "bo"}, "text": answer}})
        self.bot.handle({"message": {"chat": {"id": 5}, "from": {"first_name": "Bo", "username": "bo"}, "contact": {"phone_number": "+998901112233"}}})
        texts = self.api.texts()
        self.assertTrue(any("received for" in t for t in texts))
        self.assertTrue(any("Follow ALI TRAVEL" in t for t in texts))


@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="", SITE_URL="https://alitravel.example")
class ReviewThanksTests(APITestCase):
    def setUp(self):
        cache.clear()
        models.Tour.objects.create(slug="t", title="Tour T", destination_name="X", category="Culture", duration_label="1 day", group_type="Small group", summary="s", price_from_usd=10)
        models.SiteContent.objects.update_or_create(pk=1, defaults={"instagram_url": "https://www.instagram.com/al1_travel1", "youtube_url": "https://youtube.com/@alitravel_z", "telegram_url": "", "facebook_url": "not-a-link"})

    def review(self, lang="en", **extra):
        body = {"tour_slug": "t", "name": "Anna", "rating": 5, "text": "Wonderful.", "email": "anna@example.com"}
        return self.client.post("/api/reviews/", dict(body, **extra), format="json", HTTP_X_LANG=lang)

    def test_a_reviewer_with_an_email_is_thanked_and_invited_to_follow_us(self):
        self.assertEqual(self.review().status_code, 201)
        thanks = [m for m in mail.outbox if m.to == ["anna@example.com"]]
        self.assertEqual(len(thanks), 1)
        self.assertIn("Thank you for your review", thanks[0].subject)
        self.assertIn("Instagram: https://www.instagram.com/al1_travel1", thanks[0].body)
        self.assertIn("YouTube: https://youtube.com/@alitravel_z", thanks[0].body)
        self.assertNotIn("not-a-link", thanks[0].body)  # only real https links are offered
        self.assertNotIn("Telegram:", thanks[0].body)  # an empty link is left out

    def test_the_thanks_follows_the_language_of_the_site(self):
        self.review(lang="uz")
        self.assertIn("Sharhingiz uchun rahmat", [m for m in mail.outbox if m.to == ["anna@example.com"]][0].subject)
        mail.outbox.clear()
        self.review(lang="ru")
        self.assertIn("Спасибо за ваш отзыв", [m for m in mail.outbox if m.to == ["anna@example.com"]][0].subject)

    def test_nobody_is_mailed_when_no_email_was_left_but_the_team_is_told(self):
        self.review(email="")
        self.assertEqual([m.to for m in mail.outbox], [["team@example.com"]])


@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="", TELEGRAM_TEAM_USERNAMES=["Al1_travel"], SITE_URL="http://localhost:5173")
class TelegramReviewTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.api = FakeTelegram()
        self.bot = Bot(self.api)
        models.SiteContent.objects.update_or_create(pk=1, defaults={"instagram_url": "https://www.instagram.com/al1_travel1", "youtube_url": "https://youtube.com/@alitravel_z"})
        models.Tour.objects.create(slug="city", title="City Tour", destination_name="Samarkand", category="Culture", duration_label="1 day", group_type="Small group", summary="s", price_from_usd=100, status="published")
        self.booking = models.BookingRequest.objects.create(
            service_type="tour", service_slug="city", service_title="City Tour", full_name="Anna", email="telegram-77@telegram.invalid", phone="+4915112345",
            guests=2, lang="uz", telegram_chat_id=77)
        for step in ({"message": {"chat": {"id": 77}, "from": {"first_name": "Anna", "username": "anna_t"}, "text": "/start"}},
                     {"callback_query": {"id": "1", "data": "lang:uz", "from": {"first_name": "Anna", "username": "anna_t"}, "message": {"chat": {"id": 77}}}}):
            self.bot.handle(step)

    def press(self, data, chat=77):
        self.bot.handle({"callback_query": {"id": "1", "data": data, "from": {"first_name": "Anna", "username": "anna_t"}, "message": {"chat": {"id": chat}}}})

    def say(self, text, chat=77):
        self.bot.handle({"message": {"chat": {"id": chat}, "from": {"first_name": "Anna", "username": "anna_t"}, "text": text}})

    def complete(self):
        self.client.force_authenticate(get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True))
        with mock.patch("api.notifications.telegram_send") as send:
            self.client.patch(f"/api/bookings/{self.booking.pk}/update_status/", {"status": "completed"}, format="json")
        return send

    def test_completing_a_trip_asks_for_stars_in_the_chat(self):
        send = self.complete()
        chat, text = send.call_args.args[:2]
        markup = send.call_args.args[2]
        self.assertEqual(chat, 77)
        self.assertIn("ALI TRAVEL bilan sayohat qilganingiz uchun rahmat", text)
        self.assertIn("yulduzlarni bosib", text)
        self.assertNotIn("localhost", text)
        self.assertEqual([b["callback_data"] for b in markup["inline_keyboard"][0]], [f"rv:{self.booking.reference}:{n}" for n in range(1, 6)])

    def test_a_rating_and_comment_become_a_verified_review_then_the_bot_invites_to_follow_and_return(self):
        self.complete()
        self.press(f"rv:{self.booking.reference}:5")
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "review")
        self.assertIn("⭐⭐⭐⭐⭐", self.api.last()["text"])
        self.say("Osh juda mazali bo'ldi!")
        review = models.Review.objects.get()
        self.assertEqual((review.rating, review.verified, review.status, review.reference, review.tour_slug), (5, True, "pending", self.booking.reference, "city"))
        self.assertEqual((review.text, review.name, review.lang), ("Osh juda mazali bo'ldi!", "Anna", "uz"))
        texts = self.api.texts()
        self.assertTrue(any("Sharhingiz qabul qilindi" in t for t in texts))
        follow = [t for t in texts if "kuzatib boring" in t][-1]
        self.assertIn("Sizni yana kutib qolamiz", follow)
        self.assertTrue([b for b in self.api.sent[-2][1]["reply_markup"]["inline_keyboard"][0] if "instagram.com" in b.get("url", "")])
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "")
        self.assertTrue([m for m in mail.outbox if m.to == ["team@example.com"] and "review" in m.subject.lower()])  # the team is told

    def test_skipping_saves_no_review_but_still_invites_to_return(self):
        self.complete()
        self.press(f"rv:{self.booking.reference}:4")
        self.say("Oʻtkazib yuborish")
        self.assertEqual(models.Review.objects.count(), 0)
        self.assertTrue(any("Sizni yana kutib qolamiz" in t for t in self.api.texts()))

    def test_a_trip_can_be_reviewed_only_once_and_only_by_its_own_chat(self):
        self.complete()
        self.press(f"rv:{self.booking.reference}:5")
        self.say("Super")
        self.press(f"rv:{self.booking.reference}:5")
        self.assertIn("allaqachon baholagansiz", self.api.last()["text"])
        self.assertEqual(models.Review.objects.count(), 1)
        self.press(f"rv:{self.booking.reference}:5", chat=99)  # somebody else's chat
        self.assertEqual(models.TelegramUser.objects.filter(state="review").count(), 0)
        self.assertEqual(models.Review.objects.count(), 1)


class SignInProtectionTests(APITestCase):
    def setUp(self):
        cache.clear()
        get_user_model().objects.create_user("boss@example.com", "boss@example.com", "right-password", is_staff=True)

    def sign_in(self, password, email="boss@example.com", ip="203.0.113.7"):
        return self.client.post("/api/auth/login/", {"email": email, "password": password}, format="json", REMOTE_ADDR=ip)

    def test_repeated_wrong_passwords_lock_that_address_and_account_for_a_while(self):
        for _ in range(8):
            self.assertEqual(self.sign_in("wrong").status_code, 400)
        locked = self.sign_in("right-password")  # even the right password is refused while locked
        self.assertEqual(locked.status_code, 429)
        self.assertIn("Too many failed attempts", locked.json()["error"])

    def test_the_lock_does_not_affect_other_addresses_or_other_accounts(self):
        for _ in range(8):
            self.sign_in("wrong")
        self.assertEqual(self.sign_in("right-password", ip="198.51.100.9").status_code, 200)
        self.assertEqual(self.sign_in("whatever", email="other@example.com").status_code, 400)

    def test_a_successful_sign_in_clears_the_failures(self):
        for _ in range(5):
            self.sign_in("wrong")
        self.assertEqual(self.sign_in("right-password").status_code, 200)
        for _ in range(5):
            self.assertEqual(self.sign_in("wrong").status_code, 400)  # the counter started again from zero

    def test_behind_a_proxy_each_visitor_has_their_own_rate_limit(self):
        from django.conf import settings
        models.Tour.objects.create(slug="t", title="T", destination_name="X", category="Culture", duration_label="1 day", group_type="Small group", summary="s", price_from_usd=10)
        body = {"tour_slug": "t", "name": "Anna", "rating": 5, "text": "Nice"}
        behind_nginx = dict(settings.REST_FRAMEWORK, NUM_PROXIES=1)
        with override_settings(REST_FRAMEWORK=behind_nginx):
            # nginx connects from 127.0.0.1 and appends the visitor's real address last in X-Forwarded-For
            for _ in range(8):
                self.assertEqual(self.client.post("/api/reviews/", body, format="json", REMOTE_ADDR="127.0.0.1", HTTP_X_FORWARDED_FOR="9.9.9.9").status_code, 201)
            self.assertEqual(self.client.post("/api/reviews/", body, format="json", REMOTE_ADDR="127.0.0.1", HTTP_X_FORWARDED_FOR="9.9.9.9").status_code, 429)
            self.assertEqual(self.client.post("/api/reviews/", body, format="json", REMOTE_ADDR="127.0.0.1", HTTP_X_FORWARDED_FOR="8.8.8.8").status_code, 201)
