import datetime
import secrets
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .market import current as current_market, default_market


class Published(models.TextChoices):
    DRAFT = "draft", "Draft"
    REVIEW = "review", "Awaiting review"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class MarketManager(models.Manager):
    """Only the rows of the current market (global or local, see market.py)."""

    def get_queryset(self):
        return super().get_queryset().filter(market=current_market())


class MarketScoped(models.Model):
    """A row that belongs to the global site (dollars) or the local one (so'm). ``objects`` sees the current market only;
    ``everywhere`` sees both (for copying and maintenance)."""

    market = models.CharField(max_length=6, default=default_market, db_index=True)
    objects = MarketManager()
    everywhere = models.Manager()

    class Meta:
        abstract = True


class Catalogued(MarketScoped):
    """Shared by every public listing: a publishing status and per-language overrides.

    ``i18n`` maps a language code to the translated fields, e.g. ``{"uz": {"title": "…"}}``.
    Missing or empty values fall back to the English columns.
    """

    status = models.CharField(max_length=12, choices=Published.choices, default=Published.PUBLISHED)
    i18n = models.JSONField(default=dict, blank=True)
    # Local copies only: while ``price_auto`` is on, the so'm prices follow the Central Bank rate from the dollar prices kept in
    # ``price_source``; an admin who types a price in so'm switches it off for that listing.
    price_auto = models.BooleanField(default=False)
    price_source = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True


class Discountable(models.Model):
    """A listing can carry its own percentage discount; site-wide promotions can add to it (the larger one applies)."""

    discount_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(90)])

    class Meta:
        abstract = True


class SiteText(MarketScoped):
    """Admin override for one piece of interface copy in one language (key is the English text)."""

    lang = models.CharField(max_length=5)
    key = models.TextField()
    value = models.TextField()

    class Meta:
        unique_together = ("market", "lang", "key")


def default_group_tiers():
    """Price per person as a percentage of the listed price, by group size. The listed ("from") price is for 14 or more travelers.

    For the 2-day Samarkand tour ($209) the rows give exactly $209 (14+), $249 (11-13), $267 (7-10), $289 (3-6) and $294 (1-2);
    every other tour follows the same proportions.
    """
    return [{"min": 14, "percent": 100}, {"min": 11, "percent": 119.138756}, {"min": 7, "percent": 127.751196},
            {"min": 3, "percent": 138.277512}, {"min": 1, "percent": 140.669856}]


def default_map_cities():
    """The cities marked green on the home page's Silk Road map. Each leads to the tours of that city, or to the tour named in `target`."""
    return {"samarkand": {"green": True, "target": ""}, "bukhara": {"green": True, "target": ""}, "shahrisabz": {"green": True, "target": ""}}


def default_cost_rates():
    """What a tour costs the company, in US dollars. Used to add the costs of every confirmed tour automatically (see accounting.py)."""
    return {"guide_per_day": 30, "car_per_day": 60, "car_seats": 4, "hotel_per_room_night": 25, "meals_per_person_day": 0,
            "hotel_cost_percent": 80, "transport_cost_percent": 75, "other_cost_percent": 70}


