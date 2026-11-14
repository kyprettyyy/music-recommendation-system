from django.core.management.base import BaseCommand, CommandError
from music.models import Track, Interaction
from music.engine import GENRES

class Command(BaseCommand):
    help = "Create fictional tracks and synthetic users in an empty catalog"
    def handle(self, *args, **options):
        if Track.objects.exists():
            raise CommandError("Catalog must be empty; use a separate database for demo data")
        themes = [
            ("Midnight River", "river rain midnight road wandering home"),
            ("Quiet Garden", "garden light quiet morning leaves dreaming"),
            ("Open Highway", "highway home fields road sunshine freedom"),
            ("City Lights", "city dance night rhythm bright together"),
            ("Street Stories", "street city voice rhythm story tomorrow"),
            ("Blue Window", "window rain night quiet soft dreaming"),
            ("Thunder Sky", "thunder fire sky storm voice power"),
            ("Summer Letters", "summer love sunshine light together heart"),
            ("Island Breeze", "island ocean sunshine freedom rhythm home"),
            ("Wild Horizon", "road thunder freedom sky guitar tomorrow")]
        for j, genre in enumerate(GENRES):
            title, words = themes[j]
            for k in range(2):
                i = j*2+k+1
                Track.objects.create(id=i, title=f"{title} {k+1}", artist="Synthetic demo",
                    genre=genre, audio_url=f"/static/demo/{i}.wav",
                    lyrics=(words+" ")*4+("heart light" if k else "night home"), is_demo=True)
        for u in range(12):
            for i in {u%10*2+1, u%10*2+2, ((u+1)%10)*2+1}:
                Interaction.objects.create(actor=f"demo:{u}", track_id=i, liked=True, play_count=2)
        self.stdout.write("Created 20 fictional tracks and 12 synthetic listeners")
