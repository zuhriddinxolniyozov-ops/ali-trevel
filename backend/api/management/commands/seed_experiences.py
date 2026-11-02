"""Hands-on food experiences in Samarkand: bake and taste non from a clay tandir, cook and taste plov from a kazan, or both.

Guests shape the food themselves, taste it together at the dastarkhan and take the rest home. Texts are written in English, Uzbek
and Russian; titles are also translated into French, German and Spanish. Photos are linked from Wikimedia Commons. Prices are sample
prices to edit in the admin panel.
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

TASTE_NON = step("11:30", "Sit at the dastarkhan and taste your bread hot, with tea, honey and dried fruit",
                 "Dasturxonga oʻtiring va noningizni choy, asal va quritilgan mevalar bilan issiqligida tatib koʻring",
                 "Сядьте за дастархан и попробуйте лепёшку горячей — с чаем, мёдом и сухофруктами")
TASTE_PLOV_HIGHLIGHT = ("Taste what you cooked at the dastarkhan and take a portion home", "Pishirganingizni dasturxonda tatib koʻring va bir qismini olib keting",
                        "Попробуйте приготовленное за дастарханом и увезите порцию с собой")

EXPERIENCES = [
    dict(
        slug="samarkand-non-baking-class", title="Bake & Taste Samarkand Non", price=35, duration="2 hours", image="Tandir_non_tayyorlayotgan_novvoy.jpg",
        titles=tr("Samarqand nonini yoping va tatib koʻring", "Испеките и попробуйте самаркандскую лепёшку", "Cuire et goûter le pain non de Samarcande", "Samarkand-Non backen und probieren", "Hornee y pruebe el pan non de Samarcanda"),
        guide="Local master baker", guides=tr("Mahalliy usta novvoy", "Местный мастер-пекарь"),
        summary="Shape and bake your own Samarkand non on the wall of a clay tandir, then taste it hot at the dastarkhan and take the rest home.",
        summaries=tr("Samarqand noningizni sopol tandir devorida shakllab yoping, soʻng dasturxonda issiqligida tatib koʻring va qolganini uyga olib keting.",
                     "Сформируйте и испеките собственную самаркандскую лепёшку на стенке глиняного тандыра, затем попробуйте её горячей за дастарханом и увезите остальное домой."),
        description=("Samarkand non is more than bread: a thick, round loaf stamped with a flower-like pattern and baked on the inner wall of a clay tandir until it turns golden. "
                     "A local master baker welcomes you at his tandir, shows how the dough is prepared and lets you shape and stamp your own loaf. "
                     "You press it onto the hot wall yourself and wait the few minutes it takes for the crust to crackle. "
                     "Then comes the best part: you sit at the dastarkhan and taste your bread hot from the oven, with tea, butter, honey and dried fruit, as Samarkand has done for centuries. "
                     "Whatever is left, you take home. No experience is needed; it suits beginners and families."),
        descriptions=tr("Samarqand noni — shunchaki non emas: guldek naqsh bosilgan, qalin, yumaloq, sopol tandirning ichki devorida tilla rangga kirguncha yopiladigan non. "
                        "Mahalliy usta novvoy sizni tandir yonida kutib oladi, xamir qanday tayyorlanishini koʻrsatadi va oʻz noningizni shakllab, naqsh bosishga imkon beradi. "
                        "Uni qizib turgan devorga oʻzingiz yopishtirasiz va qobigʻi chitirlab pishishini bir necha daqiqa kutasiz. "
                        "Eng yoqimli lahza esa shundan keyin: dasturxon atrofida oʻz noningizni tandirdan issiq holda choy, saryogʻ, asal va quritilgan mevalar bilan tatib koʻrasiz — Samarqand asrlardan beri shunday qilib kelgan. "
                        "Qolganini uyga olib ketasiz. Tajriba shart emas; bu yangi boshlovchilar va oilalar uchun mos.",
                        "Самаркандская лепёшка — это больше, чем хлеб: толстая круглая лепёшка с цветочным узором, которую пекут на внутренней стенке глиняного тандыра до золотистой корочки. "
                        "Местный мастер-пекарь встретит вас у тандыра, покажет, как готовят тесто, и даст сформировать и украсить узором собственную лепёшку. "
                        "Вы сами прижмёте её к раскалённой стенке и подождёте несколько минут, пока корочка заиграет. "
                        "А затем самое приятное: за дастарханом вы попробуете свою лепёшку горячей, прямо из печи — с чаем, маслом, мёдом и сухофруктами, как это делает Самарканд веками. "
                        "Остальное увезёте с собой. Опыт не нужен: подходит новичкам и семьям."),
        highlights=[("Shape and stamp your own Samarkand non", "Oʻz Samarqand noningizni shakllang va naqsh bosing", "Сформируйте и украсьте узором собственную самаркандскую лепёшку"),
                    ("Press it onto the wall of a real clay tandir", "Uni haqiqiy sopol tandir devoriga yopishtiring", "Прижмите её к стенке настоящего глиняного тандыра"),
                    ("Taste it hot at the dastarkhan with tea, honey and dried fruit", "Dasturxonda issiqligida choy, asal va quritilgan mevalar bilan tatib koʻring", "Попробуйте горячей за дастарханом — с чаем, мёдом и сухофруктами"),
                    ("Take your own bread home", "O'zingiz yopgan nonni uyga olib ketasiz", "Увезите собственный хлеб с собой")],
        included=[("Hotel pickup and drop-off", "Mehmonxonadan olib ketish va qaytarish", "Трансфер от отеля и обратно"),
                  ("A local master baker by your side", "Yoningizda mahalliy usta novvoy", "Местный мастер-пекарь рядом с вами"),
                  ("All ingredients and an apron", "Barcha masalliqlar va fartuk", "Все ингредиенты и фартук"),
                  ("Tasting at the dastarkhan: tea, honey and dried fruit", "Dasturxonda tatib koʻrish: choy, asal va quritilgan mevalar", "Дегустация за дастарханом: чай, мёд и сухофрукты"),
                  ("Your own bread to take home", "O'zingiz yopgan non — o'zingiz bilan", "Ваша лепёшка — с собой")],
        story="The smell of bread from a clay oven is the oldest welcome in Central Asia. Carry your own loaf home and it will keep a little of Samarkand's warmth.",
        stories=tr("Sopol tandirdan chiqqan non hidi Markaziy Osiyodagi eng qadimiy mehmondo'stlik belgisi. O'zingiz yopgan nonni olib ketsangiz, unda Samarqand mehrining bir parchasi saqlanadi.",
                   "Запах хлеба из глиняной печи — самое древнее приветствие Центральной Азии. Увезите свою лепёшку домой — и в ней останется немного самаркандского тепла."),
        plan=[step("09:30", *PICKUP),
              step("10:00", "Meet the baker and see how the dough is made: flour, water, salt and patience", "Novvoy bilan tanishing va xamir qanday tayyorlanishini koʻring: un, suv, tuz va sabr", "Знакомство с пекарем и тесто: мука, вода, соль и терпение"),
              step("10:30", "Shape your loaf and stamp the pattern with a chekich", "Nonni shakllang va chekich bilan naqsh bosing", "Сформируйте лепёшку и нанесите узор чекичем"),
              step("11:00", "Press it onto the wall of the tandir", "Uni tandir devoriga yopishtiring", "Прижмите её к стенке тандыра"),
              TASTE_NON,
              step("11:45", "Pack your bread and return to your hotel", "Nonni o'rab, mehmonxonaga qaytasiz", "Упакуйте хлеб и возвращайтесь в отель")],
    ),
    dict(
        slug="samarkand-plov-masterclass", title="Cook & Taste Samarkand Plov", price=65, duration="4 hours", image="Plov_Tashkent.jpg",
        titles=tr("Samarqand oshini pishiring va tatib koʻring", "Приготовьте и попробуйте самаркандский плов", "Cuisiner et goûter le plov de Samarcande", "Samarkander Plov kochen und probieren", "Cocine y pruebe el plov de Samarcanda"),
        guide="Local cook (oshpaz)", guides=tr("Mahalliy oshpaz", "Местный повар (ошпаз)"),
        summary="Shop at Siyob Bazaar with a local cook, cook Samarkand plov in a kazan, taste it together at the dastarkhan and take a portion home.",
        summaries=tr("Siyob bozorida oshpaz bilan xarid qiling, qozonda haqiqiy Samarqand oshini pishiring, dasturxonda birga tatib koʻring va bir qismini oʻzingiz bilan olib keting.",
                     "Сделайте покупки на базаре Сиаб с местным поваром, приготовьте настоящий самаркандский плов в казане, попробуйте его вместе за дастарханом и увезите порцию с собой."),
        description=("Plov is the dish of Uzbek celebrations, and cooking it is a ritual. Your local cook (oshpaz) meets you at Siyob Bazaar, where you choose the rice, "
                     "yellow carrots and lamb by sight and smell. In the kitchen you cut, fry and layer everything in a large kazan, learning the secrets of the zirvak and the steam while the fragrance fills the courtyard. "
                     "While the plov rests you prepare a fresh tomato and onion salad. Then everyone sits down at the dastarkhan to taste the plov you cooked, with fresh bread and green tea, "
                     "and you leave with a take-away portion and a printed recipe card."),
        descriptions=tr("Osh — oʻzbek bayramlarining taomi, uni pishirish esa marosim. Mahalliy oshpaz sizni Siyob bozorida kutib oladi, bu yerda guruch, sariq sabzi va qoʻy goʻshtini koʻz va hid bilan tanlaysiz. "
                        "Oshxonada hamma narsani toʻgʻrab, qovurib, katta qozonga solasiz; hovlini hid egallab turganda zirvak va dam berish sirlarini oʻrganasiz. "
                        "Osh dam yeyotganda yangi pomidor-piyoz salati tayyorlaysiz. Soʻng hamma dasturxon atrofida oʻzingiz pishirgan oshni yangi non va koʻk choy bilan tatib koʻradi, "
                        "siz esa olib ketish uchun osh va bosma retsept kartasi bilan qaytasiz.",
                        "Плов — блюдо узбекских праздников, а его приготовление — ритуал. Местный повар (ошпаз) встретит вас на базаре Сиаб, где вы выберете рис, жёлтую морковь и баранину на глаз и по запаху. "
                        "На кухне вы нарежете, обжарите и выложите всё слоями в большом казане, узнаете секреты зирвака и пара, пока аромат наполняет двор. "
                        "Пока плов настаивается, вы приготовите свежий салат из помидоров и лука. Затем все садятся за дастархан и пробуют плов, который вы приготовили, со свежей лепёшкой и зелёным чаем, "
                        "а вы уходите с порцией на вынос и печатной карточкой рецепта."),
        highlights=[("Shop for ingredients at Siyob Bazaar with your cook", "Siyob bozorida oshpaz bilan masalliq xarid qiling", "Выберите продукты на базаре Сиаб вместе с поваром"),
                    ("Cook plov in a traditional kazan", "An'anaviy qozonda osh pishiring", "Приготовьте плов в традиционном казане"),
                    ("Learn the secrets of zirvak and steam", "Zirvak va dam berish sirlarini o'rganing", "Узнайте секреты зирвака и пара"),
                    TASTE_PLOV_HIGHLIGHT],
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
        slug="samarkand-plov-and-non-masterclass", title="Samarkand Non & Plov Experience", price=89, duration="5 hours", image="Tandir_nonlarini_ko‘rsatayotgan_novvoy.jpg",
        titles=tr("Samarqand noni va oshi tajribasi", "Самаркандская лепёшка и плов: гастро-опыт", "L'expérience du non et du plov de Samarcande", "Samarkander Non & Plov Erlebnis", "Experiencia de non y plov de Samarcanda"),
        guide="Local cook (oshpaz)", guides=tr("Mahalliy oshpaz", "Местный повар (ошпаз)"),
        summary="The whole Samarkand table in one morning: market, plov in a kazan and your own non from the tandir, tasted together at the dastarkhan, with treats to take home.",
        summaries=tr("Bir ertalabda butun Samarqand dasturxoni: bozor, qozonda osh va tandirdan oʻz noningiz — dasturxonda birga tatib koʻriladi, olib ketish uchun sovgʻalar bilan.",
                     "Весь самаркандский стол за одно утро: базар, плов в казане и собственная лепёшка из тандыра — всё пробуем вместе за дастарханом, с угощениями с собой."),
        description=("The whole Samarkand table in one morning. Start at Siyob Bazaar to shop with your cook, then cook plov in a kazan and, while it steams, "
                     "shape and bake your own non in the tandir. Sit down together at the dastarkhan to taste the plov and the hot bread you made, "
                     "and leave with a take-away portion of plov, your own loaf, a printed recipe card and a certificate of participation."),
        descriptions=tr("Bir ertalabda butun Samarqand dasturxoni. Siyob bozorida oshpaz bilan xarid qilishdan boshlaysiz, soʻng qozonda osh pishirasiz va u dam yeyotganda tandirda oʻz noningizni shakllab yopasiz. "
                        "Dasturxon atrofida birga oʻzingiz pishirgan oshni va issiq nonni tatib koʻrasiz, olib ketish uchun osh, oʻzingiz yopgan non, bosma retsept kartasi va ishtirok sertifikati bilan qaytasiz.",
                        "Весь самаркандский стол за одно утро. Начните на базаре Сиаб — сделайте покупки вместе с поваром, затем приготовьте плов в казане и, пока он томится, сформируйте и испеките собственную лепёшку в тандыре. "
                        "Сядьте вместе за дастархан и попробуйте приготовленный плов и горячий хлеб, а уходите с порцией плова на вынос, своей лепёшкой, печатной карточкой рецепта и сертификатом участника."),
        highlights=[("Shop for ingredients at Siyob Bazaar with your cook", "Siyob bozorida oshpaz bilan masalliq xarid qiling", "Выберите продукты на базаре Сиаб вместе с поваром"),
                    ("Cook plov in a traditional kazan", "An'anaviy qozonda osh pishiring", "Приготовьте плов в традиционном казане"),
                    ("Shape and stamp your own Samarkand non", "Oʻz Samarqand noningizni shakllang va naqsh bosing", "Сформируйте и украсьте узором собственную самаркандскую лепёшку"),
                    TASTE_PLOV_HIGHLIGHT],
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

# What the first version of these tours said, so an admin's own edits are never overwritten: a field is only replaced
# when it still holds the original text.
OLD = {
    "samarkand-non-baking-class": dict(
        title="Samarkand Non Bread Baking Class",
        summary="Knead, stamp and bake your own Samarkand non in a clay tandir with a local master baker, then take the warm bread home.",
        description=("Samarkand non is famous across Central Asia: a thick, round loaf stamped with a pattern and baked on the inner wall of a clay tandir. "
                     "In this hands-on class a local master baker shows you how to prepare the dough, shape and stamp the loaf with the traditional chekich, "
                     "and press it onto the hot oven wall. While it bakes you drink tea and hear how bread stands at the centre of Uzbek hospitality. "
                     "You eat a piece fresh from the oven and take your own bread home. No experience is needed; the class suits beginners and families."),
        highlights=["Knead, shape and stamp your own non", "Bake it on the wall of a real clay tandir", "Taste it hot, with tea", "Take your own bread home"],
        included=["Hotel pickup and drop-off", "Instruction by a local master baker", "All ingredients and an apron", "Tea and fresh bread", "Your own bread to take home"]),
    "samarkand-plov-masterclass": dict(
        title="Samarkand Plov Masterclass",
        summary="Shop at Siyob Bazaar, cook real Samarkand plov in a kazan with a local cook, eat it together and take a portion home.",
        description=("Plov is the dish of Uzbek celebrations, and cooking it is a ritual. Your local cook (oshpaz) meets you at Siyob Bazaar, where you choose the rice, "
                     "yellow carrots and lamb. In the kitchen you cut, fry and layer everything in a large kazan, learning the secrets of the zirvak and the timing of the steam. "
                     "While the plov rests you prepare a fresh tomato and onion salad. Everyone sits down to eat the plov you cooked, and you leave with a take-away portion and a printed recipe card."),
        highlights=["Shop for ingredients at Siyob Bazaar with your cook", "Cook plov in a traditional kazan", "Learn the secrets of zirvak and steam", "Eat what you cooked and take a portion home"],
        included=None),
    "samarkand-plov-and-non-masterclass": dict(
        title="Plov & Non Masterclass",
        summary="The full Samarkand food morning: market, plov in a kazan and your own non from the tandir, with a shared lunch and treats to take home.",
        description=("The full Samarkand food experience in one morning. Start at Siyob Bazaar to shop with your cook, then prepare plov in a kazan and, while it steams, "
                     "shape and bake your own non in the tandir. Sit down to a shared lunch of the plov and fresh bread, and leave with a take-away portion of plov, "
                     "your own loaf, a printed recipe card and a certificate of participation."),
        highlights=["Shop for ingredients at Siyob Bazaar with your cook", "Cook plov in a traditional kazan", "Knead, shape and stamp your own non", "Eat what you cooked and take a portion home"],
        included=None),
}
OLD_STEPS = {  # old step text -> the new step that replaces it
    "Meet the baker and learn the dough: flour, water, salt and patience": EXPERIENCES[0]["plan"][1],
    "Bake it on the wall of the tandir": EXPERIENCES[0]["plan"][3],
    "Taste your bread hot, with tea and jam": TASTE_NON,
}


def refresh_changes(tour, e):
    """Bring a tour created by the first version up to the new wording, field by field, only where it is still unedited."""
    old, changed = OLD[e["slug"]], []
    for field in ("title", "summary", "description"):
        if getattr(tour, field) == old[field] and old[field] != e[field]:
            setattr(tour, field, e[field])
            changed.append(field)
    for field, new in (("highlights", [h[0] for h in e["highlights"]]), ("included", [i[0] for i in e["included"]])):
        if old.get(field) is not None and getattr(tour, field) == old[field]:
            setattr(tour, field, new)
            changed.append(field)
    if tour.itinerary:
        swapped = False
        for day in tour.itinerary:
            for index, item in enumerate(day.get("items", [])):
                new = OLD_STEPS.get(item.get("text", "")) if item.get("type") == "step" else None
                if new and e["slug"] == "samarkand-non-baking-class":
                    day["items"][index] = new
                    swapped = True
        if swapped:
            changed.append("itinerary")
    return changed


TIMES = {"2 hours": tr("2 soat", "2 часа", "2 heures", "2 Stunden", "2 horas"),
         "4 hours": tr("4 soat", "4 часа", "4 heures", "4 Stunden", "4 horas"),
         "5 hours": tr("5 soat", "5 часов", "5 heures", "5 Stunden", "5 horas")}
SHARED = {
    "Tips (optional)": tr("Choyxo'rlik (ixtiyoriy)", "Чаевые (по желанию)", "Pourboires (facultatif)", "Trinkgeld (optional)", "Propinas (opcional)"),
    "Hands-on experience": tr("Amaliy tajriba", "Практический опыт", "Expérience pratique", "Mitmach-Erlebnis", "Experiencia práctica"),
}


def register_phrases():
    PHRASES.update(TIMES)
    PHRASES.update(SHARED)
    for e in EXPERIENCES:
        PHRASES[e["title"]] = e["titles"]
        PHRASES[e["guide"]] = e["guides"]
        PHRASES[e["summary"]] = e["summaries"]
        PHRASES[e["description"]] = e["descriptions"]
        PHRASES[e["story"]] = e["stories"]
        PHRASES[PICKUP[0]] = tr(PICKUP[1], PICKUP[2])
        for en, uz, ru in e["highlights"] + e["included"]:
            PHRASES.setdefault(en, tr(uz, ru))
        for item in e["plan"]:
            if item["type"] == "step":
                PHRASES.setdefault(item["text"], tr(item["i18n"]["uz"], item["i18n"]["ru"]))


register_phrases()
