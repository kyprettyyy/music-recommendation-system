# Multimodal Music Recommendation System

A Django music recommendation application combining listening behavior, lyric embeddings, and audio genre features. Users can browse tracks, search the catalog, save favorites, and receive personalized top-five recommendations.

## Features

- User registration, login, and persistent favorites.
- Track search by title, artist, and genre.
- Playback history and implicit-feedback collaborative filtering.
- Skip-gram Word2Vec lyric embeddings and cosine similarity.
- AlexNet genre classification from MFCC audio features.
- Hybrid rankings with a breakdown of each recommendation score.

## Recommendation pipeline

The recommender combines user-based collaborative filtering, lyric similarity, and audio similarity with default weights of 0.4, 0.3, and 0.3. It adjusts the weights when a feature is unavailable, excludes consumed tracks, and uses popularity or an explicit genre preference for cold starts.

Audio is converted to mono at 22,050 Hz, cropped or padded to five seconds, and transformed into 128 MFCC coefficients. An AlexNet-style network produces scores for ten music genres. Word2Vec maps lyrics to 32-dimensional track vectors.

## Quick start

Use Python 3.11. On Windows, run `start-demo.cmd`, or execute:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-core.txt
python recommend/manage.py migrate
python recommend/manage.py seed_demo
python recommend/manage.py build_features --demo
python recommend/manage.py runserver
```

Open `http://127.0.0.1:8000/`. Play or favorite a track, then refresh recommendations.

The demo includes generated tones, fictional lyrics, and sample listener histories. Demo audio scores are synthetic; Word2Vec embeddings are trained from the demo lyrics. For real audio, install `requirements.txt` and follow the [data setup guide](docs/REAL_DATA.md).

## Project structure

```text
recommend/music/engine.py      Hybrid recommendation scoring
recommend/music/audio.py       MFCC extraction and audio inference
recommend/music/nn/            AlexNet and dataset loader
recommend/music/management/    Catalog and feature commands
recommend/music/templates/     Web pages
scripts/                       Data preparation and model training
```

## Tests

```powershell
python recommend/manage.py test music
```

[Architecture](docs/ARCHITECTURE.md) · [Data and training](docs/REAL_DATA.md) · [Acknowledgements](THIRD_PARTY.md)
