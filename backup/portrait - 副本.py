#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaceOrbit - 写真模式
真实感人像生成 | 身份图(面部) + 姿态参考图(身形) 分离
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
WORKFLOW_PATH = "workflows/portrait_6angles.json"
TEMPLATES_DIR = "user_templates_portrait"
TEMP_DIR = "temp"
OUTPUT_DIR = "output"
COMFYUI_API = "http://127.0.0.1:8188"
MODEL_OPTIONS = {
    "RealVisXL V5.0 FP16": "RealVisXL_V5.0_fp16.safetensors",
    "RealVisXL V5.0 Lightning": "realvisxlV50_v50LightningBakedvae.safetensors",
    "DreamShaper XL": "dreamshaperXL_lightningDPMSDE.safetensors"
}

# 创建必要的文件夹
for dir_name in [TEMPLATES_DIR, TEMP_DIR, OUTPUT_DIR]:
    os.makedirs(dir_name, exist_ok=True)

# ==================== 默认参数 ====================
DEFAULT_NEGATIVE = "worst quality, low quality, normal quality, lowres, jpeg artifacts, blurry, noisy, soft focus, distorted, deformed, ugly, bad anatomy, bad hands, asymmetrical face, out of frame, cropped head, two heads, double head, multiple faces, extra head, clone, multiple people, watermark, text, signature, illustration, 3d, 2d, painting, cartoon, sketch, dark, underexposed, low contrast, gray skin, dull color, muddy colors, flat lighting, haze, foggy, washed out"

# 六角度默认提示词
DEFAULT_PROMPTS = {
    "front": "high quality realistic full body studio portrait photo, front view, facing camera, standing upright, both eyes visible, natural skin texture, bright soft studio lighting, clean white background, balanced exposure, clear contrast, natural skin tone, sharp focus, high resolution",
    "back": "high quality realistic full body studio portrait photo, back view, facing away from camera, back of head visible, no face visible, standing upright, bright soft studio lighting, clean white background, balanced exposure, clear contrast, realistic color, sharp focus, high resolution",
    "left_quarter": "high quality realistic full body studio portrait photo, three quarter left side view, body turned 45 degrees left, face slightly turned left, both eyes visible, natural skin texture, bright soft studio lighting, clean white background, balanced exposure, clear contrast, natural skin tone, sharp focus, high resolution",
    "right_quarter": "high quality realistic full body studio portrait photo, three quarter right side view, body turned 45 degrees right, face slightly turned right, both eyes visible, natural skin texture, bright soft studio lighting, clean white background, balanced exposure, clear contrast, natural skin tone, sharp focus, high resolution",
    "side": "high quality realistic full body studio portrait photo, strict side view, body turned 90 degrees left, face looking left, one eye visible, nose profile visible, ear visible, standing upright, bright soft studio lighting, clean white background, balanced exposure, clear contrast, natural skin tone, sharp focus, high resolution",
    "top": "high quality realistic portrait photo, top down view, camera above the person, looking slightly upward, visible head and shoulders from above, bright soft studio lighting, clean white background, balanced exposure, clear contrast, natural skin tone, sharp focus, high resolution"
}

# 姿态参考图说明
POSE_GUIDE = """
### 📌 姿态参考图要求
| 角度 | 文件名 | 说明 |
|------|--------|------|
| 正面 | `pose_front.jpg` | 正面站立，双手自然下垂 |
| 背面 | `pose_back.jpg` | 背面站立 |
| 左四分之三 | `pose_left_quarter.jpg` | 身体左转45度 |
| 右四分之三 | `pose_right_quarter.jpg` | 身体右转45度 |
| 侧面 | `pose_side.jpg` | 严格90度侧身 |
| 顶视 | `pose_top.jpg` | 俯拍角度 |

> 💡 **提示**：姿态参考图只需提供身形轮廓，可以是任何人。面部特征来自上传的身份照片。
"""

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

