"""Is the website ready to go live? `python manage.py site_check` (and `--live` once it is online).

Prints a green OK, a yellow WARN (works, but should be fixed) or a red FAIL (the site would be broken or unsafe) for each point.
`--live` also opens the real website at SITE_URL and checks that pages, the API, the sitemap and the HTTPS redirect answer.
"""
import urllib.error
import urllib.request
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from api import models, notifications


class Command(BaseCommand):
    help = "Check that the site is ready to go live (add --live to test the real website at SITE_URL)."

    def add_arguments(self, parser):
        parser.add_argument("--live", action="store_true", help="Also request the live website at SITE_URL.")

    # ---- small helpers ---------------------------------------------------------
    def report(self, level, text):
        self.results.append(level)
        style = {"OK": self.style.SUCCESS, "WARN": self.style.WARNING, "FAIL": self.style.ERROR}[level]
        self.stdout.write(f"{style(f'[{level}]'.ljust(7))} {text}")

    def handle(self, *args, **options):
        self.results = []
        host = urlparse(settings.SITE_URL).hostname or ""
        public = host not in ("", "localhost", "127.0.0.1")

        self.stdout.write(self.style.MIGRATE_HEADING("Settings"))
        self.report("OK" if not settings.DEBUG else "FAIL", "DEBUG is off" if not settings.DEBUG else "DEBUG is ON: set DEBUG=false in backend/.env")
        self.report("OK" if settings.SITE_URL.startswith("https://") else ("FAIL" if public else "WARN"),
                    f"SITE_URL = {settings.SITE_URL}" + ("" if settings.SITE_URL.startswith("https://") else "  (must be your public https:// address, e.g. https://alitravel.uz)"))
        hosts = [h for h in settings.ALLOWED_HOSTS if h not in ("localhost", "127.0.0.1")]
        self.report("OK" if hosts and (not public or host in settings.ALLOWED_HOSTS or "*" in settings.ALLOWED_HOSTS) else "FAIL",
                    f"ALLOWED_HOSTS = {', '.join(settings.ALLOWED_HOSTS) or '(empty)'}" + ("" if hosts else "  (add your domain names)"))
        self.report("OK" if settings.SECURE_SSL_REDIRECT or settings.DEBUG else "WARN",
                    "HTTP is redirected to HTTPS" if getattr(settings, "SECURE_SSL_REDIRECT", False) else "HTTP is not redirected to HTTPS (SECURE_SSL_REDIRECT=false)")

        self.stdout.write(self.style.MIGRATE_HEADING("Website files"))
        if settings.SERVE_FRONTEND:
            built = (settings.FRONTEND_DIST / "index.html").exists()
            self.report("OK" if built else "FAIL", f"Website built in {settings.FRONTEND_DIST}" if built else "Website not built: run `npm run build` in the frontend folder")
        else:
            self.report("WARN", "Django does not serve the website (SERVE_FRONTEND=false): nginx must serve frontend/dist")
        for label, folder in (("Photo uploads", settings.MEDIA_ROOT), ("Backups", settings.BASE_DIR / "backups")):
            try:
                folder.mkdir(parents=True, exist_ok=True)
                probe = folder / ".write-test"
                probe.write_text("ok")
                probe.unlink()
                self.report("OK", f"{label} folder is writable ({folder})")
            except OSError as error:
                self.report("FAIL", f"{label} folder is not writable: {error}")

        self.stdout.write(self.style.MIGRATE_HEADING("Content"))
        counts = {name: model.objects.filter(status="published").count() for name, model in (("destinations", models.Destination), ("tours", models.Tour), ("hotels", models.Hotel))}
        for name, count in counts.items():
            self.report("OK" if count else "FAIL", f"{count} published {name}")
        self.report("OK" if get_user_model().objects.filter(is_staff=True, is_active=True).exists() else "FAIL", "An admin account exists" if get_user_model().objects.filter(is_staff=True).exists() else "No admin account: run `manage.py createsuperuser`")
        sample = models.Hotel.objects.filter(status="published", summary__startswith="Sample listing").count() + models.Hotel.objects.filter(status="published", destination_slug__in=["samarkand", "bukhara", "khorezm", "tashkent"], summary__icontains="sample").count()
        self.report("WARN" if sample else "OK", f"{sample} sample hotel(s) are published: replace them with real partner hotels in Admin" if sample else "No sample hotels published")
        placeholders = [page.slug for page in models.LegalPage.objects.all() if "[" in page.body]
        self.report("WARN" if placeholders else "OK", f"Legal pages still contain [bracketed] placeholders ({', '.join(placeholders)}): fill in the company details and have a lawyer read them" if placeholders else "Legal pages have no placeholders left")
        content = models.SiteContent.objects.filter(pk=1).first()
        self.report("OK" if content and content.phone_primary and content.email else "WARN", "Contact phone and e-mail are set" if content and content.phone_primary and content.email else "Contact phone/e-mail missing in Admin → Contact & settings")
        if not models.Review.objects.filter(status="published").exists():
            self.report("WARN", "No published reviews yet: the home page shows the three demonstration testimonials until the first real review is published")

        self.stdout.write(self.style.MIGRATE_HEADING("Notifications"))
        console_mail = "console" in settings.MAILERS.get("default", {}).get("BACKEND", "")
        self.report("WARN" if console_mail else "OK", "E-mail is printed in the console, not sent: set EMAIL_HOST in backend/.env" if console_mail else "E-mail is sent through SMTP")
        if settings.TELEGRAM_BOT_TOKEN:
            chats = notifications.team_chat_ids()
            self.report("OK" if chats else "WARN", f"Telegram alerts go to {len(chats)} team chat(s)" if chats else f"Telegram team account(s) {', '.join(settings.TELEGRAM_TEAM_USERNAMES)} have not pressed Start in the bot yet")
        else:
            self.report("WARN", "Telegram bot is not configured (TELEGRAM_BOT_TOKEN)")

        if options["live"]:
            self.check_live(host)

        self.stdout.write("")
        self.stdout.write("Remember: change the sample admin password before going live (`manage.py changepassword <e-mail>`).")
        fails, warns = self.results.count("FAIL"), self.results.count("WARN")
        summary = f"{self.results.count('OK')} OK, {warns} warning(s), {fails} problem(s)"
        self.stdout.write(self.style.ERROR(summary) if fails else (self.style.WARNING(summary) if warns else self.style.SUCCESS(summary)))
        if fails:
            raise CommandError("The site is not ready to go live yet.")

    # ---- the real website --------------------------------------------------------
    def fetch(self, url, follow=True):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None

        opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
        request = urllib.request.Request(url, headers={"User-Agent": "ALI-TRAVEL-site-check"})
        try:
            with opener.open(request, timeout=15) as response:
                return response.status, response.headers.get("Content-Type", ""), response.read(400000).decode("utf-8", "replace"), response.url
        except urllib.error.HTTPError as error:
            return error.code, error.headers.get("Content-Type", ""), "", url
        except Exception as error:  # DNS not set up yet, server down, certificate problem...
            return 0, "", str(error), url

    def check_live(self, host):
        self.stdout.write(self.style.MIGRATE_HEADING(f"Live website: {settings.SITE_URL}"))
        base = settings.SITE_URL
        checks = [("/", "text/html", "<div id=\"root\">"), ("/tours", "text/html", "<div id=\"root\">"), ("/api/destinations/", "application/json", "["),
                  ("/api/tours/", "application/json", "["), ("/api/site-content/", "application/json", "{"), ("/sitemap.xml", "xml", "<urlset"), ("/robots.txt", "text/plain", "Sitemap")]
        for path, kind, needle in checks:
            status, content_type, body, _ = self.fetch(base + path)
            good = status == 200 and kind in content_type and needle in body
            self.report("OK" if good else "FAIL", f"{path}  ->  {status or 'no answer'} {content_type.split(';')[0]}" + ("" if good else f"  {body[:90] if status == 0 else ''}"))
        if base.startswith("https://"):
            status, _, _, _ = self.fetch("http://" + host + "/", follow=False)
            self.report("OK" if status in (301, 302, 307, 308) else "WARN", f"http://{host}/ redirects to https" if status in (301, 302, 307, 308) else f"http://{host}/ answered {status or 'nothing'}: it should redirect to https")
