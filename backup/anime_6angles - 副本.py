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
import random

# ==================== 配置 ====================
WORKFLOW_PATH = "workflows/anime_6angles.json"
TEMPLATES_DIR = "user_templates"
TEMP_DIR = "temp"
COMFYUI_API = "http://127.0.0.1:8188"
MODEL_OPTIONS = {
    "Animagine XL 3.0": "animagine-xl-3.0.safetensors",
    "Animagine XL 3.1": "animagine-xl-3.1.safetensors"
}

os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# ==================== 负向提示词（必须先定义）====================
DEFAULT_NEGATIVE = "nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, ugly, deformed, grayscale, dull, washed out, desaturated, low contrast"

# ==================== 预设角色库 ====================
PRESET_CHARACTERS = {
    "火影忍者 - 漩涡鸣人": {
        "prompt": "masterpiece, best quality, very aesthetic, 1boy, Naruto Uzumaki, naruto, blonde spiky hair, blue eyes, whisker marks, orange jumpsuit, ninja headband, shuriken, confident smile, action pose, konoha village background",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "金色刺猬头、蓝色眼睛、胡须纹、橙色连体衣、木叶护额"
    },
    "火影忍者 - 宇智波佐助": {
        "prompt": "masterpiece, best quality, very aesthetic, 1boy, Sasuke Uchiha, naruto, black hair, black eyes, sharingan, dark blue shirt, white shorts, ninja headband, cold expression, standing, uchiha clan symbol",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "黑色刺猬头、写轮眼、深蓝色上衣、白色短裤"
    },
    "海贼王 - 蒙奇·D·路飞": {
        "prompt": "masterpiece, best quality, very aesthetic, 1boy, Monkey D Luffy, one piece, black hair, straw hat, red vest, blue shorts, sandals, scar on chest, big smile, rubber powers, sunny background",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "黑色短发、草帽、红色马甲、蓝色短裤、胸前伤疤"
    },
    "海贼王 - 索隆": {
        "prompt": "masterpiece, best quality, very aesthetic, 1boy, Roronoa Zoro, one piece, green hair, bandana, haramaki, three swords, demon aura, muscular, serious expression, dojo background",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "绿色头发、头巾、三刀流、严肃表情"
    },
    "咒术回战 - 五条悟": {
        "prompt": "masterpiece, best quality, very aesthetic, 1boy, Gojo Satoru, jujutsu kaisen, white hair, blindfold, black suit, infinity, six eyes, smug smile, jujutsu high background",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "白发、眼罩、黑色西装、六眼"
    },
    "鬼灭之刃 - 灶门炭治郎": {
        "prompt": "masterpiece, best quality, very aesthetic, 1boy, Kamado Tanjiro, demon slayer, dark red hair, scar on forehead, hanafuda earrings, green checkered haori, water breathing, determined expression",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "深红色头发、额头伤疤、花牌耳饰、绿色格子羽织"
    },
    "鬼灭之刃 - 灶门祢豆子": {
        "prompt": "masterpiece, best quality, very aesthetic, 1girl, Kamado Nezuko, demon slayer, long black hair, pink ribbon, bamboo mouthpiece, pink kimono, demon form, sleeping in box, cute expression",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "黑色长发、粉色丝带、竹筒嘴、粉色和服"
    },
    "进击的巨人 - 利威尔兵长": {
        "prompt": "masterpiece, best quality, very aesthetic, 1boy, Levi Ackerman, attack on titan, black hair, undercut, cravat, survey corps uniform, ODM gear, cold eyes, cleaning, titan background",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "黑色短发、领巾、调查兵团制服、立体机动装置"
    },
    "死神 - 黑崎一护": {
        "prompt": "masterpiece, best quality, very aesthetic, 1boy, Ichigo Kurosaki, bleach, orange hair, substitute shinigami badge, zangetsu, bankai, hollow mask, soul reaper uniform, determined",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "橙色头发、斩魄刀、代理死神徽章"
    },
    "新海诚风格 - 原创角色": {
        "prompt": "masterpiece, best quality, very aesthetic, 1girl, shinkai style, makoto shinkai, your name style, realistic background, clouds, sunset, beautiful sky, emotional, detailed",
        "negative": DEFAULT_NEGATIVE + ", deformed, ugly, bad anatomy",
        "description": "新海诚电影风格：真实系背景、美丽天空、情感氛围"
    }
}

