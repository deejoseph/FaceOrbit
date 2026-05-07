#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaceOrbit - 2.5D多画风模式
赛博朋克/攻壳机动队/水彩/魔法等多种画风，保留照片面部特征
专注画风迁移，单张输出
"""

import gradio as gr
import json
import os
import uuid
import webbrowser
import threading
import requests
import time
from datetime import datetime
from PIL import Image
import io
import shutil

# ==================== 配置 ====================
WORKFLOW_PATH = "workflows/scifi_style.json"
TEMPLATES_DIR = "user_templates_25d"
TEMP_DIR = "temp"
OUTPUT_DIR = "output"
COMFYUI_API = "http://127.0.0.1:8188"
MODEL_OPTIONS = {
    "GhostXL V1.0": "ghostxl_v10BakedVAE.safetensors"
}

# 创建必要的文件夹
for dir_name in [TEMPLATES_DIR, TEMP_DIR, OUTPUT_DIR]:
    os.makedirs(dir_name, exist_ok=True)

# ==================== 负向提示词 ====================
DEFAULT_NEGATIVE = "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, ugly, deformed, grayscale, dull, washed out, desaturated, low contrast"

# ==================== 预设画风库 ====================
PRESET_STYLES = {
    "经典镜头 - 仿攻壳机动队": {
        "prompt": "masterpiece, best quality, 1girl, mechanical girl, detailed face, shadows, 8k, ultra sharp, metal, intricate, ornaments detailed, cold colors, highly intricate details, rendering on cgsociety, facing camera, mechanical limbs, killing machine, ghost in the shell, anime art style",
        "description": "致敬《攻壳机动队》，机械义体、赛博朋克风格",
        "gender": "female"
    },
    "水彩少女": {
        "prompt": "masterpiece, top quality, best quality, official art, beautiful and aesthetic:1.2, 1girl, upper body:1.3, extreme detailed, abstract art:1.2, colorful, highest detailed, blue and green, watercolor painting",
        "description": "水彩风格，清新淡雅，色彩柔和",
        "gender": "female"
    },
    "义体改造": {
        "prompt": "masterpiece, best quality, 1girl, mechanical girl, realistic anime style, ultra realistic details, shadows, octane render, 8k, ultra sharp, metal, intricate, cold colors, highly intricate details, realistic light, neon details, mechanical limbs, wires and cables connecting to head",
        "description": "机械义体改造，科技感十足",
        "gender": "female"
    },
    "冬日暖阳": {
        "prompt": "masterpiece, best quality, 1girl, realistic anime style, upper body, looking at viewer, winter coat, snow, warm sun, blurry background, professional photography, highly detailed, 8k",
        "description": "冬日暖阳，温馨氛围",
        "gender": "female"
    },
    "春天花会开": {
        "prompt": "masterpiece, best quality, 1girl, realistic anime style, a girl with blonde hair sitting on the grass, surrounded by flowers, flying petals, cloudy sky, depth of field, dappled sunlight, lens flare, wide shot, photography",
        "description": "春日花海，浪漫唯美",
        "gender": "female"
    },
    "一家老的CD店": {
        "prompt": "masterpiece, best quality, 1girl, realistic, in an old record store, standing before vinyl albums, soft lighting, slow flow of music, lonely yet elegant, mysterious, vintage atmosphere, detailed, 8k",
        "description": "怀旧CD店，文艺气息",
        "gender": "female"
    },
    "旗袍夜色": {
        "prompt": "masterpiece, best quality, 1girl, realistic, cheongsam, walking alone on cobblestone path, dimly lit street, deep eyes, streetlights, dappled shadows, nostalgic, ambiguous atmosphere, light steps, 8k",
        "description": "旗袍夜色，东方韵味",
        "gender": "female"
    },
    "魔法师": {
        "prompt": "masterpiece, top quality, best quality, official art, beautiful and aesthetic:1.2, 1girl, red hair, dark skinned, priest, magic, temple, holy magic, mystical haze, magical timestream, powerful magic, cataclysmic spell, colorful, 8k",
        "description": "魔法师，奇幻色彩",
        "gender": "female"
    },
    "弹吉他": {
        "prompt": "masterpiece, best quality, 1girl, long red hair, blue eyes, on the stage, dim light, guitar, wings, sunglasses, HDR, UHD, 8K, Highly detailed, Studio lighting, ultra-fine painting, Professional",
        "description": "摇滚少女，动感活力",
        "gender": "female"
    },
    "水彩重金属": {
        "prompt": "masterpiece, best quality, watercolor artwork, a stunning watercolor painting on canvas, white background, simple watercolor, artistic watercolor, steampunk, toned body, artificial intelligence city, highly detailed",
        "description": "水彩+重金属，独特混搭",
        "gender": "female"
    }
}

# ==================== 辅助函数：构建自定义提示词 ====================
def build_custom_prompt(gender, identity, scene, props, action, extra_details):
    """根据用户选择构建自定义提示词"""
    prompt_parts = ["masterpiece, best quality"]
    
    if gender == "女孩":
        prompt_parts.append("1girl")
    elif gender == "男孩":
        prompt_parts.append("1boy")
    
    if identity and identity != "无":
        prompt_parts.append(identity)
    if scene and scene != "无":
        prompt_parts.append(scene)
    if props and props != "无":
        prompt_parts.append(props)
    if action and action != "无":
        prompt_parts.append(action)
    if extra_details:
        prompt_parts.append(extra_details)
    
    prompt_parts.append("8k, ultra sharp, highly detailed, best quality")
    return ", ".join(prompt_parts)

# ==================== 辅助函数 ====================
def list_templates():
    templates = [f.replace('.json', '') for f in os.listdir(TEMPLATES_DIR) if f.endswith('.json')]
    return templates

def save_template(name, params):
    if not name:
        return "❌ 请输入模板名称", gr.Dropdown(choices=list_templates())
    filepath = os.path.join(TEMPLATES_DIR, f"{name}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({"name": name, "params": params, "created_at": datetime.now().isoformat()}, f, indent=2)
    return f"✅ 模板「{name}」已保存", gr.Dropdown(choices=list_templates())

def load_template(name):
    filepath = os.path.join(TEMPLATES_DIR, f"{name}.json")
    if not os.path.exists(filepath):
        return None, f"❌ 模板「{name}」不存在"
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["params"], f"✅ 已加载模板「{name}」"

def delete_template(name):
    filepath = os.path.join(TEMPLATES_DIR, f"{name}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
    return f"✅ 已删除模板「{name}」", gr.Dropdown(choices=list_templates())

def save_image_to_project(image, prefix="scifi", style_name=""):
    """保存单张图片到规范的文件夹结构"""
    if image is None:
        return None, ""
    
    job_folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_dir = os.path.join(OUTPUT_DIR, "jobs", job_folder_name)
    single_dir = os.path.join(job_dir, "single")
    os.makedirs(single_dir, exist_ok=True)
    
    # 清理文件名中的特殊字符
    safe_style_name = "".join(c for c in style_name if c.isalnum() or c in "._- ").strip()
    filename = f"{prefix}_{job_folder_name}_{safe_style_name}.png" if safe_style_name else f"{prefix}_{job_folder_name}.png"
    filepath = os.path.join(single_dir, filename)
    image.save(filepath)
    print(f"💾 已保存: {filepath}")
    
    return filepath, job_dir

# ==================== ComfyUI API 调用 ====================
def run_comfyui_workflow(workflow, progress):
    """发送工作流到 ComfyUI 并获取图片（单张）"""
    
    progress(0.7, desc="发送到 ComfyUI...")
    
    debug_path = os.path.join(TEMP_DIR, f"25d_api_send_{int(time.time())}.json")
    with open(debug_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)
    print(f"📤 已保存发送到 API 的工作流: {debug_path}")
    
    try:
        response = requests.post(f"{COMFYUI_API}/prompt", json={"prompt": workflow}, timeout=60)
        if response.status_code != 200:
            return None, f"❌ API 错误: {response.text}"
        
        data = response.json()
        prompt_id = data.get("prompt_id")
        if not prompt_id:
            return None, "❌ 未获取到 prompt_id"
        
        print(f"✅ 工作流已提交，prompt_id: {prompt_id}")
        progress(0.8, desc=f"生成中... (ID: {prompt_id[:8]})")
        
        elapsed = 0
        while True:
            try:
                resp = requests.get(f"{COMFYUI_API}/history/{prompt_id}", timeout=10)
                if resp.status_code == 200:
                    history = resp.json()
                    if prompt_id in history:
                        outputs = history[prompt_id].get("outputs", {})
                        print(f"📦 找到输出节点: {list(outputs.keys())}")
                        
                        # 查找 SaveImage 节点的输出（通常是 15）
                        for node_id, node_output in outputs.items():
                            if "images" in node_output and node_output["images"]:
                                img_info = node_output["images"][0]
                                img_response = requests.get(
                                    f"{COMFYUI_API}/view",
                                    params={"filename": img_info["filename"], "subfolder": img_info.get("subfolder", "")}
                                )
                                if img_response.status_code == 200:
                                    img = Image.open(io.BytesIO(img_response.content))
                                    print(f"🖼️ 获取图片成功")
                                    return img, f"✅ 生成完成！耗时 {elapsed} 秒"
            except Exception as e:
                print(f"查询时出错: {e}")
            
            elapsed += 2
            minutes = elapsed // 60
            seconds = elapsed % 60
            progress(0.8, desc=f"生成中... 已等待 {minutes}分{seconds}秒")
            time.sleep(2)
        
    except Exception as e:
        return None, f"❌ 运行失败: {str(e)}"

# ==================== 核心生成函数 ====================
def generate_images(
    input_image,
    model_name,
    mode,
    selected_style,
    custom_prompt,
    negative_prompt,
    ip_weight,
    cn_strength,
    denoise,
    cfg,
    steps,
    correction_strength,
    width,
    height,
    use_fixed_seed,
    fixed_seed_value,
    progress=gr.Progress()
):
    if input_image is None:
        return None, "❌ 请先上传头像照片"
    
    is_preset_mode = (mode == "🎨 预设画风模式")
    
    style_name = ""
    if is_preset_mode and selected_style and selected_style != "无（使用自定义提示词）":
        style_data = PRESET_STYLES.get(selected_style, {})
        prompt_text = style_data.get("prompt", "")
        style_name = selected_style
        gender_hint = style_data.get("gender", "female")
        
        print(f"🎨 预设画风模式 - 使用画风: {selected_style}")
        
        # 女性角色提示
        if gender_hint == "female":
            print("💡 提示：预设画风为女性角色，男性用户请使用高级模式")
    else:
        prompt_text = custom_prompt
        style_name = "自定义"
        print(f"⚙️ 高级模式 - 使用自定义提示词")
    
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    # 保存上传的图片
    comfyui_input_dir = "D:/PixelSmile/ComfyUI-aki/ComfyUI-aki-v3/ComfyUI/input"
    os.makedirs(comfyui_input_dir, exist_ok=True)
    
    original_filename = os.path.basename(input_image)
    local_image_path = os.path.join(comfyui_input_dir, f"faceorbit_{uuid.uuid4().hex}_{original_filename}")
    shutil.copy2(input_image, local_image_path)
    print(f"📸 图片已复制到 ComfyUI input: {local_image_path}")
    
    # 修改工作流参数
    workflow["3"]["inputs"]["image"] = local_image_path
    workflow["1"]["inputs"]["ckpt_name"] = MODEL_OPTIONS.get(model_name, "ghostxl_v10BakedVAE.safetensors")
    workflow["7"]["inputs"]["text"] = prompt_text
    workflow["8"]["inputs"]["text"] = negative_prompt
    
    if use_fixed_seed:
        workflow["11"]["inputs"]["seed"] = fixed_seed_value
    else:
        # 随机种子，范围 0 到 2^32-1
        import random
        workflow["11"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)
        print(f"🎲 使用随机种子: {workflow['11']['inputs']['seed']}")
    
    workflow["9"]["inputs"]["weight"] = ip_weight
    workflow["9"]["inputs"]["cn_strength"] = cn_strength
    
    workflow["11"]["inputs"]["denoise"] = denoise
    workflow["11"]["inputs"]["cfg"] = cfg
    workflow["11"]["inputs"]["steps"] = steps
    
    workflow["14"]["inputs"]["correction_strength"] = correction_strength
    
    workflow["10"]["inputs"]["width"] = width
    workflow["10"]["inputs"]["height"] = height
    
    debug_path = os.path.join(TEMP_DIR, f"25d_debug_{int(time.time())}.json")
    with open(debug_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2)
    print(f"📁 调试工作流: {debug_path}")
    
    progress(0.5, desc="生成中...")
    image, status = run_comfyui_workflow(workflow, progress)
    
    if image:
        saved_path, job_dir = save_image_to_project(image, prefix="scifi", style_name=style_name)
        msg = f"✅ 生成完成！图片已保存到: {job_dir}\n"
        if is_preset_mode and selected_style and selected_style != "无（使用自定义提示词）":
            msg += f"🎨 使用画风：{selected_style}\n"
            if "女性" in str(PRESET_STYLES.get(selected_style, {}).get("description", "")):
                msg += "💡 提示：预设画风为女性角色，男性用户建议使用高级模式"
        return image, msg
    else:
        return None, status

# ==================== UI 界面 ====================
def create_ui():
    with gr.Blocks(title="FaceOrbit - 2.5D多画风模式") as demo:
        gr.Markdown("""
        # 🎨 FaceOrbit - 2.5D多画风模式
        ### 赛博朋克/水彩/魔法等多种画风 | 专注画风迁移，单张输出
        
        > 💡 **模型特点**：GhostXL 擅长画风迁移，不擅长多角度。本模式专注画风表现。
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                input_image = gr.Image(label="📸 上传头像照片", type="filepath", height=250)
                gr.Markdown("> 📌 **照片的作用**：决定角色的**面部特征**（脸型、五官、表情）")
                
                model_selector = gr.Dropdown(choices=list(MODEL_OPTIONS.keys()), label="🎮 选择模型", value="GhostXL V1.0")
                mode_selector = gr.Radio(
                    choices=["🎨 预设画风模式", "⚙️ 高级模式"],
                    label="选择模式",
                    value="🎨 预设画风模式"
                )
                
                # 预设画风模式
                with gr.Group(visible=True) as preset_mode_group:
                    gr.Markdown("### 🎨 选择画风")
                    gr.Markdown("> ⚠️ **提示**：预设画风为女性角色设计，男性角色请使用「高级模式」")
                    
                    style_dropdown = gr.Dropdown(
                        choices=["无（使用自定义提示词）"] + list(PRESET_STYLES.keys()),
                        label="🎭 画风预设",
                        value="经典镜头 - 仿攻壳机动队"
                    )
                    
                    style_desc = gr.Markdown(f"**画风描述**：{PRESET_STYLES['经典镜头 - 仿攻壳机动队']['description']}")
                    
                    def update_style_desc(choice):
                        if choice in PRESET_STYLES:
                            return f"**画风描述**：{PRESET_STYLES[choice]['description']}"
                        return "**画风描述**：使用自定义提示词"
                    style_dropdown.change(update_style_desc, style_dropdown, style_desc)
                
                # 高级模式
                with gr.Group(visible=False) as advanced_mode_group:
                    gr.Markdown("### ⚙️ 自定义提示词")
                    gr.Markdown("自由组合元素，或直接输入完整提示词")
                    
                    with gr.Row():
                        gender = gr.Dropdown(choices=["女孩", "男孩"], label="性别", value="女孩")
                        identity = gr.Dropdown(choices=["无", "战士", "魔法师", "机械师", "特工", "忍者"], label="身份", value="无")
                    with gr.Row():
                        scene = gr.Dropdown(choices=["无", "城市夜景", "森林", "雪地", "舞台"], label="场景", value="无")
                        props = gr.Dropdown(choices=["无", "吉他", "剑", "魔法杖", "枪"], label="道具", value="无")
                    with gr.Row():
                        action = gr.Dropdown(choices=["无", "站立", "坐着", "奔跑", "弹奏"], label="动作", value="无")
                        extra_details = gr.Textbox(label="额外细节", placeholder="霓虹灯、雨景、机械义体...", lines=1)
                    custom_prompt = gr.Textbox(label="完整提示词", value="", lines=4)
                    
                    def update_prompt(g, i, s, p, a, e):
                        return build_custom_prompt(g, i, s, p, a, e)
                    
                    for comp in [gender, identity, scene, props, action, extra_details]:
                        comp.change(update_prompt, [gender, identity, scene, props, action, extra_details], custom_prompt)
                    
                    # 高级模式提示
                    gr.Markdown("> 💡 **提示**：高级模式支持男性和女性角色，可根据需要自由调整提示词")
                
                # 通用参数
                with gr.Accordion("⚙️ 生成参数", open=False):
                    with gr.Row():
                        use_fixed_seed = gr.Checkbox(label="使用固定种子", value=False)
                        fixed_seed_value = gr.Number(value=42, label="种子值", precision=0)
                    
                    negative_prompt = gr.Textbox(label="负向提示词", value=DEFAULT_NEGATIVE, lines=2)
                    ip_weight = gr.Slider(0.5, 1.0, value=0.85, step=0.01, label="相似度（越高越像照片）")
                    cn_strength = gr.Slider(0.0, 1.0, value=0.45, step=0.01, label="姿态控制")
                    denoise = gr.Slider(0.5, 0.9, value=0.6, step=0.01, label="创意度")
                    cfg = gr.Slider(1.0, 10.0, value=6.5, step=0.1, label="提示词引导")
                    steps = gr.Slider(20, 50, value=28, step=1, label="采样步数")
                    correction_strength = gr.Slider(0.0, 1.0, value=0.3, step=0.05, label="色彩校正（降低可减少重影）")
                    with gr.Row():
                        width = gr.Number(value=1024, label="宽度")
                        height = gr.Number(value=1024, label="高度")
                
                with gr.Accordion("💾 模板管理", open=False):
                    with gr.Row():
                        template_name = gr.Textbox(label="模板名称", scale=2)
                        save_btn = gr.Button("💾 保存", scale=1)
                    save_status = gr.Markdown("")
                    with gr.Row():
                        template_list = gr.Dropdown(choices=list_templates(), scale=2)
                        load_btn = gr.Button("📂 加载", scale=1)
                        delete_btn = gr.Button("🗑️ 删除", scale=1)
                    load_status = gr.Markdown("")
                    refresh_btn = gr.Button("🔄 刷新列表")
                
                generate_btn = gr.Button("🚀 开始生成", variant="primary", size="lg")
                status = gr.Markdown("")
            
            # 输出区域 - 单张图片
            with gr.Column(scale=1):
                gr.Markdown("### ✨ 生成结果")
                gr.Markdown("> ⚠️ **提示**：GhostXL 擅长画风迁移，本模式专注画风表现，输出单张最佳效果")
                output_image = gr.Image(label="生成结果")
        
        # 模式切换
        def switch_mode(m):
            is_preset = (m == "🎨 预设画风模式")
            return gr.update(visible=is_preset), gr.update(visible=not is_preset)
        mode_selector.change(switch_mode, mode_selector, [preset_mode_group, advanced_mode_group])
        
        # 模板操作
        def get_params():
            return {
                "model_name": model_selector.value,
                "negative_prompt": negative_prompt.value,
                "use_fixed_seed": use_fixed_seed.value,
                "fixed_seed_value": fixed_seed_value.value,
                "ip_weight": ip_weight.value,
                "cn_strength": cn_strength.value,
                "denoise": denoise.value,
                "cfg": cfg.value,
                "steps": steps.value,
                "correction_strength": correction_strength.value,
                "width": width.value,
                "height": height.value
            }
        
        save_btn.click(lambda n: save_template(n, get_params()), [template_name], [save_status, template_list])
        
        def set_params(params):
            if not params:
                return [gr.update()] * 12
            return [
                params.get("model_name", "GhostXL V1.0"),
                params.get("negative_prompt", DEFAULT_NEGATIVE),
                params.get("use_fixed_seed", True),
                params.get("fixed_seed_value", 42),
                params.get("ip_weight", 0.85),
                params.get("cn_strength", 0.45),
                params.get("denoise", 0.6),
                params.get("cfg", 6.5),
                params.get("steps", 28),
                params.get("correction_strength", 0.3),
                params.get("width", 1024),
                params.get("height", 1024)
            ]
        
        load_btn.click(lambda n: set_params(load_template(n)[0]), [template_list], 
            [model_selector, negative_prompt, use_fixed_seed, fixed_seed_value,
             ip_weight, cn_strength, denoise, cfg, steps, correction_strength, width, height, load_status])
        
        delete_btn.click(delete_template, [template_list], [load_status, template_list])
        refresh_btn.click(lambda: gr.Dropdown(choices=list_templates()), outputs=[template_list])
        
        # 生成按钮
        generate_btn.click(
            lambda img, model, mode, style, custom_prompt, neg, ip, cn, den, c, st, corr, w, h, seed_flag, seed_val: 
                generate_images(
                    img, model, mode, style, custom_prompt, neg,
                    ip, cn, den, c, st, corr, w, h, seed_flag, seed_val
                ),
            inputs=[input_image, model_selector, mode_selector, style_dropdown, custom_prompt, negative_prompt,
                    ip_weight, cn_strength, denoise, cfg, steps, correction_strength, width, height,
                    use_fixed_seed, fixed_seed_value],
            outputs=[output_image, status]
        )
    
    return demo

def open_browser(url, delay=1.5):
    threading.Timer(delay, lambda: webbrowser.open(url)).start()

if __name__ == "__main__":
    demo = create_ui()
    local_url = "http://127.0.0.1:7865"
    
    print(f"🚀 正在启动 FaceOrbit - 2.5D多画风模式...")
    print(f"📍 本地地址: {local_url}")
    print(f"🔧 ComfyUI API 地址: {COMFYUI_API}")
    print(f"💡 GhostXL 专注画风迁移，单张输出")
    
    open_browser(local_url)
    
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7865
    )