class SiteContent(MarketScoped):
    """Site settings and editable homepage copy: one row per market."""

    hero_eyebrow = models.CharField(max_length=200, blank=True)
    hero_title = models.CharField(max_length=200, blank=True)
    hero_subtitle = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone_primary = models.CharField(max_length=40, blank=True)
    phone_secondary = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=255, blank=True)
    hours = models.CharField(max_length=255, blank=True)
    instagram_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)  # the company page on X (Twitter)
    group_pricing_tiers = models.JSONField(default=default_group_tiers, blank=True)
    analytics_id = models.CharField(max_length=40, blank=True)  # Google Analytics 4 measurement id such as G-XXXXXXXXXX
    extra_contacts = models.JSONField(default=list, blank=True)  # more lines for the footer and contact page: [{"label", "value", "url"}]
    cost_rates = models.JSONField(default=default_cost_rates, blank=True)  # see default_cost_rates
    map_cities = models.JSONField(default=default_map_cities, blank=True)  # {city key: {"green": bool, "target": "" or "/tours/<slug>"}} for the home page map
    # Local site: the Central Bank's dollar rate (so'm for 1 USD) used for its prices, and the day it was read.
    usd_rate = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    usd_rate_date = models.DateField(null=True, blank=True)
    # Local site: a traveller's so'm price = dollar price x this factor x the dollar rate (0.7 = 30% below the dollar price).
    local_price_factor = models.DecimalField(max_digits=7, decimal_places=5, default=Decimal("0.70000"))
    # The booking deposit (see payments.py): asked right after a booking request is sent, in this site's currency.
    deposit_enabled = models.BooleanField(default=False)
    deposit_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("1.00"))
    deposit_refund_on_cancel = models.BooleanField(default=True)   # a traveller who cancels gets it back at once
    booking_verification_enabled = models.BooleanField(default=False)   # booking requires email code verification

    @classmethod
    def current(cls):
        """The settings row of the current market (created on first use)."""
        row = cls.objects.order_by("pk").first()
        return row or cls.objects.create()


class Destination(Catalogued):
    slug = models.SlugField()
    name = models.CharField(max_length=120)
    region = models.CharField(max_length=120)
    summary = models.TextField()
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    gallery = models.JSONField(default=list, blank=True)  # more photos after the cover (image_url); shown as a slider
    suggested_duration = models.CharField(max_length=60)
    highlights = models.JSONField(default=list, blank=True)
    activities = models.JSONField(default=list, blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        constraints = [models.UniqueConstraint(fields=["market", "slug"], name="destination_market_slug")]

    def __str__(self):
        return self.name


class Tour(Catalogued, Discountable):
    slug = models.SlugField()
    title = models.CharField(max_length=200)
    destination_slug = models.SlugField(blank=True)
    destination_name = models.CharField(max_length=120)
    category = models.CharField(max_length=80)
    multi_city = models.BooleanField(default=False)  # also listed under the "Multi-city" filter of the Tours page
    duration_label = models.CharField(max_length=60)
    group_type = models.CharField(max_length=60)
    summary = models.TextField()
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    gallery = models.JSONField(default=list, blank=True)  # more photos after the cover (image_url); shown as a slider
    price_from_usd = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.8)
    review_count = models.PositiveIntegerField(default=0)
    highlights = models.JSONField(default=list, blank=True)
    # Day-by-day plan: [{"day": 1, "items": [{"time": "09:00", "type": "visit|meal|transfer|free|custom", "stop": 0, ...}]}].
    # "stop" is an index into ``route`` so the place names are translated together with the route.
    itinerary = models.JSONField(default=list, blank=True)
    story = models.TextField(blank=True)  # a short, beautifully written keepsake text about the place
    # Expected costs per booking: [{"name", "category", "per": "person|group|day", "amount_usd"}]
    cost_items = models.JSONField(default=list, blank=True)
    included = models.JSONField(default=list, blank=True)
    excluded = models.JSONField(default=list, blank=True)
    # Special bonuses the team adds to a tour, shown as their own block on the tour page:
    # [{"title", "text", "duration", "tag": "bonus|exclusive|gift", "image", "gallery": [...], "i18n": {"uz": {"title", "text", "duration"}}}]
    bonuses = models.JSONField(default=list, blank=True)
    # Practical details shown in the "Tour details" panel.
    tour_type = models.CharField(max_length=20, blank=True)  # car | walking | mixed | train | workshop
    group_pricing = models.BooleanField(default=True)  # the listed price is for the biggest group of the table; smaller groups pay more per person
    max_travelers = models.PositiveSmallIntegerField(null=True, blank=True)
    languages = models.JSONField(default=list, blank=True)  # guide languages, e.g. ["English", "Russian"]
    transport_included = models.BooleanField(default=False)
    tickets_included = models.BooleanField(default=False)
    pickup_included = models.BooleanField(default=False)
    guide = models.CharField(max_length=160, blank=True)
    meeting_point = models.CharField(max_length=200, blank=True)
    # One stop per line as "Name | entrance fee in USD" (the fee is optional). Translatable like any other list.
    route = models.JSONField(default=list, blank=True)
    # For a single historical place that is also part of a bigger tour: its entrance ticket and the parent tour.
    entrance_fee_usd = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    parent_slug = models.SlugField(blank=True)
    featured = models.BooleanField(default=False)
    is_demo = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    # Exact location of a place (a single place of a tour): shown on a map with a link to Google Maps.
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_note = models.CharField(max_length=200, blank=True)  # address or how to find it, e.g. "Registan Street, next to the ticket office"

    class Meta:
        ordering = ["-featured", "-created"]
        constraints = [models.UniqueConstraint(fields=["market", "slug"], name="tour_market_slug")]

    def __str__(self):
        return self.title


