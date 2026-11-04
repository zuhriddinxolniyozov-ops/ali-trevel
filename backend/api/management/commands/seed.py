from django.core.management.base import BaseCommand

from api import models
from api.management.commands import legal_cancellation, legal_privacy, legal_terms
from api.management.commands.seed_translations import LANGS, PHRASES
from api.management.commands import seed_experiences, seed_hotels, seed_regions
from api.management.commands import seed_locations, seed_package, seed_package_11
from api.management.commands.seed_places import CITY_ITINERARY, OLD_ROUTE_ORDER, PLACES, ROUTE_ORDER  # also adds the place texts to PHRASES

IMG = "https://media.base44.com/images/public/6ae38de40859b796c87648a9/"
IMAGES = {
    "hero": "14ddbab3e_generated_33090cb1.png",
    "samarkand": "6327bf0cb_generated_2203993e.png",
    "bukhara": "780cda9ec_generated_20313d8f.png",
    "khiva": "8054594a1_generated_60aea52c.png",
    "tashkent": "3648aa8bc_generated_495371d6.png",
    "shahrisabz": "e0ba2f5b5_generated_dc4a22bd.png",
    "nurata": "d9ffcddb6_generated_87b80de4.png",
    "plov": "16a581b59_generated_0e96498e.png",
    "yurt": "39a2311cf_generated_02f12d28.png",
    "hotel": "e21221760_generated_94e42112.png",
    "transfer": "dacc3ab31_generated_a2f2a0ee.png",
    "craft": "a2decca86_generated_a9cd7abb.png",
}


def img(key):
    return IMG + IMAGES[key]


DESTINATIONS = [
    ("samarkand", "Samarkand", "Silk Road crossroads", "Turquoise domes, the Registan and a city that has welcomed travellers for 2,500 years.", "3 days", True),
    ("bukhara", "Bukhara", "Holy city of the Silk Road", "A living museum of minarets, trading domes and courtyard tea houses.", "2-3 days", True),
    ("khiva", "Khiva", "Walled desert city", "Itchan Kala, a perfectly preserved walled town of clay and glazed tile.", "2 days", True),
    ("tashkent", "Tashkent", "The modern capital", "Soviet modernism, grand bazaars and the metro's palace-like stations.", "2 days", False),
    ("shahrisabz", "Shahrisabz", "Birthplace of Timur", "The ruined Ak-Saray palace and quiet mountain-foothill streets.", "1 day", False),
    ("nurata", "Nurata Mountains", "Yurt camps & desert", "Stargazing, camel rides and a night in a yurt camp beside Aydarkul lake.", "1-2 days", False),
]

ACTIVITIES = {
    "samarkand": ["Registan Square at golden hour", "Gur-e-Amir mausoleum visit", "Siab bazaar tasting walk"],
    "bukhara": ["Poi Kalon ensemble and Ark fortress", "Trading domes and old bazaar walk", "Evening tea in a courtyard house"],
    "khiva": ["Itchan Kala walled city walk", "Islam Khoja minaret climb", "Sunset over the city walls"],
    "tashkent": ["Chorsu bazaar and plov centre", "Tashkent metro stations tour", "Khast-Imam old town"],
    "shahrisabz": ["Ak-Saray palace ruins", "Dorus-Saodat complex", "Mountain-foothill drive"],
    "nurata": ["Aydarkul lake and yurt camp", "Petroglyphs of Sarmish", "Stargazing and camel ride"],
}

