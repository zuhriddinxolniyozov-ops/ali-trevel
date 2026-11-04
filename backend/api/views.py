import secrets
from datetime import date

from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import authenticate, get_user_model
from django.core.files.storage import default_storage
from django.utils.text import slugify
from django.db.models import Count, Sum
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, parser_classes, permission_classes, throttle_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from . import notifications

from . import models, serializers as s

User = get_user_model()


class RegisterThrottle(AnonRateThrottle):
    scope = "register"
    rate = "20/hour"


LOGIN_FAILS_ALLOWED = 8
LOGIN_LOCK_SECONDS = 15 * 60


class BookingThrottle(AnonRateThrottle):
    scope = "booking"
    rate = "40/hour"


class ContactThrottle(AnonRateThrottle):
    scope = "contact"
    rate = "20/hour"


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or bool(request.user and request.user.is_staff)


class CatalogViewSet(viewsets.ModelViewSet):
    """Public read, admin write. Models with a status field only expose published rows to non-admins."""

    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request
        staff = bool(request.user and request.user.is_staff)
        # Admins see every status when writing, or when they ask for it (?all=1); the public site shows published only.
        sees_all = staff and (request.method not in permissions.SAFE_METHODS or request.query_params.get("all"))
        qs = qs if sees_all else qs.filter(status="published")
        destination = request.query_params.get("destination_slug")
        if destination and hasattr(self.queryset.model, "destination_slug"):
            qs = qs.filter(destination_slug=destination)
        return qs

    def create(self, request, *args, **kwargs):
        # Admins create records without picking a slug; derive a unique one from the title/name.
        data = request.data.copy()
        if not data.get("slug"):
            base = slugify(data.get("title") or data.get("name") or "item")[:60] or "item"
            data["slug"] = f"{base}-{secrets.token_hex(2)}"
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DestinationViewSet(CatalogViewSet):
    queryset = models.Destination.objects.all()
    serializer_class = s.DestinationSerializer


class TourViewSet(CatalogViewSet):
    queryset = models.Tour.objects.all()
    serializer_class = s.TourSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        for key in ("category", "destination_slug", "featured", "parent_slug", "tour_type"):
            if params.get(key):
                qs = qs.filter(**{key: params[key]})
        if params.get("has_parent"):  # every single place of every tour (the day plan finds its places among them by name)
            qs = qs.exclude(parent_slug="")
        return qs


    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def duplicate(self, request, slug=None):
        tour = self.get_object()
        tour.pk = None
        tour.slug = f"{tour.slug[:55]}-copy-{secrets.token_hex(2)}"
        tour.title = f"{tour.title} (copy)"
        tour.status = "draft"
        tour.featured = False
        tour.save()
        return Response(s.TourSerializer(tour, context={"request": request}).data, status=201)


class HotelViewSet(CatalogViewSet):
    queryset = models.Hotel.objects.order_by("-stars", "id")  # 5-star hotels first
    serializer_class = s.HotelSerializer


class FoodViewSet(CatalogViewSet):
    queryset = models.FoodExperience.objects.all()
    serializer_class = s.FoodSerializer


class TransportViewSet(CatalogViewSet):
    queryset = models.TransportOption.objects.all()
    serializer_class = s.TransportSerializer


@api_view(["GET", "PUT"])
@permission_classes([permissions.AllowAny])
def site_content(request):
    obj, _ = models.SiteContent.objects.get_or_create(pk=1)
    if request.method == "PUT":
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        ser = s.SiteContentSerializer(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)
    return Response(s.SiteContentSerializer(obj).data)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([ContactThrottle])
