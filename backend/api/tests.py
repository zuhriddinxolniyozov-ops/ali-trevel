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
        # the 120 of automatic costs (template: 50 + 30 x 2 days + 5 x 2 people) were added when the booking was completed
        self.assertEqual((r["paid"], r["balance"], r["costs"], r["profit"], r["state"]), (300, 278, 240, 338, "partial"))

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

    def test_without_a_template_the_general_cost_rates_are_used(self):
        self.tour.cost_items = []
        self.tour.save()
        response = self.api.post(f"/api/accounting/bookings/{self.booking.id}/auto-costs/")
        self.assertEqual(response.status_code, 200)
        # 2 guests, 2 days: guide 30 x 2 + one car 60 x 2 + 1 night x 1 room x 25
        self.assertEqual(response.json()["costs"], 205)
        self.assertEqual({e["category"] for e in response.json()["expenses"]}, {"guide", "transport", "hotel"})

    def test_summary_counts_only_completed_tours_and_includes_general_expenses(self):
        models.BookingRequest.objects.create(  # not completed: must not count as revenue
            service_type="tour", service_title="Other", full_name="Bo", email="b@b.co", phone="+998901234568", guests=1,
            estimated_total_usd=999, status="confirmed", travel_date=date(2026, 10, 6))
        self.api.post("/api/payments/", {"booking": self.booking.id, "amount_usd": "200", "paid_on": "2026-10-05"})
        self.api.post("/api/expenses/", {"booking": self.booking.id, "category": "transport", "description": "Taxi", "amount_usd": "80", "spent_on": "2026-10-05"})
        self.api.post("/api/expenses/", {"category": "office", "description": "Rent", "amount_usd": "40", "spent_on": "2026-10-01"})
        s = self.api.get("/api/accounting/summary/?from=2026-10-01&to=2026-10-31").json()
        self.assertEqual((s["revenue"], s["received"], s["outstanding"]), (578, 200, 378))
        self.assertEqual((s["tour_costs"], s["general_costs"], s["expenses"], s["profit"]), (200, 40, 240, 338))  # 120 automatic + the 80 taxi
        self.assertEqual(s["margin"], round(338 / 578 * 100, 1))
        self.assertEqual({c["category"]: c["amount"] for c in s["by_category"]}, {"guide": 50, "transport": 140, "meals": 10, "office": 40})
        self.assertEqual(s["expected"]["count"], 1)  # the confirmed tour is a forecast, never revenue
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
        self.assertEqual((tiers[0]["min"], tiers[0]["percent"]), (14, 100))
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
        return {"message_id": 1000 + len(self.sent)} if method == "sendMessage" else {}

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

    def test_after_booking_in_the_bot_the_traveller_is_asked_when_they_reach_samarkand_airport(self):
        self.choose("en")
        self.press("b:city")
        self.say("2030-05-15")
        self.say("2")
        self.say("+998 90 123 45 67")
        self.assertIn("Samarkand airport", self.api.last()["text"])
        booking = models.BookingRequest.objects.get(telegram_chat_id=77)
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "book_arrival")
        self.say("15 May, 14:30, HY 123")
        booking.refresh_from_db()
        self.assertEqual(booking.arrival_note, "15 May, 14:30, HY 123")
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "")
        self.assertTrue(any("our guide will meet you" in t for t in self.api.texts()))

    def test_the_arrival_question_can_be_skipped(self):
        self.choose("en")
        self.press("b:city")
        for answer in ("2030-05-15", "2", "+998 90 123 45 67"):
            self.say(answer)
        self.say("⏭ Skip")
        self.assertEqual(models.BookingRequest.objects.get(telegram_chat_id=77).arrival_note, "")
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "")

    def test_the_welcome_text_is_shown_only_after_start(self):
        self.choose("uz")
        self.assertIn("xush kelibsiz", self.api.last()["text"])  # right after /start and the language choice
        self.press("menu")
        self.assertNotIn("xush kelibsiz", self.api.last()["text"])  # every later menu is only a short title
        self.press("lang")
        self.press("lang:ru")  # changing the language later does not bring the welcome back
        self.assertNotIn("Добро пожаловать", self.api.last()["text"])
        self.say("/start")  # /start does
        self.press("lang:ru")
        self.assertIn("Добро пожаловать", self.api.last()["text"])

    @override_settings(TELEGRAM_TEAM_USERNAMES=["Al1_travel"])
    def test_the_team_confirms_or_declines_a_booking_with_the_buttons_under_the_alert(self):
        booking = models.BookingRequest.objects.create(service_type="tour", service_slug="city", service_title="City Tour", full_name="Anna", email="a@example.com", phone="+998901234567", guests=2, lang="en")
        other = models.BookingRequest.objects.create(service_type="tour", service_slug="city", service_title="City Tour", full_name="Bob", email="b@example.com", phone="+998901234567", guests=1, lang="en")

        def team(data):
            self.bot.handle({"callback_query": {"id": "9", "data": data, "from": {"first_name": "Team", "username": "Al1_travel"}, "message": {"chat": {"id": 5}, "message_id": 12}}})
        self.press(f"bk:ok:{booking.reference}")  # a traveller (not in the team) cannot decide
        booking.refresh_from_db()
        self.assertEqual(booking.status, "pending")
        team(f"bk:ok:{booking.reference}")
        booking.refresh_from_db()
        self.assertEqual(booking.status, "confirmed")
        self.assertIn(booking.reference, self.api.last()["text"])
        self.assertTrue(any(m == "editMessageReplyMarkup" for m, _ in self.api.sent))  # the buttons are taken away
        self.assertEqual(len(mail.outbox), 1)  # the traveller is told
        team(f"bk:no:{booking.reference}")  # an answered booking is not changed again
        booking.refresh_from_db()
        self.assertEqual(booking.status, "confirmed")
        team(f"bk:no:{other.reference}")
        other.refresh_from_db()
        self.assertEqual(other.status, "cancelled")

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
        self.assertIn("14 or more", card)
        self.assertIn("https://alitravel.example/tours/city", card)
        self.assertIn("Registan", card)
        self.assertIn("r:city", [b.get("callback_data") for b in self.api.buttons()])

    def test_the_price_page_lists_the_group_tiers(self):
        self.choose("en")
        self.press("prices")
        text = self.api.last()["text"]
        self.assertIn("14+ travelers — 100%", text)
        self.assertIn("3–6 travelers — 138%", text)
        self.assertIn("1–2 travelers — 141%", text)

    def test_a_request_reaches_the_team_and_the_admin_panel(self):
        self.choose("en")
        self.press("r:city")
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "asking")
        self.assertTrue(self.api.last()["reply_markup"]["keyboard"][0][0]["request_contact"])
        self.say("2 people, 5 May please")
        message = models.ContactMessage.objects.get()
        self.assertIn("2 people, 5 May please", message.message)
        self.assertIn("Shahar turi", message.message)
        self.assertIn("@anna_t", message.message)
        self.assertEqual(message.subject, "Telegram: Shahar turi")
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
        self.assertIn("did not quite understand", self.api.last()["text"])  # the hint and the menu buttons are one message
        self.assertTrue(self.api.buttons())

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
        self.assertEqual((booking.travel_date.isoformat(), booking.phone, booking.estimated_total_usd), ("2099-05-01", "+4915112345", Decimal("1106.24")))  # 4 travellers: $200 x 138.28% = $276.56 each
        self.assertIn(booking.reference, self.api.texts()[-2])
        self.assertEqual(models.TelegramUser.objects.get(chat_id=77).state, "book_arrival")  # the arrival question follows; skipping it ends the booking
        self.say("⏭ Skip")
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
        self.assertIn("Telegram bot", team_alerts[0][1])
        self.assertIn("Sayt", team_alerts[1][1])  # alerts are in Uzbek
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
        self.say("2000-01-01")
        self.assertIn("already passed", self.api.texts()[-1])
        self.say("1 January 2001")
        self.assertIn("already passed", self.api.texts()[-1])
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
        self.assertNotIn("Подписывайтесь", " ".join(self.api.texts()))  # looking at a tour is not followed by an invitation any more
        self.assertEqual(self.links(), [])

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
        self.bot.handle({"message": {"chat": {"id": 5}, "from": {"first_name": "Bo", "username": "bo"}, "text": "⏭ Skip"}})
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
        self.assertTrue([b for b in self.api.sent[-1][1]["reply_markup"]["inline_keyboard"][0] if "instagram.com" in b.get("url", "")])
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


import re
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError


