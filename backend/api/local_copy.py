"""The local (so'm) site: copying the global site into it once, and keeping its automatic prices in step with the dollar rate.

Prices a traveller pays start 30% below the dollar price (market.to_local_price); what things cost the company is converted
without a discount (market.to_local_cost). A copied listing remembers its dollar prices in ``price_source`` and follows the
Central Bank rate every day while ``price_auto`` is on; an admin who types a price on the local site switches that off.
"""
import datetime
import re
from decimal import Decimal

from django.db import transaction

from . import models
from .market import GLOBAL, LOCAL, fetch_cbu_rate, to_local_cost, to_local_price, use

CATALOGUES = (models.Destination, models.Tour, models.Hotel, models.FoodExperience, models.TransportOption)
PRICE_FIELDS = ("price_from_usd", "entrance_fee_usd", "base_price_usd", "extra_passenger_usd")
COST_RATE_KEYS = ("guide_per_day", "car_per_day", "hotel_per_room_night", "meals_per_person_day")   # money; the rest are counts and percents
FEE = re.compile(r"^(?P<name>[^|]*)\|\s*(?P<fee>\d+(?:\.\d+)?)\s*$")


def _route(lines, rate, factor):
    """'Registan Square | 16' -> 'Registan Square | 40000' (the entrance ticket in so'm)."""
    out = []
    for line in lines or []:
        match = FEE.match(str(line))
        out.append(f"{match['name'].rstrip()} | {int(to_local_price(match['fee'], rate, factor))}" if match else line)
    return out


def _snapshot(row):
    """The dollar prices of a global listing, kept on its local copy."""
    source = {f: (None if getattr(row, f) is None else str(getattr(row, f))) for f in PRICE_FIELDS if hasattr(row, f)}
    if hasattr(row, "route"):
        source["route"] = list(row.route or [])
        source["i18n_route"] = {lang: list(values["route"]) for lang, values in (row.i18n or {}).items() if isinstance(values, dict) and values.get("route")}
    if hasattr(row, "cost_items"):
        source["cost_items"] = list(row.cost_items or [])
    return source


def apply_rate(row, rate, factor):
    """Recompute the so'm prices of a local listing from the dollar prices it remembers."""
    source = row.price_source or {}
    for field in PRICE_FIELDS:
        if field in source:
            setattr(row, field, to_local_price(source[field], rate, factor) if source[field] is not None else None)
    if "route" in source:
        row.route = _route(source["route"], rate, factor)
        i18n = dict(row.i18n or {})
        for lang, lines in (source.get("i18n_route") or {}).items():
            i18n[lang] = {**i18n.get(lang, {}), "route": _route(lines, rate, factor)}
        row.i18n = i18n
    if "cost_items" in source:
        row.cost_items = [{**item, "amount_usd": float(to_local_cost(item.get("amount_usd") or 0, rate))} for item in source["cost_items"]]


def _copy(row, **changes):
    row.pk = None
    row.id = None
    row.market = LOCAL
    row._state.adding = True
    for key, value in changes.items():
        setattr(row, key, value)
    return row


@transaction.atomic
def make_local(rate):
    """Copy everything the admin manages on the global site into the local site (only what the local site does not have yet).

    Bookings, payments, messages, partners and reviews are not copied: they belong to the people who used the global site.
    Returns {what: how many rows were added}.
    """
    rate = Decimal(str(rate))
    added = {}
    with use(LOCAL):
        if not models.SiteContent.objects.exists():
            site = models.SiteContent.everywhere.filter(market=GLOBAL).order_by("pk").first() or models.SiteContent(market=GLOBAL)
            rates = dict(site.cost_rates or {})
            for key in COST_RATE_KEYS:
                if key in rates:
                    rates[key] = float(to_local_cost(rates[key], rate))
            _copy(site, cost_rates=rates, usd_rate=rate, usd_rate_date=datetime.date.today(), deposit_amount=Decimal("13000")).save()   # the $1 deposit in so'm
            added["settings"] = 1
        factor = models.SiteContent.current().local_price_factor
        have = set(models.SiteText.objects.values_list("lang", "key"))
        texts = [_copy(x) for x in models.SiteText.everywhere.filter(market=GLOBAL) if (x.lang, x.key) not in have]
        models.SiteText.objects.bulk_create(texts)
        added["texts"] = len(texts)
        have = set(models.LegalPage.objects.values_list("slug", flat=True))
        pages = [_copy(x) for x in models.LegalPage.everywhere.filter(market=GLOBAL) if x.slug not in have]
        models.LegalPage.objects.bulk_create(pages)
        added["legal pages"] = len(pages)
        if not models.Promotion.objects.exists():
            promos = [_copy(x) for x in models.Promotion.everywhere.filter(market=GLOBAL)]
            models.Promotion.objects.bulk_create(promos)
            added["promotions"] = len(promos)
        for model in CATALOGUES:
            have = set(model.objects.values_list("slug", flat=True))
            count = 0
            for row in model.everywhere.filter(market=GLOBAL).order_by("pk"):
                if row.slug in have:
                    continue
                source = _snapshot(row)
                copy = _copy(row, price_auto=bool(source), price_source=source)
                apply_rate(copy, rate, factor)
                if model is models.Tour:
                    without_guide(copy)
                copy.save()
                count += 1
            added[model._meta.verbose_name_plural] = count
    return added