# ==================== 预设角度提示词 ====================
PRESET_ANGLE_PROMPTS = {
    "front": "front view, looking at viewer, facing camera, centered, symmetrical face",
    "back": "from behind, back view, looking away from camera, back of head visible, from rear",
    "side": "side view, profile shot, facing left, one eye visible, side profile, three quarter face",
    "threequarter": "three quarter view, 3/4 pose, turned slightly right, looking at camera",
    "rightfront": "facing right, looking right, right side angle, angled right",
    "top": "looking up, from below, low angle, looking upward, worm's eye view"
}

# ==================== 各角度默认提示词（高级模式专用）====================
DEFAULT_PROMPTS = {
    "front": "masterpiece, best quality, very aesthetic, 1girl, solo, upper body, plain background, vibrant, high saturation, colorful, bright, detailed face",
    "back": "masterpiece, best quality, very aesthetic, 1girl, from behind, back view, looking away, solo, upper body, plain background, vibrant, high saturation, colorful",
    "side": "masterpiece, best quality, very aesthetic, 1girl, side view, profile, facing left, solo, upper body, plain background, vibrant, high saturation, colorful",
    "threequarter": "masterpiece, best quality, very aesthetic, 1girl, three quarter view, 3/4 pose, turned slightly, looking at camera, solo, upper body, plain background",
    "rightfront": "masterpiece, best quality, very aesthetic, 1girl, facing right, looking right, right side, angled right, solo, upper body, plain background",
    "top": "masterpiece, best quality, very aesthetic, 1girl, looking up, from below, low angle, looking upward, worm's eye view, solo, upper body, plain background"
}

# ==================== 模板管理 ====================
def save_template(name, params):
    if not name:
        return "❌ 请输入模板名称", gr.Dropdown(choices=list_templates())
    
    template_file = os.path.join(TEMPLATES_DIR, f"{name}.json")
    template_data = {
        "name": name,
        "params": params,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(template_file, "w", encoding="utf-8") as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    return f"✅ 模板「{name}」已保存", gr.Dropdown(choices=list_templates())

def load_template(name):
    template_file = os.path.join(TEMPLATES_DIR, f"{name}.json")
    
    if not os.path.exists(template_file):
        return None, f"❌ 模板「{name}」不存在"
    
    with open(template_file, "r", encoding="utf-8") as f:
        template_data = json.load(f)
    
    params = template_data["params"]
    return params, f"✅ 已加载模板「{name}」"

def list_templates():
    templates = []
    for file in os.listdir(TEMPLATES_DIR):
        if file.endswith(".json"):
            templates.append(file.replace(".json", ""))
    return templates

def delete_template(name):
    template_file = os.path.join(TEMPLATES_DIR, f"{name}.json")
    if os.path.exists(template_file):
        os.remove(template_file)
        return f"✅ 已删除模板「{name}」", gr.Dropdown(choices=list_templates())
    return f"❌ 模板「{name}」不存在", gr.Dropdown(choices=list_templates())

# ==================== 保存图片到项目目录 ====================
def save_images_to_project(images, prefix="anime"):
    """保存图片到项目 output 目录"""
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    angle_names = ["front", "back", "side", "threequarter", "rightfront", "top"]
    saved_paths = []
    
    for i, (img, angle) in enumerate(zip(images, angle_names)):
        if img is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{angle}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)
            img.save(filepath)
            print(f"💾 已保存: {filepath}")
            saved_paths.append(filepath)
    
    return saved_paths

