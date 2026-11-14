"""MFCC preprocessing shared by training and inference."""
import torch
import torchaudio
from .nn.net import AlexNet

SAMPLE_RATE = 22050
NUM_SAMPLES = SAMPLE_RATE * 5


def mfcc(path):
    signal, rate = torchaudio.load(str(path), backend='soundfile')
    signal = signal.mean(dim=0, keepdim=True)
    if rate != SAMPLE_RATE:
        signal = torchaudio.functional.resample(signal, rate, SAMPLE_RATE)
    signal = signal[:, :NUM_SAMPLES]
    signal = torch.nn.functional.pad(signal, (0, max(0, NUM_SAMPLES-signal.shape[-1])))
    return torchaudio.transforms.MFCC(sample_rate=SAMPLE_RATE, n_mfcc=128, log_mels=True)(signal)


class AudioPredictor:
    def __init__(self, checkpoint):
        self.model = AlexNet()
        self.model.load_state_dict(torch.load(str(checkpoint), map_location='cpu', weights_only=True))
        self.model.eval()

    def scores(self, path):
        with torch.inference_mode():
            return self.model(mfcc(path).unsqueeze(0)).softmax(dim=1)[0].tolist()
