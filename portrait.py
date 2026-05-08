#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaceOrbit - 写真模式
真实感人像生成 | 支持「面部优先」和「姿势优先」两种侧重

工作流文件：
- portrait_1.json : 姿势优先 - 优先保证姿态准确性，适用于舞蹈动作、特定姿态等
- portrait_2.json : 面部优先 - 优先保证身份相似度，适用于产品图、证件照等

技术栈：InstantID + DWPose + SDXL
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
# 工作流路径 - 两个版本
WORKFLOW_POSE_PRIORITY = "workflows/portrait_1.json"   # 姿势优先
WORKFLOW_IDENTITY_PRIORITY = "workflows/portrait_2.json"  # 面部优先

TEMPLATES_DIR = "user_templates_portrait"
TEMP_DIR = "temp"
OUTPUT_DIR = "output"
COMFYUI_API = "http://127.0.0.1:8188"

# ComfyUI 路径
COMFYUI_INPUT_DIR = "D:/PixelSmile/ComfyUI-aki/ComfyUI-aki-v3/ComfyUI/input"

MODEL_OPTIONS = {
    "RealVisXL V5.0 FP16": "RealVisXL_V5.0_fp16.safetensors",
    "RealVisXL V5.0 Lightning": "realvisxlV50_v50LightningBakedvae.safetensors",
    "DreamShaper XL": "dreamshaperXL_lightningDPMSDE.safetensors"
}

# 创建必要的文件夹
for dir_name in [TEMPLATES_DIR, TEMP_DIR, OUTPUT_DIR, "workflows"]:
    os.makedirs(dir_name, exist_ok=True)

# ==================== 默认参数 ====================
DEFAULT_NEGATIVE = "worst quality, low quality, normal quality, lowres, jpeg artifacts, blurry, noisy, soft focus, distorted, deformed, ugly, bad anatomy, bad hands, asymmetrical face, out of frame, cropped head, two heads, double head, multiple faces, extra head, clone, multiple people, watermark, text, signature, illustration, 3d, 2d, painting, cartoon, sketch, dark, underexposed, low contrast, gray skin, dull color, muddy colors, flat lighting, haze, foggy, washed out, front view, facing viewer"

# 六角度默认提示词
DEFAULT_PROMPTS = {
    "front": "professional portrait photo, single person, head and shoulders, face centered, looking at camera, neutral expression, plain background, studio lighting, high resolution, realistic skin texture, 8k, sharp focus",
    "back": "professional portrait photo, single person, back view, back of head visible, shoulders and back, plain background, high resolution",
    "left": "professional portrait photo, single person, left three quarter view, body turned 45 degrees left, face visible, plain background, high resolution",
    "right": "professional portrait photo, single person, right three quarter view, body turned 45 degrees right, face visible, plain background, high resolution",
    "side": "professional portrait photo, single person, side profile view, facing left or right, profile visible, plain background, high resolution",
    "top": "professional portrait photo, single person, top down view, bird's eye view, one person, plain white background, high resolution"
}

# 姿势优先模式的增强提示词（更强调姿态）
POSE_ENHANCED_PROMPTS = {
    "front": "full body photo, standing upright, feet shoulder width apart, arms relaxed at sides, facing camera directly, weight evenly distributed, professional stance, plain background, studio lighting",
    "back": "full body photo, standing with back to camera, facing away, back straight, shoulders relaxed, plain background",
    "left": "full body photo, standing at 45 degree angle left, body turned slightly, weight on back foot, natural pose, left side prominent, plain background",
    "right": "full body photo, standing at 45 degree angle right, body turned slightly, weight on back foot, natural pose, right side prominent, plain background",
    "side": "full body photo, strict side profile, standing sideways, one arm visible, natural stance, plain background",
    "top": "portrait photo, looking upward, head tilted back slightly, camera above, shoulders visible, plain background"
}

# ==================== UI 说明 ====================
def get_workflow_info_html():
    """生成工作流说明 HTML（简洁版）"""
    return """
    <div style="background: #f0f4f8; padding: 12px; border-radius: 8px; margin: 10px 0;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <div>
                <strong>📖 基于 InstantID + DWPose + SDXL</strong>
            </div>
        </div>
        <hr style="margin: 8px 0;">
        <div style="font-size: 13px;">
            <strong>🎯 两种模式</strong><br>
            • <strong>👤 面部优先</strong>：保证人物脸部相似度（产品图、证件照）<br>
            • <strong>🏃 姿势优先</strong>：保证姿态准确性（舞蹈、运动场景）
        </div>
        <div style="font-size: 12px; color: #666; margin-top: 8px;">
            💡 详细说明请点击下方「📖 打开完整指南」按钮
        </div>
    </div>
    """

