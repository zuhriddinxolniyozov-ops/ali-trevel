"""Everything the website shows about a tour, as Telegram messages: the overview, the details, the day-by-day plan, the places with their
map links and the price by group size. The texts are the tour's own (in the traveller's language); only the labels live here."""
import html
import urllib.parse

from . import models

LANG_ORDER = ("en", "uz", "ru", "fr", "de", "es")

LABELS = {
    "details": ("📋 Tour details", "📋 Tur tafsilotlari", "📋 Детали тура", "📋 Détails du circuit", "📋 Tourdetails", "📋 Detalles del tour"),
    "plan": ("🗓 Day-by-day plan", "🗓 Kunlik reja", "🗓 План по дням", "🗓 Programme jour par jour", "🗓 Tagesplan", "🗓 Plan día a día"),
    "places": ("📍 Places and map", "📍 Joylar va xarita", "📍 Места и карта", "📍 Lieux et carte", "📍 Orte und Karte", "📍 Lugares y mapa"),
    "group": ("💵 Price by group size", "💵 Guruh hajmiga qarab narx", "💵 Цена по размеру группы", "💵 Prix selon le groupe", "💵 Preis nach Gruppengröße", "💵 Precio según el grupo"),
    "back_tour": ("⬅️ Back to the tour", "⬅️ Turga qaytish", "⬅️ К туру", "⬅️ Retour au circuit", "⬅️ Zurück zur Tour", "⬅️ Volver al tour"),
    "full_tour": ("🧳 Open the full tour", "🧳 To'liq turni ochish", "🧳 Открыть полный тур", "🧳 Ouvrir le circuit complet", "🧳 Ganze Tour öffnen", "🧳 Abrir el tour completo"),
    "map": ("Map", "Xaritada", "На карте", "Carte", "Karte", "Mapa"),
    "directions": ("Directions", "Yo'l ko'rsatish", "Маршрут", "Itinéraire", "Route", "Cómo llegar"),
    "whole_route": ("🗺 The whole route on Google Maps", "🗺 Butun marshrut Google Maps'da", "🗺 Весь маршрут в Google Maps", "🗺 Tout l'itinéraire sur Google Maps", "🗺 Die ganze Route in Google Maps", "🗺 Toda la ruta en Google Maps"),
    "d_type": ("Tour type", "Tur turi", "Тип тура", "Type de circuit", "Tourart", "Tipo de tour"),
    "d_duration": ("Duration", "Davomiyligi", "Продолжительность", "Durée", "Dauer", "Duración"),
    "d_group": ("Group", "Guruh", "Группа", "Groupe", "Gruppe", "Grupo"),
    "d_up_to": ("up to {n} travelers", "{n} kishigacha", "до {n} человек", "jusqu'à {n} voyageurs", "bis zu {n} Reisende", "hasta {n} viajeros"),
    "d_languages": ("Guide languages", "Gid tillari", "Языки гида", "Langues du guide", "Sprachen des Guides", "Idiomas del guía"),
    "d_transport": ("Transport", "Transport", "Транспорт", "Transport", "Transport", "Transporte"),
    "d_tickets": ("Entrance tickets", "Kirish chiptalari", "Входные билеты", "Billets d'entrée", "Eintrittskarten", "Entradas"),
    "d_pickup": ("Pickup", "Kutib olish", "Встреча", "Prise en charge", "Abholung", "Recogida"),
    "d_guide": ("Guide", "Gid", "Гид", "Guide", "Guide", "Guía"),
    "d_meeting": ("Meeting point", "Uchrashuv joyi", "Место встречи", "Point de rendez-vous", "Treffpunkt", "Punto de encuentro"),
    "yes": ("included", "kiradi", "включено", "inclus", "inklusive", "incluido"),
    "no": ("not included", "kirmaydi", "не включено", "non inclus", "nicht inklusive", "no incluido"),
    "included": ("Included", "Narxga kiradi", "Входит в цену", "Inclus", "Inklusive", "Incluido"),
    "excluded": ("Not included", "Narxga kirmaydi", "Не входит в цену", "Non inclus", "Nicht inklusive", "No incluido"),
    "hotel_note": ("🏨 The price includes the most affordable hotels and a standard taxi. Hotels of 3, 4 or 5 stars and a premium-class taxi cost extra.",
                   "🏨 Narxga eng arzon mehmonxonalar va oddiy taksi kiradi. 3, 4 yoki 5 yulduzli mehmonxonalar va premium klassdagi taksi uchun qo'shimcha to'lov olinadi.",
                   "🏨 В цену входят самые доступные отели и обычное такси. За отели 3, 4 или 5 звёзд и такси премиум-класса взимается доплата.",
                   "🏨 Le prix inclut les hôtels les plus abordables et un taxi standard. Les hôtels 3, 4 ou 5 étoiles et un taxi premium sont en supplément.",
                   "🏨 Im Preis sind die günstigsten Hotels und ein Standardtaxi enthalten. Hotels mit 3, 4 oder 5 Sternen und ein Premiumtaxi kosten extra.",
                   "🏨 El precio incluye los hoteles más económicos y un taxi estándar. Los hoteles de 3, 4 o 5 estrellas y un taxi premium tienen un coste adicional."),
    "day": ("Day {n}", "{n}-kun", "День {n}", "Jour {n}", "Tag {n}", "Día {n}"),
    "breakfast": ("Breakfast", "Nonushta", "Завтрак", "Petit-déjeuner", "Frühstück", "Desayuno"),
    "lunch": ("Lunch", "Tushlik", "Обед", "Déjeuner", "Mittagessen", "Almuerzo"),
    "dinner": ("Dinner", "Kechki ovqat", "Ужин", "Dîner", "Abendessen", "Cena"),
    "transfer": ("Transfer to {place}", "{place}ga yo'l", "Переезд: {place}", "Trajet vers {place}", "Fahrt nach {place}", "Traslado a {place}"),
    "free": ("Free time", "Erkin vaqt", "Свободное время", "Temps libre", "Freie Zeit", "Tiempo libre"),
    "ticket": ("ticket", "chipta", "билет", "billet", "Ticket", "entrada"),
    "plan_note": ("Times are approximate; our team confirms the final schedule with you.", "Vaqtlar taxminiy; yakuniy jadvalni jamoamiz siz bilan tasdiqlaydi.",
                  "Время примерное; окончательное расписание подтвердит наша команда.", "Les horaires sont approximatifs ; notre équipe confirme le programme final.",
                  "Die Zeiten sind ungefähr; unser Team bestätigt den endgültigen Ablauf.", "Los horarios son aproximados; nuestro equipo confirma el programa final."),
    "no_plan": ("A detailed plan for this tour is agreed with our team.", "Bu tur uchun batafsil reja jamoamiz bilan kelishiladi.", "Подробный план этого тура согласуется с нашей командой.",
                "Le programme détaillé de ce circuit est convenu avec notre équipe.", "Der detaillierte Ablauf dieser Tour wird mit unserem Team abgestimmt.", "El programa detallado de este tour se acuerda con nuestro equipo."),
    "route_head": ("Route and entrance tickets", "Marshrut va kirish chiptalari", "Маршрут и входные билеты", "Itinéraire et billets d'entrée", "Route und Eintrittskarten", "Ruta y entradas"),
    "tickets_not": ("Entrance tickets are not in the tour price; they are paid at each site.", "Kirish chiptalari tur narxiga kirmaydi; har bir joyda to'lanadi.",
                    "Входные билеты не входят в цену тура и оплачиваются на месте.", "Les billets d'entrée ne sont pas dans le prix ; ils se paient sur place.",
                    "Die Eintrittskarten sind nicht im Preis enthalten; sie werden vor Ort bezahlt.", "Las entradas no están en el precio; se pagan en cada lugar."),
    "tickets_yes": ("Entrance tickets are included in the tour price.", "Kirish chiptalari tur narxiga kiradi.", "Входные билеты включены в цену тура.",
                    "Les billets d'entrée sont inclus dans le prix.", "Die Eintrittskarten sind im Preis enthalten.", "Las entradas están incluidas en el precio."),
    "no_route": ("This tour has no fixed list of places.", "Bu turda joylarning qat'iy ro'yxati yo'q.", "У этого тура нет фиксированного списка мест.",
                 "Ce circuit n'a pas de liste fixe de lieux.", "Diese Tour hat keine feste Liste von Orten.", "Este tour no tiene una lista fija de lugares."),
    "group_head": ("Price per person by group size", "Bir kishi uchun narx guruh hajmiga qarab", "Цена с человека по размеру группы", "Prix par personne selon la taille du groupe",
                   "Preis pro Person nach Gruppengröße", "Precio por persona según el tamaño del grupo"),
    "group_rule": ("The bigger the group, the cheaper it is for each person; a small group pays a little more, because the guide, the car and the organisation cost the same for 2 people as for 20.",
                   "Guruh qancha katta bo'lsa, har bir kishi uchun narx shuncha arzon; kichik guruh biroz qimmatroq to'laydi, chunki gid, mashina va tashkilot xarajati 2 kishiga ham, 20 kishiga ham bir xil.",
                   "Чем больше группа, тем дешевле для каждого; маленькая группа платит чуть больше, ведь гид, машина и организация стоят одинаково для 2 и для 20 человек.",
                   "Plus le groupe est grand, moins cher c'est pour chacun ; un petit groupe paie un peu plus, car le guide, la voiture et l'organisation coûtent autant pour 2 que pour 20.",
                   "Je größer die Gruppe, desto günstiger für jeden; eine kleine Gruppe zahlt etwas mehr, denn Guide, Auto und Organisation kosten für 2 genauso viel wie für 20.",
                   "Cuanto mayor es el grupo, más barato sale por persona; un grupo pequeño paga algo más, porque el guía, el coche y la organización cuestan lo mismo para 2 que para 20."),
    "group_flat": ("The price per person is the same for every group size.", "Bir kishi uchun narx guruh hajmidan qat'i nazar bir xil.",
                   "Цена с человека одинакова для любого размера группы.", "Le prix par personne est le même quelle que soit la taille du groupe.",
                   "Der Preis pro Person ist für jede Gruppengröße gleich.", "El precio por persona es el mismo para cualquier tamaño de grupo."),
    "person": ("person", "kishi", "чел.", "pers.", "Pers.", "pers."),
    "total": ("total", "jami", "итого", "total", "gesamt", "total"),
    "location": ("📍 Location", "📍 Joylashuvi", "📍 Расположение", "📍 Emplacement", "📍 Standort", "📍 Ubicación"),
    "open_maps": ("Open in Google Maps", "Google Maps'da ochish", "Открыть в Google Maps", "Ouvrir dans Google Maps", "In Google Maps öffnen", "Abrir en Google Maps"),
    "part_of": ("Part of the tour", "Tarkibida", "Входит в тур", "Fait partie du circuit", "Teil der Tour", "Parte del tour"),
    "place_rule": ("This place is visited as part of the full tour and cannot be booked on its own.", "Bu joy to'liq tur doirasida ko'riladi va alohida bron qilib bo'lmaydi.",
                   "Это место посещается в рамках полного тура и отдельно не бронируется.", "Ce lieu se visite dans le cadre du circuit complet et ne se réserve pas séparément.",
                   "Dieser Ort wird im Rahmen der ganzen Tour besucht und kann nicht einzeln gebucht werden.", "Este lugar se visita dentro del tour completo y no se reserva por separado."),
    "entrance": ("Entrance ticket", "Kirish chiptasi", "Входной билет", "Billet d'entrée", "Eintrittskarte", "Entrada"),
    "story_head": ("A few words to remember", "Esda qoladigan so'zlar", "Несколько слов на память", "Quelques mots à retenir", "Ein paar Worte zum Merken", "Unas palabras para recordar"),
}

