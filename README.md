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

## Hands-on classes, reviews and booking confidence

- **Samarkand classes** (Tours with category *Food*, type *Hands-on class*): Non Bread Baking Class, Plov Masterclass and Plov & Non
  Masterclass, each with a step-by-step plan; guests take their bread and plov home. Created by `manage.py seed --extras`. Prices
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
- Telegram: create a bot with @BotFather, put `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env` (see `.env.example`).

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