def get_parameter_guide_html():
    """参数调优指南 HTML"""
    return """
    <div style="background: #fef3c7; padding: 12px; border-radius: 8px; margin: 10px 0;">
        <strong>🔧 参数调优速查</strong>
        <table style="width: 100%; font-size: 12px; margin-top: 8px;">
            <tr><th>目标</th><th>参数</th><th>调整</th></tr>
            <tr><td>提高身份相似度</td><td>相似度</td><td style="color:#e74c3c">↑ 增大</td></tr>
            <tr><td>提高姿态准确度</td><td>姿态控制</td><td style="color:#e74c3c">↑ 增大</td></tr>
            <tr><td>更多细节变化</td><td>创意度</td><td style="color:#e74c3c">↑ 增大</td></tr>
            <tr><td>更贴近原图</td><td>创意度</td><td style="color:#2ecc71">↓ 减小</td></tr>
        </table>
    </div>
    """

def open_workflow_guide():
    """打开工作流说明 HTML 文件"""
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, "workflow_ui.html")
    
    if os.path.exists(html_path):
        webbrowser.open(f"file://{os.path.abspath(html_path)}")
        return "📖 已打开工作流说明文档"
    else:
        return f"❌ 未找到 workflow_ui.html 文件\n请确保文件存在于: {script_dir}"

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
    
    angle_names = ["front", "back", "left", "right", "side", "top"]
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

# ==================== 工作流加载 ====================
def get_workflow_path(priority_mode):
    """根据模式选择工作流文件"""
    if "姿势优先" in priority_mode:
        return WORKFLOW_POSE_PRIORITY
    else:
        return WORKFLOW_IDENTITY_PRIORITY

