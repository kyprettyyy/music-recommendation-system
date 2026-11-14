# Recommendation architecture

The web application records positive implicit feedback in SQLite. Each actor is an authenticated account or a random session identity; the API never accepts another user's identity from a request. Play strength is capped at 10 and a current favorite adds 3. Removing a favorite leaves genuine play history intact.

## Scoring

For user u, cosine similarity between sparse interaction vectors selects neighbors with positive overlap. A candidate's collaborative score is the similarity-weighted mean of neighbor strengths normalized by each neighbor's maximum strength. Items missing from neighbor histories contribute zero.

Lyrics are tokenized into lowercase Latin words or individual Han characters. Skip-gram Word2Vec trains 32-dimensional embeddings with window 4, min_count 1, workers 1, seed 42 and 80 epochs. Track vectors average in-vocabulary tokens; user vectors average consumed track vectors with implicit strengths. Negative cosine is clipped to zero. This small-corpus baseline does not promise robust language understanding; more data and proper Chinese segmentation would be needed for realistic use.

Real audio is mixed to mono, resampled to 22050 Hz, cropped/padded to five seconds and transformed to 128 MFCC coefficients using the configured torchaudio defaults. AlexNet produces ten logits, converted to softmax scores. The audio preference vector averages consumed track scores, or uses an explicit one-hot genre preference. Candidate audio relevance uses cosine similarity. These softmax values are not calibrated probabilities.

The final score uses collaborative/lyrics/audio weights 0.4/0.3/0.3, normalized over available modalities for each candidate. Without a usable modality, normalized popularity supplies a deterministic fallback. Consumed tracks are excluded. Scores from different modality subsets are approximate and have not been calibrated against human relevance judgments. Every result reports component scores, effective weights and feature provenance.

## Runtime

The website reads a prebuilt JSON feature index rather than re-running PyTorch on each request. Features include track titles to reject an index belonging to another catalog. Vectors are checked for dimensions and finite values. Building features is atomic at the output-file level; rebuilding is required after changing lyrics or audio models.

Search, favorites, playback and recommendations use same-origin endpoints. POST events require Django CSRF tokens; database increments avoid lost play counts. Django's account forms apply password validation. Seeded demo actors use a reserved `demo:` prefix. No real personal listening history is bundled.

The baseline scans the catalog and histories in memory and is intended for coursework-scale collections, not production scale. No recommendation quality evaluation has been performed. No lyrics-timestamp synchronization is claimed: GTZAN supplies no lyrics or timestamps.