class Hotel(Catalogued, Discountable):
    slug = models.SlugField()
    name = models.CharField(max_length=160)
    destination_slug = models.SlugField(blank=True)
    destination_name = models.CharField(max_length=120)
    stars = models.PositiveSmallIntegerField(default=3)
    summary = models.TextField()
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    price_from_usd = models.DecimalField(max_digits=14, decimal_places=2)
    amenities = models.JSONField(default=list, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.6)
    is_demo = models.BooleanField(default=True)
    gallery = models.JSONField(default=list, blank=True)  # more photos after the cover (image_url); shown as a slider
    PROPERTY_TYPES = [("hotel", "Hotel"), ("boutique", "Boutique hotel"), ("guesthouse", "Guesthouse"), ("hostel", "Hostel")]
    property_type = models.CharField(max_length=12, choices=PROPERTY_TYPES, default="hotel")
    PRICE_BASES = [("room", "per room per night"), ("bed", "per bed per night")]
    price_basis = models.CharField(max_length=6, choices=PRICE_BASES, default="room")  # hostels are priced per dorm bed
    photos_illustrative = models.BooleanField(default=False)  # the photos show the destination, not this property itself

    class Meta:
        constraints = [models.UniqueConstraint(fields=["market", "slug"], name="hotel_market_slug")]

    def __str__(self):
        return self.name


class FoodExperience(Catalogued):
    slug = models.SlugField()
    name = models.CharField(max_length=160)
    destination_name = models.CharField(max_length=120, blank=True)
    summary = models.TextField()
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    kind = models.CharField(max_length=60, default="Dish")
    price_from_usd = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["market", "slug"], name="food_market_slug")]

    def __str__(self):
        return self.name


class TransportOption(Catalogued, Discountable):
    slug = models.SlugField()
    name = models.CharField(max_length=160)
    vehicle = models.CharField(max_length=120)
    capacity = models.PositiveSmallIntegerField(default=3)
    included_passengers = models.PositiveSmallIntegerField(default=3)
    summary = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    base_price_usd = models.DecimalField(max_digits=14, decimal_places=2)
    extra_passenger_usd = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["market", "slug"], name="transport_market_slug")]

    def __str__(self):
        return self.name


