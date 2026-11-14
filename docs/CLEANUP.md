# Archive review

Kept 125 canonical source/asset files before adding documentation. Excluded 328 duplicate or irrelevant files. Hashed download variants, IDE state, bytecode, SQLite databases, checkpoints and unrelated SVM code were excluded. Notebook outputs were cleared; player background images were retained at their supplied resolution.

Configuration now uses environment variables or an ephemeral development secret. Inference paths resolve relative to the source rather than the working directory. Static audio URLs are generated independently of disk paths. Candidate sampling uses dataset length; same-genre sampling uses annotation labels. Invalid genre parameters return HTTP 400.

The notebook validation loop used the training batch instead of the test batch; corrected and switched to evaluation mode during validation. Other historical notebook limitations remain, including raw test annotations requiring conversion and hard-coded device/path assumptions. No accuracy claims are made.

Original artifacts remain untouched outside this repository. No verified source license was supplied; provenance is retained in THIRD_PARTY.md.
