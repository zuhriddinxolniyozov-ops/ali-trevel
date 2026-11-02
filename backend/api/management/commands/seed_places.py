"""Samarkand's places: a factual note ("about") and a short keepsake text ("story") for each, in six languages,
plus the sample two-day plan of the Samarkand City Tour.

Translations are (uz, ru, fr, de, es) and are merged into the seed phrase book at import time.
"""
from api.management.commands.seed_translations import PHRASES

# slug suffix, name, entrance fee (USD), summary, about, story
PLACES = [
    ("registan-square", "Registan Square", 16,
     "The heart of Samarkand: three madrasahs facing a grand square covered in tile and gold.",
     "Registan means “sandy place”. Three madrasahs frame the square: Ulugh Beg (1417–1420), Sher-Dor (1619–1636) with its sun-faced big cats chasing deer, and gilded Tilya-Kori (1646–1660). Today the old student cells hold craft shops, and the square glows after dark.",
     "At golden hour the tiles of the Registan turn from blue to flame, and for a moment the whole square feels like a jewel box opened just for you."),
    ("gur-e-amir-mausoleum", "Gur-e-Amir Mausoleum", 13,
     "The turquoise-domed tomb of Amir Timur and his descendants, a masterpiece of Timurid architecture.",
     "Gur-e-Amir means “Tomb of the Emir”. Begun in 1403, it became the resting place of Timur (d. 1405), his sons Shah Rukh and Miran Shah, his grandson Ulugh Beg and his teacher Mir Sayyid Baraka. Its ribbed turquoise dome and the dark-green stone over Timur's grave are famous, and it foreshadows the great Mughal tombs of India.",
     "Beneath a dome the colour of the sky after rain, an emperor who shook the world sleeps in silence. Pause in the gilded half-light and you can almost hear history breathe."),
    ("bibi-khanym-mosque", "Bibi-Khanym Mosque", 9,
     "One of the largest mosques of its time, built by Timur, with a monumental portal and a vast courtyard.",
     "Timur ordered this mosque after his Indian campaign; it was built in 1399–1404 and named after his senior wife. It was among the largest mosques of the Islamic world. Earthquakes damaged it, it has been partly restored, and a giant marble Quran stand still stands in the courtyard.",
     "Even weathered by centuries, her great arches still reach for the sky. Cross the vast courtyard where thousands once prayed and let the silence tell you what ambition sounds like."),
    ("siyob-bazaar", "Siyob Bazaar", 1,
     "Samarkand's busy main market beside the Bibi-Khanym Mosque: fresh bread, dried fruit, nuts and spices.",
     "Samarkand's main market lies beside the Bibi-Khanym Mosque. Look for round Samarkand non bread, dried apricots and raisins, nuts, halva and spices. It is the best place to taste before you buy and to watch everyday local life.",
     "Warm bread, honeyed sweets and the calls of the sellers: here Samarkand still trades as it did when caravans arrived from China. Take a taste and carry the city home."),
    ("shah-i-zinda", "Shah-i-Zinda", 11,
     "A street of blue-tiled mausoleums climbing a hill, one of the most revered sites in Central Asia.",
     "Shah-i-Zinda means “the Living King”. A lane of mausoleums climbs a hill near the shrine traditionally linked to Qusam ibn Abbas, cousin of the Prophet Muhammad. Most buildings date from the 14th–15th centuries and are covered in blue and turquoise glazed tiles, a high point of Timurid art.",
     "A stair of blue, each step quieter than the last. Under tiles that have kept their colour for six hundred years, you walk through a street where the departed were honoured with the finest art of the age."),
    ("silk-road-eternal-city", "Silk Road Eternal City", 22,
     "A modern Silk Road-themed complex of pedestrian streets, workshops, cafés and fountains.",
     "A recently built complex inspired by the Silk Road, with pedestrian streets, craft workshops, cafés and fountains. A relaxed stop to see artisans at work, shop for gifts and rest between the great monuments.",
     "Where caravans once rested, lanterns and fountains now welcome you. Wander the lanes, watch a craftsman at work, and feel how the old road keeps inviting travellers."),
    ("ulugh-beg-observatory", "Ulugh Beg Observatory", 29,
     "The remains of the 15th-century observatory of the astronomer-ruler Ulugh Beg.",
     "Built around 1428–1429 for Ulugh Beg, Timur's grandson, ruler and astronomer. Here his team compiled a catalogue of more than a thousand stars that served scholars for centuries. You can see the underground part of the giant sextant, and a small museum tells the story of the scholar-king, who died in 1449.",
     "Long before telescopes, a king looked up from a hill outside Samarkand and counted the stars with an instrument the size of a building. Stand in its curved trench and you stand inside an old dream of the sky."),
    ("imam-al-bukhari-complex", "Imam al-Bukhari Complex", 29,
     "The memorial complex and mosque honouring the hadith scholar Imam al-Bukhari, a place of pilgrimage.",
     "Imam al-Bukhari (810–870) was born in Bukhara and became the most famous collector of hadith, the sayings and actions of the Prophet Muhammad. His book Sahih al-Bukhari is regarded by Sunni Muslims as the most authentic after the Quran. He died in the village of Khartang near Samarkand. The memorial complex with a mosque, his tomb and a museum on his life and the study of hadith was greatly expanded in 1998.",
     "Quiet gardens, a blue-domed prayer hall and a village where a great scholar came to rest: this is a place for stillness. Leave the hurry of the road at the gate and carry a little of its calm home."),
]

