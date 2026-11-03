"""Serve the built website (frontend/dist) and the uploaded photos from Django itself.

On a live server this means one process answers everything: the pages, the API, sitemap.xml and the photos. For heavy traffic nginx can
take over the files (see deploy/nginx.conf); this keeps working either way. Turned on with SERVE_FRONTEND (default: on when DEBUG is off).
"""
import os

from django.conf import settings
from django.http import Http404, HttpResponse
from django.utils._os import safe_join
from django.views.static import serve

RESERVED = ("api/", "media/", "django-admin/", "static/")


def _with_headers(response, cache):
    response["Cache-Control"] = cache
    return response


def website(request, path=""):
    """Any address that is not the API or a file belongs to the React app, which draws the page itself."""
    if not settings.SERVE_FRONTEND:
        raise Http404
    path = path.lstrip("/")
    if path.startswith(RESERVED) or path in ("api", "media", "django-admin"):
        raise Http404
    root = settings.FRONTEND_DIST
    if path:
        try:
            candidate = safe_join(root, path)
        except Exception:  # an attempt to climb out of the folder
            raise Http404
        if os.path.isfile(candidate):
            # built files carry a hash in their name, so browsers may keep them for a year; anything else is checked every time
            cache = "public, max-age=31536000, immutable" if path.startswith("assets/") else "public, max-age=300"
            return _with_headers(serve(request, path, document_root=root), cache)
        if "." in path.rsplit("/", 1)[-1]:  # a missing file such as /assets/old.js must be a real 404, not the home page
            raise Http404
    index = root / "index.html"
    if not index.exists():
        return HttpResponse("The website has not been built yet: run `npm run build` in the frontend folder.", status=503, content_type="text/plain")
    return _with_headers(serve(request, "index.html", document_root=root), "no-cache")


def media(request, path):
    if not settings.SERVE_FRONTEND:
        raise Http404
    return _with_headers(serve(request, path, document_root=settings.MEDIA_ROOT), "public, max-age=2592000")
