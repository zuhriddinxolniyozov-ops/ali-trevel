"""The 11-day Silk Road journey: Samarkand (2 days), Shahrisabz and Qarshi (1 day), the road to Bukhara (1 day), Bukhara (2 days), the road to Khiva
(1 day), Khiva (2 days), back to Bukhara (1 day) and the road to Samarkand via Gijduvan and Rabat-i-Malik (1 day).

It reuses the places and helpers of the 7-day package and adds three places of Khiva. The price is a sample price to edit in the admin panel.
"""
from api.management.commands import seed_package as base
from api.management.commands.seed_package import FEES, PLAN_TEXT, meal, step, tr
from api.management.commands.seed_regions import photo
from api.management.commands.seed_translations import PHRASES

SLUG = "silk-road-11-day-journey"
PRICE = 1290
KHIVA = "Khorezm"

NEW_PLACES = [
    ("kunya-ark-khiva", "Kunya-Ark Citadel (Khiva)", 6, "Konya Ark gate.jpg",
     "The old fortress and residence of the khans of Khiva, with a throne room, a mosque and a view over the whole old town.",
     "Kunya-Ark means “the old fortress”. It was the home of the khans of Khiva, who ruled from here for centuries, and it holds their reception hall with a throne, a summer mosque with a colourful tiled porch, and the old mint. Climb the watchtower at sunset: from the top you see the whole of Itchan Kala, its minarets and domes, and the desert beyond the walls.",
     "A khan once looked at his city from this tower. At sunset you will see why he never wanted to leave.",
     ("Xiva xonlarining qadimiy qal'asi va qarorgohi: taxt zali, masjid va butun eski shahar manzarasi.",
      "Ko'hna Ark — «eski qal'a» degani. Bu yerda asrlar davomida Xiva xonlari hukmronlik qilgan; qal'ada taxtli qabul zali, rang-barang sirli ayvonli yozgi masjid va eski zarbxona bor. Quyosh botishida kuzatuv minorasiga chiqing: yuqoridan butun Ichan Qal'a, uning minoralari, gumbazlari va devorlar ortidagi cho'l ko'rinadi.",
      "Bir paytlar xon shu minoradan shahriga qaragan. Quyosh botganda uning nega ketgisi kelmaganini tushunasiz."),
     ("Старая крепость и резиденция хивинских ханов с тронным залом, мечетью и видом на весь старый город.",
      "Кунья-Арк означает «старая крепость». Здесь веками правили хивинские ханы; в крепости находятся приёмный зал с троном, летняя мечеть с красочным облицованным айваном и старый монетный двор. На закате поднимитесь на смотровую башню: сверху видны весь Ичан-Кала, его минареты, купола и пустыня за стенами.",
      "Когда-то хан смотрел на свой город с этой башни. На закате вы поймёте, почему ему не хотелось уезжать.")),
    ("islam-khoja-minaret-khiva", "Islam Khoja Minaret (Khiva)", 5, "Imam Khoja Minaret, Khiva (480996).jpg",
     "The tallest minaret of Khiva, striped with turquoise tiles, with a small madrasah at its foot.",
     "The Islam Khoja Minaret, about 45 metres high, is the tallest building in Khiva. It was built in 1910 by the grand vizier Islam Khoja together with a madrasah, and its bands of turquoise and blue glazed tiles make it the best-known landmark of the old town. You can climb the narrow staircase inside to look over Itchan Kala.",
     "Forty-five metres of turquoise rising from the mud-brick town: the minaret that tells every traveller they have arrived in Khiva.",
     ("Xivadagi eng baland minora: feruza sirli sopol bandlar bilan, poydevorida kichik madrasa bor.",
      "Islomxo'ja minorasi taxminan 45 metr balandlikda, Xivadagi eng baland bino. U 1910-yilda bosh vazir Islomxo'ja tomonidan madrasa bilan birga qurilgan; feruza va ko'k sirli sopol bandlari uni eski shaharning eng mashhur belgisiga aylantirgan. Ichkaridagi tor zinadan chiqib, Ichan Qal'aga yuqoridan qarash mumkin.",
      "Paxsa shahar ustida ko'tarilgan qirq besh metr feruza: har bir sayyohga Xivaga yetib kelganini aytadigan minora."),
     ("Самый высокий минарет Хивы, украшенный полосами бирюзовой плитки, с небольшим медресе у подножия.",
      "Минарет Ислам-Ходжа высотой около 45 метров — самое высокое здание Хивы. Он построен в 1910 году великим визирем Ислам-Ходжой вместе с медресе, а полосы бирюзовой и синей глазурованной плитки сделали его самой узнаваемой достопримечательностью старого города. По узкой лестнице внутри можно подняться и осмотреть Ичан-Кала сверху.",
      "Сорок пять метров бирюзы над глинобитным городом: минарет, который говорит каждому путнику, что он приехал в Хиву.")),
    ("pahlavon-mahmud-mausoleum-khiva", "Pahlavon Mahmud Mausoleum (Khiva)", 4, "XIV-XIX asr Pahlovon Mahmud Maqbarasi.jpg",
     "The tiled mausoleum of Khiva's patron saint, the poet and wrestler Pahlavon Mahmud, and a place of pilgrimage.",
     "Pahlavon Mahmud (1247–1326) was a poet, a wrestler undefeated in his time and a Sufi, and he is the patron saint of Khiva. His mausoleum, with a high blue-tiled dome and a courtyard of carved wooden columns, is the spiritual heart of the town and is still visited by pilgrims. The complex was enlarged by the khans in the 18th and 19th centuries.",
     "A wrestler who chose kindness over victory sleeps under a blue dome. The people of Khiva still come to ask him for strength.",
     ("Xivaning homiysi — shoir va polvon Pahlavon Mahmudning sirli maqbarasi, ziyoratgoh.",
      "Pahlavon Mahmud (1247–1326) — shoir, o'z davrida yengilmagan polvon va tasavvuf namoyandasi, Xivaning homiysi. Baland ko'k sirli gumbazi va o'ymakor yog'och ustunli hovlisi bor maqbarasi shaharning ma'naviy markazi bo'lib, bugun ham ziyoratchilar keladi. Majmua XVIII–XIX asrlarda xonlar tomonidan kengaytirilgan.",
      "G'alabadan ko'ra mehribonlikni tanlagan polvon ko'k gumbaz ostida yotibdi. Xivaliklar hamon undan kuch so'rab keladi."),
     ("Облицованный мавзолей покровителя Хивы — поэта и борца Пахлаван Махмуда, место паломничества.",
      "Пахлаван Махмуд (1247–1326) — поэт, непобеждённый борец своего времени и суфий, покровитель Хивы. Его мавзолей с высоким синим куполом и двором с резными деревянными колоннами — духовное сердце города, сюда до сих пор приходят паломники. Комплекс расширяли ханы в XVIII–XIX веках.",
      "Борец, выбравший доброту вместо победы, спит под синим куполом. Хивинцы до сих пор приходят просить у него силы.")),
]

