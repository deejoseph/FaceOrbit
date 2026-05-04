from __future__ import annotations

import base64
import json
import shutil
import threading
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request
from PIL import Image


PROJECT_ROOT = Path(r"D:\PixelSmile\FaceOrbit")
# 改成秋叶包 V3 的路径
COMFY_ROOT = Path(r"D:\PixelSmile\ComfyUI-aki\ComfyUI-aki-v3")
COMFY_INPUT = COMFY_ROOT / "ComfyUI" / "input"
COMFY_OUTPUT = COMFY_ROOT / "ComfyUI" / "output"
WORKFLOW_TEMPLATE = PROJECT_ROOT / "FaceOrbit_workflow.json"
PROJECT_INPUT = PROJECT_ROOT / "input"
PROJECT_JOBS = PROJECT_ROOT / "output" / "jobs"
PROJECT_TOTAL = PROJECT_ROOT / "output" / "total"
PROJECT_SINGLE = PROJECT_ROOT / "output" / "single"
PROJECT_SHEETS = PROJECT_ROOT / "output" / "contact_sheets"
PROJECT_LOGS = PROJECT_ROOT / "logs"
COMFY_API = "http://127.0.0.1:8188"


FIXED_VIEW_ANGLES = {
    "正面主视": {"horizontal": 0, "vertical": 10},
    "背面视图": {"horizontal": 180, "vertical": 10},
    "顶视图": {"horizontal": 0, "vertical": 75},
    "四分之三视图": {"horizontal": 45, "vertical": 15},
    "侧视图": {"horizontal": 90, "vertical": 10},
    "正面": {"horizontal": 0, "vertical": 0},
    "左前": {"horizontal": 315, "vertical": 6},
    "右前": {"horizontal": 45, "vertical": 6},
    "侧面": {"horizontal": 90, "vertical": 0},
    "背面": {"horizontal": 160, "vertical": 0},
    "俯视": {"horizontal": 0, "vertical": 35},
    "正立面": {"horizontal": 0, "vertical": 0},
    "侧立面": {"horizontal": 90, "vertical": 6},
    "背立面": {"horizontal": 180, "vertical": 6},
    "鸟瞰": {"horizontal": 0, "vertical": 55},
}

def get_fixed_angle(view_name: str) -> tuple[int, int]:
    angle = FIXED_VIEW_ANGLES.get(view_name, {"horizontal": 0, "vertical": 10})
    return angle["horizontal"], angle["vertical"]

