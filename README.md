# FaceOrbit - AI形象生成器

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 上传一张照片，AI 帮你生成多角度形象或多风格艺术照。开源、免费、本地运行。

## ✨ 功能特性

### 📐 多角度生成（6个角度）
| 模式 | 说明 | 输出 |
|------|------|------|
| **写真模式** | 真实感人像，保留原片质感 | 6张（正面/背面/侧面/四分之三/右前/顶视） |
| **二次元模式** | 日系动漫风格，30+预设角色 | 6张（同上） |

### 🎨 多画风迁移（单张输出）
| 模式 | 说明 | 输出 |
|------|------|------|
| **真实感画风** | 摄影/电影质感，10种预设画风 | 1张 |
| **2.5D画风** | 赛博朋克/水彩/魔法，10种预设画风 | 1张 |

### 🚀 核心能力
- **InstantID 集成**：保留你的面部特征，实现身份迁移
- **双模式设计**：体验模式（预设画风）+ 高级模式（自定义参数）
- **模板管理**：保存/加载参数组合，一键复用
- **自动拼图**：多角度模式自动合成6格拼图
- **内置操作指南**：完整的参数与提示词中文说明

## 🖼️ 效果展示

### 多角度模式 - 6个角度生成
| 正面 | 背面 | 侧面 | 四分之三 | 右前 | 顶视 |
|------|------|------|----------|------|------|
| ![front](docs/images/front_sample.jpg) | ![back](docs/images/back_sample.jpg) | ![side](docs/images/side_sample.jpg) | ![threequarter](docs/images/threequarter_sample.jpg) | ![rightfront](docs/images/rightfront_sample.jpg) | ![top](docs/images/top_sample.jpg) |

### 多画风模式 - 画风迁移
| 赛博朋克 | 水彩 | 魔法 | 电影质感 |
|----------|------|------|----------|
| ![cyberpunk](docs/images/cyberpunk_sample.jpg) | ![watercolor](docs/images/watercolor_sample.jpg) | ![magic](docs/images/magic_sample.jpg) | ![cinema](docs/images/cinema_sample.jpg) |

## 🚀 快速开始

### 环境要求

- Python 3.10+
- ComfyUI（已安装 InstantID 插件）
- 8GB+ 显存 GPU（推荐）

### 安装

```bash
git clone https://github.com/deejoseph/FaceOrbit.git
cd FaceOrbit
pip install gradio requests pillow
运行
bash
# 启动启动器（推荐）
python launcher.py

# 或直接启动任意模式
python portrait.py    # 写真模式 :7861
python anime.py       # 二次元模式:7862
python realistic.py   # 真实感画风:7864
python scifi.py       # 2.5D画风:7865
浏览器将自动打开 http://127.0.0.1:7860

📁 项目结构
text
FaceOrbit/
├── launcher.py                 # 启动器（四模式入口）
├── portrait.py                 # 写真模式（多角度）
├── anime.py                    # 二次元模式（多角度）
├── realistic.py                # 真实感画风（多画风）
├── scifi.py                    # 2.5D画风（多画风）
├── guide_content.py            # 操作指南（共用）
├── character_presets.py        # 预设角色库
├── workflows/
│   ├── portrait_6angles.json
│   ├── anime_6angles.json
│   ├── realistic_style.json
│   └── scifi_style.json
├── temp/                       # 临时文件
└── output/                     # 生成图片输出
    └── jobs/                   # 按时间归档
🎮 预设画风（10种）
真实感画风模式
画风	描述
霓虹灯的夜晚	都市氛围，光影交错
职场女精英	干练优雅，自然光
赛博女战士	科幻装甲，红色元素
城市的傍晚	夕阳余晖下的女性
狼灵少女	神秘气质，野性之美
地下城幻境	发光蘑菇下的探险者
路边的咖啡屋	时尚街拍，电影质感
哥特美学	暗黑优雅，艺术感人像
窗边	赛博公寓，雨夜霓虹
家居	古典奢华，静谧午后
2.5D画风模式
画风	描述
经典镜头-仿攻壳机动队	机械义体，赛博朋克
水彩少女	清新淡雅，色彩柔和
义体改造	科技感十足
冬日暖阳	温馨氛围
春天花会开	浪漫唯美
一家老的CD店	文艺气息
旗袍夜色	东方韵味
魔法师	奇幻色彩
弹吉他	动感活力
水彩重金属	独特混搭
⚙️ 参数说明
多角度模式推荐参数
参数	写真模式	二次元模式
相似度	0.92	0.8
姿态控制	0.5	0.35
创意度	0.73	0.7
提示词引导	3.0	6.5
采样步数	30	28
多画风模式推荐参数
参数	真实感画风	2.5D画风
相似度	0.92	0.85
姿态控制	0.5	0.45
创意度	0.73	0.6
提示词引导	3.0	6.5
采样步数	30	28
📄 许可证
MIT

🙏 致谢
ComfyUI

InstantID

Animagine XL 3.1

RealVisXL

GhostXL