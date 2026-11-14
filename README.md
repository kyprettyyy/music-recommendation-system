# Multimodal Music Recommendation System

[中文说明](README.zh-CN.md) · [Architecture](docs/ARCHITECTURE.md) · [Validation](docs/VALIDATION.md) · [Provenance](THIRD_PARTY.md)

Django music recommendation app combining implicit-feedback collaborative filtering, Word2Vec lyric embeddings and AlexNet/MFCC audio genre features. Search, persistent favorites, listening history, account registration/login and explainable top-five rankings are available.

The supplied 2022 project implemented audio classification and genre-based ranking. Hybrid ranking and the current application were added during a November 2026 restoration based on the supplied résumé and course report. See [claim mapping](docs/RESUME_MAPPING.md). The repository preserves the original author's supplied README and credits.

## Run the self-contained demo

Python 3.11 is the tested runtime. Windows users can run `start-demo.cmd` for setup and launch (network required on first setup). From this repository directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-core.txt
python recommend/manage.py migrate
python recommend/manage.py seed_demo
python recommend/manage.py build_features --demo
python recommend/manage.py runserver
```

Open http://127.0.0.1:8000/ . Play a track or favorite it, then refresh recommendations. Demo tracks are original one-second tones with fictional lyrics and synthetic listener histories. Demo audio scores are synthetic; lyric vectors are actually trained using skip-gram Word2Vec. They demonstrate execution, not music recommendation quality. `seed_demo` requires an empty database; feature building can be rerun. An exhausted catalog may return fewer than five unseen tracks.

The app operates without PyTorch in demo mode. Guest preferences persist in the browser session; account preferences follow a registered user across sessions. Guest activity is not automatically merged on login. Django admin supports track and interaction management after `python recommend/manage.py createsuperuser`.

## Real audio and lyrics

Install full dependencies with `python -m pip install -r requirements.txt`. Obtain compatible trusted weights and GTZAN separately; they are excluded from this repository. Detailed [data and training instructions](docs/REAL_DATA.md) cover ZIP extraction, CSV conversion, catalog import, lyric import, feature building, training and evaluation. Real catalog import requires a separate empty database.

GTZAN has no supplied lyrics or real user interaction history. Word2Vec and collaborative filtering cannot establish real-world quality without those data. Missing features are omitted and available weights are normalized. No lyrics are fabricated for real GTZAN tracks.

## Verification

```powershell
python recommend/manage.py test music
python recommend/manage.py check
```

Ten automated tests cover collaborative ranking, lyric similarity, genre preference, cold start, exclusion of consumed tracks, private favorites, account persistence, CSRF, bad requests and stale feature indexes. A real 200-file audio compatibility run and a small one-epoch training smoke test completed. These do not establish independent recommendation quality; see [validation limits](docs/VALIDATION.md).

## Repository layout

- `recommend/music/engine.py`: hybrid scoring independent of Django.
- `recommend/music/api.py`, `models.py`, `templates/hybrid.html`: current web app.
- `recommend/music/audio.py`, `nn/net.py`: MFCC and AlexNet inference.
- `recommend/music/management/commands/`: import, demo and feature commands.
- `scripts/`: safe ZIP preparation and reproducible audio training/evaluation.
- `recommend.ipynb`, legacy views/templates/static assets: historical material; the active URL table uses the restored app.
- `picture/`: historical screenshots and diagrams, not screenshots of the restored UI.

Local study defaults to debug mode. Configure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` separately for deployment. Optional `MUSIC_DATABASE_PATH` and `MUSIC_FEATURE_PATH` keep independent experiments isolated. No production deployment has been assessed. No blanket license is assigned to third-party material.