MODE_PRESETS = {
    "Celadon": {
        "prompt": "celadon ceramic vessel, museum-grade product photography, glossy green glaze, fine crackle texture, clean neutral background, soft studio lighting, same exact object, coherent camera orbit, one intact vessel only, spout body arch-handle lid and knob must stay attached and rotate together, highly detailed",
        "negative": "deformed vessel, repeated viewpoint, duplicate object, detached spout, detached handle, misaligned arch handle, wrong spout attachment, floating lid, broken ceramic, asymmetrical body, blur, low quality",
        "views": [
            {"name": "正面主视", "zoom": 1.5, "steps": 24, "cfg": 2.2},
            {"name": "背面视图", "zoom": 1.35, "steps": 36, "cfg": 2.4},
            {"name": "顶视图", "zoom": 1.5, "steps": 20, "cfg": 1.8},
            {"name": "四分之三视图", "zoom": 2.2, "steps": 28, "cfg": 2.0},
            {"name": "侧视图", "zoom": 1.5, "steps": 24, "cfg": 2.2},
        ],
    },
    "Pet": {
        "prompt": "same pet, realistic animal portrait, consistent fur pattern, clean studio background, soft natural lighting, coherent camera orbit, stable anatomy, detailed eyes and fur, identity preserved, high fidelity, 4K",
        "negative": "extra limbs, deformed anatomy, duplicate body parts, wrong fur pattern, mismatched face, blurry eyes, deformed ears, low quality, blur, cartoon, illustration",
        "views": [
            {"name": "正面", "zoom": 1.2, "steps": 28, "cfg": 2.8},
            {"name": "左前", "zoom": 1.2, "steps": 28, "cfg": 2.8},
            {"name": "右前", "zoom": 1.2, "steps": 28, "cfg": 2.8},
            {"name": "侧面", "zoom": 1.1, "steps": 28, "cfg": 2.6},
            {"name": "背面", "zoom": 1.0, "steps": 28, "cfg": 2.5},
            {"name": "俯视", "zoom": 1.1, "steps": 28, "cfg": 2.6},
        ],
    },
    "Human": {
        "prompt": "same person, realistic full body portrait, consistent face identity and body shape, clean editorial background, soft cinematic lighting, coherent camera orbit around the entire body, stable anatomy, detailed hair and fabric, full body rotates together, high fidelity, professional photography, 4K",
        "negative": "bad anatomy, deformed face, mismatched limbs, duplicate body parts, blurry face, wrong eyes, extra fingers, deformed hands, torso facing wrong direction, head turned but body facing forward, low quality, blur, cartoon",
        "views": [
            {"name": "正面", "zoom": 0.85, "steps": 40, "cfg": 3.2},
            {"name": "左前", "zoom": 1.3, "steps": 35, "cfg": 3.0},
            {"name": "右前", "zoom": 1.3, "steps": 35, "cfg": 3.0},
            {"name": "侧面", "zoom": 1.2, "steps": 32, "cfg": 3.0},
            {"name": "背面", "zoom": 1.2, "steps": 32, "cfg": 3.0},
            {"name": "俯视", "zoom": 1.1, "steps": 28, "cfg": 3.0},
        ],
    },
    "Industrial": {
        "prompt": "industrial structure, engineered surfaces, technical product render, clean background, precise geometry, hard-surface detailing, controlled reflections, coherent camera orbit, structural consistency, high detail, 4K, sharp edges",
        "negative": "warped geometry, broken structure, detached parts, extra parts, soft edges, blurry reflections, low quality, blur, unrealistic materials, cartoon",
        "views": [
            {"name": "正面", "zoom": 0.9, "steps": 40, "cfg": 1.8},
            {"name": "左前", "zoom": 0.9, "steps": 35, "cfg": 1.8},
            {"name": "右前", "zoom": 0.9, "steps": 35, "cfg": 1.8},
            {"name": "侧面", "zoom": 0.85, "steps": 35, "cfg": 1.8},
            {"name": "背面", "zoom": 0.85, "steps": 35, "cfg": 1.8},
            {"name": "俯视", "zoom": 0.8, "steps": 30, "cfg": 1.8},
        ],
    },
    "Architecture": {
        "prompt": "architectural subject, professional archviz, clean facade lines, balanced daylight, realistic materials, stable geometry, coherent camera orbit, controlled perspective, detailed surfaces, high detail, 4K, sharp lines, realistic shadows",
        "negative": "warped building, broken facade, impossible perspective, distorted geometry, blurry textures, low quality, blur, cartoon, unrealistic lighting",
        "views": [
            {"name": "正立面", "zoom": 0.9, "steps": 32, "cfg": 2.2},
            {"name": "左前", "zoom": 0.85, "steps": 32, "cfg": 2.2},
            {"name": "右前", "zoom": 0.85, "steps": 32, "cfg": 2.2},
            {"name": "侧立面", "zoom": 0.9, "steps": 32, "cfg": 2.2},
            {"name": "背立面", "zoom": 0.9, "steps": 32, "cfg": 2.2},
            {"name": "鸟瞰", "zoom": 0.8, "steps": 32, "cfg": 2.2},
        ],
    },
}

JOBS: dict[str, dict] = {}

def ensure_dirs() -> None:
    for p in [PROJECT_JOBS, PROJECT_INPUT, PROJECT_TOTAL, PROJECT_SINGLE, PROJECT_SHEETS, PROJECT_LOGS]:
        p.mkdir(parents=True, exist_ok=True)
    COMFY_INPUT.mkdir(parents=True, exist_ok=True)

def json_response(handler: SimpleHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)

def decode_data_url(data_url: str) -> bytes:
    if "," not in data_url:
        raise ValueError("invalid image payload")
    return base64.b64decode(data_url.split(",", 1)[1])

