"""The 7-day Silk Road package: Samarkand (2 days) - Shahrisabz and Qarshi (1 day) - the road to Bukhara (1 day) - Bukhara (2 days) -
the road back to Samarkand (1 day).

The visited places are the place records that already exist (Samarkand, Shahrisabz, Bukhara) plus four new ones on the road (Qarshi, Gijduvan,
Rabat-i-Malik). Every place has a photograph from Wikimedia Commons, a note and a keepsake text; texts are English, Uzbek and Russian
(French, German and Spanish fall back to English). The price is a sample price to edit in the admin panel.
"""
from api.management.commands.seed_regions import photo
from api.management.commands.seed_translations import PHRASES

SLUG = "silk-road-7-day-journey"
PRICE = 790

# Photographs for the Samarkand places, which first had one generic picture (slug -> Commons file).
PLACE_PHOTOS = {
    "registan-square": "Registan Samarkand Uzbekistan.JPG", "gur-e-amir-mausoleum": "Gur-e Amir 01.jpg", "bibi-khanym-mosque": "Bibi-Khanym Mosque, Samarkand.jpg",
    "siyob-bazaar": "Siyob Bazaar in Samarkand.jpg", "shah-i-zinda": "Shah-i-Zinda 01.jpg", "ulugh-beg-observatory": "Ulugh Beg Observatory 01.jpg",
    "imam-al-bukhari-complex": "Imam Al-Bukhari memorial komlpex.jpg",
}
PLACEHOLDER = "generated_2203993e.png"  # the one generic picture the Samarkand places started with


def tr(uz, ru):
    return (uz, ru, "", "", "")


