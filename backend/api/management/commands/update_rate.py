from django.core.management.base import BaseCommand

from api.local_copy import update_rate


class Command(BaseCommand):
    help = "Read today's Central Bank dollar rate and move the automatic so'm prices of the local site to it."

    def handle(self, *args, **options):
        rate = update_rate()
        self.stdout.write(f"rate: {rate}" if rate else "The rate could not be read (or the local site does not exist yet); prices unchanged.")