def normalize_views(mode: str, payload_views: list[dict] | None) -> list[dict]:
    if payload_views is not None:
        base = payload_views
        print(f"[DEBUG] Using {len(base)} views from frontend")
    else:
        base = MODE_PRESETS[mode]["views"]
        print(f"[DEBUG] Using {len(base)} views from preset")
    views = []
    for idx, view in enumerate(base):
        horizontal, vertical = get_fixed_angle(view.get("name", f"view_{idx+1}"))
        views.append({
            "index": idx + 1,
            "name": view.get("name", f"view_{idx+1}"),
            "horizontal": horizontal,
            "vertical": vertical,
            "zoom": float(view.get("zoom", 1.0)),
            "steps": int(view.get("steps", 24)),
            "cfg": float(view.get("cfg", 2.0)),
        })
        print(f"[DEBUG] View {idx+1}: {views[-1]['name']} steps={views[-1]['steps']} cfg={views[-1]['cfg']} zoom={views[-1]['zoom']}")
    return views

def build_prompt_for_view(view_name: str, horizontal: int, vertical: int, zoom: float, mode: str = "Celadon") -> str:
    angle_desc = f"horizontal angle {horizontal} degrees, vertical angle {vertical} degrees"
    view_desc_map = {
        "正面": "front view",
        "左前": "front-left quarter view",
        "右前": "front-right quarter view",
        "侧面": "side view",
        "背面": "back view",
        "俯视": "top-down view",
        "正立面": "front elevation",
        "侧立面": "side elevation",
        "背立面": "back elevation",
        "鸟瞰": "bird's eye view",
    }
    
    # ========== Celadon 模式（已有详细描述）==========
    if mode == "Celadon":
        prompts = {
            "正面主视": f"Turn the camera to a front view, {angle_desc}, zoom level {zoom}. Show the front of the celadon porcelain product centered in frame.",
            "背面视图": f"Turn the camera to a back view, {angle_desc}, zoom level {zoom}. Show the back of the celadon porcelain product centered in frame.",
            "顶视图": f"Turn the camera to a top-down view, {angle_desc}, zoom level {zoom}. Show the top of the celadon porcelain product centered in frame.",
            "四分之三视图": f"Turn the camera to a three-quarter view, {angle_desc}, zoom level {zoom}. Show the celadon porcelain product from a dynamic angle centered in frame.",
            "侧视图": f"Turn the camera to a side view, {angle_desc}, zoom level {zoom}. Show the side profile of the celadon porcelain product centered in frame.",
        }
        base_prompt = prompts.get(view_name, prompts.get("正面主视"))
        return base_prompt + " Keep the same celadon glaze, shape, and material properties. celadon porcelain product photo, premium ceramic object, consistent object, clean background, 4K, high resolution"
    
    # ========== Human 模式（详细描述每个视角）==========
    if mode == "Human":
        if view_name == "正面":
            return f"Turn the camera to front view, {angle_desc}, zoom level {zoom}. Show the full body of the same person from head to toe. Natural face expression, symmetrical face, realistic skin texture, no distortion. Keep the same face identity, body shape, clothing. Professional full-body portrait photography, clean background, 4K, high resolution."
        elif view_name == "左前":
            return f"Turn the camera to front-left quarter view, {angle_desc}, zoom level {zoom}. Show the person from the left front angle. The body and head should be turned slightly to the left, revealing the left side of the face and body. Keep the same face identity, body shape, clothing. Professional portrait photography, clean background, 4K, high resolution."
        elif view_name == "右前":
            return f"Turn the camera to front-right quarter view, {angle_desc}, zoom level {zoom}. Show the person from the right front angle. The body and head should be turned slightly to the right, revealing the right side of the face and body. Keep the same face identity, body shape, clothing. Professional portrait photography, clean background, 4K, high resolution."
        elif view_name == "侧面":
            return f"Turn the camera to side view, {angle_desc}, zoom level {zoom}. Show the person in strict profile. Only one eye is visible, and the body shows the full side silhouette. Keep the same face identity, body shape, clothing. Professional portrait photography, clean background, 4K, high resolution."
        elif view_name == "背面":
            return f"Turn the camera to back view, {angle_desc}, zoom level {zoom}. Show the person from behind. The face is not visible; focus on the back of the head, shoulders, and back. Keep the same hair style, body shape, clothing. Professional portrait photography, clean background, 4K, high resolution."
        elif view_name == "俯视":
            return f"Turn the camera to top-down view, {angle_desc}, zoom level {zoom}. Show the person from above looking down. The top of the head, shoulders, and arms are visible. Keep the same hair style, clothing. Professional photography, clean background, 4K, high resolution."
        else:
            view_desc = view_desc_map.get(view_name, "view")
            return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same person from this angle. Keep the same face identity, body shape, clothing. Professional portrait photography, clean background, 4K, high resolution."
    
    # ========== Pet 模式（已优化）==========
    if mode == "Pet":
        if view_name == "正面":
            return f"Turn the camera to front view, {angle_desc}, zoom level {zoom}. Show the pet directly facing the camera, symmetrical face, both eyes visible. Keep the same fur pattern and face markings. Clean studio background, soft lighting, 4K, high resolution."
        elif view_name == "左前":
            return f"Turn the camera to front-left quarter view, {angle_desc}, zoom level {zoom}. Show the pet from the left front angle, with the body and head turned to the left. The left side of the face and body should be clearly visible. The right eye may be partially hidden. Keep the same fur pattern and markings. Clean studio background, soft lighting, 4K, high resolution."
        elif view_name == "右前":
            return f"Turn the camera to front-right quarter view, {angle_desc}, zoom level {zoom}. Show the pet from the right front angle, with the body and head turned to the right. The right side of the face and body should be clearly visible. Keep the same fur pattern and markings. Clean studio background, soft lighting, 4K, high resolution."
        elif view_name == "侧面":
            return f"Turn the camera to side view, {angle_desc}, zoom level {zoom}. Show the pet in strict profile, only one eye visible, the body showing the full side silhouette. Keep the same fur pattern and body shape. Clean studio background, soft lighting, 4K, high resolution."
        elif view_name == "背面":
            return f"Turn the camera to back view, {angle_desc}, zoom level {zoom}. Show the pet from behind, looking at the back of the head and body. The face is not visible. Keep the same fur pattern and markings. Clean studio background, soft lighting, 4K, high resolution."
        elif view_name == "俯视":
            return f"Turn the camera to top-down view, {angle_desc}, zoom level {zoom}. Show the pet from above, looking down onto the back, head, and body. The face is partially visible but mostly the top of the head. Keep the same fur pattern and body shape. Clean studio background, soft lighting, 4K, high resolution."
        else:
            view_desc = view_desc_map.get(view_name, "view")
            return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same pet from this angle. Keep the same fur pattern, face markings, and body shape. The pet's head and body rotate together. Clean studio background, soft lighting, 4K, high resolution."
    
    # ========== Industrial 模式（详细描述）==========
    if mode == "Industrial":
        if view_name == "正面":
            return f"Turn the camera to front view, {angle_desc}, zoom level {zoom}. Show the industrial object directly facing the camera. The front face, control panels, and main features must be centered. Keep the exact same geometry, surface finish, and structural integrity. Clean background, technical product render, 4K, sharp edges."
        elif view_name == "左前":
            return f"Turn the camera to front-left quarter view, {angle_desc}, zoom level {zoom}. Show the industrial object from the left front angle. The left side and front face are visible. Maintain correct perspective and proportions. Keep geometry and surface details consistent. Clean background, technical product render, 4K, sharp edges."
        elif view_name == "右前":
            return f"Turn the camera to front-right quarter view, {angle_desc}, zoom level {zoom}. Show the industrial object from the right front angle. The right side and front face are visible. Maintain correct perspective and proportions. Keep geometry and surface details consistent. Clean background, technical product render, 4K, sharp edges."
        elif view_name == "侧面":
            return f"Turn the camera to side view, {angle_desc}, zoom level {zoom}. Show the industrial object in strict side view. The side profile, including all extrusions, handles, and vents, must be clearly visible. Keep geometry consistent. Clean background, technical product render, 4K, sharp edges."
        elif view_name == "背面":
            return f"Turn the camera to back view, {angle_desc}, zoom level {zoom}. Show the industrial object from behind. The rear panel, connectors, and back features must be accurately rendered. Keep geometry consistent. Clean background, technical product render, 4K, sharp edges."
        elif view_name == "俯视":
            return f"Turn the camera to top-down view, {angle_desc}, zoom level {zoom}. Show the industrial object from above. The top surface, including any mounting points, vents, or handles, must be clearly visible. Keep geometry consistent. Clean background, technical product render, 4K, sharp edges."
        else:
            view_desc = view_desc_map.get(view_name, "view")
            return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same industrial object from this angle. Keep the exact same geometry, surface finish, and structural integrity. Clean background, technical product render, 4K, sharp edges."
    
    # ========== Architecture 模式（详细描述）==========
    if mode == "Architecture":
        if view_name == "正立面":
            return f"Turn the camera to front elevation, {angle_desc}, zoom level {zoom}. Show the building directly from the front, with the facade centered and vertical lines straight. Keep the same architectural design, materials, and structural consistency. Professional architectural visualization, balanced lighting, 4K, sharp lines."
        elif view_name == "左前":
            return f"Turn the camera to front-left perspective, {angle_desc}, zoom level {zoom}. Show the building from a left front angle, revealing both the front facade and part of the left side. Maintain correct perspective and proportion. Keep the same design and materials. Architectural visualization, balanced lighting, 4K, sharp lines."
        elif view_name == "右前":
            return f"Turn the camera to front-right perspective, {angle_desc}, zoom level {zoom}. Show the building from a right front angle, revealing both the front facade and part of the right side. Maintain correct perspective and proportion. Keep the same design and materials. Architectural visualization, balanced lighting, 4K, sharp lines."
        elif view_name == "侧立面":
            return f"Turn the camera to side elevation, {angle_desc}, zoom level {zoom}. Show the building strictly from the side, with the side facade centered. Vertical lines must be straight. Keep the same design, materials, and structural consistency. Architectural visualization, balanced lighting, 4K, sharp lines."
        elif view_name == "背立面":
            return f"Turn the camera to back elevation, {angle_desc}, zoom level {zoom}. Show the building directly from the back, with the rear facade centered. Keep the same design, materials, and structural consistency. Architectural visualization, balanced lighting, 4K, sharp lines."
        elif view_name == "鸟瞰":
            return f"Turn the camera to bird's eye view, {angle_desc}, zoom level {zoom}. Show the building from a high angle looking down, revealing the roof and overall site layout. Maintain correct perspective. Keep the same design and materials. Architectural visualization, balanced lighting, 4K, sharp lines."
        else:
            view_desc = view_desc_map.get(view_name, "view")
            return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same building from this angle. Keep the same facade design, materials, and structural consistency. Professional architectural visualization, balanced lighting, 4K, sharp lines."
    
    # 默认（理论上不会执行到这里）
    view_desc = view_desc_map.get(view_name, "view")
    return f"Turn the camera to {view_desc}, {angle_desc}, zoom level {zoom}. Show the same subject from this angle. Keep consistency with the original image."