PLAN_TEXT.update({
    "Drive from Bukhara across the Kyzylkum desert to Khiva (about 7 hours, with stops)": ("Buxorodan Qizilqum cho'li orqali Xivaga yo'l (taxminan 7 soat, to'xtashlar bilan)", "Дорога из Бухары через пустыню Кызылкум в Хиву (около 7 часов, с остановками)"),
    "Arrive in Khiva and check in": ("Xivaga yetib kelasiz va mehmonxonaga joylashasiz", "Прибытие в Хиву и заселение"),
    "Free time in Khiva: shops, workshops and tea in a courtyard": ("Xivada erkin vaqt: do'konlar, ustaxonalar va hovlida choy", "Свободное время в Хиве: лавки, мастерские и чай во дворике"),
    "Drive from Khiva back to Bukhara (about 7 hours, with stops)": ("Xivadan Buxoroga qaytish (taxminan 7 soat, to'xtashlar bilan)", "Дорога из Хивы обратно в Бухару (около 7 часов, с остановками)"),
    "Evening at leisure in Bukhara": ("Buxoroda erkin kechqurun", "Свободный вечер в Бухаре"),
    "Drive on to Samarkand (about 3 hours), with a lunch stop": ("Samarqandga qarab yo'lni davom ettirasiz (taxminan 3 soat), tushlik uchun to'xtash bilan", "Дальше едем в Самарканд (около 3 часов), с остановкой на обед"),
})

