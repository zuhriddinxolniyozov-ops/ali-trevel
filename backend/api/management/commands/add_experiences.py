from django.core.management.base import BaseCommand

from api import models
from api.local_copy import make_local
from api.market import GLOBAL, LOCAL, use
from api.management.commands.seed_activities import EXPERIENCES, tour_fields


class Command(BaseCommand):
    help = "Add the short experiences (photo shoots, evening walks, a wedding, day trips) to the global site and copy them to the local one. Existing ones are left as they are."

    def handle(self, *args, **options):
        added = 0
        with use(GLOBAL):
            for e in EXPERIENCES:
                if not models.Tour.objects.filter(slug=e["slug"]).exists():
                    models.Tour.objects.create(slug=e["slug"], **tour_fields(e))
                    added += 1
        self.stdout.write(f"global site: {added} experiences added")
        with use(LOCAL):
            site = models.SiteContent.objects.order_by("pk").first()
        if site and site.usd_rate:
            copied = make_local(site.usd_rate)
            self.stdout.write(f"local site: {copied.get('tours', 0)} copied")
