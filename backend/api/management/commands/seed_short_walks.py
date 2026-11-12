"""Short walks in Samarkand (2 to 4 hours), shown under the three multi-day tours on the home page.

Kind of walk, length and price follow the same walks on GetYourGuide (Samarkand search, November 2026); the owner's rule is
the GetYourGuide price minus 1 US dollar. The texts are ALI TRAVEL's own, the photos are the owner's (media/tours/samarkand-short) and free-licence pictures from Wikimedia Commons.
Columns of the translations: uz, ru, fr, de, es.
"""

LANGS = ("uz", "ru", "fr", "de", "es")
PHOTOS = "/media/tours/samarkand-short/"


def commons(name):
    from urllib.parse import quote
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(name)}?width=1280"


CATEGORY = {
    "Culture": ("Madaniyat", "Культура", "Culture", "Kultur", "Cultura"),
    "Food": ("Taomlar", "Еда", "Gastronomie", "Essen", "Gastronomía"),
}
DURATION = {
    "2 hours": ("2 soat", "2 часа", "2 heures", "2 Stunden", "2 horas"),
    "3 hours": ("3 soat", "3 часа", "3 heures", "3 Stunden", "3 horas"),
    "3.5 hours": ("3,5 soat", "3,5 часа", "3 h 30", "3,5 Stunden", "3,5 horas"),
    "4 hours": ("4 soat", "4 часа", "4 heures", "4 Stunden", "4 horas"),
}
GROUP = {"Small group": ("Kichik guruh", "Малая группа", "Petit groupe", "Kleingruppe", "Grupo reducido")}
ITEM = {
    "Local guide": ("Mahalliy gid", "Местный гид", "Guide local", "Lokaler Guide", "Guía local"),
    "Tasting of dried fruit, nuts and halva at the bazaar": ("Bozorda quruq meva, yong'oq va holva tatib ko'rish", "Дегустация сухофруктов, орехов и халвы на базаре",
        "Dégustation de fruits secs, noix et halva au bazar", "Kostprobe von Trockenobst, Nüssen und Halwa auf dem Basar", "Degustación de frutos secos y halva en el bazar"),
    "10 tastings of Samarkand food": ("Samarqand taomlaridan 10 xil ta'm", "10 дегустаций самаркандской еды", "10 dégustations de spécialités de Samarcande",
        "10 Kostproben der Küche Samarkands", "10 degustaciones de comida de Samarcanda"),
    "Lunch with plov": ("Palovli tushlik", "Обед с пловом", "Déjeuner avec plov", "Mittagessen mit Plov", "Almuerzo con plov"),
    "Green tea": ("Ko'k choy", "Зелёный чай", "Thé vert", "Grüner Tee", "Té verde"),
    "Stories and legends of Samarkand": ("Samarqand tarixi va rivoyatlari", "Истории и легенды Самарканда", "Histoires et légendes de Samarcande",
        "Geschichten und Legenden Samarkands", "Historias y leyendas de Samarcanda"),
    "Tea break at a chaikhana": ("Choyxonada choy tanaffusi", "Чайная пауза в чайхане", "Pause thé dans une tchaïkhana", "Teepause in einer Teestube", "Pausa para el té en una chaijana"),
    "Street food tastings in the evening": ("Kechki ko'cha taomlarini tatib ko'rish", "Вечерняя дегустация уличной еды", "Dégustations de street food le soir",
        "Streetfood-Kostproben am Abend", "Degustaciones de comida callejera por la noche"),
    "Visit to a family home in a mahalla": ("Mahalladagi oila xonadoniga tashrif", "Визит в семью в махалле", "Visite d'une famille dans une mahalla",
        "Besuch bei einer Familie in einer Mahalla", "Visita a una familia en una mahalla"),
    "Bread from the tandir, tea and a home-cooked lunch": ("Tandir noni, choy va uy taomidan tushlik", "Лепёшка из тандыра, чай и домашний обед",
        "Pain du tandir, thé et déjeuner maison", "Brot aus dem Tandir, Tee und hausgemachtes Mittagessen", "Pan del tandir, té y almuerzo casero"),
    "Hotel pickup and drop-off": ("Mehmonxonadan olib ketish va qaytarish", "Трансфер из отеля и обратно", "Prise en charge et retour à l'hôtel",
        "Abholung und Rückfahrt zum Hotel", "Recogida y regreso al hotel"),
    # not included
    "Entrance tickets": ("Kirish chiptalari", "Входные билеты", "Billets d'entrée", "Eintrittskarten", "Entradas"),
    "Food and drinks": ("Taom va ichimliklar", "Еда и напитки", "Repas et boissons", "Essen und Getränke", "Comida y bebidas"),
    "Hotel pickup (available on request)": ("Mehmonxonadan olib ketish (so'rov bo'yicha)", "Трансфер из отеля (по запросу)", "Prise en charge à l'hôtel (sur demande)",
        "Hotelabholung (auf Anfrage)", "Recogida en el hotel (bajo petición)"),
    "Tips (optional)": ("Choychaqa (ixtiyoriy)", "Чаевые (по желанию)", "Pourboires (facultatif)", "Trinkgeld (freiwillig)", "Propinas (opcional)"),
}
MEETING = {
    "Your hotel in Samarkand": ("Samarqanddagi mehmonxonangiz", "Ваш отель в Самарканде", "Votre hôtel à Samarcande", "Ihr Hotel in Samarkand", "Su hotel en Samarcanda"),
    "Bibi-Khanym Mosque, main gate": ("Bibixonim masjidi, asosiy darvoza", "Мечеть Биби-Ханым, главные ворота", "Mosquée Bibi-Khanym, portail principal",
        "Bibi-Chanum-Moschee, Haupttor", "Mezquita de Bibi-Khanym, puerta principal"),
    "Registan Square, main entrance": ("Registon maydoni, asosiy kirish", "Площадь Регистан, главный вход", "Place du Régistan, entrée principale",
        "Registan-Platz, Haupteingang", "Plaza del Registán, entrada principal"),
    "Registan Square, by the fountain": ("Registon maydoni, favvora yonida", "Площадь Регистан, у фонтана", "Place du Régistan, près de la fontaine",
        "Registan-Platz, am Brunnen", "Plaza del Registán, junto a la fuente"),
}

