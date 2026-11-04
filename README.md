# ali-trevel

A re-creation of the ALI TRAVEL site (Uzbekistan travel agency): **Django REST** backend + **React (Vite + Tailwind)** frontend.

Catalogue content (tours, hotels, destinations, food, transport) is **sample data** written for this project
(`backend/api/management/commands/seed.py`); photos are hot-linked from the original site's media host.

## Run the backend

```powershell
.\venv\Scripts\python.exe -m pip install django djangorestframework django-cors-headers
cd backend
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py seed
..\venv\Scripts\python.exe manage.py createsuperuser   # staff users get the /admin dashboard
..\venv\Scripts\python.exe manage.py runserver
```

API at http://127.0.0.1:8000/api/ · Django admin at http://127.0.0.1:8000/admin/

## Run the frontend (needs Node.js)

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (Vite proxies `/api` to the Django server).

## What is included

Home, Destinations (+detail), Tours (+detail with booking request), Hotels (+detail), Local Food, Transport
(price estimator), Plan My Trip, About, Contact, Legal pages, email/password sign-in and registration,
My account (booking requests, cancel, saved items), Partner registration/dashboard, and an Admin dashboard
(bookings, messages, partners, tours, site settings).

## Admin panel

Sign in at `/login` with a staff account; staff users are sent to `/admin`. Create one with
`manage.py createsuperuser` (or set `is_staff=True` on an existing user).

Sections: Overview, Tours & packages (filters, feature/publish/duplicate/archive/delete), Other listings
(destinations, hotels, experiences, transport), Bookings, Customers, Partners, Enquiries,
Homepage content and Contact & settings.

## Languages (EN, UZ, RU, FR, DE, ES)

- **Interface copy** is keyed by its English text. Built-in translations live in `frontend/src/strings.js`;
  admins override any text per language under *Admin → Homepage content* (stored in the `SiteText` table,
  served at `/api/texts/`). Every fixed string on the public site is listed there.
- **Listings** (tours, destinations, hotels, experiences, transport) carry an `i18n` JSON field. Each editor in
  the admin has EN/UZ/RU/FR/DE/ES tabs; empty fields fall back to English. The site sends the chosen language in
  the `X-Lang` header and the API returns the translated values.
- Contact details (phones, email, address, social links) are edited under *Contact & settings*.

## Site editor (Admin → Site editor)

The public website shown exactly as visitors see it, inside the admin console, with editing switched on
(it is the real site loaded at `/?edit=1` in a frame; editing tools exist only there and only for a signed-in admin).