class WebsiteServingTests(APITestCase):
    """On a live server Django itself gives out the built website, so one process is enough."""

    def setUp(self):
        self.dist = Path(tempfile.mkdtemp())
        (self.dist / "assets").mkdir()
        (self.dist / "index.html").write_text("<!doctype html><div id=\"root\"></div>", encoding="utf-8")
        (self.dist / "assets" / "app-abc123.js").write_text("console.log(1)", encoding="utf-8")
        (self.dist / "robots-extra.txt").write_text("x", encoding="utf-8")
        self.media = Path(tempfile.mkdtemp())
        (self.media / "photo.jpg").write_bytes(b"\xff\xd8\xff")
        self.settings = override_settings(SERVE_FRONTEND=True, FRONTEND_DIST=self.dist, MEDIA_ROOT=self.media)
        self.settings.enable()
        self.addCleanup(self.settings.disable)

    def test_every_page_address_gets_the_app_so_links_and_refresh_work(self):
        for path in ("/", "/tours", "/tours/samarkand-city-tour", "/legal/privacy", "/admin/bookings", "/destinations/khorezm"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn(b'<div id="root">', b"".join(response.streaming_content), path)
            self.assertEqual(response["Cache-Control"], "no-cache")

    def test_built_files_are_cached_for_a_year_and_missing_files_are_real_404s(self):
        asset = self.client.get("/assets/app-abc123.js")
        self.assertEqual(asset.status_code, 200)
        self.assertIn("immutable", asset["Cache-Control"])
        self.assertEqual(self.client.get("/assets/old-file.js").status_code, 404)
        self.assertEqual(self.client.get("/missing.png").status_code, 404)

    def test_the_api_the_sitemap_and_unknown_api_paths_are_not_swallowed_by_the_app(self):
        self.assertEqual(self.client.get("/api/destinations/").json(), [])
        self.assertIn("application/xml", self.client.get("/sitemap.xml")["Content-Type"])
        missing = self.client.get("/api/does-not-exist/")
        self.assertEqual(missing.status_code, 404)
        self.assertNotIn(b'<div id="root">', missing.content)

    def test_photos_are_served_and_nothing_outside_the_folders_can_be_read(self):
        self.assertEqual(self.client.get("/media/photo.jpg").status_code, 200)
        for sneaky in ("/../../../etc/passwd", "/assets/../../backend/config/settings.py", "/media/../../config/settings.py", "/%2e%2e/%2e%2e/manage.py"):
            response = self.client.get(sneaky)
            self.assertNotEqual(response.status_code, 200, sneaky)
            self.assertNotIn(b"SECRET_KEY", b"".join(getattr(response, "streaming_content", [response.content])), sneaky)

    def test_it_can_be_switched_off_when_nginx_serves_the_files(self):
        with override_settings(SERVE_FRONTEND=False):
            self.assertEqual(self.client.get("/tours").status_code, 404)
            self.assertEqual(self.client.get("/media/photo.jpg").status_code, 404)

    def test_a_missing_build_says_so_instead_of_crashing(self):
        (self.dist / "index.html").unlink()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.assertIn(b"npm run build", response.content)


class SiteCheckTests(APITestCase):
    def run_check(self, **settings_override):
        out = StringIO()
        with override_settings(**settings_override):
            try:
                call_command("site_check", stdout=out)
                failed = False
            except CommandError:
                failed = True
        return out.getvalue(), failed

    def test_a_site_that_is_not_ready_is_reported_with_the_reasons(self):
        text, failed = self.run_check(DEBUG=True, SERVE_FRONTEND=True, FRONTEND_DIST=Path(tempfile.mkdtemp()), ALLOWED_HOSTS=["localhost"])
        self.assertTrue(failed)
        self.assertIn("DEBUG is ON", text)
        self.assertIn("Website not built", text)
        self.assertIn("0 published tours", text)
        self.assertIn("change the sample admin password", text)

    def test_a_ready_site_passes(self):
        dist = Path(tempfile.mkdtemp())
        (dist / "index.html").write_text("<div id=\"root\"></div>", encoding="utf-8")
        for model, kwargs in ((models.Destination, dict(slug="d", name="D", region="r", summary="s", suggested_duration="1 day")),
                              (models.Hotel, dict(slug="h", name="H", destination_name="D", summary="A real hotel", price_from_usd=50)),
                              (models.Tour, dict(slug="t", title="T", destination_name="D", category="Culture", duration_label="1 day", group_type="Small group", summary="s", price_from_usd=10))):
            model.objects.create(status="published", **kwargs)
        get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)
        models.SiteContent.objects.update_or_create(pk=1, defaults={"phone_primary": "+998901112233", "email": "info@example.com"})
        text, failed = self.run_check(DEBUG=False, SERVE_FRONTEND=True, FRONTEND_DIST=dist, SITE_URL="https://alitravel.uz", ALLOWED_HOSTS=["alitravel.uz"], SECURE_SSL_REDIRECT=True)
        self.assertFalse(failed, text)
        self.assertIn("SITE_URL = https://alitravel.uz", text)
        self.assertIn("1 published tours", text)

    def test_the_live_check_asks_the_real_website_and_reports_each_answer(self):
        def fake_fetch(self_, url, follow=True):
            answers = {"/": (200, "text/html; charset=utf-8", "<div id=\"root\">"), "/tours": (200, "text/html", "<div id=\"root\">"), "/api/destinations/": (200, "application/json", "[]"),
                       "/api/tours/": (200, "application/json", "[]"), "/api/site-content/": (200, "application/json", "{}"), "/sitemap.xml": (200, "application/xml", "<urlset"),
                       "/robots.txt": (500, "text/plain", "")}
            if url.startswith("http://"):
                return 301, "", "", url
            return (*answers[url.replace("https://alitravel.uz", "")], url)

        out = StringIO()
        from api.management.commands.site_check import Command
        with mock.patch.object(Command, "fetch", fake_fetch), override_settings(SITE_URL="https://alitravel.uz", DEBUG=False, ALLOWED_HOSTS=["alitravel.uz"]):
            with self.assertRaises(CommandError):
                call_command("site_check", "--live", stdout=out)
        text = out.getvalue()
        self.assertIn("Live website: https://alitravel.uz", text)
        self.assertIn("/sitemap.xml  ->  200 application/xml", text)
        self.assertIn("/robots.txt  ->  500", text)
        self.assertIn("redirects to https", text)


from api.management.commands import seed_hotels, seed_package, seed_package_11
from api.management.commands.seed import Command as SeedCommand, apply_translations


class HotelDirectoryTests(APITestCase):
    def seed(self):
        command = SeedCommand(stdout=StringIO())
        command.add_hotels()
        return command

    def test_the_real_hotels_are_created_once_with_photos_types_and_prices(self):
        models.Hotel.objects.create(slug="registan-heritage-boutique", name="Sample", destination_slug="samarkand", destination_name="Samarkand", summary="s", price_from_usd=78, status="published")
        self.seed()
        real = models.Hotel.objects.filter(is_demo=False)
        self.assertEqual(real.count(), len(seed_hotels.HOTELS))
        self.assertGreaterEqual(real.count(), 25)
        self.assertEqual(models.Hotel.objects.get(slug="registan-heritage-boutique").status, "archived")  # the made-up sample is put away
        self.assertTrue(all(h.image_url and len(h.gallery) >= 2 for h in real), "every hotel has a cover and at least two more photos")
        self.assertEqual({h.property_type for h in real}, {"hotel", "boutique", "guesthouse", "hostel"})
        self.assertTrue(all(h.price_basis == "bed" for h in real.filter(property_type="hostel")))
        self.assertTrue(all(h.price_basis == "room" for h in real.filter(property_type__in=["hotel", "boutique"])))
        self.assertTrue(all(h.stars == 0 for h in real.filter(property_type__in=["hostel", "guesthouse"])))
        self.assertEqual(real.filter(stars__gte=4).count() > 5, True)
        hyatt = real.get(slug="hyatt-regency-tashkent")
        self.assertIn("Hyatt_Regency", hyatt.image_url)  # a real photo of the hotel itself comes first ...
        self.assertTrue(hyatt.photos_illustrative)  # ... the rest of its gallery shows the destination, and the page says so
        lotte = real.get(slug="lotte-city-hotel-tashkent-palace")  # five photographs of the hotel itself: only those are shown
        self.assertFalse(lotte.photos_illustrative)
        self.assertTrue(all("Lotte" in u or "Buyuk_Turon" in u or "%D0%BE%D1%82%D0%B5%D0%BB" in u or "%D0%B3%D0%BE%D1%81%D1%82%D0%B8%D0%BD" in u or "Tashkent" in u for u in [lotte.image_url, *lotte.gallery]))
        khiva = real.get(slug="orient-star-khiva-hotel")  # its own rooms, courtyard and restaurant (Commons category "Orient Star Hotel (Khiva)")
        self.assertFalse(khiva.photos_illustrative)
        self.assertTrue(all("khiva15" in u or "khiva16" in u or "khiva17" in u for u in [khiva.image_url, *khiva.gallery]))
        platan = real.get(slug="hotel-platan-samarkand")  # no photos of its own: photos of similar hotels, never monuments
        self.assertTrue(platan.photos_illustrative)
        for h in real:
            for url in [h.image_url, *h.gallery]:
                self.assertFalse(any(m in url for m in ("Registan_Square", "Gur-e_Amir", "Shah-i-Zinda", "Madrasa", "Mausoleum", "Minaret", "Mosque")), f"{h.name}: {url}")
        self.assertEqual(self.seed() and models.Hotel.objects.filter(is_demo=False).count(), len(seed_hotels.HOTELS))  # nothing is created twice

    def test_each_destination_has_hotels_and_the_prices_are_sensible(self):
        self.seed()
        for destination in ("samarkand", "bukhara", "khorezm", "tashkent", "fergana", "karakalpakstan", "kashkadarya"):
            self.assertTrue(models.Hotel.objects.filter(destination_slug=destination, is_demo=False).exists(), destination)
        for h in models.Hotel.objects.filter(is_demo=False):
            self.assertTrue(3 <= h.price_from_usd <= 400, f"{h.name} {h.price_from_usd}")
            low_high = seed_hotels.RANGES.get(h.slug)
            if low_high:
                self.assertEqual(int(h.price_from_usd), low_high[0], h.name)  # the "from" price is the low end of the range seen

    def test_the_api_lists_published_hotels_with_gallery_in_the_visitors_language(self):
        self.seed()
        apply_translations()
        listing = self.client.get("/api/hotels/", HTTP_X_LANG="uz").json()
        self.assertEqual(len(listing), len(seed_hotels.HOTELS))
        platan = next(h for h in listing if h["slug"] == "hotel-platan-samarkand")
        self.assertIsInstance(platan["gallery"], list)
        self.assertTrue(platan["summary"].startswith("Samarqanddagi 4 yulduzli mehmonxona"))
        self.assertIn("$59–$93", platan["description"])
        russian = self.client.get("/api/hotels/hotel-platan-samarkand/", HTTP_X_LANG="ru").json()
        self.assertTrue(russian["summary"].startswith("Четырёхзвёздочный отель в Самарканде"))

    def test_only_admins_change_the_gallery_and_an_archived_hotel_is_hidden_from_visitors(self):
        self.seed()
        slug = "registan-hostel-samarkand"
        self.assertEqual(self.client.patch(f"/api/hotels/{slug}/", {"gallery": []}, format="json").status_code, 401)
        self.client.force_authenticate(get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True))
        photos = ["/media/uploads/a.jpg", "/media/uploads/b.jpg", "https://example.com/c.jpg"]
        done = self.client.patch(f"/api/hotels/{slug}/", {"gallery": photos, "photos_illustrative": False, "status": "archived"}, format="json")
        self.assertEqual(done.status_code, 200)
        self.assertEqual(done.json()["gallery"], photos)
        self.client.force_authenticate(None)
        self.assertNotIn(slug, [h["slug"] for h in self.client.get("/api/hotels/").json()])

    def test_admins_add_several_photos_to_a_tour_and_a_destination(self):
        call_command("seed", verbosity=0)
        photos = ["/media/uploads/a.jpg", "/media/uploads/b.jpg"]
        self.assertEqual(self.client.patch("/api/tours/samarkand-city-tour/", {"gallery": photos}, format="json").status_code, 401)
        self.client.force_authenticate(get_user_model().objects.create_user("boss2@example.com", "boss2@example.com", "x", is_staff=True))
        self.assertEqual(self.client.patch("/api/tours/samarkand-city-tour/", {"gallery": photos}, format="json").status_code, 200)
        self.assertEqual(self.client.patch("/api/destinations/samarkand/", {"gallery": photos[:1]}, format="json").status_code, 200)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/tours/samarkand-city-tour/").json()["gallery"], photos)
        self.assertEqual(self.client.get("/api/destinations/samarkand/").json()["gallery"], photos[:1])

    def test_the_packages_are_multi_city_and_an_admin_adds_any_tour_to_that_list(self):
        call_command("seed", verbosity=0)
        multi = {x["slug"] for x in self.client.get("/api/tours/").json() if x["multi_city"]}
        self.assertTrue({"silk-road-7-day-journey", "silk-road-11-day-journey", "silk-road-multi-city-tour"} <= multi)
        self.assertNotIn("samarkand-city-tour", multi)
        self.client.force_authenticate(get_user_model().objects.create_user("boss3@example.com", "boss3@example.com", "x", is_staff=True))
        self.assertTrue(self.client.patch("/api/tours/samarkand-city-tour/", {"multi_city": True}, format="json").json()["multi_city"])


