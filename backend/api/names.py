from . import models

MODELS = {"tour": (models.Tour, "title"), "selection": (models.Tour, "title"), "hotel": (models.Hotel, "name"), "transport": (models.TransportOption, "name")}


def service_name(kind, slug, fallback, lang="uz"):
    """The name of a booked tour, hotel or transport in `lang` (the booking itself keeps the English title)."""
    model, field = MODELS.get(kind, (models.Tour, "title"))
    row = model.objects.filter(slug=slug).first() if slug else None
    if not row:
        return fallback
    return (row.i18n or {}).get(lang, {}).get(field) or getattr(row, field, fallback)