def contact(request):
    if request.data.get("website"):  # a hidden field only robots fill in
        return Response({"ok": True}, status=status.HTTP_201_CREATED)
    ser = s.ContactMessageSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    message = ser.save()
    notifications.message_received(message)
    return Response(ser.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def newsletter(request):
    email = (request.data.get("email") or "").strip().lower()
    if "@" not in email:
        return Response({"error": "A valid email is required."}, status=400)
    models.NewsletterSubscriber.objects.get_or_create(email=email, defaults={"source": request.data.get("source", "")})
    return Response({"ok": True}, status=201)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([BookingThrottle])
def submit_booking(request):
    if request.data.get("website"):  # a hidden field only robots fill in
        return Response({"reference": "", "status": "pending"}, status=201)
    ser = s.BookingSubmitSerializer(data=request.data)
    if not ser.is_valid():
        return Response({"error": "Please check the form fields.", "fields": ser.errors}, status=400)
    user = request.user if request.user.is_authenticated else None
    lang = (request.headers.get("X-Lang") or "en")[:5]
    booking = ser.save(user=user, lang=lang)
    notifications.booking_created(booking)
    return Response({"reference": booking.reference, "status": booking.status}, status=201)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([BookingThrottle])
def booking_arrival(request):
    """The traveller tells us when they arrive at Samarkand airport; the booking reference and its e-mail address identify the booking."""
    reference = str(request.data.get("reference") or "").strip().upper()
    email = str(request.data.get("email") or "").strip().lower()
    booking = models.BookingRequest.objects.filter(reference=reference, email__iexact=email).first() if reference and email else None
    if not booking or booking.status in ("cancelled", "completed"):
        return Response({"error": "We could not find this booking."}, status=404)
    ser = s.ArrivalSerializer(data=request.data)
    if not ser.is_valid():
        return Response({"error": "Please check the arrival date and time.", "fields": ser.errors}, status=400)
    for field, value in ser.validated_data.items():
        setattr(booking, field, value)
    booking.save(update_fields=list(ser.validated_data))
    notifications.arrival_received(booking)
    return Response({"ok": True})


class BookingViewSet(viewsets.ReadOnlyModelViewSet):
    """Admins see everything; signed-in users see requests tied to their account or email."""

    serializer_class = s.BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = models.BookingRequest.objects.all()
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(email__iexact=user.email) | qs.filter(user=user)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status not in ("pending", "confirmed"):
            return Response({"error": "This request can no longer be cancelled."}, status=400)
        booking.status = "cancelled"
        booking.save(update_fields=["status"])
        notifications.booking_cancelled_by_traveller(booking)
        return Response(s.BookingSerializer(booking, context={"request": request}).data)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        before = booking.status
        for field in ("status", "admin_notes"):
            if field in request.data:
                setattr(booking, field, request.data[field])
        booking.save()
        if booking.status != before:
            notifications.booking_status_changed(booking)
        return Response(s.BookingSerializer(booking, context={"request": request}).data)


class SavedItemViewSet(viewsets.ModelViewSet):
    serializer_class = s.SavedItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = models.SavedItem.objects.filter(user=self.request.user)
        for key in ("item_type", "item_slug"):
            if self.request.query_params.get(key):
                qs = qs.filter(**{key: self.request.query_params[key]})
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessageAdminViewSet(viewsets.ModelViewSet):
    queryset = models.ContactMessage.objects.all()
    serializer_class = s.ContactMessageAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ["get", "patch", "delete"]


class PartnerViewSet(viewsets.ModelViewSet):
    serializer_class = s.PartnerSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = models.Partner.objects.all()
        return qs if self.request.user.is_staff else qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAdminUser])
    def review(self, request, pk=None):
        partner = self.get_object()
        partner.status = request.data.get("status", partner.status)
        partner.admin_notes = request.data.get("admin_notes", partner.admin_notes)
        partner.save()
        return Response(s.PartnerSerializer(partner).data)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def customers(request):
    """Everyone who dealt with us, as one list: website accounts, guests who booked without an account and Telegram bot users."""
    bookings = list(models.BookingRequest.objects.all())  # newest first
    by_email, by_chat = {}, {}
    for b in bookings:
        if b.telegram_chat_id:
            by_chat.setdefault(b.telegram_chat_id, []).append(b)
        else:
            by_email.setdefault(b.email.lower(), []).append(b)

    def summary(rows):
        return {
            "bookings": len(rows), "total_usd": float(sum((r.final_price_usd if r.final_price_usd is not None else r.estimated_total_usd) - r.discount_usd for r in rows if r.status != "cancelled")),
            "last_booking_at": rows[0].created if rows else None,
            "recent_bookings": [{"reference": r.reference, "service_title": r.service_title, "status": r.status, "travel_date": r.travel_date, "guests": r.guests,
                                 "arrival": " ".join(x for x in (str(r.arrival_date or ""), r.arrival_time.strftime("%H:%M") if r.arrival_time else "", r.arrival_flight, r.arrival_note) if x)} for r in rows[:5]],
        }

    people, known_emails = [], set()
    for u in User.objects.order_by("-date_joined"):
        known_emails.add(u.email.lower())
        rows = by_email.get(u.email.lower(), [])
        people.append({"key": f"user-{u.id}", "kind": "account", "name": u.get_full_name() or u.username, "email": u.email, "phone": rows[0].phone if rows else "", "username": "",
                       "lang": "", "chat_id": None, "is_staff": u.is_staff, "joined": u.date_joined, **summary(rows)})
    for email, rows in by_email.items():
        if email not in known_emails:
            people.append({"key": f"guest-{email}", "kind": "guest", "name": rows[0].full_name, "email": rows[0].email, "phone": rows[0].phone, "username": "", "lang": rows[0].lang,
                           "chat_id": None, "is_staff": False, "joined": rows[-1].created, **summary(rows)})
    for t in models.TelegramUser.objects.order_by("-created"):
        rows = by_chat.get(t.chat_id, [])
        people.append({"key": f"telegram-{t.chat_id}", "kind": "telegram", "name": t.display_name or str(t.chat_id), "email": "", "phone": t.phone or (rows[0].phone if rows else ""),
                       "username": t.username, "lang": t.lang, "chat_id": t.chat_id, "is_staff": False, "joined": t.created, **summary(rows)})
    people.sort(key=lambda p: p["last_booking_at"] or p["joined"], reverse=True)
    return Response(people)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def admin_stats(request):
    today = date.today()
    by_status = {
        row["status"]: row
        for row in models.BookingRequest.objects.values("status").annotate(n=Count("id"), total=Sum("estimated_total_usd"))
    }
    latest = models.BookingRequest.objects.all()[:5]
    upcoming = models.BookingRequest.objects.filter(status__in=["pending", "confirmed"], travel_date__gte=today).order_by("travel_date")[:5]
    catalogues = (models.Destination, models.Tour, models.Hotel, models.FoodExperience, models.TransportOption)
    return Response({
        "pending": by_status.get("pending", {}).get("n", 0),
        "total_bookings": sum(row["n"] for row in by_status.values()),
        "confirmed": by_status.get("confirmed", {}).get("n", 0),
        "confirmed_value": float(by_status.get("confirmed", {}).get("total") or 0),
        "tours_live": models.Tour.objects.filter(status="published").count(),
        "tours_unpublished": models.Tour.objects.exclude(status="published").count(),
        "published_listings": sum(m.objects.filter(status="published").count() for m in catalogues),
        "customers": User.objects.filter(is_staff=False).count(),
        "new_messages": models.ContactMessage.objects.filter(status="new").count(),
        "pending_partners": models.Partner.objects.filter(status="pending").count(),
        "latest": s.BookingSerializer(latest, many=True, context={"request": request}).data,
        "upcoming": s.BookingSerializer(upcoming, many=True, context={"request": request}).data,
    })


