"""Two versions of the site: "global" (prices in US dollars, the default) and "local" (for Uzbekistan, prices in so'm).

Every listing, booking and setting belongs to one of them. The site and the admin panel say which one they show with the
``X-Market`` header; the middleware below makes it the current market for the request, and the models' default manager only
returns rows of the current market. Code that runs outside a request (the Telegram bot, e-mails, commands) works with the
global market unless it switches with ``use("local")``.
"""
import contextlib
import contextvars
import json
import urllib.request
from decimal import ROUND_HALF_UP, Decimal

GLOBAL, LOCAL = "global", "local"
MARKETS = (GLOBAL, LOCAL)
LOCAL_DISCOUNT = Decimal("0.70")   # local prices start 30% below the global (dollar) price
CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/"

_current = contextvars.ContextVar("market", default=GLOBAL)


def current():
    return _current.get()


def default_market():
    """Field default: a new row belongs to the market of the request (or command) that creates it."""
    return _current.get()


@contextlib.contextmanager
def use(market):
    token = _current.set(market if market in MARKETS else GLOBAL)
    try:
        yield
    finally:
        _current.reset(token)


class MarketMiddleware:
    """Reads ``X-Market`` (or ``?market=``) and makes it the current market while the request runs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        wanted = request.headers.get("X-Market") or request.GET.get("market") or GLOBAL
        with use(wanted):
            return self.get_response(request)


def round_som(amount):
    """So'm prices in whole ten thousands from 100 000 (so a small move of the dollar rate does not change them), whole thousands
    from 10 000, hundreds below."""
    value = Decimal(str(amount or 0))
    step = Decimal(10000) if value >= 100000 else Decimal(1000) if value >= 10000 else Decimal(100)
    return ((value / step).quantize(Decimal(1), rounding=ROUND_HALF_UP) * step) if value > 0 else Decimal(0)


def to_local_price(usd, rate, factor=LOCAL_DISCOUNT):
    """A traveller's price in so'm: the dollar price x the local price factor (see SiteContent.local_price_factor) x the rate."""
    return None if usd is None else round_som(Decimal(str(usd)) * Decimal(str(factor)) * Decimal(str(rate)))


def to_local_cost(usd, rate):
    """What something costs the company, in so'm (no discount: a cost is a cost)."""
    return None if usd is None else round_som(Decimal(str(usd)) * Decimal(str(rate)))


def money(amount, market=None, decimals=True):
    """$1,290.00 for the global site, 1 873 000 so'm for the local one."""
    value = Decimal(str(amount or 0))
    if (market or current()) == LOCAL:
        return f"{int(value.quantize(Decimal(1), rounding=ROUND_HALF_UP)):,}".replace(",", " ") + " so'm"
    return f"${value:,.2f}" if decimals else f"${value:,.0f}"


# Where the dollar rate is read, in order. The Central Bank's site does not answer servers abroad (the site runs in Australia),
# so two public sources of the same day's market rate follow it; they differ from the official rate by a fraction of a percent.
RATE_SOURCES = (
    (CBU_URL, lambda data: data[0]["Rate"]),
    ("https://open.er-api.com/v6/latest/USD", lambda data: data["rates"]["UZS"]),
    ("https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json", lambda data: data["usd"]["uzs"]),
)


def _read(url, pick, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": "ALI TRAVEL site"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    rate = Decimal(str(pick(data))).quantize(Decimal("0.01"))
    return rate if 1000 < rate < 1000000 else None


def fetch_rate_with_source(timeout=12):
    """(so'm for 1 USD, where it was read) — the Central Bank first — or (None, "") when no source answers."""
    for url, pick in RATE_SOURCES:
        try:
            rate = _read(url, pick, timeout)
        except Exception:  # network trouble or a changed format: try the next source
            continue
        if rate:
            return rate, url.split("/")[2]
    return None, ""


def fetch_cbu_rate(timeout=12):
    """Today's dollar rate (so'm for 1 USD), or None when it cannot be read: keep the last known rate then."""
    return fetch_rate_with_source(timeout)[0]