# slug, name, fee (None = free), photo, summary, about, story, (uz summary, uz about, uz story), (ru summary, ru about, ru story)
NEW_PLACES = [
    ("kok-gumbaz-mosque-qarshi", "Kok-Gumbaz Mosque (Qarshi)", None, "Qarshi Kok Gumbaz Mosque and cistern.JPG",
     "A historic blue-domed mosque in the centre of Qarshi, with an old water cistern beside it.",
     "Qarshi is the main city of the Kashkadarya oasis and has been a halt on the road between Samarkand, Bukhara and the south for many centuries. The Kok-Gumbaz Mosque, named after its blue dome, is one of the old buildings that still stand in the city, with a traditional water cistern (hauz) beside it. It is a calm place to stretch your legs, meet local people and see everyday Qarshi before the road to Bukhara.",
     "Every oasis city has a place where travellers once drank, rested and prayed. In Qarshi it sits under a blue dome, next to still water.",
     ("Qarshi markazidagi tarixiy ko'k gumbazli masjid, yonida qadimiy hovuz bor.",
      "Qarshi — Qashqadaryo vohasining asosiy shahri, asrlar davomida Samarqand, Buxoro va janub oralig'idagi yo'lda to'xtash joyi bo'lgan. Ko'k gumbazi tufayli nomlangan Ko'k Gumbaz masjidi shaharda saqlanib qolgan qadimiy binolardan biri, yonida an'anaviy hovuz bor. Buxoro yo'liga chiqishdan oldin oyoq yozish, mahalliy odamlar bilan uchrashish va Qarshining kundalik hayotini ko'rish uchun xotirjam joy.",
      "Har bir voha shahrida yo'lovchilar bir paytlar suv ichib, dam olib, ibodat qilgan joy bor. Qarshida u ko'k gumbaz ostida, sokin suv yonida turadi."),
     ("Историческая мечеть с голубым куполом в центре Карши, рядом с ней старый водоём.",
      "Карши — главный город Кашкадарьинского оазиса, на протяжении веков остановка на пути между Самаркандом, Бухарой и югом. Мечеть Кок-Гумбаз, названная по голубому куполу, — одно из старых зданий, сохранившихся в городе; рядом с ней традиционный хауз. Спокойное место, чтобы размяться, встретить местных жителей и увидеть повседневные Карши перед дорогой в Бухару.",
      "В каждом городе-оазисе есть место, где путники когда-то пили воду, отдыхали и молились. В Карши оно находится под голубым куполом, рядом с тихой водой.")),
    ("rabati-malik-caravanserai", "Rabat-i-Malik Caravanserai", None, "Rabati Malik caravanserai 01.jpg",
     "The ruined gateway of an 11th-century caravanserai on the old road between Bukhara and Samarkand.",
     "Rabat-i-Malik was built in the 11th century as a fortified inn for caravans crossing the steppe between Bukhara and Samarkand. Today the great portal and part of the walls remain beside the highway, and an old covered water cistern (sardoba) stands nearby. It is the best place on the road to picture the caravans that once carried silk, paper and spices through Uzbekistan.",
     "Here the Silk Road is not a name on a map but a gate in the steppe. Stand where the caravan masters once counted their camels and listen to the wind.",
     ("Buxoro va Samarqand oralig'idagi qadimiy yo'lda joylashgan XI asr karvonsaroyining vayron darvozasi.",
      "Rabotimalik XI asrda Buxoro va Samarqand oralig'idagi dashtdan o'tuvchi karvonlar uchun mustahkam mehmonxona sifatida qurilgan. Bugun katta peshtoq va devorlarning bir qismi trassa yonida saqlanib qolgan, yaqinida esa qadimiy yopiq suv ombori (sardoba) turadi. Bu yo'lda ipak, qog'oz va ziravorlar tashigan karvonlarni tasavvur qilish uchun eng yaxshi joy.",
      "Bu yerda Ipak yo'li xaritadagi nom emas, dashtdagi darvoza. Karvonboshilar tuyalarini sanagan joyda turing va shamolga quloq soling."),
     ("Разрушенные ворота караван-сарая XI века на старой дороге между Бухарой и Самаркандом.",
      "Рабат-и Малик построен в XI веке как укреплённый постоялый двор для караванов, пересекавших степь между Бухарой и Самаркандом. Сегодня у трассы сохранились большой портал и часть стен, а рядом стоит старая крытая цистерна (сардоба). Лучшее место на дороге, чтобы представить караваны, которые везли через Узбекистан шёлк, бумагу и пряности.",
      "Здесь Шёлковый путь — не название на карте, а ворота в степи. Встаньте там, где караванщики считали своих верблюдов, и послушайте ветер.")),
    ("gijduvan-ceramics", "Gijduvan Ceramics Workshop", None, "Gijduvan ceramics.jpg",
     "A family pottery in Gijduvan, famous for hand-painted plates and bowls, with a madrasah built by Ulugh Beg in the same town.",
     "Gijduvan, between Bukhara and Navoi, is one of Uzbekistan's best-known pottery towns. Potters here shape and paint plates, bowls and jugs in a style recognised by its deep green, blue and white glazes. In a workshop you can watch the wheel, the painting and the kiln, and buy directly from the makers. The town also has the Ulugh Beg Madrasah, built in 1433, and the tomb of the Sufi teacher Abdulkhalik Gijduvani.",
     "A plate is a small map of a town's patience: every line painted by hand, every glaze waiting for the fire.",
     ("Gijduvonda oilaviy kulolchilik ustaxonasi: qo'lda bo'yalgan lagan va kosalari mashhur; shaharda Ulug'bek qurgan madrasa ham bor.",
      "Buxoro va Navoiy oralig'idagi G'ijduvon O'zbekistonning eng mashhur kulolchilik shaharlaridan biri. Bu yerdagi ustalar to'q yashil, ko'k va oq sirli lagan, kosa va ko'zalarni shakllaydi va bo'yaydi. Ustaxonada charx, naqsh chizish va xumdonni ko'rasiz, ustalarning o'zidan xarid qilasiz. Shaharda 1433-yilda qurilgan Ulug'bek madrasasi va tasavvuf ustozi Abdulxoliq G'ijduvoniy maqbarasi ham bor.",
      "Lagan — shahar sabrining kichik xaritasi: har chiziq qo'lda chizilgan, har sir olovni kutadi."),
     ("Семейная гончарная мастерская в Гиждуване, известная расписными тарелками и пиалами; в городе также медресе, построенное Улугбеком.",
      "Гиждуван между Бухарой и Навои — один из самых известных гончарных городов Узбекистана. Мастера формируют и расписывают тарелки, пиалы и кувшины в манере с глубокой зелёной, синей и белой глазурью. В мастерской можно увидеть круг, роспись и печь и купить прямо у мастеров. В городе также медресе Улугбека (1433) и мавзолей суфийского учителя Абдулхалика Гиждувани.",
      "Тарелка — маленькая карта терпения города: каждая линия нарисована вручную, каждая глазурь ждёт огня.")),
]

