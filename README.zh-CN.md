# 多模态音乐推荐系统

基于 Django 和 PyTorch 的音乐推荐系统，结合听歌行为、歌词语义和音频风格生成个性化推荐。支持曲库搜索、收藏、播放记录和 Top-5 推荐。

## 主要功能

- 用户注册、登录与收藏管理。
- 按歌名、作者和风格搜索歌曲。
- 根据播放和收藏记录进行用户协同过滤。
- 使用 Word2Vec 歌词向量计算语义相似度。
- 使用 MFCC 和 AlexNet 提取音频风格特征。
- 融合多路分数，并展示推荐结果的评分组成。

## 推荐流程

协同过滤、歌词相似度、音频相似度的默认权重分别为 0.4、0.3、0.3。某类特征缺失时，系统对其余权重重新归一化；推荐列表排除已消费歌曲，新用户可以通过热门度或指定风格获得推荐。

音频统一为 22050 Hz 单声道，裁剪或补齐至 5 秒，提取 128 维 MFCC，送入 AlexNet 风格网络得到十类音乐风格分数。歌词使用 skip-gram Word2Vec 生成 32 维向量。

## 快速启动

使用 Python 3.11。Windows 可运行 `start-demo.cmd`，也可以执行：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-core.txt
python recommend/manage.py migrate
python recommend/manage.py seed_demo
python recommend/manage.py build_features --demo
python recommend/manage.py runserver
```

打开 `http://127.0.0.1:8000/`，播放或收藏歌曲后刷新推荐。

演示曲库使用生成的短音调、虚构歌词和示例用户行为。演示音频分数为合成数据，歌词向量由 Word2Vec 训练生成。接入真实音频时，安装 `requirements.txt` 并按 [数据与训练说明](docs/REAL_DATA.md) 配置曲库和模型。

## 目录结构

```text
recommend/music/engine.py      混合推荐评分
recommend/music/audio.py       MFCC 提取与音频推理
recommend/music/nn/            AlexNet 与数据集加载
recommend/music/management/    曲库导入和特征生成
recommend/music/templates/     页面模板
scripts/                       数据处理与模型训练
```

运行测试：`python recommend/manage.py test music`。

[English](README.md) · [架构](docs/ARCHITECTURE.md) · [数据与训练](docs/REAL_DATA.md) · [致谢](THIRD_PARTY.md)