# ==================== ComfyUI API 调用 ====================
def run_comfyui_workflow(workflow, progress):
    """发送工作流到 ComfyUI 并获取图片"""
    
    progress(0.7, desc="发送到 ComfyUI...")
    
    debug_path = os.path.join(TEMP_DIR, f"portrait_api_send_{int(time.time())}.json")
    with open(debug_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2)
    print(f"📤 已保存发送到 API 的工作流: {debug_path}")
    
    # 输出节点名称（与工作流 JSON 一致）
    node_order = ["save_front", "save_back", "save_left", "save_right", "save_side", "save_top"]
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
                                    print(f"🖼️ 获取图片: {node_id} ({angle_names[node_order.index(node_id)]})")
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
    priority_mode,
    prompt_front,
    prompt_back,
    prompt_left,
    prompt_right,
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
    
    # 根据模式选择工作流
    workflow_path = get_workflow_path(priority_mode)
    
    if not os.path.exists(workflow_path):
        return [None]*6, f"❌ 工作流文件不存在: {workflow_path}\n请确保 portrait_1.json 和 portrait_2.json 放在 workflows/ 目录下"
    
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    print(f"📁 使用工作流: {workflow_path}")
    print(f"🎯 模式: {priority_mode}")
    
    # 保存上传的图片到 ComfyUI 的 input 目录
    os.makedirs(COMFYUI_INPUT_DIR, exist_ok=True)
    
    original_filename = os.path.basename(input_image)
    if not original_filename.startswith("faceorbit_"):
        local_image_path = os.path.join(COMFYUI_INPUT_DIR, f"faceorbit_{uuid.uuid4().hex}_{original_filename}")
    else:
        local_image_path = os.path.join(COMFYUI_INPUT_DIR, original_filename)
    
    shutil.copy2(input_image, local_image_path)
    print(f"📸 图片已复制到 ComfyUI input: {local_image_path}")
    
    # 更新工作流中的图片路径
    workflow["3"]["inputs"]["image"] = local_image_path
    workflow["1"]["inputs"]["ckpt_name"] = MODEL_OPTIONS.get(model_name, "RealVisXL_V5.0_fp16.safetensors")
    
    # 根据侧重模式调整提示词
    is_priority_pose = ("姿势优先" in priority_mode)
    
    if is_priority_pose:
        # 姿势优先模式：使用增强的姿势提示词
        angle_prompts = {
            "7_front": POSE_ENHANCED_PROMPTS["front"],
            "7_back": POSE_ENHANCED_PROMPTS["back"],
            "7_left": POSE_ENHANCED_PROMPTS["left"],
            "7_right": POSE_ENHANCED_PROMPTS["right"],
            "7_side": POSE_ENHANCED_PROMPTS["side"],
            "7_top": POSE_ENHANCED_PROMPTS["top"]
        }
        print(f"🏃 姿势优先模式 - 使用增强姿态提示词")
    else:
        # 面部优先模式：使用用户自定义提示词
        angle_prompts = {
            "7_front": prompt_front,
            "7_back": prompt_back,
            "7_left": prompt_left,
            "7_right": prompt_right,
            "7_side": prompt_side,
            "7_top": prompt_top
        }
        print(f"👤 面部优先模式 - 使用用户提示词")
    
    # 应用提示词
    for node_id, prompt_text in angle_prompts.items():
        if node_id in workflow:
            workflow[node_id]["inputs"]["text"] = prompt_text
    
    if "8" in workflow:
        workflow["8"]["inputs"]["text"] = negative_prompt
    
    # 设置种子
    sampler_nodes = ["11_front", "11_back", "11_left", "11_right", "11_side", "11_top"]
    if use_fixed_seed:
        for node_id in sampler_nodes:
            if node_id in workflow:
                workflow[node_id]["inputs"]["seed"] = fixed_seed_value
        print(f"🎲 使用固定种子: {fixed_seed_value}")
    else:
        for node_id in sampler_nodes:
            if node_id in workflow:
                random_seed = random.randint(0, 2**32 - 1)
                workflow[node_id]["inputs"]["seed"] = random_seed
        print(f"🎲 使用随机种子（每个角度不同）")
    
    # 设置 InstantID 参数
    angle_configs = {
        "9_front": {"ip_weight": ip_weight, "cn_strength": cn_strength},
        "9_back": {"ip_weight": ip_weight, "cn_strength": cn_strength},
        "9_left": {"ip_weight": ip_weight, "cn_strength": cn_strength},
        "9_right": {"ip_weight": ip_weight, "cn_strength": cn_strength},
        "9_side": {"ip_weight": ip_weight, "cn_strength": cn_strength},
        "9_top": {"ip_weight": ip_weight, "cn_strength": cn_strength}
    }
    
    # 根据模式微调参数
    if is_priority_pose:
        # 姿势优先：背面和侧面需要更强姿态控制
        angle_configs["9_back"]["cn_strength"] = min(0.8, cn_strength * 1.1)
        angle_configs["9_side"]["cn_strength"] = min(0.8, cn_strength * 1.05)
        angle_configs["9_top"]["ip_weight"] = max(0.5, ip_weight * 0.7)
    else:
        # 面部优先：后面视图需要稍弱姿态控制
        angle_configs["9_back"]["cn_strength"] = max(0.1, cn_strength * 0.8)
        angle_configs["9_top"]["ip_weight"] = max(0.5, ip_weight * 0.85)
    
    for node_id, config in angle_configs.items():
        if node_id in workflow:
            workflow[node_id]["inputs"]["ip_weight"] = config["ip_weight"]
            workflow[node_id]["inputs"]["cn_strength"] = config["cn_strength"]
    
    # 设置 KSampler 参数
    for node_id in sampler_nodes:
        if node_id in workflow:
            workflow[node_id]["inputs"]["denoise"] = denoise
            workflow[node_id]["inputs"]["cfg"] = cfg
            workflow[node_id]["inputs"]["steps"] = steps
    
    # 设置 VAE 色彩校正（如果存在）
    for node_id in ["14_front", "14_back", "14_left", "14_right", "14_side", "14_top"]:
        if node_id in workflow:
            workflow[node_id]["inputs"]["correction_strength"] = correction_strength
    
    # 设置 latent 尺寸
    latent_nodes = ["10_back", "10_left", "10_right", "10_side", "10_top", "20_front"]
    for node_id in latent_nodes:
        if node_id in workflow:
            workflow[node_id]["inputs"]["width"] = width
            workflow[node_id]["inputs"]["height"] = height
    
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
        return (None, None, None, None, None, None, "⚠️ 未获取到图片\n\n请检查 ComfyUI 是否正常运行，以及模型文件是否完整")

