#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaceOrbit - 真实感多画风模式
摄影/电影/生活等多种真实感画风，保留照片面部特征
专注真实感人像与场景，单张输出
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
import random

# ==================== 配置 ====================
WORKFLOW_PATH = "workflows/realistic_style.json"
TEMPLATES_DIR = "user_templates_realistic"
TEMP_DIR = "temp"
OUTPUT_DIR = "output"
COMFYUI_API = "http://127.0.0.1:8188"
MODEL_OPTIONS = {
    "RealVisXL V5.0 Lightning": "realvisxlV50_v50LightningBakedvae.safetensors",
    "RealVisXL V5.0 FP16": "RealVisXL_V5.0_fp16.safetensors",
    "DreamShaper XL": "dreamshaperXL_lightningDPMSDE.safetensors"
}

# 创建必要的文件夹
for dir_name in [TEMPLATES_DIR, TEMP_DIR, OUTPUT_DIR]:
    os.makedirs(dir_name, exist_ok=True)

# ==================== 负向提示词 ====================
DEFAULT_NEGATIVE = "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, ugly, deformed, illustration, 3d, 2d, painting, cartoon, sketch"

# ==================== 预设画风库 ====================
PRESET_STYLES = {
    "霓虹灯的夜晚": {
        "prompt": "city street, neon, fog, volumetric, closeup portrait photo of young woman, beautiful woman, dark clothes, 8k, ultra detailed, photorealistic",
        "description": "霓虹灯夜晚，都市氛围，光影交错",
        "gender": "female"
    },
    "职场女精英": {
        "prompt": "centered, portrait photo of 35 year old woman, open jacket, sweater, natural skin, dark shot, professional, highly detailed, 8k",
        "description": "职场女性，干练优雅，自然光",
        "gender": "female"
    },
    "赛博女战士": {
        "prompt": "masterpiece, best quality, 1girl, sci-fi armor with black and red colors, glowing elements, red hair, cyberpunk, futuristic, highly detailed, 8k",
        "description": "赛博战士，科幻装甲，红色元素",
        "gender": "female"
    },
    "城市的傍晚": {
        "prompt": "perfect photo of beautiful woman standing on high tech cupola building, city view, evening sunset, aesthetic, vibrant, photorealistic, 8k",
        "description": "城市傍晚，建筑美学，夕阳余晖下的女性",
        "gender": "female"
    },
    "一只狼": {
        "prompt": "closeup portrait photo of mysterious woman with wolf spirit, silver hair, wolf-like eyes, fantasy, dark atmospheric, ethereal, highly detailed, 8k",
        "description": "狼灵少女，神秘气质，野性之美",
        "gender": "female"
    },
    "地下城幻境": {
        "prompt": "beautiful woman explorer in underground ancient city, glowing mushrooms lighting her face, breathtaking, vibrant, magic, fantasy, ethereal, 8k",
        "description": "地下古城探险者，发光蘑菇下的女性身影",
        "gender": "female"
    },
    "路边的咖啡屋": {
        "prompt": "cinematic photorealistic, beautiful woman sitting outside modern industrial-style cafe, casual chic outfit, coffee cup, natural lighting, street photography, film grain, bokeh, professional, 8k",
        "description": "咖啡屋外，时尚女性，街拍质感",
        "gender": "female"
    },
    "欧洲风格 - 哥特美学": {
        "prompt": "photo of gothic style woman, dark elegant dress, Victorian atmosphere, award winning photography, light attenuation, complete sharpness, 8k",
        "description": "哥特女性，暗黑优雅，艺术感人像",
        "gender": "female"
    },
    "窗边": {
        "prompt": "beautiful woman with short red hair, pale skin, freckles, big green eyes, slim face, lying in her bed, headphones, eyes closed, poorly lit apartment, window with view on night city, outside rainy, neon lights, ultra HD quality, realistic, photorealism, 8k",
        "description": "窗边少女，赛博公寓，雨夜霓虹",
        "gender": "female"
    },
    "家居": {
        "prompt": "luxury classical style living room, beautiful woman reading a book on couch, tranquil afternoon light, sophisticated, elegant, highly detailed, 8k",
        "description": "家居生活，古典奢华，静谧午后的女性",
        "gender": "female"
    }
}

