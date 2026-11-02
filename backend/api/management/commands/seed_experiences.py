"""Hands-on food experiences in Samarkand: baking non in a tandir, cooking plov in a kazan, and both together.

Visitors take home what they make. Texts are written in English, Uzbek and Russian; titles are also translated into French,
German and Spanish. Photos are linked from Wikimedia Commons. Prices are sample prices to edit in the admin panel.
"""
from api.management.commands.seed_regions import photo
from api.management.commands.seed_translations import PHRASES

HERE = "Your hotel in Samarkand"


def step(time, text, uz, ru):
    return {"time": time, "type": "step", "text": text, "i18n": {"uz": uz, "ru": ru}}


def lunch(time):
    return {"time": time, "type": "meal", "meal": "lunch", "included": True}


def tr(uz, ru, fr="", de="", es=""):
    return (uz, ru, fr, de, es)


PICKUP = ("Hotel pickup in Samarkand", "Samarqanddagi mehmonxonadan olib ketish", "Встреча в вашем отеле в Самарканде")

EXPERIENCES = [
    dict(
        slug="samarkand-non-baking-class", title="Samarkand Non Bread Baking Class", price=35, duration="2 hours", image="Tandir_non_tayyorlayotgan_novvoy.jpg",
        titles=tr("Samarqand noni yopish darsi", "Мастер-класс по выпечке самаркандской лепёшки", "Atelier de cuisson du pain non de Samarcande", "Backkurs für Samarkand-Non-Brot", "Taller de pan non de Samarcanda"),
        guide="Local master baker", guides=tr("Mahalliy usta novvoy", "Местный мастер-пекарь"),
        summary="Knead, stamp and bake your own Samarkand non in a clay tandir with a local master baker, then take the warm bread home.",
        summaries=tr("Mahalliy usta novvoy bilan o'z Samarqand noningiz uchun xamir qoring, naqsh bosing va sopol tandirda yoping, so'ng issiq nonni o'zingiz bilan olib keting.",
                     "Замесите, украсьте узором и испеките собственную самаркандскую лепёшку в глиняном тандыре вместе с местным мастером-пекарем — и увезите тёплый хлеб с собой."),
        description=("Samarkand non is famous across Central Asia: a thick, round loaf stamped with a pattern and baked on the inner wall of a clay tandir. "
                     "In this hands-on class a local master baker shows you how to prepare the dough, shape and stamp the loaf with the traditional chekich, "
                     "and press it onto the hot oven wall. While it bakes you drink tea and hear how bread stands at the centre of Uzbek hospitality. "
                     "You eat a piece fresh from the oven and take your own bread home. No experience is needed; the class suits beginners and families."),
        descriptions=tr("Samarqand noni butun Markaziy Osiyoda mashhur: qalin, yumaloq, naqsh bosilgan va sopol tandirning ichki devorida yopiladigan non. Bu amaliy darsda mahalliy usta novvoy xamir tayyorlashni, nonni shakllash va an'anaviy chekich bilan naqsh bosishni hamda uni qizib turgan tandir devoriga yopishtirishni ko'rsatadi. Non pishayotganda choy ichasiz va non o'zbek mehmondo'stligining markazida turishini eshitasiz. Yangi nonning bir bo'lagini tatib ko'rasiz va o'zingiz yopgan nonni uyga olib ketasiz. Tajriba shart emas; dars yangi boshlovchilar va oilalar uchun mos.",
                        "Самаркандская лепёшка известна по всей Центральной Азии: толстый круглый хлеб с узором, который выпекают на внутренней стенке глиняного тандыра. На этом практическом занятии местный мастер-пекарь покажет, как приготовить тесто, сформировать лепёшку, украсить её узором традиционным чекичем и прижать к раскалённой стенке печи. Пока хлеб печётся, вы пьёте чай и узнаёте, почему хлеб — центр узбекского гостеприимства. Вы пробуете кусочек прямо из печи и увозите свою лепёшку с собой. Опыт не нужен: занятие подходит новичкам и семьям."),
        highlights=[("Knead, shape and stamp your own non", "O'z noningiz uchun xamir qoring, shakl bering va naqsh bosing", "Замесите, сформируйте и украсьте узором собственную лепёшку"),
                    ("Bake it on the wall of a real clay tandir", "Uni haqiqiy sopol tandir devorida yoping", "Испеките её на стенке настоящего глиняного тандыра"),
                    ("Taste it hot, with tea", "Issiqligida, choy bilan tatib ko'ring", "Попробуйте горячей, с чаем"),
                    ("Take your own bread home", "O'zingiz yopgan nonni uyga olib ketasiz", "Увезите собственный хлеб с собой")],
        included=[("Hotel pickup and drop-off", "Mehmonxonadan olib ketish va qaytarish", "Трансфер от отеля и обратно"),
                  ("Instruction by a local master baker", "Mahalliy usta novvoy ko'rsatmasi", "Обучение у местного мастера-пекаря"),
                  ("All ingredients and an apron", "Barcha masalliqlar va fartuk", "Все ингредиенты и фартук"),
                  ("Tea and fresh bread", "Choy va yangi non", "Чай и свежий хлеб"),
                  ("Your own bread to take home", "O'zingiz yopgan non — o'zingiz bilan", "Ваша лепёшка — с собой")],
        story="The smell of bread from a clay oven is the oldest welcome in Central Asia. Carry your own loaf home and it will keep a little of Samarkand's warmth.",
        stories=tr("Sopol tandirdan chiqqan non hidi Markaziy Osiyodagi eng qadimiy mehmondo'stlik belgisi. O'zingiz yopgan nonni olib ketsangiz, unda Samarqand mehrining bir parchasi saqlanadi.",
                   "Запах хлеба из глиняной печи — самое древнее приветствие Центральной Азии. Увезите свою лепёшку домой — и в ней останется немного самаркандского тепла."),
        plan=[step("09:30", *PICKUP),
              step("10:00", "Meet the baker and learn the dough: flour, water, salt and patience", "Novvoy bilan tanishing va xamirni o'rganing: un, suv, tuz va sabr", "Знакомство с пекарем и тесто: мука, вода, соль и терпение"),
              step("10:30", "Shape your loaf and stamp the pattern with a chekich", "Nonni shakllang va chekich bilan naqsh bosing", "Сформируйте лепёшку и нанесите узор чекичем"),
              step("11:00", "Bake it on the wall of the tandir", "Uni tandir devorida yoping", "Испеките её на стенке тандыра"),
              step("11:30", "Taste your bread hot, with tea and jam", "Nonni choy va murabbo bilan issiqligida tatib ko'ring", "Попробуйте хлеб горячим — с чаем и вареньем"),
              step("11:45", "Pack your bread and return to your hotel", "Nonni o'rab, mehmonxonaga qaytasiz", "Упакуйте хлеб и возвращайтесь в отель")],
    ),
    dict(
        slug="samarkand-plov-masterclass", title="Samarkand Plov Masterclass", price=65, duration="4 hours", image="Plov_Tashkent.jpg",
        titles=tr("Samarqand osh pishirish ustozlik darsi", "Мастер-класс по плову в Самарканде", "Masterclass de plov à Samarcande", "Plov-Kochkurs in Samarkand", "Masterclass de plov en Samarcanda"),
        guide="Local cook (oshpaz)", guides=tr("Mahalliy oshpaz", "Местный повар (ошпаз)"),
        summary="Shop at Siyob Bazaar, cook real Samarkand plov in a kazan with a local cook, eat it together and take a portion home.",
        summaries=tr("Siyob bozorida xarid qiling, mahalliy oshpaz bilan qozonda haqiqiy Samarqand oshini pishiring, birga yeng va bir qismini o'zingiz bilan olib keting.",
                     "Сделайте покупки на базаре Сиаб, приготовьте настоящий самаркандский плов в казане с местным поваром, съешьте его вместе и увезите порцию с собой."),
        description=("Plov is the dish of Uzbek celebrations, and cooking it is a ritual. Your local cook (oshpaz) meets you at Siyob Bazaar, where you choose the rice, "
                     "yellow carrots and lamb. In the kitchen you cut, fry and layer everything in a large kazan, learning the secrets of the zirvak and the timing of the steam. "
                     "While the plov rests you prepare a fresh tomato and onion salad. Everyone sits down to eat the plov you cooked, and you leave with a take-away portion and a printed recipe card."),
        descriptions=tr("Osh — o'zbek bayramlarining taomi, uni pishirish esa marosim. Mahalliy oshpaz sizni Siyob bozorida kutib oladi, bu yerda guruch, sariq sabzi va qo'y go'shtini tanlaysiz. Oshxonada hamma narsani to'g'rab, qovurib, katta qozonga solasiz, zirvak sirlari va dam berish vaqtini o'rganasiz. Osh dam yeyotganda yangi pomidor-piyoz salati tayyorlaysiz. Hamma o'zingiz pishirgan oshni birga yeydi, siz esa olib ketish uchun osh va bosma retsept kartasi bilan qaytasiz.",
                        "Плов — блюдо узбекских праздников, а его приготовление — настоящий ритуал. Местный повар (ошпаз) встретит вас на базаре Сиаб, где вы выберете рис, жёлтую морковь и баранину. На кухне вы нарежете, обжарите и выложите всё слоями в большом казане, узнаете секреты зирвака и тонкости пара. Пока плов настаивается, вы приготовите свежий салат из помидоров и лука. Все вместе садятся есть плов, который вы приготовили, а вы уходите с порцией на вынос и печатной карточкой рецепта."),
        highlights=[("Shop for ingredients at Siyob Bazaar with your cook", "Siyob bozorida oshpaz bilan masalliq xarid qiling", "Выберите продукты на базаре Сиаб вместе с поваром"),
                    ("Cook plov in a traditional kazan", "An'anaviy qozonda osh pishiring", "Приготовьте плов в традиционном казане"),
                    ("Learn the secrets of zirvak and steam", "Zirvak va dam berish sirlarini o'rganing", "Узнайте секреты зирвака и пара"),
                    ("Eat what you cooked and take a portion home", "O'zingiz pishirganni yeng va bir qismini olib keting", "Съешьте приготовленное и увезите порцию с собой")],
        included=[("Hotel pickup and drop-off", "Mehmonxonadan olib ketish va qaytarish", "Трансфер от отеля и обратно"),
                  ("Market visit with your cook", "Oshpaz bilan bozorga borish", "Поход на базар с поваром"),
                  ("All ingredients and an apron", "Barcha masalliqlar va fartuk", "Все ингредиенты и фартук"),
                  ("Lunch of the plov you cooked", "O'zingiz pishirgan osh bilan tushlik", "Обед из плова, который вы приготовили"),
                  ("Take-away portion of plov and a recipe card", "O'zingiz bilan olib ketadigan osh va retsept kartasi", "Порция плова с собой и карточка с рецептом")],
        story="Plov is never just rice. It is the meal that brings a family together, and now you have stirred it with your own hands. Take the recipe home and invite someone you love.",
        stories=tr("Osh hech qachon shunchaki guruch emas. U oilani bir joyga to'playdigan taom, endi uni o'z qo'lingiz bilan aralashtirdingiz. Retseptni uyga olib boring va yaqin odamingizni taklif qiling.",
                   "Плов — никогда не просто рис. Это блюдо, объединяющее семью, и теперь вы помешивали его своими руками. Увезите рецепт домой и позовите близкого человека."),
        plan=[step("09:00", *PICKUP),
              step("09:30", "Shop for rice, carrots, onions and lamb at Siyob Bazaar", "Siyob bozorida guruch, sabzi, piyoz va qo'y go'shti xarid qilish", "Покупка риса, моркови, лука и баранины на базаре Сиаб"),
              step("10:30", "Prepare the ingredients and light the fire under the kazan", "Masalliqlarni tayyorlash va qozon ostiga o't yoqish", "Подготовка продуктов и розжиг огня под казаном"),
              step("11:00", "Fry the meat, make the zirvak and layer the rice", "Go'shtni qovuring, zirvak tayyorlang va guruchni soling", "Обжарьте мясо, приготовьте зирвак и выложите рис"),
              step("12:00", "Let it steam while you make a fresh salad", "Osh dam yeyotganda yangi salat tayyorlang", "Пока плов томится, приготовьте свежий салат"),
              lunch("13:00"),
              step("13:30", "Pack your take-away portion and recipe card, then return to your hotel", "Olib ketish uchun osh va retsept kartasini o'rab, mehmonxonaga qaytasiz", "Упакуйте порцию с собой и карточку рецепта, возвращение в отель")],
    ),
    dict(
        slug="samarkand-plov-and-non-masterclass", title="Plov & Non Masterclass", price=89, duration="5 hours", image="Tandir_nonlarini_ko‘rsatayotgan_novvoy.jpg",
        titles=tr("Osh va non ustozlik darsi", "Мастер-класс: плов и лепёшка", "Masterclass plov et pain non", "Plov- & Non-Kochkurs", "Masterclass de plov y pan non"),
        guide="Local cook (oshpaz)", guides=tr("Mahalliy oshpaz", "Местный повар (ошпаз)"),
        summary="The full Samarkand food morning: market, plov in a kazan and your own non from the tandir, with a shared lunch and treats to take home.",
        summaries=tr("To'liq Samarqand taomlari ertalabi: bozor, qozonda osh va tandirdan o'z noningiz, birgalikda tushlik va olib ketish uchun sovg'alar.",
                     "Полное самаркандское гастрономическое утро: базар, плов в казане и собственная лепёшка из тандыра, общий обед и угощения с собой."),
        description=("The full Samarkand food experience in one morning. Start at Siyob Bazaar to shop with your cook, then prepare plov in a kazan and, while it steams, "
                     "shape and bake your own non in the tandir. Sit down to a shared lunch of the plov and fresh bread, and leave with a take-away portion of plov, "
                     "your own loaf, a printed recipe card and a certificate of participation."),
        descriptions=tr("Bir ertalabda to'liq Samarqand taomlari tajribasi. Siyob bozorida oshpaz bilan xarid qilishdan boshlaysiz, so'ng qozonda osh tayyorlaysiz va u dam yeyotganda tandirda o'z noningizni shakllab yopasiz. Osh va yangi non bilan birgalikda tushlik qilasiz, olib ketish uchun osh, o'zingiz yopgan non, bosma retsept kartasi va ishtirok sertifikati bilan qaytasiz.",
                        "Полный самаркандский гастрономический опыт за одно утро. Начните на базаре Сиаб — сделайте покупки вместе с поваром, затем приготовьте плов в казане и, пока он томится, сформируйте и испеките собственную лепёшку в тандыре. Сядьте за общий обед из плова и свежего хлеба и уходите с порцией плова на вынос, своей лепёшкой, печатной карточкой рецепта и сертификатом участника."),
        highlights=[("Shop for ingredients at Siyob Bazaar with your cook", "Siyob bozorida oshpaz bilan masalliq xarid qiling", "Выберите продукты на базаре Сиаб вместе с поваром"),
                    ("Cook plov in a traditional kazan", "An'anaviy qozonda osh pishiring", "Приготовьте плов в традиционном казане"),
                    ("Knead, shape and stamp your own non", "O'z noningiz uchun xamir qoring, shakl bering va naqsh bosing", "Замесите, сформируйте и украсьте узором собственную лепёшку"),
                    ("Eat what you cooked and take a portion home", "O'zingiz pishirganni yeng va bir qismini olib keting", "Съешьте приготовленное и увезите порцию с собой")],
        included=[("Hotel pickup and drop-off", "Mehmonxonadan olib ketish va qaytarish", "Трансфер от отеля и обратно"),
                  ("Market visit with your cook", "Oshpaz bilan bozorga borish", "Поход на базар с поваром"),
                  ("All ingredients and an apron", "Barcha masalliqlar va fartuk", "Все ингредиенты и фартук"),
                  ("Lunch of the plov you cooked", "O'zingiz pishirgan osh bilan tushlik", "Обед из плова, который вы приготовили"),
                  ("Your own bread to take home", "O'zingiz yopgan non — o'zingiz bilan", "Ваша лепёшка — с собой"),
                  ("Take-away portion of plov and a recipe card", "O'zingiz bilan olib ketadigan osh va retsept kartasi", "Порция плова с собой и карточка с рецептом"),
                  ("Certificate of participation", "Ishtirok sertifikati", "Сертификат участника")],
        story="Bread from the tandir and plov from the kazan: the two hearts of an Uzbek table, made by your own hands. Take them home, and the table at home will remember Samarkand.",
        stories=tr("Tandirdan non va qozondan osh — o'zbek dasturxonining ikki qalbi, o'z qo'lingiz bilan yaratilgan. Ularni uyga olib boring, uydagi dasturxon Samarqandni eslab turadi.",
                   "Хлеб из тандыра и плов из казана — два сердца узбекского стола, созданные вашими руками. Увезите их домой — и стол дома будет помнить Самарканд."),
        plan=[step("09:00", *PICKUP),
              step("09:30", "Shop for rice, carrots, onions and lamb at Siyob Bazaar", "Siyob bozorida guruch, sabzi, piyoz va qo'y go'shti xarid qilish", "Покупка риса, моркови, лука и баранины на базаре Сиаб"),
              step("10:30", "Cook the plov in the kazan: fry the meat, make the zirvak, layer the rice", "Qozonda osh pishiring: go'shtni qovuring, zirvak qiling, guruchni soling", "Готовим плов в казане: обжариваем мясо, делаем зирвак, выкладываем рис"),
              step("11:30", "While the plov steams, shape and stamp your non and bake it in the tandir", "Osh dam yeyotganda nonni shakllab, naqsh bosing va tandirda yoping", "Пока плов томится, сформируйте лепёшку, нанесите узор и испеките её в тандыре"),
              lunch("13:00"),
              step("13:45", "Pack your plov, bread and recipe card, then return to your hotel", "Osh, non va retsept kartasini o'rab, mehmonxonaga qaytasiz", "Упакуйте плов, хлеб и карточку рецепта, возвращение в отель")],
    ),
]

