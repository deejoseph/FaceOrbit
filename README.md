# FaceOrbit - AI动漫形象生成器

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 上传照片，生成属于你的动漫角色形象。支持 6 个角度、30+ 预设角色、自定义提示词。

## ✨ 功能特性

- **双模式设计**
  - 🎮 体验模式：30+ 预设角色一键生成（火影、海贼、鬼灭、原神、初音未来等）
  - ⚙️ 高级模式：自定义提示词，精细控制每个角度

- **6 角度生成**：正面、背面、侧面、四分之三、右前、顶视

- **InstantID 集成**：保留你的面部特征，实现身份迁移

- **内置操作指南**：完整的参数与提示词中文说明

- **模板管理**：保存/加载参数组合，一键复用

- **图片管理**：自动生成拼图，规范文件夹结构

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
python anime_6angles.py
浏览器将自动打开 http://127.0.0.1:7860

📁 项目结构
text
FaceOrbit/
├── anime_6angles.py           # 主程序
├── guide_content.py           # 操作指南内容
├── character_presets.py       # 预设角色库（30+角色）
├── workflows/
│   └── anime_6angles.json     # ComfyUI 工作流
├── temp/                      # 临时文件
└── output/                    # 生成图片输出
    └── jobs/                  # 按时间归档
🎮 预设角色示例
作品	角色
火影忍者	鸣人、佐助、春野樱、日向雏田
海贼王	路飞、索隆
鬼灭之刃	炭治郎、祢豆子、蝴蝶忍
原神	胡桃、刻晴、纳西妲
VOCALOID	初音未来
BanG Dream	高松灯、千早爱音
孤独摇滚	后藤一里
间谍过家家	约尔、安妮亚
⚙️ 参数说明
参数	说明	推荐范围
相似度	与上传照片的相似程度	0.7-0.9
姿态控制	控制姿势的精确度	0.2-0.5
创意度	模型自由发挥程度	0.65-0.8
提示词引导	提示词的影响力	5-7
采样步数	生成质量	28-35
色彩校正	画面鲜艳程度	0.5-0.7
📄 许可证
MIT

🙏 致谢
ComfyUI

InstantID

Animagine XL 3.1