PLAN_TEXT = {
    "Meet your guide at your hotel in Samarkand": ("Gid bilan Samarqanddagi mehmonxonada uchrashasiz", "Встреча с гидом в вашем отеле в Самарканде"),
    "Check in at your hotel": ("Mehmonxonaga joylashasiz", "Заселение в отель"),
    "Free evening in Samarkand": ("Samarqandda erkin kechqurun", "Свободный вечер в Самарканде"),
    "Free time: the trading domes and craft workshops of Bukhara": ("Erkin vaqt: Buxoroning savdo gumbazlari va hunarmandlar ustaxonalari", "Свободное время: торговые купола и мастерские ремесленников Бухары"),
    "Farewell dinner in Bukhara": ("Buxoroda xayrlashuv kechki ovqati", "Прощальный ужин в Бухаре"),
    "Drive from Samarkand over the Tahtakaracha pass to Shahrisabz (about 2 hours)": ("Samarqanddan Taxtaqoracha dovoni orqali Shahrisabzga yo'l (taxminan 2 soat)", "Дорога из Самарканда через перевал Тахтакарача в Шахрисабз (около 2 часов)"),
    "Drive from Shahrisabz to Qarshi (about 1.5 hours)": ("Shahrisabzdan Qarshigacha yo'l (taxminan 1,5 soat)", "Дорога из Шахрисабза в Карши (около 1,5 часов)"),
    "Evening walk in Qarshi": ("Qarshida kechki sayr", "Вечерняя прогулка по Карши"),
    "Drive from Qarshi across the desert to Bukhara (about 3.5 hours, with a lunch stop)": ("Qarshidan cho'l orqali Buxoroga yo'l (taxminan 3,5 soat, tushlik uchun to'xtash bilan)", "Дорога из Карши через пустыню в Бухару (около 3,5 часов, с остановкой на обед)"),
    "Arrive in Bukhara and check in": ("Buxoroga yetib kelasiz va mehmonxonaga joylashasiz", "Прибытие в Бухару и заселение"),
    "Drive from Bukhara to Gijduvan (about 45 minutes)": ("Buxorodan G'ijduvonga yo'l (taxminan 45 daqiqa)", "Дорога из Бухары в Гиждуван (около 45 минут)"),
    "Drive on to Samarkand (about 3 hours)": ("Samarqandga qarab yo'lni davom ettirasiz (taxminan 3 soat)", "Дальше едем в Самарканд (около 3 часов)"),
    "Arrive in Samarkand: transfer to your hotel, the station or the airport": ("Samarqandga yetib kelasiz: mehmonxona, vokzal yoki aeroportga transfer", "Прибытие в Самарканд: трансфер в отель, на вокзал или в аэропорт"),
}

TITLE = "7-Day Silk Road Journey: Samarkand, Shahrisabz, Qarshi and Bukhara"
TITLE_T = ("7 kunlik Ipak yo'li sayohati: Samarqand, Shahrisabz, Qarshi va Buxoro", "7-дневное путешествие по Шёлковому пути: Самарканд, Шахрисабз, Карши и Бухара")
SUMMARY = "Seven days through three oasis regions: two days in Samarkand, a day in Shahrisabz and Qarshi, a day on the road to Bukhara, two days in Bukhara and a day back to Samarkand."
SUMMARY_T = ("Yetti kun uch vohada: Samarqandda ikki kun, Shahrisabz va Qarshida bir kun, Buxoroga yo'lda bir kun, Buxoroda ikki kun va Samarqandga qaytish uchun bir kun.",
             "Семь дней в трёх оазисных регионах: два дня в Самарканде, день в Шахрисабзе и Карши, день в дороге в Бухару, два дня в Бухаре и день на обратный путь в Самарканд.")