- **Edit mode:** click any text to change it (interface text is saved per language; tour/hotel/destination text is saved
  into that record's translation for the current language), click a photo to replace it, click a card's **Edit** pill
  for the full form.
- **Blank template cards:** in the empty slot next to the last card of a grid, a dashed "+" card opens an empty form
  (e.g. "Add a historical place" on a destination page comes pre-attached to that destination and its city tour).
  Fill it in, upload a photo, publish.
- **Browse mode** lets you click through the site like a visitor. Language, page and device size are in the toolbar.
- **Photos:** uploaded through `POST /api/upload/` (admin only; JPG/PNG/GIF/WebP, max 8 MB, checked by file signature)
  and stored in `backend/media/`. In development Django serves `/media/`; in production serve that folder from your web server.

`manage.py seed --extras` adds the Samarkand city tour and its seven historical places and fills missing translations
without touching anything already edited.

## Day-by-day plans and place notes

A tour can carry a day-by-day plan (`Tour.itinerary`): each day is a list of timed items — visit, meal, transfer, free time
or custom text. Items point at the tour's route by index, so place names are translated together with the route.
Edit it under *Admin → Tours → Day-by-day plan* (add days, pick places from the route, mark meals as included or not).
The plan is shown on the tour page and, after a booking request, again with real dates and a print button; the plain-text
plan is saved with the booking. Each place (a child tour) has an "about" text (`description`) and a keepsake `story`, both
translated.

## Accounting (Admin → Accounting)

Money rules (USD): total due = agreed price (or the estimate) − discount; balance = total due − payments; profit = total due −
costs. Revenue and profit count tours marked **completed**, by the day the tour took place.

- **Summary:** revenue, received, outstanding, expenses, net profit and margin for This month / Last month / This year / All
  time, a 12-month chart, expenses by category and the tours still waiting for payment.
- **Tour ledger:** every completed tour with price, discount, payments, costs and profit. Open a row to set the agreed price and
  discount, record payments (or "mark as paid in full"), record expenses, fill expenses from the tour's cost template
  (*Tours → Costs for accounting*: per person / per group / per day) and print an invoice.
- **General expenses:** costs not tied to a tour (rent, advertising, salaries).
- **Exports:** CSV of tours and of expenses.

Run `manage.py test api` for the accounting tests.

## Discounts and promotions (Admin → Promotions)

- **Announce a sale:** create a promotion (e.g. 20% off all tours). A banner appears at the top of the site and every matching
  price shows the old price crossed out with the new price beside it. Set start/end dates or pause it at any time.
- **Single item:** tours, hotels and transport have a *Discount (%)* field in their editor. If both apply, the larger wins.
- Banner text is translated per language inside the promotion.

## Hotels

Visitors can pick an optional hotel when requesting a tour (nights and rooms are totalled), or send a stay request from a hotel page.

## Legal pages (Admin → Legal pages)

Privacy Policy, Terms and Conditions and Cancellation Policy are served at `/legal/privacy`, `/legal/terms`, `/legal/cancellation`
(EN/UZ/RU written; other languages fall back to English until you translate them). Markup: `##` heading, `###` sub-heading,
`- ` bullet, `1. ` step, `**bold**`, `[text](url)`. Run `manage.py seed --extras` to create them.
Replace the `[bracketed]` company details and have a lawyer review the texts.

## Partner letters (Admin → Partner letters)

Drafts of a cooperation proposal, official email, price-request letter and cooperation agreement for hotels, guides and drivers
(EN/UZ/RU). Fill the form, edit the text, copy, print, download as .doc or open in email.

## Regions of Uzbekistan

Seven regions are shown on the home page: Samarkand, Bukhara, Khorezm (Khiva), Kashkadarya (Shahrisabz), Tashkent, Fergana Valley and
Karakalpakstan. Each has a regional tour with a day-by-day plan (like the Samarkand City Tour) and one tour card per historical place
(24 places) with an "about" note, a keepsake text and the entrance fee. Run `manage.py seed --extras` to create them; records an admin
has edited are never overwritten. Photos are linked from Wikimedia Commons and the facts come from Wikipedia. Prices of the regional
tours are sample prices — change them in Tours & packages. Place texts are written in English, Uzbek and Russian; French, German and
Spanish show the English text until translated in the admin panel. The three sample hotels of the new regions are placeholders.

## Hands-on food experiences, reviews and booking confidence

- **Samarkand food experiences** (Tours with category *Food*, type *Hands-on experience*): *Bake & Taste Samarkand Non*, *Cook & Taste
  Samarkand Plov* and *Samarkand Non & Plov Experience*, each with a step-by-step plan; guests shape the food, taste it at the dastarkhan
  and take the rest home. Created by `manage.py seed --extras`. Prices
  ($35 / $65 / $89) are sample prices; photos come from Wikimedia Commons. They also appear in the "Hands-on experiences" section of the
  home page.
- **Reviews:** every priced tour page has a review form. Nothing is shown until an admin publishes it in **Admin → Reviews**.
  A "Verified traveller" mark is added when the booking reference and email match a confirmed or completed booking. Published reviews
  update the tour's star rating, and the home page shows real reviews instead of the demonstration ones as soon as any exist.
- **Booking confidence:** tour pages show free cancellation (per the Cancellation Policy), "reserve now, pay later", group size and
  pickup, plus a "Good to know" FAQ. Tour cards show small badges. A WhatsApp button (from *Contact & settings*) is on every page.

## Group pricing and selecting several tours

- **Prices start at 20 travelers.** The price on a tour is the price per person for a group of 20 or more. Smaller groups pay a higher
  percentage (default: 15–19 → 105%, 10–14 → 115%, 6–9 → 130%, 4–5 → 150%, 2–3 → 180%, 1 → 220%). Edit the table in
  **Admin → Group pricing**; switch it off for a single tour with *Price depends on group size* in the tour editor (the Samarkand
  classes are off, as they are a fixed price per person).
- **At the end of the booking form** (and again after the request is sent) visitors see their price per person and total, the price
  for every group size, and a short explanation of why smaller groups pay more. The group price is also written into the request
  for the admin.
- **Select tours:** every tour card has a *Select* button. The selection is remembered in the browser; a bar at the bottom opens one
  combined booking request for all selected tours. The home page now lists all tours, not only three.

## Limiting a promotion to some tours

In **Admin → Promotions** a campaign can be limited to chosen destinations (for example only Samarkand), to chosen tours (for example
only the plov class), or both. With nothing ticked it covers every price of the chosen kind. Hotels follow their destination;
transport options have no destination, so a limited campaign does not discount them.

## Notifications (e-mail and Telegram)

- The team is told about every **new booking request, contact message and review** (e-mail to `NOTIFY_EMAILS`, and Telegram when a bot is set up).
- The **traveller** gets an e-mail when the request arrives, and again when the team confirms, cancels or completes it (the last one
  asks for a review). Mails follow the language the traveller was reading (English, Uzbek, Russian; other languages receive English).
  Internal admin notes are never e-mailed.
- Without `EMAIL_HOST` in `backend/.env`, e-mails are printed in the server console instead of being sent. Sending never delays or
  breaks a booking: it runs in the background and failures are only logged.
- Telegram: create a bot with @BotFather and put `TELEGRAM_BOT_TOKEN` in `backend/.env`. Open the bot in Telegram, press Start, then run
  `python manage.py telegram_setup`: it names the bot, finds your chat, saves `TELEGRAM_CHAT_ID` and sends a test message.

## Going live (a Linux server)

1. Copy the project to the server, create a virtualenv and `pip install -r backend/requirements.txt`.
2. Copy `backend/.env.example` to `backend/.env` and fill it in: `DEBUG=false`, a private `SECRET_KEY`, `ALLOWED_HOSTS`, `SITE_URL`,
   e-mail settings. The server refuses to start with `DEBUG=false` and the development secret key.
3. `python manage.py migrate`, then `python manage.py seed --extras` to load the sample catalogue, and `python manage.py changepassword alitravel004@gmail.com` (the sample admin account).
   **Change the sample admin password** before going live; create more admins with `createsuperuser`.
4. `cd frontend && npm install && npm run build`; point nginx at `frontend/dist` (see `deploy/nginx.conf`, which also proxies `/api`,
   `/sitemap.xml` and `/robots.txt` to Django and serves `/media`). Get a free HTTPS certificate with certbot.
5. Run the API with gunicorn under systemd (`deploy/alitravel.service`).
6. Nightly backup: `python manage.py backup` (SQLite copy or JSON export, plus uploaded photos, into `backend/backups/`, newest 14 kept).
   Add it to cron, e.g. `0 3 * * * cd /var/www/alitravel/backend && ../venv/bin/python manage.py backup`.

## Search engines, sharing and analytics

- Each page sets its own title, description, share image and canonical link; priced tours also publish structured data (price) for
  search results. `/sitemap.xml` lists every published page; `/robots.txt` keeps the admin out. The site is a single-page app, so
  search engines that do not run JavaScript only see the basic page; pre-rendering can be added later.
- **Photo credits** page (`/credits`, linked in the footer) links every Wikimedia Commons photo to its file page, which names the
  photographer and licence. Replacing photos with your own (Site editor → click a photo) removes the need for credits.
- **Google Analytics** is optional: enter a measurement ID (`G-…`) in *Contact & settings*. A cookie banner appears and nothing is
  loaded until the visitor accepts.
- **Spam protection:** forms contain a hidden field that robots fill in (such messages are silently dropped), and bookings, messages
  and reviews are rate-limited per visitor.

## Telegram bot for travellers

The bot (`@alitraveluzbot`) does two jobs: it alerts the team (see Notifications) and it answers travellers.

- **/start** asks for a language (English, Uzbek, Russian, French, German, Spanish). The choice is remembered; `/start` or the
  Language button changes it.
- The **menu** shows destinations, tours, cooking classes, prices and group sizes, the cancellation and payment rules, and contact
  details. Everything comes live from the website's own data (tour texts in the traveller's language, discounts, group-price
  table, contact details from *Contact & settings*), so editing the site updates the bot.
