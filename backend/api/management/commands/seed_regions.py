"""The other regions of Uzbekistan, built the same way as Samarkand: a regional tour with a day-by-day plan, plus one tour card
for each historical place with a factual note ("about") and a short keepsake text ("story").

Photos are hotlinked from Wikimedia Commons (Special:FilePath), picked to match each place; sources: Wikipedia and Wikimedia Commons.
Place texts are written in English, Uzbek and Russian; French, German and Spanish show the English text until an admin translates them.
Names, titles and the regional tour texts are translated into all six languages.

Every place is (slug, name, (uz, ru, fr, de, es names), fee USD, photo file, summary, about, story, uz texts, ru texts).
"""
from urllib.parse import quote

from api.management.commands.seed_translations import PHRASES

COMMONS = "https://commons.wikimedia.org/wiki/Special:FilePath/"


def photo(filename):
    return COMMONS + quote(filename, safe="(),") + "?width=1280"


def meal(time, kind, included=False):
    return {"time": time, "type": "meal", "meal": kind, "included": included}


def visit(time, stop):
    return {"time": time, "type": "visit", "stop": stop}


def drive(time, stop):
    return {"time": time, "type": "transfer", "stop": stop}


B = lambda t: meal(t, "breakfast", True)  # noqa: E731 - breakfast is part of the package
L = lambda t: meal(t, "lunch")  # noqa: E731
D = lambda t: meal(t, "dinner")  # noqa: E731