# The visiting order of the two-day plan; the route of the city tour follows it, so "stop" indexes line up.
ROUTE_ORDER = ["Gur-e-Amir Mausoleum", "Registan Square", "Bibi-Khanym Mosque", "Siyob Bazaar", "Shah-i-Zinda",
               "Silk Road Eternal City", "Ulugh Beg Observatory", "Imam al-Bukhari Complex"]
OLD_ROUTE_ORDER = ["Registan Square", "Gur-e-Amir Mausoleum", "Bibi-Khanym Mosque", "Siyob Bazaar", "Shah-i-Zinda",
                   "Ulugh Beg Observatory", "Silk Road Eternal City", "Imam al-Bukhari Complex"]


def meal(time, kind, included):
    return {"time": time, "type": "meal", "meal": kind, "included": included}


def visit(time, stop):
    return {"time": time, "type": "visit", "stop": ROUTE_ORDER.index(stop)}


CITY_ITINERARY = [
    {"day": 1, "items": [
        meal("08:00", "breakfast", True), visit("09:00", "Gur-e-Amir Mausoleum"), visit("10:30", "Registan Square"),
        meal("13:00", "lunch", False), visit("14:00", "Bibi-Khanym Mosque"), visit("15:00", "Siyob Bazaar"),
        visit("16:00", "Shah-i-Zinda"), meal("18:00", "dinner", False)]},
    {"day": 2, "items": [
        meal("08:00", "breakfast", True), visit("09:00", "Silk Road Eternal City"), visit("11:00", "Ulugh Beg Observatory"),
        meal("13:00", "lunch", False), {"time": "14:00", "type": "transfer", "stop": ROUTE_ORDER.index("Imam al-Bukhari Complex")},
        visit("15:00", "Imam al-Bukhari Complex"), meal("18:00", "dinner", False)]},
]

