"""Accounting for the admin console: what each tour earned, what was paid, what it cost, and what is still owed.

Money rules (all in US dollars):
  total due = (agreed price, or the estimate when none was agreed) - discount
  balance   = total due - payments received
  profit    = total due - the costs booked against that tour
Revenue and profit only count tours that are marked *completed*.
"""
import csv
from datetime import date
from decimal import Decimal

from django.db.models import Q
from django.http import HttpResponse
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from . import models

ZERO = Decimal("0")
CENTS = Decimal("0.01")


def amount_field(**kwargs):
    return serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False, **kwargs)


class PaymentSerializer(serializers.ModelSerializer):
    amount_usd = amount_field(min_value=CENTS)

    class Meta:
        model = models.Payment
        fields = "__all__"


class ExpenseSerializer(serializers.ModelSerializer):
    amount_usd = amount_field(min_value=CENTS)

    class Meta:
        model = models.Expense
        fields = "__all__"


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = models.Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(booking_id=self.request.query_params["booking"]) if "booking" in self.request.query_params else qs


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = models.Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if "booking" in params:
            qs = qs.filter(booking_id=params["booking"])
        if params.get("general"):
            qs = qs.filter(booking__isnull=True)
        return qs


# ---------- calculations ----------

def parse_date(value):
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def service_date(booking):
    """The day the service was delivered: the end date, else the start date, else the day it was requested."""
    return booking.end_date or booking.travel_date or booking.created.date()


def in_range(day, start, end):
    return (not start or day >= start) and (not end or day <= end)


def money(booking):
    price = booking.final_price_usd if booking.final_price_usd is not None else booking.estimated_total_usd
    due = max(price - booking.discount_usd, ZERO)
    paid = sum((p.amount_usd for p in booking.payments.all()), ZERO)
    costs = sum((e.amount_usd for e in booking.expenses.all()), ZERO)
    balance = due - paid
    if due == 0:
        state = "unpriced"
    elif balance <= 0:
        state = "settled"
    elif paid > 0:
        state = "partial"
    else:
        state = "unpaid"
    return {"price": price, "total_due": due, "paid": paid, "balance": balance, "costs": costs, "profit": due - costs, "state": state}


def num(value):
    return float(value) if isinstance(value, Decimal) else value


def row(booking):
    m = money(booking)
    return {
        "id": booking.id, "reference": booking.reference, "service_type": booking.service_type, "service_slug": booking.service_slug,
        "service_title": booking.service_title, "full_name": booking.full_name, "email": booking.email, "phone": booking.phone,
        "guests": booking.guests, "status": booking.status, "travel_date": booking.travel_date, "end_date": booking.end_date,
        "service_date": service_date(booking).isoformat(), "estimated_total_usd": num(booking.estimated_total_usd),
        "final_price_usd": num(booking.final_price_usd), "discount_usd": num(booking.discount_usd),
        **{k: num(v) for k, v in m.items()},
        "payments": PaymentSerializer(booking.payments.all(), many=True).data,
        "expenses": ExpenseSerializer(booking.expenses.all(), many=True).data,
    }


def bookings_queryset():
    return models.BookingRequest.objects.prefetch_related("payments", "expenses")


# ---------- endpoints ----------

@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def ledger(request):
    """Tours with their money columns. ?status=completed|all|<status>, ?state=open|settled, ?q=text, ?from=&to="""
    params = request.query_params
    qs = bookings_queryset()
    if params.get("status", "completed") != "all":
        qs = qs.filter(status=params.get("status", "completed"))
    if params.get("q"):
        qs = qs.filter(Q(reference__icontains=params["q"]) | Q(full_name__icontains=params["q"]) | Q(service_title__icontains=params["q"]))
    start, end = parse_date(params.get("from")), parse_date(params.get("to"))
    rows = [row(b) for b in qs if in_range(service_date(b), start, end)]
    wanted = params.get("state")
    if wanted == "open":
        rows = [r for r in rows if r["state"] in ("unpaid", "partial")]
    elif wanted:
        rows = [r for r in rows if r["state"] == wanted]
    return Response(rows)


@api_view(["PATCH"])
@permission_classes([permissions.IsAdminUser])
def booking_finance(request, pk):
    """Set the agreed price and discount (or the status) of a booking."""
    booking = bookings_queryset().get(pk=pk)
    data = request.data
    if "final_price_usd" in data:
        booking.final_price_usd = None if data["final_price_usd"] in ("", None) else Decimal(str(data["final_price_usd"]))
    if "discount_usd" in data:
        booking.discount_usd = Decimal(str(data["discount_usd"] or 0))
    if data.get("status") in dict(models.BookingRequest.STATUS):
        booking.status = data["status"]
    if booking.discount_usd < 0:
        return Response({"error": "The discount cannot be negative."}, status=400)
    booking.save()
    return Response(row(booking))


@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def auto_costs(request, pk):
    """Fill the booking's expenses from the tour's cost template (replaces earlier automatic rows)."""
    booking = bookings_queryset().get(pk=pk)
    tour = models.Tour.objects.filter(slug=booking.service_slug).first()
    if not tour or not tour.cost_items:
        return Response({"error": "This tour has no cost template yet. Add one in the tour editor under “Costs for accounting”."}, status=400)
    days = max(1, len(tour.itinerary) or 1)
    categories = dict(models.Expense.CATEGORIES)
    booking.expenses.filter(auto=True).delete()
    for item in tour.cost_items:
        unit = Decimal(str(item.get("amount_usd") or 0))
        per = item.get("per", "group")
        quantity = booking.guests if per == "person" else days if per == "day" else 1
        if unit * quantity > 0:
            models.Expense.objects.create(
                booking=booking, category=item.get("category") if item.get("category") in categories else "other",
                description=str(item.get("name") or "Cost")[:200], amount_usd=unit * quantity, spent_on=service_date(booking), auto=True,
            )
    return Response(row(bookings_queryset().get(pk=pk)))