# ==================== 辅助函数 ====================
def build_custom_prompt(gender, age, style, scene, clothing, extra_details):
    """根据用户选择构建自定义提示词"""
    prompt_parts = ["masterpiece, best quality, photorealistic, 8k"]
    
    if gender == "女性":
        prompt_parts.append("1girl")
    elif gender == "男性":
        prompt_parts.append("1boy")
    
    if age and age != "无":
        prompt_parts.append(f"{age} years old")
    if style and style != "无":
        prompt_parts.append(style)
    if scene and scene != "无":
        prompt_parts.append(scene)
    if clothing and clothing != "无":
        prompt_parts.append(clothing)
    if extra_details:
        prompt_parts.append(extra_details)
    
    prompt_parts.append("highly detailed, professional photography")
    return ", ".join(prompt_parts)

# ==================== 通用辅助函数 ====================
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

def save_image_to_project(image, prefix="realistic", style_name=""):
    """保存单张图片到规范的文件夹结构"""
    if image is None:
        return None, ""
    
    job_folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_dir = os.path.join(OUTPUT_DIR, "jobs", job_folder_name)
    single_dir = os.path.join(job_dir, "single")
    os.makedirs(single_dir, exist_ok=True)
    
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
    
    debug_path = os.path.join(TEMP_DIR, f"realistic_api_send_{int(time.time())}.json")
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
        print(f"🎨 预设画风模式 - 使用画风: {selected_style}")
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
    workflow["1"]["inputs"]["ckpt_name"] = MODEL_OPTIONS.get(model_name, "realvisxlV50_v50LightningBakedvae.safetensors")
    workflow["7"]["inputs"]["text"] = prompt_text
    workflow["8"]["inputs"]["text"] = negative_prompt
    
    if use_fixed_seed:
        workflow["11"]["inputs"]["seed"] = fixed_seed_value
        print(f"🎲 使用固定种子: {fixed_seed_value}")
    else:
        random_seed = random.randint(0, 2**32 - 1)
        workflow["11"]["inputs"]["seed"] = random_seed
        print(f"🎲 使用随机种子: {random_seed}")
    
    workflow["9"]["inputs"]["weight"] = ip_weight
    workflow["9"]["inputs"]["cn_strength"] = cn_strength
    
    workflow["11"]["inputs"]["denoise"] = denoise
    workflow["11"]["inputs"]["cfg"] = cfg
    workflow["11"]["inputs"]["steps"] = steps
    
    workflow["14"]["inputs"]["correction_strength"] = correction_strength
    
    workflow["10"]["inputs"]["width"] = width
    workflow["10"]["inputs"]["height"] = height
    
    debug_path = os.path.join(TEMP_DIR, f"realistic_debug_{int(time.time())}.json")
    with open(debug_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2)
    print(f"📁 调试工作流: {debug_path}")
    
    progress(0.5, desc="生成中...")
    image, status = run_comfyui_workflow(workflow, progress)
    
    if image:
        saved_path, job_dir = save_image_to_project(image, prefix="realistic", style_name=style_name)
        msg = f"✅ 生成完成！图片已保存到: {job_dir}\n🎨 使用画风：{style_name}"
        return image, msg
    else:
        return None, status

