from django.db.models.signals import post_save
from django.dispatch import receiver

from . import accounting, models


@receiver(post_save, sender=models.BookingRequest)
def keep_costs_in_step(sender, instance, **kwargs):
    """Confirmed and completed bookings get their expected costs added automatically; other statuses have none."""
    if kwargs.get("raw"):
        return
    update = kwargs.get("update_fields")
    if update is not None and not ({"status", "guests", "final_price_usd", "discount_usd", "travel_date", "end_date"} & set(update)):
        return  # e.g. only the arrival details were saved
    accounting.sync_costs(instance)
