# guide_content.py - 操作指南内容
# 独立维护，修改不会影响主程序

GUIDE_MARKDOWN = """
# 🎨 Animagine XL 3.1 完整操作指南

> 本指南基于官方文档整理，适用于 FaceOrbit 高级模式

---

## 📋 目录
1. [推荐参数设置](#一推荐参数设置)
2. [提示词标签系统](#二提示词标签系统)
3. [质量修饰符](#三质量修饰符)
4. [评级/年代/美学标签](#四评级年代美学标签)
5. [常用分类标签](#五常用分类标签)
6. [推荐负向提示词](#六推荐负向提示词)
7. [完整示例](#七完整示例)
8. [艺术家风格参考](#八艺术家风格参考)
9. [快速调参参考](#九快速调参参考)
10. [模型已知局限](#十模型已知局限)

---

## 一、推荐参数设置

| 参数 | 推荐值 | 说明 |
|:---|:---|:---|
| **采样器 (Sampler)** | `euler_ancestral` (Euler a) | 官方强烈推荐 |
| **采样步数 (Steps)** | `28 - 30` | **低于 30 步效果最好** |
| **CFG Scale** | `5 - 7` | 越低模型越自由，越高越遵循提示词 |
| **分辨率** | `832x1216` / `896x1152` | 竖版立绘推荐 |

### 支持的分辨率

| 尺寸 | 宽高比 | 适用场景 |
|:---|:---|:---|
| 1024 x 1024 | 1:1 方形 | 头像/图标 |
| 1152 x 896 | 9:7 | 半身立绘 |
| **832 x 1216** | **13:19** | **全身立绘（推荐）** |
| 1344 x 768 | 7:4 横向 | 场景/多人 |
| 1536 x 640 | 12:5 横向 | 宽幅场景 |

---

## 二、提示词标签系统

Animagine XL 3.1 使用 **Danbooru 风格标签**，而非自然语言。

### 📌 标签顺序模板（官方推荐）
质量标签, 角色数量, 角色名称, 作品来源, 服装, 动作, 表情, 场景, 风格, 年代标签

text

**示例**：
masterpiece, best quality, very aesthetic, 1girl, Hatsune Miku, vocaloid, long turquoise hair, school uniform, standing, singing, night concert, newest

text

---

## 三、质量修饰符

> 必须放在提示词开头，直接影响生成质量

| 标签 | 分数标准 | 使用建议 |
|:---|:---|:---|
| `masterpiece` | > 95% | 追求最高质量时使用 |
| `best quality` | 85% - 95% | **日常推荐** |
| `great quality` | 75% - 85% | 快速生成 |
| `good quality` | 50% - 75% | 测试时使用 |
| `normal quality` | 25% - 50% | 不推荐 |
| `low quality` | 10% - 25% | 避免使用 |
| `worst quality` | ≤ 10% | 避免使用 |

**官方推荐开场组合**：
masterpiece, best quality, very aesthetic, absurdres

text

---

## 四、评级/年代/美学标签

### 评级修饰符

| 标签 | 含义 | 说明 |
|:---|:---|:---|
| `safe` | 全年龄 | 一般内容 |
| `sensitive` | 敏感 | 轻度敏感内容 |
| `nsfw` | 成人 | 成人内容 |
| `explicit` | 明确 | 明确成人内容 |

### 年代修饰符（控制画风年代）

| 标签 | 年份范围 | 风格特点 |
|:---|:---|:---|
| `newest` | 2021 - 2024 | 现代动漫风格 |
| `recent` | 2018 - 2020 | 近期风格 |
| `mid` | 2015 - 2017 | 中期风格 |
| `early` | 2011 - 2014 | 早期风格 |
| `oldest` | 2005 - 2010 | 复古动漫风格 |

### 美学修饰符（视觉美感评分）

| 标签 | 分数范围 | 含义 |
|:---|:---|:---|
| `very aesthetic` | > 0.71 | 极具美感 |
| `aesthetic` | 0.45 - 0.71 | 有美感 |
| `displeasing` | 0.27 - 0.45 | 不美观 |
| `very displeasing` | ≤ 0.27 | 非常不美观 |

---

## 五、常用分类标签

### 👕 服装标签

| 标签 | 中文 | 标签 | 中文 |
|:---|:---|:---|:---|
| `school uniform` | 校服 | `kimono` | 和服 |
| `maid dress` | 女仆装 | `armor` | 盔甲 |
| `casual clothes` | 便服 | `suit` | 西装 |
| `yukata` | 浴衣 | `sailor uniform` | 水手服 |
| `sweater` | 毛衣 | `hoodie` | 连帽衫 |
| `apron` | 围裙 | `coat` | 外套 |

### 💇 发型标签

| 标签 | 中文 | 标签 | 中文 |
|:---|:---|:---|:---|
| `long hair` | 长发 | `short hair` | 短发 |
| `ponytail` | 马尾 | `twin tails` | 双马尾 |
| `drill hair` | 钻头卷发 | `braid` | 辫子 |
| `blonde` | 金发 | `black hair` | 黑发 |
| `brown hair` | 棕发 | `white hair` | 白发 |
| `blue hair` | 蓝发 | `pink hair` | 粉发 |

### 😊 表情标签

| 标签 | 中文 | 标签 | 中文 |
|:---|:---|:---|:---|
| `smile` | 微笑 | `sad` | 悲伤 |
| `angry` | 愤怒 | `blush` | 脸红 |
| `tears` | 流泪 | `serious` | 严肃 |
| `surprised` | 惊讶 | `embarrassed` | 尴尬 |
| `happy` | 开心 | `evil smile` | 邪笑 |

### 🎬 动作/姿势标签

| 标签 | 中文 | 标签 | 中文 |
|:---|:---|:---|:---|
| `standing` | 站立 | `sitting` | 坐姿 |
| `lying down` | 躺卧 | `action pose` | 动作姿势 |
| `looking at viewer` | 看着观众 | `looking away` | 看向别处 |
| `fighting pose` | 战斗姿势 | `crossed arms` | 交叉手臂 |
| `hand on hip` | 叉腰 | `running` | 奔跑 |

### 🌲 背景/场景标签

| 标签 | 中文 | 标签 | 中文 |
|:---|:---|:---|:---|
| `plain background` | 纯色背景 | `cityscape` | 城市风景 |
| `nature` | 自然风景 | `night` | 夜晚 |
| `classroom` | 教室 | `battlefield` | 战场 |
| `outdoors` | 户外 | `indoors` | 室内 |
| `forest` | 森林 | `beach` | 海滩 |
| `space` | 太空 | `abstract` | 抽象 |

---

## 六、推荐负向提示词

官方建议使用以下负向提示词来引导模型生成高质量图像：
nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, ugly, deformed, grayscale, dull, washed out, desaturated, low contrast

text

**快速版**（如果觉得太长）：
nsfw, lowres, worst quality, low quality, blurry, ugly, deformed, watermark

text

---

## 七、完整示例

### 示例1：火影忍者 - 漩涡鸣人

**正向提示词**：
masterpiece, best quality, very aesthetic, 1boy, Naruto Uzumaki, naruto, blonde spiky hair, blue eyes, whisker marks, orange jumpsuit, ninja headband, shuriken, confident smile, action pose, konoha village background, newest

text

### 示例2：鬼灭之刃 - 灶门祢豆子

**正向提示词**：
masterpiece, best quality, very aesthetic, 1girl, Kamado Nezuko, demon slayer, long black hair, pink ribbon, bamboo mouthpiece, pink kimono, demon form, cute expression, forest, newest

text

### 示例3：新海诚风格（原创角色）

**正向提示词**：
masterpiece, best quality, very aesthetic, 1girl, shinkai style, makoto shinkai, your name style, realistic background, clouds, sunset, beautiful sky, emotional, detailed, recent

text

### 示例4：原创角色 - 剑士女孩

**正向提示词**：
masterpiece, best quality, very aesthetic, 1girl, solo, fantasy, long brown hair, green eyes, leather armor, cloak, sword, standing on cliff, sunset sky, wind blowing hair, epic, detailed, newest

text

---

## 八、艺术家风格参考

Animagine XL 3.1 支持识别特定艺术家的风格，在提示词中加入艺术家名字即可：

| 艺术家 | 风格特点 |
|:---|:---|
| `Takashi Takeuchi` | Type-Moon / Fate 风格 |
| `Kantoku` | 柔和、细腻、治愈系 |
| `Mika Pikazo` | 鲜艳、多彩、活力 |
| `Suzuhito Yasuda` | 轻小说插画风格 |
| `Kouhaku Kuroboshi` | 幻想、细腻 |
| `lack` | 柔美、透明感 |
| `redjuice` | 科幻/未来感 |
| `huke` | 厚涂、黑暗风格 |

> 💡 使用方式：直接添加到提示词末尾，如 `, Takashi Takeuchi style`

---

## 九、快速调参参考

| 目标 | 参数调整 |
|:---|:---|
| **更像上传照片** | ↑ `ip_weight` (0.85-0.95) <br> ↓ `denoise` (0.65-0.7) |
| **更自由发挥** | ↓ `ip_weight` (0.7-0.8) <br> ↑ `denoise` (0.75-0.8) |
| **更遵循角度提示词** | ↑ `cn_strength` (0.45-0.6) |
| **更鲜艳色彩** | ↑ `correction_strength` (0.7-0.8) |
| **提高清晰度** | ↑ `steps` (35-40) <br> 使用 `euler_ancestral` |

### 参数范围速查

| 参数 | 最小值 | 推荐值 | 最大值 |
|:---|:---|:---|:---|
| 相似度 (ip_weight) | 0.5 | 0.8 | 1.0 |
| 姿态控制 (cn_strength) | 0.0 | 0.35 | 0.8 |
| 创意度 (denoise) | 0.5 | 0.7 | 0.9 |
| 提示词引导 (cfg) | 1.0 | 6.5 | 10.0 |
| 采样步数 (steps) | 20 | 28 | 50 |
| 色彩校正 | 0.0 | 0.65 | 1.0 |

---

## 十、模型已知局限

1. **仅限动漫风格**：不适合生成真实照片
2. **需要详细提示词**：简短提示词效果不佳
3. **标签格式**：使用 Danbooru 标签而非自然语言
4. **手部渲染**：虽已改进，但偶尔仍有瑕疵
5. **NSFW 内容**：可能生成未提示的成人内容
6. **数据集限制**：约 87 万张图像训练，某些角色可能不准确

---

## 十一、提示词快速参考卡

**格式**：`[质量] + [数量] + [角色] + [作品] + [服装] + [动作] + [场景]`

- **质量**：masterpiece, best quality, very aesthetic
- **数量**：1girl, 1boy, 2girls, solo
- **服装**：school uniform, kimono, armor, casual clothes
- **动作**：standing, sitting, action pose, looking at viewer
- **场景**：plain background, cityscape, nature, night
- **年代**：newest, recent, mid, early, oldest
- **评级**：safe, sensitive, nsfw

---

> 📚 **更多资源**
> - 官方模型页: https://huggingface.co/cagliostrolab/animagine-xl-3.1
> - Danbooru 标签库: https://danbooru.donmai.us/tags
> 
> *指南版本: v1.0 | 更新日期: 2025-01*
"""

# 可供主程序导入的变量
__all__ = ['GUIDE_MARKDOWN']