# ==================== UI 界面 ====================
def create_ui():
    with gr.Blocks(title="FaceOrbit - 真实感多画风模式") as demo:
        gr.Markdown("""
        # 📸 FaceOrbit - 真实感多画风模式
        ### 摄影/电影/生活等多种真实感画风 | 上传照片，AI 帮你创造真实影像
        
        > 💡 **模型特点**：RealVisXL 擅长真实感人像，单张输出，画质堪比摄影。
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                input_image = gr.Image(label="📸 上传头像照片", type="filepath", height=250)
                gr.Markdown("> 📌 **照片的作用**：决定人物的**面部特征**（脸型、五官、表情）")
                
                model_selector = gr.Dropdown(choices=list(MODEL_OPTIONS.keys()), label="🎮 选择模型", value="RealVisXL V5.0 Lightning")
                mode_selector = gr.Radio(
                    choices=["🎨 预设画风模式", "⚙️ 高级模式"],
                    label="选择模式",
                    value="🎨 预设画风模式"
                )
                
                # 预设画风模式
                with gr.Group(visible=True) as preset_mode_group:
                    gr.Markdown("### 🎨 选择画风")
                    gr.Markdown("> 💡 **提示**：预设画风涵盖人像、场景、动物等多种真实感主题")
                    
                    style_dropdown = gr.Dropdown(
                        choices=["无（使用自定义提示词）"] + list(PRESET_STYLES.keys()),
                        label="🎭 画风预设",
                        value="职场女精英"
                    )
                    
                    style_desc = gr.Markdown(f"**画风描述**：{PRESET_STYLES['职场女精英']['description']}")
                    
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
                        gender = gr.Dropdown(choices=["女性", "男性"], label="性别", value="女性")
                        age = gr.Dropdown(choices=["无", "20", "25", "30", "35", "40", "45"], label="年龄", value="无")
                    with gr.Row():
                        style = gr.Dropdown(choices=["无", "职场", "休闲", "运动", "晚礼服"], label="风格", value="无")
                        scene = gr.Dropdown(choices=["无", "城市街头", "办公室", "咖啡馆", "自然公园", "海边"], label="场景", value="无")
                    with gr.Row():
                        clothing = gr.Dropdown(choices=["无", "西装", "休闲装", "连衣裙", "运动服"], label="服装", value="无")
                        extra_details = gr.Textbox(label="额外细节", placeholder="例如：自然光、虚化背景、夕阳...", lines=1)
                    
                    custom_prompt = gr.Textbox(label="完整提示词", value="", lines=4)
                    
                    def update_prompt(g, a, s, sc, c, e):
                        return build_custom_prompt(g, a, s, sc, c, e)
                    
                    for comp in [gender, age, style, scene, clothing, extra_details]:
                        comp.change(update_prompt, [gender, age, style, scene, clothing, extra_details], custom_prompt)
                
                # 通用参数
                with gr.Accordion("⚙️ 生成参数", open=False):
                    with gr.Row():
                        use_fixed_seed = gr.Checkbox(label="使用固定种子", value=False)
                        fixed_seed_value = gr.Number(value=42, label="种子值", precision=0, visible=False)
                    
                    def toggle_seed_input(checked):
                        return gr.update(visible=checked)
                    use_fixed_seed.change(toggle_seed_input, inputs=[use_fixed_seed], outputs=[fixed_seed_value])
                    
                    negative_prompt = gr.Textbox(label="负向提示词", value=DEFAULT_NEGATIVE, lines=2)
                    ip_weight = gr.Slider(0.5, 1.0, value=0.92, step=0.01, label="相似度（越高越像照片）")
                    cn_strength = gr.Slider(0.0, 1.0, value=0.5, step=0.01, label="姿态控制")
                    denoise = gr.Slider(0.5, 0.9, value=0.73, step=0.01, label="创意度")
                    cfg = gr.Slider(1.0, 10.0, value=3.0, step=0.1, label="提示词引导")
                    steps = gr.Slider(15, 50, value=30, step=1, label="采样步数")
                    correction_strength = gr.Slider(0.0, 1.0, value=0.55, step=0.05, label="色彩校正")
                    with gr.Row():
                        width = gr.Number(value=896, label="宽度")
                        height = gr.Number(value=1152, label="高度")
                
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
                gr.Markdown("> 💡 **提示**：RealVisXL 擅长真实感人像，单张输出高质量影像")
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
                params.get("model_name", "RealVisXL V5.0 Lightning"),
                params.get("negative_prompt", DEFAULT_NEGATIVE),
                params.get("use_fixed_seed", False),
                params.get("fixed_seed_value", 42),
                params.get("ip_weight", 0.92),
                params.get("cn_strength", 0.5),
                params.get("denoise", 0.73),
                params.get("cfg", 3.0),
                params.get("steps", 30),
                params.get("correction_strength", 0.55),
                params.get("width", 896),
                params.get("height", 1152)
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
    local_url = "http://127.0.0.1:7864"
    
    print(f"🚀 正在启动 FaceOrbit - 真实感多画风模式...")
    print(f"📍 本地地址: {local_url}")
    print(f"🔧 ComfyUI API 地址: {COMFYUI_API}")
    print(f"💡 RealVisXL 擅长真实感人像，单张输出")
    
    open_browser(local_url)
    
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7864
    )