REGIONS = [
    dict(
        slug="bukhara", city_slug="bukhara-city-tour", name="Bukhara", names=("Buxoro", "Бухара", "Boukhara", "Buchara", "Bujará"),
        title="Bukhara City Tour", titles=("Buxoro shahar turi", "Обзорный тур по Бухаре", "Visite de la ville de Boukhara", "Stadtrundfahrt Buchara", "Tour por la ciudad de Bujará"),
        price=319, days=2, meeting="Bukhara airport", meetings=("Buxoro aeroporti", "Аэропорт Бухары", "Aéroport de Boukhara", "Flughafen Buchara", "Aeropuerto de Bujará"),
        image="bukhara",
        places=[
            ("ark-fortress", "Ark Fortress", ("Ark qal'asi", "Крепость Арк", "Forteresse Ark", "Ark-Festung", "Fortaleza Ark"), 8, "Ark_of_Bukhara_2023.9.jpg",
             "The mighty fortress and former home of the emirs of Bukhara, with museums inside its walls.",
             "The Ark is a fortress and a royal town within the town, with roots reaching back to around the 5th century. Most of its present buildings date from the last three centuries, when the emirs ruled from here. You walk up the ramp to the gate, see the reception court and visit small museums on the history of Bukhara.",
             "Behind walls the colour of sand, emirs once held court above the city. Walk up the old ramp and you climb into the pages of a chronicle written in clay and brick.",
             ("Qudratli qal'a va Buxoro amirlarining sobiq qarorgohi, devorlari ichida muzeylar bor.",
              "Ark — shahar ichidagi qirollik shaharchasi bo'lgan qal'a, ildizlari taxminan V asrga borib taqaladi. Hozirgi binolarning aksariyati amirlar shu yerdan turib hukmronlik qilgan so'nggi uch asrga tegishli. Darvozagacha qiya yo'ldan yurasiz, qabul hovlisini ko'rasiz va Buxoro tarixiga bag'ishlangan kichik muzeylarga kirasiz.",
              "Qum rangidagi devorlar ortida amirlar bir paytlar shahar ustidan hukm yuritgan. Qadimiy qiya yo'ldan ko'tarilsangiz, loy va g'ishtda yozilgan yilnomaning sahifalariga kirib borasiz."),
             ("Мощная крепость и бывшая резиденция бухарских эмиров, внутри которой работают музеи.",
              "Арк — крепость и царский городок внутри города, история которого уходит примерно к V веку. Большинство нынешних построек относится к последним трём векам, когда отсюда правили эмиры. Вы поднимаетесь по пандусу к воротам, осматриваете приёмный двор и небольшие музеи по истории Бухары.",
              "За стенами цвета песка эмиры когда-то вершили суд над городом. Поднимитесь по старому пандусу — и вы войдёте в страницы летописи, написанной глиной и кирпичом.")),
            ("poi-kalon-complex", "Poi Kalon Complex", ("Poyi Kalon majmuasi", "Ансамбль Пои-Калян", "Ensemble Poï Kalon", "Poi-Kalon-Ensemble", "Conjunto Poi Kalon"), 10, "Kalyan_Minaret,_Bukhara_(Минарет_Калян_в_Бухаре,_Minorai_Kalon).jpg",
             "The Kalyan Minaret, the Kalon Mosque and the Mir-i-Arab Madrasah around Bukhara's central square.",
             "Poi Kalon means “foot of the great”. The Kalyan Minaret, built in 1127 and about 46 metres tall, has been the city's landmark for nearly nine centuries; legend says even Genghis Khan spared it. Beside it stand the large Kalon Mosque (1514) and the Mir-i-Arab Madrasah (1530s), still a working religious school.",
             "At dusk the great minaret turns the colour of honey and the whole square holds its breath. Stand where caravans once stopped and look up: some towers are built to be remembered.",
             ("Buxoro markaziy maydonidagi Kalon minorasi, Kalon masjidi va Mir Arab madrasasi.",
              "Poyi Kalon — «buyuklar etagi» degani. 1127-yilda qurilgan, balandligi taxminan 46 metr bo'lgan Kalon minorasi to'qqiz asrga yaqin shaharning timsoli; rivoyatga ko'ra, hatto Chingizxon ham uni omon qoldirgan. Yonida katta Kalon masjidi (1514) va hozir ham faol diniy maktab bo'lgan Mir Arab madrasasi (1530-yillar) turadi.",
              "Kechqurun buyuk minora asal rangiga kiradi, butun maydon nafasini ushlaydi. Karvonlar to'xtagan joyda turib tepaga qarang: ba'zi minoralar eslab qolinish uchun quriladi."),
             ("Минарет Калян, мечеть Калян и медресе Мири-Араб вокруг главной площади Бухары.",
              "Пои-Калян значит «подножие великого». Минарет Калян, построенный в 1127 году и достигающий примерно 46 метров, почти девять веков остаётся символом города; по легенде, даже Чингисхан пощадил его. Рядом стоят большая мечеть Калян (1514) и медресе Мири-Араб (1530-е годы), которое и сегодня действующее религиозное училище.",
              "В сумерках великий минарет становится цвета мёда, и вся площадь затаивает дыхание. Встаньте там, где останавливались караваны, и посмотрите вверх: некоторые башни строятся, чтобы их помнили.")),
            ("lyabi-hauz", "Lyabi-Hauz", ("Labi Hovuz", "Ляби-Хауз", "Lyabi-Haouz", "Labi-Haus", "Lyabi-Hauz"), 2, "Nadir_Divan-Beghi_Madrassah.JPG",
             "The shaded pool at the heart of old Bukhara, ringed by madrasahs, tea houses and mulberry trees.",
             "Lyabi-Hauz means “by the pool”. The pond was dug in 1620 and is one of the few that survive from the many that once cooled the city. It is framed by the Nadir Divan-Beghi Madrasah and Khanaka and the Kukeldash Madrasah, with a statue of the wise trickster Nasreddin Hoja at one side. The best way to enjoy it is with tea under the old mulberries.",
             "Evening settles on the water, lanterns come on, and Bukhara slows down to the speed of a cup of tea. Sit, listen and let the old city tell its stories.",
             ("Qadimiy Buxoro qalbidagi soyali hovuz; atrofida madrasalar, choyxonalar va tut daraxtlari.",
              "Labi Hovuz — «hovuz bo'yi» degani. Hovuz 1620-yilda qazilgan va shaharni bir paytlar salqinlatgan ko'plab hovuzlardan omon qolgan kam sonlilaridan biri. Uni Nodir Devonbegi madrasasi va xonaqosi hamda Ko'kaldosh madrasasi o'rab turadi, bir chetda dono hazilkash Nasriddin Xo'ja haykali bor. Eng yaxshisi — qadimiy tutlar soyasida choy ichib o'tirish.",
              "Suv ustiga oqshom tushadi, fonuslar yonadi, Buxoro esa bir piyola choy tezligida sekinlashadi. O'tiring, tinglang va qadimiy shahar o'z hikoyalarini aytib bersin."),
             ("Тенистый пруд в сердце старой Бухары в окружении медресе, чайхан и тутовых деревьев.",
              "Ляби-Хауз означает «у водоёма». Пруд выкопан в 1620 году и остаётся одним из немногих, переживших множество водоёмов, которые когда-то охлаждали город. Его обрамляют медресе и ханака Надир Диван-беги и медресе Кукельдаш, а сбоку стоит памятник мудрому шутнику Насреддину Ходже. Лучший способ насладиться местом — чай под старыми тутами.",
              "На воду ложится вечер, зажигаются фонари, и Бухара замедляется до скорости чашки чая. Присядьте, послушайте — и пусть старый город расскажет свои истории.")),
            ("chor-minor", "Chor Minor", ("Chor Minor", "Чор-Минор", "Tchor Minor", "Chor Minor", "Chor Minor"), 3, "Chor_Minor_mosque_(Чор-Минор,_Бухара).jpg",
             "A charming gatehouse with four blue-domed towers, one of Bukhara's most photographed little buildings.",
             "Chor Minor means “four minarets”. Built in 1807 by a wealthy Bukharan merchant, Khalif Niyaz-kul, it is the gatehouse of a madrasah that no longer exists. Each of its four towers is different, and visitors have long read symbols into them, from four religions to four seasons.",
             "Four little towers, four different hats of blue: Chor Minor is the whimsical side of Bukhara. It asks for no more than a smile and a photograph.",
             ("To'rt ko'k gumbazli minorasi bor ajoyib darvozaxona, Buxoroning eng ko'p suratga olinadigan kichik binolaridan biri.",
              "Chor Minor — «to'rt minora» degani. 1807-yilda boy buxorolik savdogar Xalifa Niyozqul qurgan, u endi mavjud bo'lmagan madrasaning darvozaxonasidir. To'rt minoraning har biri o'zgacha, sayyohlar ularda to'rt din yoki to'rt fasl kabi ramzlarni qidirib kelgan.",
              "To'rt kichkina minora, ko'k rangdagi to'rt xil bosh kiyim: Chor Minor — Buxoroning hazilkash yuzi. Undan faqat tabassum va bitta surat kerak."),
             ("Очаровательный портал с четырьмя башенками под синими куполами — одно из самых фотографируемых зданий Бухары.",
              "Чор-Минор означает «четыре минарета». Построен в 1807 году богатым бухарским купцом Халифой Ниязкулом как портал медресе, которого уже нет. Каждая из четырёх башен отличается от других, и путешественники издавна видели в них символы — от четырёх религий до четырёх времён года.",
              "Четыре башенки — четыре разных синих головных убора: Чор-Минор — это шутливое лицо Бухары. От вас нужны лишь улыбка и один снимок.")),
            ("ismail-samani-mausoleum", "Ismail Samani Mausoleum", ("Ismoil Somoniy maqbarasi", "Мавзолей Исмаила Самани", "Mausolée d'Ismaïl Samani", "Ismail-Samani-Mausoleum", "Mausoleo de Ismail Samani"), 6, "Samanid_Mausoleum,_Bukhara.jpg",
             "A tenth-century brick tomb of the Samanid dynasty, a masterpiece of early Central Asian architecture.",
             "Built in the 9th–10th centuries for Ismail Samani, founder of the Samanid dynasty, this small cube topped by a dome is among the oldest surviving Islamic monuments in Central Asia. Its walls are woven from baked brick in dozens of patterns that seem to change with the light. It survived the centuries partly because it was buried under silt before being rediscovered.",
             "A thousand years old and woven from plain brick, it looks like fine lace in stone. Stand close and watch the patterns move with the sun.",
             ("X asrga oid Somoniylar sulolasi g'isht maqbarasi, Markaziy Osiyo qadimgi me'morchiligining durdonasi.",
              "Somoniylar sulolasi asoschisi Ismoil Somoniy uchun IX–X asrlarda qurilgan, ustida gumbazi bor bu kichik kub Markaziy Osiyodagi eng qadimgi islom yodgorliklaridan biridir. Devorlari pishgan g'ishtdan o'nlab naqshlarda to'qilgan va yorug'likka qarab o'zgargandek tuyuladi. Uning asrlar osha saqlanib qolishiga qisman loyqa ostida qolgani sabab bo'lgan.",
              "Ming yillik va oddiy g'ishtdan to'qilgan bu maqbara toshdagi nafis dantelaga o'xshaydi. Yaqin turib, naqshlar quyosh bilan qanday harakatlanishini kuzating."),
             ("Кирпичная усыпальница династии Саманидов X века, шедевр раннесредневековой архитектуры Центральной Азии.",
              "Построенный в IX–X веках для Исмаила Самани, основателя династии Саманидов, небольшой куб с куполом — один из древнейших сохранившихся исламских памятников Центральной Азии. Стены выложены обожжённым кирпичом в десятках узоров, которые будто меняются вместе со светом. Уцелеть ему помогло и то, что одно время он был скрыт под наносами ила.",
              "Тысячелетний и сплетённый из простого кирпича, он похож на тонкое каменное кружево. Подойдите ближе и посмотрите, как узоры движутся вслед за солнцем.")),
        ],
        plan=[
            [B("08:00"), visit("09:00", 4), visit("10:30", 0), L("13:00"), visit("14:30", 1), visit("16:30", 2), D("18:30")],
            [B("08:00"), visit("09:30", 3), L("13:00"), D("18:00")],
        ],
    ),
    dict(
        slug="khorezm", city_slug="khorezm-khiva-tour", name="Khorezm", names=("Xorazm", "Хорезм", "Khorezm", "Choresm", "Corasmia"),
        title="Khiva & Khorezm Tour", titles=("Xiva va Xorazm turi", "Тур по Хиве и Хорезму", "Circuit Khiva et Khorezm", "Tour Chiwa & Choresm", "Tour por Jiva y Corasmia"),
        price=339, days=2, meeting="Urgench airport", meetings=("Urganch aeroporti", "Аэропорт Ургенча", "Aéroport d'Ourguentch", "Flughafen Urgentsch", "Aeropuerto de Urgench"),
        image="khiva",
        places=[
            ("itchan-kala", "Itchan Kala", ("Ichan-Qal'a", "Ичан-Кала", "Itchan Kala", "Itschan Kala", "Itchan Kala"), 18, "Islam_Khodja_Madrasa_01.jpg",
             "The perfectly preserved walled inner town of Khiva, a UNESCO World Heritage Site.",
             "Itchan Kala is the walled inner town of Khiva and in 1990 became the first site in Uzbekistan on the UNESCO World Heritage List. It keeps more than 50 historic monuments and some 250 old houses, mostly from the 18th and 19th centuries, within sand-coloured walls. Climb the Islam Khoja Minaret (1910), the tallest in the country, for a view across the roofs.",
             "Inside the clay walls time moves as slowly as a camel at dusk. Every gate and tiled dome is a doorway into a Khiva that still believes in caravans.",
             ("Xivaning devor bilan o'ralgan, mukammal saqlangan ichki shahri, YuNESKO Butunjahon merosi ob'ekti.",
              "Ichan-Qal'a — Xivaning devor bilan o'ralgan ichki shahri bo'lib, 1990-yilda O'zbekistonda YuNESKO Butunjahon merosi ro'yxatiga kirgan birinchi ob'ekt bo'ldi. Qum rangidagi devorlar ichida 50 dan ortiq tarixiy yodgorlik va, asosan XVIII–XIX asrlarga oid, 250 ga yaqin eski uy saqlanib qolgan. Mamlakatdagi eng baland Islom Xo'ja minorasiga (1910) chiqib, tomlar uzra manzarani tomosha qiling.",
              "Loy devorlar ichida vaqt shom paytidagi tuyadek sekin yuradi. Har bir darvoza va koshinli gumbaz hamon karvonlarga ishonadigan Xivaga eshik ochadi."),
             ("Идеально сохранившийся внутренний город Хивы за крепостными стенами, объект Всемирного наследия ЮНЕСКО.",
              "Ичан-Кала — внутренний город Хивы за стенами; в 1990 году он стал первым объектом Узбекистана в списке Всемирного наследия ЮНЕСКО. Здесь сохранилось более 50 исторических памятников и около 250 старых домов, в основном XVIII–XIX веков, в стенах песочного цвета. Поднимитесь на минарет Ислам-Ходжа (1910) — самый высокий в стране, — чтобы увидеть город с высоты.",
              "За глиняными стенами время движется медленно, как верблюд на закате. Каждые ворота и каждый облицованный купол — дверь в Хиву, которая всё ещё верит в караваны.")),
            ("kalta-minor-minaret", "Kalta Minor Minaret", ("Kalta Minor minorasi", "Минарет Кальта-Минор", "Minaret Kalta Minor", "Kalta-Minor-Minarett", "Minarete Kalta Minor"), 4, "Kalta_Minor_01.jpg",
             "The unfinished turquoise minaret that became the symbol of Khiva.",
             "Khan Muhammad Amin began the Kalta Minor (“short minaret”) in 1852 and meant it to be the tallest in the Islamic world. Work stopped when he died in 1855, leaving a fat tower of about 26 metres covered in green and turquoise glazed tile. Its unfinished form is what makes it so beloved.",
             "A tower that never reached the sky became the heart of a city. Some dreams are more beautiful unfinished.",
             ("Xivaning ramziga aylangan, tugallanmagan firuza rangli minora.",
              "Muhammad Amin xon Kalta Minorni («kalta minora») 1852-yilda boshlagan va uni islom olamidagi eng baland minora qilishni niyat qilgan. 1855-yilda xon vafot etgach, ish to'xtab, yashil va firuza sirli koshin bilan qoplangan, taxminan 26 metrli yo'g'on minora qolgan. Uni aziz qiladigan narsa aynan tugallanmagan shaklidir.",
              "Osmonga yetmagan minora shaharning qalbiga aylandi. Ba'zi orzular tugallanmagan holida go'zalroq."),
             ("Недостроенный бирюзовый минарет, ставший символом Хивы.",
              "Хан Мухаммад Амин начал строить Кальта-Минор («короткий минарет») в 1852 году, намереваясь сделать его самым высоким в исламском мире. Работы прекратились со смертью хана в 1855 году, оставив толстую башню около 26 метров, покрытую зелёной и бирюзовой глазурованной плиткой. Именно незавершённость и сделала её такой любимой.",
              "Башня, не достигшая неба, стала сердцем города. Некоторые мечты прекраснее незавершёнными.")),
            ("juma-mosque-khiva", "Juma Mosque", ("Juma masjidi", "Мечеть Джума", "Mosquée Djouma", "Juma-Moschee", "Mezquita Juma"), 5, "Juma_Mosque_20140927_Uzbekistan_0284_Khiva_(15638472913).jpg",
             "A forest of carved wooden columns holds up the roof of Khiva's Friday mosque.",
             "The Juma (“Friday”) Mosque dates back to the 10th century, though what stands today was rebuilt in the late 18th century. Instead of a courtyard it has a hall with more than 200 carved wooden columns, some of them centuries old, that hold up the flat roof. Light falls through small openings in the ceiling and makes the hall feel like a quiet grove.",
             "Step among two hundred carved trees without a leaf. In the soft light of the roof, the old wood still seems to remember the hands that shaped it.",
             ("Xivaning juma masjidi tomini o'ymakor yog'och ustunlar o'rmoni ushlab turadi.",
              "Juma masjidi X asrga borib taqaladi, ammo hozirgi bino XVIII asr oxirida qayta qurilgan. Hovli o'rniga uning 200 dan ortiq o'ymakor yog'och ustunli zali bor, ustunlarning ba'zilari asrlik bo'lib, tekis tomni ko'tarib turadi. Shift teshiklaridan tushayotgan yorug'lik zalni sokin bog'ga o'xshatadi.",
              "Bargsiz ikki yuz o'yma daraxt orasida yuring. Shiftdan tushgan mayin nurda eski yog'och hamon o'ziga shakl bergan qo'llarni eslayotganga o'xshaydi."),
             ("Лес резных деревянных колонн держит крышу пятничной мечети Хивы.",
              "Мечеть Джума («Пятничная») восходит к X веку, хотя нынешнее здание перестроено в конце XVIII века. Вместо двора здесь зал с более чем 200 резными деревянными колоннами, часть которых насчитывает века и поддерживает плоскую крышу. Свет проникает через небольшие отверстия в потолке, и зал напоминает тихую рощу.",
              "Пройдите между двумя сотнями резных деревьев без листвы. В мягком свете потолка старое дерево словно помнит руки, придавшие ему форму.")),
            ("tash-hauli-palace", "Tash Hauli Palace", ("Tosh Hovli saroyi", "Дворец Таш-Хаули", "Palais Tach Haouli", "Tasch-Hauli-Palast", "Palacio Tash Hauli"), 8, "Tash_Hauli_Palace,_Khiva_(481376).jpg",
             "The khan's “Stone House”, a palace of tiled courtyards and carved wooden columns.",
             "Tash Hauli (“Stone House”) was built for Allah Kuli Khan in the 1830s as a more comfortable home than the old fortress. Its courtyards, one for the harem, one for receptions and one for the khan's court, are decorated with blue-and-white majolica tiles and deep-carved wooden columns on stone bases. It is one of the finest surviving examples of Khorezm decorative art.",
             "Blue tiles climb the walls like a slow wave and carved columns hold up a painted sky. This is where a khan lived, and where you may linger as a guest.",
             ("Xonning «Tosh Hovli»si — koshinli hovlilar va o'ymakor yog'och ustunlar saroyi.",
              "Tosh Hovli («tosh uy») Olloqulixon uchun 1830-yillarda eski qal'adan qulayroq turar joy sifatida qurilgan. Biri harami, biri qabul va yana biri xon devoni uchun mo'ljallangan hovlilari ko'k-oq maiolika koshinlar hamda tosh poydevorlardagi chuqur o'yilgan yog'och ustunlar bilan bezatilgan. Bu Xorazm bezak san'atining saqlanib qolgan eng go'zal namunalaridan biridir.",
              "Ko'k koshinlar sekin to'lqin kabi devorlarga ko'tariladi, o'yma ustunlar naqshli osmonni ushlab turadi. Xon shu yerda yashagan, siz esa mehmon sifatida to'xtab turishingiz mumkin."),
             ("«Каменный дом» хана — дворец с облицованными дворами и резными деревянными колоннами.",
              "Таш-Хаули («Каменный дом») построен для Аллакули-хана в 1830-х годах как более удобное жильё, чем старая крепость. Его дворы — для гарема, для приёмов и для ханского двора — украшены сине-белой майоликой и глубоко резными деревянными колоннами на каменных базах. Это один из лучших сохранившихся образцов хорезмского декоративного искусства.",
              "Синяя плитка поднимается по стенам, как медленная волна, а резные колонны держат расписное небо. Здесь жил хан, а вы можете задержаться как гость.")),
        ],
        plan=[
            [B("08:00"), visit("09:00", 0), visit("10:30", 1), L("13:00"), D("18:30")],
            [B("08:00"), visit("09:30", 2), visit("11:00", 3), L("13:00"), D("18:00")],
        ],
    ),
    dict(
        slug="kashkadarya", city_slug="kashkadarya-shahrisabz-tour", name="Kashkadarya", names=("Qashqadaryo", "Кашкадарья", "Kachkadaria", "Kaschkadarja", "Kashkadarya"),
        title="Shahrisabz & Kashkadarya Tour", titles=("Shahrisabz va Qashqadaryo turi", "Тур по Шахрисабзу и Кашкадарье", "Circuit Chakhrisabz et Kachkadaria", "Tour Schachrisabs & Kaschkadarja", "Tour por Shahrisabz y Kashkadarya"),
        price=229, days=1, meeting="Your hotel in Samarkand", meetings=("Samarqanddagi mehmonxonangiz", "Ваш отель в Самарканде", "Votre hôtel à Samarcande", "Ihr Hotel in Samarkand", "Su hotel en Samarcanda"),
        image="shahrisabz",
        places=[
            ("ak-saray-palace", "Ak-Saray Palace", ("Oqsaroy", "Дворец Ак-Сарай", "Palais Ak-Saray", "Ak-Saray-Palast", "Palacio Ak-Saray"), 8, "Ak_Serai_Palace,_Shakhrisabz_(490496).jpg",
             "The colossal gate towers of the summer palace that Timur began to build in his home town.",
             "Timur began Ak-Saray (“White Palace”) in 1380 and it was still unfinished when he died in 1405. Only parts of two gate towers survive, still about 38 metres high, with traces of blue, white and gold tile. An inscription said to have been over the entrance read “If you doubt our power, look at our buildings”.",
             "Two great pillars of brick stand against the sky, and even half a palace is enough to take your breath away. The man who built it wanted the world to look up.",
             ("Temur o'z vatanida qurishni boshlagan yozgi saroyning ulkan darvoza minoralari.",
              "Temur Oqsaroyni («Oq saroy») 1380-yilda boshlagan va u 1405-yilda vafot etganda saroy hali tugallanmagan edi. Hozir ikki darvoza minorasining bir qismigina saqlangan, balandligi hamon taxminan 38 metr, ko'k, oq va tilla rangli koshin izlari bor. Kirish tepasidagi bitikda «Qudratimizga shubha qilsangiz, binolarimizga boqing» deyilgani aytiladi.",
              "Osmon bag'rida ikkita g'isht ustun turibdi, yarim saroyning o'zi ham nafasingizni qaytaradi. Uni qurgan kishi dunyo tepaga qarashini istagan."),
             ("Колоссальные башни портала летнего дворца, который Тимур начал строить в родном городе.",
              "Тимур начал строить Ак-Сарай («Белый дворец») в 1380 году, и ко дню его смерти в 1405 году дворец остался недостроенным. Сохранились лишь части двух башен портала высотой около 38 метров со следами синей, белой и золотой плитки. Надпись над входом, по преданию, гласила: «Если сомневаешься в нашей мощи — взгляни на наши постройки».",
              "Два огромных кирпичных столпа стоят на фоне неба, и даже половины дворца достаточно, чтобы захватило дух. Тот, кто его строил, хотел, чтобы мир смотрел вверх.")),
            ("amir-timur-birthplace-shahrisabz", "Amir Timur Birthplace", ("Amir Temur tug'ilgan joy", "Родина Амира Темура", "Lieu de naissance d'Amir Timour", "Geburtsort von Amir Timur", "Lugar de nacimiento de Amir Timur"), 3, "Amir_Temur_5.jpg",
             "Shahrisabz, the birthplace of Amir Timur, with a monument to the great ruler in the old centre.",
             "Timur was born in 1336 near Kesh, today's Shahrisabz, and the town stayed close to his heart all his life. A large monument to him stands in the old centre near the ruins of Ak-Saray. Walking the streets and the park, you see why he chose to build here, in a green valley beneath the mountains.",
             "Every great story starts in some small place. Here, among apricot trees and mountain light, a boy was born who would later reshape the map of Asia.",
             ("Shahrisabz — Amir Temur tug'ilgan shahar, eski markazda buyuk hukmdorga o'rnatilgan yodgorlik bor.",
              "Temur 1336-yilda Kesh, ya'ni hozirgi Shahrisabz yaqinida tug'ilgan va shahar umri davomida uning qalbiga yaqin bo'lib qoldi. Eski markazda, Oqsaroy xarobalari yaqinida unga qo'yilgan katta haykal turadi. Ko'chalar va bog' bo'ylab yurib, nega u aynan tog'lar etagidagi yam-yashil vodiyda qurishni tanlaganini tushunasiz.",
              "Har bir buyuk hikoya kichik joydan boshlanadi. Mana shu yerda, o'rik daraxtlari va tog' nuri orasida Osiyo xaritasini o'zgartiradigan bola tug'ilgan."),
             ("Шахрисабз — родина Амира Темура; в старом центре стоит памятник великому правителю.",
              "Тимур родился в 1336 году близ Кеша, нынешнего Шахрисабза, и город остался близок его сердцу на всю жизнь. В старом центре, возле руин Ак-Сарая, стоит большой памятник ему. Гуляя по улицам и парку, вы понимаете, почему он выбрал строить именно здесь, в зелёной долине у подножия гор.",
              "Каждая великая история начинается в каком-нибудь небольшом месте. Здесь, среди абрикосовых деревьев и горного света, родился мальчик, который позже изменил карту Азии.")),
            ("dorut-tilovat-complex", "Dorut Tilovat Complex", ("Dorut Tilovat majmuasi", "Комплекс Дорут-Тиловат", "Complexe Dorut Tilovat", "Dorut-Tilovat-Komplex", "Complejo Dorut Tilovat"), 6, "Dorut_Tilovat_1.jpg",
             "A calm ensemble of the Kok-Gumbaz mosque and family mausoleums of Timur's dynasty.",
             "Dorut Tilovat (“place of reading”) is a memorial ensemble that includes the blue-domed Kok-Gumbaz Mosque, built by Ulugh Beg in 1435–1436 in memory of his father Shah Rukh, and the Gumbazi Seyidan mausoleum. Beside it, the Dorus-Saodat crypt was prepared by Timur for his family. It is one of the quietest and most graceful corners of Shahrisabz.",
             "Under a dome the blue of a summer sky, the dynasty rests in silence. Pause here and you will feel how architecture can teach calm.",
             ("Ko'k Gumbaz masjidi va Temuriylar sulolasi oilaviy maqbaralaridan iborat sokin majmua.",
              "Dorut Tilovat («qiroat joyi») — Ulug'bek otasi Shohruh xotirasiga 1435–1436-yillarda qurdirgan ko'k gumbazli Ko'k Gumbaz masjidi va Gumbazi Sayyidon maqbarasini o'z ichiga olgan yodgorlik majmuasi. Yonida Temur oilasi uchun tayyorlatgan Dorus-Saodat dahmasi bor. Bu Shahrisabzning eng sokin va nafis burchaklaridan biri.",
              "Yoz osmoni rangidagi gumbaz ostida sulola sukunatda orom oladi. Shu yerda to'xtasangiz, me'morchilik xotirjamlikka o'rgata olishini his qilasiz."),
             ("Спокойный ансамбль мечети Кок-Гумбаз и семейных мавзолеев династии Тимура.",
              "Дорут-Тиловат («место чтения») — мемориальный ансамбль, в который входят мечеть Кок-Гумбаз с синим куполом, построенная Улугбеком в 1435–1436 годах в память об отце Шахрухе, и мавзолей Гумбази Сеидан. Рядом находится усыпальница Дорус-Саодат, которую Тимур приготовил для своей семьи. Это один из самых тихих и изящных уголков Шахрисабза.",
              "Под куполом цвета летнего неба в тишине покоится династия. Остановитесь здесь — и почувствуете, как архитектура учит спокойствию.")),
        ],
        plan=[
            [B("07:30"), drive("08:00", 0), visit("10:00", 0), visit("11:30", 1), L("13:00"), visit("14:30", 2), D("18:30")],
        ],
    ),
    dict(
        slug="tashkent", city_slug="tashkent-city-tour", name="Tashkent", names=("Toshkent", "Ташкент", "Tachkent", "Taschkent", "Taskent"),
        title="Tashkent City Tour", titles=("Toshkent shahar turi", "Обзорный тур по Ташкенту", "Visite de la ville de Tachkent", "Stadtrundfahrt Taschkent", "Tour por la ciudad de Taskent"),
        price=329, days=2, meeting="Tashkent airport", meetings=("Toshkent aeroporti", "Аэропорт Ташкента", "Aéroport de Tachkent", "Flughafen Taschkent", "Aeropuerto de Taskent"),
        image="tashkent",
        places=[
            ("khast-imam-complex", "Khast-Imam Complex", ("Hazrati Imom majmuasi", "Комплекс Хазрати Имам", "Complexe Khast-Imam", "Chast-Imam-Komplex", "Complejo Jast-Imam"), 5, "Hazrat_Imam_01.jpg",
             "The religious heart of Tashkent: madrasahs, mosques and the library with the ancient Uthman Quran.",
             "Khast-Imam grew around the tomb of Kaffal Shashi, a scholar and imam of the 10th century. Today the square holds the 16th-century Barak-Khan Madrasah, the Tilla Sheikh Mosque and the Muyi Muborak library, where an early copy of the Quran known as the Uthman Quran is kept. It is a peaceful place for a first taste of Uzbek Islamic architecture.",
             "Turquoise domes, tall arches and the soft murmur of a quiet square: here Tashkent turns from a modern capital into an old city of prayer.",
             ("Toshkentning ma'naviy markazi: madrasalar, masjidlar va qadimiy Usmon Qur'oni saqlanadigan kutubxona.",
              "Hazrati Imom X asrning olimi va imomi Qaffol Shoshiy qabri atrofida shakllangan. Bugun maydonda XVI asrdagi Barakxon madrasasi, Tillashayx masjidi va qadimiy Usmon Qur'oni nusxasi saqlanadigan Muyi Muborak kutubxonasi joylashgan. O'zbek islom me'morchiligi bilan tanishishni boshlash uchun sokin joy.",
              "Firuza gumbazlar, baland ravoqlar va sokin maydonning mayin shivirlashi: shu yerda Toshkent zamonaviy poytaxtdan qadimiy ibodat shahriga aylanadi."),
             ("Духовное сердце Ташкента: медресе, мечети и библиотека с древним Кораном Усмана.",
              "Хазрати Имам вырос вокруг могилы Каффаля Шаши — учёного и имама X века. Сегодня на площади находятся медресе Барак-хана XVI века, мечеть Тилла-Шейх и библиотека Муйи Муборак, где хранится древний список Корана, известный как Коран Усмана. Это спокойное место, чтобы впервые познакомиться с узбекской исламской архитектурой.",
              "Бирюзовые купола, высокие арки и тихий шёпот площади: здесь Ташкент из современной столицы превращается в древний город молитвы.")),
            ("chorsu-bazaar", "Chorsu Bazaar", ("Chorsu bozori", "Базар Чорсу", "Bazar Chorsou", "Tschorsu-Basar", "Bazar Chorsú"), 0, "Chorsu_Market_general_view.jpg",
             "Tashkent's great domed market of spices, bread, dried fruit and everything in between.",
             "Chorsu means “crossroads”, and the bazaar has stood at the heart of the old town for centuries. Beneath its big blue dome you find mountains of spices, nuts, sweets and round non bread, while stalls around it sell everything from meat to hand-made knives. It is the best place to taste before you buy.",
             "Under the blue dome the colours spill over: saffron, pomegranate, apricot. Take a piece of warm bread and let the city offer you the rest.",
             ("Toshkentning ziravorlar, non, quritilgan mevalar va boshqa ko'p narsalar sotiladigan ulkan gumbazli bozori.",
              "Chorsu — «chorraha» degani, bozor asrlar davomida eski shahar qalbida turibdi. Katta ko'k gumbaz ostida ziravorlar, yong'oq, shirinliklar va yumaloq non tog'lari, atrofdagi rastalarda esa go'shtdan tortib qo'lda yasalgan pichoqlargacha hamma narsa sotiladi. Sotib olishdan oldin tatib ko'rish uchun eng yaxshi joy.",
              "Ko'k gumbaz ostida ranglar to'kilib ketadi: za'faron, anor, o'rik. Issiq non bo'lagini oling, qolganini shaharning o'zi taklif qiladi."),
             ("Огромный купольный рынок Ташкента: специи, лепёшки, сухофрукты и многое другое.",
              "Чорсу значит «перекрёсток», и базар стоит в сердце старого города веками. Под большим синим куполом высятся горы специй, орехов, сладостей и круглых лепёшек, а вокруг торгуют всем — от мяса до ножей ручной работы. Лучшее место, чтобы попробовать, прежде чем купить.",
              "Под синим куполом краски выплёскиваются через край: шафран, гранат, абрикос. Возьмите кусок тёплого хлеба — остальное город предложит сам.")),
            ("amir-timur-square", "Amir Timur Square", ("Amir Temur xiyoboni", "Сквер Амира Темура", "Place Amir Timour", "Amir-Timur-Platz", "Plaza de Amir Timur"), 0, "Amir-Timur-Platz_vom_Hotel_Usbekistan_in_Richtung_Westen.jpg",
             "Tashkent's main square, with the equestrian statue of Amir Timur and the Tashkent Chimes clock tower.",
             "The square lies at the heart of modern Tashkent. Its centrepiece is a bronze equestrian statue of Amir Timur, placed there in 1993 after Uzbekistan's independence. Nearby are the Hotel Uzbekistan, the Tashkent Chimes clock tower and a park of fountains, a pleasant place for an evening walk.",
             "At sunset the old conqueror on his horse seems to look over the whole city. Walk the paths slowly: a young country is writing its story here.",
             ("Toshkentning asosiy maydoni; Amir Temur otliq haykali va «Toshkent kurantlari» soat minorasi shu yerda.",
              "Maydon zamonaviy Toshkent markazida joylashgan. Uning bosh bezagi — O'zbekiston mustaqilligidan so'ng, 1993-yilda o'rnatilgan Amir Temurning otliq bronza haykali. Yaqinda «O'zbekiston» mehmonxonasi, «Toshkent kurantlari» soat minorasi va favvoralar bog'i bor, oqshom sayri uchun yoqimli joy.",
              "Quyosh botayotganda ot ustidagi qadimiy fotih butun shaharga boqayotgandek tuyuladi. Yo'lakchalarda sekin yuring: yosh davlat bu yerda o'z hikoyasini yozmoqda."),
             ("Главная площадь Ташкента с конной статуей Амира Темура и часовой башней «Ташкентские куранты».",
              "Площадь расположена в сердце современного Ташкента. Её главное украшение — бронзовая конная статуя Амира Темура, установленная в 1993 году после обретения Узбекистаном независимости. Рядом находятся гостиница «Узбекистан», часовая башня «Ташкентские куранты» и парк с фонтанами — приятное место для вечерней прогулки.",
              "На закате старый завоеватель на коне будто смотрит на весь город. Идите по дорожкам не спеша: молодая страна пишет здесь свою историю.")),
            ("tashkent-metro", "Tashkent Metro", ("Toshkent metrosi", "Ташкентский метрополитен", "Métro de Tachkent", "Taschkenter Metro", "Metro de Taskent"), 1, "81-717-714_8630_train_at_Chinor_station.jpg",
             "A ride through the metro's palace-like stations, each decorated around its own theme.",
             "The Tashkent Metro opened in 1977 as the first in Central Asia. Its stations are designed around themes, with marble, chandeliers, mosaics and carved ornament, so a short ride is also a small art tour. Stations such as Kosmonavtlar, Alisher Navoi and Mustaqillik Maydoni are favourites of visitors.",
             "Underground, the city keeps a gallery open to everyone for the price of a ticket. Ride a few stops and see the capital's imagination shining under the ground.",
             ("Metroning saroyga o'xshash bekatlari bo'ylab sayr, har biri o'z mavzusida bezatilgan.",
              "Toshkent metrosi 1977-yilda Markaziy Osiyoda birinchi bo'lib ochilgan. Bekatlari mavzular asosida qurilgan, marmar, qandillar, mozaika va o'ymakor naqshlar bilan bezatilgan, shuning uchun qisqa safar ham kichik san'at sayohatiga aylanadi. «Kosmonavtlar», «Alisher Navoiy» va «Mustaqillik maydoni» kabi bekatlar mehmonlar sevimlisi.",
              "Yer ostida shahar bir chipta narxiga hamma uchun ochiq galereyani saqlaydi. Bir necha bekat yuring va poytaxt tasavvurining yer ostida porlashini ko'ring."),
             ("Поездка по станциям метро, похожим на дворцы, каждая из которых оформлена по своей теме.",
              "Ташкентский метрополитен открылся в 1977 году первым в Центральной Азии. Станции оформлены по темам — мрамор, люстры, мозаика и резной орнамент, — поэтому короткая поездка превращается в небольшую арт-экскурсию. Станции «Космонавтлар», «Алишер Навои» и «Мустакиллик майдони» любимы гостями города.",
              "Под землёй город держит галерею, открытую всем по цене билета. Проедьте несколько станций — и увидите, как под землёй сияет воображение столицы.")),
        ],
        plan=[
            [B("08:00"), visit("09:00", 0), visit("11:00", 1), L("13:00"), visit("15:00", 2), D("18:30")],
            [B("08:00"), visit("10:00", 3), L("13:00"), D("18:00")],
        ],
    ),
    dict(
        slug="fergana", city_slug="fergana-valley-tour", name="Fergana Valley", names=("Farg'ona vodiysi", "Ферганская долина", "Vallée de Ferghana", "Ferghanatal", "Valle de Fergana"),
        title="Fergana Valley Tour", titles=("Farg'ona vodiysi turi", "Тур по Ферганской долине", "Circuit dans la vallée de Ferghana", "Tour durch das Ferghanatal", "Tour por el valle de Fergana"),
        price=369, days=2, meeting="Fergana airport", meetings=("Farg'ona aeroporti", "Аэропорт Ферганы", "Aéroport de Ferghana", "Flughafen Fergana", "Aeropuerto de Fergana"),
        image="fergana", image_file="Khudayar_Khan_Palace,_Kokand_(2004-09-19).jpg",
        new_destination=dict(
            region="The valley of craftsmen", regions=("Hunarmandlar vodiysi", "Долина мастеров", "La vallée des artisans", "Das Tal der Handwerker", "El valle de los artesanos"),
            summary="Silk ikat in Margilan, glazed pottery in Rishton and the khans' palace in Kokand, in Uzbekistan's green eastern valley.",
            summaries=("Margilondagi ipak ikat, Rishtondagi sirli sopol va Qo'qondagi xonlar saroyi: O'zbekistonning yam-yashil sharqiy vodiysida.", "Шёлковый икат Маргилана, глазурованная керамика Риштана и ханский дворец Коканда в зелёной восточной долине Узбекистана.", "L'ikat de soie de Marguilan, la céramique émaillée de Rishtan et le palais des khans à Kokand, dans la verte vallée orientale de l'Ouzbékistan.", "Seiden-Ikat in Margilan, glasierte Keramik in Rischtan und der Khanspalast in Kokand im grünen Osten Usbekistans.", "El ikat de seda de Margilán, la cerámica vidriada de Rishtán y el palacio de los janes en Kokand, en el verde valle oriental de Uzbekistán."),
            activities=[
                ("Yodgorlik silk factory visit", ("Yodgorlik ipak fabrikasiga tashrif", "Посещение шёлковой фабрики «Ёдгорлик»", "Visite de la fabrique de soie Yodgorlik", "Besuch der Seidenfabrik Yodgorlik", "Visita a la fábrica de seda Yodgorlik")),
                ("Rishton pottery workshop", ("Rishton kulolchilik ustaxonasi", "Гончарная мастерская в Риштане", "Atelier de poterie de Rishtan", "Töpferwerkstatt in Rischtan", "Taller de cerámica de Rishtán")),
                ("Khudayar Khan Palace in Kokand", ("Qo'qondagi Xudoyorxon o'rdasi", "Дворец Худояр-хана в Коканде", "Palais de Khoudayar Khan à Kokand", "Khudayar-Khan-Palast in Kokand", "Palacio de Khudayar Khan en Kokand")),
            ],
            duration="2 days",
        ),
        places=[
            ("khudayar-khan-palace-kokand", "Khudayar Khan Palace", ("Xudoyorxon o'rdasi", "Дворец Худояр-хана", "Palais de Khoudayar Khan", "Khudayar-Khan-Palast", "Palacio de Khudayar Khan"), 6, "Khudayar_Khan_Palace,_Kokand_(2004-09-19).jpg",
             "The richly decorated palace of the last khan of Kokand, with tiled façades and painted rooms.",
             "The palace in Kokand was built in 1863–1873 for Khudayar Khan, the last ruler of the Kokand Khanate, and once had around 100 rooms around several courtyards. Only a part survives today, with a long façade in blue, white and yellow tile. Inside there is a museum of local history, crafts and the khanate's story.",
             "The last khan's palace still wears a coat of tiles in every shade of the sky. Walk through its halls and you hear the footsteps of a vanished empire.",
             ("Qo'qon oxirgi xonining boy bezatilgan o'rdasi: koshinli peshtoqlar va naqshli xonalar.",
              "Qo'qondagi o'rda Qo'qon xonligining so'nggi hukmdori Xudoyorxon uchun 1863–1873-yillarda qurilgan va bir paytlar bir necha hovli atrofida 100 ga yaqin xonaga ega edi. Bugun uning bir qismi saqlangan, uzun peshtoqi ko'k, oq va sariq koshin bilan qoplangan. Ichkarida o'lkashunoslik, hunarmandchilik va xonlik tarixi muzeyi joylashgan.",
              "Oxirgi xon o'rdasi hamon osmonning har xil tusidagi koshin ko'ylagini kiyib turibdi. Zallar bo'ylab yuring va yo'qolgan saltanat qadamlarini eshitasiz."),
             ("Богато украшенный дворец последнего кокандского хана с облицованными фасадами и расписными залами.",
              "Дворец в Коканде построен в 1863–1873 годах для Худояр-хана, последнего правителя Кокандского ханства, и когда-то насчитывал около 100 комнат вокруг нескольких дворов. Сегодня сохранилась лишь часть, с длинным фасадом в синей, белой и жёлтой плитке. Внутри действует музей краеведения, ремёсел и истории ханства.",
              "Дворец последнего хана по-прежнему одет в плитку всех оттенков неба. Пройдите по его залам — и услышите шаги исчезнувшей империи.")),
            ("rishton-ceramics", "Rishton Ceramics", ("Rishton kulolchiligi", "Риштанская керамика", "Céramique de Rishtan", "Rischtaner Keramik", "Cerámica de Rishtán"), 3, "09_Taller_ceràmic_de_Rustam_Usmanov,_Burhoniddin_Roshidoni_Ko'chasi_6_(Rixtan).jpg",
             "A workshop visit to see Rishton's famous blue-green glazed pottery being made by hand.",
             "Rishton has been a pottery centre for around a thousand years. Its masters mix a glaze from the ash of mountain plants and local minerals, which gives the famous deep turquoise and blue; each plate is shaped on the wheel and painted by hand. You can watch the work from clay to kiln, try the wheel and buy plates direct from the maker.",
             "Between a turning wheel and a patient hand, a lump of clay becomes a piece of sky. Take one home and it will keep a little of Rishton in your kitchen.",
             ("Rishtonning mashhur ko'k-yashil sirli sopolini qo'lda yasash jarayonini ustaxonada ko'rish.",
              "Rishton taxminan ming yildan beri kulolchilik markazi. Ustalar tog' o'simliklari kuli va mahalliy minerallardan sir tayyorlaydi, shu sababli mashhur to'q firuza va ko'k rang hosil bo'ladi; har bir lagan charxda shakllantirilib, qo'lda bo'yaladi. Ishni loydan o'choqqacha kuzatishingiz, charxda urinib ko'rishingiz va laganlarni to'g'ridan-to'g'ri ustadan sotib olishingiz mumkin.",
              "Aylanayotgan charx va sabrli qo'l orasida bir parcha loy osmon bo'lagiga aylanadi. Birini olib ketsangiz, oshxonangizda Rishtondan bir parcha qoladi."),
             ("Посещение мастерской, где вручную делают знаменитую сине-зелёную глазурованную керамику Риштана.",
              "Риштан — центр гончарного дела уже около тысячи лет. Мастера готовят глазурь из золы горных растений и местных минералов, что даёт знаменитый глубокий бирюзовый и синий цвет; каждая тарелка формуется на круге и расписывается вручную. Можно проследить работу от глины до печи, попробовать себя на круге и купить посуду прямо у мастера.",
              "Между вращающимся кругом и терпеливой рукой комок глины становится кусочком неба. Увезите один с собой — и в вашей кухне останется немного Риштана.")),
            ("yodgorlik-silk-factory-margilan", "Yodgorlik Silk Factory", ("Yodgorlik ipak fabrikasi", "Шёлковая фабрика «Ёдгорлик»", "Fabrique de soie Yodgorlik", "Seidenfabrik Yodgorlik", "Fábrica de seda Yodgorlik"), 8, "Yodgorlik_Silk_Factory,_Margilan_(497109).jpg",
             "Follow silk from cocoon to shimmering ikat cloth in Margilan, the silk capital of the valley.",
             "Margilan lay on a branch of the Silk Road and is still famous for its silk. At the Yodgorlik workshop you can follow the traditional process: boiling cocoons, reeling the thread, dyeing it with natural colours and weaving the cloth on wooden looms. The bright, feathered patterns of ikat (called atlas and adras) come from tying and dyeing the threads before weaving.",
             "Each thread has travelled from a tiny cocoon to a river of colour. Touch the cloth and you hold a thousand years of Silk Road in your hand.",
             ("Vodiyning ipak poytaxti Marg'ilonda ipakning pilladan yaltiroq ikat matogacha bo'lgan yo'lini kuzating.",
              "Marg'ilon Ipak yo'lining bir tarmog'ida joylashgan va ipagi bilan hamon mashhur. «Yodgorlik» ustaxonasida an'anaviy jarayonni kuzatasiz: pillani qaynatish, ipni o'rash, tabiiy bo'yoqlar bilan bo'yash va yog'och dastgohda mato to'qish. Ikatning (atlas va adras) yorqin, patsimon naqshlari ipni to'qishdan oldin bog'lab bo'yash orqali hosil bo'ladi.",
              "Har bir ip kichik pilladan ranglar daryosigacha yo'l bosgan. Matoga tegsangiz, kaftingizda Ipak yo'lining ming yilini ushlab turasiz."),
             ("Проследите путь шёлка от кокона до переливающейся ткани икат в Маргилане, шёлковой столице долины.",
              "Маргилан лежал на ветви Шёлкового пути и до сих пор славится шёлком. В мастерской «Ёдгорлик» вы увидите традиционный процесс: варку коконов, размотку нити, окраску натуральными красителями и ткачество на деревянных станках. Яркие «перистые» узоры икат (атлас и адрас) получаются благодаря тому, что нити перед ткачеством перевязывают и красят.",
              "Каждая нить прошла путь от крошечного кокона до реки красок. Прикоснитесь к ткани — и вы держите в руке тысячу лет Шёлкового пути.")),
        ],
        plan=[
            [B("08:00"), drive("09:00", 0), visit("10:30", 0), L("13:00"), visit("15:00", 1), D("18:30")],
            [B("08:00"), visit("10:00", 2), L("13:00"), D("18:00")],
        ],
    ),
    dict(
        slug="karakalpakstan", city_slug="karakalpakstan-expedition", name="Karakalpakstan", names=("Qoraqalpog'iston", "Каракалпакстан", "Karakalpakstan", "Karakalpakstan", "Karakalpakstán"),
        title="Karakalpakstan Expedition", titles=("Qoraqalpog'iston ekspeditsiyasi", "Экспедиция по Каракалпакстану", "Expédition au Karakalpakstan", "Karakalpakstan-Expedition", "Expedición a Karakalpakstán"),
        price=499, days=3, meeting="Nukus airport", meetings=("Nukus aeroporti", "Аэропорт Нукуса", "Aéroport de Noukous", "Flughafen Nukus", "Aeropuerto de Nukus"),
        image="karakalpakstan", image_file="Graveyard_of_ships_(431543).jpg",
        new_destination=dict(
            region="Desert fortresses and the Aral Sea", regions=("Cho'l qal'alari va Orol dengizi", "Крепости пустыни и Аральское море", "Forteresses du désert et mer d'Aral", "Wüstenfestungen und der Aralsee", "Fortalezas del desierto y el mar de Aral"),
            summary="Ancient Khorezm fortresses, a world-class art museum in Nukus and the ship graveyard of the vanished Aral Sea.",
            summaries=("Qadimiy Xorazm qal'alari, Nukusdagi jahon darajasidagi san'at muzeyi va yo'qolgan Orol dengizining kemalar qabristoni.", "Древние хорезмские крепости, художественный музей мирового уровня в Нукусе и кладбище кораблей исчезнувшего Аральского моря.", "Les anciennes forteresses du Khorezm, un musée d'art de classe mondiale à Noukous et le cimetière de navires de la mer d'Aral disparue.", "Antike chorasmische Festungen, ein Kunstmuseum von Weltrang in Nukus und der Schiffsfriedhof des verschwundenen Aralsees.", "Antiguas fortalezas de Corasmia, un museo de arte de categoría mundial en Nukus y el cementerio de barcos del desaparecido mar de Aral."),
            activities=[
                ("Savitsky Museum in Nukus", ("Nukusdagi Savitskiy muzeyi", "Музей Савицкого в Нукусе", "Musée Savitsky à Noukous", "Savitsky-Museum in Nukus", "Museo Savitsky en Nukus")),
                ("Ayaz-Kala and Toprak-Kala fortresses", ("Ayoz-Qala va Tuproq-Qala qal'alari", "Крепости Аяз-Кала и Топрак-Кала", "Forteresses d'Ayaz-Kala et de Toprak-Kala", "Festungen Ayaz-Kala und Toprak-Kala", "Fortalezas de Ayaz-Kala y Toprak-Kala")),
                ("Ship graveyard at Moynaq", ("Mo'ynoqdagi kemalar qabristoni", "Кладбище кораблей в Муйнаке", "Cimetière de navires de Moynaq", "Schiffsfriedhof von Moynaq", "Cementerio de barcos de Moynaq")),
            ],
            duration="3 days",
        ),
        places=[
            ("mizdakhan-necropolis", "Mizdakhan Necropolis", ("Mizdahkan nekropoli", "Некрополь Миздахкан", "Nécropole de Mizdahkan", "Nekropole Mizdahkan", "Necrópolis de Mizdahkán"), 4, "Necropolis_Mizdakhan_02.JPG",
             "A vast hilltop city of the dead, in use for around two thousand years.",
             "Mizdakhan, near Khojeli, is one of the oldest and largest burial sites in Central Asia, with graves and monuments from the 4th century BC to the 14th century. It combines Zoroastrian, Muslim and local traditions: you can see the remains of an ancient fortress, pilgrim shrines and the Mazlum Khan Sulu mausoleum from the 14th century. The wide view over the desert plain is unforgettable.",
             "On the hill the desert wind turns the pages of two thousand years. It is a place for quiet steps and long thoughts.",
             ("Ikki ming yilga yaqin foydalanilgan, tepalikdagi ulkan o'liklar shahri.",
              "Xo'jayli yaqinidagi Mizdahkan Markaziy Osiyodagi eng qadimiy va yirik qabristonlardan biri bo'lib, miloddan avvalgi IV asrdan XIV asrgacha bo'lgan qabr va yodgorliklarni o'z ichiga oladi. Unda zardushtiylik, islom va mahalliy an'analar uyg'unlashgan: qadimiy qal'a qoldiqlari, ziyoratgohlar va XIV asrga oid Mazlumxon Sulu maqbarasini ko'rasiz. Cho'l tekisligi uzra ochiladigan keng manzara unutilmas.",
              "Tepalikda cho'l shamoli ikki ming yil sahifalarini varaqlaydi. Bu jim qadamlar va uzoq o'ylar uchun joy."),
             ("Огромный город мёртвых на холме, использовавшийся около двух тысяч лет.",
              "Миздахкан близ Ходжейли — один из древнейших и крупнейших могильников Центральной Азии, с погребениями и памятниками от IV века до н. э. до XIV века. Здесь соединились зороастрийские, мусульманские и местные традиции: вы увидите остатки древней крепости, места паломничества и мавзолей Мазлумхан-Слу XIV века. Широкий вид на пустынную равнину незабываем.",
              "На холме пустынный ветер листает страницы двух тысяч лет. Это место для тихих шагов и долгих мыслей.")),
            ("savitsky-museum-nukus", "Savitsky Museum", ("Savitskiy muzeyi", "Музей Савицкого", "Musée Savitsky", "Savitsky-Museum", "Museo Savitsky"), 10, "The_Karakalpakstan_State_Museum_of_Art_named_after_I.V._Savitsky.jpg",
             "The “Louvre of the desert”: a world-famous collection of Russian avant-garde and Karakalpak art in Nukus.",
             "The Nukus museum is named after Igor Savitsky (1915–1984), an artist and collector who saved thousands of paintings by Soviet avant-garde artists at a time when their work was out of favour. Today it holds one of the finest collections of Russian avant-garde art in the world, together with Karakalpak jewellery, textiles and archaeology. It is a surprising treasure in a remote desert town.",
             "One man gathered what others feared to keep, and the desert became a gallery. Walk its rooms and meet the quiet courage of art.",
             ("«Cho'ldagi Luvr»: Nukusdagi rus avangardi va qoraqalpoq san'atining jahonga mashhur to'plami.",
              "Nukus muzeyi rassom va kolleksioner Igor Savitskiy (1915–1984) nomi bilan ataladi; u sovet avangard rassomlarining asarlari e'tibordan chetda qolgan paytda ularning minglab asarlarini saqlab qolgan. Bugun u dunyodagi rus avangardining eng yaxshi to'plamlaridan birini, shuningdek qoraqalpoq taqinchoqlari, matolari va arxeologiyasini saqlaydi. Olis cho'l shaharchasidagi kutilmagan xazina.",
              "Bir inson boshqalar saqlashdan qo'rqqanini yig'di va cho'l galereyaga aylandi. Xonalarini aylaning va san'atning sokin jasoratini uchratasiz."),
             ("«Лувр в пустыне»: всемирно известная коллекция русского авангарда и каракалпакского искусства в Нукусе.",
              "Музей в Нукусе назван в честь Игоря Савицкого (1915–1984), художника и коллекционера, который спас тысячи картин советских авангардистов, когда их искусство было не в чести. Сегодня здесь одна из лучших в мире коллекций русского авангарда, а также каракалпакские украшения, ткани и археологические находки. Неожиданное сокровище в далёком пустынном городе.",
              "Один человек собрал то, что другие боялись хранить, — и пустыня стала галереей. Пройдите по её залам и встретьтесь с тихой смелостью искусства.")),
            ("toprak-kala", "Toprak-Kala", ("Tuproq-Qala", "Топрак-Кала", "Toprak-Kala", "Toprak-Kala", "Toprak-Kala"), 5, "Toprak-Kala_01.jpg",
             "The ruined palace city of the rulers of ancient Khorezm, once covered in painted walls.",
             "Toprak-Kala was a royal city of Khorezm in the 2nd–3rd centuries AD and part of the group known as the “fifty fortresses”. Archaeologists found wall paintings, clay sculpture, coins and a royal archive of documents here. Today you walk among the great earth walls and towers and can still make out the plan of a palace.",
             "Walls of earth that once held kings still stand in the sand. Listen: the desert keeps their names.",
             ("Qadimiy Xorazm hukmdorlarining vayron bo'lgan saroy shahri, bir paytlar devorlari rasmlar bilan qoplangan.",
              "Tuproq-Qala milodiy II–III asrlarda Xorazmning shoh shahri bo'lgan va «ellik qal'a» deb ataluvchi guruhga kiradi. Arxeologlar bu yerdan devor rasmlari, loy haykallar, tangalar va shohlar hujjatlari arxivini topgan. Bugun siz katta tuproq devor va minoralar orasida yurasiz va saroy rejasini hamon ajrata olasiz.",
              "Bir paytlar shohlarni ushlagan tuproq devorlar qumda hamon turibdi. Quloq soling: cho'l ularning ismlarini saqlaydi."),
             ("Разрушенный дворцовый город правителей древнего Хорезма, когда-то покрытый расписными стенами.",
              "Топрак-Кала была царским городом Хорезма во II–III веках н. э. и входит в группу «пятидесяти крепостей». Археологи нашли здесь настенную живопись, глиняную скульптуру, монеты и царский архив документов. Сегодня вы идёте среди огромных глиняных стен и башен и всё ещё можете различить план дворца.",
              "Глиняные стены, когда-то хранившие царей, всё ещё стоят в песках. Прислушайтесь: пустыня хранит их имена.")),
            ("ayaz-kala-fortress", "Ayaz-Kala Fortress", ("Ayoz-Qala qal'asi", "Крепость Аяз-Кала", "Forteresse d'Ayaz-Kala", "Festung Ayaz-Kala", "Fortaleza de Ayaz-Kala"), 5, "Ayaz-Kala-2.jpg",
             "Hilltop fortresses of ancient Khorezm watching over the Kyzylkum desert.",
             "Ayaz-Kala is a group of desert fortresses built between the 4th century BC and the 7th century AD on a hill above the Kyzylkum. The largest fort sits on the top, with views over the sand and a nearby yurt camp. Climb the old walls at sunrise or sunset for the best light and the strongest sense of the Silk Road's edge.",
             "At sunset the old stones turn the colour of embers and the whole desert goes quiet. You are standing where watchmen once waited for caravans.",
             ("Qizilqum cho'li uzra qarab turgan qadimiy Xorazmning tepalikdagi qal'alari.",
              "Ayoz-Qala — miloddan avvalgi IV asrdan milodiy VII asrgacha Qizilqum ustidagi tepalikda qurilgan cho'l qal'alari guruhi. Eng katta qal'a cho'qqida turadi, qum va yaqindagi yurta lageriga ochiladigan manzarasi bor. Eng yaxshi yorug'lik va Ipak yo'li chekkasini eng kuchli his qilish uchun eski devorlarga tong yoki shomda chiqing.",
              "Quyosh botganda qadimiy toshlar cho'g' rangiga kiradi, butun cho'l jim bo'lib qoladi. Siz bir paytlar qo'riqchilar karvonni kutgan joyda turibsiz."),
             ("Крепости на холмах древнего Хорезма, наблюдающие за пустыней Кызылкум.",
              "Аяз-Кала — группа пустынных крепостей, построенных между IV веком до н. э. и VII веком н. э. на холме над Кызылкумом. Самая большая крепость стоит на вершине, с видом на пески и ближайший юртовый лагерь. Поднимитесь на старые стены на рассвете или закате — лучший свет и самое сильное чувство края Шёлкового пути.",
              "На закате старые камни становятся цвета углей, и вся пустыня стихает. Вы стоите там, где сторожа когда-то ждали караваны.")),
            ("moynaq-ship-graveyard", "Moynaq & the Aral Sea", ("Mo'ynoq va Orol dengizi", "Муйнак и Аральское море", "Moynaq et la mer d'Aral", "Moynaq und der Aralsee", "Moynaq y el mar de Aral"), 5, "Graveyard_of_ships_(431543).jpg",
             "The rusting ships of Moynaq, once a seaport, now far from the shrunken Aral Sea.",
             "Moynaq was a busy fishing port on the Aral Sea. As the sea shrank from the 1960s, the water retreated, and today the shoreline is some 150 kilometres away. Rusting ships stand in the sand beside a small museum telling the story of the town and the sea. It is a striking and thought-provoking place, and a reminder of how fragile nature can be.",
             "Ships wait in the sand for a sea that has gone. Stand beside them in the wind and listen to a lesson written in rust.",
             ("Bir paytlar dengiz porti bo'lgan Mo'ynoqdagi zanglagan kemalar, endi kichrayib ketgan Orol dengizidan uzoqda.",
              "Mo'ynoq Orol dengizidagi gavjum baliqchilik porti edi. 1960-yillardan boshlab dengiz kichrayib, suv chekindi, bugun qirg'oq chizig'i taxminan 150 kilometr naridadir. Qum ustida zanglagan kemalar turibdi, yonida shahar va dengiz tarixini hikoya qiluvchi kichik muzey bor. Bu ta'sirli va o'ylantiruvchi joy, tabiat qanchalik mo'rtligini eslatadi.",
              "Kemalar qum ustida ketib qolgan dengizni kutmoqda. Ularning yonida shamolda turing va zangda yozilgan saboqni tinglang."),
             ("Ржавеющие корабли Муйнака — бывшего морского порта, теперь далеко от обмелевшего Аральского моря.",
              "Муйнак был оживлённым рыболовецким портом на Аральском море. С 1960-х годов море мелело и отступало, и сегодня береговая линия находится примерно в 150 километрах. Ржавеющие корабли стоят в песке рядом с небольшим музеем, рассказывающим о городе и море. Это впечатляющее, заставляющее задуматься место, напоминание о хрупкости природы.",
              "Корабли ждут в песке ушедшее море. Постойте рядом с ними на ветру — и услышьте урок, написанный ржавчиной.")),
        ],
        plan=[
            [B("08:00"), visit("09:00", 0), L("13:00"), visit("14:30", 1), D("18:30")],
            [B("07:30"), drive("08:00", 2), visit("09:30", 2), visit("12:00", 3), L("14:00"), D("18:30")],
            [B("07:00"), drive("08:00", 4), visit("10:30", 4), L("13:00"), D("18:00")],
        ],
    ),
]