TYPES = {
    "car": ("Car tour", "Mashinada tur", "Автотур", "Circuit en voiture", "Autotour", "Tour en coche"),
    "walking": ("Walking tour", "Piyoda tur", "Пешеходный тур", "Visite à pied", "Rundgang", "Tour a pie"),
    "mixed": ("Car + walking", "Mashina + piyoda", "Авто + пешком", "Voiture + marche", "Auto + zu Fuß", "Coche + a pie"),
    "train": ("Train tour", "Poyezdda tur", "Тур на поезде", "Circuit en train", "Bahntour", "Tour en tren"),
    "workshop": ("Hands-on experience", "Amaliy tajriba", "Практический опыт", "Expérience pratique", "Praxiserlebnis", "Experiencia práctica"),
}


def lab(name, lang, **fields):
    entry = LABELS[name]
    text = entry[LANG_ORDER.index(lang)] if lang in LANG_ORDER else entry[0]
    return text.format(**fields) if fields else text


def esc(value):
    return html.escape(str(value or ""), quote=False)


def loc(obj, field, lang):
    return (getattr(obj, "i18n", None) or {}).get(lang, {}).get(field) or getattr(obj, field, "")


def money(amount):
    amount = float(amount)
    return f"${int(amount):,}" if amount == int(amount) else f"${amount:,.2f}"