@api_view(["GET", "PUT"])
@permission_classes([permissions.AllowAny])
def site_texts(request):
    """GET -> {lang: {english text: override}}; PUT {lang, key, value} (admin) sets or clears one override."""
    if request.method == "PUT":
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        lang, key, value = request.data.get("lang"), request.data.get("key"), (request.data.get("value") or "").strip()
        if lang not in ("en", "uz", "ru", "fr", "de", "es") or not key:
            return Response({"error": "Unknown language or empty key."}, status=400)
        if value:
            models.SiteText.objects.update_or_create(lang=lang, key=key, defaults={"value": value})
        else:
            models.SiteText.objects.filter(lang=lang, key=key).delete()
        return Response({"ok": True})
    out = {}
    for row in models.SiteText.objects.all():
        out.setdefault(row.lang, {})[row.key] = row.value
    return Response(out)


def _auth_response(user):
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": s.UserSerializer(user).data})


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
@throttle_classes([RegisterThrottle])
def register(request):
    ser = s.RegisterSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    return _auth_response(ser.save())


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    email = (request.data.get("email") or "").strip().lower()
    key = f"login-fails:{AnonRateThrottle().get_ident(request)}:{email}"
    if cache.get(key, 0) >= LOGIN_FAILS_ALLOWED:
        return Response({"error": "Too many failed attempts. Please try again in a few minutes."}, status=429)
    user = authenticate(username=email, password=request.data.get("password") or "")
    if not user:
        cache.set(key, cache.get(key, 0) + 1, LOGIN_LOCK_SECONDS)
        return Response({"error": "Incorrect email or password."}, status=400)
    cache.delete(key)
    return _auth_response(user)


@api_view(["POST"])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"ok": True})


