import datetime
import secrets

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Published(models.TextChoices):
    DRAFT = "draft", "Draft"
    REVIEW = "review", "Awaiting review"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"


class Catalogued(models.Model):
    """Shared by every public listing: a publishing status and per-language overrides.

    ``i18n`` maps a language code to the translated fields, e.g. ``{"uz": {"title": "…"}}``.
    Missing or empty values fall back to the English columns.
    """

    status = models.CharField(max_length=12, choices=Published.choices, default=Published.PUBLISHED)
    i18n = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True


class Discountable(models.Model):
    """A listing can carry its own percentage discount; site-wide promotions can add to it (the larger one applies)."""

    discount_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(90)])

    class Meta:
        abstract = True


class SiteText(models.Model):
    """Admin override for one piece of interface copy in one language (key is the English text)."""

    lang = models.CharField(max_length=5)
    key = models.TextField()
    value = models.TextField()

    class Meta:
        unique_together = ("lang", "key")


def default_group_tiers():
    """Price per person as a percentage of the listed price, by group size. The listed ("from") price is for 20 or more travelers."""
    return [{"min": 20, "percent": 100}, {"min": 15, "percent": 105}, {"min": 10, "percent": 115}, {"min": 6, "percent": 130},
            {"min": 4, "percent": 150}, {"min": 2, "percent": 180}, {"min": 1, "percent": 220}]


class SiteContent(models.Model):
    """Single-row site settings and editable homepage copy."""

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
    group_pricing_tiers = models.JSONField(default=default_group_tiers, blank=True)


class Destination(Catalogued):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=120)
    region = models.CharField(max_length=120)
    summary = models.TextField()
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    suggested_duration = models.CharField(max_length=60)
    highlights = models.JSONField(default=list, blank=True)
    activities = models.JSONField(default=list, blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Tour(Catalogued, Discountable):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    destination_slug = models.SlugField(blank=True)
    destination_name = models.CharField(max_length=120)
    category = models.CharField(max_length=80)
    duration_label = models.CharField(max_length=60)
    group_type = models.CharField(max_length=60)
    summary = models.TextField()
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    price_from_usd = models.DecimalField(max_digits=8, decimal_places=2)
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
    # Practical details shown in the "Tour details" panel.
    tour_type = models.CharField(max_length=20, blank=True)  # car | walking | mixed | train | workshop
    group_pricing = models.BooleanField(default=True)  # the listed price is for 20+ travelers; smaller groups pay more per person
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
    entrance_fee_usd = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    parent_slug = models.SlugField(blank=True)
    featured = models.BooleanField(default=False)
    is_demo = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-featured", "-created"]

    def __str__(self):
        return self.title


class Hotel(Catalogued, Discountable):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=160)
    destination_slug = models.SlugField(blank=True)
    destination_name = models.CharField(max_length=120)
    stars = models.PositiveSmallIntegerField(default=3)
    summary = models.TextField()
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    price_from_usd = models.DecimalField(max_digits=8, decimal_places=2)
    amenities = models.JSONField(default=list, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.6)
    is_demo = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FoodExperience(Catalogued):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=160)
    destination_name = models.CharField(max_length=120, blank=True)
    summary = models.TextField()
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    kind = models.CharField(max_length=60, default="Dish")
    price_from_usd = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class TransportOption(Catalogued, Discountable):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=160)
    vehicle = models.CharField(max_length=120)
    capacity = models.PositiveSmallIntegerField(default=3)
    included_passengers = models.PositiveSmallIntegerField(default=3)
    summary = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)  # absolute link or an uploaded /media/ path
    base_price_usd = models.DecimalField(max_digits=8, decimal_places=2)
    extra_passenger_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return self.name


class BookingRequest(models.Model):
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
    estimated_total_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Accounting: the price agreed with the traveller (falls back to the estimate) and any discount.
    final_price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=12, choices=STATUS, default="pending")
    admin_notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = "AT-" + secrets.token_hex(3).upper()
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
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


class Partner(models.Model):
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
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHODS, default="cash")
    paid_on = models.DateField(default=datetime.date.today)
    note = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["paid_on", "id"]


class Expense(models.Model):
    """Money spent to deliver a tour, or a general business expense when ``booking`` is empty."""

    CATEGORIES = [
        ("guide", "Guide"), ("transport", "Transport"), ("meals", "Meals"), ("hotel", "Hotel"),
        ("tickets", "Tickets"), ("marketing", "Marketing"), ("office", "Office"), ("other", "Other"),
    ]
    booking = models.ForeignKey(BookingRequest, null=True, blank=True, related_name="expenses", on_delete=models.CASCADE)
    category = models.CharField(max_length=12, choices=CATEGORIES, default="other")
    description = models.CharField(max_length=200)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    spent_on = models.DateField(default=datetime.date.today)
    paid_to = models.CharField(max_length=160, blank=True)
    auto = models.BooleanField(default=False)  # created from the tour's cost template
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-spent_on", "-id"]


class Promotion(models.Model):
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


class LegalPage(models.Model):
    """Privacy policy, terms or cancellation policy. ``body`` uses a tiny markup: ## heading, - bullet, 1. step, **bold**, [text](url)."""

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    body = models.TextField()
    updated = models.DateField(default=datetime.date.today)
    i18n = models.JSONField(default=dict, blank=True)  # {"uz": {"title": "...", "body": "..."}}

    def __str__(self):
        return self.title


class Review(models.Model):
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