- **Send a request** (or *Request this tour*) lets the traveller write a message and share their phone number. It arrives as an
  *Enquiry* in the admin panel and as an alert in the team's Telegram.
- Run it with `python manage.py telegram_bot` (it polls Telegram, so no public address is needed). On a server use
  `deploy/alitravel-bot.service`. Run `python manage.py telegram_setup` once to name the bot and register its commands.
- Links to the website are only shown as buttons when `SITE_URL` is a public `https://` address; before that they appear as text.
- The bot's texts are in `backend/api/telegram_texts.py`.

### Who receives the Telegram alerts

- Alerts go **only to the team account(s)** named in `TELEGRAM_TEAM_USERNAMES` (default `Al1_travel`), never to travellers who talk
  to the bot. For Telegram to allow it, the team account must open the bot once and press **Start** (with `manage.py telegram_bot`
  running). The bot then confirms that the account is registered.
- The team is told about every **booking from the website and from the bot** (the alert says which one), and every message and review.
- Travellers can **book in the bot**: *Book this tour* asks for the date, the number of travellers (the group price is calculated)
  and a phone number, then creates a normal booking request (visible in Admin → Bookings). When the team confirms, cancels or
  completes it, the traveller is told in the same Telegram chat. *My bookings* lists their requests.
- `python manage.py telegram_setup` describes the bot and shows whether the team account is connected.