class BookingRequest(MarketScoped):
    STATUS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]
    reference = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    service_type = models.CharField(max_length=20)
    service_slug = models.CharField(max_length=200, blank=True)
    service_title = models.CharField(max_length=255)
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    travel_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    guests = models.PositiveSmallIntegerField(default=1)
    details_summary = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    estimated_total_usd = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    # Accounting: the price agreed with the traveller (falls back to the estimate) and any discount.
    final_price_usd = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    discount_usd = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS, default="pending")
    admin_notes = models.TextField(blank=True)
    lang = models.CharField(max_length=5, blank=True)  # the language the traveller was reading, for e-mails
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)  # set when the request was made in the Telegram bot
    # When and how the traveller reaches Samarkand airport (sent after booking, so the guide can meet them).
    arrival_date = models.DateField(null=True, blank=True)
    arrival_time = models.TimeField(null=True, blank=True)
    arrival_flight = models.CharField(max_length=60, blank=True)  # flight or train number
    arrival_note = models.CharField(max_length=300, blank=True)  # free text, e.g. typed in the Telegram bot
    # Local site: travellers are already in Uzbekistan, so instead of the airport they say where the team meets them
    # (arrival_date and arrival_time then hold the day and time of that meeting).
    meeting_place = models.CharField(max_length=200, blank=True)
    # The booking deposit (payments.py): "" = not asked, pending, paid, failed, refunded or kept (the team decided not to refund).
    DEPOSIT_STATES = [("", "Not asked"), ("pending", "Waiting for payment"), ("paid", "Paid"), ("failed", "Not paid"), ("refunded", "Refunded"), ("kept", "Kept")]
    deposit_status = models.CharField(max_length=10, choices=DEPOSIT_STATES, blank=True, default="")
    deposit_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    deposit_currency = models.CharField(max_length=3, blank=True)
    deposit_txn = models.CharField(max_length=40, blank=True, db_index=True)   # our id of the current payment attempt
    deposit_payment_id = models.CharField(max_length=64, blank=True)          # Octo's payment UUID
    deposit_paid_at = models.DateTimeField(null=True, blank=True)
    deposit_refunded_at = models.DateTimeField(null=True, blank=True)
    wants_guide = models.BooleanField(default=False)  # local site: the guide is not in the price; the traveller asked for one (extra payment)
    verification_code = models.CharField(max_length=6, blank=True)   # 6-digit email verification code (when booking_verification_enabled)
    verification_code_hash = models.CharField(max_length=64, blank=True)  # HMAC-SHA256 of the code
    verification_sent_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)  # when the email was verified; deposit starts after this
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = "AT-" + secrets.token_hex(3).upper()
        super().save(*args, **kwargs)


class ContactMessage(MarketScoped):
    STATUS = [("new", "New"), ("read", "Read"), ("replied", "Replied")]
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS, default="new")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    source = models.CharField(max_length=60, blank=True)
    created = models.DateTimeField(auto_now_add=True)


class SavedItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20)
    item_slug = models.CharField(max_length=200)
    item_title = models.CharField(max_length=255)
    item_image = models.URLField(max_length=500, blank=True)
    item_meta = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "item_type", "item_slug")
        ordering = ["-created"]


class Partner(MarketScoped):
    STATUS = [("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    business_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    partner_type = models.CharField(max_length=40)
    city = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    admin_notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]


class Payment(models.Model):
    """Money received from a traveller for a booking."""

    METHODS = [("cash", "Cash"), ("card", "Card"), ("transfer", "Bank transfer"), ("other", "Other")]
    booking = models.ForeignKey(BookingRequest, related_name="payments", on_delete=models.CASCADE)
    amount_usd = models.DecimalField(max_digits=16, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHODS, default="cash")
    paid_on = models.DateField(default=datetime.date.today)
    note = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["paid_on", "id"]


class Expense(MarketScoped):
    """Money spent to deliver a tour, or a general business expense when ``booking`` is empty."""

    CATEGORIES = [
        ("guide", "Guide"), ("transport", "Transport"), ("meals", "Meals"), ("hotel", "Hotel"),
        ("tickets", "Tickets"), ("marketing", "Marketing"), ("office", "Office"), ("other", "Other"),
    ]
    booking = models.ForeignKey(BookingRequest, null=True, blank=True, related_name="expenses", on_delete=models.CASCADE)
    category = models.CharField(max_length=12, choices=CATEGORIES, default="other")
    description = models.CharField(max_length=200)
    amount_usd = models.DecimalField(max_digits=16, decimal_places=2)
    spent_on = models.DateField(default=datetime.date.today)
    paid_to = models.CharField(max_length=160, blank=True)
    auto = models.BooleanField(default=False)  # created from the tour's cost template
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-spent_on", "-id"]


class Promotion(MarketScoped):
    """A campaign such as "20% off all tours". While active it shows as a banner and discounts matching prices."""

    APPLIES = [("all", "Everything"), ("tours", "Tours"), ("hotels", "Hotels"), ("transport", "Transport")]
    title = models.CharField(max_length=160)
    message = models.CharField(max_length=300, blank=True)
    percent = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(90)])
    applies_to = models.CharField(max_length=10, choices=APPLIES, default="all")
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    # Optional limits: destination slugs and tour slugs. Both empty = everything of the chosen kind; otherwise only listings in one of
    # the chosen destinations or among the chosen tours (hotels follow their destination; transport has no destination).
    destinations = models.JSONField(default=list, blank=True)
    tours = models.JSONField(default=list, blank=True)
    i18n = models.JSONField(default=dict, blank=True)  # {"uz": {"title": "...", "message": "..."}}
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def covers(self, item):
        """Whether this campaign's limits (if any) include a tour, hotel or transport option."""
        if not (self.destinations or self.tours):
            return True
        return getattr(item, "destination_slug", "") in self.destinations or getattr(item, "slug", "") in self.tours

    def is_running(self, today=None):
        today = today or datetime.date.today()
        return self.active and (not self.starts_on or self.starts_on <= today) and (not self.ends_on or self.ends_on >= today)


