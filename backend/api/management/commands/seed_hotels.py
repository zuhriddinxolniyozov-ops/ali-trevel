"""Real places to stay in Uzbekistan: 4–5 star hotels, ordinary hotels, boutique hotels, guesthouses and hostels.

The names, classes and approximate "from" prices were collected from public booking-site listings (Booking.com, Tripadvisor, Trip.com,
Expedia, Hostelz, Kayak and similar) in 2025–2026. Booking-site prices change with dates and season and the sites often disagree, so each
price here is the lowest realistic nightly rate rounded to a whole dollar (per room, or per dorm bed for hostels) and is shown on the
website as indicative; the team confirms the exact rate for the dates requested. Stars follow the booking sites and can differ between them.

Photos: Wikimedia Commons has real photographs of only a few of these businesses (Orient Star Khiva, LOTTE Tashkent Palace, Hyatt Regency
Tashkent), so those use their own. Every other gallery shows photographs of similar places to stay in Uzbekistan (hotel rooms, courtyards, entrances,
hostel signs) and the page says so, until the team uploads the property's own photos in the admin panel. Monuments are never used as hotel photos.
"""
from api.management.commands.hotel_photos import FILES
from api.management.commands.seed_regions import photo
from api.management.commands.seed_translations import PHRASES

# city key -> (destination slug, destination name, English name, (uz "-dagi" form, ru "in" form, fr, de, es))
CITIES = {
    "samarkand": ("samarkand", "Samarkand", "Samarkand", ("Samarqanddagi", "Самарканде", "Samarcande", "Samarkand", "Samarcanda")),
    "bukhara": ("bukhara", "Bukhara", "Bukhara", ("Buxorodagi", "Бухаре", "Boukhara", "Buchara", "Bujará")),
    "khiva": ("khorezm", "Khorezm", "Khiva", ("Xivadagi", "Хиве", "Khiva", "Chiwa", "Jiva")),
    "tashkent": ("tashkent", "Tashkent", "Tashkent", ("Toshkentdagi", "Ташкенте", "Tachkent", "Taschkent", "Taskent")),
    "kokand": ("fergana", "Fergana Valley", "Kokand", ("Qo'qondagi", "Коканде", "Kokand", "Kokand", "Kokand")),
    "margilan": ("fergana", "Fergana Valley", "Margilan", ("Marg'ilondagi", "Маргилане", "Marguilan", "Margilan", "Margilán")),
    "fergana": ("fergana", "Fergana Valley", "Fergana", ("Farg'onadagi", "Фергане", "Ferghana", "Fergana", "Fergana")),
    "nukus": ("karakalpakstan", "Karakalpakstan", "Nukus", ("Nukusdagi", "Нукусе", "Noukous", "Nukus", "Nukus")),
    "shahrisabz": ("kashkadarya", "Kashkadarya", "Shahrisabz", ("Shahrisabzdagi", "Шахрисабзе", "Chakhrisabz", "Schachrisabs", "Shahrisabz")),
}

# (property type, stars) -> English phrase and its translations (uz, ru, fr, de, es)
TYPES = {
    ("hotel", 5): ("5-star hotel", ("5 yulduzli mehmonxona", "Пятизвёздочный отель", "Hôtel 5 étoiles", "5-Sterne-Hotel", "Hotel de 5 estrellas")),
    ("hotel", 4): ("4-star hotel", ("4 yulduzli mehmonxona", "Четырёхзвёздочный отель", "Hôtel 4 étoiles", "4-Sterne-Hotel", "Hotel de 4 estrellas")),
    ("hotel", 3): ("3-star hotel", ("3 yulduzli mehmonxona", "Трёхзвёздочный отель", "Hôtel 3 étoiles", "3-Sterne-Hotel", "Hotel de 3 estrellas")),
    ("boutique", 3): ("Boutique hotel", ("Butik-mehmonxona", "Бутик-отель", "Hôtel de charme", "Boutique-Hotel", "Hotel boutique")),
    ("guesthouse", 0): ("Guesthouse", ("Mehmon uyi", "Гостевой дом", "Maison d'hôtes", "Gästehaus", "Casa de huéspedes")),
    ("hostel", 0): ("Hostel with dorm beds", ("Umumiy xonada joylari bor yotoqxona", "Хостел с местами в общих номерах", "Auberge de jeunesse avec lits en dortoir", "Hostel mit Betten im Schlafsaal", "Hostal con camas en dormitorio")),
}

