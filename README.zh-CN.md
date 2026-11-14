# 多模态音乐推荐系统

Django + PyTorch 音乐推荐项目。现已补齐协同过滤、歌词 Word2Vec、音频风格分数融合，以及搜索、收藏、播放记录、注册登录和 Top-5 推荐页面。

本仓库保留原始音频分类代码和来源说明；混合推荐等功能是依据简历和实训报告在 **2026 年 11 月补充实现** 的，不能用于证明 2022 年已经完成这些功能。对应关系见 [简历与报告核对](docs/RESUME_MAPPING.md)。

## 快速运行

推荐 Python 3.11。Windows 可双击 `start-demo.cmd` 自动安装演示依赖并启动；首次运行需要网络。也可以在本目录依次执行：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-core.txt
python recommend/manage.py migrate
python recommend/manage.py seed_demo
python recommend/manage.py build_features --demo
python recommend/manage.py runserver
```

打开 http://127.0.0.1:8000/ 。先播放或收藏歌曲，再刷新推荐；支持歌名、作者、风格搜索和收藏列表。注册后偏好关联账号，访客偏好保留在当前浏览器会话；两者不会自动合并。演示初始化要求数据库曲库为空，重复构建特征可以直接运行最后两条命令。

演示包含 20 首原创短音调、虚构歌词和 12 位合成用户的行为。歌词向量通过实际训练 Word2Vec 生成；演示音频分数是合成的，并非神经网络预测。页面和接口均标注演示性质。演示用于验证流程，不代表真实歌曲或真实推荐效果。

## 真实数据与模型

[完整操作说明](docs/REAL_DATA.md)包含 ZIP 解压、标签转换、曲库与歌词导入、音频分数生成、训练和测试。原模型已成功完成真实音频推理；GTZAN 原始数据没有歌词和真实用户行为，缺失模态会自动退出融合，不会替真实歌曲编造歌词。

新推荐器结合用户协同过滤、歌词向量余弦相似度、音频风格向量相似度；默认权重为 0.4 / 0.3 / 0.3，可用模态自动重新归一化。排除听过或收藏过的曲目，冷启动使用热门度或显式风格；候选不足时返回少于五首。

## 验证情况

- 10 项自动化测试通过，Django 系统检查与迁移一致性检查通过。
- 旧权重已跑通 200 首测试音频；因训练来源和数据隔离无法追溯，这只是兼容性检查。
- 新训练脚本已完成 4 首真实音频的单轮训练流程检查，未进行完整重新训练。
- 已实际训练演示歌词 Word2Vec 并生成推荐特征。

运行测试：`python recommend/manage.py test music`。详见 [验证记录与限制](docs/VALIDATION.md)。

## 上传范围

源代码、说明和历史展示图片可在检查后上传。数据库、音频、权重、生成的特征和原始报告均未纳入 Git；不公开原报告中的其他成员及教师资料。项目来源见 [THIRD_PARTY.md](THIRD_PARTY.md)，原说明完整保留于 `README.original.md`，未擅自添加覆盖第三方内容的开源许可。