TOURS = [
    ("silk-road-multi-city-tour", "Silk Road Multi-City Tour", "samarkand", "Samarkand", "Multi-city", "9 days", "Private / small group", "Three cities in nine days with time to sit in tea houses.", "samarkand", 1290, 4.9, 38),
    ("bukhara-old-city-guided-tour", "Bukhara Old City Guided Tour", "bukhara", "Bukhara", "Culture", "1 day", "Private", "Courtyards, trading domes and a family cooking class with a local guide.", "bukhara", 85, 4.8, 54),
    ("nurata-mountains-cultural-journey", "Nurata Mountains Cultural Journey", "nurata", "Nurata", "Adventure", "2 days", "Small group", "Desert, petroglyphs and a night in a yurt camp under the stars.", "yurt", 210, 4.9, 27),
    ("samarkand-registan-and-bazaar", "Samarkand Registan & Bazaar Walk", "samarkand", "Samarkand", "Culture", "Half day", "Private", "The Registan at golden hour and the Siab bazaar with a local guide.", "samarkand", 55, 4.7, 61),
    ("khiva-walled-city-day", "Khiva Walled City Day", "khiva", "Khiva", "Culture", "1 day", "Private", "Climb the Islam Khoja minaret and wander Itchan Kala's lanes.", "khiva", 70, 4.8, 33),
    ("tashkent-plov-and-metro", "Tashkent Plov & Metro Tour", "tashkent", "Tashkent", "Food", "Half day", "Small group", "The national dish in the plov centre, then the metro's palace-like stations.", "plov", 48, 4.6, 40),
    ("rishton-ceramics-workshop", "Rishton Ceramics Workshop", "tashkent", "Fergana", "Craft", "1 day", "Small group", "Spend a day at the potter's wheel in a Rishton master's studio.", "craft", 95, 4.8, 19),
]

HOTELS = [
    ("registan-heritage-boutique", "Registan Heritage Boutique", "samarkand", "Samarkand", 4, "A courtyard guesthouse a short walk from the Registan.", "hotel", 78),
    ("bukhara-courtyard-house", "Bukhara Courtyard House", "bukhara", "Bukhara", 3, "Family-run rooms around a vine-covered courtyard in the old city.", "hotel", 55),
    ("khiva-caravanserai-inn", "Khiva Caravanserai Inn", "khiva", "Khiva", 3, "Sleep inside the walls of Itchan Kala.", "khiva", 60),
    ("tashkent-grand-residence", "Tashkent Grand Residence", "tashkent", "Tashkent", 5, "A modern five-star in the city centre with an airport shuttle.", "tashkent", 140),
]

FOOD = [
    ("plov", "Plov", "Tashkent", "Rice, lamb, carrot and chickpea cooked in a kazan — Uzbekistan's national dish.", "plov", "Dish"),
    ("samsa", "Samsa", "Samarkand", "Baked pastry filled with lamb and onion, served hot from a tandoor.", "plov", "Street food"),
    ("non", "Samarkand non bread", "Samarkand", "Dense, stamped bread baked on the walls of a clay oven.", "craft", "Bread"),
    ("plov-masterclass", "Bukhara cooking class", "Bukhara", "Cook plov with a family in their courtyard.", "plov", "Experience"),
]

TRANSPORT = [
    ("sedan-transfer", "Airport transfer — Sedan", "Chevrolet Cobalt", 3, 3, "Meet & greet with your name on a sign.", "transfer", 18, 4),
    ("minivan-transfer", "Airport transfer — Minivan", "Hyundai Starex", 7, 5, "Room for families and luggage.", "transfer", 35, 5),
    ("intercity-driver", "Intercity driver (per day)", "Sedan or SUV", 3, 3, "Private driver between cities.", "transfer", 95, 10),
]