# Hotels for the new regions so visitors can pick one (sample listings; replace with your partner hotels in the admin panel).
HOTELS = [
    ("shahrisabz-courtyard-guesthouse", "Shahrisabz Courtyard Guesthouse", "kashkadarya", "Kashkadarya", 3, "Sample listing — a family guesthouse near the Ak-Saray ruins.", 52),
    ("kokand-silk-road-inn", "Kokand Silk Road Inn", "fergana", "Fergana Valley", 3, "Sample listing — a quiet inn close to the Khudayar Khan Palace.", 58),
    ("nukus-museum-view-hotel", "Nukus Museum View Hotel", "karakalpakstan", "Karakalpakstan", 3, "Sample listing — a simple hotel a short walk from the Savitsky Museum.", 56),
]

# ---- English texts shared by every regional tour, with their translations (placeholders filled in per region)
SUMMARY_EN = "The highlights of {region} with a local guide, taxi rides between stops and a warm welcome on arrival."
SUMMARY_T = (
    "Mahalliy gid bilan {region} bo'ylab eng muhim joylar: bekatlar orasida taksi va kelganingizda iliq kutib olish.",
    "Главные места региона «{region}» с местным гидом, поездки на такси между остановками и тёплая встреча по прибытии.",
    "Les incontournables de la région « {region} » avec un guide local, taxi entre les étapes et accueil chaleureux à l'arrivée.",
    "Die Highlights der Region „{region}“ mit lokalem Guide, Taxifahrten zwischen den Stopps und herzlichem Empfang bei der Ankunft.",
    "Lo mejor de la región «{region}» con guía local, taxi entre las paradas y una cálida bienvenida a la llegada.",
)
DESCRIPTION_EN = ("Walk and ride through the highlights of {region}: {places}. Your guide from the ALI TRAVEL team stays with you "
                  "throughout the tour. Meeting point: {meeting}. Taxis between the stops are included; entrance tickets are paid separately at each site.")