class SilkRoadPackageTests(APITestCase):
    def setUp(self):
        SeedCommand(stdout=StringIO()).add_extras()
        self.admin = get_user_model().objects.create_user("owner@example.com", "owner@example.com", "pw-12345!", is_staff=True)

    def test_the_seven_day_package_follows_the_route_the_owner_asked_for(self):
        tour = models.Tour.objects.get(slug=seed_package.SLUG)
        self.assertEqual(tour.duration_label, "7 days")
        self.assertEqual([d["day"] for d in tour.itinerary], list(range(1, 8)))
        stops = [line.split("|")[0].strip() for line in tour.route]

        def visited(day):
            return [stops[i["stop"]] for i in tour.itinerary[day - 1]["items"] if i["type"] == "visit"]
        self.assertIn("Registan Square", visited(1))
        self.assertIn("Gur-e-Amir Mausoleum", visited(2))  # two days in Samarkand
        self.assertIn("Ak-Saray Palace", visited(3))  # Shahrisabz and Qarshi
        self.assertIn("Kok-Gumbaz Mosque (Qarshi)", visited(4))  # the day on the road to Bukhara
        self.assertIn("Lyabi-Hauz", visited(4))
        self.assertIn("Ark Fortress", visited(5))  # two days in Bukhara
        self.assertIn("Chor Minor", visited(6))
        self.assertIn("Rabat-i-Malik Caravanserai", visited(7))  # the way back to Samarkand
        self.assertEqual(sum(1 for d in tour.itinerary for i in d["items"] if i["type"] == "meal" and i["meal"] == "breakfast"), 6)

    def test_every_visited_place_has_a_note_and_its_own_real_photograph(self):
        tour = models.Tour.objects.get(slug=seed_package.SLUG)
        places = {models.Tour.objects.get(slug=s).route[0].split("|")[0].strip(): models.Tour.objects.get(slug=s) for s in models.Tour.objects.exclude(parent_slug="").values_list("slug", flat=True)}
        photos = set()
        for line in tour.route:
            place = places[line.split("|")[0].strip()]
            self.assertTrue(place.description and place.story, place.slug)
            self.assertIn("wikimedia.org", place.image_url, place.slug)
            self.assertNotIn(seed_package.PLACEHOLDER, place.image_url)
            photos.add(place.image_url)
        self.assertEqual(len(photos), len(tour.route), "no two places share one photograph")

    def test_texts_are_translated_and_edits_in_the_site_editor_reach_the_public_site(self):
        uz = self.client.get(f"/api/tours/{seed_package.SLUG}/", HTTP_X_LANG="uz").json()
        self.assertIn("Ipak yo'li", uz["title"])
        self.assertTrue(any("Qarshi" in line for line in uz["highlights"]))
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.patch(f"/api/tours/{seed_package.SLUG}/", {"summary": "Edited in the site editor.", "price_from_usd": "850.00"}, format="json").status_code, 200)
        self.client.force_authenticate(None)
        public = self.client.get(f"/api/tours/{seed_package.SLUG}/").json()
        self.assertEqual((public["summary"], public["price_from_usd"]), ("Edited in the site editor.", 850.0))
        listed = self.client.get("/api/tours/?has_parent=1").json()
        rows = listed["results"] if isinstance(listed, dict) else listed
        self.assertTrue(rows and all(r["parent_slug"] for r in rows))
        self.assertIn("Rabat-i-Malik Caravanserai", [r["route"][0].split("|")[0].strip() for r in rows])

    def test_the_eleven_day_journey_adds_khiva_and_every_place_has_a_photo(self):
        tour = models.Tour.objects.get(slug=seed_package_11.SLUG)
        self.assertEqual((tour.duration_label, len(tour.itinerary)), ("11 days", 11))
        stops = [line.split("|")[0].strip() for line in tour.route]
        by_day = {d["day"]: [stops[i["stop"]] for i in d["items"] if i["type"] == "visit"] for d in tour.itinerary}
        self.assertIn("Gur-e-Amir Mausoleum", by_day[2])
        self.assertIn("Ak-Saray Palace", by_day[3])
        self.assertIn("Ark Fortress", by_day[5])
        self.assertIn("Kunya-Ark Citadel (Khiva)", by_day[8])  # two days in Khiva
        self.assertIn("Pahlavon Mahmud Mausoleum (Khiva)", by_day[9])
        self.assertIn("Rabat-i-Malik Caravanserai", by_day[11])
        self.assertNotIn("Farewell dinner in Bukhara", [i.get("text") for d in tour.itinerary for i in d["items"]])
        places = {models.Tour.objects.get(slug=s).route[0].split("|")[0].strip(): models.Tour.objects.get(slug=s) for s in models.Tour.objects.exclude(parent_slug="").values_list("slug", flat=True)}
        for stop in stops:
            self.assertIn("wikimedia.org", places[stop].image_url, stop)
            self.assertTrue(places[stop].description, stop)

    def test_multi_day_tours_warn_that_better_hotels_and_a_premium_taxi_cost_extra(self):
        uz = self.client.get(f"/api/tours/{seed_package_11.SLUG}/", HTTP_X_LANG="uz").json()
        self.assertIn("qo'shimcha to'lov", uz["description"])
        self.assertIn("eng arzon mehmonxona", " ".join(uz["included"]).lower())
        from .telegram_texts import text as tx
        for lang in ("en", "uz", "ru", "fr", "de", "es"):
            self.assertTrue(tx("stay_note", lang).strip(), lang)