# ==================== UI 界面 ====================
def create_ui():
    with gr.Blocks(title="FaceOrbit - 写真模式", theme=gr.themes.Soft(), css="""
        .gradio-container { max-width: 1400px; margin: auto; }
    """) as demo:
        
        gr.Markdown("""
        # 📸 FaceOrbit - 写真模式
        ### 真实感人像生成 | 上传照片，生成专业级人物肖像（6个角度）
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                input_image = gr.Image(label="📸 上传头像照片", type="filepath", height=280)
                gr.Markdown("""
                > 📌 **照片的作用**：决定人物的**面部特征**（脸型、五官、表情）
                > ⚠️ **注意**：请使用清晰、正面、单人的照片，以获得最佳效果
                """)
                
                model_selector = gr.Dropdown(choices=list(MODEL_OPTIONS.keys()), label="🎮 选择模型", value="RealVisXL V5.0 FP16")
                
                # ========== 侧重模式选择 ==========
                priority_mode = gr.Radio(
                    choices=["👤 面部优先 - 强调面部特征一致性", "🏃 姿势优先 - 强调姿态准确性"],
                    label="🎯 生成侧重",
                    value="👤 面部优先 - 强调面部特征一致性",
                    info="面部优先：多角度生成时人脸更像；姿势优先：动作姿态更准确"
                )
                
                # 工作流说明
                workflow_info = gr.HTML(get_workflow_info_html())
                
                # 打开完整指南按钮
                guide_status = gr.Markdown("")
                open_guide_btn = gr.Button("📖 打开完整指南", size="sm", variant="secondary")
                open_guide_btn.click(fn=open_workflow_guide, outputs=[guide_status])
                
                # 动态提示信息
                priority_info = gr.Markdown("")
                
                def update_priority_info(priority):
                    if "面部优先" in priority:
                        return """
                        <div style="background: #e8f4fd; padding: 10px; border-radius: 8px; margin: 5px 0;">
                            <strong>💡 面部优先提示</strong><br>
                            • 脸部不像 → 提高「相似度」<br>
                            • 脸部变形 → 降低「创意度」
                        </div>
                        """
                    else:
                        return """
                        <div style="background: #fef3c7; padding: 10px; border-radius: 8px; margin: 5px 0;">
                            <strong>💡 姿势优先提示</strong><br>
                            • 姿态不对 → 提高「姿态控制」<br>
                            • 确保项目目录有骨架图（front.png、side.png等）
                        </div>
                        """
                
                priority_mode.change(update_priority_info, inputs=[priority_mode], outputs=[priority_info])
                
                with gr.Accordion("📝 各角度提示词设置（仅面部优先模式生效）", open=False):
                    gr.Markdown("> 💡 姿势优先模式会自动使用增强的姿势提示词，此处的设置不会生效")
                    with gr.Tabs():
                        with gr.TabItem("正面"):
                            prompt_front = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["front"], lines=2)
                        with gr.TabItem("背面"):
                            prompt_back = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["back"], lines=2)
                        with gr.TabItem("左四分之三"):
                            prompt_left = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["left"], lines=2)
                        with gr.TabItem("右四分之三"):
                            prompt_right = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["right"], lines=2)
                        with gr.TabItem("侧面"):
                            prompt_side = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["side"], lines=2)
                        with gr.TabItem("顶视"):
                            prompt_top = gr.Textbox(label="正向提示词", value=DEFAULT_PROMPTS["top"], lines=2)
                    
                    negative_prompt = gr.Textbox(label="负向提示词（所有角度共用）", value=DEFAULT_NEGATIVE, lines=3)
                
                with gr.Accordion("⚙️ 生成参数", open=False):
                    with gr.Row():
                        use_fixed_seed = gr.Checkbox(label="🎲 使用固定种子", value=False)
                        fixed_seed_value = gr.Number(value=42, label="种子值", precision=0, visible=False)
                    
                    def toggle_seed_input(checked):
                        return gr.update(visible=checked)
                    use_fixed_seed.change(toggle_seed_input, inputs=[use_fixed_seed], outputs=[fixed_seed_value])
                    
                    ip_weight = gr.Slider(0.5, 1.5, value=1.15, step=0.01, label="🎭 相似度 - 越接近1.5越像照片")
                    cn_strength = gr.Slider(0.0, 0.8, value=0.45, step=0.01, label="🎯 姿态控制")
                    denoise = gr.Slider(0.4, 0.9, value=0.72, step=0.01, label="✨ 创意度")
                    cfg = gr.Slider(4.0, 8.0, value=5.5, step=0.1, label="📝 提示词引导")
                    steps = gr.Slider(20, 50, value=30, step=1, label="🔢 采样步数")
                    correction_strength = gr.Slider(0.0, 1.0, value=0.5, step=0.05, label="🎨 色彩校正")
                    with gr.Row():
                        width = gr.Number(value=832, label="宽度")
                        height = gr.Number(value=1216, label="高度")
                
                # 参数调优指南
                gr.HTML(get_parameter_guide_html())
                
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
                    with gr.TabItem("左四分之三"): out_l = gr.Image()
                    with gr.TabItem("右四分之三"): out_r = gr.Image()
                    with gr.TabItem("侧面"): out_s = gr.Image()
                    with gr.TabItem("顶视"): out_t = gr.Image()
        
        # 模板操作
        def get_params():
            return {
                "model_name": model_selector.value,
                "priority_mode": priority_mode.value,
                "prompt_front": prompt_front.value,
                "prompt_back": prompt_back.value,
                "prompt_left": prompt_left.value,
                "prompt_right": prompt_right.value,
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
                return [gr.update()] * 19
            return [
                params.get("model_name", "RealVisXL V5.0 FP16"),
                params.get("priority_mode", "👤 面部优先 - 强调面部特征一致性"),
                params.get("prompt_front", DEFAULT_PROMPTS["front"]),
                params.get("prompt_back", DEFAULT_PROMPTS["back"]),
                params.get("prompt_left", DEFAULT_PROMPTS["left"]),
                params.get("prompt_right", DEFAULT_PROMPTS["right"]),
                params.get("prompt_side", DEFAULT_PROMPTS["side"]),
                params.get("prompt_top", DEFAULT_PROMPTS["top"]),
                params.get("negative_prompt", DEFAULT_NEGATIVE),
                params.get("use_fixed_seed", False),
                params.get("fixed_seed_value", 42),
                params.get("ip_weight", 1.15),
                params.get("cn_strength", 0.45),
                params.get("denoise", 0.72),
                params.get("cfg", 5.5),
                params.get("steps", 30),
                params.get("correction_strength", 0.5),
                params.get("width", 832),
                params.get("height", 1216)
            ]
        
        save_btn.click(lambda n: save_template(n, get_params()), [template_name], [save_status, template_list])
        load_btn.click(lambda n: set_params(load_template(n)[0]), [template_list], 
            [model_selector, priority_mode, prompt_front, prompt_back, prompt_left, prompt_right, prompt_side, prompt_top,
             negative_prompt, use_fixed_seed, fixed_seed_value,
             ip_weight, cn_strength, denoise, cfg, steps, correction_strength, width, height, load_status])
        delete_btn.click(delete_template, [template_list], [load_status, template_list])
        refresh_btn.click(lambda: gr.Dropdown(choices=list_templates()), outputs=[template_list])
        
        # 生成按钮
        generate_btn.click(
            generate_images,
            [input_image, model_selector, priority_mode, 
             prompt_front, prompt_back, prompt_left, prompt_right, prompt_side, prompt_top,
             negative_prompt, ip_weight, cn_strength, denoise, cfg, steps, 
             correction_strength, width, height, use_fixed_seed, fixed_seed_value],
            [out_f, out_b, out_l, out_r, out_s, out_t, status]
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
    print(f"📁 工作流文件:")
    print(f"   - 姿势优先: {WORKFLOW_POSE_PRIORITY}")
    print(f"   - 面部优先: {WORKFLOW_IDENTITY_PRIORITY}")
    print(f"💡 提示：可根据需求选择「面部优先」或「姿势优先」模式")
    print(f"📖 UI 说明文档: workflow_ui.html")
    
    # 检查工作流文件是否存在
    for wf in [WORKFLOW_POSE_PRIORITY, WORKFLOW_IDENTITY_PRIORITY]:
        if not os.path.exists(wf):
            print(f"⚠️ 工作流文件不存在: {wf}")
    
    open_browser(local_url)
    
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7861,
        theme=gr.themes.Soft()
    )