import re
from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models

User = get_user_model()


def promo_text(promo, field, lang):
    return (promo.i18n or {}).get(lang, {}).get(field) or getattr(promo, field)


def effective_discount(instance, context, lang):
    """The percentage off right now: the listing's own discount or a running promotion, whichever is larger."""
    promos = context.setdefault("_running_promotions", [p for p in models.Promotion.objects.filter(active=True) if p.is_running()])
    kind = {"tour": "tours", "hotel": "hotels", "transportoption": "transport"}.get(instance._meta.model_name)
    best, title = instance.discount_percent or 0, ""
    for promo in promos:
        if promo.applies_to in ("all", kind) and promo.percent > best and promo.covers(instance):
            best, title = promo.percent, promo_text(promo, "title", lang)
    return best, title


class LocalizedMixin:
    """Overlay ``instance.i18n[lang]`` onto the response when the client asks for a language.

    The language comes from the ``X-Lang`` header; the admin passes ``?raw=1`` to get the
    untranslated English columns plus the full ``i18n`` map for editing.
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        lang = request.headers.get("X-Lang") if request else None
        if lang and lang != "en" and not request.query_params.get("raw"):
            for key, value in (getattr(instance, "i18n", None) or {}).get(lang, {}).items():
                if value and key in data:
                    data[key] = value
        if hasattr(instance, "discount_percent"):
            data["effective_discount"], data["promo_title"] = effective_discount(instance, self.context, lang or "en")
        return data


def model_serializer(model, **extra):
    meta = type("Meta", (), {"model": model, "fields": "__all__", **extra})
    bases = (LocalizedMixin, serializers.ModelSerializer) if hasattr(model, "i18n") else (serializers.ModelSerializer,)
    return type(f"{model.__name__}Serializer", bases, {"Meta": meta})


class SiteContentSerializer(serializers.ModelSerializer):
    """The public site settings. The cost rates are business-internal and never leave the server here (Accounting has its own endpoint)."""

    class Meta:
        model = models.SiteContent
        exclude = ["cost_rates"]

    def validate_map_cities(self, value):
        """Which cities of the home page map are green and where a click leads: a known kind of link only, so a typo cannot send visitors elsewhere."""
        if not isinstance(value, dict) or len(value) > 40:
            raise serializers.ValidationError("Choose the cities of the map.")
        clean = {}
        for key, item in value.items():
            if not re.fullmatch(r"[a-z]{3,30}", str(key)) or not isinstance(item, dict):
                raise serializers.ValidationError("A city of the map is not valid.")
            target = str(item.get("target") or "").strip()
            if target and not re.fullmatch(r"/(tours|destinations)/[a-z0-9-]{1,80}(#[a-z]+)?", target):
                raise serializers.ValidationError("A link must lead to a tour or a destination of this website.")
            clean[key] = {"green": bool(item.get("green")), "target": target}
        return clean

    def validate_extra_contacts(self, value):
        """Extra lines for the footer and contact page: a label, a value and an optional link, checked and trimmed."""
        if not isinstance(value, list) or len(value) > 20:
            raise serializers.ValidationError("Add up to 20 lines.")
        clean = []
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each line needs a label and a value.")
            label, text, url = (str(item.get(k) or "").strip() for k in ("label", "value", "url"))
            if not (label or text):
                continue  # an empty row is simply dropped
            if len(label) > 60 or len(text) > 200 or len(url) > 300:
                raise serializers.ValidationError("A line is too long.")
            if url and not url.lower().startswith(("https://", "http://", "tel:", "mailto:", "tg://")):
                raise serializers.ValidationError("A link must start with https://, tel: or mailto:.")
            clean.append({"label": label, "value": text, "url": url})
        return clean


DestinationSerializer = model_serializer(models.Destination)
HotelSerializer = model_serializer(models.Hotel)
FoodSerializer = model_serializer(models.FoodExperience)
TransportSerializer = model_serializer(models.TransportOption)
ContactMessageSerializer = model_serializer(models.ContactMessage, read_only_fields=["status", "created"])
ContactMessageAdminSerializer = model_serializer(models.ContactMessage, read_only_fields=["created"])  # the team can change the status
SavedItemSerializer = model_serializer(models.SavedItem, read_only_fields=["user", "created"])
class BookingSerializer(serializers.ModelSerializer):
    """A booking, with the name of the booked service in the language the admin reads (service_title_local)."""

    class Meta:
        model = models.BookingRequest
        fields = "__all__"

    def to_representation(self, instance):
        from .names import service_name
        data = super().to_representation(instance)
        request = self.context.get("request")
        lang = (request.headers.get("X-Lang") if request else None) or "en"
        data["service_title_local"] = service_name(instance.service_type, instance.service_slug, instance.service_title, lang) if lang != "en" else instance.service_title
        return data

PartnerSerializer = model_serializer(models.Partner, read_only_fields=["user", "status", "admin_notes"])
PromotionSerializer = model_serializer(models.Promotion)
LegalPageSerializer = model_serializer(models.LegalPage)
_PRIVATE = {"email": {"write_only": True}, "reference": {"write_only": True}}
ReviewSerializer = model_serializer(models.Review, read_only_fields=["status", "verified", "created", "tour_title"], extra_kwargs=_PRIVATE)
ReviewAdminSerializer = model_serializer(models.Review, read_only_fields=["created"])


class TourSerializer(model_serializer(models.Tour)):
    price_from_usd = serializers.DecimalField(max_digits=8, decimal_places=2, coerce_to_string=False)
    rating = serializers.DecimalField(max_digits=2, decimal_places=1, coerce_to_string=False)
    entrance_fee_usd = serializers.DecimalField(max_digits=8, decimal_places=2, coerce_to_string=False, allow_null=True, required=False)


class BookingSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BookingRequest
        fields = [
            "service_type", "service_slug", "service_title", "full_name", "email", "phone",
            "travel_date", "end_date", "guests", "details_summary", "special_requests",
            "estimated_total_usd",
        ]
        extra_kwargs = {"estimated_total_usd": {"required": False}}


class ArrivalSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BookingRequest
        fields = ["arrival_date", "arrival_time", "arrival_flight"]
        extra_kwargs = {"arrival_date": {"required": True, "allow_null": False}, "arrival_time": {"required": True, "allow_null": False}, "arrival_flight": {"required": False}}


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role"]

    def get_full_name(self, user):
        return user.get_full_name() or user.username

    def get_role(self, user):
        return "admin" if user.is_staff else "user"


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, data):
        first, _, last = data.get("full_name", "").partition(" ")
        return User.objects.create_user(
            username=data["email"], email=data["email"], password=data["password"],
            first_name=first, last_name=last,
        )