class ArrivalDetailsTests(APITestCase):
    def setUp(self):
        self.booking = models.BookingRequest.objects.create(service_type="tour", service_slug="city", service_title="City Tour", full_name="Anna", email="Anna@Example.com", phone="+998901234567", guests=2, lang="en")

    def post(self, **extra):
        return self.client.post("/api/bookings-arrival/", {"reference": self.booking.reference, "email": "anna@example.com", "arrival_date": "2030-05-15", "arrival_time": "14:30", "arrival_flight": "HY 123", **extra}, format="json")

    @override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="")
    def test_the_traveller_sends_the_arrival_time_after_booking_and_the_team_is_told(self):
        mail.outbox.clear()
        self.assertEqual(self.post().status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual((str(self.booking.arrival_date), self.booking.arrival_time.strftime("%H:%M"), self.booking.arrival_flight), ("2030-05-15", "14:30", "HY 123"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("14:30", mail.outbox[0].body)
        self.assertIn("HY 123", mail.outbox[0].body)

    def test_a_wrong_email_or_missing_time_is_refused(self):
        self.assertEqual(self.post(email="someone@else.com").status_code, 404)
        self.assertEqual(self.post(arrival_time="").status_code, 400)
        self.assertEqual(self.post(reference="AT-NOPE").status_code, 404)
        self.booking.refresh_from_db()
        self.assertIsNone(self.booking.arrival_date)

    def test_the_admin_sees_the_arrival_details(self):
        self.post()
        admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "pw-12345!", is_staff=True)
        self.client.force_authenticate(admin)
        row = next(b for b in (lambda d: d["results"] if isinstance(d, dict) else d)(self.client.get("/api/bookings/").json()) if b["reference"] == self.booking.reference)
        self.assertEqual((row["arrival_date"], row["arrival_time"][:5], row["arrival_flight"]), ("2030-05-15", "14:30", "HY 123"))


class MigrationsTests(APITestCase):
    def test_every_model_change_has_a_migration(self):
        """A model field without a migration breaks booking on a server whose database was not migrated (NOT NULL errors)."""
        call_command("makemigrations", check=True, dry_run=True, verbosity=0)

    def test_a_booking_request_of_every_kind_is_accepted(self):
        for kind in ("tour", "hotel", "transport", "plan", "selection"):
            answer = self.client.post("/api/bookings-submit/", {"service_type": kind, "service_slug": "x", "service_title": "Something", "full_name": "Anna Test", "email": f"{kind}@example.com", "phone": "+998901234567",
                                                                "travel_date": "2031-02-01", "end_date": None, "guests": 2, "details_summary": "", "special_requests": "", "estimated_total_usd": 123.4, "website": ""}, format="json")
            self.assertEqual(answer.status_code, 201, (kind, answer.content))
            self.assertTrue(answer.json()["reference"].startswith("AT-"))


class AutomaticCostTests(APITestCase):
    """Costs are added by themselves when a booking is confirmed; what is left of the price is the profit."""

    def setUp(self):
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)
        self.api = APIClient()
        self.api.force_authenticate(self.admin)
        self.tour = models.Tour.objects.create(
            slug="week", title="Week", destination_name="Samarkand", category="Culture", duration_label="3 days", group_type="Small group", summary="s",
            price_from_usd=300, tickets_included=True, route=["Registan | 16", "Bibi-Khanym | 9"], itinerary=[{"day": 1, "items": []}, {"day": 2, "items": []}, {"day": 3, "items": []}])
        self.booking = models.BookingRequest.objects.create(
            service_type="tour", service_slug="week", service_title="Week", full_name="Ann", email="a@b.co", phone="+998901234567",
            travel_date=date(2030, 5, 1), guests=5, estimated_total_usd=2000)

    def costs(self):
        return {e.category: e.amount_usd for e in self.booking.expenses.all()}

    def test_a_pending_booking_has_no_costs_and_confirming_adds_them(self):
        self.assertEqual(self.costs(), {})
        self.booking.status = "confirmed"
        self.booking.save()
        # 5 guests, 3 days: guide 3 x 30, 2 cars x 3 days x 60, 2 nights x 3 rooms x 25, tickets (16 + 9) x 5
        self.assertEqual(self.costs(), {"guide": Decimal("90.00"), "transport": Decimal("360.00"), "hotel": Decimal("150.00"), "tickets": Decimal("125.00")})
        row = self.api.get("/api/accounting/ledger/?status=confirmed").json()[0]
        self.assertEqual((row["costs"], row["profit"]), (725, 1275))  # what is left is the profit

    def test_cancelling_removes_the_automatic_costs_but_not_the_ones_added_by_hand(self):
        self.booking.status = "confirmed"
        self.booking.save()
        models.Expense.objects.create(booking=self.booking, category="other", description="Gift", amount_usd=10)
        self.booking.status = "cancelled"
        self.booking.save()
        self.assertEqual(list(self.costs()), ["other"])

    def test_an_edited_cost_is_not_overwritten_and_changing_the_rates_recalculates(self):
        self.booking.status = "confirmed"
        self.booking.save()
        guide = self.booking.expenses.get(category="guide")
        self.assertEqual(self.api.patch(f"/api/expenses/{guide.id}/", {"amount_usd": "200"}, format="json").status_code, 200)
        self.assertFalse(self.booking.expenses.get(category="guide").auto)
        self.assertEqual(self.api.put("/api/accounting/rates/", {"car_per_day": 100}, format="json").json()["car_per_day"], 100)
        self.assertEqual(self.costs()["transport"], Decimal("600.00"))  # 2 cars x 3 days x 100
        self.assertEqual(self.costs()["guide"], Decimal("200.00"))  # the hand-edited cost stays

    def test_hotel_and_transport_bookings_cost_a_share_of_their_price(self):
        stay = models.BookingRequest.objects.create(service_type="hotel", service_title="Hotel", full_name="Bo", email="b@b.co", phone="+998901234567", guests=2, estimated_total_usd=100, status="confirmed")
        self.assertEqual({e.category: e.amount_usd for e in stay.expenses.all()}, {"hotel": Decimal("80.00")})
        ride = models.BookingRequest.objects.create(service_type="transport", service_title="Car", full_name="Cy", email="c@b.co", phone="+998901234567", guests=2, estimated_total_usd=100, status="completed")
        self.assertEqual({e.category: e.amount_usd for e in ride.expenses.all()}, {"transport": Decimal("75.00")})

    def test_rates_are_for_staff_only_and_must_be_numbers(self):
        self.assertEqual(APIClient().get("/api/accounting/rates/").status_code in (401, 403), True)
        self.assertEqual(self.api.put("/api/accounting/rates/", {"guide_per_day": "abc"}, format="json").status_code, 400)
        self.assertEqual(self.api.put("/api/accounting/rates/", {"guide_per_day": -1}, format="json").status_code, 400)


class AdminDeskTests(APITestCase):
    """Enquiry buttons, the customers list with Telegram, extra contact lines and the exact places of the tours."""

    def setUp(self):
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)
        self.api = APIClient()
        self.api.force_authenticate(self.admin)

    def test_the_team_can_mark_an_enquiry_read_and_replied(self):
        message = models.ContactMessage.objects.create(full_name="Anna", email="a@b.co", message="Hello")
        for status in ("read", "replied", "new"):
            answer = self.api.patch(f"/api/messages/{message.id}/", {"status": status}, format="json")
            self.assertEqual(answer.status_code, 200)
            message.refresh_from_db()
            self.assertEqual(message.status, status)
        # the public contact form still cannot choose its own status
        self.client.post("/api/contact/", {"full_name": "Bo", "email": "bo@b.co", "message": "Hi there", "status": "replied"}, format="json")
        self.assertEqual(models.ContactMessage.objects.get(email="bo@b.co").status, "new")

    def test_customers_include_accounts_guests_and_telegram_people_with_their_bookings(self):
        get_user_model().objects.create_user("acc@example.com", "acc@example.com", "x", first_name="Acc")
        models.BookingRequest.objects.create(service_type="tour", service_title="City", full_name="Guest", email="guest@example.com", phone="+998901111111", guests=2, estimated_total_usd=300)
        models.TelegramUser.objects.create(chat_id=77, lang="uz", first_name="Anna", username="anna_t")
        models.BookingRequest.objects.create(service_type="tour", service_title="Khiva", full_name="Anna", email="telegram-77@telegram.invalid", phone="+998902222222", guests=3,
                                             estimated_total_usd=900, telegram_chat_id=77, arrival_note="15 May 14:30 HY 123")
        models.TelegramUser.objects.create(chat_id=88, lang="en", first_name="Silent")
        people = {p["key"]: p for p in self.api.get("/api/customers/").json()}
        telegram = people["telegram-77"]
        self.assertEqual((telegram["kind"], telegram["username"], telegram["bookings"], telegram["total_usd"]), ("telegram", "anna_t", 1, 900))
        self.assertIn("HY 123", telegram["recent_bookings"][0]["arrival"])
        self.assertEqual(people["telegram-88"]["bookings"], 0)  # someone who only chatted
        self.assertEqual((people["guest-guest@example.com"]["kind"], people["guest-guest@example.com"]["bookings"]), ("guest", 1))
        self.assertTrue(any(p["kind"] == "account" and p["email"] == "acc@example.com" for p in people.values()))
        self.assertEqual(APIClient().get("/api/customers/").status_code in (401, 403), True)

    def test_extra_contact_lines_are_saved_cleaned_and_shown_publicly_while_the_cost_rates_stay_private(self):
        lines = [{"label": " WhatsApp ", "value": "+998 90 123 45 67", "url": "https://wa.me/998901234567"}, {"label": "", "value": "", "url": ""}, {"label": "Licence", "value": "No. 123", "url": ""}]
        self.assertEqual(self.api.put("/api/site-content/", {"extra_contacts": lines}, format="json").status_code, 200)
        public = APIClient().get("/api/site-content/").json()
        self.assertEqual(public["extra_contacts"], [{"label": "WhatsApp", "value": "+998 90 123 45 67", "url": "https://wa.me/998901234567"}, {"label": "Licence", "value": "No. 123", "url": ""}])
        self.assertNotIn("cost_rates", public)
        self.assertEqual(self.api.put("/api/site-content/", {"extra_contacts": [{"label": "x", "value": "y", "url": "javascript:alert(1)"}]}, format="json").status_code, 400)
        self.assertEqual(self.api.put("/api/site-content/", {"extra_contacts": [{"label": "x", "value": "y"}] * 21}, format="json").status_code, 400)
        self.assertEqual(APIClient().put("/api/site-content/", {"extra_contacts": []}, format="json").status_code, 403)

    def test_every_place_of_the_seeded_tours_has_an_exact_location_inside_uzbekistan(self):
        SeedCommand(stdout=StringIO()).add_extras()
        places = models.Tour.objects.exclude(parent_slug="")
        self.assertGreaterEqual(places.count(), 35)
        for place in places:
            self.assertIsNotNone(place.latitude, place.slug)
            self.assertTrue(37 <= place.latitude <= 45.7 and 55.9 <= place.longitude <= 73.2, (place.slug, place.latitude, place.longitude))
        uz = self.client.get("/api/tours/rishton-ceramics/", HTTP_X_LANG="uz").json()
        self.assertIn("shahar markazi", uz["location_note"])  # an approximate position says so, in the reader's language
        self.assertEqual(self.client.get("/api/tours/registan-square/").json()["location_note"], "")