# slug, name, city, type, stars, from price (USD per room, or per dorm bed for hostels), price basis, extra fact (en, uz, ru) or None, amenities
HOTELS = [
    # ---- Samarkand
    ("movenpick-samarkand", "Mövenpick Samarkand", "samarkand", "hotel", 5, 114, "room", None, None),
    ("orient-star-samarkand-hotel", "Orient Star Samarkand Hotel", "samarkand", "hotel", 3, 78, "room",
     ("About 2.2 km from the Registan.", "Registondan taxminan 2,2 km.", "Примерно в 2,2 км от Регистана."), None),
    ("grand-samarkand-superior-hotel", "Grand Samarkand Superior Hotel", "samarkand", "hotel", 4, 80, "room",
     ("About 1.9 km from the Registan.", "Registondan taxminan 1,9 km.", "Примерно в 1,9 км от Регистана."), None),
    ("hotel-platan-samarkand", "Hotel Platan", "samarkand", "hotel", 4, 59, "room",
     ("About 1.8 km from the Registan.", "Registondan taxminan 1,8 km.", "Примерно в 1,8 км от Регистана."), None),
    ("emirhan-hotel-samarkand", "Emirhan Hotel", "samarkand", "hotel", 3, 61, "room", None, None),
    ("antica-family-guest-house-samarkand", "Antica Family Guest House", "samarkand", "guesthouse", 0, 50, "room", None, None),
    ("registan-hostel-samarkand", "Registan Hostel", "samarkand", "hostel", 0, 6, "bed", None, None),
    ("backpackers-house-markhaba-samarkand", "Backpackers House Markhaba", "samarkand", "hostel", 0, 9, "bed",
     ("Shared bathrooms on each floor.", "Har qavatda umumiy hammom.", "Общие санузлы на каждом этаже."), None),
    # ---- Bukhara
    ("zargaron-plaza-hotel-bukhara", "Zargaron Plaza Hotel", "bukhara", "hotel", 4, 70, "room", None, None),
    ("minzifa-boutique-hotel-bukhara", "Minzifa Boutique Hotel", "bukhara", "boutique", 3, 55, "room", None, None),
    ("hostel-al-bukhari", "Hostel Al Bukhari", "bukhara", "hostel", 0, 10, "bed", None, None),
    ("bobo-haydar-guest-house-bukhara", "Bobo Haydar Guest House", "bukhara", "guesthouse", 0, 12, "bed",
     ("Dorm beds from about $12; private rooms from about $30.", "Umumiy xonada joy taxminan $12 dan; alohida xona taxminan $30 dan.", "Место в общем номере примерно от $12; отдельная комната примерно от $30."), None),
    ("dervish-hostel-bukhara", "Dervish Hostel", "bukhara", "hostel", 0, 13, "bed",
     ("Private rooms from about $64.", "Alohida xonalar taxminan $64 dan.", "Отдельные номера примерно от $64."), None),
    # ---- Khiva
    ("orient-star-khiva-hotel", "Orient Star Khiva Hotel", "khiva", "hotel", 3, 40, "room",
     ("On Pakhlavon Makhmud street.", "Pahlavon Mahmud ko'chasida.", "На улице Пахлаван Махмуд."), None),
    ("malika-khorezm-hotel-khiva", "Malika Khorezm Hotel", "khiva", "hotel", 3, 41, "room",
     ("About 200 m from Ichan Kala.", "Ichan-Qal'adan taxminan 200 m.", "Примерно в 200 м от Ичан-Калы."), None),
    ("hotel-asia-khiva", "Hotel Asia Khiva", "khiva", "hotel", 3, 44, "room",
     ("About 600 m from the city centre.", "Shahar markazidan taxminan 600 m.", "Примерно в 600 м от центра города."), None),
    # ---- Tashkent
    ("hyatt-regency-tashkent", "Hyatt Regency Tashkent", "tashkent", "hotel", 5, 123, "room", None, None),
    ("lotte-city-hotel-tashkent-palace", "LOTTE City Hotel Tashkent Palace", "tashkent", "hotel", 5, 88, "room", None, None),
    ("holiday-inn-tashkent-city", "Holiday Inn Tashkent City", "tashkent", "hotel", 4, 110, "room", None, None),
    ("garnet-hotel-tashkent", "Garnet Hotel", "tashkent", "hotel", 4, 80, "room", None, None),
    ("anvars-guests-tashkent", "Anvar's Guests", "tashkent", "guesthouse", 0, 38, "room", None, None),
    ("backpackers-tashkent", "Backpackers Tashkent", "tashkent", "hostel", 0, 5, "bed", None, None),
    # ---- Fergana Valley
    ("asia-hotel-fergana", "Asia Hotel Fergana", "fergana", "hotel", 4, 55, "room", None, None),
    ("grand-fergana-hotel", "Grand Fergana Hotel", "fergana", "hotel", 3, 75, "room", None, None),
    ("silk-road-kokand-hotel", "Silk Road Kokand Hotel", "kokand", "hotel", 3, 69, "room", None, None),
    ("atlas-hotel-margilan", "Atlas Hotel", "margilan", "hotel", 3, 52, "room", None, None),
    # ---- Karakalpakstan
    ("karakalpak-palace-hotel-nukus", "Karakalpak Palace Hotel", "nukus", "hotel", 3, 36, "room",
     ("On Islam Karimov avenue.", "Islom Karimov shoh ko'chasida.", "На проспекте Ислама Каримова."), None),
    # ---- Kashkadarya (Shahrisabz)
    ("hotel-kesh-palace-shahrisabz", "Hotel Kesh Palace", "shahrisabz", "hotel", 3, 66, "room",
     ("30 rooms, with breakfast, Wi-Fi and free parking.", "30 xona; nonushta, Wi-Fi va bepul to'xtash joyi.", "30 номеров; завтрак, Wi-Fi и бесплатная парковка."),
     ["Breakfast included", "Wi-Fi", "Free parking"]),
    ("shahzod-guesthouse-homestay-shahrisabz", "Shahzod Guesthouse & Homestay", "shahrisabz", "guesthouse", 0, 48, "room", None, None),
]

