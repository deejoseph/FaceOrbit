# FaceOrbit - AI动漫形象生成器

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 上传照片，生成属于你的动漫角色形象。支持 4 种风格模式、6 个角度、30+ 预设角色。

## ✨ 功能特性

### 🎮 四种形象生成模式

| 模式 | 描述 | 端口 |
|------|------|------|
| 📸 **写真模式** | 真实感人像，适合证件照/职业照 | 7861 |
| 🎨 **二次元模式** | 日系动漫风格，30+ 预设角色 | 7862 |
| ✨ **立体感动漫** | 2.5D 游戏CG风格 | 7863 |
| 🎬 **影视明星** | 电影质感，好莱坞级光影 | 7864 |

### 🚀 核心功能

- **6 角度生成**：正面、背面、侧面、四分之三、右前、顶视
- **InstantID 集成**：保留你的面部特征
- **内置操作指南**：完整的参数与提示词中文说明
- **模板管理**：保存/加载参数组合
- **自动拼图**：6张图自动合成对比图

## 🚀 快速开始

### 环境要求

- Python 3.10+
- ComfyUI（已安装 InstantID 插件）
- 8GB+ 显存 GPU

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
python ghostmix.py    # 立体感动漫:7863
python cinema.py      # 影视明星模式:7864
📁 项目结构
text
FaceOrbit/
├── launcher.py                 # 启动器（四模式入口）
├── portrait.py                 # 写真模式
├── anime.py                    # 二次元模式
├── ghostmix.py                 # 立体感动漫模式
├── cinema.py                   # 影视明星模式
├── guide_content.py            # 操作指南（共用）
├── character_presets.py        # 预设角色库
├── workflows/
│   ├── portrait_6angles.json
│   ├── anime_6angles.json
│   ├── ghostmix_6angles.json
│   └── cinema_6angles.json
├── temp/                       # 临时文件
└── output/                     # 生成图片输出
    └── jobs/                   # 按时间归档
⚙️ 参数说明
参数	说明	推荐范围
相似度	与上传照片的相似程度	0.7-0.95
姿态控制	控制姿势的精确度	0.2-0.6
创意度	模型自由发挥程度	0.65-0.8
提示词引导	提示词的影响力	2.5-7
采样步数	生成质量	28-35
色彩校正	画面鲜艳程度	0.5-0.7
📄 许可证
MIT

🙏 致谢
ComfyUI

InstantID

Animagine XL 3.1