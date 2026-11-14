import json
import random
import math
import wave
import struct
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from music.engine import GENRES, tokenize
from music.models import Track

class Command(BaseCommand):
    help = "Train skip-gram Word2Vec and build optional AlexNet audio features"
    def add_arguments(self, parser):
        parser.add_argument("--demo", action="store_true")
        parser.add_argument("--checkpoint")
        parser.add_argument("--audio-root")
    def handle(self, *args, **options):
        import numpy as np
        from gensim.models import Word2Vec
        tracks = list(Track.objects.order_by("pk"))
        if not tracks:
            raise CommandError("Import tracks or run seed_demo first")
        if options["demo"] and any(not t.is_demo for t in tracks):
            raise CommandError("--demo requires an entirely synthetic catalog")
        sentences = [tokenize(t.lyrics) for t in tracks]
        corpus = [s for s in sentences if s]
        model = Word2Vec(corpus, vector_size=32, window=4, min_count=1, sg=1,
            workers=1, seed=42, epochs=80) if corpus else None
        predictor = None
        if not options["demo"] and options["checkpoint"]:
            if not options["audio_root"]:
                raise CommandError("--audio-root is required with --checkpoint")
            from music.audio import AudioPredictor
            predictor = AudioPredictor(options["checkpoint"])
        index = {}
        for track, words in zip(tracks, sentences):
            vectors = [model.wv[w] for w in words if model and w in model.wv]
            feature = {"title": track.title, "lyrics": np.mean(vectors, axis=0).tolist() if vectors else [],
                "audio": [], "source": "word2vec-lyrics; audio-unavailable"}
            if options["demo"]:
                rng = random.Random(track.pk)
                scores = [rng.uniform(.01,.05) for _ in GENRES]
                scores[GENRES.index(track.genre)] = .8
                feature["audio"] = [v/sum(scores) for v in scores]
                feature["source"] = "synthetic-audio-scores; word2vec-on-fictional-lyrics"
                folder = Path(settings.BASE_DIR)/"music/static/demo"
                folder.mkdir(parents=True, exist_ok=True)
                with wave.open(str(folder/f"{track.pk}.wav"), "wb") as f:
                    f.setparams((1,2,22050,0,"NONE","not compressed"))
                    f.writeframes(b"".join(struct.pack("<h",int(3000*math.sin(2*math.pi*(180+track.pk*20)*i/22050))) for i in range(22050)))
            elif predictor:
                root = Path(options["audio_root"]).resolve()
                audio = (root/track.genre/track.title).resolve()
                if not audio.is_relative_to(root):
                    raise CommandError("Audio path outside root")
                feature["audio"] = predictor.scores(audio)
                feature["source"] = "alexnet-mfcc; word2vec-lyrics" if vectors else "alexnet-mfcc; lyrics-unavailable"
            index[str(track.pk)] = feature
        output = Path(settings.MUSIC_FEATURE_PATH)
        output.parent.mkdir(parents=True, exist_ok=True)
        temp = output.with_suffix(".tmp")
        temp.write_text(json.dumps(index, indent=2), encoding="utf-8")
        temp.replace(output)
        self.stdout.write(f"Built {len(index)} track features")