# GetYourGuide price (USD per person) -> ours = that minus 1
WALKS = [
    dict(slug="samarkand-siab-bazaar-bibi-khanym-walk", category="Culture", duration="2 hours", gyg_price=15, max=12,
         cover="bibi-khanym.jpg", gallery=["siab-dried-fruit.jpg", "dastarkhan-sweets.jpg"],
         included=["Local guide", "Tasting of dried fruit, nuts and halva at the bazaar", "Stories and legends of Samarkand"],
         excluded=["Entrance tickets", "Hotel pickup (available on request)", "Tips (optional)"], meeting="Bibi-Khanym Mosque, main gate",
         text={
             "en": ("Samarkand: Siab Bazaar and Bibi-Khanym Mosque Walk", "Two hours at the heart of old Samarkand: Tamerlane's great mosque and the city's busiest bazaar.",
                    "Start under the giant portal of the Bibi-Khanym Mosque, built by Amir Timur after his campaign to India, and hear the legend of the queen it is named after. Then cross the street into Siab Bazaar, where Samarkand has bought its bread, melons, spices and sweets for centuries. Your guide shows you how to choose dried fruit and nuts, and you taste halva and fresh non straight from the stalls.",
                    ["Bibi-Khanym Mosque and its legend", "Siab Bazaar, the oldest market of Samarkand", "Tasting of dried fruit, nuts and halva", "Small group, easy pace"]),
             "uz": ("Samarqand: Siyob bozori va Bibixonim masjidi bo'ylab sayr", "Eski Samarqand qalbida ikki soat: Amir Temurning ulug' masjidi va shaharning eng gavjum bozori.",
                    "Sayr Amir Temur Hindiston yurishidan keyin qurdirgan Bibixonim masjidining ulkan peshtoqi ostida boshlanadi, masjidga nom bergan malika haqidagi rivoyatni eshitasiz. So'ng ko'chaning narigi tomonidagi Siyob bozoriga o'tasiz: Samarqand asrlar davomida noni, qovuni, ziravorlari va shirinliklarini shu yerdan oladi. Gid quruq meva va yong'oqni qanday tanlashni ko'rsatadi, rastalardan holva va issiq non tatib ko'rasiz.",
                    ["Bibixonim masjidi va uning rivoyati", "Samarqandning eng qadimiy bozori Siyob", "Quruq meva, yong'oq va holva tatib ko'rish", "Kichik guruh, shoshilmasdan"]),
             "ru": ("Самарканд: прогулка по базару Сиаб и мечети Биби-Ханым", "Два часа в сердце старого Самарканда: великая мечеть Тамерлана и самый оживлённый базар города.",
                    "Прогулка начинается под гигантским порталом мечети Биби-Ханым, построенной Амиром Темуром после индийского похода, — вы услышите легенду о царице, чьё имя она носит. Затем вы перейдёте улицу и окажетесь на базаре Сиаб, где Самарканд веками покупает хлеб, дыни, специи и сладости. Гид покажет, как выбирать сухофрукты и орехи, а вы попробуете халву и горячую лепёшку прямо с прилавка.",
                    ["Мечеть Биби-Ханым и её легенда", "Сиаб — старейший базар Самарканда", "Дегустация сухофруктов, орехов и халвы", "Малая группа, спокойный темп"]),
             "fr": ("Samarcande : bazar Siab et mosquée Bibi-Khanym à pied", "Deux heures au cœur du vieux Samarcande : la grande mosquée de Tamerlan et le bazar le plus animé de la ville.",
                    "Départ sous l'immense portail de la mosquée Bibi-Khanym, bâtie par Amir Timour après sa campagne en Inde, avec la légende de la reine qui lui donne son nom. Traversez ensuite la rue jusqu'au bazar Siab, où Samarcande achète depuis des siècles son pain, ses melons, ses épices et ses douceurs. Votre guide vous apprend à choisir fruits secs et noix, et vous goûtez la halva et le pain chaud des étals.",
                    ["La mosquée Bibi-Khanym et sa légende", "Le bazar Siab, le plus ancien de Samarcande", "Dégustation de fruits secs, noix et halva", "Petit groupe, rythme tranquille"]),
             "de": ("Samarkand: Siab-Basar und Bibi-Chanum-Moschee zu Fuß", "Zwei Stunden im Herzen des alten Samarkand: Timurs große Moschee und der lebhafteste Basar der Stadt.",
                    "Start ist unter dem riesigen Portal der Bibi-Chanum-Moschee, die Amir Timur nach seinem Indienfeldzug bauen ließ, mit der Legende der Königin, nach der sie benannt ist. Dann geht es über die Straße in den Siab-Basar, wo Samarkand seit Jahrhunderten Brot, Melonen, Gewürze und Süßes kauft. Ihr Guide zeigt Ihnen, wie man Trockenobst und Nüsse auswählt, und Sie probieren Halwa und warmes Fladenbrot direkt vom Stand.",
                    ["Die Bibi-Chanum-Moschee und ihre Legende", "Siab, der älteste Basar Samarkands", "Kostprobe von Trockenobst, Nüssen und Halwa", "Kleingruppe, gemütliches Tempo"]),
             "es": ("Samarcanda: bazar Siab y mezquita de Bibi-Khanym a pie", "Dos horas en el corazón de la vieja Samarcanda: la gran mezquita de Tamerlán y el bazar más animado de la ciudad.",
                    "Se empieza bajo el enorme portal de la mezquita de Bibi-Khanym, construida por Amir Timur tras su campaña en la India, con la leyenda de la reina que le da nombre. Después se cruza la calle hasta el bazar Siab, donde Samarcanda compra desde hace siglos su pan, melones, especias y dulces. El guía le enseña a elegir frutos secos y usted prueba halva y pan caliente en los puestos.",
                    ["La mezquita de Bibi-Khanym y su leyenda", "Siab, el bazar más antiguo de Samarcanda", "Degustación de frutos secos y halva", "Grupo reducido, ritmo tranquilo"]),
         }),
    dict(slug="samarkand-food-and-culture-walk", category="Food", duration="3 hours", gyg_price=90, max=10,
         cover="dastarkhan-sweets.jpg", gallery=["siab-dried-fruit.jpg", "registan-square.jpg"],
         included=["Local guide", "10 tastings of Samarkand food", "Lunch with plov", "Green tea"],
         excluded=["Entrance tickets", "Hotel pickup (available on request)", "Tips (optional)"], meeting="Registan Square, main entrance",
         text={
             "en": ("Samarkand: Food and Culture Walk with 10 Tastings and Lunch", "Three hours of Samarkand flavours: bread from the tandir, sweets, dried fruit, samsa and a plov lunch.",
                    "Walk from the Registan into the old quarters with a local guide and eat your way through the city. You try ten things Samarkand is famous for, from its round non bread baked in a clay tandir to samsa, navat crystal sugar, halva, dried apricots and nuts. Between the tastings your guide explains the customs of the Uzbek dastarkhan and the history of the streets you walk. The walk ends with a plov lunch and green tea.",
                    ["10 tastings of Samarkand food", "Samarkand non from the clay tandir", "Plov lunch with green tea", "Customs of the Uzbek table"]),
             "uz": ("Samarqand: 10 xil ta'm va tushlik bilan taom va madaniyat sayri", "Samarqand ta'mlari bilan uch soat: tandir noni, shirinliklar, quruq meva, somsa va palovli tushlik.",
                    "Mahalliy gid bilan Registondan eski mahallalarga yo'l olasiz va shaharni ta'mlari orqali tanishasiz. Samarqand mashhur bo'lgan o'nta narsani tatib ko'rasiz: loy tandirda yopilgan dumaloq non, somsa, novvot, holva, o'rik qoqi va yong'oq. Ta'mlar orasida gid o'zbek dasturxoni odatlari va siz yurgan ko'chalar tarixini so'zlab beradi. Sayr palov va ko'k choy bilan tushlik bilan yakunlanadi.",
                    ["Samarqand taomlaridan 10 xil ta'm", "Loy tandirdan Samarqand noni", "Palov va ko'k choy bilan tushlik", "O'zbek dasturxoni odatlari"]),
             "ru": ("Самарканд: гастрономическая прогулка, 10 дегустаций и обед", "Три часа вкусов Самарканда: хлеб из тандыра, сладости, сухофрукты, самса и обед с пловом.",
                    "С местным гидом вы пройдёте от Регистана в старые кварталы и познакомитесь с городом через его кухню. Вы попробуете десять блюд, которыми славится Самарканд: круглую лепёшку из глиняного тандыра, самсу, нават, халву, курагу и орехи. Между дегустациями гид расскажет об обычаях узбекского дастархана и истории улиц, по которым вы идёте. Прогулка заканчивается обедом с пловом и зелёным чаем.",
                    ["10 дегустаций самаркандской еды", "Самаркандская лепёшка из тандыра", "Обед с пловом и зелёным чаем", "Обычаи узбекского стола"]),
             "fr": ("Samarcande : balade gourmande avec 10 dégustations et déjeuner", "Trois heures de saveurs de Samarcande : pain du tandir, douceurs, fruits secs, samsa et déjeuner au plov.",
                    "Partez du Régistan vers les vieux quartiers avec un guide local et découvrez la ville par sa cuisine. Vous goûtez dix spécialités qui font la fierté de Samarcande : le pain rond cuit dans un tandir d'argile, la samsa, le navat, la halva, les abricots secs et les noix. Entre deux dégustations, votre guide raconte les coutumes du dastarkhan ouzbek et l'histoire des rues. La balade se termine par un déjeuner de plov et du thé vert.",
                    ["10 dégustations de spécialités", "Le pain de Samarcande cuit au tandir", "Déjeuner au plov et thé vert", "Les coutumes de la table ouzbèke"]),
             "de": ("Samarkand: Food- und Kulturspaziergang mit 10 Kostproben und Mittagessen", "Drei Stunden Samarkand zum Schmecken: Brot aus dem Tandir, Süßes, Trockenobst, Samsa und Plov zum Mittag.",
                    "Mit einem lokalen Guide gehen Sie vom Registan in die Altstadtviertel und lernen die Stadt über ihre Küche kennen. Sie probieren zehn Spezialitäten, für die Samarkand berühmt ist: das runde Fladenbrot aus dem Lehmofen, Samsa, Navat-Kandiszucker, Halwa, getrocknete Aprikosen und Nüsse. Zwischen den Kostproben erzählt Ihr Guide von den Bräuchen am usbekischen Dastarchan und der Geschichte der Gassen. Zum Abschluss gibt es Plov und grünen Tee.",
                    ["10 Kostproben der Küche Samarkands", "Samarkander Brot aus dem Lehmofen", "Plov zum Mittag mit grünem Tee", "Bräuche am usbekischen Tisch"]),
             "es": ("Samarcanda: paseo gastronómico con 10 degustaciones y almuerzo", "Tres horas de sabores de Samarcanda: pan del tandir, dulces, frutos secos, samsa y almuerzo con plov.",
                    "Desde el Registán se adentra con un guía local en los barrios antiguos y conoce la ciudad a través de su cocina. Probará diez cosas por las que Samarcanda es famosa: el pan redondo del horno tandir, la samsa, el navat, la halva, los albaricoques secos y las nueces. Entre bocado y bocado, el guía le cuenta las costumbres del dastarján uzbeko y la historia de las calles. El paseo termina con un almuerzo de plov y té verde.",
                    ["10 degustaciones de comida local", "Pan de Samarcanda del horno tandir", "Almuerzo con plov y té verde", "Costumbres de la mesa uzbeka"]),
         }),
    dict(slug="samarkand-bazaar-and-old-town-stories-walk", category="Culture", duration="4 hours", gyg_price=12, max=15,
         cover="costume-sher-dor.jpg", gallery=["registan-square.jpg", "group-tilla-kori.jpg", "shah-i-zinda.jpg"],
         included=["Local guide", "Stories and legends of Samarkand"],
         excluded=["Entrance tickets", "Food and drinks", "Hotel pickup (available on request)", "Tips (optional)"], meeting="Registan Square, by the fountain",
         text={
             "en": ("Samarkand: Bazaar and Old Town Walk with Stories", "Four hours on foot from the Registan to Shah-i-Zinda, through the bazaar and the old town, with the stories behind every wall.",
                    "Meet your guide at the Registan and hear how three madrasas turned a sandy square into the most famous place of the Silk Road. Step into the golden courtyard of Tilla-Kori, walk the old streets to the Bibi-Khanym Mosque and wander through Siab Bazaar. The walk ends at Shah-i-Zinda, the avenue of turquoise mausoleums where Samarkand keeps its oldest legend. On the way you hear about Amir Timur, Ulugh Beg and the craftsmen who covered the city in tiles.",
                    ["Registan and the golden courtyard of Tilla-Kori", "Bibi-Khanym Mosque and Siab Bazaar", "Shah-i-Zinda, the avenue of turquoise mausoleums", "Legends of Amir Timur and Ulugh Beg"]),
             "uz": ("Samarqand: Bozor va Eski shahar bo'ylab hikoyali sayr", "Registondan Shohi Zindagacha, bozor va eski shahar orqali to'rt soatlik piyoda sayr va har bir devor ortidagi hikoyalar.",
                    "Gid bilan Registonda uchrashasiz va uch madrasa qumli maydonni Ipak yo'lining eng mashhur joyiga qanday aylantirganini eshitasiz. Tillakori madrasasining oltin hovlisiga kirasiz, eski ko'chalar bo'ylab Bibixonim masjidigacha yurasiz va Siyob bozorini aylanasiz. Sayr Samarqandning eng qadimiy rivoyatini saqlagan feruza maqbaralar ko'chasi Shohi Zindada tugaydi. Yo'lda Amir Temur, Ulug'bek va shaharni koshinlar bilan bezagan ustalar haqida eshitasiz.",
                    ["Registon va Tillakorining oltin hovlisi", "Bibixonim masjidi va Siyob bozori", "Feruza maqbaralar ko'chasi Shohi Zinda", "Amir Temur va Ulug'bek haqidagi rivoyatlar"]),
             "ru": ("Самарканд: прогулка по базару и Старому городу с рассказами", "Четыре часа пешком от Регистана до Шахи-Зинды через базар и старый город — с историями за каждой стеной.",
                    "Встреча с гидом на Регистане: вы узнаете, как три медресе превратили песчаную площадь в самое известное место Шёлкового пути. Вы зайдёте в золотой двор медресе Тилля-Кари, пройдёте старыми улицами к мечети Биби-Ханым и погуляете по базару Сиаб. Прогулка заканчивается у Шахи-Зинды — улицы бирюзовых мавзолеев, где Самарканд хранит свою древнейшую легенду. По пути вы услышите об Амире Темуре, Улугбеке и мастерах, покрывших город изразцами.",
                    ["Регистан и золотой двор Тилля-Кари", "Мечеть Биби-Ханым и базар Сиаб", "Шахи-Зинда — улица бирюзовых мавзолеев", "Легенды об Амире Темуре и Улугбеке"]),
             "fr": ("Samarcande : bazar et vieille ville, balade avec histoires", "Quatre heures à pied du Régistan à Chah-i-Zinda, par le bazar et la vieille ville, avec les histoires derrière chaque mur.",
                    "Rendez-vous au Régistan, où votre guide raconte comment trois madrasas ont fait d'une place de sable le lieu le plus célèbre de la Route de la soie. Entrez dans la cour dorée de Tilla-Kari, suivez les vieilles rues jusqu'à la mosquée Bibi-Khanym et flânez dans le bazar Siab. La balade s'achève à Chah-i-Zinda, l'allée des mausolées turquoise où Samarcande garde sa plus ancienne légende. En chemin : Amir Timour, Ulugh Beg et les artisans qui ont couvert la ville de faïence.",
                    ["Le Régistan et la cour dorée de Tilla-Kari", "La mosquée Bibi-Khanym et le bazar Siab", "Chah-i-Zinda, l'allée des mausolées turquoise", "Légendes d'Amir Timour et d'Ulugh Beg"]),
             "de": ("Samarkand: Basar und Altstadt zu Fuß, mit Geschichten", "Vier Stunden zu Fuß vom Registan bis Schah-i-Sinda, durch Basar und Altstadt, mit den Geschichten hinter jeder Mauer.",
                    "Treffpunkt ist der Registan, wo Ihr Guide erzählt, wie drei Medresen einen Sandplatz zum berühmtesten Ort der Seidenstraße machten. Sie betreten den goldenen Hof der Tilla-Kari, gehen durch alte Gassen zur Bibi-Chanum-Moschee und schlendern über den Siab-Basar. Der Spaziergang endet in Schah-i-Sinda, der Gasse der türkisfarbenen Mausoleen, in der Samarkand seine älteste Legende bewahrt. Unterwegs hören Sie von Amir Timur, Ulugh Beg und den Handwerkern, die die Stadt mit Fliesen bedeckten.",
                    ["Registan und der goldene Hof der Tilla-Kari", "Bibi-Chanum-Moschee und Siab-Basar", "Schah-i-Sinda, die Gasse der türkisfarbenen Mausoleen", "Legenden von Amir Timur und Ulugh Beg"]),
             "es": ("Samarcanda: bazar y casco antiguo a pie, con historias", "Cuatro horas a pie del Registán a Shah-i-Zinda, por el bazar y el casco antiguo, con las historias de cada muro.",
                    "Se encuentra con su guía en el Registán y descubre cómo tres madrazas convirtieron una plaza de arena en el lugar más famoso de la Ruta de la Seda. Entra en el patio dorado de Tilla-Kari, recorre las calles antiguas hasta la mezquita de Bibi-Khanym y pasea por el bazar Siab. El paseo termina en Shah-i-Zinda, la avenida de mausoleos turquesa donde Samarcanda guarda su leyenda más antigua. Por el camino oirá hablar de Amir Timur, Ulugh Beg y los artesanos que cubrieron la ciudad de azulejos.",
                    ["El Registán y el patio dorado de Tilla-Kari", "La mezquita de Bibi-Khanym y el bazar Siab", "Shah-i-Zinda, la avenida de mausoleos turquesa", "Leyendas de Amir Timur y Ulugh Beg"]),
         }),
    dict(slug="samarkand-highlights-walk-tea-break", category="Culture", duration="3.5 hours", gyg_price=12, max=10,
         cover=commons("Gur-e Amir 01.jpg"), gallery=["registan-square.jpg", "group-tilla-kori.jpg", "shah-i-zinda.jpg"],
         included=["Local guide", "Tea break at a chaikhana", "Stories and legends of Samarkand"],
         excluded=["Entrance tickets", "Hotel pickup (available on request)", "Tips (optional)"], meeting="Registan Square, by the fountain",
         text={
             "en": ("Samarkand Highlights Walk: Gur-e-Amir, Registan and Shah-i-Zinda with a Tea Break", "The five great sights of Samarkand on foot in one morning, with a break for green tea in a chaikhana.",
                    "Begin at Gur-e-Amir, the ribbed blue dome over the tomb of Amir Timur, then walk to the Registan and its three madrasas. Continue along the pedestrian street to the Bibi-Khanym Mosque and the Siab Bazaar, where you stop for green tea and sweets in a chaikhana. The walk ends at Shah-i-Zinda, the street of turquoise mausoleums. Your guide brings the Timurid age to life with stories at every stop.",
                    ["Gur-e-Amir, the tomb of Amir Timur", "Registan and its three madrasas", "Tea break in a chaikhana by Siab Bazaar", "Shah-i-Zinda at the end of the walk"]),
             "uz": ("Samarqandning asosiy joylari: Go'ri Amir, Registon va Shohi Zinda, choy tanaffusi bilan", "Samarqandning beshta mashhur yodgorligi bir ertalabda piyoda, choyxonada ko'k choy tanaffusi bilan.",
                    "Sayr Amir Temur maqbarasi ustidagi qovurg'ali ko'k gumbaz — Go'ri Amirdan boshlanadi, so'ng Registon va uning uch madrasasiga borasiz. Piyodalar ko'chasi bo'ylab Bibixonim masjidi va Siyob bozorigacha yurasiz, choyxonada ko'k choy va shirinliklar uchun to'xtaysiz. Sayr feruza maqbaralar ko'chasi Shohi Zindada tugaydi. Gid har bir to'xtashda Temuriylar davrini hikoyalar bilan jonlantiradi.",
                    ["Go'ri Amir — Amir Temur maqbarasi", "Registon va uning uch madrasasi", "Siyob bozori yonidagi choyxonada choy tanaffusi", "Sayr oxirida Shohi Zinda"]),
             "ru": ("Главное в Самарканде: Гур-Эмир, Регистан и Шахи-Зинда с чайной паузой", "Пять главных памятников Самарканда пешком за одно утро, с зелёным чаем в чайхане.",
                    "Прогулка начинается у Гур-Эмира — ребристого голубого купола над гробницей Амира Темура, затем вы идёте к Регистану и его трём медресе. Дальше по пешеходной улице — к мечети Биби-Ханым и базару Сиаб, где в чайхане вас ждут зелёный чай и сладости. Прогулка заканчивается у Шахи-Зинды, улицы бирюзовых мавзолеев. Гид оживляет эпоху Тимуридов рассказами на каждой остановке.",
                    ["Гур-Эмир — гробница Амира Темура", "Регистан и три его медресе", "Чайная пауза у базара Сиаб", "Шахи-Зинда в конце прогулки"]),
             "fr": ("L'essentiel de Samarcande : Gour-Emir, Régistan et Chah-i-Zinda avec pause thé", "Les cinq grands sites de Samarcande à pied en une matinée, avec une pause thé vert dans une tchaïkhana.",
                    "Départ au Gour-Emir, le dôme bleu côtelé au-dessus du tombeau d'Amir Timour, puis marche jusqu'au Régistan et ses trois madrasas. Continuez par la rue piétonne jusqu'à la mosquée Bibi-Khanym et au bazar Siab, avec une pause thé vert et douceurs dans une tchaïkhana. La balade se termine à Chah-i-Zinda, l'allée des mausolées turquoise. À chaque arrêt, votre guide fait revivre l'époque timouride.",
                    ["Le Gour-Emir, tombeau d'Amir Timour", "Le Régistan et ses trois madrasas", "Pause thé près du bazar Siab", "Chah-i-Zinda pour finir"]),
             "de": ("Samarkands Highlights: Gur-Emir, Registan und Schah-i-Sinda mit Teepause", "Die fünf großen Sehenswürdigkeiten Samarkands zu Fuß an einem Vormittag, mit grünem Tee in einer Teestube.",
                    "Start ist am Gur-Emir, der gerippten blauen Kuppel über dem Grab Amir Timurs, dann geht es zum Registan mit seinen drei Medresen. Über die Fußgängerstraße erreichen Sie die Bibi-Chanum-Moschee und den Siab-Basar, wo Sie in einer Teestube grünen Tee und Süßes genießen. Der Spaziergang endet in Schah-i-Sinda, der Gasse der türkisfarbenen Mausoleen. Ihr Guide erweckt an jedem Halt die Timuridenzeit zum Leben.",
                    ["Gur-Emir, das Grab Amir Timurs", "Der Registan und seine drei Medresen", "Teepause am Siab-Basar", "Schah-i-Sinda zum Abschluss"]),
             "es": ("Lo esencial de Samarcanda: Gur-e-Amir, Registán y Shah-i-Zinda con pausa para el té", "Los cinco grandes monumentos de Samarcanda a pie en una mañana, con té verde en una chaijana.",
                    "Se empieza en Gur-e-Amir, la cúpula azul acanalada sobre la tumba de Amir Timur, y se sigue hasta el Registán y sus tres madrazas. Por la calle peatonal se llega a la mezquita de Bibi-Khanym y al bazar Siab, con una pausa de té verde y dulces en una chaijana. El paseo termina en Shah-i-Zinda, la calle de los mausoleos turquesa. En cada parada el guía da vida a la época timúrida.",
                    ["Gur-e-Amir, la tumba de Amir Timur", "El Registán y sus tres madrazas", "Pausa para el té junto al bazar Siab", "Shah-i-Zinda al final"]),
         }),
    dict(slug="samarkand-evening-walk-food-tastings", category="Food", duration="4 hours", gyg_price=39, max=10, pickup=True,
         cover=commons("Registan Square in night July 2018 (Samarkand).jpg"), gallery=[commons("Siyob Bazaar in Samarkand.jpg"), "dastarkhan-sweets.jpg", commons("Plov_Tashkent.jpg")],
         included=["Local guide", "Street food tastings in the evening", "Green tea", "Hotel pickup and drop-off"],
         excluded=["Entrance tickets", "Tips (optional)"], meeting="Your hotel in Samarkand",
         text={
             "en": ("Samarkand by Evening: Walk with Local Food Tastings", "Four evening hours: the Registan under the lights, the old streets after sunset and the food locals eat at night.",
                    "We pick you up at your hotel in the late afternoon. As the sun goes down you walk through the old town with a local guide and taste the food Samarkand eats in the evening: hot samsa from the tandir, shashlik grilled over coals, fresh non, salads and sweets with green tea. The walk ends at the Registan when its three madrasas are lit up, and we drive you back to your hotel.",
                    ["The Registan lit up at night", "Samsa, shashlik and fresh non", "Old streets after sunset", "Hotel pickup and drop-off"]),
             "uz": ("Kechki Samarqand: mahalliy taomlarni tatib ko'riladigan sayr", "Kechki to'rt soat: chiroqlardagi Registon, quyosh botgandan keyingi eski ko'chalar va mahalliylar kechqurun yeydigan taomlar.",
                    "Kechga yaqin sizni mehmonxonadan olib ketamiz. Quyosh botayotganda mahalliy gid bilan eski shahar bo'ylab yurasiz va Samarqand kechqurun yeydigan taomlarni tatib ko'rasiz: tandirdan issiq somsa, cho'g'da pishgan shashlik, yangi non, salatlar va ko'k choy bilan shirinliklar. Sayr uch madrasa chiroqlarda yarqirab turgan Registonda tugaydi, so'ng sizni mehmonxonaga qaytaramiz.",
                    ["Tungi chiroqlardagi Registon", "Somsa, shashlik va yangi non", "Quyosh botgandan keyingi eski ko'chalar", "Mehmonxonadan olib ketish va qaytarish"]),
             "ru": ("Вечерний Самарканд: прогулка с дегустацией местной еды", "Четыре вечерних часа: Регистан в огнях, старые улицы после заката и то, что местные едят вечером.",
                    "Ближе к вечеру мы забираем вас из отеля. На закате вы гуляете по старому городу с местным гидом и пробуете то, что Самарканд ест вечером: горячую самсу из тандыра, шашлык на углях, свежую лепёшку, салаты и сладости с зелёным чаем. Прогулка заканчивается на Регистане, когда три медресе освещены, а затем мы отвозим вас в отель.",
                    ["Регистан в ночной подсветке", "Самса, шашлык и свежая лепёшка", "Старые улицы после заката", "Трансфер из отеля и обратно"]),
             "fr": ("Samarcande le soir : balade avec dégustations locales", "Quatre heures en soirée : le Régistan illuminé, les vieilles rues au coucher du soleil et ce que l'on mange ici le soir.",
                    "Nous venons vous chercher à l'hôtel en fin d'après-midi. Au coucher du soleil, vous parcourez la vieille ville avec un guide local et goûtez ce que Samarcande mange le soir : samsa chaude du tandir, chachlyk grillé sur la braise, pain frais, salades et douceurs avec du thé vert. La balade se termine au Régistan illuminé, puis nous vous raccompagnons à l'hôtel.",
                    ["Le Régistan illuminé", "Samsa, chachlyk et pain frais", "Les vieilles rues au crépuscule", "Prise en charge et retour à l'hôtel"]),
             "de": ("Samarkand am Abend: Spaziergang mit lokalen Kostproben", "Vier Abendstunden: der beleuchtete Registan, alte Gassen nach Sonnenuntergang und das, was man hier abends isst.",
                    "Am späten Nachmittag holen wir Sie im Hotel ab. Bei Sonnenuntergang gehen Sie mit einem lokalen Guide durch die Altstadt und probieren, was Samarkand am Abend isst: heiße Samsa aus dem Tandir, Schaschlik vom Holzkohlegrill, frisches Fladenbrot, Salate und Süßes mit grünem Tee. Der Spaziergang endet am beleuchteten Registan, danach bringen wir Sie zurück ins Hotel.",
                    ["Der beleuchtete Registan", "Samsa, Schaschlik und frisches Brot", "Alte Gassen nach Sonnenuntergang", "Abholung und Rückfahrt zum Hotel"]),
             "es": ("Samarcanda al atardecer: paseo con degustación local", "Cuatro horas de tarde-noche: el Registán iluminado, las calles antiguas al anochecer y lo que se come aquí por la noche.",
                    "Le recogemos en su hotel a última hora de la tarde. Al ponerse el sol recorre el casco antiguo con un guía local y prueba lo que Samarcanda come por la noche: samsa caliente del tandir, shashlik a la brasa, pan recién hecho, ensaladas y dulces con té verde. El paseo termina en el Registán iluminado y le llevamos de vuelta al hotel.",
                    ["El Registán iluminado", "Samsa, shashlik y pan recién hecho", "Calles antiguas al anochecer", "Recogida y regreso al hotel"]),
         }),
    dict(slug="samarkand-mahalla-life-and-food", category="Food", duration="4 hours", gyg_price=57, max=8, pickup=True,
         cover=commons("Tandir_non_tayyorlayotgan_novvoy.jpg"), gallery=["siab-dried-fruit.jpg", commons("Plov_Tashkent.jpg"), "dastarkhan-sweets.jpg"],
         included=["Local guide", "Visit to a family home in a mahalla", "Bread from the tandir, tea and a home-cooked lunch", "Hotel pickup and drop-off"],
         excluded=["Entrance tickets", "Tips (optional)"], meeting="Your hotel in Samarkand",
         text={
             "en": ("Samarkand Local Life: Mahalla Walk and Home-Cooked Food", "Four hours behind the monuments: an old mahalla, a baker at his tandir and lunch in a family courtyard.",
                    "Leave the tourist streets behind and walk with a local guide into a mahalla, one of the old neighbourhoods where Samarkand families have lived for generations. Watch a baker slap dough onto the wall of a clay tandir and taste the bread hot, buy fruit at the corner market and sit down in a family courtyard for tea and a home-cooked lunch. You see how people really live, pray and celebrate here, and we drive you back to your hotel.",
                    ["An old Samarkand mahalla", "Bread hot from the tandir", "Home-cooked lunch in a family courtyard", "Hotel pickup and drop-off"]),
             "uz": ("Samarqand hayoti: mahalla sayri va uy taomlari", "Yodgorliklar ortidagi to'rt soat: eski mahalla, tandir oldidagi novvoy va oila hovlisida tushlik.",
                    "Sayyohlar ko'chalarini ortda qoldirib, mahalliy gid bilan mahallaga — Samarqand oilalari avloddan-avlodga yashab kelayotgan eski mahallalardan biriga kirasiz. Novvoy xamirni loy tandir devoriga yopishtirishini ko'rasiz va nonni issiqligida tatib ko'rasiz, burchakdagi bozorchadan meva olasiz, so'ng oila hovlisida choy va uy taomidan tushlik qilasiz. Bu yerda odamlar haqiqatda qanday yashashi, ibodat qilishi va bayram qilishini ko'rasiz, keyin sizni mehmonxonaga qaytaramiz.",
                    ["Samarqandning eski mahallasi", "Tandirdan uzilgan issiq non", "Oila hovlisida uy taomidan tushlik", "Mehmonxonadan olib ketish va qaytarish"]),
             "ru": ("Жизнь Самарканда: прогулка по махалле и домашняя еда", "Четыре часа за фасадами памятников: старая махалля, пекарь у тандыра и обед во дворе семьи.",
                    "Оставив туристические улицы, вы с местным гидом заходите в махаллю — один из старых кварталов, где самаркандские семьи живут поколениями. Вы увидите, как пекарь прилепляет тесто к стенке глиняного тандыра, и попробуете горячую лепёшку, купите фрукты на маленьком рынке и сядете в семейном дворе за чай и домашний обед. Вы узнаете, как здесь живут, молятся и празднуют, а потом мы отвезём вас в отель.",
                    ["Старая самаркандская махалля", "Горячая лепёшка из тандыра", "Домашний обед в семейном дворе", "Трансфер из отеля и обратно"]),
             "fr": ("La vie à Samarcande : balade en mahalla et cuisine maison", "Quatre heures derrière les monuments : une vieille mahalla, un boulanger à son tandir et un déjeuner dans une cour familiale.",
                    "Quittez les rues touristiques et entrez avec un guide local dans une mahalla, l'un des vieux quartiers où les familles de Samarcande vivent depuis des générations. Regardez un boulanger plaquer la pâte contre la paroi d'un tandir et goûtez le pain tout chaud, achetez des fruits au petit marché puis asseyez-vous dans une cour familiale pour le thé et un déjeuner maison. Vous découvrez comment on vit, prie et fait la fête ici, puis nous vous raccompagnons à l'hôtel.",
                    ["Une vieille mahalla de Samarcande", "Le pain tout chaud du tandir", "Déjeuner maison dans une cour familiale", "Prise en charge et retour à l'hôtel"]),
             "de": ("Alltag in Samarkand: Mahalla-Spaziergang und Hausmannskost", "Vier Stunden hinter den Monumenten: eine alte Mahalla, ein Bäcker am Tandir und Mittagessen im Familienhof.",
                    "Lassen Sie die Touristenstraßen hinter sich und gehen Sie mit einem lokalen Guide in eine Mahalla, eines der alten Viertel, in denen Samarkander Familien seit Generationen leben. Sehen Sie, wie ein Bäcker den Teig an die Wand des Lehmofens drückt, probieren Sie das Brot ofenwarm, kaufen Sie Obst am kleinen Markt und setzen Sie sich in einem Familienhof zu Tee und hausgemachtem Mittagessen. Sie erleben, wie man hier wirklich lebt, betet und feiert, danach bringen wir Sie ins Hotel zurück.",
                    ["Eine alte Mahalla in Samarkand", "Ofenwarmes Brot aus dem Tandir", "Hausgemachtes Essen im Familienhof", "Abholung und Rückfahrt zum Hotel"]),
             "es": ("La vida en Samarcanda: paseo por la mahalla y comida casera", "Cuatro horas detrás de los monumentos: una vieja mahalla, un panadero en su tandir y almuerzo en el patio de una familia.",
                    "Deje atrás las calles turísticas y entre con un guía local en una mahalla, uno de los barrios antiguos donde las familias de Samarcanda viven desde hace generaciones. Vea cómo un panadero pega la masa a la pared del horno tandir y pruebe el pan caliente, compre fruta en el mercadillo y siéntese en el patio de una familia para tomar té y un almuerzo casero. Descubrirá cómo se vive, se reza y se celebra aquí, y después le llevamos al hotel.",
                    ["Una vieja mahalla de Samarcanda", "Pan caliente del tandir", "Almuerzo casero en un patio familiar", "Recogida y regreso al hotel"]),
         }),
]