def parse_stop(line):
    name, _, fee = str(line).partition("|")
    fee = fee.strip()
    try:
        return name.strip(), (float(fee) if fee else None)
    except ValueError:
        return name.strip(), None


def located(place):
    return place is not None and place.latitude is not None and place.longitude is not None


def pair(place):
    return f"{float(place.latitude):.6f},{float(place.longitude):.6f}"


def map_url(place):
    return f"https://www.google.com/maps/search/?api=1&query={pair(place)}"


def route_url(places):
    if len(places) < 2:
        return map_url(places[0])
    url = f"https://www.google.com/maps/dir/?api=1&origin={pair(places[0])}&destination={pair(places[-1])}"
    if len(places) > 2:
        url += "&waypoints=" + urllib.parse.quote("|".join(pair(p) for p in places[1:-1][:8]), safe=",")
    return url


def places_by_name():
    """Every single place of every tour, by its English name (the route of a tour names its stops the same way)."""
    return {parse_stop(p.route[0])[0].lower(): p for p in models.Tour.objects.exclude(parent_slug="") if p.route}


def stops_of(tour, lang):
    """[(english name, shown name, fee)] for the stops of a tour's route."""
    english = [parse_stop(line) for line in tour.route or []]
    shown = [parse_stop(line)[0] for line in (loc(tour, "route", lang) or [])]
    return [(name, shown[i] if i < len(shown) and shown[i] else name, fee) for i, (name, fee) in enumerate(english)]


