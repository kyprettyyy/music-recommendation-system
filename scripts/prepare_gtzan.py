"""Safely extract GTZAN audio/CSV and convert raw labels for the legacy loader."""
import argparse
import csv
import shutil
import sys
import zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'recommend'))
from music.engine import GENRES


def prepare(archive, output):
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            name = item.filename.replace('\\', '/')
            if item.is_dir() or Path(name).suffix.lower() not in ('.wav', '.csv'):
                continue
            target = (root/name).resolve()
            if not target.is_relative_to(root) or item.file_size > 100_000_000:
                raise ValueError('Invalid archive member')
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(item) as source, target.open('xb') as dest:
                shutil.copyfileobj(source, dest)
    for raw in root.rglob('*30_sec*.csv'):
        if raw.stem.endswith('_final'):
            continue
        with raw.open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        output_csv = raw.with_name(raw.stem+'_final.csv')
        with output_csv.open('x', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['index', 'filename', 'label', 'label_id'])
            for i, row in enumerate(rows):
                writer.writerow([i, row['filename'], row['label'], GENRES.index(row['label'])])
        print(f'{output_csv}: {len(rows)} rows')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive')
    parser.add_argument('output')
    args = parser.parse_args()
    prepare(args.archive, args.output)
