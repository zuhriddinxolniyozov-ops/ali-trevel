"""sitemap.xml and robots.txt, so search engines can find every public page."""
from xml.sax.saxutils import escape

from django.conf import settings
from django.http import HttpResponse

from . import models

STATIC_PAGES = ["/", "/destinations", "/tours", "/hotels", "/transport", "/food", "/plan", "/about", "/contact",
                "/legal/privacy", "/legal/terms", "/legal/cancellation", "/credits"]


def public_paths():
    paths = list(STATIC_PAGES)
    paths += [f"/destinations/{slug}" for slug in models.Destination.objects.filter(status="published").values_list("slug", flat=True)]
    paths += [f"/tours/{slug}" for slug in models.Tour.objects.filter(status="published").values_list("slug", flat=True)]
    paths += [f"/hotels/{slug}" for slug in models.Hotel.objects.filter(status="published").values_list("slug", flat=True)]
    return paths


def sitemap(request):
    rows = "".join(f"<url><loc>{escape(settings.SITE_URL + path)}</loc></url>" for path in public_paths())
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>'
    return HttpResponse(xml, content_type="application/xml")


def robots(request):
    text = f"User-agent: *\nDisallow: /admin\nDisallow: /account\nDisallow: /api/\nAllow: /\n\nSitemap: {settings.SITE_URL}/sitemap.xml\n"
    return HttpResponse(text, content_type="text/plain")
