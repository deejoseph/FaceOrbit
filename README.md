# FaceOrbit - AI 形象生成工作流套件

基于 ComfyUI 的多风格、多角度 AI 人像生成工作流。

## ✨ 特性

- **4 种风格**：写真、二次元、立体感动漫、影视明星
- **6 个角度**：正面、背面、侧面、四分之三、右前、顶视
- **身份保留**：基于 InstantID，保持人物特征
- **色彩校正**：内置 VAE 色彩修正，解决灰蒙蒙问题
- **一键切换**：工作流文件即拖即用

## 📥 安装

### 前置要求

- ComfyUI 已安装
- 8GB+ 显存 GPU（推荐）

### 依赖插件

| 插件 | 说明 |
|------|------|
| ComfyUI-InstantID | 人脸特征提取 |
| ComfyUI-EasyColorCorrector | 色彩校正 |
| ComfyUI-Manager | 插件管理（可选） |

### 模型下载

将以下模型放入 `ComfyUI/models/` 对应目录：

| 模型 | 路径 | 用途 |
|------|------|------|
| `realvisxlV50_v50LightningBakedvae.safetensors` | `checkpoints/` | 写真 |
| `animagine-xl-3.1.safetensors` | `checkpoints/` | 二次元 |
| `GhostMix-V2.0-fp16-BakedVAE.safetensors` | `checkpoints/` | 立体感动漫 |
| `RealVisXL_V5.0_fp16.safetensors` | `checkpoints/` | 影视明星 |
| `ip-adapter.bin` | `instantid/` | InstantID 核心 |
| `diffusion_pytorch_model.safetensors` | `controlnet/` | InstantID ControlNet |
| `sdxl_vae.safetensors` | `vae/` | VAE 解码 |
| `qwen-image-edit-2511-multiple-angles-lora.safetensors` | `loras/` | 多角度 LoRA |

> antelopev2 模型放入 `insightface/models/antelopev2/`

## 🚀 使用方法

1. 下载对应风格的工作流 JSON 文件
2. 拖入 ComfyUI 界面
3. 修改 `LoadImage` 节点中的图片路径为您的照片
4. 点击 `Queue Prompt` 生成

### 工作流文件

| 文件 | 风格 |
|------|------|
| `portrait_6angles.json` | 写真 |
| `anime_6angles.json` | 二次元 |
| `ghostmix_6angles.json` | 立体感动漫 |
| `cinema_6angles.json` | 影视明星 |

## ⚙️ 参数说明

| 参数 | 说明 | 推荐范围 |
|------|------|---------|
| `ip_weight` | 身份相似度 | 0.7-0.95 |
| `cn_strength` | 姿态控制强度 | 0.2-0.6 |
| `denoise` | 重绘幅度 | 0.65-0.8 |
| `cfg` | 提示词引导强度 | 2.5-6.5 |
| `correction_strength` | 色彩校正强度 | 0.4-0.7 |

## 📊 各风格推荐参数

| 风格 | ip_weight | cn_strength | denoise | cfg |
|------|-----------|-------------|---------|-----|
| 写真 | 0.92 | 0.5 | 0.73 | 3.0 |
| 二次元 | 0.8 | 0.35 | 0.7 | 6.5 |
| 立体感动漫 | 0.88 | 0.45 | 0.7 | 2.8 |
| 影视明星 | 0.9 | 0.5 | 0.72 | 2.6 |

## 🖼️ 示例效果

> （待补充效果图）

## ⚠️ 注意事项

- 8GB 显存建议分批运行，每次只生成一个角度
- 使用前确保所有依赖模型已正确下载并放置
- 顶视角度可能需要手动调整为仰视

## 📝 更新日志

### v1.0.0 (2025-01-XX)
- 初始版本发布
- 支持 4 种风格 × 6 个角度
- 集成 InstantID 身份保留
- 集成 VAE 色彩校正

## 📄 许可证

MIT

## 🙏 致谢

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [InstantID](https://github.com/InstantID/InstantID)
- [ComfyUI-EasyColorCorrector](https://github.com/regiellis/ComfyUI-EasyColorCorrector)