def photo(name):
    return name if name.startswith("https://") else PHOTOS + name


def walk_fields(w):
    """The columns of a new tour (English) and its translations."""
    i18n = {}
    for col, lang in enumerate(LANGS):
        title, summary, description, highlights = w["text"][lang]
        i18n[lang] = {
            "title": title, "summary": summary, "description": description, "highlights": highlights,
            "category": CATEGORY[w["category"]][col], "duration_label": DURATION[w["duration"]][col], "group_type": GROUP["Small group"][col],
            "meeting_point": MEETING[w["meeting"]][col], "included": [ITEM[x][col] for x in w["included"]], "excluded": [ITEM[x][col] for x in w["excluded"]],
            "destination_name": ("Samarqand", "Самарканд", "Samarcande", "Samarkand", "Samarcanda")[col],
        }
    title, summary, description, highlights = w["text"]["en"]
    return dict(
        title=title, summary=summary, description=description, highlights=highlights, destination_slug="samarkand", destination_name="Samarkand",
        category=w["category"], tour_type="walking", duration_label=w["duration"], group_type="Small group", price_from_usd=w["gyg_price"] - 1,
        group_pricing=False, pickup_included=w.get("pickup", False), transport_included=w.get("pickup", False), tickets_included=False,
        image_url=photo(w["cover"]), gallery=[photo(x) for x in w["gallery"]], max_travelers=w["max"], languages=["English", "Russian", "Uzbek"],
        included=w["included"], excluded=w["excluded"], meeting_point=w["meeting"], guide="", review_count=0, rating=0, featured=False, is_demo=False,
        status="published", i18n=i18n,
    )