### Rating a finished trip in Telegram

When the team marks a bot booking **completed**, the traveller gets a thank-you message in the chat with five star buttons. A tap on the
stars asks for a short comment (or *Skip*); the comment is saved as a **verified review awaiting approval** (Admin → Reviews) and the team
is alerted. The bot then thanks the traveller, suggests following ALI TRAVEL on Instagram, YouTube, Telegram and Facebook, and says it looks
forward to welcoming them again. A trip can be reviewed once, and only from the chat that booked it.

## Sign-in protection and rate limits

- After 8 wrong passwords for the same e-mail from the same address, sign-in is refused for 15 minutes (even with the right password).
  A successful sign-in resets the count. Registration is limited to 20 per hour per address.
- Bookings (40/hour), messages (20/hour) and reviews (8/hour) are limited per visitor. Behind nginx set `NUM_PROXIES=1` in
  `backend/.env` (already the default when `DEBUG=false`), otherwise every visitor would look like `127.0.0.1` and share one limit.
  The counters live in each server process, so with 3 gunicorn workers the effective limit is about three times higher; use a shared
  cache (Redis) if you need exact limits.

## Putting alitravel.uz online (step by step)

The whole site can run as **one process**: in production Django also gives out the built website and the uploaded photos, so you need
a server with Python and Node.js, the domain, and nothing else. (nginx in front is optional and faster; see `deploy/nginx.conf`.)

**What you need:** a small Linux server (VPS) with a public IP address, and control of the DNS records of `alitravel.uz`.

1. **DNS:** at your domain registrar create an `A` record for `alitravel.uz` and one for `www.alitravel.uz`, both pointing to the server's IP.
   It can take minutes to hours to spread.
2. **Server:** install Python 3.12+, Node.js 20+, git and nginx (`sudo apt install python3-venv nodejs npm git nginx certbot python3-certbot-nginx`).
   Copy the project to `/var/www/alitravel` (git clone or upload).
3. **Backend:**
   ```
   cd /var/www/alitravel && python3 -m venv venv && venv/bin/pip install -r backend/requirements.txt
   cp backend/.env.example backend/.env      # then edit it (see below)
   cd backend && ../venv/bin/python manage.py migrate
   ../venv/bin/python manage.py seed --extras   # only for a brand-new database; skip if you copy your own db.sqlite3 and media/ folder
   ../venv/bin/python manage.py changepassword alitravel004@gmail.com   # a new, private admin password
   ```
4. **`backend/.env`** needs at least: `DEBUG=false`, `SECRET_KEY=<long random string>`, `ALLOWED_HOSTS=alitravel.uz,www.alitravel.uz`,
   `SITE_URL=https://alitravel.uz`, `CSRF_TRUSTED_ORIGINS=https://alitravel.uz,https://www.alitravel.uz`, `NUM_PROXIES=1`,
   the e-mail settings (`EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`), `TELEGRAM_BOT_TOKEN` and `TELEGRAM_TEAM_USERNAMES=Al1_travel`.
5. **Website:** `cd frontend && npm install && npm run build`. Django then serves `frontend/dist` itself (`SERVE_FRONTEND` is on by default
   when `DEBUG=false`). Set `SERVE_FRONTEND=false` only if nginx serves those files.
6. **Keep it running:** `deploy/alitravel.service` (the API and the website) and `deploy/alitravel-bot.service` (the Telegram bot) with systemd.
7. **nginx + HTTPS:** use `deploy/nginx.conf`, then `sudo certbot --nginx -d alitravel.uz -d www.alitravel.uz` for a free certificate.
   If your host terminates HTTPS itself and does not send `X-Forwarded-Proto`, set `SECURE_SSL_REDIRECT=false` to avoid a redirect loop.