def save_images_to_project(images, prefix="portrait"):
    """保存单张图片和拼图到规范的文件夹结构"""
    if not images:
        return [], ""
    
    job_folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_dir = os.path.join(OUTPUT_DIR, "jobs", job_folder_name)
    single_dir = os.path.join(job_dir, "single")
    total_dir = os.path.join(job_dir, "total")
    os.makedirs(single_dir, exist_ok=True)
    os.makedirs(total_dir, exist_ok=True)
    
    angle_names = ["front", "back", "left_quarter", "right_quarter", "side", "top"]
    saved_paths = []
    single_paths = []
    
    for i, (img, angle) in enumerate(zip(images, angle_names)):
        if img:
            filename = f"{prefix}_{angle}.png"
            filepath = os.path.join(single_dir, filename)
            img.save(filepath)
            saved_paths.append(filepath)
            single_paths.append(filepath)
            print(f"💾 已保存单张: {filepath}")
    
    # 创建拼图
    if len(single_paths) == 6:
        try:
            thumb_width, thumb_height = 300, 438
            collage_width = thumb_width * 3
            collage_height = thumb_height * 2
            collage = Image.new('RGB', (collage_width, collage_height), color='white')
            
            for idx, img_path in enumerate(single_paths):
                row = idx // 3
                col = idx % 3
                img = Image.open(img_path)
                img.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                x = col * thumb_width
                y = row * thumb_height
                collage.paste(img, (x, y))
            
            collage_path = os.path.join(total_dir, f"{prefix}_collage.png")
            collage.save(collage_path)
            print(f"🖼️ 已保存拼图: {collage_path}")
            saved_paths.append(collage_path)
        except Exception as e:
            print(f"创建拼图失败: {e}")
    
    return saved_paths, job_dir

# ==================== ComfyUI API 调用 ====================
def run_comfyui_workflow(workflow, progress):
    """发送工作流到 ComfyUI 并获取图片"""
    
    progress(0.7, desc="发送到 ComfyUI...")
    
    debug_path = os.path.join(TEMP_DIR, f"portrait_api_send_{int(time.time())}.json")
    with open(debug_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)
    print(f"📤 已保存发送到 API 的工作流: {debug_path}")
    
    # 使用您工作流中的实际节点名称
    node_order = ["15_front", "15_back", "15_left_quarter", "15_right_quarter", "15_side", "15_top"]
    angle_names = ["正面", "背面", "左四分之三", "右四分之三", "侧面", "顶视"]
    
    try:
        response = requests.post(
            f"{COMFYUI_API}/prompt",
            json={"prompt": workflow},
            timeout=60
        )
        
        if response.status_code != 200:
            error_msg = response.text
            print(f"❌ API 错误: {error_msg}")
            return [None] * 6, f"❌ API 错误: {error_msg}"
        
        data = response.json()
        prompt_id = data.get("prompt_id")
        
        if not prompt_id:
            return [None] * 6, "❌ 未获取到 prompt_id"
        
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
                        
                        images = []
                        for node_id in node_order:
                            if node_id in outputs and "images" in outputs[node_id]:
                                img_info = outputs[node_id]["images"][0]
                                img_response = requests.get(
                                    f"{COMFYUI_API}/view",
                                    params={"filename": img_info["filename"], "subfolder": img_info.get("subfolder", "")}
                                )
                                if img_response.status_code == 200:
                                    img = Image.open(io.BytesIO(img_response.content))
                                    images.append(img)
                                    print(f"🖼️ 获取图片: {node_id} ({angle_names[node_order.index(node_id)]}) -> {img_info['filename']}")
                                else:
                                    print(f"⚠️ 获取图片失败: {node_id}")
                                    images.append(None)
                            else:
                                print(f"⚠️ 节点 {node_id} 没有图片输出")
                                images.append(None)
                        
                        if any(images):
                            print(f"✅ 成功获取 {len([i for i in images if i])}/6 张图片")
                            return images, f"✅ 生成完成！共 {len([i for i in images if i])} 张图片，耗时 {elapsed} 秒"
                        else:
                            print("⏳ 生成中，继续等待...")
            except Exception as e:
                print(f"查询时出错: {e}")
            
            elapsed += 2
            minutes = elapsed // 60
            seconds = elapsed % 60
            progress(0.8, desc=f"生成中... 已等待 {minutes}分{seconds}秒")
            time.sleep(2)
        
    except requests.exceptions.ConnectionError:
        return [None] * 6, f"❌ 无法连接 ComfyUI API\n请确保 ComfyUI 已启动并添加 --listen 参数"
    except Exception as e:
        print(f"❌ 异常: {e}")
        return [None] * 6, f"❌ 运行失败: {str(e)}"

