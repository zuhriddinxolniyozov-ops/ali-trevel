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
    "menu_classes": {"en": "🍲 Food experiences", "uz": "🍲 Taom tajribalari", "ru": "🍲 Гастро-опыты", "fr": "🍲 Expériences culinaires", "de": "🍲 Kulinarische Erlebnisse", "es": "🍲 Experiencias gastronómicas"},
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
        "en": "Taste Samarkand with your own hands: bake non in a clay tandir or cook plov in a kazan, taste it together at the dastarkhan and take the rest home. Choose one:",
        "uz": "Samarqandni oʻz qoʻlingiz bilan tatib koʻring: sopol tandirda non yoping yoki qozonda osh pishiring, dasturxonda birga tatib koʻring va qolganini uyga olib keting. Birini tanlang:",
        "ru": "Почувствуйте вкус Самарканда своими руками: испеките лепёшку в глиняном тандыре или приготовьте плов в казане, попробуйте вместе за дастарханом и увезите остальное домой. Выберите:",
        "fr": "Goûtez Samarcande de vos propres mains : cuisez du pain non dans un tandir en argile ou préparez un plov dans un kazan, dégustez-le ensemble au dastarkhan et rapportez le reste. Choisissez :",
        "de": "Schmecken Sie Samarkand mit eigenen Händen: Backen Sie Non im Lehm-Tandir oder kochen Sie Plov im Kazan, probieren Sie gemeinsam am Dastarkhan und nehmen Sie den Rest mit nach Hause. Wählen Sie:",
        "es": "Pruebe Samarcanda con sus propias manos: hornee pan non en un tandir de barro o cocine plov en un kazán, pruébenlo juntos en el dastarkhán y llévese el resto a casa. Elija:"},
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