DESCRIPTION_T = (
    "{region} bo'ylab eng muhim joylarni piyoda va mashinada kezing: {places}. ALI TRAVEL jamoasidan gidingiz sayohat davomida yoningizda bo'ladi. Uchrashuv joyi: {meeting}. Bekatlar orasidagi taksi narxga kiritilgan; kirish chiptalari har bir joyda alohida to'lanadi.",
    "Пройдите и проедьте по главным местам региона «{region}»: {places}. Ваш гид из команды ALI TRAVEL будет с вами весь тур. Место встречи: {meeting}. Такси между остановками включено; входные билеты оплачиваются отдельно на каждом объекте.",
    "Parcourez à pied et en voiture les incontournables de la région « {region} » : {places}. Votre guide de l'équipe ALI TRAVEL vous accompagne tout au long du circuit. Point de rendez-vous : {meeting}. Les taxis entre les étapes sont inclus ; les billets d'entrée se paient séparément sur chaque site.",
    "Erkunden Sie zu Fuß und per Auto die Highlights der Region „{region}“: {places}. Ihr Guide vom ALI-TRAVEL-Team begleitet Sie während der gesamten Tour. Treffpunkt: {meeting}. Taxifahrten zwischen den Stopps sind inklusive; Eintrittskarten werden an jeder Sehenswürdigkeit separat bezahlt.",
    "Recorra a pie y en coche lo mejor de la región «{region}»: {places}. Su guía del equipo de ALI TRAVEL le acompaña durante todo el tour. Punto de encuentro: {meeting}. Los taxis entre las paradas están incluidos; las entradas se pagan aparte en cada lugar.",
)
TRIP_T = (
    "{n} ta tarixiy joyga sayohat", "Поездка к {n} историческим местам", "Excursion vers {n} sites historiques", "Fahrt zu {n} historischen Orten", "Viaje a {n} lugares históricos",
)
EXTRA_PHRASES = {
    "Three days of hotel accommodation": ("Uch kunlik mehmonxona", "Три дня проживания в отеле", "Trois jours d'hébergement à l'hôtel", "Drei Tage Hotelunterkunft", "Tres días de alojamiento en hotel"),
    "Round-trip transfer from Samarkand": ("Samarqanddan borib-kelish transferi", "Трансфер из Самарканда туда и обратно", "Transfert aller-retour depuis Samarcande", "Hin- und Rücktransfer ab Samarkand", "Traslado de ida y vuelta desde Samarcanda"),
    "Seven regions, one Silk Road": ("Yetti hudud, bitta Ipak yo'li", "Семь регионов, один Шёлковый путь", "Sept régions, une Route de la soie", "Sieben Regionen, eine Seidenstraße", "Siete regiones, una Ruta de la Seda"),
    "Khorezm": ("Xorazm", "Хорезм", "Khorezm", "Choresm", "Corasmia"),
    "Kashkadarya": ("Qashqadaryo", "Кашкадарья", "Kachkadaria", "Kaschkadarja", "Kashkadarya"),
    "Sample listing — a family guesthouse near the Ak-Saray ruins.": ("Namuna e'lon — Oqsaroy xarobalari yaqinidagi oilaviy mehmon uyi.", "Пример объявления — семейный гостевой дом возле руин Ак-Сарая.", "", "", ""),
    "Sample listing — a quiet inn close to the Khudayar Khan Palace.": ("Namuna e'lon — Xudoyorxon o'rdasi yaqinidagi sokin mehmonxona.", "Пример объявления — тихая гостиница рядом с дворцом Худояр-хана.", "", "", ""),
    "Sample listing — a simple hotel a short walk from the Savitsky Museum.": ("Namuna e'lon — Savitskiy muzeyidan sal narida joylashgan oddiy mehmonxona.", "Пример объявления — простая гостиница в нескольких шагах от музея Савицкого.", "", "", ""),
}

