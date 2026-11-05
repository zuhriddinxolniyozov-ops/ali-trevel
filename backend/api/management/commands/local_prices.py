from decimal import Decimal

from django.core.management.base import BaseCommand

from api.local_copy import remove_guide_from_local_tours, set_local_prices


class Command(BaseCommand):
    help = "Local site: set one tour's price in so'm and move all other prices by the same proportion; take the guide out of the tours."

    def add_arguments(self, parser):
        parser.add_argument("--tour", default="samarkand-city-tour")
        parser.add_argument("--price", type=Decimal, default=Decimal("600000"), help="the tour's new price in so'm (per person, biggest group)")

    def handle(self, *args, **options):
        factor = set_local_prices(options["tour"], options["price"])
        changed = remove_guide_from_local_tours()
        self.stdout.write(f"local price factor {factor}; tours without a guide now: {changed}")