# One city tour plus the historical places of Samarkand, each shown as its own tour card.
CITY_TOUR_SLUG = "samarkand-city-tour"
LANGUAGES = ["English", "Russian", "Uzbek"]
CITY_FEES = {name: fee for _, name, fee, *_ in PLACES}
CITY_TOUR = dict(
    title="Samarkand City Tour", destination_slug="samarkand", destination_name="Samarkand", category="Culture",
    duration_label="2 days", group_type="Small group", tour_type="car", max_travelers=21, languages=LANGUAGES,
    transport_included=True, tickets_included=False, pickup_included=True, guide="ALI TRAVEL team",
    meeting_point="Samarkand airport", price_from_usd=209, rating=4.9, review_count=0,
    summary="Two days through Samarkand's must-see places with a local guide, taxi rides between stops and pickup from the airport.",
    description=(
        "Walk and ride through the highlights of Samarkand: the Registan, Gur-e-Amir, Bibi-Khanym, Siyob Bazaar, Shah-i-Zinda, "
        "Ulugh Beg, the Silk Road Eternal City and the Imam al-Bukhari complex. Your guide from the ALI TRAVEL team meets you at "
        "Samarkand airport and stays with you all day. Taxis between the stops are included; entrance tickets are paid separately at each site."
    ),
    route=[f"{name} | {CITY_FEES[name]}" for name in ROUTE_ORDER], itinerary=CITY_ITINERARY,
    included=["Local guide service", "Walking tour", "One meal per day", "Two days of hotel accommodation", "Trip to 7 historical places", "Taxi service between the places", "Airport pickup"],
    excluded=["Entrance tickets", "Lunch", "Dinner"],
)

TRANSLATABLE = {
    models.Destination: ["name", "region", "summary", "description", "suggested_duration", "activities", "highlights"],
    models.Tour: ["title", "destination_name", "category", "duration_label", "group_type", "summary", "description", "highlights",
                  "included", "excluded", "guide", "meeting_point", "route", "story", "location_note"],
    models.Hotel: ["name", "destination_name", "summary", "description", "amenities"],
    models.FoodExperience: ["name", "kind", "destination_name", "summary"],
    models.TransportOption: ["name", "vehicle", "summary"],
}


def translate(value, column):
    """Translate a text or a list of texts; ``None`` when nothing in it is known. Route lines keep their ``| fee``."""
    def one(text):
        name, bar, fee = text.partition("|")
        found = PHRASES.get(name.strip())
        if not found:
            return None
        return f"{found[column]} | {fee.strip()}" if bar else found[column]

    if isinstance(value, str):
        return one(value) if value else None
    if isinstance(value, list) and value:
        done = [one(item) if isinstance(item, str) else None for item in value]
        return [d or item for d, item in zip(done, value)] if any(done) else None
    return None


def apply_translations():
    """Fill missing per-language fields from the phrase book; never touches text an admin already translated."""
    changed = 0
    for model, fields in TRANSLATABLE.items():
        for obj in model.objects.all():
            data = dict(obj.i18n or {})
            touched = False
            for column, lang in enumerate(LANGS):
                entry = dict(data.get(lang, {}))
                for field in fields:
                    if entry.get(field):
                        continue
                    translated = translate(getattr(obj, field, None), column)
                    if translated:
                        entry[field] = translated
                        touched = True
                data[lang] = entry
            if touched:
                obj.i18n = {k: v for k, v in data.items() if v}
                obj.save(update_fields=["i18n"])
                changed += 1
    return changed


LEGAL_PAGES = {"privacy": legal_privacy, "terms": legal_terms, "cancellation": legal_cancellation}


def load_legal_pages():
    """Create the three legal pages (English + Uzbek + Russian). Pages an admin has edited are left alone."""
    created = 0
    for slug, source in LEGAL_PAGES.items():
        page = models.LegalPage.objects.filter(slug=slug).first()
        if page:
            continue
        models.LegalPage.objects.create(
            slug=slug, title=source.EN[0], body=source.EN[1],
            i18n={"uz": {"title": source.UZ[0], "body": source.UZ[1]}, "ru": {"title": source.RU[0], "body": source.RU[1]}})
        created += 1
    return created


