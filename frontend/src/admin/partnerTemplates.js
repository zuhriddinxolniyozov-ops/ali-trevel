/**
 * Drafts of the letters ALI TRAVEL sends to hotels, guides and transport providers in Samarkand:
 * a cooperation proposal, a short official email, a price request and a cooperation agreement,
 * in English, Uzbek and Russian. They are filled from a small form and stay editable.
 * These are drafts: the agreement in particular should be read by a lawyer before it is signed.
 */
export const PARTNER_TYPES = ['hotel', 'guide', 'transport']
export const DOCS = ['proposal', 'email', 'inquiry', 'agreement', 'photos']
export const DOC_LANGS = [['en', 'English'], ['uz', "Oʻzbekcha"], ['ru', 'Русский']]

const list = (items) => items.map((x) => `- ${x}`).join('\n')
const steps = (items) => items.map((x, i) => `${i + 1}. ${x}`).join('\n')
const when = (iso, lang) => (iso ? new Date(`${iso}T12:00:00`).toLocaleDateString(lang === 'uz' ? 'uz-UZ' : lang === 'ru' ? 'ru-RU' : 'en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) : '____')
const blank = (v, fallback = '________________') => (v && String(v).trim() ? v : fallback)

const KINDS = {
  en: {
    hotel: { who: 'hotels and guesthouses', one: 'hotel', short: 'accommodation', asks: [
      'Your net (contract) rates per room per night for single, double and triple occupancy, in low and high season',
      'Whether breakfast is included, and the price of other meals',
      'Group rates for 10 or more guests and any free-room policy (for example one free room per 15 paying)',
      'Check-in and check-out times, and options for early arrival or late departure',
      'Your cancellation and no-show conditions, and the notice we must give',
      'Room categories, number of rooms and facilities (air conditioning, Wi-Fi, parking, accessibility)',
      'How you register foreign guests, and the invoice details we should use',
      'A named contact for reservations, reachable by phone, WhatsApp and email'],
      services: 'accommodation of guests sent by the Operator, with breakfast and the other services stated in each confirmation',
      standards: ['Rooms are clean, safe and as described, with working air conditioning or heating, hot water and Wi-Fi.', 'Foreign guests are registered as the law requires, and the Partner gives the Operator the registration confirmation on request.', 'Reserved rooms are held until the agreed check-in time; if the Partner cannot honour a booking it offers an equal or better hotel at its own cost.'],
      annex: ['Room category | single | double | triple | low season | high season | breakfast'] },
    guide: { who: 'licensed guides', one: 'guide', short: 'guiding', asks: [
      'Your guide licence number and validity, and the languages you guide in',
      'Your full-day (up to 8 hours) and half-day (up to 4 hours) rates, for individual guests and for groups of up to 10 and up to 20',
      'Surcharges for airport meetings, evening work, public holidays and trips outside the city',
      'Your specialisations (history, architecture, crafts, food, photography)',
      'Your experience with museums and monuments and their entrance procedures',
      'Your availability calendar, and how far ahead you need a confirmation',
      'Your cancellation conditions and how you prefer to be paid',
      'First-aid training or insurance you hold, and references from other operators'],
      services: 'guided tours in Samarkand and its surroundings for the guests sent by the Operator, in the languages stated in each confirmation',
      standards: ['The guide holds a valid licence for the whole term and carries it during tours.', 'The guide is punctual, well informed, respectful of guests and of religious sites, and follows the programme in the confirmation.', 'The guide never sells services or collects payments from guests on his or her own account, and does not take guests to shops for commission without the Operator’s knowledge.'],
      annex: ['Service | language | individual | group up to 10 | group up to 20 | surcharges'] },
    transport: { who: 'transport providers', one: 'transport provider', short: 'transport', asks: [
      'Your vehicle types, seat numbers, model years and photographs (sedan, minivan, minibus, bus)',
      'Your rates for airport and railway-station transfers, city use per hour and per day, and intercity trips by route or by kilometre',
      'Whether rates include fuel, driver, parking and waiting time, and the free waiting time at airports',
      'Driver languages and experience; air conditioning and child seats',
      'Vehicle insurance, technical inspection and licences',
      'Surcharges for night, holiday and out-of-hours service',
      'Your cancellation and no-show conditions',
      'A named dispatcher reachable by phone, WhatsApp and email'],
      services: 'transfers, city transport and intercity trips for the guests sent by the Operator, as stated in each confirmation',
      standards: ['Vehicles are clean, roadworthy, air-conditioned and insured, with a valid technical inspection.', 'Drivers are licensed, polite, punctual and follow safe-driving rules; the Partner replaces a vehicle or driver at its own cost if either is unavailable.', 'Pickup is at the agreed place and time, with a name sign at airports; the driver tracks flights and waits at least 60 minutes after landing at no extra charge.'],
      annex: ['Vehicle | seats | airport transfer | city per hour | city per day | intercity per route / km'] },
  },
  uz: {
    hotel: { who: 'mehmonxona va mehmon uylari', one: 'mehmonxona', short: 'joylashtirish', asks: [
      'Bir, ikki va uch kishilik xona uchun past va yuqori mavsumdagi bir kecha uchun netto (shartnoma) narxlaringiz',
      'Nonushta narxga kiritilganmi va boshqa ovqatlar narxi',
      '10 va undan kʻp mehmonlar uchun guruh narxlari hamda bepul xona siyosati (masalan, har 15 tʻlovchiga bitta bepul xona)',
      'Joylashish va chiqish vaqtlari, erta kelish yoki kech ketish imkoniyatlari',
      'Bekor qilish va kelmaslik shartlaringiz hamda biz qancha oldin xabar berishimiz kerakligi',
      'Xona toifalari, xonalar soni va qulayliklar (konditsioner, Wi-Fi, tʻxtash joyi, imkoniyati cheklanganlar uchun qulaylik)',
      'Chet ellik mehmonlarni qanday rʻyxatdan ʻtkazishingiz va hisob-faktura uchun rekvizitlar',
      'Bron bʻyicha masʼul shaxs — telefon, WhatsApp va elektron pochta orqali aloqada'],
      services: 'Operator yuborgan mehmonlarni joylashtirish, nonushta va har bir tasdiqda kʻrsatilgan boshqa xizmatlar',
      standards: ['Xonalar toza, xavfsiz va tavsifga mos, ishlaydigan konditsioner yoki isitish, issiq suv va Wi-Fi bilan.', 'Chet ellik mehmonlar qonun talab qilganidek rʻyxatdan ʻtkaziladi va Hamkor sʻrov bʻyicha Operatorga rʻyxatdan ʻtganlik tasdiʻini beradi.', 'Band qilingan xonalar kelishilgan joylashish vaqtigacha saqlanadi; Hamkor bronni bajara olmasa, ʻz hisobidan teng yoki yaxshiroq mehmonxona taklif etadi.'],
      annex: ['Xona toifasi | 1 kishilik | 2 kishilik | 3 kishilik | past mavsum | yuqori mavsum | nonushta'] },
    guide: { who: 'litsenziyali gidlar', one: 'gid', short: 'gidlik xizmati', asks: [
      'Gid litsenziyangiz raqami va amal qilish muddati hamda qaysi tillarda ishlashingiz',
      'Tʻliq kun (8 soatgacha) va yarim kun (4 soatgacha) narxlaringiz — yakka mehmonlar hamda 10 va 20 kishigacha guruhlar uchun',
      'Aeroportda kutib olish, kechki ish, bayram kunlari va shahardan tashqari safarlar uchun qʻshimcha haq',
      'Mutaxassisliklaringiz (tarix, meʼmorchilik, hunarmandchilik, taomlar, fotosuratlar)',
      'Muzey va yodgorliklar hamda ularga kirish tartibi bʻyicha tajribangiz',
      'Bandlik taqvimingiz va tasdiqni qancha oldin bilishingiz kerakligi',
      'Bekor qilish shartlaringiz va qanday tʻlov olishni afzal kʻrishingiz',
      'Birinchi yordam kursi yoki suʻurtangiz hamda boshqa operatorlardan tavsiyalar'],
      services: 'Operator yuborgan mehmonlar uchun Samarqand va uning atrofida har bir tasdiqda kʻrsatilgan tillarda ekskursiya xizmati',
      standards: ['Gid butun muddat davomida amaldagi litsenziyaga ega va ekskursiya vaqtida uni ʻzi bilan olib yuradi.', 'Gid vaqtida keladi, bilimli, mehmonlar va diniy joylarga hurmat bilan munosabatda bʻladi hamda tasdiqdagi dasturga amal qiladi.', 'Gid mehmonlarga ʻz nomidan xizmat sotmaydi va tʻlov yiʻmaydi hamda Operatorga maʼlum qilmasdan komissiya evaziga dʻkonlarga olib bormaydi.'],
      annex: ['Xizmat | til | yakka | 10 kishigacha guruh | 20 kishigacha guruh | qʻshimcha haq'] },
    transport: { who: 'transport xizmati kʻrsatuvchilar', one: 'transport xizmati kʻrsatuvchi', short: 'transport', asks: [
      'Avtomobil turlari, ʻrindiqlar soni, ishlab chiqarilgan yili va suratlari (sedan, miniven, mikroavtobus, avtobus)',
      'Aeroport va vokzal transferlari, shahar bʻylab soatiga va kuniga hamda shaharlararo qatnov (yʻnalish yoki kilometr bʻyicha) narxlaringiz',
      'Narxga yoqilʻi, haydovchi, tʻxtash joyi va kutish vaqti kiritilganmi hamda aeroportdagi bepul kutish vaqti',
      'Haydovchilarning tillari va tajribasi; konditsioner va bolalar ʻrindiʻi',
      'Avtomobil suʻurtasi, texnik kʻrik va litsenziyalar',
      'Tungi, bayram va ish vaqtidan tashqari xizmat uchun qʻshimcha haq',
      'Bekor qilish va kelmaslik shartlaringiz',
      'Dispetcher — telefon, WhatsApp va elektron pochta orqali aloqada'],
      services: 'Operator yuborgan mehmonlar uchun har bir tasdiqda kʻrsatilgan transferlar, shahar transporti va shaharlararo qatnovlar',
      standards: ['Avtomobillar toza, yurishga yaroqli, konditsionerli va suʻurtalangan, amaldagi texnik kʻrikka ega.', 'Haydovchilar litsenziyali, xushmuomala, vaqtida keladi va xavfsiz haydash qoidalariga rioya qiladi; avtomobil yoki haydovchi bʻlmasa, Hamkor ʻz hisobidan almashtiradi.', 'Kutib olish kelishilgan joy va vaqtda, aeroportda ismi yozilgan lavha bilan amalga oshiriladi; haydovchi reysni kuzatadi va qʻnishdan keyin kamida 60 daqiqa qʻshimcha haqsiz kutadi.'],
      annex: ['Avtomobil | ʻrindiqlar | aeroport transferi | shahar soatiga | shahar kuniga | shaharlararo yʻnalish / km'] },
  },
  ru: {
    hotel: { who: 'отели и гостевые дома', one: 'отель', short: 'размещение', asks: [
      'Ваши нетто-тарифы (контрактные) за номер в сутки при одноместном, двухместном и трёхместном размещении в низкий и высокий сезон',
      'Включён ли завтрак и стоимость других приёмов пищи',
      'Групповые тарифы от 10 гостей и политика бесплатного номера (например, один бесплатный на 15 платящих)',
      'Время заезда и выезда, возможности раннего заезда и позднего выезда',
      'Ваши условия отмены и незаезда и срок, за который мы должны уведомлять',
      'Категории номеров, их количество и удобства (кондиционер, Wi-Fi, парковка, доступность)',
      'Как вы регистрируете иностранных гостей и реквизиты для выставления счетов',
      'Ответственное лицо по бронированию — на связи по телефону, WhatsApp и почте'],
      services: 'размещение гостей, направленных Оператором, с завтраком и другими услугами, указанными в каждом подтверждении',
      standards: ['Номера чистые, безопасные и соответствуют описанию, с исправным кондиционером или отоплением, горячей водой и Wi-Fi.', 'Иностранные гости регистрируются, как требует закон, и Партнёр по запросу передаёт Оператору подтверждение регистрации.', 'Забронированные номера удерживаются до согласованного времени заезда; если Партнёр не может выполнить бронь, он за свой счёт предоставляет равноценный или лучший отель.'],
      annex: ['Категория номера | одноместный | двухместный | трёхместный | низкий сезон | высокий сезон | завтрак'] },
    guide: { who: 'лицензированные гиды', one: 'гид', short: 'гидовские услуги', asks: [
      'Номер вашей лицензии гида, срок её действия и языки, на которых вы работаете',
      'Ставки за полный день (до 8 часов) и полдня (до 4 часов) — для индивидуальных гостей и групп до 10 и до 20 человек',
      'Доплаты за встречу в аэропорту, вечернюю работу, праздничные дни и поездки за город',
      'Ваши специализации (история, архитектура, ремёсла, кухня, фотография)',
      'Ваш опыт работы с музеями и памятниками и порядок входа на них',
      'Ваш календарь занятости и за сколько вам нужно подтверждение',
      'Ваши условия отмены и предпочтительный способ оплаты',
      'Курсы первой помощи или страховка и рекомендации от других операторов'],
      services: 'экскурсионное обслуживание в Самарканде и окрестностях для гостей, направленных Оператором, на языках, указанных в каждом подтверждении',
      standards: ['Гид имеет действующую лицензию на весь срок и носит её с собой во время экскурсий.', 'Гид пунктуален, хорошо информирован, уважителен к гостям и религиозным местам и следует программе из подтверждения.', 'Гид не продаёт гостям услуги и не принимает оплату от своего имени и не возит гостей в магазины за комиссию без ведома Оператора.'],
      annex: ['Услуга | язык | индивидуально | группа до 10 | группа до 20 | доплаты'] },
    transport: { who: 'транспортные компании', one: 'транспортная компания', short: 'транспорт', asks: [
      'Типы автомобилей, число мест, год выпуска и фотографии (седан, минивэн, микроавтобус, автобус)',
      'Ваши тарифы на трансферы из аэропорта и вокзала, по городу — за час и за день, и межгород — по маршруту или за километр',
      'Включены ли в тариф топливо, водитель, парковка и ожидание, и сколько бесплатного ожидания в аэропорту',
      'Языки и опыт водителей; кондиционер и детские кресла',
      'Страховка автомобилей, техосмотр и лицензии',
      'Доплаты за ночное, праздничное и внеурочное обслуживание',
      'Ваши условия отмены и неявки',
      'Диспетчер — на связи по телефону, WhatsApp и почте'],
      services: 'трансферы, городские и междугородние перевозки гостей, направленных Оператором, как указано в каждом подтверждении',
      standards: ['Автомобили чистые, исправные, с кондиционером и страховкой и действующим техосмотром.', 'Водители имеют права, вежливы, пунктуальны и соблюдают правила безопасного вождения; если автомобиль или водитель недоступен, Партнёр заменяет его за свой счёт.', 'Подача в согласованном месте и в срок, в аэропорту — с табличкой с именем; водитель отслеживает рейс и ждёт не менее 60 минут после посадки без доплаты.'],
      annex: ['Автомобиль | мест | трансфер из аэропорта | город за час | город за день | межгород маршрут / км'] },
  },
}

const COMMON = {
  en: {
    offers: (d) => [
      'Steady bookings from international guests throughout the season, with forecasts shared in advance',
      'Written reservations stating names, dates, number of guests and special requests',
      `Payment by bank transfer within ${d.paymentDays} days of the invoice, without delays or hidden deductions`,
      'Your business presented on our website and in our itineraries, with your own photographs and description',
      'Respectful, long-term cooperation, honest feedback from our guests and a direct contact at our office'],
    greeting: (d) => (d.contact ? `Dear ${d.contact},` : 'Dear Sir or Madam,'),
    close: 'Yours sincerely,',
    attn: 'Attention',
  },
  uz: {
    offers: (d) => [
      'Butun mavsum davomida xalqaro mehmonlardan barqaror bronlar, prognozlarni oldindan ulashish',
      'Ismlar, sanalar, mehmonlar soni va maxsus istaklar kʻrsatilgan yozma bronlar',
      `Hisob-fakturadan keyin ${d.paymentDays} kun ichida bank ʻtkazmasi orqali tʻlov, kechikishlarsiz va yashirin ushlab qolishlarsiz`,
      'Biznesingizni veb-saytimiz va marshrutlarimizda ʻz suratlaringiz va tavsifingiz bilan taqdim etish',
      'Hurmatli, uzoq muddatli hamkorlik, mehmonlarimizning halol fikrlari va ofisimizda tʻʻridan-tʻʻri aloqa shaxsi'],
    greeting: (d) => (d.contact ? `Hurmatli ${d.contact},` : 'Hurmatli hamkasb,'),
    close: 'Hurmat bilan,',
    attn: 'Diqqatga',
  },
  ru: {
    offers: (d) => [
      'Стабильные бронирования от иностранных гостей в течение всего сезона и заблаговременные прогнозы',
      'Письменные заявки с указанием имён, дат, числа гостей и особых пожеланий',
      `Оплату банковским переводом в течение ${d.paymentDays} дней после выставления счёта, без задержек и скрытых удержаний`,
      'Презентацию вашего бизнеса на нашем сайте и в маршрутах с вашими фотографиями и описанием',
      'Уважительное долгосрочное сотрудничество, честные отзывы наших гостей и прямой контакт в нашем офисе'],
    greeting: (d) => (d.contact ? `Уважаемый(ая) ${d.contact}!` : 'Уважаемые коллеги!'),
    close: 'С уважением,',
    attn: 'Вниманию',
  },
}

const signature = (d, lang) => `${blank(d.ourName)}\n${blank(d.ourRole, lang === 'ru' ? 'Должность' : lang === 'uz' ? 'Lavozim' : 'Position')}\n${d.company}\n${[d.ourPhone, d.ourEmail].filter(Boolean).join(' · ')}`

const TEXT = {
  en: {
    proposal: (d, k, c) => `${when(d.date, 'en')}

To: ${blank(d.partner)}${d.contact ? `\nAttention: ${d.contact}` : ''}
${blank(d.city, 'Samarkand')}

**Subject: Proposal for cooperation — ${d.company} and ${blank(d.partner)}**

${c.greeting(d)}

${d.company} is a tour operator based in Samarkand. We design private and small-group journeys, cultural experiences, guided tours and airport transfers across Uzbekistan for guests from Europe, Asia and North America.

We are building a network of reliable ${k.who} in ${blank(d.city, 'Samarkand')} that we can recommend to our guests with confidence, and we would like to invite ${blank(d.partner)} to become one of our partners.

**What we offer you**
${list(c.offers(d))}

**What we would ask of you**
${list(k.asks)}

**Proposed terms**
${list([`Net contract rates valid for the season, confirmed in writing, with any change notified at least 30 days ahead`, d.commission ? `A commission or discount of ${d.commission}% on rates, where this applies to your services` : 'No commission is requested unless you offer one', `Reservations confirmed in writing by both sides; payment within ${d.paymentDays} days of the invoice`, `A cooperation agreement valid for ${d.termMonths} months, renewable by consent`])}

**Next steps**
${steps([`Please send us the information above by ${when(d.deadline, 'en')}.`, 'We will arrange a call or a meeting at your premises at a time that suits you.', 'If we agree, we will sign the cooperation agreement (a draft is available on request) and start sending bookings.'])}

Thank you for your time. We would be glad to work with you and to show our guests the best of ${blank(d.city, 'Samarkand')}.

${c.close}

${signature(d, 'en')}`,

    email: (d, k, c) => `**Subject: Cooperation with ${d.company} — ${k.short} in ${blank(d.city, 'Samarkand')}**

${c.greeting(d)}

My name is ${blank(d.ourName, '[name]')} from ${d.company}, a tour operator in Samarkand working with international guests. We are looking for reliable ${k.who} to cooperate with, and ${blank(d.partner)} was recommended to us.

We would like to know your current rates and availability, and to discuss regular cooperation: written reservations, clear forecasts and payment within ${d.paymentDays} days of the invoice.

Could you please send us your net rates for the coming season and a short description of your ${k.short} by ${when(d.deadline, 'en')}? A detailed list of what we need is attached. I would also be glad to arrange a short call or visit.

Thank you very much. I look forward to your reply.

${c.close}

${signature(d, 'en')}`,

    inquiry: (d, k, c) => `${when(d.date, 'en')}

To: ${blank(d.partner)}${d.contact ? `\nAttention: ${d.contact}` : ''}

**Subject: Request for rates and availability — ${k.short}, ${new Date(`${d.date || new Date().toISOString().slice(0, 10)}T12:00:00`).getFullYear()} season**

${c.greeting(d)}

${d.company} is planning programmes in ${blank(d.city, 'Samarkand')} for the coming season and would like to include ${blank(d.partner)}. To prepare our offers to guests, please send us your written rates and conditions.

**Please include**
${steps(k.asks)}

**How to reply**
${list([`Rates in US dollars per unit, stating the period of validity and what is included`, 'Any taxes, tourist fees or service charges shown separately', 'Your terms of payment and the invoice details to use', `Please reply by ${when(d.deadline, 'en')} to ${blank(d.ourEmail)}`])}

This request is for information and does not oblige either side to book. Once we have agreed rates, we will confirm each reservation in writing.

Thank you in advance for your prompt reply.

${c.close}

${signature(d, 'en')}`,

    agreement: (d, k) => `**DRAFT — to be reviewed by a lawyer before signing**

# COOPERATION AGREEMENT No. ______

Samarkand, ${when(d.date, 'en')}

**${d.company}** (“the Operator”), represented by ${blank(d.ourName)}, ${blank(d.ourRole, 'authorised representative')}, acting under ${blank(d.authority, 'the charter / power of attorney No. ____')}, registered address: ${blank(d.ourAddress)},

and **${blank(d.partner)}** (“the Partner”), represented by ${blank(d.contact)}, acting under ${blank(d.partnerAuthority, 'the charter / power of attorney No. ____')}, registered address: ${blank(d.partnerAddress)},

together “the Parties”, have agreed as follows.

## 1. Subject of the agreement
1.1. The Partner provides ${k.services} (“the Services”).
1.2. The Operator sends guests to the Partner and pays for the Services at the rates in Annex 1.
1.3. The Agreement is non-exclusive: each Party remains free to work with others.

## 2. Standards of service
${list(k.standards)}
2.1. The Partner holds all licences, registrations and insurance required by the law of the Republic of Uzbekistan for the Services and keeps them valid throughout the term.

## 3. Rates and reservations
3.1. The rates are in Annex 1, in US dollars, and include all taxes and fees unless stated. The Partner may change them for a new season by written notice at least 30 days ahead; confirmed reservations keep their confirmed rate.
3.2. The Operator sends reservation requests in writing (email or messenger). The Partner confirms or declines within 24 hours. A reservation exists once confirmed in writing, stating names, dates, services and price.
3.3. ${d.commission ? `The Partner grants the Operator a ${d.commission}% commission / discount on the rates in Annex 1.` : 'No commission is payable unless the Parties agree it in writing.'}

## 4. Payment
4.1. The Partner issues an invoice after the Services are delivered. The Operator pays it by bank transfer within ${d.paymentDays} days of receiving it, in US dollars or in Uzbek soums at the rate of the Central Bank on the payment date.
4.2. Guests pay for their own extras directly. The Partner does not charge guests for anything included in the confirmation.
4.3. Disputed amounts are paid in part if undisputed; the disputed part is settled promptly after review.

## 5. Changes, cancellation and no-show
5.1. The Operator may cancel a confirmed reservation free of charge up to ${d.cancelHours} hours before the start of the Services. Later cancellation and no-show are charged as set out in Annex 1 (by default the first night / one day of the Service).
5.2. If the Partner cannot deliver a confirmed Service, it informs the Operator at once and, at its own cost, provides an equal or better replacement, or compensates the Operator’s reasonable additional costs.

## 6. Quality and complaints
6.1. The Operator tells the Partner about any complaint as soon as it arises, so it can be solved on the spot. The Partner answers written complaints within 7 days.
6.2. The Parties review quality at least once a season. Repeated serious failures give the Operator the right to stop sending guests.

## 7. Liability
7.1. Each Party is liable for its own breaches under the law of the Republic of Uzbekistan.
7.2. The Partner is responsible for the safety of guests and property while in its care and for its staff, premises and vehicles. The Operator is not liable for the Partner’s acts or omissions.
7.3. Neither Party is liable for indirect loss, except where the law does not allow this.

## 8. Confidentiality and personal data
8.1. The Parties keep the rates, guest lists and business information received under this Agreement confidential during its term and for 3 years after.
8.2. Guest data is used only to deliver the Services and meet legal duties, protected as required by the law on personal data, and deleted when no longer needed.

## 9. Force majeure
9.1. A Party is not liable for failure caused by events beyond its reasonable control (natural disaster, epidemic, war, government action and similar) if it notifies the other promptly. If such an event lasts more than 60 days, either Party may terminate.

## 10. Term and termination
10.1. The Agreement starts on the date above and lasts ${d.termMonths} months. It renews automatically for the same period unless a Party gives 30 days’ written notice.
10.2. Either Party may end it at once for serious breach that is not remedied within 10 days of written notice. Confirmed reservations are still honoured.

## 11. Disputes and governing law
11.1. The Agreement is governed by the law of the Republic of Uzbekistan.
11.2. The Parties first try to settle disputes by negotiation. If that fails within 30 days, the dispute goes to the competent court of the Republic of Uzbekistan.

## 12. Final provisions
12.1. Changes are valid only in writing signed by both Parties. Annex 1 is part of the Agreement.
12.2. The Agreement is made in two copies of equal force, one for each Party.
12.3. Notices are sent to the contacts below and are effective on receipt.

## 13. Details and signatures
**The Operator — ${d.company}**
Address: ${blank(d.ourAddress)}
Phone: ${blank(d.ourPhone)} · Email: ${blank(d.ourEmail)}
Bank details: ________________
Signature: ____________  /  ${blank(d.ourName)}  /  Stamp

**The Partner — ${blank(d.partner)}**
Address: ${blank(d.partnerAddress)}
Phone / Email: ${blank(d.partnerContacts)}
Bank details: ________________
Signature: ____________  /  ${blank(d.contact)}  /  Stamp

## Annex 1 — Rates (US dollars)
${k.annex[0]}
____________________________________________
____________________________________________
____________________________________________
Valid from ____________ to ____________. Cancellation / no-show charge: ____________.`,
  },

  uz: {
    proposal: (d, k, c) => `${when(d.date, 'uz')}

Kimga: ${blank(d.partner)}${d.contact ? `\n${c.attn}: ${d.contact}` : ''}
${blank(d.city, 'Samarqand')}

**Mavzu: Hamkorlik taklifi — ${d.company} va ${blank(d.partner)}**

${c.greeting(d)}

${d.company} — Samarqandda joylashgan turoperator. Biz Yevropa, Osiyo va Shimoliy Amerikadan kelgan mehmonlar uchun ʻzbekiston bʻylab shaxsiy va kichik guruh sayohatlari, madaniy tajribalar, ekskursiyalar va aeroport transferlarini tashkil etamiz.

Biz ${blank(d.city, 'Samarqand')}da mehmonlarimizga ishonch bilan tavsiya eta oladigan ishonchli ${k.who} tarmoʻini yaratmoqdamiz va ${blank(d.partner)}ni hamkorlarimizdan biri bʻlishga taklif qilamiz.

**Biz sizga nimani taklif qilamiz**
${list(c.offers(d))}

**Sizdan nimani sʻraymiz**
${list(k.asks)}

**Taklif etilayotgan shartlar**
${list([`Mavsum uchun amal qiladigan, yozma tasdiqlangan netto narxlar; har qanday ʻzgarish kamida 30 kun oldin xabar qilinadi`, d.commission ? `Xizmatlaringizga tegishli bʻlsa, narxlardan ${d.commission}% komissiya yoki chegirma` : 'Siz ʻzingiz taklif qilmasangiz, komissiya sʻralmaydi', `Bronlar ikki tomonlama yozma tasdiqlanadi; tʻlov hisob-fakturadan keyin ${d.paymentDays} kun ichida`, `${d.termMonths} oyga amal qiladigan, kelishuv bʻyicha uzaytiriladigan hamkorlik shartnomasi`])}

**Keyingi qadamlar**
${steps([`Iltimos, yuqoridagi maʼlumotlarni ${when(d.deadline, 'uz')} gacha yuboring.`, 'Sizga qulay vaqtda qʻnʻiroq yoki ʻz joyingizda uchrashuv tashkil etamiz.', 'Kelishsak, hamkorlik shartnomasini imzolaymiz (loyihasi sʻrov bʻyicha beriladi) va bronlar yubora boshlaymiz.'])}

Vaqtingizni ajratganingiz uchun rahmat. Siz bilan ishlashdan va mehmonlarimizga ${blank(d.city, 'Samarqand')}ning eng yaxshisini kʻrsatishdan xursand bʻlamiz.

${c.close}

${signature(d, 'uz')}`,

    email: (d, k, c) => `**Mavzu: ${d.company} bilan hamkorlik — ${blank(d.city, 'Samarqand')}da ${k.short}**

${c.greeting(d)}

Men ${d.company} turoperatoridan ${blank(d.ourName, '[ism]')}man; biz Samarqandda xalqaro mehmonlar bilan ishlaymiz. Hamkorlik qilish uchun ishonchli ${k.who} izlayapmiz va ${blank(d.partner)} bizga tavsiya etildi.

Joriy narxlaringiz va bandligingizni bilishni hamda muntazam hamkorlikni muhokama qilishni istaymiz: yozma bronlar, aniq prognozlar va hisob-fakturadan keyin ${d.paymentDays} kun ichida tʻlov.

Iltimos, kelgusi mavsum uchun netto narxlaringizni va ${k.short} haqida qisqa tavsifni ${when(d.deadline, 'uz')} gacha yuboring. Kerakli maʼlumotlarning batafsil rʻyxati ilova qilingan. Qisqa qʻnʻiroq yoki tashrif tashkil etishdan ham xursand bʻlardim.

Katta rahmat. Javobingizni kutaman.

${c.close}

${signature(d, 'uz')}`,

    inquiry: (d, k, c) => `${when(d.date, 'uz')}

Kimga: ${blank(d.partner)}${d.contact ? `\n${c.attn}: ${d.contact}` : ''}

**Mavzu: Narxlar va bandlik sʻrovi — ${k.short}, ${new Date(`${d.date || new Date().toISOString().slice(0, 10)}T12:00:00`).getFullYear()}-yil mavsumi**

${c.greeting(d)}

${d.company} kelgusi mavsum uchun ${blank(d.city, 'Samarqand')}da dasturlar rejalashtirmoqda va ${blank(d.partner)}ni ham qʻshmoqchi. Mehmonlarga takliflar tayyorlash uchun, iltimos, yozma narxlar va shartlaringizni yuboring.

**Iltimos, quyidagilarni kʻrsating**
${steps(k.asks)}

**Qanday javob berish kerak**
${list([`Narxlar AQSH dollarida, birlik uchun, amal qilish muddati va nimalar kiritilgani kʻrsatilgan holda`, 'Soliq, turistik yiʻim yoki xizmat haqi alohida kʻrsatilsin', 'Tʻlov shartlaringiz va hisob-faktura uchun rekvizitlar', `Iltimos, ${when(d.deadline, 'uz')} gacha ${blank(d.ourEmail)} manziliga javob bering`])}

Ushbu sʻrov axborot uchun bʻlib, hech bir tomonni bron qilishga majburlamaydi. Narxlar kelishilgach, har bir bronni yozma tasdiqlaymiz.

Tezkor javobingiz uchun oldindan rahmat.

${c.close}

${signature(d, 'uz')}`,

    agreement: (d, k) => `**LOYIHA — imzolashdan oldin yurist tomonidan kʻrib chiqilishi kerak**

# HAMKORLIK SHARTNOMASI № ______

Samarqand, ${when(d.date, 'uz')}

**${d.company}** (“Operator”), ${blank(d.ourName)}, ${blank(d.ourRole, 'vakolatli vakil')} timsolida, ${blank(d.authority, 'Nizom / ishonchnoma № ____')} asosida harakat qiladi, yuridik manzili: ${blank(d.ourAddress)},

va **${blank(d.partner)}** (“Hamkor”), ${blank(d.contact)} timsolida, ${blank(d.partnerAuthority, 'Nizom / ishonchnoma № ____')} asosida harakat qiladi, yuridik manzili: ${blank(d.partnerAddress)},

birgalikda “Tomonlar”, quyidagilar haqida kelishdilar.

## 1. Shartnoma predmeti
1.1. Hamkor ${k.services} (“Xizmatlar”) bʻyicha xizmat kʻrsatadi.
1.2. Operator mehmonlarni Hamkorga yuboradi va Xizmatlar uchun 1-ilovadagi narxlarda tʻlaydi.
1.3. Shartnoma eksklyuziv emas: har bir Tomon boshqalar bilan ishlash huquqini saqlab qoladi.

## 2. Xizmat kʻrsatish standartlari
${list(k.standards)}
2.1. Hamkor Xizmatlar uchun ʻzbekiston Respublikasi qonunchiligi talab qiladigan barcha litsenziya, rʻyxatdan ʻtish va suʻurtaga ega bʻlib, ularni butun muddat davomida amalda saqlaydi.

## 3. Narxlar va bronlar
3.1. Narxlar 1-ilovada, AQSH dollarida va, kʻrsatilmagan bʻlsa, barcha soliq va yiʻimlarni ʻz ichiga oladi. Hamkor ularni yangi mavsum uchun kamida 30 kun oldin yozma xabar berib ʻzgartirishi mumkin; tasdiqlangan bronlar tasdiqlangan narxini saqlaydi.
3.2. Operator bron sʻrovlarini yozma (elektron pochta yoki messenjer) yuboradi. Hamkor 24 soat ichida tasdiqlaydi yoki rad etadi. Bron ismlar, sanalar, xizmatlar va narx kʻrsatilgan yozma tasdiqdan keyin amalga oshgan hisoblanadi.
3.3. ${d.commission ? `Hamkor Operatorga 1-ilovadagi narxlardan ${d.commission}% komissiya / chegirma beradi.` : 'Tomonlar yozma kelishmaguncha komissiya tʻlanmaydi.'}

## 4. Tʻlov
4.1. Hamkor Xizmatlar kʻrsatilgandan keyin hisob-faktura chiqaradi. Operator uni olgandan keyin ${d.paymentDays} kun ichida bank ʻtkazmasi orqali, AQSH dollarida yoki tʻlov kuni Markaziy bank kursi bʻyicha sʻmda tʻlaydi.
4.2. Mehmonlar qʻshimcha xarajatlarini bevosita ʻzlari tʻlaydi. Hamkor tasdiqda kiritilgan hech narsa uchun mehmonlardan pul olmaydi.
4.3. Bahsli summalar bʻyicha bahssiz qismi tʻlanadi; bahsli qismi kʻrib chiqilgach, tez orada hal etiladi.

## 5. ʻzgartirish, bekor qilish va kelmaslik
5.1. Operator tasdiqlangan bronni Xizmatlar boshlanishiga ${d.cancelHours} soat qolgunga qadar bepul bekor qilishi mumkin. Keyingi bekor qilish va kelmaslik 1-ilovada kʻrsatilganidek undiriladi (odatda birinchi tun / Xizmatning bir kuni).
5.2. Hamkor tasdiqlangan Xizmatni kʻrsata olmasa, Operatorga darhol xabar beradi va ʻz hisobidan teng yoki yaxshiroq almashtirishni taʼminlaydi yoki Operatorning oqilona qʻshimcha xarajatlarini qoplaydi.

## 6. Sifat va shikoyatlar
6.1. Operator har qanday shikoyat haqida u paydo bʻlishi bilan Hamkorga xabar beradi, shunda u joyida hal qilinadi. Hamkor yozma shikoyatlarga 7 kun ichida javob beradi.
6.2. Tomonlar sifatni kamida mavsumda bir marta kʻrib chiqadi. Takroriy jiddiy kamchiliklar Operatorga mehmon yuborishni tʻxtatish huquqini beradi.

## 7. Javobgarlik
7.1. Har bir Tomon ʻz buzilishlari uchun ʻzbekiston Respublikasi qonunchiligiga muvofiq javob beradi.
7.2. Hamkor ʻz qaramoʻidagi mehmonlar va mulk xavfsizligi, xodimlari, binolari va transporti uchun javobgar. Operator Hamkorning harakat yoki harakatsizligi uchun javobgar emas.
7.3. Qonun yʻl qʻymagan hollardan tashqari, Tomonlar bilvosita zarar uchun javobgar emas.

## 8. Konfidensiallik va shaxsiy maʼlumotlar
8.1. Tomonlar ushbu Shartnoma bʻyicha olingan narxlar, mehmonlar rʻyxati va tijoriy maʼlumotlarni uning muddati davomida va undan keyin 3 yil sir saqlaydi.
8.2. Mehmonlar maʼlumoti faqat Xizmatlarni kʻrsatish va qonuniy majburiyatlarni bajarish uchun ishlatiladi, shaxsiy maʼlumotlar tʻʻrisidagi qonun talab qilganidek himoyalanadi va keraksiz bʻlganda ʻchiriladi.

## 9. Fors-major
9.1. Tomon ʻzining oqilona nazoratidan tashqari hodisalar (tabiiy ofat, epidemiya, urush, davlat qarorlari va shunga ʻxshash) sabab bajarmaganligi uchun, ikkinchi Tomonni tezda xabardor qilsa, javobgar emas. Bunday hodisa 60 kundan ortiq davom etsa, istalgan Tomon Shartnomani bekor qilishi mumkin.

## 10. Muddat va bekor qilish
10.1. Shartnoma yuqoridagi sanadan kuchga kiradi va ${d.termMonths} oy amal qiladi. Tomon 30 kun oldin yozma xabar bermasa, ʻsha muddatga avtomatik uzaytiriladi.
10.2. Yozma ogohlantirishdan keyin 10 kun ichida bartaraf etilmagan jiddiy buzilishda istalgan Tomon Shartnomani darhol bekor qilishi mumkin. Tasdiqlangan bronlar baribir bajariladi.

## 11. Nizolar va qʻllaniladigan huquq
11.1. Shartnomaga ʻzbekiston Respublikasi qonunchiligi qʻllaniladi.
11.2. Tomonlar nizolarni avval muzokaralar orqali hal etishga harakat qiladi. 30 kun ichida kelishilmasa, nizo ʻzbekiston Respublikasining vakolatli sudiga beriladi.

## 12. Yakuniy qoidalar
12.1. ʻzgartirishlar faqat ikkala Tomon imzolagan yozma shaklda haqiqiy. 1-ilova Shartnomaning ajralmas qismidir.
12.2. Shartnoma teng yuridik kuchga ega ikki nusxada tuzilgan, har bir Tomon uchun bittadan.
12.3. Xabarnomalar quyidagi aloqa maʼlumotlariga yuboriladi va olingan paytdan kuchga kiradi.

## 13. Rekvizitlar va imzolar
**Operator — ${d.company}**
Manzil: ${blank(d.ourAddress)}
Telefon: ${blank(d.ourPhone)} · Elektron pochta: ${blank(d.ourEmail)}
Bank rekvizitlari: ________________
Imzo: ____________  /  ${blank(d.ourName)}  /  Muhr

**Hamkor — ${blank(d.partner)}**
Manzil: ${blank(d.partnerAddress)}
Telefon / Elektron pochta: ${blank(d.partnerContacts)}
Bank rekvizitlari: ________________
Imzo: ____________  /  ${blank(d.contact)}  /  Muhr

## 1-ilova — Narxlar (AQSH dollarida)
${k.annex[0]}
____________________________________________
____________________________________________
____________________________________________
Amal qilish muddati ____________ dan ____________ gacha. Bekor qilish / kelmaslik tʻlovi: ____________.`,
  },

  ru: {
    proposal: (d, k, c) => `${when(d.date, 'ru')}

Кому: ${blank(d.partner)}${d.contact ? `\n${c.attn}: ${d.contact}` : ''}
${blank(d.city, 'Самарканд')}

**Тема: Предложение о сотрудничестве — ${d.company} и ${blank(d.partner)}**

${c.greeting(d)}

${d.company} — туроператор из Самарканда. Мы организуем индивидуальные и мини-групповые путешествия, культурные программы, экскурсии и трансферы из аэропортов по всему Узбекистану для гостей из Европы, Азии и Северной Америки.

Мы создаём сеть надёжных партнёров — ${k.who} в городе ${blank(d.city, 'Самарканд')}, которых можем с уверенностью рекомендовать гостям, и приглашаем ${blank(d.partner)} стать одним из наших партнёров.

**Что мы предлагаем вам**
${list(c.offers(d))}

**Что мы просим от вас**
${list(k.asks)}

**Предлагаемые условия**
${list([`Нетто-тарифы на сезон, подтверждённые письменно; об изменениях сообщается не менее чем за 30 дней`, d.commission ? `Комиссия или скидка ${d.commission}% от тарифов, если это применимо к вашим услугам` : 'Комиссия не запрашивается, если вы сами её не предложите', `Бронирования подтверждаются письменно обеими сторонами; оплата в течение ${d.paymentDays} дней после выставления счёта`, `Соглашение о сотрудничестве сроком на ${d.termMonths} мес. с возможностью продления по согласию`])}

**Следующие шаги**
${steps([`Пожалуйста, пришлите указанную выше информацию до ${when(d.deadline, 'ru')}.`, 'Мы организуем звонок или встречу у вас в удобное для вас время.', 'При согласии подпишем соглашение о сотрудничестве (проект предоставим по запросу) и начнём направлять бронирования.'])}

Благодарим за уделённое время. Будем рады работать с вами и показывать гостям лучшее в городе ${blank(d.city, 'Самарканд')}.

${c.close}

${signature(d, 'ru')}`,

    email: (d, k, c) => `**Тема: Сотрудничество с ${d.company} — ${k.short} в ${blank(d.city, 'Самарканде')}**

${c.greeting(d)}

Меня зовут ${blank(d.ourName, '[имя]')}, я представляю ${d.company} — туроператора из Самарканда, работающего с иностранными гостями. Мы ищем надёжных партнёров — ${k.who}, и нам порекомендовали ${blank(d.partner)}.

Хотели бы узнать ваши действующие тарифы и наличие мест, а также обсудить постоянное сотрудничество: письменные заявки, понятные прогнозы и оплата в течение ${d.paymentDays} дней после выставления счёта.

Пожалуйста, пришлите нам до ${when(d.deadline, 'ru')} нетто-тарифы на ближайший сезон и краткое описание вашего предложения (${k.short}). Подробный перечень необходимой информации — во вложении. Буду рад(а) организовать короткий звонок или визит.

Большое спасибо. Жду вашего ответа.

${c.close}

${signature(d, 'ru')}`,

    inquiry: (d, k, c) => `${when(d.date, 'ru')}

Кому: ${blank(d.partner)}${d.contact ? `\n${c.attn}: ${d.contact}` : ''}

**Тема: Запрос тарифов и наличия — ${k.short}, сезон ${new Date(`${d.date || new Date().toISOString().slice(0, 10)}T12:00:00`).getFullYear()} года**

${c.greeting(d)}

${d.company} планирует программы в городе ${blank(d.city, 'Самарканд')} на предстоящий сезон и хотела бы включить ${blank(d.partner)}. Чтобы подготовить предложения гостям, просим прислать ваши тарифы и условия в письменном виде.

**Пожалуйста, укажите**
${steps(k.asks)}

**Как ответить**
${list([`Тарифы в долларах США за единицу с указанием срока действия и того, что включено`, 'Налоги, туристические сборы или сервисные сборы — отдельно', 'Ваши условия оплаты и реквизиты для выставления счетов', `Просим ответить до ${when(d.deadline, 'ru')} на ${blank(d.ourEmail)}`])}

Этот запрос носит информационный характер и не обязывает стороны к бронированию. После согласования тарифов мы будем подтверждать каждое бронирование письменно.

Заранее благодарим за оперативный ответ.

${c.close}

${signature(d, 'ru')}`,

    agreement: (d, k) => `**ПРОЕКТ — перед подписанием должен быть проверен юристом**

# СОГЛАШЕНИЕ О СОТРУДНИЧЕСТВЕ № ______

г. Самарканд, ${when(d.date, 'ru')}

**${d.company}** (далее — «Оператор») в лице ${blank(d.ourName)}, ${blank(d.ourRole, 'уполномоченного представителя')}, действующего на основании ${blank(d.authority, 'Устава / доверенности № ____')}, юридический адрес: ${blank(d.ourAddress)},

и **${blank(d.partner)}** (далее — «Партнёр») в лице ${blank(d.contact)}, действующего на основании ${blank(d.partnerAuthority, 'Устава / доверенности № ____')}, юридический адрес: ${blank(d.partnerAddress)},

совместно именуемые «Стороны», договорились о нижеследующем.

## 1. Предмет соглашения
1.1. Партнёр оказывает услуги: ${k.services} («Услуги»).
1.2. Оператор направляет гостей Партнёру и оплачивает Услуги по тарифам из Приложения 1.
1.3. Соглашение не является эксклюзивным: каждая Сторона вправе работать с другими.

## 2. Стандарты обслуживания
${list(k.standards)}
2.1. Партнёр имеет все лицензии, регистрации и страховки, необходимые по законодательству Республики Узбекистан для оказания Услуг, и поддерживает их в силе весь срок.

## 3. Тарифы и бронирование
3.1. Тарифы указаны в Приложении 1 в долларах США и, если не указано иное, включают все налоги и сборы. Партнёр может изменить их на новый сезон, письменно уведомив не менее чем за 30 дней; подтверждённые бронирования сохраняют подтверждённый тариф.
3.2. Оператор направляет заявки письменно (почта или мессенджер). Партнёр подтверждает или отклоняет их в течение 24 часов. Бронирование считается состоявшимся после письменного подтверждения с указанием имён, дат, услуг и цены.
3.3. ${d.commission ? `Партнёр предоставляет Оператору комиссию / скидку ${d.commission}% от тарифов из Приложения 1.` : 'Комиссия не выплачивается, если Стороны не договорились об этом письменно.'}

## 4. Оплата
4.1. Партнёр выставляет счёт после оказания Услуг. Оператор оплачивает его банковским переводом в течение ${d.paymentDays} дней с момента получения в долларах США или в узбекских сумах по курсу Центрального банка на дату платежа.
4.2. Гости самостоятельно оплачивают свои дополнительные расходы. Партнёр не взимает с гостей плату за то, что включено в подтверждение.
4.3. При споре по сумме бесспорная часть оплачивается, а спорная — урегулируется в кратчайший срок после рассмотрения.

## 5. Изменение, отмена и незаезд
5.1. Оператор может бесплатно отменить подтверждённое бронирование не позднее чем за ${d.cancelHours} часов до начала Услуг. Более поздняя отмена и неявка оплачиваются, как указано в Приложении 1 (по умолчанию — первая ночь / один день Услуги).
5.2. Если Партнёр не может оказать подтверждённую Услугу, он немедленно сообщает Оператору и за свой счёт предоставляет равноценную или лучшую замену либо возмещает разумные дополнительные расходы Оператора.

## 6. Качество и претензии
6.1. Оператор сообщает Партнёру о любой претензии сразу, как она возникла, чтобы решить её на месте. Партнёр отвечает на письменные претензии в течение 7 дней.
6.2. Стороны оценивают качество не реже одного раза в сезон. Повторные серьёзные нарушения дают Оператору право прекратить направлять гостей.

## 7. Ответственность
7.1. Каждая Сторона отвечает за свои нарушения по законодательству Республики Узбекистан.
7.2. Партнёр отвечает за безопасность гостей и имущества, находящихся под его присмотром, а также за своих сотрудников, помещения и транспорт. Оператор не отвечает за действия или бездействие Партнёра.
7.3. Стороны не отвечают за косвенные убытки, кроме случаев, когда закон этого не допускает.

## 8. Конфиденциальность и персональные данные
8.1. Стороны сохраняют в тайне тарифы, списки гостей и коммерческую информацию, полученные по настоящему Соглашению, в течение его срока и 3 лет после.
8.2. Данные гостей используются только для оказания Услуг и выполнения требований закона, защищаются, как того требует закон о персональных данных, и удаляются, когда больше не нужны.

## 9. Форс-мажор
9.1. Сторона не отвечает за неисполнение, вызванное обстоятельствами вне её разумного контроля (стихийное бедствие, эпидемия, война, решения властей и подобное), если она незамедлительно уведомила другую Сторону. Если такое обстоятельство длится более 60 дней, любая Сторона вправе расторгнуть Соглашение.

## 10. Срок и расторжение
10.1. Соглашение вступает в силу с даты, указанной выше, и действует ${d.termMonths} мес. Оно автоматически продлевается на тот же срок, если одна из Сторон не уведомит письменно за 30 дней.
10.2. Любая Сторона может немедленно расторгнуть его при серьёзном нарушении, не устранённом в течение 10 дней после письменного уведомления. Подтверждённые бронирования всё равно исполняются.

## 11. Споры и применимое право
11.1. К Соглашению применяется законодательство Республики Узбекистан.
11.2. Стороны сначала стремятся урегулировать споры переговорами. Если в течение 30 дней согласия нет, спор передаётся в компетентный суд Республики Узбекистан.

## 12. Заключительные положения
12.1. Изменения действительны только в письменной форме, подписанной обеими Сторонами. Приложение 1 является неотъемлемой частью Соглашения.
12.2. Соглашение составлено в двух экземплярах равной юридической силы — по одному для каждой Стороны.
12.3. Уведомления направляются по указанным ниже контактам и вступают в силу с момента получения.

## 13. Реквизиты и подписи
**Оператор — ${d.company}**
Адрес: ${blank(d.ourAddress)}
Телефон: ${blank(d.ourPhone)} · Эл. почта: ${blank(d.ourEmail)}
Банковские реквизиты: ________________
Подпись: ____________  /  ${blank(d.ourName)}  /  М.П.

**Партнёр — ${blank(d.partner)}**
Адрес: ${blank(d.partnerAddress)}
Телефон / эл. почта: ${blank(d.partnerContacts)}
Банковские реквизиты: ________________
Подпись: ____________  /  ${blank(d.contact)}  /  М.П.

## Приложение 1 — Тарифы (доллары США)
${k.annex[0]}
____________________________________________
____________________________________________
____________________________________________
Действуют с ____________ по ____________. Штраф за отмену / незаезд: ____________.`,
  },
}

/* ---------- request for photographs and permission to publish them ---------- */
const PHOTO_ASKS = {
  en: {
    hotel: ['6 to 12 good photographs, landscape orientation, at least 1600 pixels wide: the building and entrance, a typical room and bathroom, the breakfast area, the courtyard or terrace',
      'Your current star class, room categories and the lowest usual nightly price, so that our website shows correct information'],
    guide: ['2 to 3 recent photographs of yourself guiding (a portrait and a group at a monument), at least 1600 pixels wide',
      'The languages you guide in and the places you know best, in two or three lines'],
    transport: ['6 to 10 good photographs of your vehicles, outside and inside, landscape orientation, at least 1600 pixels wide',
      'The vehicle models, the number of seats and the services you offer (airport transfers, daily hire, long distance)'],
  },
  uz: {
    hotel: [`6 tadan 12 tagacha sifatli surat, gorizontal, kamida 1600 piksel kenglikda: bino va kirish, oddiy xona va hammom, nonushta joyi, hovli yoki terrasa`,
      `Hozirgi yulduz toifasi, xona turlari va odatdagi eng past kechalik narx, saytimizda toʻgʻri maʼlumot koʻrsatilishi uchun`],
    guide: [`Oʻzingiz gidlik qilayotgan 2–3 ta soʻnggi surat (portret va yodgorlik oldidagi guruh), kamida 1600 piksel kenglikda`,
      `Qaysi tillarda gidlik qilishingiz va eng yaxshi bilgan joylaringiz, 2–3 qatorda`],
    transport: [`Avtomobillaringizning 6 tadan 10 tagacha sifatli surati, tashqaridan va ichkaridan, gorizontal, kamida 1600 piksel kenglikda`,
      `Avtomobil modellari, oʻrindiqlar soni va xizmatlaringiz (aeroport transferi, kunlik ijara, uzoq masofa)`],
  },
  ru: {
    hotel: ['6–12 качественных фотографий в горизонтальной ориентации, шириной не менее 1600 пикселей: здание и вход, типовой номер и ванная, зал для завтрака, двор или терраса',
      'Вашу текущую звёздность, категории номеров и обычную минимальную цену за ночь, чтобы на нашем сайте была верная информация'],
    guide: ['2–3 свежие фотографии с экскурсий (портрет и группа у памятника), шириной не менее 1600 пикселей',
      'Языки, на которых вы работаете, и места, которые знаете лучше всего, в двух-трёх строках'],
    transport: ['6–10 качественных фотографий ваших автомобилей снаружи и внутри, в горизонтальной ориентации, шириной не менее 1600 пикселей',
      'Модели автомобилей, число мест и ваши услуги (трансферы из аэропорта, аренда на день, дальние поездки)'],
  },
}

const PHOTOS = {
  en: (d, k, c) => `${when(d.date, 'en')}

To: ${blank(d.partner)}${d.contact ? `\nAttention: ${d.contact}` : ''}
${blank(d.city, 'Samarkand')}

**Subject: Photographs of ${blank(d.partner)} for the ${d.company} website**

${c.greeting(d)}

Thank you for working with ${d.company}. We present our partners on our website, in our itineraries and in our Telegram bot, and we would like ${blank(d.partner)} to appear with its own photographs rather than with general pictures of the destination.

**What we kindly ask you to send**
${list([...PHOTO_ASKS.en[d.type || 'hotel'], 'Your permission, confirmed in your reply, to publish the photographs on our website and social networks with your name credited', 'Confirmation that you own the photographs or have the right to share them'])}

**How to send them**
${list(['Reply to this email with the photographs attached, or send them by WhatsApp or Telegram' + (d.ourPhone ? ` to ${d.ourPhone}` : ''), 'Large files can be sent through Google Drive, Telegram or WeTransfer'])}

**What we promise**
${list([`We use the photographs only to present ${blank(d.partner)} to our guests, with your name beside them, and we do not sell or pass them to anyone else`, 'We will remove or replace any photograph within 5 working days of your request', 'Your photographs stay your property'])}

Please reply by ${when(d.deadline, 'en')}. Thank you for your time and for the cooperation.

${c.close}
${signature(d, 'en')}`,
  uz: (d, k, c) => `${when(d.date, 'uz')}

Kimga: ${blank(d.partner)}${d.contact ? `\nDiqqatga: ${d.contact}` : ''}
${blank(d.city, 'Samarqand')}

**Mavzu: ${blank(d.partner)} suratlari ${d.company} veb-sayti uchun**

${c.greeting(d)}

${d.company} bilan hamkorlik qilayotganingiz uchun rahmat. Biz hamkorlarimizni veb-saytimizda, marshrutlarimizda va Telegram-botimizda taqdim etamiz va ${blank(d.partner)} yoʻnalishning umumiy suratlari bilan emas, oʻz suratlari bilan koʻrinishini istaymiz.

**Yuborishingizni soʻraymiz**
${list([...PHOTO_ASKS.uz[d.type || 'hotel'], `Suratlarni veb-saytimizda va ijtimoiy tarmoqlarimizda ismingiz koʻrsatilgan holda eʼlon qilishga javob xatingizda tasdiqlangan ruxsatingiz`, `Suratlar sizniki ekani yoki ularni ulashish huquqingiz borligi tasdigʻi`])}

**Qanday yuborish kerak**
${list([`Suratlarni ilova qilib shu xatga javob yozing yoki WhatsApp yoki Telegram orqali yuboring` + (d.ourPhone ? ` (${d.ourPhone})` : ''), `Katta fayllarni Google Drive, Telegram yoki WeTransfer orqali yuborish mumkin`])}

**Biz nimani va'da qilamiz**
${list([`Suratlardan faqat ${blank(d.partner)} ni mehmonlarimizga taqdim etish uchun, ismingiz bilan birga foydalanamiz; ularni sotmaymiz va boshqalarga bermaymiz`, `Istalgan suratni soʻrovingizdan keyin 5 ish kuni ichida olib tashlaymiz yoki almashtiramiz`, `Suratlar sizning mulkingiz boʻlib qoladi`])}

Iltimos, ${when(d.deadline, 'uz')} gacha javob bering. Vaqtingiz va hamkorligingiz uchun rahmat.

${c.close}
${signature(d, 'uz')}`,
  ru: (d, k, c) => `${when(d.date, 'ru')}

Кому: ${blank(d.partner)}${d.contact ? `\nВниманию: ${d.contact}` : ''}
${blank(d.city, 'Самарканд')}

**Тема: Фотографии ${blank(d.partner)} для сайта ${d.company}**

${c.greeting(d)}

Спасибо за сотрудничество с ${d.company}. Мы представляем партнёров на нашем сайте, в маршрутах и в Telegram-боте и хотели бы, чтобы ${blank(d.partner)} был показан с собственными фотографиями, а не с общими снимками направления.

**О чём мы просим**
${list([...PHOTO_ASKS.ru[d.type || 'hotel'], 'Ваше разрешение, подтверждённое в ответе, публиковать фотографии на нашем сайте и в социальных сетях с указанием вашего названия', 'Подтверждение, что фотографии принадлежат вам или вы вправе ими делиться'])}

**Как прислать**
${list(['Ответьте на это письмо с вложенными фотографиями или отправьте их в WhatsApp или Telegram' + (d.ourPhone ? ` (${d.ourPhone})` : ''), 'Большие файлы можно отправить через Google Drive, Telegram или WeTransfer'])}

**Что мы обещаем**
${list([`Мы используем фотографии только для представления ${blank(d.partner)} нашим гостям, рядом с вашим названием, и не продаём и не передаём их третьим лицам`, 'Любую фотографию мы удалим или заменим в течение 5 рабочих дней после вашего запроса', 'Фотографии остаются вашей собственностью'])}

Просим ответить до ${when(d.deadline, 'ru')}. Благодарим за время и сотрудничество.

${c.close}
${signature(d, 'ru')}`,
}
TEXT.en.photos = PHOTOS.en
TEXT.uz.photos = PHOTOS.uz
TEXT.ru.photos = PHOTOS.ru

/** Build one document. `data` comes from the form (see PartnerDocs.jsx). */
export function buildDocument({ doc, type, lang, data }) {
  const d = { company: 'ALI TRAVEL', paymentDays: 7, termMonths: 12, cancelHours: 48, ...data }
  return TEXT[lang][doc]({ ...d, type }, KINDS[lang][type], COMMON[lang]).trim()
}

/** Subject line of a document (for the mailto: link); documents start with "**Subject: …**" or "**Mavzu / Тема: …**". */
export function subjectOf(text) {
  const m = text.match(/\*\*(?:Subject|Mavzu|Тема):\s*(.+?)\*\*/)
  return m ? m[1] : ''
}