# ---- booking inside the bot ------------------------------------------------------------
T.update({
    "request_tour": {"en": "✉️ Ask about this tour", "uz": "✉️ Shu tur haqida savol", "ru": "✉️ Вопрос об этом туре", "fr": "✉️ Question sur ce circuit", "de": "✉️ Frage zu dieser Tour", "es": "✉️ Preguntar por este tour"},
    "book_tour": {"en": "📅 Book this tour", "uz": "📅 Shu turni bron qilish", "ru": "📅 Забронировать этот тур", "fr": "📅 Réserver ce circuit", "de": "📅 Diese Tour buchen", "es": "📅 Reservar este tour"},
    "menu_mine": {"en": "📖 My bookings", "uz": "📖 Mening bronlarim", "ru": "📖 Мои бронирования", "fr": "📖 Mes réservations", "de": "📖 Meine Buchungen", "es": "📖 Mis reservas"},
    "book_date": {
        "en": "📅 <b>{title}</b>\nWhen would you like to start? Write the date, for example <code>2027-05-01</code> or <code>01.05.2027</code>.",
        "uz": "📅 <b>{title}</b>\nQachon boshlamoqchisiz? Sanani yozing, masalan <code>2027-05-01</code> yoki <code>01.05.2027</code>.",
        "ru": "📅 <b>{title}</b>\nКогда вы хотите начать? Напишите дату, например <code>2027-05-01</code> или <code>01.05.2027</code>.",
        "fr": "📅 <b>{title}</b>\nQuand souhaitez-vous commencer ? Écrivez la date, par exemple <code>2027-05-01</code> ou <code>01.05.2027</code>.",
        "de": "📅 <b>{title}</b>\nWann möchten Sie beginnen? Schreiben Sie das Datum, zum Beispiel <code>2027-05-01</code> oder <code>01.05.2027</code>.",
        "es": "📅 <b>{title}</b>\n¿Cuándo le gustaría empezar? Escriba la fecha, por ejemplo <code>2027-05-01</code> o <code>01.05.2027</code>."},
    "book_date_bad": {
        "en": "I could not read that date, or it is in the past. Please write it like <code>2027-05-01</code> or <code>01.05.2027</code>.",
        "uz": "Sanani oʻqiy olmadim yoki u oʻtib ketgan. Iltimos, <code>2027-05-01</code> yoki <code>01.05.2027</code> koʻrinishida yozing.",
        "ru": "Не удалось прочитать дату, или она уже прошла. Напишите, например, <code>2027-05-01</code> или <code>01.05.2027</code>.",
        "fr": "Je n'ai pas pu lire cette date, ou elle est passée. Écrivez-la ainsi : <code>2027-05-01</code> ou <code>01.05.2027</code>.",
        "de": "Das Datum konnte ich nicht lesen, oder es liegt in der Vergangenheit. Bitte schreiben Sie es so: <code>2027-05-01</code> oder <code>01.05.2027</code>.",
        "es": "No pude leer esa fecha, o ya pasó. Escríbala así: <code>2027-05-01</code> o <code>01.05.2027</code>."},
    "book_guests": {
        "en": "👥 How many travelers? Write a number from 1 to 50. (Prices per person are lower for bigger groups.)",
        "uz": "👥 Necha kishi sayohat qiladi? 1 dan 50 gacha son yozing. (Katta guruhlarda bir kishi narxi arzonroq.)",
        "ru": "👥 Сколько путешественников? Напишите число от 1 до 50. (Для больших групп цена с человека ниже.)",
        "fr": "👥 Combien de voyageurs ? Écrivez un nombre de 1 à 50. (Le prix par personne baisse pour les grands groupes.)",
        "de": "👥 Wie viele Reisende? Schreiben Sie eine Zahl von 1 bis 50. (Für größere Gruppen ist der Preis pro Person niedriger.)",
        "es": "👥 ¿Cuántos viajeros? Escriba un número del 1 al 50. (El precio por persona baja en grupos grandes.)"},
    "book_guests_bad": {
        "en": "Please write the number of travelers as a number from 1 to 50.", "uz": "Iltimos, sayyohlar sonini 1 dan 50 gacha son bilan yozing.",
        "ru": "Напишите число путешественников цифрой от 1 до 50.", "fr": "Écrivez le nombre de voyageurs en chiffres, de 1 à 50.",
        "de": "Bitte schreiben Sie die Zahl der Reisenden als Zahl von 1 bis 50.", "es": "Escriba el número de viajeros como cifra del 1 al 50."},
    "book_phone": {
        "en": "💵 {guests} × {per} per person = <b>{total}</b>\n(the price per person depends on the group size; the final price is confirmed by our team)\n\n📱 Last step: share your phone number so we can confirm the booking — press the button or type the number.",
        "uz": "💵 {guests} × {per} (bir kishi) = <b>{total}</b>\n(bir kishi narxi guruh hajmiga bogʻliq; yakuniy narxni jamoamiz tasdiqlaydi)\n\n📱 Oxirgi qadam: bronni tasdiqlashimiz uchun telefon raqamingizni ulashing — tugmani bosing yoki raqamni yozing.",
        "ru": "💵 {guests} × {per} с человека = <b>{total}</b>\n(цена с человека зависит от размера группы; окончательную цену подтверждает наша команда)\n\n📱 Последний шаг: поделитесь номером телефона, чтобы мы подтвердили бронирование — нажмите кнопку или напишите номер.",
        "fr": "💵 {guests} × {per} par personne = <b>{total}</b>\n(le prix par personne dépend de la taille du groupe ; le prix final est confirmé par notre équipe)\n\n📱 Dernière étape : partagez votre numéro pour que nous confirmions la réservation — appuyez sur le bouton ou écrivez le numéro.",
        "de": "💵 {guests} × {per} pro Person = <b>{total}</b>\n(der Preis pro Person hängt von der Gruppengröße ab; den endgültigen Preis bestätigt unser Team)\n\n📱 Letzter Schritt: Teilen Sie Ihre Telefonnummer, damit wir die Buchung bestätigen — Knopf drücken oder Nummer eintippen.",
        "es": "💵 {guests} × {per} por persona = <b>{total}</b>\n(el precio por persona depende del tamaño del grupo; nuestro equipo confirma el precio final)\n\n📱 Último paso: comparta su teléfono para que confirmemos la reserva: pulse el botón o escriba el número."},
    "book_phone_bad": {
        "en": "That does not look like a phone number. Press the button or type it with the country code, e.g. +998 90 123 45 67.",
        "uz": "Bu telefon raqamiga oʻxshamayapti. Tugmani bosing yoki davlat kodi bilan yozing, masalan +998 90 123 45 67.",
        "ru": "Это не похоже на номер телефона. Нажмите кнопку или напишите номер с кодом страны, например +998 90 123 45 67.",
        "fr": "Cela ne ressemble pas à un numéro de téléphone. Appuyez sur le bouton ou saisissez-le avec l'indicatif, par ex. +998 90 123 45 67.",
        "de": "Das sieht nicht nach einer Telefonnummer aus. Drücken Sie den Knopf oder tippen Sie sie mit Ländervorwahl ein, z. B. +998 90 123 45 67.",
        "es": "Eso no parece un número de teléfono. Pulse el botón o escríbalo con el prefijo del país, p. ej. +998 90 123 45 67."},
    "book_done": {
        "en": "✅ Request <b>{ref}</b> received for “{title}”.\nNothing is charged yet: our team will confirm availability and the final price and message you here.",
        "uz": "✅ “{title}” uchun <b>{ref}</b> raqamli soʻrov qabul qilindi.\nHozircha hech narsa undirilmaydi: jamoamiz joy borligini va yakuniy narxni tasdiqlab, sizga shu yerda yozadi.",
        "ru": "✅ Запрос <b>{ref}</b> на «{title}» получен.\nПока ничего не списывается: наша команда подтвердит наличие мест и окончательную цену и напишет вам здесь.",
        "fr": "✅ Demande <b>{ref}</b> reçue pour « {title} ».\nRien n'est débité pour l'instant : notre équipe confirmera la disponibilité et le prix final et vous écrira ici.",
        "de": "✅ Anfrage <b>{ref}</b> für „{title}“ erhalten.\nEs wird noch nichts abgebucht: Unser Team bestätigt Verfügbarkeit und Endpreis und schreibt Ihnen hier.",
        "es": "✅ Solicitud <b>{ref}</b> recibida para «{title}».\nAún no se cobra nada: nuestro equipo confirmará la disponibilidad y el precio final y le escribirá aquí."},
    "mine_head": {"en": "<b>Your bookings</b>", "uz": "<b>Sizning bronlaringiz</b>", "ru": "<b>Ваши бронирования</b>", "fr": "<b>Vos réservations</b>", "de": "<b>Ihre Buchungen</b>", "es": "<b>Sus reservas</b>"},
    "mine_none": {
        "en": "You have not booked anything in this chat yet. Open a tour and press “📅 Book this tour”.",
        "uz": "Bu chatda hali hech narsa bron qilmagansiz. Turni oching va «📅 Shu turni bron qilish» ni bosing.",
        "ru": "В этом чате вы пока ничего не бронировали. Откройте тур и нажмите «📅 Забронировать этот тур».",
        "fr": "Vous n'avez encore rien réservé dans ce chat. Ouvrez un circuit et appuyez sur « 📅 Réserver ce circuit ».",
        "de": "Sie haben in diesem Chat noch nichts gebucht. Öffnen Sie eine Tour und drücken Sie „📅 Diese Tour buchen“.",
        "es": "Aún no ha reservado nada en este chat. Abra un tour y pulse «📅 Reservar este tour»."},
    "status_pending": {"en": "waiting for confirmation", "uz": "tasdiq kutilmoqda", "ru": "ожидает подтверждения", "fr": "en attente de confirmation", "de": "wartet auf Bestätigung", "es": "pendiente de confirmación"},
    "status_confirmed": {"en": "confirmed", "uz": "tasdiqlangan", "ru": "подтверждено", "fr": "confirmée", "de": "bestätigt", "es": "confirmada"},
    "status_cancelled": {"en": "cancelled", "uz": "bekor qilingan", "ru": "отменено", "fr": "annulée", "de": "storniert", "es": "cancelada"},
    "status_completed": {"en": "completed", "uz": "yakunlangan", "ru": "завершено", "fr": "terminée", "de": "abgeschlossen", "es": "completada"},
    "team_note": {
        "en": "✅ This account is registered as the <b>ALI TRAVEL team</b>: new bookings and messages from the website and from this bot will arrive here.",
        "uz": "✅ Bu akkaunt <b>ALI TRAVEL jamoasi</b> sifatida roʻyxatdan oʻtdi: saytdan va shu botdan kelgan yangi bronlar va xabarlar shu yerga keladi.",
        "ru": "✅ Этот аккаунт зарегистрирован как <b>команда ALI TRAVEL</b>: новые бронирования и сообщения с сайта и из этого бота будут приходить сюда.",
        "fr": "✅ Ce compte est enregistré comme <b>équipe ALI TRAVEL</b> : les nouvelles réservations et messages du site et de ce bot arriveront ici.",
        "de": "✅ Dieses Konto ist als <b>ALI-TRAVEL-Team</b> registriert: neue Buchungen und Nachrichten von der Website und aus diesem Bot kommen hier an.",
        "es": "✅ Esta cuenta está registrada como <b>equipo de ALI TRAVEL</b>: aquí llegarán las nuevas reservas y mensajes del sitio y de este bot."},
})

T.update({
    "social_follow": {
        "en": "📲 <b>Follow ALI TRAVEL</b> for photos, videos and stories from the Silk Road, and see how our guests travel:",
        "uz": "📲 <b>ALI TRAVEL</b> ni kuzatib boring: Ipak yoʻlidan suratlar, videolar va hikoyalar, mehmonlarimiz qanday sayohat qilishini koʻring:",
        "ru": "📲 <b>Подписывайтесь на ALI TRAVEL</b>: фото, видео и истории с Шёлкового пути — посмотрите, как путешествуют наши гости:",
        "fr": "📲 <b>Suivez ALI TRAVEL</b> pour des photos, vidéos et récits de la Route de la soie, et voyez comment voyagent nos hôtes :",
        "de": "📲 <b>Folgen Sie ALI TRAVEL</b> für Fotos, Videos und Geschichten von der Seidenstraße und sehen Sie, wie unsere Gäste reisen:",
        "es": "📲 <b>Siga a ALI TRAVEL</b> para ver fotos, vídeos e historias de la Ruta de la Seda y cómo viajan nuestros huéspedes:"},
})