# ==================== ComfyUI API 调用（无限等待版）====================
def run_comfyui_workflow(workflow, progress):
    """发送工作流到 ComfyUI 并获取图片（无超时限制）"""
    
    progress(0.7, desc="发送到 ComfyUI...")
    
    try:
        response = requests.post(
            f"{COMFYUI_API}/prompt",
            json={"prompt": workflow},
            timeout=60
        )
        
        if response.status_code != 200:
            error_msg = response.text
            print(f"API 错误详情: {error_msg}")
            return [None] * 6, f"❌ API 错误: {error_msg}"
        
        data = response.json()
        prompt_id = data.get("prompt_id")
        
        if not prompt_id:
            return [None] * 6, "❌ 未获取到 prompt_id"
        
        print(f"✅ 工作流已提交，prompt_id: {prompt_id}")
        progress(0.8, desc=f"生成中... 请耐心等待 (ID: {prompt_id[:8]})")
        
        elapsed_seconds = 0
        last_status_update = 0
        
        while True:
            try:
                resp = requests.get(f"{COMFYUI_API}/history/{prompt_id}", timeout=10)
                if resp.status_code == 200:
                    history = resp.json()
                    if prompt_id in history:
                        outputs = history[prompt_id]["outputs"]
                        print(f"✅ 收到输出，节点: {list(outputs.keys())}")
                        
                        # 动态查找所有图片输出
                        images = []
                        for node_id, node_output in outputs.items():
                            if "images" in node_output and node_output["images"]:
                                for img_info in node_output["images"]:
                                    img_data = requests.get(
                                        f"{COMFYUI_API}/view",
                                        params={"filename": img_info["filename"], "subfolder": img_info.get("subfolder", "")}
                                    )
                                    if img_data.status_code == 200:
                                        img = Image.open(io.BytesIO(img_data.content))
                                        images.append(img)
                                        print(f"🖼️ 获取图片: {node_id} -> {img_info['filename']}")
                        
                        if images:
                            # 保存到项目目录
                            saved_paths = save_images_to_project(images, "anime")
                            status_msg = f"✅ 生成完成！共 {len(images)} 张图片"
                            if saved_paths:
                                status_msg += f"\n💾 已保存到项目 output 目录"
                            return images, status_msg
                        else:
                            print("⚠️ 未找到图片输出，请检查工作流")
                            return [None] * 6, "⚠️ 未获取到图片，请检查工作流输出节点"
            except Exception as e:
                print(f"查询历史时出错: {e}")
            
            elapsed_seconds += 5
            if elapsed_seconds - last_status_update >= 10:
                last_status_update = elapsed_seconds
                minutes = elapsed_seconds // 60
                seconds = elapsed_seconds % 60
                progress(0.8 + min(elapsed_seconds / 300, 0.15), desc=f"生成中... 已等待 {minutes}分{seconds}秒")
            
            time.sleep(5)
        
    except requests.exceptions.ConnectionError:
        return [None] * 6, f"❌ 无法连接 ComfyUI API\n请确保 ComfyUI 已启动并添加 --listen 参数"
    except Exception as e:
        print(f"异常详情: {e}")
        return [None] * 6, f"❌ 运行失败: {str(e)}"

# ==================== 生成函数 ====================
def generate_images(
    input_image,
    model_name,
    preset_character,
    use_preset_angles,
    prompt_front,
    prompt_back,
    prompt_side,
    prompt_threequarter,
    prompt_rightfront,
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
    timeout_minutes,
    progress=gr.Progress()
):
    if input_image is None:
        return [None] * 6, "❌ 请先上传头像照片"
    
    if not os.path.exists(WORKFLOW_PATH):
        return [None] * 6, f"❌ 工作流文件不存在: {WORKFLOW_PATH}"
    
    progress(0.1, desc="加载工作流模板...")
    
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        workflow = json.load(f)
    
    progress(0.3, desc="配置参数...")
    
    # 1. 保存上传的图片到项目目录（避免 Gradio 临时文件问题）
    import shutil
    temp_image_dir = os.path.join(os.path.dirname(__file__), "temp", "uploaded_images")
    os.makedirs(temp_image_dir, exist_ok=True)
    
    local_image_path = os.path.join(temp_image_dir, f"input_{uuid.uuid4().hex}.jpg")
    shutil.copy2(input_image, local_image_path)
    print(f"📸 图片已复制到: {local_image_path}")
    
    # 2. 修改工作流中的图片路径
    workflow["3"]["inputs"]["image"] = local_image_path
    
    # 3. 修改模型
    selected_model = MODEL_OPTIONS.get(model_name, "animagine-xl-3.1.safetensors")
    workflow["1"]["inputs"]["ckpt_name"] = selected_model
    
    # 4. 简化为只测试正面图（先确保一张图能工作）
    # 先用默认提示词
    test_prompt = "masterpiece, best quality, very aesthetic, 1boy, front view, solo, plain background"
    workflow["7_front"]["inputs"]["text"] = test_prompt
    
    # 5. 保存调试文件
    debug_path = os.path.join(TEMP_DIR, f"debug_workflow_{int(time.time())}.json")
    with open(debug_path, "w", encoding="utf-8") as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    print(f"📁 调试工作流已保存: {debug_path}")
    
    progress(0.5, desc="连接到 ComfyUI...")
    
    # 6. 调用 API
    images, status = run_comfyui_workflow(workflow, progress)
    
    if not images or len(images) != 6:
        images = [None] * 6
    
    return images[0], images[1], images[2], images[3], images[4], images[5], status