@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="", SITE_URL="https://alitravel.example")
class TelegramLessClutterTests(APITestCase):
    """Buttons edit their own message, the date can be written in any form, and a task ends with the menu under its last message."""

    def setUp(self):
        self.api = FakeTelegram()
        self.bot = Bot(self.api)
        models.Tour.objects.create(slug="city", title="City Tour", destination_slug="samarkand", destination_name="Samarkand", category="Culture", duration_label="2 days",
                                   group_type="Small group", summary="A fine tour.", price_from_usd=200, status="published", image_url="https://example.com/photo.jpg")
        models.Destination.objects.create(slug="samarkand", name="Samarkand", region="Silk Road", summary="Domes.", suggested_duration="3 days", status="published")

    def say(self, text="", **extra):
        self.bot.handle({"message": {"chat": {"id": 5}, "from": {"first_name": "Bo", "username": "bo"}, "text": text, **extra}})

    def press(self, data, message_id=321):
        self.bot.handle({"callback_query": {"id": "1", "data": data, "from": {"first_name": "Bo", "username": "bo"}, "message": {"chat": {"id": 5}, "message_id": message_id}}})

    def start(self):
        self.say("/start")
        self.press("lang:en")
        self.api.sent.clear()

    def methods(self):
        return [m for m, _ in self.api.sent if m != "answerCallbackQuery"]

    def test_navigation_buttons_edit_the_message_instead_of_sending_new_ones(self):
        self.start()
        self.press("dests")
        self.press("tours")
        self.press("t:city")
        self.press("menu")
        self.assertEqual(self.methods(), ["editMessageText"] * 4)
        self.assertEqual({p["message_id"] for m, p in self.api.sent if m == "editMessageText"}, {321})
        shown = [p for m, p in self.api.sent if "City Tour" in p.get("text", "")][0]
        self.assertEqual(shown["link_preview_options"]["url"], "https://example.com/photo.jpg")  # the picture is part of the same message

    def test_the_first_menu_after_the_language_choice_replaces_the_language_message(self):
        self.say("/start")
        self.api.sent.clear()
        self.press("lang:uz")
        self.assertEqual(self.methods(), ["editMessageText"])
        self.assertIn("xush kelibsiz", [p for m, p in self.api.sent if m == "editMessageText"][0]["text"])

    def test_a_message_that_cannot_be_edited_is_sent_as_a_new_one(self):
        self.start()
        original = self.api.__call__

        def failing(method, payload=None):
            if method == "editMessageText":
                raise RuntimeError("Bad Request: message can't be edited")
            return original(method, payload)
        self.bot.call = failing
        self.press("dests")
        self.assertIn("sendMessage", self.methods())

    def book(self, date_text):
        self.start()
        self.press("b:city")
        self.say(date_text)
        self.say("2")
        self.say(contact={"phone_number": "+998901234567"})
        return models.BookingRequest.objects.get(telegram_chat_id=5)

    def test_the_date_can_be_written_in_any_form(self):
        from api.telegram_bot import read_date
        import datetime
        for text in ("2099-05-01", "01.05.2099", "1/5/2099", "1 May 2099", "May 1 2099", "1 may 2099", "1 мая 2099", "1er mai 2099", "1 de mayo de 2099", "1. Mai 2099"):
            self.assertEqual(read_date(text), ("ok", datetime.date(2099, 5, 1)), text)
        self.assertEqual(read_date("tomorrow")[1], datetime.date.today() + datetime.timedelta(days=1))
        self.assertEqual(read_date("bugun")[1], datetime.date.today())
        self.assertGreaterEqual(read_date("15.05")[1], datetime.date.today())  # no year: the next time this day comes
        self.assertEqual(read_date("1 January 2001"), ("past", None))
        self.assertEqual(read_date("sometime in summer"), ("text", None))

    def test_a_date_that_is_not_a_date_is_kept_as_written_and_the_team_is_told_to_confirm_it(self):
        booking = self.book("sometime in summer")
        self.assertIsNone(booking.travel_date)
        self.assertIn("sometime in summer", booking.details_summary)

    def test_the_date_can_be_left_for_later(self):
        self.start()
        self.press("b:city")
        self.assertIn("🗓 I will tell the date later", [b["text"] for row in self.api.last()["reply_markup"]["keyboard"] for b in row])
        self.say("🗓 I will tell the date later")
        self.say("3")
        self.say(contact={"phone_number": "+998901234567"})
        booking = models.BookingRequest.objects.get(telegram_chat_id=5)
        self.assertIsNone(booking.travel_date)
        self.assertIn("Sana hali yo'q", booking.details_summary)

    def test_after_a_finished_booking_the_last_message_has_only_the_social_network_buttons(self):
        models.SiteContent.objects.update_or_create(pk=1, defaults={"instagram_url": "https://www.instagram.com/al1_travel1", "youtube_url": "https://youtube.com/@alitravel_z", "telegram_url": "", "facebook_url": ""})
        self.book("2099-05-01")
        self.say("⏭ Skip")
        buttons = [b for row in self.api.last()["reply_markup"]["inline_keyboard"] for b in row]
        self.assertEqual([b.get("url") for b in buttons], ["https://www.instagram.com/al1_travel1", "https://youtube.com/@alitravel_z"])  # nothing but links to the networks
        self.assertFalse([b for b in buttons if b.get("callback_data")])
        self.assertIn("Follow ALI TRAVEL", self.api.last()["text"])
        self.assertNotIn("editMessageReplyMarkup", [m for m, _ in self.api.sent])

    def test_a_task_without_an_invitation_ends_with_just_its_thanks_and_no_menu_message(self):
        self.start()
        self.press("ask")
        self.say("Hello, a question")
        self.assertEqual(self.methods()[-1], "sendMessage")
        self.assertIn("Thank you", self.api.last()["text"])
        self.assertNotIn("inline_keyboard", self.api.last().get("reply_markup", {}))
        self.assertNotIn("Menu", " ".join(p.get("text", "") for m, p in self.api.sent))



@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="", SITE_URL="https://alitravel.example")
class TelegramCustomerDetailsTests(APITestCase):
    """People who order in the bot are kept in Customers with their name and phone number."""

    def setUp(self):
        self.api = FakeTelegram()
        self.bot = Bot(self.api)
        models.Tour.objects.create(slug="city", title="City Tour", destination_slug="samarkand", destination_name="Samarkand", category="Culture", duration_label="2 days",
                                   group_type="Small group", summary="A fine tour.", price_from_usd=200, status="published")
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)

    def say(self, text="", **extra):
        self.bot.handle({"message": {"chat": {"id": 9}, "from": {"first_name": "Bo✨", "last_name": "Karim", "username": "bo_k"}, "text": text, **extra}})

    def customer(self):
        client = APIClient()
        client.force_authenticate(self.admin)
        return next(p for p in client.get("/api/customers/").json() if p["key"] == "telegram-9")

    def test_a_shared_contact_saves_the_name_and_number_and_they_show_in_customers(self):
        self.say("/start")
        self.bot.handle({"callback_query": {"id": "1", "data": "lang:uz", "from": {"first_name": "Bo✨"}, "message": {"chat": {"id": 9}, "message_id": 5}}})
        self.bot.handle({"callback_query": {"id": "2", "data": "b:city", "from": {"first_name": "Bo✨"}, "message": {"chat": {"id": 9}, "message_id": 6}}})
        for answer in ("2099-05-01", "2"):
            self.say(answer)
        self.say(contact={"phone_number": "+998901234567", "first_name": "Karim", "last_name": "Bobomurodov"})
        person = models.TelegramUser.objects.get(chat_id=9)
        self.assertEqual((person.phone, person.contact_name, person.last_name), ("+998901234567", "Karim Bobomurodov", "Karim"))
        booking = models.BookingRequest.objects.get(telegram_chat_id=9)
        self.assertEqual((booking.full_name, booking.phone), ("Karim Bobomurodov", "+998901234567"))
        row = self.customer()
        self.assertEqual((row["name"], row["phone"], row["username"], row["bookings"]), ("Karim Bobomurodov", "+998901234567", "bo_k", 1))

    def test_a_typed_number_is_kept_too_and_the_profile_name_is_used_without_a_contact(self):
        self.say("/start")
        self.bot.handle({"callback_query": {"id": "1", "data": "lang:en", "from": {"first_name": "Bo✨"}, "message": {"chat": {"id": 9}, "message_id": 5}}})
        self.bot.handle({"callback_query": {"id": "2", "data": "b:city", "from": {"first_name": "Bo✨"}, "message": {"chat": {"id": 9}, "message_id": 6}}})
        for answer in ("2099-05-01", "3", "+998 90 111 22 33"):
            self.say(answer)
        row = self.customer()
        self.assertEqual((row["name"], row["phone"]), ("Bo✨ Karim", "+998 90 111 22 33"))
        self.assertEqual(models.BookingRequest.objects.get(telegram_chat_id=9).full_name, "Bo✨ Karim")


class ConfirmationContactTests(APITestCase):
    def test_the_confirmation_points_to_telegram_and_the_e_mail_not_whatsapp(self):
        from .notifications import _booking_data, _traveller_text
        models.SiteContent.objects.update_or_create(pk=1, defaults={"telegram_url": "https://t.me/al1_travel1", "email": "alitravel004@gmail.com"})
        booking = models.BookingRequest.objects.create(service_type="tour", service_title="City", full_name="Anna", email="a@b.co", phone="+998901234567", guests=2, status="confirmed", lang="uz")
        for kind in ("received", "confirmed", "cancelled"):
            for lang in ("en", "uz", "ru"):
                booking.lang = lang
                subject, body = _traveller_text(kind, _booking_data(booking))
                self.assertNotIn("WhatsApp", body, (kind, lang))
                if kind != "received":
                    self.assertIn("https://t.me/al1_travel1", body, (kind, lang))
                    self.assertIn("alitravel004@gmail.com", body, (kind, lang))
                    self.assertIn("📞 +998942222498", body, (kind, lang))  # the phone number is there too


