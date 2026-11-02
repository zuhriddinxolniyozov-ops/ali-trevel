from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
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