class LegalPage(MarketScoped):
    """Privacy policy, terms or cancellation policy. ``body`` uses a tiny markup: ## heading, - bullet, 1. step, **bold**, [text](url)."""

    slug = models.SlugField()
    title = models.CharField(max_length=160)
    body = models.TextField()
    updated = models.DateField(default=datetime.date.today)
    i18n = models.JSONField(default=dict, blank=True)  # {"uz": {"title": "...", "body": "..."}}

    class Meta:
        constraints = [models.UniqueConstraint(fields=["market", "slug"], name="legal_market_slug")]

    def __str__(self):
        return self.title


class Review(MarketScoped):
    """A traveller's review of a tour. Shown on the site only after an admin publishes it; reviews whose booking reference and
    email match a confirmed or completed booking are marked as verified travellers."""

    STATUS = [("pending", "Awaiting review"), ("published", "Published"), ("hidden", "Hidden")]
    tour_slug = models.CharField(max_length=200)
    tour_title = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=120)
    country = models.CharField(max_length=80, blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(max_length=2000)
    email = models.EmailField(blank=True)  # never shown; only used to verify the booking
    reference = models.CharField(max_length=20, blank=True)  # booking reference, never shown
    lang = models.CharField(max_length=5, blank=True)  # the language the reviewer was reading, for the thank-you e-mail
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS, default="pending")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.name} — {self.tour_title or self.tour_slug} ({self.rating}★)"

    def refresh_tour(self):
        """Keep the tour's star rating and review count in step with its published reviews."""
        from django.db.models import Avg
        published = Review.objects.filter(tour_slug=self.tour_slug, status="published")
        count = published.count()
        if count:
            average = published.aggregate(a=Avg("rating"))["a"]
            Tour.objects.filter(slug=self.tour_slug).update(rating=round(average, 1), review_count=count)
        else:
            Tour.objects.filter(slug=self.tour_slug).update(review_count=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.refresh_tour()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.refresh_tour()


class PendingSignup(models.Model):
    """Someone creating an account: the account itself is made only when they type the code we e-mailed them, so every
    account (and every booking made with it) belongs to a real mailbox. The password and the code are kept only as hashes."""

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    password_hash = models.CharField(max_length=128)
    code_hash = models.CharField(max_length=64)
    attempts = models.PositiveSmallIntegerField(default=0)
    sent_at = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)


class TelegramUser(models.Model):
    """Someone who talks to the Telegram bot: the language they picked and where they are in a conversation."""

    chat_id = models.BigIntegerField(unique=True)
    lang = models.CharField(max_length=5, blank=True)
    first_name = models.CharField(max_length=120, blank=True)
    username = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)  # the number the traveller shared or typed when they booked or asked
    contact_name = models.CharField(max_length=160, blank=True)  # the name on the contact they shared (more reliable than the profile name)
    state = models.CharField(max_length=20, blank=True)  # "" or "asking" (the next message is a request for the team)
    state_data = models.CharField(max_length=200, blank=True)  # e.g. the slug of the tour they want to request
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def display_name(self):
        """The name to write in bookings and in the customers list."""
        return self.contact_name or " ".join(x for x in (self.first_name, self.last_name) if x) or (f"@{self.username}" if self.username else "")

    def __str__(self):
        return f"{self.first_name or self.username or self.chat_id} ({self.lang or '?'})"