def details_text(tour, lang):
    lines = [f"<b>{esc(loc(tour, 'title', lang))}</b>", f"<i>{lab('details', lang)[2:].strip()}</i>", ""]
    kind = TYPES.get(tour.tour_type)
    if kind:
        lines.append(f"• {lab('d_type', lang)}: {kind[LANG_ORDER.index(lang)]}")
    lines.append(f"• {lab('d_duration', lang)}: {esc(loc(tour, 'duration_label', lang))}")
    group = esc(loc(tour, "group_type", lang)) + (f" · {lab('d_up_to', lang, n=tour.max_travelers)}" if tour.max_travelers else "")
    lines.append(f"• {lab('d_group', lang)}: {group}")
    if tour.languages:
        lines.append(f"• {lab('d_languages', lang)}: {esc(', '.join(tour.languages))}")
    for key, value in (("d_transport", tour.transport_included), ("d_tickets", tour.tickets_included), ("d_pickup", tour.pickup_included)):
        lines.append(f"• {lab(key, lang)}: {'✅ ' + lab('yes', lang) if value else '❌ ' + lab('no', lang)}")
    if tour.guide:
        lines.append(f"• {lab('d_guide', lang)}: {esc(loc(tour, 'guide', lang))}")
    if tour.meeting_point:
        lines.append(f"• {lab('d_meeting', lang)}: {esc(loc(tour, 'meeting_point', lang))}")
    included, excluded = loc(tour, "included", lang) or [], loc(tour, "excluded", lang) or []
    if included:
        lines += ["", f"✅ <b>{lab('included', lang)}</b>"] + [f"• {esc(x)}" for x in included]
    if excluded:
        lines += ["", f"❌ <b>{lab('excluded', lang)}</b>"] + [f"• {esc(x)}" for x in excluded]
    if len(tour.itinerary or []) >= 2:
        lines += ["", lab("hotel_note", lang)]
    if tour.story:
        lines += ["", f"<i>“{esc(loc(tour, 'story', lang))}”</i>"]
    return "\n".join(lines)