@api_view(["POST"])
def change_credentials(request):
    """Change the sign-in e-mail (the login) and/or the password of the signed-in account.

    The current password is always required. Changing the password signs every other device out (their tokens are deleted)
    and returns a fresh token for this one, so the person stays signed in here.
    """
    user = request.user
    key = f"credential-fails:{user.pk}"
    if cache.get(key, 0) >= LOGIN_FAILS_ALLOWED:
        return Response({"error": "Too many failed attempts. Please try again in a few minutes."}, status=429)
    if not user.check_password(request.data.get("current_password") or ""):
        cache.set(key, cache.get(key, 0) + 1, LOGIN_LOCK_SECONDS)
        return Response({"error": "The current password is not correct.", "fields": {"current_password": ["The current password is not correct."]}}, status=400)
    cache.delete(key)
    ser = s.ChangeCredentialsSerializer(data=request.data, context={"user": user})
    ser.is_valid(raise_exception=True)
    email, password = ser.validated_data.get("new_email"), ser.validated_data.get("new_password")
    if not email and not password:
        return Response({"error": "Write a new login or a new password."}, status=400)
    if email:
        user.username = user.email = email
    if password:
        user.set_password(password)
    user.save()
    if password:
        Token.objects.filter(user=user).delete()   # every other device signs in again with the new password
    return _auth_response(user)


@api_view(["GET", "PATCH"])
def me(request):
    if request.method == "PATCH" and "full_name" in request.data:
        first, _, last = request.data["full_name"].partition(" ")
        request.user.first_name, request.user.last_name = first, last
        request.user.save(update_fields=["first_name", "last_name"])
    return Response(s.UserSerializer(request.user).data)


MAX_UPLOAD_BYTES = 8 * 1024 * 1024
# File signatures (hex) -> extension; SVG is deliberately not accepted.
IMAGE_SIGNATURES = (
    (bytes.fromhex("ffd8ff"), ".jpg"),
    (bytes.fromhex("89504e470d0a1a0a"), ".png"),
    (b"GIF87a", ".gif"),
    (b"GIF89a", ".gif"),
)


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
@parser_classes([MultiPartParser])
def upload_image(request):
    """Store an uploaded photo (staff only). The type is decided from the file's bytes, never from its name."""
    upload = request.FILES.get("file")
    if not upload:
        return Response({"error": "Choose an image file to upload."}, status=400)
    if upload.size > MAX_UPLOAD_BYTES:
        return Response({"error": "The image is larger than 8 MB."}, status=400)
    head = upload.read(12)
    upload.seek(0)
    ext = next((e for sig, e in IMAGE_SIGNATURES if head.startswith(sig)), None)
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        ext = ".webp"
    if not ext:
        return Response({"error": "Please upload a JPG, PNG, GIF or WebP image."}, status=400)
    saved = default_storage.save(f"uploads/{secrets.token_hex(8)}{ext}", upload)
    return Response({"url": default_storage.url(saved)}, status=201)


class PromotionViewSet(viewsets.ModelViewSet):
    queryset = models.Promotion.objects.all()
    serializer_class = s.PromotionSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def active_promotions(request):
    """Campaigns running today, in the visitor's language (used by the announcement bar)."""
    running = [p for p in models.Promotion.objects.filter(active=True) if p.is_running()]
    return Response(s.PromotionSerializer(running, many=True, context={"request": request}).data)


class LegalPageViewSet(viewsets.ModelViewSet):
    """Public read; admins edit. Only the three fixed pages exist, so there is no create or delete."""

    queryset = models.LegalPage.objects.all()
    serializer_class = s.LegalPageSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    http_method_names = ["get", "put", "patch", "head", "options"]


class ReviewThrottle(AnonRateThrottle):
    scope = "review"
    rate = "8/hour"


class ReviewViewSet(viewsets.ModelViewSet):
    """Anyone can read published reviews and send one (it waits for an admin); only admins moderate."""

    queryset = models.Review.objects.all()

    def get_permissions(self):
        if self.action in ("list", "retrieve", "create"):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_throttles(self):
        return [ReviewThrottle()] if self.action == "create" else []

    def get_serializer_class(self):
        staff = bool(self.request.user and self.request.user.is_staff)
        return s.ReviewAdminSerializer if staff and self.action != "create" else s.ReviewSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        staff = bool(self.request.user and self.request.user.is_staff)
        if not (staff and self.request.query_params.get("all")) and self.action in ("list", "retrieve"):
            qs = qs.filter(status="published")
        tour = self.request.query_params.get("tour_slug")
        return qs.filter(tour_slug=tour) if tour else qs

    def create(self, request, *args, **kwargs):
        if request.data.get("website"):  # a hidden field only robots fill in
            return Response({"ok": True}, status=201)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        data = serializer.validated_data
        tour = models.Tour.objects.filter(slug=data["tour_slug"]).first()
        verified = bool(data.get("reference") and data.get("email") and models.BookingRequest.objects.filter(
            reference__iexact=data["reference"].strip(), email__iexact=data["email"].strip(), status__in=["confirmed", "completed"]).exists())
        review = serializer.save(tour_title=tour.title if tour else "", verified=verified, status="pending", lang=(self.request.headers.get("X-Lang") or "en")[:5])
        notifications.review_received(review)