@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="", SITE_URL="https://alitravel.example")
class TelegramTourInfoTests(APITestCase):
    """The bot shows what the website shows about a tour, and the team's alerts use the Uzbek tour names."""

    def setUp(self):
        self.api = FakeTelegram()
        self.bot = Bot(self.api)
        self.tour = models.Tour.objects.create(
            slug="week", title="Silk Road Week", destination_slug="samarkand", destination_name="Samarkand", category="Culture", duration_label="3 days", group_type="Small group",
            summary="A week.", description="Walk and ride through the highlights.", price_from_usd=300, tour_type="car", max_travelers=21, languages=["English", "Uzbek"],
            transport_included=True, tickets_included=False, pickup_included=True, guide="ALI TRAVEL team", meeting_point="Samarkand airport", group_pricing=True,
            route=["Registan | 16", "Bibi-Khanym | 9"], included=["Guide"], excluded=["Lunch"], story="Remember this.", status="published",
            itinerary=[{"day": 1, "items": [{"time": "09:00", "type": "visit", "stop": 0}, {"time": "13:00", "type": "meal", "meal": "lunch", "included": False}]},
                       {"day": 2, "items": [{"time": "10:00", "type": "visit", "stop": 1}]}, {"day": 3, "items": []}],
            i18n={"uz": {"title": "Ipak yo'li haftasi", "route": ["Registon | 16", "Bibixonim | 9"], "included": ["Gid"], "excluded": ["Tushlik"]}})
        models.Tour.objects.create(slug="registan", title="Registan Tour", destination_name="Samarkand", category="Culture", duration_label="Flexible hours", group_type="Small group",
                                   summary="The heart of Samarkand.", price_from_usd=0, parent_slug="week", entrance_fee_usd=16, route=["Registan | 16"], latitude=39.654722, longitude=66.975556,
                                   location_note="", status="published")
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)

    def press(self, data):
        self.bot.handle({"callback_query": {"id": "1", "data": data, "from": {"first_name": "Bo", "username": "bo"}, "message": {"chat": {"id": 5}, "message_id": 77}}})

    def start(self, lang="uz"):
        self.bot.handle({"message": {"chat": {"id": 5}, "from": {"first_name": "Bo", "username": "bo"}, "text": "/start"}})
        self.press(f"lang:{lang}")
        self.api.sent.clear()

    def shown(self):
        return [p for m, p in self.api.sent if m == "editMessageText"][-1]

    def test_a_tour_has_buttons_for_its_details_plan_places_and_group_prices(self):
        self.start()
        self.press("t:week")
        callbacks = [b.get("callback_data") for row in self.shown()["reply_markup"]["inline_keyboard"] for b in row]
        for wanted in ("ti:week", "tp:week:0", "tl:week", "tg:week", "b:week"):
            self.assertIn(wanted, callbacks)

    def test_details_list_the_facts_included_and_not_included(self):
        self.start()
        self.press("ti:week")
        text = self.shown()["text"]
        for part in ("Mashinada tur", "21 kishigacha", "✅ kiradi", "❌ kirmaydi", "Samarkand airport", "Gid", "Tushlik", "Remember this"):
            self.assertIn(part, text)
        self.assertIn("eng arzon mehmonxonalar", text)  # a multi-day tour includes the most affordable hotels

    def test_the_day_plan_shows_every_day_with_times_places_and_tickets(self):
        self.start()
        self.press("tp:week:0")
        text = self.shown()["text"]
        for part in ("1-kun", "09:00", "Registon", "🎫 $16", "Tushlik ❌", "2-kun", "Bibixonim", "3-kun"):
            self.assertIn(part, text)

    def test_places_have_map_links_and_the_whole_route_is_one_button(self):
        models.Tour.objects.create(slug="bibi", title="Bibi Tour", destination_name="Samarkand", category="Culture", duration_label="Flexible hours", group_type="Small group", summary="s",
                                   price_from_usd=0, parent_slug="week", entrance_fee_usd=9, route=["Bibi-Khanym | 9"], latitude=39.660556, longitude=66.979167, status="published")
        self.start()
        self.press("tl:week")
        payload = self.shown()
        self.assertIn("google.com/maps/search/?api=1&query=39.654722,66.975556", payload["text"])
        urls = [b.get("url") for row in payload["reply_markup"]["inline_keyboard"] for b in row if b.get("url")]
        self.assertTrue(any("maps/dir/?api=1&origin=39.654722,66.975556&destination=39.660556,66.979167" in u for u in urls))

    def test_the_price_falls_as_the_group_grows(self):
        self.start()
        self.press("tg:week")
        text = self.shown()["text"]
        prices = [float(x) for x in re.findall(r"— \$([\d,.]+) / kishi", text)]
        self.assertGreaterEqual(len(prices), 5)
        self.assertEqual(prices, sorted(prices, reverse=True))  # 1 traveller pays most, 14+ least
        self.assertEqual(prices[-1], 300)  # the listed price is for 14 or more

    def test_a_single_place_shows_its_location_and_leads_to_its_tour_not_to_a_booking(self):
        self.start()
        self.press("t:registan")
        payload = self.shown()
        self.assertIn("maps/search/?api=1&query=39.654722,66.975556", payload["text"])
        self.assertIn("alohida bron qilib bo'lmaydi", payload["text"])
        callbacks = [b.get("callback_data") for row in payload["reply_markup"]["inline_keyboard"] for b in row]
        self.assertIn("t:week", callbacks)
        self.assertNotIn("b:registan", callbacks)

    def test_the_teams_alerts_use_the_uzbek_tour_name(self):
        from .notifications import _booking_html, _booking_data
        booking = models.BookingRequest.objects.create(service_type="tour", service_slug="week", service_title="Silk Road Week", full_name="Anna", email="a@b.co", phone="+998901234567", guests=2)
        self.assertIn("Ipak yo'li haftasi", _booking_html(_booking_data(booking)))
        self.assertNotIn("Silk Road Week", _booking_html(_booking_data(booking)))

    def test_the_packages_get_cheaper_per_person_in_bigger_groups(self):
        SeedCommand(stdout=StringIO()).add_extras()
        for slug in ("silk-road-7-day-journey", "silk-road-11-day-journey", "samarkand-city-tour"):
            self.assertTrue(models.Tour.objects.get(slug=slug).group_pricing, slug)


@override_settings(NOTIFY_ASYNC=False, NOTIFY_EMAILS=["team@example.com"], TELEGRAM_BOT_TOKEN="", TELEGRAM_CHAT_ID="", SITE_URL="https://alitravel.example")
class UzbekNamesForTheTeamTests(APITestCase):
    def setUp(self):
        self.tour = models.Tour.objects.create(slug="week", title="Silk Road Week", destination_name="Samarkand", category="Culture", duration_label="3 days", group_type="Small group",
                                               summary="s", price_from_usd=300, status="published", i18n={"uz": {"title": "Ipak yo'li haftasi"}})
        self.booking = models.BookingRequest.objects.create(service_type="tour", service_slug="week", service_title="Silk Road Week", full_name="Anna", email="a@b.co", phone="+998901234567",
                                                            guests=2, estimated_total_usd=600, status="completed")
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)
        self.api = APIClient()
        self.api.force_authenticate(self.admin)

    def test_the_admin_sees_the_booked_tour_in_the_language_of_the_admin_panel(self):
        row = self.api.get("/api/bookings/", HTTP_X_LANG="uz").json()
        row = (row["results"] if isinstance(row, dict) else row)[0]
        self.assertEqual((row["service_title"], row["service_title_local"]), ("Silk Road Week", "Ipak yo'li haftasi"))
        ledger = self.api.get("/api/accounting/ledger/", HTTP_X_LANG="uz").json()[0]
        self.assertEqual(ledger["service_title_local"], "Ipak yo'li haftasi")
        self.assertEqual(self.api.get("/api/bookings/").json()[0]["service_title_local"] if isinstance(self.api.get("/api/bookings/").json(), list) else "Silk Road Week", "Silk Road Week")

    def test_a_question_asked_in_the_bot_reaches_the_admin_in_uzbek_with_the_uzbek_tour_name(self):
        api = FakeTelegram()
        bot = Bot(api)
        say = lambda text="", **extra: bot.handle({"message": {"chat": {"id": 3}, "from": {"first_name": "Bo"}, "text": text, **extra}})
        say("/start")
        bot.handle({"callback_query": {"id": "1", "data": "lang:en", "from": {"first_name": "Bo"}, "message": {"chat": {"id": 3}, "message_id": 1}}})
        bot.handle({"callback_query": {"id": "2", "data": "r:week", "from": {"first_name": "Bo"}, "message": {"chat": {"id": 3}, "message_id": 2}}})
        say("What is the price for 5 people?")
        message = models.ContactMessage.objects.get()
        self.assertEqual(message.subject, "Telegram: Ipak yo'li haftasi")
        self.assertIn("Tur: Ipak yo'li haftasi", message.message)

    def test_the_invitation_is_sent_even_when_the_thanks_could_not_be_sent(self):
        models.SiteContent.objects.update_or_create(pk=1, defaults={"instagram_url": "https://www.instagram.com/al1_travel1"})
        api = FakeTelegram()
        original = api.__call__
        calls = {"n": 0}

        def flaky(method, payload=None):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("Bad Request")
            return original(method, payload)
        Bot(flaky).end_flow(5, "en", "✅ Thank you", follow="Follow ALI TRAVEL")
        self.assertEqual([p["text"] for m, p in api.sent if m == "sendMessage"], ["Follow ALI TRAVEL"])


class SilkRoadMapSettingsTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "x", is_staff=True)
        self.api = APIClient()
        self.api.force_authenticate(self.admin)

    def test_samarkand_bukhara_and_shahrisabz_are_green_from_the_start_and_everyone_can_read_it(self):
        cities = APIClient().get("/api/site-content/").json()["map_cities"]
        self.assertEqual({k for k, v in cities.items() if v["green"]}, {"samarkand", "bukhara", "shahrisabz"})

    def test_the_owner_marks_another_city_green_and_chooses_where_a_click_leads(self):
        chosen = {"samarkand": {"green": True, "target": ""}, "khiva": {"green": True, "target": "/tours/silk-road-11-day-journey"}, "qarshi": {"green": True, "target": "/destinations/kashkadarya#tours"}}
        self.assertEqual(self.api.put("/api/site-content/", {"map_cities": chosen}, format="json").status_code, 200)
        self.assertEqual(APIClient().get("/api/site-content/").json()["map_cities"], chosen)

    def test_a_link_to_another_website_or_a_bad_city_is_refused_and_only_staff_can_change_it(self):
        for bad in ({"khiva": {"green": True, "target": "https://evil.example/"}}, {"khiva": {"green": True, "target": "javascript:alert(1)"}}, {"Khiva!": {"green": True, "target": ""}}, ["khiva"]):
            self.assertEqual(self.api.put("/api/site-content/", {"map_cities": bad}, format="json").status_code, 400, bad)
        self.assertEqual(APIClient().put("/api/site-content/", {"map_cities": {}}, format="json").status_code, 403)

    def test_the_owner_adds_a_city_of_their_own_with_its_place_on_the_map(self):
        city = {"name": "Zomin", "lat": "39.96", "lon": 68.4, "side": "right", "green": True, "target": "/tours/silk-road-7-day-journey"}
        self.assertEqual(self.api.put("/api/site-content/", {"map_cities": {"c-abc123": city, "c-empty1": {"name": "", "lat": "", "lon": "", "green": True, "target": ""}}}, format="json").status_code, 200)
        saved = APIClient().get("/api/site-content/").json()["map_cities"]
        self.assertEqual(saved["c-abc123"], {"green": True, "target": "/tours/silk-road-7-day-journey", "name": "Zomin", "lat": 39.96, "lon": 68.4, "side": "right"})
        self.assertNotIn("c-empty1", saved)  # a row left empty is dropped

    def test_a_city_outside_uzbekistan_or_without_numbers_is_refused(self):
        for bad in ({"name": "Paris", "lat": 48.85, "lon": 2.35}, {"name": "Nowhere", "lat": "abc", "lon": 66}, {"name": "x" * 41, "lat": 40, "lon": 66}):
            answer = self.api.put("/api/site-content/", {"map_cities": {"c-bad001": dict(bad, green=True, target="")}}, format="json")
            self.assertEqual(answer.status_code, 400, bad)

    def test_a_tour_can_be_a_green_dot_on_the_map_and_its_dot_leads_to_that_tour(self):
        dot = {"name": "Nurota", "lat": 40.56, "lon": 65.69, "side": "above", "green": True, "target": "/tours/nurata-mountains-cultural-journey"}
        key = "t-nurata-mountains-cultural-journey"[:30]
        self.assertEqual(self.api.put("/api/site-content/", {"map_cities": {key: dot}}, format="json").status_code, 200)
        self.assertEqual(APIClient().get("/api/site-content/").json()["map_cities"][key]["target"], dot["target"])
        dot_without_place = dict(dot, lat="", lon="")
        self.assertEqual(self.api.put("/api/site-content/", {"map_cities": {key: dot_without_place}}, format="json").status_code, 400)