# ==================== UI 界面 ====================
def create_ui():
    with gr.Blocks(title="FaceOrbit - 动漫AI形象生成器", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🎨 FaceOrbit - 动漫AI形象生成器
        ### 上传照片，生成属于你的动漫角色形象
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                input_image = gr.Image(label="📸 上传头像照片", type="filepath", height=250)
                
                gr.Markdown("""
                > 📌 **照片的作用**：决定角色的**面部特征**（脸型、五官、表情）
                > 
                > ✨ **照片不影响**：服装、背景、姿势、角度（由下方提示词控制）
                """)
                
                model_selector = gr.Dropdown(
                    choices=list(MODEL_OPTIONS.keys()),
                    label="🎮 选择模型",
                    value="Animagine XL 3.1"
                )
                
                mode_selector = gr.Radio(
                    choices=["🎮 体验模式 - 快速体验预设角色", "⚙️ 高级模式 - 自定义所有参数"],
                    label="选择模式",
                    value="🎮 体验模式 - 快速体验预设角色",
                    interactive=True
                )
                
                # ========== 体验模式界面 ==========
                with gr.Group(visible=True) as easy_mode_group:
                    gr.Markdown("### 🎮 体验模式")
                    gr.Markdown("选择你喜欢的动漫角色，一键生成！")
                    
                    preset_character = gr.Dropdown(
                        choices=["无（使用自定义提示词）"] + list(PRESET_CHARACTERS.keys()),
                        label="🎭 选择预设角色",
                        value="火影忍者 - 漩涡鸣人"
                    )
                    
                    character_description = gr.Markdown(
                        value=f"**角色描述**：{PRESET_CHARACTERS['火影忍者 - 漩涡鸣人']['description']}"
                    )
                    
                    def update_description(choice):
                        if choice in PRESET_CHARACTERS:
                            return f"**角色描述**：{PRESET_CHARACTERS[choice]['description']}"
                        return "**角色描述**：使用自定义提示词"
                    
                    preset_character.change(update_description, inputs=[preset_character], outputs=[character_description])
                    
                    use_preset_angles = gr.Checkbox(
                        label="🎯 使用预设角度提示词（推荐）",
                        value=True,
                        info="勾选后，6个角度会自动使用不同的视角描述"
                    )
                    
                    gr.Markdown("---\n**💡 提示**：体验模式下，以下高级参数仍然可以调整")
                
                # ========== 高级模式界面（始终保持定义）==========
                with gr.Group(visible=False) as advanced_mode_group:
                    gr.Markdown("### ⚙️ 高级模式")
                    gr.Markdown("自定义每个角度的提示词，精细控制生成效果")
                    
                    with gr.Tabs():
                        with gr.TabItem("正面"):
                            prompt_front = gr.Textbox(
                                label="正向提示词",
                                value=DEFAULT_PROMPTS["front"],
                                lines=3
                            )
                        with gr.TabItem("背面"):
                            prompt_back = gr.Textbox(
                                label="正向提示词",
                                value=DEFAULT_PROMPTS["back"],
                                lines=3
                            )
                        with gr.TabItem("侧面"):
                            prompt_side = gr.Textbox(
                                label="正向提示词",
                                value=DEFAULT_PROMPTS["side"],
                                lines=3
                            )
                        with gr.TabItem("四分之三"):
                            prompt_threequarter = gr.Textbox(
                                label="正向提示词",
                                value=DEFAULT_PROMPTS["threequarter"],
                                lines=3
                            )
                        with gr.TabItem("右前"):
                            prompt_rightfront = gr.Textbox(
                                label="正向提示词",
                                value=DEFAULT_PROMPTS["rightfront"],
                                lines=3
                            )
                        with gr.TabItem("顶视"):
                            prompt_top = gr.Textbox(
                                label="正向提示词",
                                value=DEFAULT_PROMPTS["top"],
                                lines=3
                            )
                    
                    negative_prompt_adv = gr.Textbox(
                        label="负向提示词（所有角度共用）",
                        value=DEFAULT_NEGATIVE,
                        lines=3
                    )
                
                # ========== 在体验模式组外部定义高级模式的变量（关键！）==========
                # 这样即使高级模式组不可见，变量也存在
                with gr.Group(visible=True):
                    prompt_front = gr.Textbox(value=DEFAULT_PROMPTS["front"], visible=False)
                    prompt_back = gr.Textbox(value=DEFAULT_PROMPTS["back"], visible=False)
                    prompt_side = gr.Textbox(value=DEFAULT_PROMPTS["side"], visible=False)
                    prompt_threequarter = gr.Textbox(value=DEFAULT_PROMPTS["threequarter"], visible=False)
                    prompt_rightfront = gr.Textbox(value=DEFAULT_PROMPTS["rightfront"], visible=False)
                    prompt_top = gr.Textbox(value=DEFAULT_PROMPTS["top"], visible=False)
                    negative_prompt_adv = gr.Textbox(value=DEFAULT_NEGATIVE, visible=False)
                
                # 模式切换时，同步更新隐藏变量的值
                def sync_prompts(mode, adv_front, adv_back, adv_side, adv_threequarter, adv_rightfront, adv_top, adv_negative):
                    is_advanced = mode == "⚙️ 高级模式 - 自定义所有参数"
                    if is_advanced:
                        # 高级模式：使用用户输入的值
                        return adv_front, adv_back, adv_side, adv_threequarter, adv_rightfront, adv_top, adv_negative
                    else:
                        # 体验模式：使用默认值（会被 generate 函数中的预设覆盖）
                        return DEFAULT_PROMPTS["front"], DEFAULT_PROMPTS["back"], DEFAULT_PROMPTS["side"], DEFAULT_PROMPTS["threequarter"], DEFAULT_PROMPTS["rightfront"], DEFAULT_PROMPTS["top"], DEFAULT_NEGATIVE
                
                # 通用高级参数
                with gr.Accordion("⚙️ 生成参数（两种模式通用）", open=False):
                    # ... 保持不变 ...
                    ip_weight = gr.Slider(0.5, 1.0, value=0.8, step=0.01, label="🎭 相似度")
                    cn_strength = gr.Slider(0.0, 0.8, value=0.35, step=0.01, label="🎯 姿态控制")
                    denoise = gr.Slider(0.5, 0.9, value=0.7, step=0.01, label="✨ 创意度")
                    cfg = gr.Slider(1.0, 10.0, value=6.5, step=0.1, label="📝 提示词引导")
                    steps = gr.Slider(20, 50, value=28, step=1, label="🔢 采样步数")
                    correction_strength = gr.Slider(0.0, 1.0, value=0.65, step=0.05, label="🎨 色彩校正")
                    with gr.Row():
                        width = gr.Number(value=832, label="📐 宽度", precision=0)
                        height = gr.Number(value=1216, label="📐 高度", precision=0)
                
                # 模板管理
                with gr.Accordion("💾 模板管理", open=False):
                    # ... 保持不变 ...
                    with gr.Row():
                        template_name = gr.Textbox(label="模板名称", placeholder="我的日系风格", scale=2)
                        save_btn = gr.Button("💾 保存", scale=1)
                    save_status = gr.Markdown("")
                    
                    with gr.Row():
                        template_list = gr.Dropdown(label="选择模板", choices=list_templates(), scale=2)
                        load_btn = gr.Button("📂 加载", scale=1)
                        delete_btn = gr.Button("🗑️ 删除", scale=1)
                    load_status = gr.Markdown("")
                    refresh_btn = gr.Button("🔄 刷新", size="sm")
                    
                    timeout_value = gr.Number(value=5, label="⏰ 超时时间（分钟）", precision=0, minimum=1, maximum=30)
                
                generate_btn = gr.Button("🚀 开始生成", variant="primary", size="lg")
                status = gr.Markdown("")
            
            # 输出区域（保持不变）
            with gr.Column(scale=1):
                gr.Markdown("### ✨ 生成结果（6个角度）")
                with gr.Tabs():
                    with gr.TabItem("正面"):
                        output_front = gr.Image(label="正面")
                    with gr.TabItem("背面"):
                        output_back = gr.Image(label="背面")
                    with gr.TabItem("侧面"):
                        output_side = gr.Image(label="侧面")
                    with gr.TabItem("四分之三"):
                        output_threequarter = gr.Image(label="四分之三")
                    with gr.TabItem("右前"):
                        output_rightfront = gr.Image(label="右前")
                    with gr.TabItem("顶视"):
                        output_top = gr.Image(label="顶视")
        
        # ========== 模式切换逻辑 ==========
        def switch_mode(mode):
            is_easy = mode == "🎮 体验模式 - 快速体验预设角色"
            return gr.update(visible=is_easy), gr.update(visible=not is_easy)
        
        mode_selector.change(switch_mode, inputs=[mode_selector], outputs=[easy_mode_group, advanced_mode_group])
        
        # 当高级模式中的输入变化时，同步到隐藏变量
        def on_advanced_input_change(front, back, side, threequarter, rightfront, top, negative):
            return front, back, side, threequarter, rightfront, top, negative
        
        # 绑定高级模式输入变化事件
        prompt_front.change(on_advanced_input_change, 
            inputs=[prompt_front, prompt_back, prompt_side, prompt_threequarter, prompt_rightfront, prompt_top, negative_prompt_adv],
            outputs=[prompt_front, prompt_back, prompt_side, prompt_threequarter, prompt_rightfront, prompt_top, negative_prompt_adv])
        
        # 保存模板（简化）
        def get_current_params():
            return {
                "model_name": model_selector.value,
                "prompt_front": prompt_front.value,
                "prompt_back": prompt_back.value,
                "prompt_side": prompt_side.value,
                "prompt_threequarter": prompt_threequarter.value,
                "prompt_rightfront": prompt_rightfront.value,
                "prompt_top": prompt_top.value,
                "negative_prompt": negative_prompt_adv.value,
                "ip_weight": ip_weight.value,
                "cn_strength": cn_strength.value,
                "denoise": denoise.value,
                "cfg": cfg.value,
                "steps": steps.value,
                "correction_strength": correction_strength.value,
                "width": width.value,
                "height": height.value
            }
        
        save_btn.click(
            lambda name: save_template(name, get_current_params()),
            inputs=[template_name],
            outputs=[save_status, template_list]
        )
        
        # 加载模板
        def set_from_params(params):
            if params is None:
                return [gr.update()] * 16
            return [
                params.get("model_name", "Animagine XL 3.1"),
                params.get("prompt_front", DEFAULT_PROMPTS["front"]),
                params.get("prompt_back", DEFAULT_PROMPTS["back"]),
                params.get("prompt_side", DEFAULT_PROMPTS["side"]),
                params.get("prompt_threequarter", DEFAULT_PROMPTS["threequarter"]),
                params.get("prompt_rightfront", DEFAULT_PROMPTS["rightfront"]),
                params.get("prompt_top", DEFAULT_PROMPTS["top"]),
                params.get("negative_prompt", DEFAULT_NEGATIVE),
                params.get("ip_weight", 0.8),
                params.get("cn_strength", 0.35),
                params.get("denoise", 0.7),
                params.get("cfg", 6.5),
                params.get("steps", 28),
                params.get("correction_strength", 0.65),
                params.get("width", 832),
                params.get("height", 1216)
            ]
        
        load_btn.click(
            lambda name: set_from_params(load_template(name)[0]) if load_template(name)[0] else [gr.update()] * 16,
            inputs=[template_list],
            outputs=[model_selector, prompt_front, prompt_back, prompt_side, prompt_threequarter, prompt_rightfront, prompt_top, negative_prompt_adv, ip_weight, cn_strength, denoise, cfg, steps, correction_strength, width, height, load_status]
        )
        
        delete_btn.click(delete_template, inputs=[template_list], outputs=[load_status, template_list])
        refresh_btn.click(lambda: gr.Dropdown(choices=list_templates()), outputs=[template_list])
        
        # 生成事件
        generate_btn.click(
            generate_images,
            inputs=[
                input_image, model_selector,
                preset_character, use_preset_angles,
                prompt_front, prompt_back, prompt_side, prompt_threequarter, prompt_rightfront, prompt_top,
                negative_prompt_adv, ip_weight, cn_strength, denoise, cfg, steps, correction_strength, width, height,
                timeout_value
            ],
            outputs=[output_front, output_back, output_side, output_threequarter, output_rightfront, output_top, status]
        )
    
    return demo

# ==================== 启动 ====================
def open_browser(url, delay=1.5):
    threading.Timer(delay, lambda: webbrowser.open(url)).start()

if __name__ == "__main__":
    demo = create_ui()
    local_url = "http://127.0.0.1:7860"
    
    print(f"🚀 正在启动 FaceOrbit...")
    print(f"📍 本地地址: {local_url}")
    print(f"🔧 ComfyUI API 地址: {COMFYUI_API}")
    
    open_browser(local_url)
    
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860
    )