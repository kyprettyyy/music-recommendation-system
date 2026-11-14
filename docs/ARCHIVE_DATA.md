# ZIP archive inspection

Seven completed ZIP files represent three distinct file inventories (matching names, sizes and CRCs within each group):

| Group | Audio recordings | Other contents |
| --- | ---: | --- |
| Full GTZAN (2 copies) | 1000 WAV | 999 PNG, 30-second and 3-second feature CSVs |
| Training split (2 copies) | 800 WAV | 999 PNG, 30-second and 3-second feature CSVs |
| Test split (3 copies) | 200 WAV | 30-second test feature CSV |

All ZIP directory inventories were read. All five CSVs across the three canonical archives were decompressed and parsed, and one WAV per group was decompressed and inspected: mono, 22050 Hz, approximately 30 seconds. The archives were not fully extracted or exhaustively CRC-tested. No source code or nested ZIPs appeared in these inventories. Training and test audio filenames have no overlap; this does not establish artist-level or recording-level independence.

The raw CSV schema starts with filename and ends with the textual genre label. The Django dataset loader expects an extra leading index column and a trailing numeric class index. Raw CSVs therefore cannot directly replace the processed annotation file. The 3-second CSV still has 9990 rows in the training archive and should not be assumed to respect the 800/200 recording split.

Recordings remain local and are excluded from Git. Incomplete `.qkdownloading` files were not treated as valid archives.