8. **Check everything:**
   ```
   cd /var/www/alitravel/backend
   ../venv/bin/python manage.py site_check          # settings, files, content, e-mail, Telegram
   ../venv/bin/python manage.py site_check --live   # then opens https://alitravel.uz and checks pages, API, sitemap, HTTPS redirect
   ```
   Every line should be `[OK]`; `[WARN]` means it works but needs attention (sample hotels, e-mail not set up, legal placeholders);
   `[FAIL]` means the site would be broken or unsafe.
9. **After going live:** place one test booking and one review yourself (the team gets a Telegram alert), check the Telegram bot's
   "Open on the website" buttons appear (they need the public `https://` `SITE_URL`), submit `https://alitravel.uz/sitemap.xml` in Google
   Search Console, and schedule `manage.py backup` every night.

## Hotels, guesthouses and hostels (photo slider)

- **28 real places to stay** across all seven regions: 4–5 star hotels, 3-star hotels, boutique hotels, guesthouses and hostels
  (`manage.py seed --extras`; the earlier made-up sample hotels are archived). Names, classes and prices come from public booking
  listings (Booking.com, Tripadvisor, Trip.com, Expedia, Hostelz and similar, 2025–2026). Booking-site prices change with the season and the
  sites disagree, so every price is an **indicative "from" rate** (per room, or per dorm bed for hostels) and the site says so; the team
  confirms the exact rate for the requested dates. Where the sources gave a range it is written in the description. Re-check the prices
  and the star ratings before relying on them (`backend/api/management/commands/seed_hotels.py`).
- **Photo slider:** every hotel card and page slides through several photos: swipe on a phone, drag with the mouse, use the arrows, dots or
  thumbnails, or the arrow keys.
- **Several photos from the admin panel:** Admin → Other listings → Hotels → *Edit*: the *Photo* is the cover and *More photos* takes many
  uploads at once (reorder with the arrows, remove with the bin). Hotels also have a *Type*, *Stars* (0 for guesthouses and hostels) and *Price is*
  (per room or per bed).
- **Photos:** almost no free photos of these businesses exist, so until you upload the hotels' own pictures each gallery shows the destination and
  the page says so (tick off *Photos show the destination, not this property* after uploading real ones). Hyatt Regency Tashkent has a real photo.
- The hotel list can be filtered by class/type and by destination.

### Real photos of the hotels

- Free (Wikimedia Commons) photos of the property itself exist for only a few places: **Orient Star Khiva**, **LOTTE City Hotel Tashkent Palace** and
  **Hyatt Regency Tashkent**. Every other hotel shows real photographs of *similar places to stay* in the same city (hotel rooms, courtyards, entrances,
  hostel signs; lists in `seed_hotels.py` POOLS and `hotel_photos.py`), and the page says so. Monuments are never used as hotel photos.
  Photos on Booking.com, Tripadvisor or a hotel's own website belong to their owners and must not be copied.
- For every other hotel ask for the photographs: **Admin → Partner letters → Photo permission request** drafts a letter (English, Uzbek, Russian) asking a
  hotel, guide or driver for 6–12 photographs and for permission to publish them with their name credited. Upload what they send in
  **Other listings → Hotels → Edit → More photos**, then untick *Photos show similar places, not this property itself*.

### Silk Road map on the home page

Right after "Traveller stories" the home page shows a map of Uzbekistan with the Great Silk Road drawn on it (Tashkent – Samarkand – Bukhara – Khiva,
branches to the Fergana Valley and to Shahrisabz/Termez). Cities link to their destination pages. Code: `frontend/src/components/SilkRoadMap.jsx`; the
outline and city positions are in `frontend/src/silkRoadGeo.js` (Natural Earth, public domain); texts in `strings.silkroad.js`.

### The 7-day Silk Road package

The first card of the home page's Destinations section is a 7-day package (`/tours/silk-road-7-day-journey`): 2 days Samarkand, a day in
Shahrisabz and Qarshi, a day on the road to Bukhara, 2 days Bukhara and the road back via Gijduvan and Rabat-i-Malik. Data: `seed_package.py`
(created by `manage.py seed --extras`). It is an ordinary tour, so **Site editor** and **Admin → Tours** change it (texts, photo, price, day plan)
and the public site shows the change at once. The places on its plan (photo, note, keepsake text) are single-place tours: edit them the same way.
The price ($790) is a sample to confirm.