DESCRIPTION = ("A week on the heart of the Great Silk Road with one guide and one car. You spend two days in Samarkand (Registan, Gur-e-Amir, Bibi-Khanym, Siyob Bazaar, Shah-i-Zinda, the Ulugh Beg Observatory and the Imam al-Bukhari complex), "
               "then cross the Tahtakaracha pass to Shahrisabz, Amir Timur's birthplace (Ak-Saray Palace, Dorut Tilovat), and sleep in Qarshi. "
               "The next day you cross the desert to Bukhara and spend two days in its old town (Ismail Samani, the Ark, Poi Kalon, Chor Minor, Lyabi-Hauz). "
               "On the last day you drive back to Samarkand via the potters of Gijduvan and the caravanserai of Rabat-i-Malik. "
               "The most affordable hotels, a private car with a driver, a licensed guide and breakfasts are included; entrance tickets are paid at the sites. Hotels of 3, 4 or 5 stars and a premium-class car are available for an extra payment.")
DESCRIPTION_T = ("Buyuk Ipak yo'lining yuragida bir hafta: bitta gid va bitta mashina bilan. Samarqandda ikki kun (Registon, Go'ri Amir, Bibixonim, Siyob bozori, Shohizinda, Ulug'bek rasadxonasi va Imom Buxoriy majmuasi), "
                 "so'ng Taxtaqoracha dovoni orqali Amir Temur tug'ilgan Shahrisabzga (Oqsaroy, Dorut Tilovat) o'tasiz va Qarshida tunaysiz. "
                 "Ertasi kuni cho'l orqali Buxoroga yetib, eski shaharda ikki kun bo'lasiz (Ismoil Somoniy, Ark, Poi Kalon, Chor Minor, Labi Hovuz). "
                 "Oxirgi kuni G'ijduvon kulollari va Rabotimalik karvonsaroyi orqali Samarqandga qaytasiz. "
                 "Narxga eng arzon mehmonxonalar, haydovchili shaxsiy mashina, litsenziyali gid va nonushtalar kiradi; kirish chiptalari joyida to'lanadi. 3, 4 yoki 5 yulduzli mehmonxonalar va premium klassdagi mashina qo'shimcha to'lov evaziga mavjud.",
                 "Неделя в сердце Великого Шёлкового пути с одним гидом и одной машиной. Два дня в Самарканде (Регистан, Гур-Эмир, Биби-Ханым, базар Сиаб, Шахи-Зинда, обсерватория Улугбека и комплекс имама аль-Бухари), "
                 "затем через перевал Тахтакарача — в Шахрисабз, на родину Амира Тимура (дворец Ак-Сарай, Дорут Тилават), ночёвка в Карши. "
                 "На следующий день — через пустыню в Бухару и два дня в старом городе (Исмаила Самани, Арк, Пои-Калон, Чор-Минор, Ляби-Хауз). "
                 "В последний день — обратно в Самарканд через гончаров Гиждувана и караван-сарай Рабат-и Малик. "
                 "В стоимость входят самые доступные отели, частная машина с водителем, лицензированный гид и завтраки; входные билеты оплачиваются на месте. Отели 3, 4 или 5 звёзд и машина премиум-класса доступны за дополнительную плату.")
STORY = "Seven days, three oases and one road: you will remember how the light changes from Samarkand's blue to Bukhara's sand."
STORY_T = ("Yetti kun, uch voha, bitta yo'l: Samarqandning moviy rangidan Buxoroning qum rangigacha yorug'lik qanday o'zgarishini eslab qolasiz.",
           "Семь дней, три оазиса и одна дорога: вы запомните, как свет меняется от синевы Самарканда до песочного цвета Бухары.")
MEETING = "Your hotel in Samarkand"
MEETING_T = ("Samarqanddagi mehmonxonangiz", "Ваш отель в Самарканде")