def update_rate(rate=None):
    """Read today's Central Bank rate and move every automatic local price to it. Returns the rate, or None when it could not be read."""
    rate = rate or fetch_cbu_rate()
    if not rate:
        return None
    with use(LOCAL):
        site = models.SiteContent.objects.order_by("pk").first()
        if not site:
            return None   # the local site was never created
        site.usd_rate, site.usd_rate_date = rate, datetime.date.today()
        site.save(update_fields=["usd_rate", "usd_rate_date"])
        for model in CATALOGUES:
            for row in model.objects.filter(price_auto=True):
                apply_rate(row, rate, site.local_price_factor)
                row.save()
    return rate


@transaction.atomic
def set_local_prices(slug, price):
    """Make the local tour ``slug`` cost ``price`` so'm and move every other copied price by the same proportion.

    Every copied listing follows the rate again afterwards (prices typed by hand before are replaced too). Returns the new factor.
    """
    with use(LOCAL):
        site = models.SiteContent.current()
        tour = models.Tour.objects.get(slug=slug)
        dollars = Decimal(str(tour.price_source["price_from_usd"]))
        factor = (Decimal(str(price)) / (dollars * site.usd_rate)).quantize(Decimal("0.00001"))
        site.local_price_factor = factor
        site.save(update_fields=["local_price_factor"])
        for model in CATALOGUES:
            for row in model.objects.exclude(price_source={}):
                apply_rate(row, site.usd_rate, factor)
                row.price_auto = True
                row.save()
    return factor


# The local site's tours do not include a guide: a traveller who wants one asks for it in the booking form (extra payment).
GUIDE_ITEM = re.compile(r"guide|\bgid|гид|guía|reiseleiter", re.IGNORECASE)
NO_GUIDE = {
    "en": "Guide (on request, extra payment)", "uz": "Gid (xohlasangiz, qo'shimcha to'lov evaziga)", "ru": "Гид (по желанию, за доплату)",
    "fr": "Guide (sur demande, avec supplément)", "de": "Guide (auf Wunsch, gegen Aufpreis)", "es": "Guía (a petición, con pago adicional)",
}
# the short descriptions of the copied tours, without the guide
SUMMARY_FIXES = {
    "en": ((" with a local guide, taxi rides", " with taxi rides"), (" with a local guide.", ".")),
    "uz": (("mahalliy gid, joylar", "joylar"), ("Mahalliy gid bilan ", ""), ("va mahalliy gid bilan ", "va "), ("mahalliy gid bilan ", "")),
    "ru": ((" с местным гидом, такси", " с такси"), (" с местным гидом, поездки", ": поездки"), (" с местным гидом.", ".")),
    "fr": ((" avec un guide local, taxi", " avec taxi"), (" avec un guide local.", ".")),
    "de": ((" mit lokalem Guide, Taxifahrten", " mit Taxifahrten"), (" mit einem lokalen Guide.", ".")),
    "es": ((" con guía local, taxi", " con taxi"), (" con un guía local.", ".")),
}


def _fix(text, lang):
    for old, new in SUMMARY_FIXES.get(lang, ()):
        text = text.replace(old, new)
    return text[:1].upper() + text[1:] if text else text


def without_guide(tour):
    """Take the guide out of what a local tour includes (it becomes an extra on request). Classes keep their cook or baker."""
    if tour.tour_type == "workshop":
        return
    changed = [x for x in tour.included if GUIDE_ITEM.search(x)]
    if changed or tour.guide == "ALI TRAVEL team":
        tour.included = [x for x in tour.included if not GUIDE_ITEM.search(x)]
        if NO_GUIDE["en"] not in tour.excluded:
            tour.excluded = [NO_GUIDE["en"], *tour.excluded]
        tour.guide = ""
    tour.summary, tour.description = _fix(tour.summary, "en"), _fix(tour.description, "en")
    i18n = {}
    for lang, values in (tour.i18n or {}).items():
        values = dict(values) if isinstance(values, dict) else values
        if isinstance(values, dict):
            if values.get("included"):
                values["included"] = [x for x in values["included"] if not GUIDE_ITEM.search(x)]
                excluded = values.get("excluded") or []
                values["excluded"] = excluded if NO_GUIDE.get(lang) in excluded else [NO_GUIDE.get(lang, NO_GUIDE["en"]), *excluded]
            for key in ("summary", "description"):
                if values.get(key):
                    values[key] = _fix(values[key], lang)
            values.pop("guide", None)
        i18n[lang] = values
    tour.i18n = i18n


def remove_guide_from_local_tours():
    with use(LOCAL):
        count = 0
        for tour in models.Tour.objects.all():
            before = (tour.included, tour.summary, tour.i18n, tour.guide)
            without_guide(tour)
            if (tour.included, tour.summary, tour.i18n, tour.guide) != before:
                tour.save()
                count += 1
    return count