def load_workflow(filenames: list[str], views: list[dict], mode: str = "Celadon", is_single: bool = False) -> dict:
    workflow = json.loads(WORKFLOW_TEMPLATE.read_text(encoding="utf-8-sig"))
    
    # 🔧 修复：单图时只设置第一个参考图，其他设置为空或删除引用
    if len(filenames) == 1:
        img = filenames[0]
        workflow["6_load"]["inputs"]["image"] = img
        # 关键修复：其他两个参考图节点不应该被赋值，或者设置为空字符串
        # 方案1：删除对其他节点的引用（推荐）
        if "7_load2" in workflow:
            workflow["7_load2"]["inputs"]["image"] = ""  # 空字符串表示不使用
        if "8_load3" in workflow:
            workflow["8_load3"]["inputs"]["image"] = ""  # 空字符串表示不使用
        print(f"[DEBUG] Single image mode: using only 6_load, disabling 7_load2 and 8_load3")
    else:
        # 多图模式：按顺序赋值
        workflow["6_load"]["inputs"]["image"] = filenames[0] if len(filenames) > 0 else "reference.png"
        workflow["7_load2"]["inputs"]["image"] = filenames[1] if len(filenames) > 1 else ""
        workflow["8_load3"]["inputs"]["image"] = filenames[2] if len(filenames) > 2 else ""
        print(f"[DEBUG] Multiple image mode: using {len(filenames)} reference images")

    if is_single:
        print(f"[DEBUG] Single generation, disabling other samplers")
        all_samplers = ["23_front_sampler", "33_back_sampler", "43_top_sampler", 
                        "53_threequarter_sampler", "63_side_sampler", "73_additional_sampler"]
        sampler_map = {
            "正面": "23_front_sampler", "正面主视": "23_front_sampler",
            "左前": "33_back_sampler", "背面视图": "33_back_sampler",
            "右前": "43_top_sampler", "顶视图": "43_top_sampler",
            "侧面": "53_threequarter_sampler", "四分之三视图": "53_threequarter_sampler",
            "背面": "63_side_sampler", "侧视图": "63_side_sampler",
            "俯视": "73_additional_sampler", "鸟瞰": "73_additional_sampler",
            "正立面": "23_front_sampler", "侧立面": "53_threequarter_sampler",
            "背立面": "63_side_sampler",
        }
        current_view_name = views[0]["name"]
        keep_sampler = sampler_map.get(current_view_name, "23_front_sampler")
        for sampler_id in all_samplers:
            if sampler_id in workflow:
                if sampler_id == keep_sampler:
                    print(f"  [KEEP] {sampler_id}")
                else:
                    workflow[sampler_id]["inputs"]["steps"] = 1
                    workflow[sampler_id]["inputs"]["denoise"] = 0
                    print(f"  [DISABLED] {sampler_id}")

    encoder_map = {
        "正面主视": "20_front_encoder",
        "背面视图": "30_back_encoder",
        "顶视图": "40_top_encoder",
        "四分之三视图": "50_threequarter_encoder",
        "侧视图": "60_side_encoder",
        "正面": "20_front_encoder",
        "左前": "30_back_encoder",
        "右前": "40_top_encoder",
        "侧面": "50_threequarter_encoder",
        "背面": "60_side_encoder",
        "俯视": "70_additional_encoder",
        "正立面": "20_front_encoder",
        "侧立面": "50_threequarter_encoder",
        "背立面": "60_side_encoder",
        "鸟瞰": "70_additional_encoder",
    }
    sampler_map = {
        "正面主视": "23_front_sampler",
        "背面视图": "33_back_sampler",
        "顶视图": "43_top_sampler",
        "四分之三视图": "53_threequarter_sampler",
        "侧视图": "63_side_sampler",
        "正面": "23_front_sampler",
        "左前": "33_back_sampler",
        "右前": "43_top_sampler",
        "侧面": "53_threequarter_sampler",
        "背面": "63_side_sampler",
        "俯视": "73_additional_sampler",
        "正立面": "23_front_sampler",
        "侧立面": "53_threequarter_sampler",
        "背立面": "63_side_sampler",
        "鸟瞰": "73_additional_sampler",
    }
    latent_map = {
        "正面主视": "22_front_latent",
        "背面视图": "32_back_latent",
        "顶视图": "42_top_latent",
        "四分之三视图": "52_threequarter_latent",
        "侧视图": "62_side_latent",
        "正面": "22_front_latent",
        "左前": "32_back_latent",
        "右前": "42_top_latent",
        "侧面": "52_threequarter_latent",
        "背面": "62_side_latent",
        "俯视": "72_additional_latent",
        "正立面": "22_front_latent",
        "侧立面": "52_threequarter_latent",
        "背立面": "62_side_latent",
        "鸟瞰": "72_additional_latent",
    }

    print(f"[DEBUG] Processing {len(views)} views: mode={mode}")
    for view in views:
        name = view["name"]
        print(f"  {name}: steps={view.get('steps')}, cfg={view.get('cfg')}, zoom={view.get('zoom')}")
        if name not in encoder_map:
            print(f"  [WARN] View '{name}' not found")
            continue
        encoder_id = encoder_map[name]
        workflow[encoder_id]["inputs"]["prompt"] = build_prompt_for_view(
            name, view["horizontal"], view["vertical"], view["zoom"], mode
        )
        workflow[encoder_id]["inputs"]["target_size"] = 1024
        workflow[encoder_id]["inputs"]["target_vl_size"] = 384

        sampler_id = sampler_map[name]
        workflow[sampler_id]["inputs"]["steps"] = view["steps"]
        workflow[sampler_id]["inputs"]["cfg"] = view["cfg"]
        print(f"  [OK] {sampler_id}: steps={view['steps']}, cfg={view['cfg']}")

        if name in latent_map:
            latent_id = latent_map[name]
            workflow[latent_id]["inputs"]["width"] = 1024
            workflow[latent_id]["inputs"]["height"] = 1024

    return workflow