# Lowest and highest nightly rates seen on public booking listings in 2025–2026 (USD), where the sources gave a range.
RANGES = {
    "orient-star-samarkand-hotel": (78, 110), "hotel-platan-samarkand": (59, 93), "emirhan-hotel-samarkand": (61, 72),
    "orient-star-khiva-hotel": (40, 50), "malika-khorezm-hotel-khiva": (41, 50), "hotel-asia-khiva": (44, 75),
    "hyatt-regency-tashkent": (123, 268), "lotte-city-hotel-tashkent-palace": (88, 196), "holiday-inn-tashkent-city": (110, 152),
    "asia-hotel-fergana": (55, 96), "silk-road-kokand-hotel": (69, 103), "atlas-hotel-margilan": (52, 84),
    "karakalpak-palace-hotel-nukus": (36, 69), "hotel-kesh-palace-shahrisabz": (66, 83),
}
# the sentence about that range, per language: (template, per room, per dorm bed)
RANGE_TEXT = (
    ("Rates seen on public booking listings in 2025–2026: roughly ${low}–${high} {unit}.", "per room per night", "per dorm bed per night"),
    ("2025–2026-yillardagi ochiq bron e'lonlarida narxlar taxminan ${low}–${high} ({unit}).", "bir xona uchun kecha", "bir joy uchun kecha"),
    ("По публичным объявлениям 2025–2026 годов цены примерно ${low}–${high} ({unit}).", "за номер в сутки", "за место в сутки"),
    ("Tarifs relevés dans des annonces publiques en 2025–2026 : environ {low}–{high} $ ({unit}).", "par chambre et par nuit", "par lit et par nuit"),
    ("In öffentlichen Angeboten 2025–2026 gesehene Preise: etwa {low}–{high} $ ({unit}).", "pro Zimmer und Nacht", "pro Bett und Nacht"),
    ("Tarifas vistas en anuncios públicos en 2025–2026: aproximadamente {low}–{high} $ ({unit}).", "por habitación y noche", "por cama y noche"),
)

