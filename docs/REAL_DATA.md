# Real data and audio workflow

Use Python 3.11 and install `requirements.txt`. All paths below are examples relative to the repository root. Use absolute paths for environment variables. The extraction command refuses to overwrite existing files and skips redundant spectrogram images.

## Prepare the dataset

```powershell
python scripts/prepare_gtzan.py "PATH_TO_TRAIN/gtzan.zip" artifacts/train
python scripts/prepare_gtzan.py "PATH_TO_TEST/gtzan_test.zip" artifacts/test
```

This produces `artifacts/train/GTZAN/genres_original`, `artifacts/test/GTZAN_TEST/genres_original`, raw CSVs and converted `_final.csv` annotations for the dataset loader. The import commands use raw CSV column names directly. A full archive has 1000 audio files; the split archives have 800 and 200. Their training/test filenames do not overlap, but artist and recording leakage has not been audited. The split training ZIP also retains the complete 3-second feature CSV; do not assume it is a properly split training table.

## Train and evaluate

```powershell
python scripts/train_audio.py train --annotations artifacts/train/GTZAN/features_30_sec.csv --audio-root artifacts/train/GTZAN/genres_original --epochs 20 --checkpoint artifacts/alexnet.pth --report artifacts/train_metrics.json
python scripts/train_audio.py evaluate --annotations artifacts/test/GTZAN_TEST/features_30_sec_test.csv --audio-root artifacts/test/GTZAN_TEST/genres_original --checkpoint artifacts/alexnet.pth --report artifacts/test_metrics.json
```

Training reserves a seeded 10% validation subset of the supplied training CSV. Checkpoint selection uses that validation subset; held-out test data are evaluated separately. This is a basic recording-level split, not a guarantee of artist-independent generalization. Use `--device cuda` only with a compatible CUDA installation. Broken audio files fail visibly; repair or explicitly exclude them from the annotations before training rather than silently skipping them.

The scripts use a shared MFCC configuration for training and inference. Torchaudio warns that some mel filters are zero because the original default FFT size is small. Improving this requires retraining and validating the feature/network contract. Checkpoints are loaded with `weights_only=True`; do not use untrusted model files.

## Import a real catalog

Use a separate empty database and feature index, so demo data do not contaminate real rankings:

```powershell
$env:MUSIC_DATABASE_PATH = "ABSOLUTE_PATH_TO/artifacts/real.sqlite3"
$env:MUSIC_FEATURE_PATH = "ABSOLUTE_PATH_TO/artifacts/real_features.json"
python recommend/manage.py migrate
python recommend/manage.py import_catalog artifacts/train/GTZAN/features_30_sec.csv
python recommend/manage.py build_features --checkpoint artifacts/alexnet.pth --audio-root artifacts/train/GTZAN/genres_original
python recommend/manage.py runserver
```

Create the parent `artifacts` directory first. For browser playback, copy the imported genre folders into `recommend/music/static/GTZAN/genres_original/`, or map the generated `/static/GTZAN/genres_original/...` URLs to the local dataset in your own static server. Merely generating a feature index does not copy audio files.

Optional lyric input is a UTF-8 CSV with columns `filename,lyrics`. Supply it with `import_catalog ... --lyrics path/to/lyrics.csv` in an empty database. The command trains vectors on the supplied lyric corpus when `build_features` runs. Real GTZAN has no provided lyric corpus or human interaction histories. With no lyrics, lyric vectors remain empty; with no interaction overlap, collaborative scores are unavailable. Explicit genre selection enables audio-based cold start. Real user plays and favorites gradually supply feedback.

`build_features` without `--checkpoint` can produce lyric-only features. `build_features --demo` is reserved for synthetic catalogs; it does not use a trained audio network. Demo score vectors are generated rather than inferred.