HIGHLIGHTS = [
    ("Two days in Samarkand: Registan, Gur-e-Amir, Shah-i-Zinda and the Ulugh Beg Observatory", "Samarqandda ikki kun: Registon, Go'ri Amir, Shohizinda va Ulug'bek rasadxonasi", "Два дня в Самарканде: Регистан, Гур-Эмир, Шахи-Зинда и обсерватория Улугбека"),
    ("Shahrisabz: Ak-Saray Palace and Amir Timur's birthplace", "Shahrisabz: Oqsaroy va Amir Temur tug'ilgan joy", "Шахрисабз: дворец Ак-Сарай и родина Амира Тимура"),
    ("A night in Qarshi and a drive across the desert to Bukhara", "Qarshida tunash va cho'l orqali Buxoroga yo'l", "Ночь в Карши и дорога через пустыню в Бухару"),
    ("Two days in Bukhara's old town: the Ark, Poi Kalon, Chor Minor and Lyabi-Hauz", "Buxoroning eski shahrida ikki kun: Ark, Poi Kalon, Chor Minor va Labi Hovuz", "Два дня в старом городе Бухары: Арк, Пои-Калон, Чор-Минор и Ляби-Хауз"),
    ("Return via the potters of Gijduvan and the Rabat-i-Malik caravanserai", "G'ijduvon kulollari va Rabotimalik karvonsaroyi orqali qaytish", "Возвращение через гончаров Гиждувана и караван-сарай Рабат-и Малик"),
]
INCLUDED = [
    ("Six nights in the most affordable hotels (2 in Samarkand, 1 in Qarshi, 3 in Bukhara) with breakfast", "Eng arzon mehmonxonalarda olti tun (Samarqandda 2, Qarshida 1, Buxoroda 3), nonushta bilan", "Шесть ночей в самых доступных отелях (2 в Самарканде, 1 в Карши, 3 в Бухаре) с завтраком"),
    ("Private car with a driver for all seven days", "Yetti kun davomida haydovchili shaxsiy mashina", "Частная машина с водителем на все семь дней"),
    ("Licensed local guide", "Litsenziyali mahalliy gid", "Лицензированный местный гид"),
]
EXCLUDED = ["Entrance tickets", "Lunch", "Dinner"]
FEES = {"Registan Square": 16, "Gur-e-Amir Mausoleum": 13, "Bibi-Khanym Mosque": 9, "Siyob Bazaar": 1, "Shah-i-Zinda": 11, "Ulugh Beg Observatory": 29,
        "Imam al-Bukhari Complex": 29, "Ak-Saray Palace": 8, "Amir Timur Birthplace": 3, "Dorut Tilovat Complex": 6, "Ark Fortress": 8, "Poi Kalon Complex": 10,
        "Lyabi-Hauz": 2, "Chor Minor": 3, "Ismail Samani Mausoleum": 6}
EXTRA_STOPS = ["Kok-Gumbaz Mosque (Qarshi)", "Gijduvan Ceramics Workshop", "Rabat-i-Malik Caravanserai"]
ORDER = list(FEES) + EXTRA_STOPS
ROUTE = [f"{name} | {FEES[name]}" if name in FEES else name for name in ORDER]


def index(name):
    return ORDER.index(name)


def meal(time, kind, included):
    return {"time": time, "type": "meal", "meal": kind, "included": included}


def visit(time, name):
    return {"time": time, "type": "visit", "stop": index(name)}


def go(time, name):
    return {"time": time, "type": "transfer", "stop": index(name)}


def step(time, text):
    uz, ru = PLAN_TEXT[text]
    return {"time": time, "type": "step", "text": text, "i18n": {"uz": uz, "ru": ru}}


