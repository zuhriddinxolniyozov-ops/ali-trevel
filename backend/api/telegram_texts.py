"""Everything the Telegram bot says, in the six languages of the website."""

LANGS = [("en", "🇬🇧 English"), ("uz", "🇺🇿 Oʻzbekcha"), ("ru", "🇷🇺 Русский"), ("fr", "🇫🇷 Français"), ("de", "🇩🇪 Deutsch"), ("es", "🇪🇸 Español")]

CHOOSE = ("🌍 Choose your language · Tilni tanlang · Выберите язык\n"
          "Choisissez votre langue · Sprache wählen · Elija su idioma")

# key -> {lang: text}. Texts may contain Telegram HTML (<b>, <i>) and {placeholders}.
T = {
    "lang_set": {
        "en": "Language: English ✅", "uz": "Til: Oʻzbekcha ✅", "ru": "Язык: Русский ✅",
        "fr": "Langue : Français ✅", "de": "Sprache: Deutsch ✅", "es": "Idioma: Español ✅"},
    "welcome": {
        "en": "Welcome to <b>ALI TRAVEL</b> — private tours, hands-on cooking classes, hotels and transfers across Uzbekistan.\n\nWhat would you like to see?",
        "uz": "<b>ALI TRAVEL</b> ga xush kelibsiz — Oʻzbekiston boʻylab shaxsiy turlar, amaliy oshpazlik darslari, mehmonxonalar va transferlar.\n\nNimani koʻrmoqchisiz?",
        "ru": "Добро пожаловать в <b>ALI TRAVEL</b> — частные туры, практические кулинарные занятия, отели и трансферы по Узбекистану.\n\nЧто вы хотите посмотреть?",
        "fr": "Bienvenue chez <b>ALI TRAVEL</b> — circuits privés, ateliers de cuisine pratiques, hôtels et transferts à travers l'Ouzbékistan.\n\nQue souhaitez-vous découvrir ?",
        "de": "Willkommen bei <b>ALI TRAVEL</b> — private Touren, praktische Kochkurse, Hotels und Transfers in ganz Usbekistan.\n\nWas möchten Sie sehen?",
        "es": "Bienvenido a <b>ALI TRAVEL</b>: tours privados, talleres de cocina prácticos, hoteles y traslados por todo Uzbekistán.\n\n¿Qué le gustaría ver?"},
    "menu_dest": {"en": "🧭 Destinations", "uz": "🧭 Yoʻnalishlar", "ru": "🧭 Направления", "fr": "🧭 Destinations", "de": "🧭 Reiseziele", "es": "🧭 Destinos"},
    "menu_tours": {"en": "🗺 Tours", "uz": "🗺 Turlar", "ru": "🗺 Туры", "fr": "🗺 Circuits", "de": "🗺 Touren", "es": "🗺 Tours"},
    "menu_classes": {"en": "🍲 Cooking classes", "uz": "🍲 Oshpazlik darslari", "ru": "🍲 Кулинарные занятия", "fr": "🍲 Ateliers de cuisine", "de": "🍲 Kochkurse", "es": "🍲 Talleres de cocina"},
    "menu_prices": {"en": "💰 Prices & groups", "uz": "💰 Narxlar va guruhlar", "ru": "💰 Цены и группы", "fr": "💰 Prix et groupes", "de": "💰 Preise & Gruppen", "es": "💰 Precios y grupos"},
    "menu_policy": {"en": "📋 Cancellation & payment", "uz": "📋 Bekor qilish va toʻlov", "ru": "📋 Отмена и оплата", "fr": "📋 Annulation et paiement", "de": "📋 Stornierung & Zahlung", "es": "📋 Cancelación y pago"},
    "menu_contact": {"en": "📞 Contact us", "uz": "📞 Aloqa", "ru": "📞 Контакты", "fr": "📞 Contact", "de": "📞 Kontakt", "es": "📞 Contacto"},
    "menu_ask": {"en": "✉️ Send a request", "uz": "✉️ Soʻrov yuborish", "ru": "✉️ Отправить запрос", "fr": "✉️ Envoyer une demande", "de": "✉️ Anfrage senden", "es": "✉️ Enviar una solicitud"},
    "menu_lang": {"en": "🌐 Language", "uz": "🌐 Til", "ru": "🌐 Язык", "fr": "🌐 Langue", "de": "🌐 Sprache", "es": "🌐 Idioma"},
    "back": {"en": "⬅️ Menu", "uz": "⬅️ Menyu", "ru": "⬅️ Меню", "fr": "⬅️ Menu", "de": "⬅️ Menü", "es": "⬅️ Menú"},
    "pick_dest": {"en": "Choose a destination:", "uz": "Yoʻnalishni tanlang:", "ru": "Выберите направление:", "fr": "Choisissez une destination :", "de": "Wählen Sie ein Reiseziel:", "es": "Elija un destino:"},
    "pick_tour": {"en": "Choose a tour:", "uz": "Turni tanlang:", "ru": "Выберите тур:", "fr": "Choisissez un circuit :", "de": "Wählen Sie eine Tour:", "es": "Elija un tour:"},
    "tours_here": {"en": "Tours in this region:", "uz": "Bu hududdagi turlar:", "ru": "Туры в этом регионе:", "fr": "Circuits dans cette région :", "de": "Touren in dieser Region:", "es": "Tours en esta región:"},
    "no_items": {"en": "Nothing to show yet.", "uz": "Hozircha koʻrsatadigan narsa yoʻq.", "ru": "Пока нечего показать.", "fr": "Rien à afficher pour l'instant.", "de": "Noch nichts anzuzeigen.", "es": "Aún no hay nada que mostrar."},
    "classes_intro": {
        "en": "Hands-on classes in Samarkand: bake non bread in a clay tandir or cook plov in a kazan, then take your food home. Choose one:",
        "uz": "Samarqandda amaliy darslar: sopol tandirda non yoping yoki qozonda osh pishiring va oʻzingiz tayyorlagan taomni uyga olib keting. Birini tanlang:",
        "ru": "Практические занятия в Самарканде: испеките лепёшку в глиняном тандыре или приготовьте плов в казане и увезите свои блюда домой. Выберите:",
        "fr": "Ateliers pratiques à Samarcande : cuisez du pain non dans un tandir en argile ou préparez un plov dans un kazan, puis rapportez vos plats. Choisissez :",
        "de": "Praxiskurse in Samarkand: Backen Sie Non-Brot im Lehm-Tandir oder kochen Sie Plov im Kazan und nehmen Sie das Selbstgemachte mit nach Hause. Wählen Sie:",
        "es": "Talleres prácticos en Samarcanda: hornee pan non en un tandir de barro o cocine plov en un kazán y llévese lo que prepare. Elija:"},
    "duration": {"en": "Duration", "uz": "Davomiyligi", "ru": "Длительность", "fr": "Durée", "de": "Dauer", "es": "Duración"},
    "from": {"en": "From", "uz": "Dan", "ru": "От", "fr": "À partir de", "de": "Ab", "es": "Desde"},
    "per_person": {"en": "per person", "uz": "bir kishi uchun", "ru": "с человека", "fr": "par personne", "de": "pro Person", "es": "por persona"},
    "group_note": {
        "en": "Price for a group of 20 or more; smaller groups pay a little more per person (see “Prices & groups”).",
        "uz": "Narx 20 va undan ortiq kishilik guruh uchun; kichikroq guruhlar bir kishi uchun biroz koʻproq toʻlaydi («Narxlar va guruhlar» boʻlimiga qarang).",
        "ru": "Цена для группы от 20 человек; небольшие группы платят чуть больше с человека (см. «Цены и группы»).",
        "fr": "Prix pour un groupe de 20 personnes ou plus ; les petits groupes paient un peu plus par personne (voir « Prix et groupes »).",
        "de": "Preis für eine Gruppe ab 20 Personen; kleinere Gruppen zahlen etwas mehr pro Person (siehe „Preise & Gruppen“).",
        "es": "Precio para un grupo de 20 o más; los grupos más pequeños pagan algo más por persona (vea «Precios y grupos»)."},
    "highlights": {"en": "Highlights", "uz": "Asosiy jihatlari", "ru": "Главное", "fr": "À retenir", "de": "Highlights", "es": "Lo más destacado"},
    "open_site": {"en": "🌐 Open on the website", "uz": "🌐 Saytda ochish", "ru": "🌐 Открыть на сайте", "fr": "🌐 Ouvrir sur le site", "de": "🌐 Auf der Website öffnen", "es": "🌐 Abrir en el sitio"},
    "web_line": {"en": "Details and booking", "uz": "Batafsil va bron", "ru": "Подробности и бронирование", "fr": "Détails et réservation", "de": "Details und Buchung", "es": "Detalles y reserva"},
    "request_tour": {"en": "✉️ Request this tour", "uz": "✉️ Shu turni soʻrash", "ru": "✉️ Запросить этот тур", "fr": "✉️ Demander ce circuit", "de": "✉️ Diese Tour anfragen", "es": "✉️ Solicitar este tour"},
    "prices_head": {
        "en": "<b>Prices and group size</b>\nPrices on our website are per person for a group of <b>20 or more</b>. A guide, a vehicle and the organisation of a tour cost the same for 2 people or 20, so smaller groups pay a little more per person:",
        "uz": "<b>Narxlar va guruh hajmi</b>\nSaytdagi narxlar <b>20 va undan ortiq kishilik</b> guruh uchun bir kishi narxi. Gid, avtomobil va tashkil etish xarajati 2 kishi uchun ham, 20 kishi uchun ham bir xil, shuning uchun kichikroq guruhlar bir kishi uchun biroz koʻproq toʻlaydi:",
        "ru": "<b>Цены и размер группы</b>\nЦены на сайте — с человека для группы от <b>20 человек</b>. Гид, автомобиль и организация тура стоят одинаково для 2 и для 20 человек, поэтому небольшие группы платят чуть больше с человека:",
        "fr": "<b>Prix et taille du groupe</b>\nLes prix du site sont par personne pour un groupe de <b>20 personnes ou plus</b>. Un guide, un véhicule et l'organisation coûtent autant pour 2 personnes que pour 20 ; les petits groupes paient donc un peu plus par personne :",
        "de": "<b>Preise und Gruppengröße</b>\nDie Preise auf unserer Website gelten pro Person für eine Gruppe ab <b>20 Personen</b>. Guide, Fahrzeug und Organisation kosten für 2 oder 20 Personen gleich viel, daher zahlen kleinere Gruppen etwas mehr pro Person:",
        "es": "<b>Precios y tamaño del grupo</b>\nLos precios del sitio son por persona para un grupo de <b>20 o más</b>. Un guía, un vehículo y la organización cuestan lo mismo para 2 personas que para 20, así que los grupos pequeños pagan algo más por persona:"},
    "prices_tail": {
        "en": "You always see your exact price before sending a request, and nothing is charged until our team confirms.",
        "uz": "Soʻrov yuborishdan oldin aniq narxingizni koʻrasiz, jamoamiz tasdiqlamaguncha hech narsa undirilmaydi.",
        "ru": "Точную цену вы видите до отправки запроса, и ничего не списывается, пока наша команда не подтвердит.",
        "fr": "Vous voyez toujours votre prix exact avant d'envoyer une demande, et rien n'est débité tant que notre équipe n'a pas confirmé.",
        "de": "Ihren genauen Preis sehen Sie immer vor dem Senden einer Anfrage, und es wird nichts abgebucht, bis unser Team bestätigt hat.",
        "es": "Siempre ve su precio exacto antes de enviar una solicitud, y no se cobra nada hasta que nuestro equipo confirme."},
    "travelers": {"en": "travelers", "uz": "sayyoh", "ru": "путешественников", "fr": "voyageurs", "de": "Reisende", "es": "viajeros"},
    "policy": {
        "en": "<b>Cancellation and payment</b>\n• No payment is taken when you send a request. Our team confirms availability in writing first, then agrees the payment with you.\n• Cancellation is free up to 30 days before the start.\n• Date changes made 14 days or more ahead are free, subject to availability.\n• Transfers: free until 24 hours before pickup.\n\nFull rules:",
        "uz": "<b>Bekor qilish va toʻlov</b>\n• Soʻrov yuborganingizda toʻlov olinmaydi. Jamoamiz avval joy borligini yozma tasdiqlaydi, soʻng toʻlovni siz bilan kelishadi.\n• Boshlanishidan 30 kun oldingacha bekor qilish bepul.\n• 14 kun yoki undan oldin sanani oʻzgartirish bepul (joy boʻlsa).\n• Transferlar: kutib olishdan 24 soat oldingacha bepul.\n\nToʻliq qoidalar:",
        "ru": "<b>Отмена и оплата</b>\n• При отправке запроса оплата не взимается. Сначала наша команда письменно подтверждает наличие мест, затем согласует с вами оплату.\n• Отмена бесплатна за 30 дней до начала.\n• Перенос даты за 14 дней и более бесплатен при наличии мест.\n• Трансферы: бесплатно за 24 часа до подачи.\n\nПолные правила:",
        "fr": "<b>Annulation et paiement</b>\n• Aucun paiement n'est pris à l'envoi d'une demande. Notre équipe confirme d'abord la disponibilité par écrit, puis convient du paiement avec vous.\n• L'annulation est gratuite jusqu'à 30 jours avant le départ.\n• Un changement de date 14 jours ou plus à l'avance est gratuit, selon disponibilité.\n• Transferts : gratuit jusqu'à 24 heures avant la prise en charge.\n\nRègles complètes :",
        "de": "<b>Stornierung und Zahlung</b>\n• Beim Senden einer Anfrage wird nichts abgebucht. Unser Team bestätigt zuerst schriftlich die Verfügbarkeit und vereinbart dann die Zahlung mit Ihnen.\n• Die Stornierung ist bis 30 Tage vor Beginn kostenlos.\n• Terminänderungen 14 Tage oder früher sind bei Verfügbarkeit kostenlos.\n• Transfers: kostenlos bis 24 Stunden vor der Abholung.\n\nVollständige Regeln:",
        "es": "<b>Cancelación y pago</b>\n• No se cobra nada al enviar una solicitud. Nuestro equipo confirma primero la disponibilidad por escrito y luego acuerda el pago con usted.\n• La cancelación es gratuita hasta 30 días antes del inicio.\n• Los cambios de fecha con 14 días o más de antelación son gratuitos, según disponibilidad.\n• Traslados: gratis hasta 24 horas antes de la recogida.\n\nReglas completas:"},
    "contact_head": {"en": "<b>Contact ALI TRAVEL</b>", "uz": "<b>ALI TRAVEL bilan aloqa</b>", "ru": "<b>Контакты ALI TRAVEL</b>", "fr": "<b>Contacter ALI TRAVEL</b>", "de": "<b>ALI TRAVEL kontaktieren</b>", "es": "<b>Contacto con ALI TRAVEL</b>"},
    "ask_prompt": {
        "en": "Write your question or request here: the tour, dates and number of travelers. You can also share your phone number so we can call you.",
        "uz": "Savol yoki soʻrovingizni shu yerga yozing: tur, sanalar va sayyohlar soni. Qoʻngʻiroq qilishimiz uchun telefon raqamingizni ham ulashishingiz mumkin.",
        "ru": "Напишите здесь ваш вопрос или запрос: тур, даты и число путешественников. Можно также поделиться номером телефона, чтобы мы вам позвонили.",
        "fr": "Écrivez ici votre question ou demande : le circuit, les dates et le nombre de voyageurs. Vous pouvez aussi partager votre numéro pour que nous vous appelions.",
        "de": "Schreiben Sie hier Ihre Frage oder Anfrage: Tour, Termine und Zahl der Reisenden. Sie können auch Ihre Telefonnummer teilen, damit wir Sie anrufen.",
        "es": "Escriba aquí su pregunta o solicitud: el tour, las fechas y el número de viajeros. También puede compartir su teléfono para que le llamemos."},
    "share_phone": {"en": "📱 Share my phone", "uz": "📱 Telefonimni ulashish", "ru": "📱 Поделиться телефоном", "fr": "📱 Partager mon numéro", "de": "📱 Telefonnummer teilen", "es": "📱 Compartir mi teléfono"},
    "cancel": {"en": "✖️ Cancel", "uz": "✖️ Bekor qilish", "ru": "✖️ Отмена", "fr": "✖️ Annuler", "de": "✖️ Abbrechen", "es": "✖️ Cancelar"},
    "ask_thanks": {
        "en": "Thank you! Our team received your message and will reply soon.",
        "uz": "Rahmat! Jamoamiz xabaringizni qabul qildi va tez orada javob beradi.",
        "ru": "Спасибо! Наша команда получила ваше сообщение и скоро ответит.",
        "fr": "Merci ! Notre équipe a reçu votre message et vous répondra bientôt.",
        "de": "Danke! Unser Team hat Ihre Nachricht erhalten und antwortet bald.",
        "es": "¡Gracias! Nuestro equipo recibió su mensaje y responderá pronto."},
    "unknown": {
        "en": "I did not quite understand. Please choose from the menu, or press “✉️ Send a request” to write to our team.",
        "uz": "Tushunmadim. Iltimos, menyudan tanlang yoki jamoamizga yozish uchun «✉️ Soʻrov yuborish» tugmasini bosing.",
        "ru": "Не совсем понял. Выберите пункт меню или нажмите «✉️ Отправить запрос», чтобы написать нашей команде.",
        "fr": "Je n'ai pas bien compris. Choisissez dans le menu ou appuyez sur « ✉️ Envoyer une demande » pour écrire à notre équipe.",
        "de": "Das habe ich nicht ganz verstanden. Bitte wählen Sie im Menü oder drücken Sie „✉️ Anfrage senden“, um unserem Team zu schreiben.",
        "es": "No lo he entendido bien. Elija en el menú o pulse «✉️ Enviar una solicitud» para escribir a nuestro equipo."},
}


def text(key, lang, **fields):
    entry = T[key]
    return (entry.get(lang) or entry["en"]).format(**fields) if fields else (entry.get(lang) or entry["en"])