TITLE_T = (
    "{n} turi", "Тур: {n}", "Visite : {n}", "Tour: {n}", "Tour: {n}",
)


def register_phrases():
    """Add the translations of all regional texts to the shared phrase book (fr/de/es place texts stay empty = English)."""
    PHRASES.update(EXTRA_PHRASES)
    for r in REGIONS:
        PHRASES[r["name"]] = r["names"]
        PHRASES[r["title"]] = r["titles"]
        PHRASES[r["meeting"]] = r["meetings"]
        places_en = ", ".join(p[1] for p in r["places"])
        PHRASES[SUMMARY_EN.format(region=r["name"])] = tuple(SUMMARY_T[i].format(region=r["names"][i]) for i in range(5))
        PHRASES[DESCRIPTION_EN.format(region=r["name"], places=places_en, meeting=r["meeting"])] = tuple(
            DESCRIPTION_T[i].format(region=r["names"][i], places=", ".join(p[2][i] for p in r["places"]), meeting=r["meetings"][i]) for i in range(5))
        n = len(r["places"])
        PHRASES[f"Trip to {n} historical places"] = tuple(TRIP_T[i].format(n=n) for i in range(5))
        nd = r.get("new_destination")
        if nd:
            PHRASES[nd["region"]] = nd["regions"]
            PHRASES[nd["summary"]] = nd["summaries"]
            for en, tr in nd["activities"]:
                PHRASES[en] = tr
        for slug, name, names, fee, _, summary, about, story, uz, ru in r["places"]:
            PHRASES[name] = names
            PHRASES[f"{name} Tour"] = tuple(TITLE_T[i].format(n=names[i]) for i in range(5))
            for en, (u, ru_text) in ((summary, (uz[0], ru[0])), (about, (uz[1], ru[1])), (story, (uz[2], ru[2]))):
                PHRASES[en] = (u, ru_text, "", "", "")


register_phrases()