@override_settings(TELEGRAM_BOT_TOKEN="123:abc", TELEGRAM_CHAT_ID="", SITE_URL="https://alitravel.example", SECURE_SSL_REDIRECT=False)
class TelegramWebhookTests(APITestCase):
    """The live server gets bot messages from Telegram over https instead of polling."""

    def post(self, update, secret=None):
        from .telegram_bot import webhook_secret
        import json as _json
        headers = {"HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN": webhook_secret() if secret is None else secret}
        return self.client.generic("POST", "/api/telegram/webhook/", _json.dumps(update), content_type="application/json", **headers)

    def test_a_call_without_the_secret_is_refused_and_nothing_is_sent(self):
        from unittest import mock
        api = FakeTelegram()
        with mock.patch("api.telegram_webhook.make_call", return_value=api):
            self.assertEqual(self.post({"message": {"chat": {"id": 5}, "from": {}, "text": "/start"}}, secret="wrong").status_code, 403)
        self.assertEqual(api.sent, [])

    def test_start_sent_through_the_webhook_is_answered_with_the_language_choice(self):
        from unittest import mock
        api = FakeTelegram()
        with mock.patch("api.telegram_webhook.make_call", return_value=lambda method, payload=None: api(method, payload)):
            response = self.post({"update_id": 1, "message": {"chat": {"id": 5}, "from": {"first_name": "Ali"}, "text": "/start"}})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(api.texts())
        self.assertIn("lang:uz", [b["callback_data"] for b in api.buttons()])

    def test_a_broken_update_still_gets_200_so_telegram_does_not_resend_it_forever(self):
        from unittest import mock
        def boom(method, payload=None):
            raise RuntimeError("telegram down")
        with mock.patch("api.telegram_webhook.make_call", return_value=boom):
            self.assertEqual(self.post({"update_id": 2, "message": {"chat": {"id": 5}, "from": {}, "text": "/start"}}).status_code, 200)

    def test_polling_refuses_to_start_while_the_website_has_the_webhook(self):
        from unittest import mock
        from django.core.management import call_command
        from django.core.management.base import CommandError
        calls = []
        def fake(method, payload=None, timeout=20):
            calls.append(method)
            return {"getMe": {"username": "alitraveluzbot"}, "getWebhookInfo": {"url": "https://alitravel.example/api/telegram/webhook/"}}.get(method, True)
        with mock.patch("api.management.commands.telegram_bot.make_call", return_value=fake):
            with self.assertRaises(CommandError):
                call_command("telegram_bot", "--once")
        self.assertNotIn("deleteWebhook", calls)

    def test_webhook_mode_registers_the_site_address_with_the_secret(self):
        from unittest import mock
        from django.core.management import call_command
        from .telegram_bot import webhook_secret
        calls = []
        def fake(method, payload=None, timeout=20):
            calls.append((method, payload))
            return {"getMe": {"username": "alitraveluzbot"}, "getWebhookInfo": {"url": ""}}.get(method, True)
        with mock.patch("api.management.commands.telegram_bot.make_call", return_value=fake):
            call_command("telegram_bot", "--webhook", "--once", stdout=__import__("io").StringIO())
        hook = [p for m, p in calls if m == "setWebhook"][0]
        self.assertEqual(hook["url"], "https://alitravel.example/api/telegram/webhook/")
        self.assertEqual(hook["secret_token"], webhook_secret())

    def test_watch_site_warns_only_when_something_is_wrong(self):
        """The daily check is silent while the certificate is fresh and the domain points here, and tells the team otherwise."""
        from unittest import mock
        from django.core.management import call_command
        from django.test import override_settings
        cmd = "api.management.commands.watch_site"
        cases = [(80, "52.65.166.20", 0), (10, "52.65.166.20", 1), (80, "3.107.3.123", 1), (None, "52.65.166.20", 1)]
        for days, pointed, alerts in cases:
            with override_settings(SITE_URL="https://alitravel.uz"), \
                 mock.patch(f"{cmd}.certificate_days_left", return_value=days), \
                 mock.patch(f"{cmd}.own_address", return_value="52.65.166.20"), \
                 mock.patch(f"{cmd}.socket.gethostbyname", return_value=pointed), \
                 mock.patch(f"{cmd}.notifications._tell_the_team") as tell:
                call_command("watch_site", stdout=__import__("io").StringIO())
            self.assertEqual(tell.call_count, alerts, (days, pointed))
            if alerts:
                self.assertIn("ALI TRAVEL", tell.call_args.kwargs["telegram_html"])

    def test_webhook_follows_the_server_to_its_new_address(self):
        """After the server's IP changes, Telegram still calls the old one until the webhook is set again with the new address."""
        from unittest import mock
        from django.core.management import call_command
        url = "https://alitravel.example/api/telegram/webhook/"
        for telegram_ip, expect_reset in (("3.107.3.123", True), ("52.65.166.20", False)):
            calls = []
            def fake(method, payload=None, timeout=20):
                calls.append((method, payload))
                return {"getMe": {"username": "alitraveluzbot"}, "getWebhookInfo": {"url": url, "ip_address": telegram_ip}}.get(method, True)
            with mock.patch("api.management.commands.telegram_bot.make_call", return_value=fake), \
                 mock.patch("api.management.commands.telegram_bot.current_address", return_value="52.65.166.20"):
                call_command("telegram_bot", "--webhook", "--once", stdout=__import__("io").StringIO())
            hooks = [p for m, p in calls if m == "setWebhook"]
            self.assertEqual(bool(hooks), expect_reset, telegram_ip)
            if hooks:
                self.assertEqual(hooks[0]["ip_address"], "52.65.166.20")


class ChangeCredentialsTests(APITestCase):
    """The admin changes the sign-in e-mail and the password from the admin panel."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        from rest_framework.authtoken.models import Token
        self.user = get_user_model().objects.create_user("boss@example.com", "boss@example.com", "Old-pass-123", is_staff=True)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def post(self, **data):
        return self.client.post("/api/auth/credentials/", data, format="json")

    def test_wrong_current_password_changes_nothing(self):
        res = self.post(current_password="nope", new_password="Brand-new-pass-77")
        self.assertEqual(res.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Old-pass-123"))

    def test_new_password_signs_other_devices_out_and_keeps_this_one(self):
        res = self.post(current_password="Old-pass-123", new_password="Brand-new-pass-77")
        self.assertEqual(res.status_code, 200, res.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Brand-new-pass-77"))
        self.assertNotEqual(res.data["token"], self.token.key)                 # the old token no longer works
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {res.data['token']}")
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 200)
        self.client.credentials()
        login = self.client.post("/api/auth/login/", {"email": "boss@example.com", "password": "Brand-new-pass-77"}, format="json")
        self.assertEqual(login.status_code, 200)

    def test_new_login_is_used_to_sign_in(self):
        res = self.post(current_password="Old-pass-123", new_email="  Owner@AliTravel.uz ")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data["user"]["email"], "owner@alitravel.uz")
        self.client.credentials()
        self.assertEqual(self.client.post("/api/auth/login/", {"email": "owner@alitravel.uz", "password": "Old-pass-123"}, format="json").status_code, 200)
        self.assertEqual(self.client.post("/api/auth/login/", {"email": "boss@example.com", "password": "Old-pass-123"}, format="json").status_code, 400)

    def test_weak_password_taken_email_and_empty_request_are_refused(self):
        get_user_model().objects.create_user("other@example.com", "other@example.com", "x")
        for data in ({"new_password": "short"}, {"new_password": "12345678901"}, {"new_password": "password123"},
                     {"new_email": "other@example.com"}, {"new_email": "not-an-email"}, {}):
            res = self.post(current_password="Old-pass-123", **data)
            self.assertEqual(res.status_code, 400, data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Old-pass-123"))
        self.assertEqual(self.user.username, "boss@example.com")

    def test_guessing_the_current_password_is_stopped(self):
        for _ in range(12):
            self.post(current_password="guess", new_password="Brand-new-pass-77")
        self.assertEqual(self.post(current_password="Old-pass-123", new_password="Brand-new-pass-77").status_code, 429)

    def test_signed_out_visitor_cannot_use_it(self):
        self.client.credentials()
        self.assertIn(self.post(current_password="Old-pass-123", new_password="Brand-new-pass-77").status_code, (401, 403))


class OwnerGroupPricesTests(APITestCase):
    """The owner's prices for the 2-day Samarkand tour ($209): 14+ $209, 11-13 $249, 7-10 $267, 3-6 $289, 1-2 $294."""

    def test_the_default_table_gives_exactly_the_owners_prices(self):
        from .telegram_bot import tier_percent
        tiers = models.default_group_tiers()
        for guests, price in ((20, 209), (14, 209), (13, 249), (11, 249), (10, 267), (7, 267), (6, 289), (3, 289), (2, 294), (1, 294)):
            self.assertEqual(round(209 * tier_percent(tiers, guests) / 100, 2), price, guests)

    def test_the_bot_says_the_price_is_for_the_biggest_group_of_the_table(self):
        from .telegram_bot import biggest_group
        self.assertEqual(biggest_group(models.default_group_tiers()), 14)
        self.assertEqual(biggest_group([{"min": 25, "percent": 100}, {"min": 1, "percent": 150}]), 25)