TITLE = "11-Day Silk Road Journey: Samarkand, Shahrisabz, Bukhara and Khiva"
TITLE_T = ("11 kunlik Ipak yo'li sayohati: Samarqand, Shahrisabz, Buxoro va Xiva", "11-дневное путешествие по Шёлковому пути: Самарканд, Шахрисабз, Бухара и Хива")
SUMMARY = "Eleven days through four oasis cities: Samarkand, Shahrisabz and Qarshi, Bukhara and Khiva, with the Kyzylkum desert in between."
SUMMARY_T = ("O'n bir kun to'rt voha shahrida: Samarqand, Shahrisabz va Qarshi, Buxoro va Xiva, oralarida Qizilqum cho'li.",
             "Одиннадцать дней по четырём городам-оазисам: Самарканд, Шахрисабз и Карши, Бухара и Хива, а между ними — пустыня Кызылкум.")
DESCRIPTION = ("The full Silk Road in one journey, with one guide and one car. You spend two days in Samarkand (Registan, Gur-e-Amir, Bibi-Khanym, Siyob Bazaar, Shah-i-Zinda, the Ulugh Beg Observatory and the Imam al-Bukhari complex), "
               "cross the Tahtakaracha pass to Shahrisabz, Amir Timur's birthplace, and sleep in Qarshi. Then you cross the desert to Bukhara and walk its old town for two days (Ismail Samani, the Ark, Poi Kalon, Chor Minor, Lyabi-Hauz). "
               "From Bukhara you drive across the Kyzylkum desert to Khiva and spend two days inside the walls of Itchan Kala (Kalta Minor, Kunya-Ark, Juma Mosque, Tash Hauli, the Islam Khoja Minaret and the Pahlavon Mahmud Mausoleum). "
               "You return to Bukhara and, on the last day, drive to Samarkand via the potters of Gijduvan and the caravanserai of Rabat-i-Malik. "
               "The price includes the most affordable hotels, a private car with a driver, a licensed guide and breakfasts; entrance tickets are paid at the sites. "
               "Hotels of 3, 4 or 5 stars and a premium-class car are available for an extra payment.")
DESCRIPTION_T = ("Butun Ipak yo'li bitta sayohatda: bitta gid va bitta mashina bilan. Samarqandda ikki kun (Registon, Go'ri Amir, Bibixonim, Siyob bozori, Shohizinda, Ulug'bek rasadxonasi va Imom Buxoriy majmuasi), "
                 "Taxtaqoracha dovoni orqali Amir Temur tug'ilgan Shahrisabzga o'tasiz va Qarshida tunaysiz. So'ng cho'l orqali Buxoroga borib, eski shaharda ikki kun sayr qilasiz (Ismoil Somoniy, Ark, Poi Kalon, Chor Minor, Labi Hovuz). "
                 "Buxorodan Qizilqum cho'li orqali Xivaga borasiz va Ichan Qal'a devorlari ichida ikki kun bo'lasiz (Kalta Minor, Ko'hna Ark, Juma masjidi, Tosh Hovli, Islomxo'ja minorasi va Pahlavon Mahmud maqbarasi). "
                 "Buxoroga qaytasiz va oxirgi kuni G'ijduvon kulollari hamda Rabotimalik karvonsaroyi orqali Samarqandga yetib borasiz. "
                 "Narxga eng arzon mehmonxonalar, haydovchili shaxsiy mashina, litsenziyali gid va nonushtalar kiradi; kirish chiptalari joyida to'lanadi. "
                 "3, 4 yoki 5 yulduzli mehmonxonalar va premium klassdagi mashina qo'shimcha to'lov evaziga mavjud.",
                 "Весь Шёлковый путь в одном путешествии, с одним гидом и одной машиной. Два дня в Самарканде (Регистан, Гур-Эмир, Биби-Ханым, базар Сиаб, Шахи-Зинда, обсерватория Улугбека и комплекс имама аль-Бухари), "
                 "через перевал Тахтакарача — в Шахрисабз, на родину Амира Тимура, ночёвка в Карши. Затем через пустыню в Бухару и два дня по старому городу (Исмаила Самани, Арк, Пои-Калон, Чор-Минор, Ляби-Хауз). "
                 "Из Бухары через пустыню Кызылкум — в Хиву и два дня внутри стен Ичан-Кала (Кальта-Минор, Кунья-Арк, мечеть Джума, Таш-Хаули, минарет Ислам-Ходжа и мавзолей Пахлаван Махмуда). "
                 "Возвращение в Бухару и в последний день — в Самарканд через гончаров Гиждувана и караван-сарай Рабат-и Малик. "
                 "В стоимость входят самые доступные отели, частная машина с водителем, лицензированный гид и завтраки; входные билеты оплачиваются на месте. "
                 "Отели 3, 4 или 5 звёзд и машина премиум-класса доступны за дополнительную плату.")
