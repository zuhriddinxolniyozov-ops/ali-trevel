from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from api.local_copy import make_local
from api.market import fetch_rate_with_source


class Command(BaseCommand):
    help = "Create the local (so'm) site as a copy of the global one: prices 30% lower, converted at today's dollar rate (Central Bank first). Safe to run again."

    def add_arguments(self, parser):
        parser.add_argument("--rate", type=Decimal, help="so'm for 1 US dollar (default: today's Central Bank rate)")

    def handle(self, *args, **options):
        rate, source = (options["rate"], "given") if options["rate"] else fetch_rate_with_source()
        if not rate:
            raise CommandError("The dollar rate could not be read; run again later or pass --rate.")
        added = make_local(rate)
        self.stdout.write(f"rate {rate} ({source}): " + ", ".join(f"{k} {v}" for k, v in added.items()))