ITINERARY = [
    {"day": 1, "items": [step("09:00", "Meet your guide at your hotel in Samarkand"), visit("10:00", "Registan Square"), visit("12:00", "Bibi-Khanym Mosque"),
                         meal("13:30", "lunch", False), visit("14:30", "Siyob Bazaar"), visit("16:00", "Shah-i-Zinda"), meal("19:00", "dinner", False)]},
    {"day": 2, "items": [meal("08:00", "breakfast", True), visit("09:00", "Gur-e-Amir Mausoleum"), visit("11:00", "Ulugh Beg Observatory"), meal("13:00", "lunch", False),
                         go("14:00", "Imam al-Bukhari Complex"), visit("15:00", "Imam al-Bukhari Complex"), step("18:00", "Free evening in Samarkand")]},
    {"day": 3, "items": [meal("07:00", "breakfast", True), step("07:30", "Drive from Samarkand over the Tahtakaracha pass to Shahrisabz (about 2 hours)"),
                         visit("09:30", "Ak-Saray Palace"), visit("11:00", "Amir Timur Birthplace"), visit("12:00", "Dorut Tilovat Complex"), meal("13:00", "lunch", False),
                         step("15:00", "Drive from Shahrisabz to Qarshi (about 1.5 hours)"), step("17:00", "Check in at your hotel"), step("18:00", "Evening walk in Qarshi"), meal("19:30", "dinner", False)]},
    {"day": 4, "items": [meal("07:30", "breakfast", True), visit("09:00", "Kok-Gumbaz Mosque (Qarshi)"),
                         step("10:00", "Drive from Qarshi across the desert to Bukhara (about 3.5 hours, with a lunch stop)"), meal("13:00", "lunch", False),
                         step("15:30", "Arrive in Bukhara and check in"), visit("17:30", "Lyabi-Hauz"), meal("19:30", "dinner", False)]},
    {"day": 5, "items": [meal("08:00", "breakfast", True), visit("09:00", "Ismail Samani Mausoleum"), visit("10:30", "Ark Fortress"), meal("13:00", "lunch", False),
                         visit("14:30", "Poi Kalon Complex"), meal("19:00", "dinner", False)]},
    {"day": 6, "items": [meal("08:00", "breakfast", True), visit("09:30", "Chor Minor"), step("11:00", "Free time: the trading domes and craft workshops of Bukhara"),
                         meal("13:00", "lunch", False), step("19:00", "Farewell dinner in Bukhara")]},
    {"day": 7, "items": [meal("07:30", "breakfast", True), step("08:30", "Drive from Bukhara to Gijduvan (about 45 minutes)"), visit("09:30", "Gijduvan Ceramics Workshop"),
                         step("11:30", "Drive on to Samarkand (about 3 hours)"), visit("12:30", "Rabat-i-Malik Caravanserai"), meal("13:30", "lunch", False),
                         step("16:00", "Arrive in Samarkand: transfer to your hotel, the station or the airport")]},
]


def register_phrases():
    """Add the translations of the package texts to the shared phrase book."""
    PHRASES[TITLE] = tr(*TITLE_T)
    PHRASES[SUMMARY] = tr(*SUMMARY_T)
    PHRASES[DESCRIPTION] = tr(*DESCRIPTION_T)
    PHRASES[STORY] = tr(*STORY_T)
    PHRASES[MEETING] = tr(*MEETING_T)
    PHRASES["7 days"] = tr("7 kun", "7 дней")
    PHRASES["Two days through Samarkand's must-see places with a local guide, taxi rides between stops and pickup from the airport."] = tr(
        "Samarqandning ko'rilishi shart joylari bo'ylab ikki kun: mahalliy gid, joylar orasida taksi va aeroportdan kutib olish.",
        "Два дня по главным местам Самарканда с местным гидом, такси между остановками и встречей в аэропорту.")
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


def package_fields(base):
    """Fields of the package tour, built on the shared defaults of the regional tours."""
    return dict(base, title=TITLE, destination_slug="samarkand", destination_name="Samarkand", category="Culture", duration_label="7 days", group_type="Small group",
                tour_type="car", group_pricing=True, summary=SUMMARY, description=DESCRIPTION, story=STORY, meeting_point=MEETING, price_from_usd=PRICE, featured=True,
                image_url=photo("Registan Samarkand Uzbekistan.JPG"), route=ROUTE, itinerary=ITINERARY, highlights=[h[0] for h in HIGHLIGHTS],
                included=[i[0] for i in INCLUDED] + ["Taxi service between the places", "Airport pickup"], excluded=EXCLUDED, parent_slug="", entrance_fee_usd=None)
