# Validation record

Checks completed locally on 2026-11-14 using Python 3.11, Django 4.2.27, NumPy 1.26.4, SciPy 1.13.1, Gensim 4.3.3, PyTorch/torchaudio 2.2.2 CPU and SoundFile 0.14.0.

- Ten Django tests passed: collaborative ranking and consumed exclusion, lyric similarity, popularity cold start, explicit genre, invalid weights, private persistent favorites, repeated plays, account persistence, invalid requests, CSRF, catalog search and corrupted/mismatched feature indexes.
- Django system checks passed; migration consistency reported no changes.
- The actual demo pipeline created twenty synthetic tracks, twelve synthetic users, generated tone files, and trained 32-dimensional skip-gram Word2Vec features.
- Real-data integration imported 200 tracks into a separate database, generated all 200 AlexNet feature vectors, and returned five valid audio-only rankings through the Django API when lyric/user data were absent.
- The supplied `best_model_okk.pth` loaded successfully and processed all 200 recordings from the test ZIP. This produced 200/200 matching labels and cross-entropy about 0.007947. **The checkpoint's original training provenance is unknown; this cannot be reported as independently held-out accuracy or evidence of generalization.** It is recorded only as a compatibility result.
- A new training CLI completed one epoch with four real training-archive recordings (three train, one internal validation). The tiny validation run scored zero correct; it verifies execution, not model quality. No full retraining was performed.
- All 453 supplied project files were hashed into 153 canonical filename groups. Download variants had identical content within every group. SQLite schemas were inspected read-only; original databases and weights remain excluded. No claim is made that every original image or media sample was visually reviewed.

Machine-readable results are in `validation.json`. Generated models, databases and feature indexes are local artifacts excluded from Git. GitHub Actions is configured to run core tests and the demo build after upload; no remote CI run is claimed. Browser-level visual QA and real-world relevance evaluation have not been completed.