def comfy_post_json(path: str, payload: dict) -> dict:
    req = request.Request(
        COMFY_API + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))

def comfy_get_json(path: str) -> dict:
    with request.urlopen(COMFY_API + path, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))

def resolve_comfy_image(image_meta: dict) -> Path:
    subfolder = image_meta.get("subfolder", "")
    if subfolder:
        return COMFY_OUTPUT / subfolder / image_meta["filename"]
    return COMFY_OUTPUT / image_meta["filename"]

def relative_url(path: Path) -> str:
    return "/" + path.relative_to(PROJECT_ROOT).as_posix()

def copy_result_images(prompt_id: str, mode: str, views: list[dict], job_id: str) -> dict:
    """从 ComfyUI 输出复制图片到分类目录，并返回前端所需的数据结构"""
    history = comfy_get_json(f"/history/{prompt_id}")
    entry = history.get(prompt_id, {})
    outputs = entry.get("outputs", {})
    print(f"[DEBUG] outputs keys: {list(outputs.keys())}")
    
    result = {"single_paths": []}
    is_single = len(views) == 1
    
    # 确定要处理的保存节点列表
    if is_single:
        save_nodes = ["1"]
        print(f"[DEBUG] Single generation, only processing save node 1")
    else:
        save_nodes = ["1", "2", "3", "4", "5", "6"]
    
    # 保存单图到 single 目录，同时可能生成 contact sheet
    single_images = []
    for idx, save_node in enumerate(save_nodes):
        if idx >= len(views):
            break
        if save_node not in outputs:
            print(f"[WARN] Save node {save_node} not found")
            continue
        images = outputs[save_node].get("images", [])
        if not images:
            print(f"[WARN] No images in node {save_node}")
            continue
        src = resolve_comfy_image(images[0])
        if not src.exists():
            print(f"[WARN] Image file not found: {src}")
            continue
        view = views[idx]
        # 生成安全的文件名（避免中文字符导致 URL 问题？实际路径支持中文，但建议用拼音或保留）
        safe_name = view["name"].replace(" ", "_")
        dst = PROJECT_SINGLE / f"{job_id}_{safe_name}.png"
        shutil.copy2(src, dst)
        single_images.append((view, dst))
        result["single_paths"].append({
            "name": view["name"],
            "horizontal": view.get("horizontal", 0),
            "vertical": view.get("vertical", 0),
            "zoom": view.get("zoom", 1.0),
            "steps": view.get("steps", 24),
            "cfg": view.get("cfg", 2.0),
            "path": str(dst),
            "url": relative_url(dst),
        })
        print(f"[INFO] Saved single image: {dst}")
    
    # 生成总图（contact sheet）并保存到 contact_sheets 目录
    if len(single_images) > 1:
        try:
            imgs = [Image.open(dst) for _, dst in single_images]
            if imgs:
                # 布局：3列2行 或 2列2行
                cols, rows = (3, 2) if len(imgs) > 4 else (2, 2)
                cell_w, cell_h = imgs[0].size
                total_w = cols * cell_w
                total_h = rows * cell_h
                sheet_img = Image.new('RGB', (total_w, total_h))
                for i, img in enumerate(imgs[:cols*rows]):
                    x = (i % cols) * cell_w
                    y = (i // cols) * cell_h
                    sheet_img.paste(img, (x, y))
                sheet_path = PROJECT_SHEETS / f"{job_id}_contact.png"
                sheet_img.save(sheet_path)
                result["total_url"] = relative_url(sheet_path)
                result["sheet_url"] = relative_url(sheet_path)
                print(f"[INFO] Created contact sheet: {sheet_path}")
        except Exception as e:
            print(f"[WARN] Failed to create contact sheet: {e}")
    elif len(single_images) == 1:
        # 单独生成时，总图就用那张单图
        result["total_url"] = result["single_paths"][0]["url"]
        result["sheet_url"] = result["single_paths"][0]["url"]
    else:
        result["total_url"] = None
        result["sheet_url"] = None
    
    print(f"[INFO] Total single images saved: {len(result['single_paths'])}")
    return result

def run_job(job_id: str, comfy_filenames: list[str], mode: str, views: list[dict]) -> None:
    print(f"[DEBUG] Job {job_id}: {len(views)} views, {len(comfy_filenames)} reference images")
    for v in views:
        print(f"  {v['name']}: steps={v['steps']}, cfg={v['cfg']}, zoom={v['zoom']}")
    is_single = len(views) == 1
    if is_single:
        print(f"[DEBUG] Single generation mode for view: {views[0]['name']}")
    try:
        job_dir = PROJECT_JOBS / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        JOBS[job_id]["status"] = "submitting"
        
        workflow = load_workflow(comfy_filenames, views, mode, is_single)
        response = comfy_post_json("/prompt", {"prompt": workflow, "client_id": job_id})
        prompt_id = response["prompt_id"]
        JOBS[job_id]["prompt_id"] = prompt_id
        JOBS[job_id]["status"] = "running"

        while True:
            history = comfy_get_json(f"/history/{prompt_id}")
            if prompt_id in history:
                copied = copy_result_images(prompt_id, mode, views, job_id)
                JOBS[job_id]["status"] = "completed"
                JOBS[job_id]["single_paths"] = copied["single_paths"]
                JOBS[job_id]["total_url"] = copied.get("total_url")
                JOBS[job_id]["sheet_url"] = copied.get("sheet_url")
                JOBS[job_id]["completed_at"] = time.time()
                print(f"[DEBUG] Job {job_id} completed, saved {len(copied['single_paths'])} images")
                return
            time.sleep(1.5)

    except Exception as exc:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(exc)
        print(f"[ERROR] {exc}")

class PolyViewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/modes":
            modes_info = {}
            for mode_name, preset in MODE_PRESETS.items():
                modes_info[mode_name] = {
                    "name": mode_name,
                    "views": preset["views"],
                    "prompt": preset["prompt"],
                    "negative": preset["negative"]
                }
            return json_response(self, {"modes": modes_info})
        elif self.path == "/api/mode/Celadon" or self.path == "/api/mode/Pet" or self.path == "/api/mode/Human" or self.path == "/api/mode/Industrial" or self.path == "/api/mode/Architecture":
            mode_name = self.path.split("/")[-1]
            if mode_name in MODE_PRESETS:
                return json_response(self, MODE_PRESETS[mode_name])
            return json_response(self, {"error": "Mode not found"}, status=404)
        elif self.path.startswith("/api/jobs/"):
            job_id = self.path.rsplit("/", 1)[-1]
            job = JOBS.get(job_id)
            if not job:
                return json_response(self, {"error": "job not found"}, status=404)
            return json_response(self, job)
        return super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/generate":
            return json_response(self, {"error": "not found"}, status=404)

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            
            # 支持单图（imageData）或多图（images）
            image_data = payload.get("imageData")
            images_data = payload.get("images", [])
            
            if image_data:
                img_bytes = decode_data_url(image_data)
                comfy_filename = f"polyview_{uuid.uuid4().hex}.png"
                (PROJECT_INPUT / comfy_filename).write_bytes(img_bytes)
                (COMFY_INPUT / comfy_filename).write_bytes(img_bytes)
                comfy_filenames = [comfy_filename]
            elif images_data:
                if len(images_data) > 3:
                    return json_response(self, {"error": "Maximum 3 images allowed"}, status=400)
                comfy_filenames = []
                for i, img_data in enumerate(images_data):
                    if img_data:
                        img_bytes = decode_data_url(img_data)
                        comfy_filename = f"polyview_{uuid.uuid4().hex}_{i}.png"
                        (PROJECT_INPUT / comfy_filename).write_bytes(img_bytes)
                        (COMFY_INPUT / comfy_filename).write_bytes(img_bytes)
                        comfy_filenames.append(comfy_filename)
                    else:
                        comfy_filenames.append(f"dummy_{i}.png")
            else:
                return json_response(self, {"error": "No image provided"}, status=400)
            
            mode = payload["mode"]
            views = normalize_views(mode, payload.get("views"))

            ensure_dirs()
            
            job_id = uuid.uuid4().hex
            JOBS[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "mode": mode,
                "views": views,
                "created_at": time.time(),
            }
            thread = threading.Thread(
                target=run_job,
                args=(job_id, comfy_filenames, mode, views),
                daemon=True,
            )
            thread.start()
            return json_response(self, {"job_id": job_id, "status": "queued"})
        except Exception as exc:
            return json_response(self, {"error": str(exc)}, status=500)

if __name__ == "__main__":
    ensure_dirs()
    server = ThreadingHTTPServer(("127.0.0.1", 8080), PolyViewHandler)
    print(f"PolyView V2 server running at http://127.0.0.1:8080")
    server.serve_forever()