# The earlier made-up sample listings are put away (archived) once real hotels exist.
SAMPLE_SLUGS = ["registan-heritage-boutique", "bukhara-courtyard-house", "khiva-caravanserai-inn", "tashkent-grand-residence",
                "shahrisabz-courtyard-guesthouse", "kokand-silk-road-inn", "nukus-museum-view-hotel"]

# Photographs published by the hotel group itself (Accor) for Mövenpick Samarkand: cover first, then the gallery.
DIRECT_PHOTOS = {
    "movenpick-samarkand": [f"https://www.ahstatic.com/photos/c076_{name}.jpg" for name in
                            ("ho_02_p_1024x768", "ro_02_p_2048x1536", "su_02_p_2048x1536", "rs_00_p_2048x1536", "rotwc_00_p_2048x1536")],
}

# Photographs of the property itself (keys of hotel_photos.FILES). With three or more the gallery shows only these.
OWN_PHOTOS = {
    "orient-star-khiva-hotel": ["khiva_courtyard", "khiva_room", "khiva_room2", "khiva_restaurant", "khiva_courtyard2"],
    "lotte-city-hotel-tashkent-palace": ["lotte_exterior", "lotte_street", "lotte_ornament", "lotte_food", "lotte_garden"],
    "hyatt-regency-tashkent": ["hyatt"],
}

# Photographs of similar places to stay, per destination and kind of place: "upscale" (hotels), "courtyard" (boutique hotels and guesthouses), "hostel".
POOLS = {
    "samarkand": {
        "upscale": ["samarkand_entrance", "registan_hotel1", "bibi_room1", "bibi_court2", "registan_hotel2"],
        "courtyard": ["bibi_room1", "bibi_court2", "bibi_court3", "bibi_room2", "bibi_court4"],
        "hostel": ["samarkand_hostel_sign", "samarkand_bnb", "samarkand_hostel_street", "bibi_room2", "bibi_court4"]},
    "bukhara": {
        "upscale": ["asia_bukhara1", "hovli_room", "hovli_court2", "asia_bukhara2", "khurjin1"],
        "courtyard": ["hovli_room", "hovli_court1", "hovli_court2", "khurjin1", "hovli_court3"],
        "hostel": ["hovli_court4", "hovli_room", "khurjin2", "hovli_court5", "khurjin3"]},
    "khorezm": {
        "upscale": ["khiva_courtyard3", "khiva_room3", "khiva_bar", "khiva_courtyard2", "khiva_room"],
        "courtyard": ["khiva_courtyard3", "khiva_room3", "khiva_courtyard2", "khiva_room", "khiva_restaurant"],
        "hostel": ["khiva_room3", "khiva_courtyard3", "khiva_room", "khiva_courtyard2", "khiva_bar"]},
    "tashkent": {
        "upscale": ["tashkent_citypalace", "tashkent_grandplaza", "tashkent_international", "tashkent_ramada", "tashkent_uzbekistan"],
        "courtyard": ["tashkent_qodiri1", "tashkent_qodiri2", "hovli_room", "khurjin1", "hovli_court2"],
        "hostel": ["tashkent_qodiri1", "tashkent_qodiri2", "khurjin2", "hovli_room", "hovli_court4"]},
    "fergana": {
        "upscale": ["fergana_hotel", "kokand_hotel1", "fergana_qirguli", "khiva_room3", "kokand_hotel2"],
        "courtyard": ["kokand_hotel1", "hovli_room", "hovli_court1", "fergana_hotel", "khurjin1"],
        "hostel": ["kokand_hotel2", "hovli_room", "khurjin2", "fergana_qirguli", "hovli_court4"]},
    "karakalpakstan": {
        "upscale": ["nukus_rahnamo", "kk_damir", "kk_royal", "jipek_joli", "urgench_hotel"],
        "courtyard": ["jipek_joli", "hovli_room", "kk_damir", "hovli_court1", "nukus_rahnamo"],
        "hostel": ["jipek_joli", "hovli_room", "kk_royal", "hovli_court4", "nukus_rahnamo"]},
    "kashkadarya": {
        "upscale": ["khurjin1", "hovli_court1", "asia_bukhara1", "hovli_room", "khurjin3"],
        "courtyard": ["khurjin2", "hovli_court3", "hovli_room", "khurjin4", "hovli_court5"],
        "hostel": ["khurjin2", "hovli_room", "hovli_court4", "khurjin4", "hovli_court5"]},
}


