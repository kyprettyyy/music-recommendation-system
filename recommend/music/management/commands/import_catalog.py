import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from music.models import Track
from music.engine import GENRES

class Command(BaseCommand):
    help = "Import original GTZAN CSV; optional lyrics CSV has filename,lyrics columns"
    def add_arguments(self, parser):
        parser.add_argument("annotations")
        parser.add_argument("--lyrics")
    @transaction.atomic
    def handle(self, *args, **options):
        if Track.objects.exists():
            raise CommandError("Catalog must be empty to avoid mixing demo and real data")
        lyrics = {}
        if options["lyrics"]:
            with open(options["lyrics"],encoding="utf-8-sig",newline="") as f:
                lyrics = {r["filename"]: r["lyrics"] for r in csv.DictReader(f)}
        with open(options["annotations"],encoding="utf-8-sig",newline="") as f:
            for r in csv.DictReader(f):
                name, genre = r["filename"], r["label"]
                if genre not in GENRES or Path(name).name != name or "/" in name or chr(92) in name:
                    raise CommandError("Invalid filename or genre")
                Track.objects.create(title=name, genre=genre, lyrics=lyrics.get(name,""),
                    audio_url=f"/static/GTZAN/genres_original/{genre}/{name}")
        self.stdout.write(f"Imported {Track.objects.count()} tracks")