TIMES = {"2 hours": tr("2 soat", "2 часа", "2 heures", "2 Stunden", "2 horas"),
         "4 hours": tr("4 soat", "4 часа", "4 heures", "4 Stunden", "4 horas"),
         "5 hours": tr("5 soat", "5 часов", "5 heures", "5 Stunden", "5 horas")}
SHARED = {
    "Tips (optional)": tr("Choyxo'rlik (ixtiyoriy)", "Чаевые (по желанию)", "Pourboires (facultatif)", "Trinkgeld (optional)", "Propinas (opcional)"),
    "Hands-on class": tr("Amaliy dars", "Практическое занятие", "Atelier pratique", "Praxiskurs", "Taller práctico"),
}


def register_phrases():
    PHRASES.update(TIMES)
    PHRASES.update(SHARED)
    for e in EXPERIENCES:
        PHRASES[e["title"]] = e["titles"]
        PHRASES[e["guide"]] = e["guides"]
        PHRASES[e["summary"]] = tuple(e["summaries"]) if len(e["summaries"]) == 5 else e["summaries"]
        PHRASES[e["description"]] = e["descriptions"]
        PHRASES[e["story"]] = e["stories"]
        PHRASES[PICKUP[0]] = tr(PICKUP[1], PICKUP[2])
        for en, uz, ru in e["highlights"] + e["included"]:
            PHRASES.setdefault(en, tr(uz, ru))
        for item in e["plan"]:
            if item["type"] == "step":
                PHRASES.setdefault(item["text"], tr(item["i18n"]["uz"], item["i18n"]["ru"]))


register_phrases()