def lower_first(text):
    return text[:1].lower() + text[1:]


def summary_for(city, kind, stars, extra):
    """The English summary and its translations (French, German and Spanish get the type and the city, without the extra fact)."""
    _, _, en_city, forms = CITIES[city]
    en_type, tr_type = TYPES[(kind, stars)]
    english = f"{en_type} in {en_city}." + (f" {extra[0]}" if extra else "")
    uz = f"{forms[0]} {lower_first(tr_type[0])}." + (f" {extra[1]}" if extra else "")
    ru = f"{tr_type[1]} в {forms[1]}." + (f" {extra[2]}" if extra else "")
    fr = f"{tr_type[2]} à {forms[2]}."
    de = f"{tr_type[3]} in {forms[3]}."
    es = f"{tr_type[4]} en {forms[4]}."
    return english, (uz, ru, fr, de, es)


def description_for(slug, city, kind, stars, extra, basis):
    """The summary followed by the price range seen on public listings (when known), in all six languages."""
    english, translations = summary_for(city, kind, stars, extra)
    if slug not in RANGES:
        return english, translations
    low, high = RANGES[slug]
    sentences = [text.format(low=low, high=high, unit=bed if basis == "bed" else room) for text, room, bed in RANGE_TEXT]
    return f"{english} {sentences[0]}", tuple(f"{summary} {sentence}" for summary, sentence in zip(translations, sentences[1:]))


def gallery_for(slug, destination, position, kind="hotel"):
    """Cover and extra photos (links), and whether they show similar places rather than this property.

    A property with three or more photographs of its own shows only those; one with fewer shows them first, followed by photographs of
    similar places to stay in the same destination (rotated, so neighbouring hotels do not look identical).
    """
    if slug in DIRECT_PHOTOS:
        urls = DIRECT_PHOTOS[slug]
        return urls[0], urls[1:5], False
    own = OWN_PHOTOS.get(slug, [])
    if len(own) >= 3:
        keys, similar = own, False
    else:
        group = "hostel" if kind == "hostel" else "courtyard" if kind in ("boutique", "guesthouse") else "upscale"
        pool = POOLS[destination][group]
        turn = position % len(pool)
        keys, similar = own + pool[turn:] + pool[:turn], True
    seen = []
    for key in keys:
        if key not in seen:
            seen.append(key)
    urls = [photo(FILES[key].replace(" ", "_")) for key in seen]
    return urls[0], urls[1:5], similar


def register_phrases():
    PHRASES["Free parking"] = ("Bepul to'xtash joyi", "Бесплатная парковка", "Parking gratuit", "Kostenloser Parkplatz", "Aparcamiento gratuito")
    for slug, name, city, kind, stars, price, basis, extra, amenities in HOTELS:
        english, translations = summary_for(city, kind, stars, extra)
        PHRASES[english] = translations
        full, full_translations = description_for(slug, city, kind, stars, extra, basis)
        PHRASES[full] = full_translations
    PHRASES["Khorezm"] = PHRASES.get("Khorezm", ("Xorazm", "Хорезм", "Khorezm", "Choresm", "Corasmia"))


register_phrases()