def plan_pages(tour, lang, limit=3300):
    """The day-by-day plan cut into messages that fit Telegram (whole days only)."""
    stops = stops_of(tour, lang)
    days = []
    for day in tour.itinerary or []:
        rows = [f"<b>{lab('day', lang, n=day['day'])}</b>"]
        for item in day.get("items", []):
            kind, time = item.get("type"), esc(item.get("time", ""))
            if kind == "meal":
                state = "✅" if item.get("included") else "❌"
                rows.append(f"{time} {'☕' if item.get('meal') == 'breakfast' else '🍽'} {lab(item.get('meal', 'lunch'), lang)} {state}")
            elif kind == "visit" and item.get("stop") is not None and item["stop"] < len(stops):
                _, name, fee = stops[item["stop"]]
                rows.append(f"{time} 🏛 {esc(name)}" + (f" · 🎫 {money(fee)}" if fee else ""))
            elif kind == "transfer" and item.get("stop") is not None and item["stop"] < len(stops):
                rows.append(f"{time} 🚗 {lab('transfer', lang, place=esc(stops[item['stop']][1]))}")
            elif kind == "free":
                rows.append(f"{time} 🕓 {lab('free', lang)}")
            else:
                rows.append(f"{time} ⭐ {esc((item.get('i18n') or {}).get(lang) or item.get('text', ''))}")
        days.append("\n".join(rows))
    if not days:
        return [lab("no_plan", lang)]
    pages, current = [], ""
    for block in days:
        if current and len(current) + len(block) + 2 > limit:
            pages.append(current)
            current = ""
        current = f"{current}\n\n{block}" if current else block
    pages.append(current)
    return pages


def places_text(tour, lang):
    stops = stops_of(tour, lang)
    if not stops:
        return lab("no_route", lang), []
    known = places_by_name()
    lines = [f"<b>{esc(loc(tour, 'title', lang))}</b>", f"<i>{lab('route_head', lang)}</i>", ""]
    pins = []
    for i, (name, shown, fee) in enumerate(stops, 1):
        place = known.get(name.lower())
        row = f"{i}. <b>{esc(shown)}</b>" + (f" · 🎫 {money(fee)}" if fee else "")
        if located(place):
            pins.append(place)
            row += f"\n    📍 <a href=\"{map_url(place)}\">{lab('map', lang)}</a>"
            if place.location_note:
                row += f" · <i>{esc(loc(place, 'location_note', lang))}</i>"
        lines.append(row)
    lines += ["", lab("tickets_yes" if tour.tickets_included else "tickets_not", lang)]
    return "\n".join(lines), pins


def group_text(tour, lang, per_person, tiers):
    lines = [f"<b>{esc(loc(tour, 'title', lang))}</b>", f"<i>{lab('group_head', lang)}</i>", ""]
    if not tour.group_pricing:
        return "\n".join(lines + [lab("group_flat", lang)])
    ordered = sorted(tiers, key=lambda t: t["min"])
    for index, tier in enumerate(ordered):
        low = tier["min"]
        high = ordered[index + 1]["min"] - 1 if index + 1 < len(ordered) else None
        label = f"{low}+" if high is None else (str(low) if high == low else f"{low}–{high}")
        each = per_person(low)
        lines.append(f"👥 <b>{label}</b> — {money(each)} / {lab('person', lang)}" + (f"  ({lab('total', lang)} {money(each * low)})" if low > 1 else ""))
    return "\n".join(lines + ["", f"<i>{lab('group_rule', lang)}</i>"])


def place_text(place, lang, parent):
    lines = [f"<b>{esc(loc(place, 'title', lang).removesuffix(' Tour'))}</b>", "", esc(loc(place, "description", lang) or loc(place, "summary", lang))]
    if place.entrance_fee_usd:
        lines += ["", f"🎫 {lab('entrance', lang)}: <b>{money(place.entrance_fee_usd)}</b>"]
    if located(place):
        lines += ["", f"<b>{lab('location', lang)}</b>", f"<a href=\"{map_url(place)}\">{lab('open_maps', lang)}</a> · "
                  f"<a href=\"https://www.google.com/maps/dir/?api=1&destination={pair(place)}\">{lab('directions', lang)}</a> · <code>{pair(place)}</code>"]
        if place.location_note:
            lines.append(f"<i>{esc(loc(place, 'location_note', lang))}</i>")
    if place.story:
        lines += ["", f"<i>“{esc(loc(place, 'story', lang))}”</i>"]
    if parent:
        lines += ["", f"🧳 {lab('part_of', lang)}: <b>{esc(loc(parent, 'title', lang))}</b>", f"<i>{lab('place_rule', lang)}</i>"]
    return "\n".join(lines)
