# Content-Based Music Recommendation System

English translation of the original project's description.

> This undergraduate graduation project was developed while learning neural networks, with references to learning materials and other projects. It is provided for study and discussion.
>
> Author's Bilibili profile: https://space.bilibili.com/383843542

## System design

The project combines audio preprocessing, neural-network genre classification, and a Django music recommendation interface.

## Data processing

The project uses GTZAN, with ten music genres and 100 thirty-second audio clips per genre. Processing includes cleaning labels and converting audio signals into spectral representations using torchaudio. Mel-frequency representations compress the signal and provide input features for the classifier.

## Neural network

The project uses an AlexNet-style convolutional network. Its relatively simple architecture provides a practical starting point for learning neural networks on a small audio dataset.

## Music recommendation

Django provides the web interface and backend interaction. Clicking the heart requests recommendations based on the selected track. The recommendation list displays the five highest-ranked songs.

The original demonstration address was `https://fishei.cn/project`.

## Setup

The original dataset download was shared at https://www.aliyundrive.com/s/dQG715hETzr .

The training notebook is [recommend.ipynb](recommend.ipynb), which produces `best_model_okk.pth`. Training can run locally on a GPU or in a notebook environment such as Kaggle.

The Django project is in [recommend/](recommend/). Place the GTZAN dataset under `recommend/music/static/GTZAN/` and configure the trained weights before starting the application. The original author planned to publish further deployment instructions on Bilibili.

## References

- Web player: https://github.com/Ezenlee/WebMusicPlayer
- Audio processing: https://www.youtube.com/watch?v=gp2wZqDoJ1Y&list=PL-wATfeyAMNoirN4idjev6aRu8ISZYVWm