STORY = "Eleven days, four oases and one road: from the blue of Samarkand to the walls of Khiva, the light of the Silk Road stays with you."
STORY_T = ("O'n bir kun, to'rt voha va bitta yo'l: Samarqandning moviy rangidan Xiva devorlarigacha Ipak yo'lining nuri sizda qoladi.",
           "Одиннадцать дней, четыре оазиса и одна дорога: от синевы Самарканда до стен Хивы — свет Шёлкового пути останется с вами.")

HIGHLIGHTS = [
    ("Two days in Samarkand: Registan, Gur-e-Amir, Shah-i-Zinda and the Ulugh Beg Observatory", "Samarqandda ikki kun: Registon, Go'ri Amir, Shohizinda va Ulug'bek rasadxonasi", "Два дня в Самарканде: Регистан, Гур-Эмир, Шахи-Зинда и обсерватория Улугбека"),
    ("Shahrisabz and a night in Qarshi", "Shahrisabz va Qarshida tunash", "Шахрисабз и ночь в Карши"),
    ("Two days in Bukhara's old town: the Ark, Poi Kalon, Chor Minor and Lyabi-Hauz", "Buxoroning eski shahrida ikki kun: Ark, Poi Kalon, Chor Minor va Labi Hovuz", "Два дня в старом городе Бухары: Арк, Пои-Калон, Чор-Минор и Ляби-Хауз"),
    ("Across the Kyzylkum desert to Khiva and two days inside the walls of Itchan Kala", "Qizilqum cho'li orqali Xivaga va Ichan Qal'a devorlari ichida ikki kun", "Через пустыню Кызылкум в Хиву и два дня внутри стен Ичан-Кала"),
    ("Return via the potters of Gijduvan and the Rabat-i-Malik caravanserai", "G'ijduvon kulollari va Rabotimalik karvonsaroyi orqali qaytish", "Возвращение через гончаров Гиждувана и караван-сарай Рабат-и Малик"),
]
INCLUDED = [
    ("Ten nights in the most affordable hotels (2 in Samarkand, 1 in Qarshi, 4 in Bukhara, 3 in Khiva) with breakfast", "Eng arzon mehmonxonalarda o'n tun (Samarqandda 2, Qarshida 1, Buxoroda 4, Xivada 3), nonushta bilan", "Десять ночей в самых доступных отелях (2 в Самарканде, 1 в Карши, 4 в Бухаре, 3 в Хиве) с завтраком"),
    ("Private car with a driver for all eleven days", "O'n bir kun davomida haydovchili shaxsiy mashina", "Частная машина с водителем на все одиннадцать дней"),
    ("Licensed local guide", "Litsenziyali mahalliy gid", "Лицензированный местный гид"),
]

FEES11 = dict(FEES, **{"Itchan Kala": 18, "Kalta Minor Minaret": 4, "Juma Mosque": 5, "Tash Hauli Palace": 8, "Kunya-Ark Citadel (Khiva)": 6,
                       "Islam Khoja Minaret (Khiva)": 5, "Pahlavon Mahmud Mausoleum (Khiva)": 4})
EXTRA_STOPS = ["Kok-Gumbaz Mosque (Qarshi)", "Gijduvan Ceramics Workshop", "Rabat-i-Malik Caravanserai"]
ORDER = list(FEES11) + EXTRA_STOPS
ROUTE = [f"{name} | {FEES11[name]}" if name in FEES11 else name for name in ORDER]


def visit(time, name):
    return {"time": time, "type": "visit", "stop": ORDER.index(name)}


def go(time, name):
    return {"time": time, "type": "transfer", "stop": ORDER.index(name)}


def renumber(items):
    """The 7-day package's items, pointing at this route's stop numbers."""
    names = [line.split("|")[0].strip() for line in base.ROUTE]
    return [dict(i, stop=ORDER.index(names[i["stop"]])) if "stop" in i else dict(i) for i in items]