class Command(BaseCommand):
    help = "Load sample catalogue content (marked as demonstration data)."

    def add_arguments(self, parser):
        parser.add_argument("--extras", action="store_true", help="Only add the Samarkand tours and fill missing translations; leave existing records untouched.")

    def add_extras(self):
        """Create the Samarkand tours and bring unedited ones up to date. Text an admin has changed is never overwritten."""
        city = models.Tour.objects.filter(slug=CITY_TOUR_SLUG).first()
        if not city:
            city = models.Tour.objects.create(slug=CITY_TOUR_SLUG, image_url=img("samarkand"), featured=True, **CITY_TOUR)
        else:
            changed = []
            if city.duration_label == "Flexible hours":
                city.duration_label = "2 days"
                changed.append("duration_label")
            old_route = [f"{name} | {CITY_FEES[name]}" for name in OLD_ROUTE_ORDER]
            if city.route == old_route:  # still the order first seeded: follow the plan's visiting order
                city.route = CITY_TOUR["route"]
                changed.append("route")
            if not city.itinerary:
                city.itinerary = CITY_ITINERARY
                changed.append("itinerary")
            self.refresh(city, changed)

        for suffix, place, fee, summary, about, story in PLACES:
            tour = models.Tour.objects.filter(slug=suffix).first()
            if not tour:
                models.Tour.objects.create(slug=suffix, **dict(
                    CITY_TOUR, title=f"{place} Tour", summary=summary, description=about, story=story, tour_type="walking",
                    duration_label="Flexible hours", price_from_usd=0, featured=False, image_url=img("samarkand"), parent_slug=CITY_TOUR_SLUG,
                    entrance_fee_usd=fee, route=[f"{place} | {fee}"], itinerary=[], included=["Local guide service", "Walking tour", "Taxi service", "Airport pickup"],
                    excluded=["Entrance ticket", "Lunch", "Dinner"]))
                continue
            changed = []
            if tour.description == tour.summary:  # the first seed copied the summary into the description
                tour.description = about
                changed.append("description")
            if not tour.story:
                tour.story = story
                changed.append("story")
            self.refresh(tour, changed)
        self.add_regions()
        self.add_experiences()
        self.add_hotels()
        self.add_package()
        self.add_locations()
        self.stdout.write(f"Legal pages created: {load_legal_pages()}.")
        self.stdout.write(f"Translations added to {apply_translations()} records.")

    # --- the other regions of Uzbekistan -------------------------------------------------
    RENAMES = {"khiva": ("khorezm", "Khiva", "Khorezm"), "shahrisabz": ("kashkadarya", "Shahrisabz", "Kashkadarya")}

    @staticmethod
    def drop_fields(obj, fields):
        """Forget saved translations of fields whose English text changed; they are regenerated from the phrase book."""
        i18n = {lang: {k: v for k, v in entry.items() if k not in fields} for lang, entry in (obj.i18n or {}).items()}
        obj.i18n = {lang: entry for lang, entry in i18n.items() if entry}

    def rename_regions(self):
        """Khiva is shown as the Khorezm region and Shahrisabz as the Kashkadarya region; records and links follow."""
        for old, (new, old_name, new_name) in self.RENAMES.items():
            dest = models.Destination.objects.filter(slug=old).first()
            if dest and not models.Destination.objects.filter(slug=new).exists():
                dest.slug = new
                if dest.name == old_name:
                    dest.name = new_name
                    self.drop_fields(dest, ["name"])
                dest.save()
            for model in (models.Tour, models.Hotel):
                for obj in model.objects.filter(destination_slug=old):
                    obj.destination_slug = new
                    if obj.destination_name == old_name:
                        obj.destination_name = new_name
                        self.drop_fields(obj, ["destination_name"])
                    obj.save()
            for obj in models.FoodExperience.objects.filter(destination_name=old_name):
                obj.destination_name = new_name
                self.drop_fields(obj, ["destination_name"])
                obj.save()

    def add_regions(self):
        """Create the regional tours with their places, plans, destinations and sample hotels. Existing records are left as they are."""
        self.rename_regions()
        order = {"samarkand": 0}
        for i, r in enumerate(seed_regions.REGIONS, start=1):
            order[r["slug"]] = i
        for slug, position in order.items():  # the seven regions are all shown on the home page, in this order
            models.Destination.objects.filter(slug=slug).update(featured=True, order=position)
        models.Destination.objects.filter(slug="nurata", order__lt=order["karakalpakstan"] + 1).update(order=9)
        created = 0
        for r in seed_regions.REGIONS:
            image = img(r["image"]) if r["image"] in IMAGES else seed_regions.photo(r["image_file"])
            nd = r.get("new_destination")
            if nd and not models.Destination.objects.filter(slug=r["slug"]).exists():
                models.Destination.objects.create(
                    slug=r["slug"], name=r["name"], region=nd["region"], summary=nd["summary"], description=nd["summary"], image_url=image,
                    suggested_duration=nd["duration"], featured=True, order=order[r["slug"]], activities=[a for a, _ in nd["activities"]])
            places = r["places"]
            route = [f"{p[1]} | {p[3]}" for p in places]
            plural = len(places)
            stay = {1: "Round-trip transfer from Samarkand", 2: "Two days of hotel accommodation", 3: "Three days of hotel accommodation"}[r["days"]]
            region_tour = dict(
                CITY_TOUR, title=r["title"], destination_slug=r["slug"], destination_name=r["name"], duration_label=f"{r['days']} day{'s' if r['days'] > 1 else ''}",
                meeting_point=r["meeting"], price_from_usd=r["price"], featured=False,
                summary=seed_regions.SUMMARY_EN.format(region=r["name"]),
                description=seed_regions.DESCRIPTION_EN.format(region=r["name"], places=", ".join(p[1] for p in places), meeting=r["meeting"]),
                route=route, itinerary=[{"day": d + 1, "items": items} for d, items in enumerate(r["plan"])],
                included=["Local guide service", "Walking tour", "One meal per day", stay, f"Trip to {plural} historical places", "Taxi service between the places", "Airport pickup"],
                excluded=["Entrance tickets", "Lunch", "Dinner"])
            if not models.Tour.objects.filter(slug=r["city_slug"]).exists():
                models.Tour.objects.create(slug=r["city_slug"], image_url=image, **region_tour)
                created += 1
            for slug, name, names, fee, filename, summary, about, story, *_ in places:
                if models.Tour.objects.filter(slug=slug).exists():
                    continue
                models.Tour.objects.create(slug=slug, **dict(
                    region_tour, title=f"{name} Tour", summary=summary, description=about, story=story, tour_type="walking",
                    duration_label="Flexible hours", price_from_usd=0, image_url=seed_regions.photo(filename), parent_slug=r["city_slug"],
                    entrance_fee_usd=fee, route=[f"{name} | {fee}"], itinerary=[], included=["Local guide service", "Walking tour", "Taxi service", "Airport pickup"],
                    excluded=["Entrance ticket", "Lunch", "Dinner"]))
                created += 1
        for slug, name, dslug, dname, stars, summary, price in seed_regions.HOTELS:
            if not models.Hotel.objects.filter(slug=slug).exists():
                models.Hotel.objects.create(slug=slug, name=name, destination_slug=dslug, destination_name=dname, stars=stars, summary=summary,
                                            description=summary, image_url=img("hotel"), price_from_usd=price,
                                            amenities=["Breakfast included", "Wi-Fi", "Air conditioning"])
        self.stdout.write(f"Regional tours and places created: {created}.")

    def add_hotels(self):
        """Create the real hotels, guesthouses and hostels; the made-up sample listings are archived the first time. Existing hotels are untouched."""
        created, per_destination = 0, {}
        for slug, name, city, kind, stars, price, basis, extra, amenities in seed_hotels.HOTELS:
            destination, destination_name, _, _ = seed_hotels.CITIES[city]
            position = per_destination[destination] = per_destination.get(destination, -1) + 1
            if models.Hotel.objects.filter(slug=slug).exists():
                continue
            summary, _ = seed_hotels.summary_for(city, kind, stars, extra)
            description, _ = seed_hotels.description_for(slug, city, kind, stars, extra, basis)
            cover, more, illustrative = seed_hotels.gallery_for(slug, destination, position, kind)
            models.Hotel.objects.create(
                slug=slug, name=name, destination_slug=destination, destination_name=destination_name, stars=stars, property_type=kind,
                price_basis=basis, summary=summary, description=description, image_url=cover, gallery=more, photos_illustrative=illustrative,
                price_from_usd=price, amenities=amenities or [], rating=0, is_demo=False, status="published")
            created += 1
        if created:
            models.Hotel.objects.filter(slug__in=seed_hotels.SAMPLE_SLUGS, status="published").update(status="archived")
        self.stdout.write(f"Hotels created: {created}.")

    def add_package(self):
        """Create the 7-day Silk Road package with its extra places on the road, and give the Samarkand places real photographs."""
        created = 0
        for parent, slug, name, fee, filename, summary, about, story in (
                [(seed_package.SLUG, *p[:7]) for p in seed_package.NEW_PLACES] + [(seed_package_11.SLUG, *p[:7]) for p in seed_package_11.NEW_PLACES]):
            if models.Tour.objects.filter(slug=slug).exists():
                continue
            fields = dict(CITY_TOUR, title=f"{name} Tour", destination_slug="", destination_name="Uzbekistan", summary=summary, description=about, story=story,
                          tour_type="walking", duration_label="Flexible hours", price_from_usd=0, featured=False, image_url=seed_regions.photo(filename),
                          parent_slug=parent, entrance_fee_usd=fee, route=[f"{name} | {fee}" if fee is not None else name], itinerary=[],
                          included=["Local guide service", "Walking tour", "Taxi service", "Airport pickup"], excluded=["Entrance ticket", "Lunch", "Dinner"])
            models.Tour.objects.create(slug=slug, **fields)
            created += 1
        if not models.Tour.objects.filter(slug=seed_package.SLUG).exists():
            models.Tour.objects.create(slug=seed_package.SLUG, **seed_package.package_fields(CITY_TOUR))
            created += 1
        if not models.Tour.objects.filter(slug=seed_package_11.SLUG).exists():
            models.Tour.objects.create(slug=seed_package_11.SLUG, **seed_package_11.package_fields(CITY_TOUR))
            created += 1
        for slug, filename in seed_package.PLACE_PHOTOS.items():
            place = models.Tour.objects.filter(slug=slug, image_url__contains=seed_package.PLACEHOLDER).first()
            if place:
                place.image_url = seed_regions.photo(filename)
                place.save(update_fields=["image_url"])
        self.stdout.write(f"Package and road places created: {created}.")

    def add_locations(self):
        """Give the places of the tours their exact location (only where none is set yet, so an admin's correction stays)."""
        done = 0
        for slug, (lat, lon, note) in seed_locations.LOCATIONS.items():
            place = models.Tour.objects.filter(slug=slug, latitude__isnull=True).first()
            if place:
                place.latitude, place.longitude, place.location_note = lat, lon, note
                place.save(update_fields=["latitude", "longitude", "location_note"])
                done += 1
        self.stdout.write(f"Places located: {done}.")

    def add_experiences(self):
        """Create the hands-on food classes of Samarkand (non baking, plov cooking, both). Existing records are left alone."""
        created = 0
        for e in seed_experiences.EXPERIENCES:
            existing = models.Tour.objects.filter(slug=e["slug"]).first()
            if existing:  # created by an earlier version: update the wording unless an admin changed it
                self.refresh(existing, seed_experiences.refresh_changes(existing, e))
                continue
            models.Tour.objects.create(
                slug=e["slug"], title=e["title"], destination_slug="samarkand", destination_name="Samarkand", category="Food",
                duration_label=e["duration"], group_type="Small group", tour_type="workshop", group_pricing=False, max_travelers=8, languages=LANGUAGES,
                transport_included=True, tickets_included=True, pickup_included=True, guide=e["guide"], meeting_point=seed_experiences.HERE,
                price_from_usd=e["price"], review_count=0, summary=e["summary"], description=e["description"], story=e["story"],
                highlights=[h[0] for h in e["highlights"]], included=[i[0] for i in e["included"]], excluded=["Tips (optional)", "Personal expenses"],
                itinerary=[{"day": 1, "items": e["plan"]}], route=[], image_url=seed_regions.photo(e["image"]))
            created += 1
        self.stdout.write(f"Food experiences created: {created}.")

    @staticmethod
    def refresh(tour, fields):
        """Save changed fields and drop their old translations so they are regenerated for the new English text."""
        if not fields:
            return
        i18n = {lang: {k: v for k, v in entry.items() if k not in fields} for lang, entry in (tour.i18n or {}).items()}
        tour.i18n = {lang: entry for lang, entry in i18n.items() if entry}
        tour.save(update_fields=[*fields, "i18n"])

    def handle(self, *args, **options):
        if options["extras"]:
            self.add_extras()
            self.stdout.write(self.style.SUCCESS("Extras loaded."))
            return
        models.SiteContent.objects.get_or_create(pk=1, defaults={
            "hero_eyebrow": "Samarkand · Bukhara · Khiva · Tashkent",
            "hero_title": "Discover the Magic of Uzbekistan",
            "hero_subtitle": "Unforgettable journeys, authentic experiences, and seamless travel — all in one place.",
            "email": "alitravel004@gmail.com",
            "phone_primary": "+998942222498",
            "phone_secondary": "+998938653300",
            "instagram_url": "https://www.instagram.com/al1_travel1",
            "telegram_url": "https://t.me/al1_travel1",
            "facebook_url": "https://www.facebook.com/share/1CQmva9Sds/",
            "youtube_url": "https://www.youtube.com/@Alitravel_uz",
            "x_url": "https://x.com/alitraveluz",
        })
        for i, (slug, name, region, summary, duration, featured) in enumerate(DESTINATIONS):
            dest, _ = models.Destination.objects.update_or_create(slug=slug, defaults=dict(
                name=name, region=region, summary=summary, description=summary,
                image_url=img(slug), suggested_duration=duration, featured=featured, order=i,
            ))
            if not dest.activities:  # never overwrite activities an admin has edited
                dest.activities = ACTIVITIES.get(slug, [])
                dest.save(update_fields=["activities"])
        for i, (slug, title, dslug, dname, cat, dur, group, summary, image, price, rating, reviews) in enumerate(TOURS):
            models.Tour.objects.update_or_create(slug=slug, defaults=dict(
                title=title, destination_slug=dslug, destination_name=dname, category=cat,
                duration_label=dur, group_type=group, summary=summary, description=summary,
                image_url=img(image), price_from_usd=price, rating=rating, review_count=reviews,
                featured=i < 3, included=["Licensed local guide", "Private transport", "Bottled water"],
                excluded=["International flights", "Personal expenses"],
            ))
        for slug, name, dslug, dname, stars, summary, image, price in HOTELS:
            models.Hotel.objects.update_or_create(slug=slug, defaults=dict(
                name=name, destination_slug=dslug, destination_name=dname, stars=stars, summary=summary,
                description=summary, image_url=img(image), price_from_usd=price,
                amenities=["Breakfast included", "Wi-Fi", "Air conditioning"],
            ))
        for slug, name, dname, summary, image, kind in FOOD:
            models.FoodExperience.objects.update_or_create(slug=slug, defaults=dict(
                name=name, destination_name=dname, summary=summary, image_url=img(image), kind=kind,
            ))
        for slug, name, vehicle, cap, included, summary, image, base, extra in TRANSPORT:
            models.TransportOption.objects.update_or_create(slug=slug, defaults=dict(
                name=name, vehicle=vehicle, capacity=cap, included_passengers=included, summary=summary,
                image_url=img(image), base_price_usd=base, extra_passenger_usd=extra,
            ))
        self.add_extras()
        self.stdout.write(self.style.SUCCESS("Sample content loaded."))
