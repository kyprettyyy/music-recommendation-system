"""Reproducible MFCC/AlexNet training and held-out evaluation."""
import argparse
import csv
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'recommend'))
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from music.audio import mfcc
from music.engine import GENRES
from music.nn.net import AlexNet


class Catalog(Dataset):
    def __init__(self, annotations, root):
        with open(annotations, encoding='utf-8-sig', newline='') as f:
            self.rows = list(csv.DictReader(f))
        self.root = Path(root).resolve()

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        r = self.rows[index]
        path = (self.root/r['label']/r['filename']).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError('Audio path outside root')
        return mfcc(path), GENRES.index(r['label'])


def evaluate(model, loader, device):
    model.eval()
    correct = count = 0
    loss_sum = 0.
    with torch.inference_mode():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            prediction = model(x)
            loss_sum += torch.nn.functional.cross_entropy(prediction, y, reduction='sum').item()
            correct += (prediction.argmax(1) == y).sum().item()
            count += len(y)
    return {'count': count, 'accuracy': correct/count, 'loss': loss_sum/count}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['train', 'evaluate'])
    p.add_argument('--annotations', required=True)
    p.add_argument('--audio-root', required=True)
    p.add_argument('--checkpoint', default='artifacts/alexnet.pth')
    p.add_argument('--epochs', type=int, default=20)
    p.add_argument('--batch-size', type=int, default=16)
    p.add_argument('--lr', type=float, default=.0001)
    p.add_argument('--device', default='cpu')
    p.add_argument('--report', default='artifacts/audio_metrics.json')
    args = p.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.lr <= 0:
        p.error('epochs, batch-size and lr must be positive')
    torch.manual_seed(42)
    dataset = Catalog(args.annotations, args.audio_root)
    if not len(dataset):
        p.error('Empty annotations')
    model = AlexNet().to(args.device)
    checkpoint = Path(args.checkpoint)
    if args.mode == 'evaluate':
        model.load_state_dict(torch.load(checkpoint, map_location=args.device, weights_only=True))
        result = evaluate(model, DataLoader(dataset, batch_size=args.batch_size), args.device)
    else:
        if len(dataset) < 2:
            p.error('Need at least two training recordings')
        nval = max(1, len(dataset)//10)
        train, val = random_split(dataset, [len(dataset)-nval, nval], generator=torch.Generator().manual_seed(42))
        optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
        best = float('inf')
        history = []
        for epoch in range(args.epochs):
            model.train()
            for x, y in DataLoader(train, batch_size=args.batch_size, shuffle=True):
                optimizer.zero_grad()
                loss = torch.nn.functional.cross_entropy(model(x.to(args.device)), y.to(args.device))
                loss.backward()
                optimizer.step()
            metrics = evaluate(model, DataLoader(val, batch_size=args.batch_size), args.device)
            history.append({'epoch': epoch+1, **metrics})
            print(history[-1])
            if metrics['loss'] < best:
                best = metrics['loss']
                checkpoint.parent.mkdir(parents=True, exist_ok=True)
                torch.save(model.state_dict(), checkpoint)
        result = {'validation_history': history, 'train_count': len(train), 'validation_count': nval,
                  'note': 'Validation drawn only from training CSV. Evaluate held-out test CSV separately.'}
    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
