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


SiteContentSerializer = model_serializer(models.SiteContent)
DestinationSerializer = model_serializer(models.Destination)
HotelSerializer = model_serializer(models.Hotel)
FoodSerializer = model_serializer(models.FoodExperience)
TransportSerializer = model_serializer(models.TransportOption)
ContactMessageSerializer = model_serializer(models.ContactMessage, read_only_fields=["status", "created"])
SavedItemSerializer = model_serializer(models.SavedItem, read_only_fields=["user", "created"])
BookingSerializer = model_serializer(models.BookingRequest)
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