class LocalMarketTests(APITestCase):
    """The local (so'm) site is a separate copy of the global one: same addresses, own prices, own bookings and settings."""

    RATE = Decimal("12000")

    def setUp(self):
        call_command("seed", verbosity=0)
        from .local_copy import make_local
        make_local(self.RATE)
        self.boss = get_user_model().objects.create_user("market@example.com", "market@example.com", "x", is_staff=True)

    def get(self, path, market=None):
        return self.client.get(path, **({"HTTP_X_MARKET": market} if market else {})).json()

    def test_the_copy_has_the_same_tours_at_the_same_addresses_with_prices_30_percent_lower_in_som(self):
        world = self.get("/api/tours/samarkand-city-tour/")
        home = self.get("/api/tours/samarkand-city-tour/", "local")
        self.assertEqual(world["price_from_usd"], 209)                      # the global site keeps dollars
        self.assertEqual(home["price_from_usd"], 1760000)                   # 209 x 0.7 x 12000 = 1 755 600 -> whole ten thousands
        self.assertEqual(home["title"], world["title"])
        self.assertEqual(len(self.get("/api/tours/")), len(self.get("/api/tours/", "local")))
        self.assertTrue(all("|" not in line or line.split("|")[1].strip().isdigit() for line in home["route"]))
        self.assertEqual(self.get("/api/site-content/", "local")["usd_rate"], "12000.00")
        self.assertIsNone(self.get("/api/site-content/")["usd_rate"])

    def test_changes_on_one_site_never_touch_the_other(self):
        self.client.force_authenticate(self.boss)
        self.client.patch("/api/tours/samarkand-city-tour/", {"title": "Mahalliy tur", "price_from_usd": 1500000}, format="json", HTTP_X_MARKET="local")
        self.client.put("/api/site-content/", {"hero_title": "Local hero"}, format="json", HTTP_X_MARKET="local")
        self.client.force_authenticate(None)
        self.assertEqual(self.get("/api/tours/samarkand-city-tour/")["title"], "2-Day Samarkand City Tour")
        self.assertEqual(self.get("/api/tours/samarkand-city-tour/", "local")["title"], "Mahalliy tur")
        self.assertNotEqual(self.get("/api/site-content/")["hero_title"], "Local hero")
        self.assertEqual(self.get("/api/site-content/", "local")["hero_title"], "Local hero")

    def test_a_local_booking_is_kept_apart_and_its_total_is_written_in_som(self):
        body = {"service_type": "tour", "service_slug": "samarkand-city-tour", "service_title": "Samarqand", "full_name": "Ali Valiyev",
                "email": "ali@example.com", "phone": "+998 90 123 45 67", "travel_date": "2026-12-20", "guests": 2, "estimated_total_usd": 4914000}
        with mock.patch("api.notifications._send_email") as sent, mock.patch("api.notifications._send_telegram"), self.settings(EMAIL_HOST="smtp.example.com"):
            reference = self.client.post("/api/bookings-submit/", body, format="json", HTTP_X_MARKET="local").json()["reference"]
        self.client.force_authenticate(self.boss)
        local_refs = [b["reference"] for b in self.client.get("/api/bookings/", HTTP_X_MARKET="local").json()]
        global_refs = [b["reference"] for b in self.client.get("/api/bookings/").json()]
        self.assertIn(reference, local_refs)
        self.assertNotIn(reference, global_refs)
        self.assertEqual(models.BookingRequest.everywhere.get(reference=reference).market, "local")
        from .market import money
        self.assertEqual(money(Decimal("4914000"), "local"), "4 914 000 so'm")
        self.assertEqual(money(Decimal("209"), "global"), "$209.00")

    def test_the_daily_rate_moves_automatic_prices_only(self):
        from .local_copy import update_rate
        self.client.force_authenticate(self.boss)
        self.client.patch("/api/hotels/hotel-platan-samarkand/", {"price_from_usd": 900000}, format="json", HTTP_X_MARKET="local")
        update_rate(Decimal("13000"))
        self.client.force_authenticate(None)
        self.assertEqual(self.get("/api/tours/samarkand-city-tour/", "local")["price_from_usd"], 1900000)   # 209 x 0.7 x 13000 = 1 901 900
        self.assertEqual(float(self.get("/api/hotels/hotel-platan-samarkand/", "local")["price_from_usd"]), 900000)   # typed by the team: unchanged
        self.assertEqual(self.get("/api/tours/samarkand-city-tour/")["price_from_usd"], 209)

    def test_running_the_copy_again_adds_nothing(self):
        from .local_copy import make_local
        added = make_local(self.RATE)
        self.assertEqual(sum(v for k, v in added.items()), 0)

    def test_the_owner_sets_the_2_day_tour_to_600_000_som_and_every_price_follows_without_a_guide(self):
        call_command("local_prices", "--price", "600000", verbosity=0)
        home = self.get("/api/tours/samarkand-city-tour/", "local")
        self.assertEqual(home["price_from_usd"], 600000)
        seven = self.get("/api/tours/silk-road-7-day-journey/", "local")["price_from_usd"]
        self.assertEqual(seven, float(round(Decimal(790) * Decimal(600000) / Decimal(209) / 10000) * 10000))   # the same proportion
        self.assertFalse(any("guide" in x.lower() for x in home["included"]))
        self.assertIn("Guide (on request, extra payment)", home["excluded"])
        self.assertNotIn("local guide", home["summary"])
        uz = self.client.get("/api/tours/samarkand-city-tour/", HTTP_X_MARKET="local", HTTP_X_LANG="uz").json()
        self.assertIn("Gid (xohlasangiz, qo'shimcha to'lov evaziga)", uz["excluded"])
        self.assertNotIn("gid", uz["summary"].lower())
        world = self.get("/api/tours/samarkand-city-tour/")
        self.assertEqual(world["price_from_usd"], 209)                                   # the global site keeps its guide and price
        self.assertTrue(any("guide" in x.lower() for x in world["included"]))
        cook = self.get("/api/tours/samarkand-plov-masterclass/", "local")
        self.assertEqual(cook["guide"], "Local cook (oshpaz)")                           # a class keeps its cook

    def test_a_local_booking_counts_the_guide_cost_only_when_the_traveller_asked_for_one(self):
        from .accounting import estimate_costs
        from .market import use
        with use("local"):
            plain = models.BookingRequest.objects.create(service_type="tour", service_slug="bukhara-city-tour", service_title="B", full_name="A", email="a@example.com", phone="1", guests=2, estimated_total_usd=1000000)
            guided = models.BookingRequest.objects.create(service_type="tour", service_slug="bukhara-city-tour", service_title="B", full_name="A", email="a@example.com", phone="1", guests=2, estimated_total_usd=1000000, wants_guide=True)
            self.assertNotIn("guide", [c for c, _, _ in estimate_costs(plain)])
            self.assertIn("guide", [c for c, _, _ in estimate_costs(guided)])

    def test_a_local_traveller_says_when_and_where_to_meet_instead_of_the_airport(self):
        body = {"service_type": "tour", "service_slug": "samarkand-city-tour", "service_title": "Samarqand", "full_name": "Ali Valiyev",
                "email": "meet@example.com", "phone": "+998 90 123 45 67", "travel_date": "2026-12-20", "guests": 2}
        with mock.patch("api.notifications._tell_the_team") as team, mock.patch("api.notifications._send_email"), mock.patch("api.notifications._background", side_effect=lambda fn, *a, **k: fn(*a, **k)):
            ref = self.client.post("/api/bookings-submit/", body, format="json", HTTP_X_MARKET="local").json()["reference"]
            arrival = {"reference": ref, "email": "meet@example.com", "arrival_date": "2026-12-20", "arrival_time": "09:30"}
            self.assertEqual(self.client.post("/api/bookings-arrival/", arrival, format="json", HTTP_X_MARKET="local").status_code, 400)   # the place is needed
            ok = self.client.post("/api/bookings-arrival/", {**arrival, "meeting_place": "Registon maydoni"}, format="json", HTTP_X_MARKET="local")
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(models.BookingRequest.everywhere.get(reference=ref).meeting_place, "Registon maydoni")
        card = team.call_args.kwargs["telegram_html"]
        self.assertIn("Uchrashuv", card)
        self.assertIn("Registon maydoni", card)
        self.assertNotIn("aeroport", card)

    def test_short_experiences_are_added_to_both_sites_once(self):
        call_command("add_experiences", verbosity=0)
        call_command("add_experiences", verbosity=0)   # running it again adds nothing
        world = {x["slug"]: x for x in self.get("/api/tours/") if x["slug"].endswith(("night-walk", "photo-shoot-national-costume", "day-trip", "uzbek-wedding", "sunset-hike"))}
        self.assertEqual(len(world), 12)
        self.assertEqual({x["destination_slug"] for x in world.values()}, {"samarkand", "bukhara", "khorezm"})
        night = self.get("/api/tours/samarkand-registan-night-walk/")
        self.assertEqual((night["price_from_usd"], night["review_count"], night["category"]), (15, 0, "Night tours"))
        uz = self.client.get("/api/tours/samarkand-seven-lakes-day-trip/", HTTP_X_LANG="uz").json()
        self.assertEqual(uz["category"], "Kunlik sayohatlar")
        self.assertIn("Yetti ko'l", uz["title"])
        home = self.get("/api/tours/samarkand-registan-night-walk/", "local")
        self.assertEqual(home["price_from_usd"], 130000)   # 15 x 0.7 x 12 000 = 126 000 -> whole ten thousands
        self.assertNotIn("Local guide", home["included"])
        self.assertEqual(models.Tour.everywhere.filter(slug="samarkand-registan-night-walk").count(), 2)