# ==================== 核心生成函数 ====================
def generate_images(
    input_image,
    model_name,
    prompt_front,
    prompt_back,
    prompt_left_quarter,
    prompt_right_quarter,
    prompt_side,
    prompt_top,
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
        return [None]*6, "❌ 请先上传头像照片"
    
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    # 保存上传的图片到 ComfyUI 的 input 目录
    comfyui_input_dir = "D:/PixelSmile/ComfyUI-aki/ComfyUI-aki-v3/ComfyUI/input"
    os.makedirs(comfyui_input_dir, exist_ok=True)

    original_filename = os.path.basename(input_image)
    if not original_filename.startswith("faceorbit_"):
        local_image_path = os.path.join(comfyui_input_dir, f"faceorbit_{uuid.uuid4().hex}_{original_filename}")
    else:
        local_image_path = os.path.join(comfyui_input_dir, original_filename)

    shutil.copy2(input_image, local_image_path)
    print(f"📸 图片已复制到 ComfyUI input: {local_image_path}")

    # 设置身份参考图
    workflow["3"]["inputs"]["image"] = local_image_path
    
    # 设置模型
    workflow["1"]["inputs"]["ckpt_name"] = MODEL_OPTIONS.get(model_name, "RealVisXL_V5.0_fp16.safetensors")
    
    # 设置提示词
    angle_prompts = {
        "prompt_front": prompt_front,
        "prompt_back": prompt_back,
        "prompt_left_quarter": prompt_left_quarter,
        "prompt_right_quarter": prompt_right_quarter,
        "prompt_side": prompt_side,
        "prompt_top": prompt_top
    }
    
    for node_id, prompt_text in angle_prompts.items():
        if node_id in workflow:
            workflow[node_id]["inputs"]["text"] = prompt_text
    
    # 设置负向提示词
    if "8" in workflow:
        workflow["8"]["inputs"]["text"] = negative_prompt
    
    # 设置 InstantID 参数（每个角度独立）
    # 正面
    if "instantid_front" in workflow:
        workflow["instantid_front"]["inputs"]["ip_weight"] = ip_weight
        workflow["instantid_front"]["inputs"]["cn_strength"] = cn_strength
    
    # 背面
    if "instantid_back" in workflow:
        workflow["instantid_back"]["inputs"]["ip_weight"] = ip_weight * 0.8
        workflow["instantid_back"]["inputs"]["cn_strength"] = cn_strength * 0.9
    
    # 左四分之三
    if "instantid_left_quarter" in workflow:
        workflow["instantid_left_quarter"]["inputs"]["ip_weight"] = ip_weight * 0.85
        workflow["instantid_left_quarter"]["inputs"]["cn_strength"] = cn_strength * 1.0
    
    # 右四分之三
    if "instantid_right_quarter" in workflow:
        workflow["instantid_right_quarter"]["inputs"]["ip_weight"] = ip_weight * 0.85
        workflow["instantid_right_quarter"]["inputs"]["cn_strength"] = cn_strength * 1.0
    
    # 侧面
    if "instantid_side" in workflow:
        workflow["instantid_side"]["inputs"]["ip_weight"] = ip_weight * 0.7
        workflow["instantid_side"]["inputs"]["cn_strength"] = cn_strength * 1.2
    
    # 顶视
    if "instantid_top" in workflow:
        workflow["instantid_top"]["inputs"]["ip_weight"] = ip_weight * 0.85
        workflow["instantid_top"]["inputs"]["cn_strength"] = cn_strength * 0.9
    
    # 设置采样器参数
    sampler_nodes = ["sampler_front", "sampler_back", "sampler_left_quarter", "sampler_right_quarter", "sampler_side", "sampler_top"]
    for node_id in sampler_nodes:
        if node_id in workflow:
            if use_fixed_seed:
                workflow[node_id]["inputs"]["seed"] = fixed_seed_value
            else:
                workflow[node_id]["inputs"]["seed"] = random.randint(0, 2**32 - 1)
            workflow[node_id]["inputs"]["steps"] = steps
            workflow[node_id]["inputs"]["cfg"] = cfg
            workflow[node_id]["inputs"]["denoise"] = denoise
    
    # 设置色彩校正强度（如果有）
    for node_id in ["correction_front", "correction_back", "correction_left_quarter", "correction_right_quarter", "correction_side", "correction_top"]:
        if node_id in workflow:
            workflow[node_id]["inputs"]["correction_strength"] = correction_strength
    
    # 设置分辨率
    if "10" in workflow:
        workflow["10"]["inputs"]["width"] = width
        workflow["10"]["inputs"]["height"] = height
    
    # 调试保存
    debug_path = os.path.join(TEMP_DIR, f"portrait_debug_{int(time.time())}.json")
    with open(debug_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2)
    print(f"📁 调试工作流: {debug_path}")
    
    progress(0.5, desc="生成中...")
    images, status = run_comfyui_workflow(workflow, progress)
    
    if images and any(images):
        saved_paths, job_dir = save_images_to_project(images, prefix="portrait")
        msg = f"✅ 生成完成！图片已保存到: {job_dir}"
        result = list(images[:6]) + [msg]
        while len(result) < 7:
            result.append(None)
        return tuple(result[:7])
    else:
        return (None, None, None, None, None, None, "⚠️ 未获取到图片")

# ==================== UI 界面 ====================
def create_ui():
    with gr.Blocks(title="FaceOrbit - 写真模式", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 📸 FaceOrbit - 写真模式
        ### 真实感人像生成 | 身份图(面部) + 姿态参考图(身形) 分离
        
        > 💡 **工作原理**：面部特征来自您上传的身份照片，身形姿态来自预设的姿态参考图。
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                input_image = gr.Image(label="📸 上传身份照片（面部）", type="filepath", height=250)
                gr.Markdown("> 📌 **照片的作用**：决定人物的**面部特征**（脸型、五官、表情）")
                gr.Markdown("> ⚠️ 请使用清晰、正面、单人的照片，以获得最佳效果")
                
                gr.Markdown(POSE_GUIDE)
                
                model_selector = gr.Dropdown(choices=list(MODEL_OPTIONS.keys()), label="🎮 选择模型", value="RealVisXL V5.0 FP16")
                
                with gr.Accordion("📝 各角度提示词设置", open=False):
                    with gr.Tabs():
                        with gr.TabItem("正面"):
                            prompt_front = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["front"], lines=3)
                        with gr.TabItem("背面"):
                            prompt_back = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["back"], lines=3)
                        with gr.TabItem("左四分之三"):
                            prompt_left_quarter = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["left_quarter"], lines=3)
                        with gr.TabItem("右四分之三"):
                            prompt_right_quarter = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["right_quarter"], lines=3)
                        with gr.TabItem("侧面"):
                            prompt_side = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["side"], lines=3)
                        with gr.TabItem("顶视"):
                            prompt_top = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["top"], lines=3)
                    
                    negative_prompt = gr.Textbox(label="负向提示词（所有角度共用）", value=DEFAULT_NEGATIVE, lines=3)
                
                with gr.Accordion("⚙️ 生成参数", open=False):
                    with gr.Row():
                        use_fixed_seed = gr.Checkbox(label="使用固定种子", value=False)
                        fixed_seed_value = gr.Number(value=42, label="种子值", precision=0, visible=False)
                    
                    def toggle_seed_input(checked):
                        return gr.update(visible=checked)
                    use_fixed_seed.change(toggle_seed_input, inputs=[use_fixed_seed], outputs=[fixed_seed_value])
                    
                    ip_weight = gr.Slider(0.3, 1.0, value=0.85, step=0.01, label="🎭 相似度（越高越像照片）")
                    cn_strength = gr.Slider(0.0, 1.0, value=0.6, step=0.01, label="🎯 姿态控制")
                    denoise = gr.Slider(0.4, 0.9, value=0.75, step=0.01, label="✨ 创意度")
                    cfg = gr.Slider(1.0, 10.0, value=6.0, step=0.1, label="📝 提示词引导")
                    steps = gr.Slider(20, 50, value=30, step=1, label="🔢 采样步数")
                    correction_strength = gr.Slider(0.0, 0.8, value=0.3, step=0.05, label="🎨 色彩校正")
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
            
            with gr.Column(scale=1):
                gr.Markdown("### ✨ 生成结果（6个角度）")
                with gr.Tabs():
                    with gr.TabItem("正面"): out_f = gr.Image()
                    with gr.TabItem("背面"): out_b = gr.Image()
                    with gr.TabItem("左四分之三"): out_lq = gr.Image()
                    with gr.TabItem("右四分之三"): out_rq = gr.Image()
                    with gr.TabItem("侧面"): out_s = gr.Image()
                    with gr.TabItem("顶视"): out_t = gr.Image()
        
        # 模板操作
        def get_params():
            return {
                "model_name": model_selector.value,
                "prompt_front": prompt_front.value,
                "prompt_back": prompt_back.value,
                "prompt_left_quarter": prompt_left_quarter.value,
                "prompt_right_quarter": prompt_right_quarter.value,
                "prompt_side": prompt_side.value,
                "prompt_top": prompt_top.value,
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
        
        def set_params(params):
            if not params:
                return [gr.update()] * 18
            return [
                params.get("model_name", "RealVisXL V5.0 FP16"),
                params.get("prompt_front", DEFAULT_PROMPTS["front"]),
                params.get("prompt_back", DEFAULT_PROMPTS["back"]),
                params.get("prompt_left_quarter", DEFAULT_PROMPTS["left_quarter"]),
                params.get("prompt_right_quarter", DEFAULT_PROMPTS["right_quarter"]),
                params.get("prompt_side", DEFAULT_PROMPTS["side"]),
                params.get("prompt_top", DEFAULT_PROMPTS["top"]),
                params.get("negative_prompt", DEFAULT_NEGATIVE),
                params.get("use_fixed_seed", False),
                params.get("fixed_seed_value", 42),
                params.get("ip_weight", 0.85),
                params.get("cn_strength", 0.6),
                params.get("denoise", 0.75),
                params.get("cfg", 6.0),
                params.get("steps", 30),
                params.get("correction_strength", 0.3),
                params.get("width", 896),
                params.get("height", 1152)
            ]
        
        save_btn.click(lambda n: save_template(n, get_params()), [template_name], [save_status, template_list])
        load_btn.click(lambda n: set_params(load_template(n)[0]), [template_list], 
            [model_selector, prompt_front, prompt_back, prompt_left_quarter, prompt_right_quarter, prompt_side, prompt_top,
             negative_prompt, use_fixed_seed, fixed_seed_value,
             ip_weight, cn_strength, denoise, cfg, steps, correction_strength, width, height, load_status])
        delete_btn.click(delete_template, [template_list], [load_status, template_list])
        refresh_btn.click(lambda: gr.Dropdown(choices=list_templates()), outputs=[template_list])
        
        # 生成按钮
        generate_btn.click(
            generate_images,
            [input_image, model_selector, 
             prompt_front, prompt_back, prompt_left_quarter, prompt_right_quarter, prompt_side, prompt_top,
             negative_prompt, ip_weight, cn_strength, denoise, cfg, steps, 
             correction_strength, width, height, use_fixed_seed, fixed_seed_value],
            [out_f, out_b, out_lq, out_rq, out_s, out_t, status]
        )
    
    return demo

# ==================== 启动 ====================
def open_browser(url, delay=1.5):
    threading.Timer(delay, lambda: webbrowser.open(url)).start()

if __name__ == "__main__":
    demo = create_ui()
    local_url = "http://127.0.0.1:7861"
    
    print(f"🚀 正在启动 FaceOrbit - 写真模式...")
    print(f"📍 本地地址: {local_url}")
    print(f"🔧 ComfyUI API 地址: {COMFYUI_API}")
    print(f"💡 提示：面部来自身份照片，身形来自姿态参考图（需放在 workflows 目录）")
    
    open_browser(local_url)
    
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7861,
        theme=gr.themes.Soft()
    )