def month_keys(end, count=12):
    year, month, keys = end.year, end.month, []
    for _ in range(count):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return keys[::-1]


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def summary(request):
    """Totals for completed tours in a period (by the day the tour took place) plus a 12-month trend."""
    start, end = parse_date(request.query_params.get("from")), parse_date(request.query_params.get("to"))
    completed = [(b, service_date(b), money(b)) for b in bookings_queryset().filter(status="completed")]
    general = list(models.Expense.objects.filter(booking__isnull=True))
    chosen = [(b, d, m) for b, d, m in completed if in_range(d, start, end)]

    revenue = sum((m["total_due"] for _, _, m in chosen), ZERO)
    tour_costs = sum((m["costs"] for _, _, m in chosen), ZERO)
    general_costs = sum((e.amount_usd for e in general if in_range(e.spent_on, start, end)), ZERO)
    received = sum((p.amount_usd for p in models.Payment.objects.all() if in_range(p.paid_on, start, end)), ZERO)
    outstanding = sum((m["balance"] for _, _, m in chosen if m["balance"] > 0), ZERO)
    expenses = tour_costs + general_costs
    profit = revenue - expenses

    by_category = {}
    for b, _, _ in chosen:
        for e in b.expenses.all():
            by_category[e.category] = by_category.get(e.category, ZERO) + e.amount_usd
    for e in general:
        if in_range(e.spent_on, start, end):
            by_category[e.category] = by_category.get(e.category, ZERO) + e.amount_usd

    keys = month_keys(end or date.today())
    trend = {k: {"month": k, "revenue": ZERO, "expenses": ZERO} for k in keys}
    for b, d, m in completed:
        k = d.strftime("%Y-%m")
        if k in trend:
            trend[k]["revenue"] += m["total_due"]
            trend[k]["expenses"] += m["costs"]
    for e in general:
        k = e.spent_on.strftime("%Y-%m")
        if k in trend:
            trend[k]["expenses"] += e.amount_usd

    open_rows = sorted((row(b) for b, _, m in chosen if m["balance"] > 0), key=lambda r: -r["balance"])[:8]
    return Response({
        "revenue": num(revenue), "received": num(received), "outstanding": num(outstanding),
        "tour_costs": num(tour_costs), "general_costs": num(general_costs), "expenses": num(expenses), "profit": num(profit),
        "margin": round(float(profit / revenue * 100), 1) if revenue else 0,
        "completed": len(chosen), "settled": sum(1 for _, _, m in chosen if m["state"] == "settled"),
        "by_category": [{"category": k, "amount": num(v)} for k, v in sorted(by_category.items(), key=lambda kv: -kv[1])],
        "trend": [{k: num(v) for k, v in item.items()} for item in trend.values()],
        "receivables": open_rows,
    })


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def export_csv(request):
    """?kind=bookings (default) or ?kind=expenses, optionally ?from=&to=. Opens cleanly in Excel."""
    kind = request.query_params.get("kind", "bookings")
    start, end = parse_date(request.query_params.get("from")), parse_date(request.query_params.get("to"))
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="ali-travel-{kind}.csv"'
    response.write("﻿")
    out = csv.writer(response)
    if kind == "expenses":
        out.writerow(["Date", "Category", "Description", "Amount USD", "Paid to", "Tour reference", "Tour"])
        for e in models.Expense.objects.select_related("booking"):
            if in_range(e.spent_on, start, end):
                out.writerow([e.spent_on, e.category, e.description, e.amount_usd, e.paid_to,
                              e.booking.reference if e.booking else "", e.booking.service_title if e.booking else "General"])
    else:
        out.writerow(["Reference", "Service date", "Status", "Tour", "Customer", "Email", "Guests", "Price USD", "Discount USD",
                      "Total due USD", "Paid USD", "Balance USD", "Costs USD", "Profit USD", "Payment state"])
        for b in bookings_queryset().filter(status="completed"):
            if in_range(service_date(b), start, end):
                m = money(b)
                out.writerow([b.reference, service_date(b), b.status, b.service_title, b.full_name, b.email, b.guests, m["price"], b.discount_usd,
                              m["total_due"], m["paid"], m["balance"], m["costs"], m["profit"], m["state"]])
    return response


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def invoice(request, pk):
    booking = bookings_queryset().get(pk=pk)
    m = money(booking)
    site = models.SiteContent.objects.first()
    guests = max(booking.guests, 1)
    gross = m["price"]
    return Response({
        "number": f"INV-{booking.reference}", "issued": date.today().isoformat(),
        "company": {"name": "ALI TRAVEL", "email": site.email if site else "", "phone": site.phone_primary if site else "", "address": site.address if site else ""},
        "customer": {"name": booking.full_name, "email": booking.email, "phone": booking.phone},
        "service": {"title": booking.service_title, "from": booking.travel_date, "to": booking.end_date, "guests": booking.guests},
        "lines": [{"description": booking.service_title, "quantity": guests, "unit": num(gross / guests), "amount": num(gross)}],
        "discount": num(booking.discount_usd), "total": num(m["total_due"]), "paid": num(m["paid"]), "balance": num(m["balance"]),
        "payments": PaymentSerializer(booking.payments.all(), many=True).data,
    })