def first_days():
    """Days 1-6 are those of the 7-day package, except that day 6 is no farewell: it ends with an ordinary dinner."""
    days = [dict(d, items=renumber(d["items"])) for d in base.ITINERARY[:6]]
    days[5]["items"] = [i if i.get("text") != "Farewell dinner in Bukhara" else meal("19:00", "dinner", False) for i in days[5]["items"]]
    return days


ITINERARY = first_days() + [
    {"day": 7, "items": [meal("07:30", "breakfast", True), step("08:30", "Drive from Bukhara across the Kyzylkum desert to Khiva (about 7 hours, with stops)"), meal("13:00", "lunch", False),
                         step("16:30", "Arrive in Khiva and check in"), visit("17:30", "Itchan Kala"), meal("19:30", "dinner", False)]},
    {"day": 8, "items": [meal("08:00", "breakfast", True), visit("09:00", "Kalta Minor Minaret"), visit("10:00", "Kunya-Ark Citadel (Khiva)"), meal("13:00", "lunch", False),
                         visit("14:30", "Juma Mosque"), visit("16:00", "Tash Hauli Palace"), meal("19:00", "dinner", False)]},
    {"day": 9, "items": [meal("08:00", "breakfast", True), visit("09:00", "Islam Khoja Minaret (Khiva)"), visit("11:00", "Pahlavon Mahmud Mausoleum (Khiva)"), meal("13:00", "lunch", False),
                         step("15:00", "Free time in Khiva: shops, workshops and tea in a courtyard"), meal("19:00", "dinner", False)]},
    {"day": 10, "items": [meal("07:30", "breakfast", True), step("08:30", "Drive from Khiva back to Bukhara (about 7 hours, with stops)"), meal("13:00", "lunch", False),
                          step("17:00", "Arrive in Bukhara and check in"), step("19:00", "Evening at leisure in Bukhara")]},
    {"day": 11, "items": [meal("07:30", "breakfast", True), step("08:30", "Drive from Bukhara to Gijduvan (about 45 minutes)"), visit("09:30", "Gijduvan Ceramics Workshop"),
                          step("11:30", "Drive on to Samarkand (about 3 hours), with a lunch stop"), visit("12:30", "Rabat-i-Malik Caravanserai"), meal("13:30", "lunch", False),
                          step("16:00", "Arrive in Samarkand: transfer to your hotel, the station or the airport")]},
]


def register_phrases():
    """Add the translations of the 11-day texts to the shared phrase book."""
    PHRASES[TITLE] = tr(*TITLE_T)
    PHRASES[SUMMARY] = tr(*SUMMARY_T)
    PHRASES[DESCRIPTION] = tr(*DESCRIPTION_T)
    PHRASES[STORY] = tr(*STORY_T)
    PHRASES["11 days"] = tr("11 kun", "11 дней")
    for en, uz, ru in HIGHLIGHTS + INCLUDED:
        PHRASES[en] = tr(uz, ru)
    for _, name, _, _, summary, about, story, uz, ru in NEW_PLACES:
        PHRASES[name] = tr(name, name)
        PHRASES[f"{name} Tour"] = tr(f"{name} turi", f"Тур: {name}")
        for en, u, r in ((summary, uz[0], ru[0]), (about, uz[1], ru[1]), (story, uz[2], ru[2])):
            PHRASES[en] = tr(u, r)
    for en, (uz, ru) in PLAN_TEXT.items():
        PHRASES[en] = tr(uz, ru)


register_phrases()


def package_fields(defaults):
    """Fields of the 11-day tour, built on the shared defaults of the regional tours."""
    return dict(defaults, title=TITLE, destination_slug="samarkand", destination_name="Samarkand", category="Culture", duration_label="11 days", group_type="Small group",
                tour_type="car", group_pricing=True, summary=SUMMARY, description=DESCRIPTION, story=STORY, meeting_point=base.MEETING, price_from_usd=PRICE, featured=True,
                image_url=photo("Kalta Minor 01.jpg"), route=ROUTE, itinerary=ITINERARY, highlights=[h[0] for h in HIGHLIGHTS],
                included=[i[0] for i in INCLUDED] + ["Taxi service between the places", "Airport pickup"], excluded=base.EXCLUDED, parent_slug="", entrance_fee_usd=None)
