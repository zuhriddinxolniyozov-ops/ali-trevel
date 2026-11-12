from django.core.management.base import BaseCommand

from api import models
from api.local_copy import make_local
from api.market import GLOBAL, LOCAL, use
from api.management.commands.seed_short_walks import WALKS, walk_fields


class Command(BaseCommand):
    help = "Add the 2, 3 and 4-hour Samarkand walks to the global site and copy them to the local one. Existing ones are left as they are."

    def handle(self, *args, **options):
        added = 0
        with use(GLOBAL):
            for w in WALKS:
                if not models.Tour.objects.filter(slug=w["slug"]).exists():
                    models.Tour.objects.create(slug=w["slug"], **walk_fields(w))
                    added += 1
        self.stdout.write(f"global site: {added} walks added")
        with use(LOCAL):
            site = models.SiteContent.objects.order_by("pk").first()
        if site and site.usd_rate:
            copied = make_local(site.usd_rate)
            self.stdout.write(f"local site: {copied.get('tours', 0)} copied")