TEXT = {
    "Siyob Bazaar Tour": ("Siyob bozori turi", "Тур: базар Сиаб", "Visite du bazar Siyob", "Tour: Siyob-Basar", "Tour: bazar Siyob"),
    "Samarkand's busy main market beside the Bibi-Khanym Mosque: fresh bread, dried fruit, nuts and spices.": (
        "Bibixonim masjidi yonidagi gavjum asosiy bozor: yangi non, quritilgan mevalar, yong'oq va ziravorlar.",
        "Шумный главный рынок рядом с мечетью Биби-Ханым: свежий хлеб, сухофрукты, орехи и специи.",
        "Le grand marché animé près de la mosquée Bibi-Khanym : pain frais, fruits secs, noix et épices.",
        "Der lebhafte Hauptmarkt neben der Bibi-Chanum-Moschee: frisches Brot, Trockenfrüchte, Nüsse und Gewürze.",
        "El animado mercado principal junto a la mezquita Bibi-Janum: pan fresco, frutos secos, nueces y especias."),
    # ---- about
    PLACES[0][4]: (
        "Registon — «qumli joy» degani. Maydonni uchta madrasa o'rab turadi: Ulug'bek (1417–1420), quyosh yuzli yo'lbarslari ohu quvayotgan Sherdor (1619–1636) va zarhal Tillakori (1646–1660). Hozir eski hujralarda hunarmandchilik do'konlari joylashgan, kechqurun maydon charaqlab yonadi.",
        "Регистан означает «песчаное место». Площадь обрамляют три медресе: Улугбека (1417–1420), Шердор (1619–1636) с хищниками с солнечными ликами, преследующими оленей, и позолоченное Тилля-Кари (1646–1660). Сегодня в старых кельях студентов — ремесленные лавки, а вечером площадь сияет огнями.",
        "Registan signifie « lieu sablonneux ». Trois médersas encadrent la place : Ouloug Beg (1417–1420), Cher-Dor (1619–1636), avec ses fauves au visage de soleil poursuivant des cerfs, et Tilla-Kari la dorée (1646–1660). Aujourd'hui, les anciennes cellules d'étudiants abritent des boutiques d'artisanat, et la place s'illumine à la nuit tombée.",
        "Registan bedeutet „sandiger Ort“. Drei Medresen rahmen den Platz: Ulugbek (1417–1420), Scher-Dor (1619–1636) mit seinen sonnengesichtigen Raubkatzen, die Hirsche jagen, und die vergoldete Tilla-Kari (1646–1660). Heute beherbergen die alten Studentenzellen Kunsthandwerksläden, und nach Einbruch der Dunkelheit leuchtet der Platz.",
        "Registán significa «lugar arenoso». Tres madrasas enmarcan la plaza: Ulugbek (1417–1420), Sher-Dor (1619–1636), con sus felinos de rostro solar que persiguen ciervos, y la dorada Tilla-Kari (1646–1660). Hoy las antiguas celdas de los estudiantes albergan tiendas de artesanía y, al anochecer, la plaza resplandece."),
    PLACES[1][4]: (
        "Go'ri Amir — «Amir qabri» degani. 1403-yilda boshlangan bu maqbarada Amir Temur (1405-yilda vafot etgan), o'g'illari Shohruh va Mironshoh, nabirasi Ulug'bek hamda ustozi Mir Sayyid Baraka dafn etilgan. Qovurg'ali feruza gumbaz va Temur qabri ustidagi to'q yashil tosh mashhur; maqbara Hindistondagi buyuk mug'al maqbaralariga ilhom bo'lgan deb hisoblanadi.",
        "Гур-Эмир означает «Гробница эмира». Построенный с 1403 года, мавзолей стал местом упокоения Тимура (ум. 1405), его сыновей Шахруха и Мираншаха, внука Улугбека и учителя Мир Сайида Бараки. Известны его рифлёный бирюзовый купол и тёмно-зелёный камень над могилой Тимура; считается предтечей великих гробниц Великих Моголов в Индии.",
        "Gour-Émir signifie « Tombeau de l'émir ». Commencé en 1403, il devint le dernier repos de Tamerlan (m. 1405), de ses fils Chah Rokh et Miran Chah, de son petit-fils Ouloug Beg et de son maître Mir Sayyid Baraka. Son dôme turquoise côtelé et la pierre vert sombre sur la tombe de Tamerlan sont célèbres ; il annonce les grands tombeaux moghols de l'Inde.",
        "Gur-Emir bedeutet „Grab des Emirs“. Der 1403 begonnene Bau wurde zur letzten Ruhestätte Timurs (gest. 1405), seiner Söhne Schah Ruch und Miran Schah, seines Enkels Ulugbek und seines Lehrers Mir Sayyid Baraka. Berühmt sind die gerippte türkisfarbene Kuppel und der dunkelgrüne Stein über Timurs Grab; der Bau gilt als Vorläufer der großen Mogulgräber Indiens.",
        "Gur-e-Amir significa «Tumba del Emir». Iniciado en 1403, se convirtió en el lugar de reposo de Tamerlán (m. 1405), sus hijos Shah Rukh y Miran Shah, su nieto Ulugbek y su maestro Mir Sayyid Baraka. Son famosos su cúpula turquesa acanalada y la piedra verde oscuro sobre la tumba de Tamerlán; anticipa las grandes tumbas mogolas de la India."),
    PLACES[2][4]: (
        "Amir Temur bu masjidni Hindiston yurishidan keyin qurdirgan; u 1399–1404-yillarda barpo etilgan va bosh xotini nomi bilan ataladi. U islom olamidagi eng katta masjidlardan biri bo'lgan. Zilzilalar uni shikastlagan, qisman tiklangan; hovlida hamon ulkan marmar Qur'on rahli turibdi.",
        "Тимур приказал построить эту мечеть после индийского похода; она возведена в 1399–1404 годах и названа в честь его старшей жены. Это была одна из крупнейших мечетей исламского мира. Землетрясения разрушили её, позже она была частично восстановлена; во дворе по-прежнему стоит гигантская мраморная подставка для Корана.",
        "Tamerlan ordonna cette mosquée après sa campagne des Indes ; elle fut bâtie en 1399–1404 et porte le nom de son épouse principale. C'était l'une des plus grandes mosquées du monde islamique. Endommagée par des séismes, elle a été en partie restaurée ; un immense pupitre à Coran en marbre se dresse toujours dans la cour.",
        "Timur ließ diese Moschee nach seinem Indienfeldzug errichten; sie entstand 1399–1404 und ist nach seiner Hauptfrau benannt. Sie gehörte zu den größten Moscheen der islamischen Welt. Erdbeben beschädigten sie, sie wurde teilweise restauriert; im Hof steht noch immer ein riesiger Koranständer aus Marmor.",
        "Tamerlán ordenó esta mezquita tras su campaña en la India; se construyó entre 1399 y 1404 y lleva el nombre de su esposa principal. Fue una de las mayores mezquitas del mundo islámico. Los terremotos la dañaron y se ha restaurado en parte; en el patio sigue en pie un gigantesco atril de mármol para el Corán."),
    PLACES[3][4]: (
        "Samarqandning asosiy bozori Bibixonim masjidi yonida joylashgan. Yumaloq Samarqand noni, quritilgan o'rik va mayiz, yong'oq, holva va ziravorlarni qidiring. Sotib olishdan oldin tatib ko'rish va mahalliy kundalik hayotni kuzatish uchun eng yaxshi joy.",
        "Главный рынок Самарканда находится рядом с мечетью Биби-Ханым. Ищите круглые самаркандские лепёшки, курагу и изюм, орехи, халву и специи. Здесь лучше всего пробовать перед покупкой и наблюдать за повседневной жизнью.",
        "Le grand marché de Samarcande se trouve à côté de la mosquée Bibi-Khanym. Cherchez le pain non rond de Samarcande, les abricots secs et les raisins secs, les noix, le halva et les épices. C'est le meilleur endroit pour goûter avant d'acheter et observer la vie quotidienne locale.",
        "Samarkands Hauptmarkt liegt neben der Bibi-Chanum-Moschee. Suchen Sie nach rundem Samarkander Non-Brot, getrockneten Aprikosen und Rosinen, Nüssen, Halva und Gewürzen. Hier probieren Sie am besten vor dem Kauf und erleben den Alltag der Einheimischen.",
        "El mercado principal de Samarcanda está junto a la mezquita Bibi-Janum. Busque el pan non redondo de Samarcanda, orejones y pasas, frutos secos, halva y especias. Es el mejor lugar para probar antes de comprar y para ver la vida cotidiana local."),
    PLACES[4][4]: (
        "Shohi Zinda — «Tirik shoh» degani. Maqbaralar ko'chasi Payg'ambar Muhammad (s.a.v.)ning amakivachchasi Qusam ibn Abbosga bog'lanadigan ziyoratgoh yaqinidagi tepalikka ko'tariladi. Binolarning ko'pchiligi XIV–XV asrlarga oid va ko'k-feruza sirli koshin bilan qoplangan — temuriylar san'atining cho'qqisi.",
        "Шахи-Зинда означает «Живой царь». Улица мавзолеев поднимается на холм рядом со святыней, которую традиционно связывают с Кусамом ибн Аббасом, двоюродным братом пророка Мухаммеда. Большинство построек относится к XIV–XV векам и покрыто сине-бирюзовой глазурованной плиткой — вершина искусства Тимуридов.",
        "Chah-i-Zinda signifie « le Roi vivant ». Une allée de mausolées gravit une colline près du sanctuaire traditionnellement lié à Qousam ibn Abbas, cousin du prophète Mahomet. La plupart des édifices datent des XIVe–XVe siècles et sont couverts de faïences émaillées bleues et turquoise, sommet de l'art timouride.",
        "Schah-i-Sinda bedeutet „der lebende König“. Eine Gasse aus Mausoleen steigt einen Hügel hinauf, nahe dem Schrein, der traditionell mit Kusam ibn Abbas, dem Cousin des Propheten Mohammed, verbunden wird. Die meisten Bauten stammen aus dem 14.–15. Jahrhundert und sind mit blauen und türkisfarbenen glasierten Fliesen bedeckt – ein Höhepunkt timuridischer Kunst.",
        "Shah-i-Zinda significa «el Rey Vivo». Una calle de mausoleos asciende por una colina junto al santuario vinculado tradicionalmente a Qusam ibn Abbas, primo del profeta Mahoma. La mayoría de los edificios son de los siglos XIV y XV y están cubiertos de azulejos vidriados azules y turquesa, cumbre del arte timúrida."),
    PLACES[5][4]: (
        "Ipak yo'lidan ilhomlangan, yaqinda qurilgan majmua: piyodalar ko'chalari, hunarmandchilik ustaxonalari, kafelar va favvoralar. Ustalarning ishini ko'rish, sovg'a tanlash va buyuk yodgorliklar orasida dam olish uchun xotirjam to'xtash joyi.",
        "Недавно построенный комплекс в духе Шёлкового пути: пешеходные улицы, ремесленные мастерские, кафе и фонтаны. Спокойная остановка, чтобы увидеть мастеров за работой, выбрать подарки и отдохнуть между великими памятниками.",
        "Un complexe récent inspiré de la Route de la soie, avec rues piétonnes, ateliers d'artisans, cafés et fontaines. Une halte détendue pour voir les artisans à l'œuvre, acheter des cadeaux et se reposer entre les grands monuments.",
        "Ein kürzlich erbauter, von der Seidenstraße inspirierter Komplex mit Fußgängerstraßen, Kunsthandwerkstätten, Cafés und Brunnen. Ein entspannter Halt, um Handwerkern bei der Arbeit zuzusehen, Geschenke zu kaufen und zwischen den großen Monumenten auszuruhen.",
        "Un complejo de reciente construcción inspirado en la Ruta de la Seda, con calles peatonales, talleres de artesanía, cafés y fuentes. Una parada tranquila para ver a los artesanos trabajar, comprar regalos y descansar entre los grandes monumentos."),
    PLACES[6][4]: (
        "Temurning nabirasi, hukmdor va astronom Ulug'bek uchun taxminan 1428–1429-yillarda qurilgan. Bu yerda uning jamoasi olimlarga asrlar davomida xizmat qilgan mingdan ortiq yulduz katalogini tuzgan. Ulkan sekstantning yer ostidagi qismini ko'rishingiz mumkin, kichik muzey esa 1449-yilda vafot etgan olim-shoh haqida hikoya qiladi.",
        "Построена около 1428–1429 годов для Улугбека — внука Тимура, правителя и астронома. Здесь его команда составила каталог более чем тысячи звёзд, которым учёные пользовались веками. Можно увидеть подземную часть гигантского секстанта, а небольшой музей рассказывает о правителе-учёном, погибшем в 1449 году.",
        "Construit vers 1428–1429 pour Ouloug Beg, petit-fils de Tamerlan, souverain et astronome. Son équipe y établit un catalogue de plus de mille étoiles qui a servi aux savants pendant des siècles. On peut voir la partie souterraine du sextant géant, et un petit musée raconte l'histoire du roi savant, mort en 1449.",
        "Um 1428–1429 für Ulugbek erbaut, Timurs Enkel, Herrscher und Astronom. Sein Team erstellte hier einen Katalog von über tausend Sternen, der Gelehrten jahrhundertelang diente. Zu sehen ist der unterirdische Teil des riesigen Sextanten, und ein kleines Museum erzählt vom gelehrten König, der 1449 starb.",
        "Construido hacia 1428–1429 para Ulugbek, nieto de Tamerlán, gobernante y astrónomo. Aquí su equipo elaboró un catálogo de más de mil estrellas que sirvió a los sabios durante siglos. Puede verse la parte subterránea del sextante gigante, y un pequeño museo cuenta la historia del rey sabio, fallecido en 1449."),
    PLACES[7][4]: (
        "Imom Buxoriy (810–870) Buxoroda tug'ilgan va Payg'ambar Muhammad (s.a.v.)ning so'zlari va amallari — hadislarni to'plagan eng mashhur olim bo'lgan. Uning «Sahih al-Buxoriy» kitobi sunniy musulmonlar tomonidan Qur'ondan keyingi eng ishonchli kitob sanaladi. U Samarqand yaqinidagi Hartang qishlog'ida vafot etgan. Masjid, qabr va uning hayoti hamda hadisshunoslik haqida hikoya qiluvchi muzeydan iborat yodgorlik majmuasi 1998-yilda keskin kengaytirilgan.",
        "Имам аль-Бухари (810–870) родился в Бухаре и стал самым известным собирателем хадисов — высказываний и деяний пророка Мухаммеда. Его труд «Сахих аль-Бухари» считается у суннитов самым достоверным сводом после Корана. Он умер в селении Хартанг близ Самарканда. Мемориальный комплекс с мечетью, мавзолеем и музеем о его жизни и изучении хадисов был значительно расширен в 1998 году.",
        "L'imam al-Boukhari (810–870), né à Boukhara, devint le plus célèbre collecteur de hadiths, les paroles et actes du prophète Mahomet. Son recueil Sahih al-Boukhari est considéré par les musulmans sunnites comme le plus authentique après le Coran. Il mourut dans le village de Khartang, près de Samarcande. Le complexe commémoratif, avec une mosquée, son tombeau et un musée sur sa vie et l'étude du hadith, a été considérablement agrandi en 1998.",
        "Imam al-Buchari (810–870) wurde in Buchara geboren und wurde zum berühmtesten Sammler von Hadithen, den Aussprüchen und Handlungen des Propheten Mohammed. Sein Werk Sahih al-Buchari gilt unter sunnitischen Muslimen als die verlässlichste Sammlung nach dem Koran. Er starb im Dorf Chartang bei Samarkand. Die Gedenkstätte mit Moschee, Grab und einem Museum über sein Leben und die Hadith-Wissenschaft wurde 1998 stark erweitert.",
        "El imán al-Bujari (810–870) nació en Bujará y se convirtió en el recopilador de hadices más célebre: dichos y actos del profeta Mahoma. Su obra Sahih al-Bujari es considerada por los musulmanes suníes la más fiable después del Corán. Murió en la aldea de Jartang, cerca de Samarcanda. El complejo conmemorativo, con mezquita, su tumba y un museo sobre su vida y el estudio del hadiz, se amplió mucho en 1998."),
    # ---- keepsake texts
    PLACES[0][5]: (
        "Oltin soatda Registon koshinlari ko'kdan olovga aylanadi va bir lahza butun maydon faqat siz uchun ochilgan zargarlik sandig'iga o'xshab ketadi.",
        "В золотой час изразцы Регистана переходят от синего к пламенному, и на мгновение вся площадь кажется шкатулкой с драгоценностями, раскрытой только для вас.",
        "À l'heure dorée, les faïences du Registan passent du bleu à la flamme, et l'espace d'un instant la place entière ressemble à un écrin ouvert rien que pour vous.",
        "In der goldenen Stunde wechseln die Fliesen des Registan von Blau zu Flammenrot, und für einen Augenblick wirkt der ganze Platz wie ein Schmuckkästchen, das nur für Sie geöffnet wurde.",
        "A la hora dorada, los azulejos del Registán pasan del azul a la llama y, por un instante, toda la plaza parece un joyero abierto solo para usted."),
    PLACES[1][5]: (
        "Yomg'irdan keyingi osmon rangidagi gumbaz ostida dunyoni larzaga solgan sarkarda sukunatda uxlaydi. Zarhal yarim qorong'ulikda bir lahza to'xtang — tarix nafas olayotganini deyarli eshitasiz.",
        "Под куполом цвета неба после дождя в тишине спит император, потрясший мир. Постойте минуту в позолоченном полумраке — и вы почти услышите дыхание истории.",
        "Sous un dôme couleur de ciel après la pluie, un empereur qui a fait trembler le monde repose en silence. Arrêtez-vous un instant dans la pénombre dorée : vous entendrez presque l'histoire respirer.",
        "Unter einer Kuppel in der Farbe des Himmels nach dem Regen schläft in Stille ein Herrscher, der die Welt erschütterte. Verweilen Sie im goldenen Halbdunkel, und Sie hören die Geschichte fast atmen.",
        "Bajo una cúpula del color del cielo tras la lluvia duerme en silencio un emperador que hizo temblar al mundo. Deténgase un instante en la penumbra dorada y casi oirá respirar a la historia."),
    PLACES[2][5]: (
        "Asrlar sinovidan o'tgan bo'lsa-da, uning ulkan ravoqlari hamon osmonga intiladi. Minglab kishi ibodat qilgan keng hovlidan o'ting va sukunat sizga shuhratparastlik qanday ovozda ekanini aytsin.",
        "Даже изрезанные веками, её могучие арки по-прежнему тянутся к небу. Пройдите по огромному двору, где молились тысячи людей, и пусть тишина расскажет, как звучит честолюбие.",
        "Même éprouvées par les siècles, ses grandes arcades se tendent encore vers le ciel. Traversez la vaste cour où des milliers de fidèles ont prié, et laissez le silence vous dire à quoi ressemble l'ambition.",
        "Selbst von Jahrhunderten gezeichnet, streben ihre großen Bögen noch immer zum Himmel. Durchqueren Sie den weiten Hof, in dem Tausende beteten, und lassen Sie die Stille erzählen, wie sich Ehrgeiz anhört.",
        "Aun curtidos por los siglos, sus grandes arcos siguen alzándose hacia el cielo. Cruce el vasto patio donde rezaron miles de personas y deje que el silencio le diga cómo suena la ambición."),
    PLACES[3][5]: (
        "Issiq non, asalli shirinliklar va sotuvchilarning ovozi: bu yerda Samarqand karvonlar Xitoydan kelgan zamondagidek savdo qiladi. Tatib ko'ring va shaharni o'zingiz bilan olib keting.",
        "Тёплый хлеб, медовые сладости и зазывные голоса торговцев: здесь Самарканд торгует так же, как во времена караванов из Китая. Попробуйте на вкус — и увезите город с собой.",
        "Du pain chaud, des douceurs au miel et les appels des marchands : ici, Samarcande commerce comme au temps des caravanes venues de Chine. Goûtez, et emportez la ville avec vous.",
        "Warmes Brot, honigsüße Leckereien und die Rufe der Händler: Hier handelt Samarkand noch wie zu der Zeit, als Karawanen aus China eintrafen. Kosten Sie und nehmen Sie die Stadt mit nach Hause.",
        "Pan caliente, dulces de miel y los pregones de los vendedores: aquí Samarcanda comercia como cuando llegaban las caravanas de China. Pruebe un bocado y llévese la ciudad a casa."),
    PLACES[4][5]: (
        "Ko'k zinapoya, har bir qadam avvalgisidan sokinroq. Olti yuz yildan beri rangini yo'qotmagan koshinlar ostida, o'tganlar zamonasining eng go'zal san'ati bilan ulug'langan ko'cha bo'ylab yurasiz.",
        "Лестница синевы, и каждый шаг тише предыдущего. Под плиткой, шестьсот лет хранящей свой цвет, вы идёте по улице, где ушедших чтили лучшим искусством эпохи.",
        "Un escalier de bleu, chaque marche plus silencieuse que la précédente. Sous des faïences qui gardent leur couleur depuis six cents ans, vous marchez dans une rue où l'on honorait les défunts par le plus bel art de l'époque.",
        "Eine Treppe aus Blau, jede Stufe leiser als die vorige. Unter Fliesen, die seit sechshundert Jahren ihre Farbe halten, gehen Sie durch eine Straße, in der die Verstorbenen mit der feinsten Kunst ihrer Zeit geehrt wurden.",
        "Una escalera de azul, cada peldaño más silencioso que el anterior. Bajo azulejos que conservan su color desde hace seiscientos años, camina por una calle donde se honraba a los difuntos con el mejor arte de la época."),
    PLACES[5][5]: (
        "Karvonlar dam olgan joyda endi chiroqlar va favvoralar sizni kutib oladi. Ko'chalarni aylaning, ustaning ishini tomosha qiling va eski yo'l sayohatchilarni hamon chorlayotganini his qiling.",
        "Там, где отдыхали караваны, вас встречают фонари и фонтаны. Пройдитесь по улочкам, посмотрите на работу мастера и почувствуйте, как древняя дорога всё ещё зовёт путников.",
        "Là où les caravanes faisaient halte, lanternes et fontaines vous accueillent désormais. Flânez dans les ruelles, regardez un artisan travailler et sentez comment l'ancienne route continue d'appeler les voyageurs.",
        "Wo einst Karawanen rasteten, empfangen Sie nun Laternen und Brunnen. Schlendern Sie durch die Gassen, sehen Sie einem Handwerker zu und spüren Sie, wie die alte Straße Reisende weiter einlädt.",
        "Donde antes descansaban las caravanas, hoy le reciben farolas y fuentes. Pasee por las callejuelas, vea trabajar a un artesano y sienta cómo el viejo camino sigue invitando a los viajeros."),
    PLACES[6][5]: (
        "Teleskoplar paydo bo'lishidan ancha oldin bir podshoh Samarqand yaqinidagi tepalikdan osmonga boqdi va bino kattaligidagi asbob bilan yulduzlarni sanadi. Uning egri xandaqida turing — siz osmon haqidagi qadimiy orzu ichida turgan bo'lasiz.",
        "Задолго до телескопов правитель взглянул с холма под Самаркандом и сосчитал звёзды прибором размером со здание. Встаньте в его изогнутую траншею — и вы окажетесь внутри древней мечты о небе.",
        "Bien avant les télescopes, un roi leva les yeux depuis une colline près de Samarcande et compta les étoiles avec un instrument grand comme un édifice. Tenez-vous dans sa tranchée courbe : vous serez à l'intérieur d'un très ancien rêve du ciel.",
        "Lange vor den Teleskopen blickte ein König von einem Hügel bei Samarkand zum Himmel und zählte die Sterne mit einem Instrument von der Größe eines Gebäudes. Stehen Sie in seinem gebogenen Graben, und Sie stehen im Inneren eines uralten Traums vom Himmel.",
        "Mucho antes de los telescopios, un rey miró al cielo desde una colina cercana a Samarcanda y contó las estrellas con un instrumento del tamaño de un edificio. Colóquese en su zanja curva y estará dentro de un antiguo sueño del cielo."),
    PLACES[7][5]: (
        "Sokin bog'lar, zangori gumbazli ibodatxona va buyuk olim orom topgan qishloq: bu joy sukunat uchun yaratilgan. Yo'lning shoshqaloqligini darvoza oldida qoldiring va undagi xotirjamlikdan bir parchasini uyingizga olib keting.",
        "Тихие сады, мечеть с синим куполом и селение, где обрёл покой великий учёный: это место для тишины. Оставьте суету дороги у ворот и увезите домой частицу его спокойствия.",
        "Des jardins paisibles, une salle de prière à dôme bleu et un village où un grand savant est venu reposer : c'est un lieu de calme. Laissez la hâte de la route à la porte et emportez chez vous un peu de sa sérénité.",
        "Stille Gärten, ein Gebetsraum mit blauer Kuppel und ein Dorf, in dem ein großer Gelehrter zur Ruhe kam: ein Ort der Stille. Lassen Sie die Hast der Straße am Tor zurück und nehmen Sie ein wenig von seiner Ruhe mit nach Hause.",
        "Jardines tranquilos, una sala de oración de cúpula azul y una aldea donde un gran sabio vino a descansar: un lugar para el silencio. Deje la prisa del camino en la puerta y llévese a casa un poco de su calma."),
}
PHRASES.update(TEXT)