The home page's first row shows three packages in this order: the 2-day Samarkand City Tour, the 7-day journey and the 11-day journey
(Samarkand, Shahrisabz, Qarshi, Bukhara, Khiva; `seed_package_11.py`, `/tours/silk-road-11-day-journey`). They also come first on the Tours page.
Every tour with a day plan of two or more days includes the most affordable hotels and a standard taxi: its booking form (and the Telegram bot) says that
3-, 4- and 5-star hotels and a premium-class taxi cost extra, and the choice is saved in the booking request. The prices ($790 and $1,290) are samples.

Telegram bot: the welcome text ("Welcome to ALI TRAVEL … What would you like to see?") is shown only right after `/start` and the language choice; later menus carry a short
"Menu" title. Every new-booking alert sent to the team has **Confirm / Decline** buttons: a team account (TELEGRAM_TEAM_USERNAMES) taps one, the booking becomes
confirmed or cancelled and the traveller is told by e-mail and in Telegram, exactly as when the status is changed in the admin panel.

Between the Destinations and Tours sections of the home page an advert shows the three places with the cheapest entrance tickets (`BestValue.jsx`, picked
automatically from the places' entrance fees). A single place cannot be booked on its own, so each card says which tour it belongs to and leads to that full tour.

After a tour request the traveller is asked when they reach Samarkand airport (date, time, flight or train number): a form on the "Request received" screen on the website
(`POST /api/bookings-arrival/`, identified by booking reference + e-mail) and one more question in the Telegram bot (free text, can be skipped). The details are saved on
the booking, shown in Admin → Bookings and sent to the team by e-mail and Telegram.

### Accounting, customers, enquiries, extra contacts, exact places

- **Automatic costs.** When a booking is confirmed or completed its costs are added by themselves (`api/accounting.py`, `signals.py`): guide per day, cars (one per 4 travellers) per day,
  the most affordable hotel (2 travellers per room, nights = days - 1) and the entrance tickets when the price includes them; a tour's own cost template, if it has one, is used instead.
  Rates: **Admin -> Accounting -> Cost rates** (sample values, change them). Profit = price - costs. A cost added or edited by hand is never overwritten.
  The Summary also shows the expected profit of confirmed tours.
- **Customers** lists website accounts, guests who booked without an account and Telegram bot users, with their bookings (and arrival details).
- **Enquiries**: New / Read / Replied buttons (they did not work before: the status was read-only in the API); Telegram messages are marked.
- **Settings -> More contact lines**: any number of extra lines (name, text, optional link) shown in the footer and on the contact page.
- **Exact places**: every single place of a tour has a latitude, longitude and optional note (`seed_locations.py`, editable in the tour editor): a map with links to
  Google Maps and directions on its page, a pin next to each stop of a tour and a link that opens the whole route. Coordinates come from Wikipedia and OpenStreetMap;
  a few places only have the town centre and say "approximate location".

Telegram bot, less clutter: buttons that only navigate (menu, destinations, tours, a tour, prices, policy, contact, my bookings, language) **edit the message they are under** instead of
sending a new one; a tour or destination shows its picture as a link preview inside the same message. A task (question, booking, arrival, review) ends with the menu buttons under its last
message — no separate "Menu" message. When booking, the date can be written in any form ("15 May", "15.05.2027", "tomorrow", "1 мая"…), left for later with a button, or written as free
text (kept for the team to confirm).

Telegram bot: a tour now has the same information as its page on the website, in six buttons under the tour (they edit the same message): **details** (type, duration, group, languages,
transport/tickets/pickup, guide, meeting point, included / not included, story), **day-by-day plan** (in pages), **places and map** (every stop with its ticket and a Google Maps link,
and the whole route as one button), **price by group size** (the bigger the group, the cheaper per person) and booking. A single place shows its note, ticket and exact location and leads to its
full tour. Alerts for the team in Telegram use the Uzbek tour names; the 7- and 11-day packages are priced by group size like the other tours.

**Silk Road map (home page)**: in **Admin -> Contact & settings -> Silk Road map** tick a city to mark it with a green pulsing dot; a click on it opens the tours of that city, or the tour chosen
next to it. Cities not on the map yet (Qarshi, Navoi, Jizzakh, Kokand, Namangan, Andijan, Urgench) appear once ticked (`frontend/src/mapCities.js`, `SiteContent.map_cities`).

Silk Road map, more: in the same Settings section **Cities you added** lets the owner put any other place of Uzbekistan on the map (name, latitude, longitude, where the name sits,
green or not and where a click leads). The city is drawn at its real position (`project()` in `frontend/src/mapCities.js`).
