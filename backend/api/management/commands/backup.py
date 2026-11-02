"""Make a dated copy of the database (and the uploaded photos) so nothing is lost: `python manage.py backup`.

SQLite is copied with SQLite's own backup call, which is safe while the site is running. For PostgreSQL the data is exported to JSON
(restore it with `loaddata`). Old copies are removed, keeping the newest `--keep` ones. Run it every night from cron or Task Scheduler.
"""
import datetime
import json
import shutil
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Copy the database and uploaded photos into backend/backups/."

    def add_arguments(self, parser):
        parser.add_argument("--keep", type=int, default=14, help="How many backups to keep (default 14).")
        parser.add_argument("--to", default=str(settings.BASE_DIR / "backups"), help="Folder for the backups.")

    def handle(self, *args, **options):
        target = Path(options["to"])
        target.mkdir(parents=True, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        database = settings.DATABASES["default"]
        if database["ENGINE"].endswith("sqlite3"):
            destination = target / f"db-{stamp}.sqlite3"
            source = sqlite3.connect(str(database["NAME"]))
            copy = sqlite3.connect(str(destination))
            with copy:
                source.backup(copy)
            copy.close()
            source.close()
        else:
            destination = target / f"data-{stamp}.json"
            with open(destination, "w", encoding="utf-8") as handle:
                call_command("dumpdata", "--natural-foreign", "--natural-primary", "--exclude", "contenttypes", "--exclude", "auth.permission", stdout=handle)
            json.loads(destination.read_text(encoding="utf-8") or "[]")  # fail loudly if the export is not valid
        media = Path(settings.MEDIA_ROOT)
        if media.exists() and any(media.iterdir()):
            shutil.make_archive(str(target / f"media-{stamp}"), "zip", media)
        for pattern in ("db-*.sqlite3", "data-*.json", "media-*.zip"):
            for old in sorted(target.glob(pattern))[: -options["keep"] or None]:
                old.unlink()
        self.stdout.write(self.style.SUCCESS(f"Backup saved: {destination}"))
