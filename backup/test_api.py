# test_api.py - 放在 FaceOrbit 目录下运行
import json
import requests
import uuid
import shutil
import os

WORKFLOW_PATH = "workflows/ghostmix_6angles.json"
COMFYUI_API = "http://127.0.0.1:8188"
INPUT_IMAGE = "D:/PixelSmile/FaceOrbit/input/face1.webp"  # 改成你的测试图片路径

# 读取工作流
with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 复制图片到 ComfyUI input 目录
comfyui_input_dir = "D:/PixelSmile/ComfyUI-aki/ComfyUI-aki-v3/ComfyUI/input"
os.makedirs(comfyui_input_dir, exist_ok=True)
local_image_path = os.path.join(comfyui_input_dir, f"test_{uuid.uuid4().hex}.jpg")
shutil.copy2(INPUT_IMAGE, local_image_path)
print(f"📸 图片已复制: {local_image_path}")

# 只修改图片路径
workflow["3"]["inputs"]["image"] = local_image_path

# 发送请求
response = requests.post(f"{COMFYUI_API}/prompt", json={"prompt": workflow})
print(response.json())