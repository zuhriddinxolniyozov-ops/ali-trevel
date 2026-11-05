"""Daily health check of the live site: `python manage.py watch_site` (the server runs it every morning from cron).

It looks at what a visitor's browser sees and warns the team (Telegram, in Uzbek, and e-mail) before visitors notice:
  * the https certificate expires in fewer than WARN_DAYS days (normally certbot renews it 30 days before; if that keeps
    failing the site would show "not secure" when it runs out);
  * the domain points at another address than this server's (for example after an IP change), so the site does not open.
Nothing is sent while everything is fine. `--test` sends the report even then, to check that the alerts arrive.
"""
import datetime
import html
import json
import socket
import ssl
import urllib.request
from urllib.parse import urlsplit

from django.conf import settings
from django.core.management.base import BaseCommand

from api import notifications

WARN_DAYS = 21


def certificate_days_left(host):
    """Days until the certificate served for `host` expires (None if it cannot be read, e.g. it is already invalid)."""
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=15) as raw, context.wrap_socket(raw, server_hostname=host) as tls:
            ends = datetime.datetime.strptime(tls.getpeercert()["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.UTC)
    except (OSError, ssl.SSLError, KeyError, ValueError):
        return None
    return (ends - datetime.datetime.now(datetime.UTC)).days


def own_address():
    """This server's public IPv4 address as the outside world sees it ('' when unknown)."""
    try:
        with urllib.request.urlopen("https://checkip.amazonaws.com", timeout=10) as response:
            return response.read().decode().strip()
    except OSError:
        return ""


class Command(BaseCommand):
    help = "Update the local site's dollar rate, and warn the team when the https certificate is about to run out or the domain no longer points at this server."

    def add_arguments(self, parser):
        parser.add_argument("--test", action="store_true", help="send the report even when everything is fine")

    def handle(self, *args, **options):
        from api.local_copy import update_rate
        rate = update_rate()   # every morning the local site's so'm prices follow the Central Bank dollar rate
        self.stdout.write(f"dollar rate: {rate or 'not updated'}")
        host = urlsplit(settings.SITE_URL).hostname or ""
        if not settings.SITE_URL.startswith("https://") or host in ("", "localhost", "127.0.0.1"):
            self.stdout.write("SITE_URL is not a public https address; nothing to watch.")
            return
        problems = []
        try:
            pointed = socket.gethostbyname(host)
        except OSError:
            pointed = ""
        mine = own_address()
        if not pointed:
            problems.append(f"🌐 {host} domeni hech qayerga yo'naltirilmagan (DNS javob bermayapti).")
        elif mine and pointed != mine:
            problems.append(f"🌐 {host} domeni {pointed} manziliga qaraydi, server esa {mine} da. aHOST DNS menejerda @ A yozuvini {mine} ga o'zgartiring.")
        days = certificate_days_left(host)
        if days is None:
            problems.append(f"🔒 {host} uchun HTTPS sertifikatini o'qib bo'lmadi: sayt \"xavfsiz emas\" deb chiqishi mumkin.")
        elif days < WARN_DAYS:
            problems.append(f"🔒 HTTPS sertifikati {days} kundan keyin tugaydi va o'zi yangilanmayapti. Serverda: sudo certbot renew")
        state = f"sertifikat: {days if days is not None else '?'} kun qoldi; domen: {pointed or '?'}; server: {mine or '?'}"
        self.stdout.write(state)
        if problems or options["test"]:
            body = "\n".join(problems) if problems else "✅ Hammasi joyida."
            title = "⚠️ ALI TRAVEL sayt tekshiruvi" if problems else "ALI TRAVEL sayt tekshiruvi"
            notifications._tell_the_team(f"ALI TRAVEL: sayt tekshiruvi ({host})", f"{body}\n\n{state}",
                                         telegram_html=f"<b>{title}</b>\n\n{html.escape(body, quote=False)}\n\n<i>{html.escape(state, quote=False)}</i>")
            self.stdout.write(json.dumps({"sent": True, "problems": len(problems)}))
