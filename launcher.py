#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaceOrbit 启动器 - 选择形象生成模式
多角度模块：写真模式、二次元模式
多画风模块：影视明星模式、2.5D多画风模式
"""

import subprocess
import sys
import os
import webbrowser
import threading
import time
import socket

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import gradio as gr
except ImportError:
    print("请先安装 gradio: pip install gradio")
    sys.exit(1)


def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return False
        except socket.error:
            return True


def kill_process_on_port(port):
    """结束占用指定端口的进程"""
    import subprocess
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port} | findstr LISTENING',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[4]
                    subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                    print(f"✅ 已结束占用端口 {port} 的进程 (PID: {pid})")
                    return True
    except Exception as e:
        print(f"⚠️ 清理端口 {port} 时出错: {e}")
    return False


def ensure_port_free(port):
    """确保端口可用，如果被占用则尝试清理"""
    if is_port_in_use(port):
        print(f"⚠️ 端口 {port} 被占用，正在尝试清理...")
        kill_process_on_port(port)
        time.sleep(1)
        if is_port_in_use(port):
            print(f"❌ 端口 {port} 仍被占用，请手动关闭相关程序")
            return False
        else:
            print(f"✅ 端口 {port} 已清理完成")
    return True


def launch_with_delay(port, script_name, delay=5):
    """启动子进程，等待指定时间后打开浏览器"""
    def _launch():
        ensure_port_free(port)
        print(f"🚀 正在启动 {script_name}...")
        process = subprocess.Popen([sys.executable, script_name])
        print(f"⏳ 等待 {delay} 秒让服务启动...")
        time.sleep(delay)
        print(f"🌐 打开浏览器: http://127.0.0.1:{port}")
        webbrowser.open(f"http://127.0.0.1:{port}")
    
    threading.Thread(target=_launch, daemon=True).start()


# ========== 多角度模式 ==========
def launch_portrait():
    """启动写真模式（多角度）"""
    launch_with_delay(7861, "portrait.py")


def launch_anime():
    """启动二次元模式（多角度）"""
    launch_with_delay(7862, "anime.py")


# ========== 多画风模式 ==========
def launch_realistic():
    """启动影视明星/真实感模式（多画风）"""
    launch_with_delay(7864, "realistic.py")


def launch_scifi():
    """启动2.5D多画风模式（多画风）"""
    launch_with_delay(7865, "scifi.py")


def create_launcher():
    """创建启动页面"""
    with gr.Blocks(title="FaceOrbit - AI形象生成器", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🎨 FaceOrbit - AI形象生成器
        
        ### 上传照片，生成属于你的专属形象
        """)
        
        # ========== 多角度模块 ==========
        gr.Markdown("""
        ---
        ## 📐 多角度生成
        *上传一张照片，生成6个不同角度*
        """)
        
        with gr.Row():
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("""
                ### 📸 写真模式
                *真实感人像*
                
                生成高度逼真的人物肖像
                - 保留原片质感
                - 适合证件照/职业照
                - 自然肤色与细节
                - ✅ 支持6个角度
                """)
                portrait_btn = gr.Button("🎭 进入写真模式", variant="primary", size="lg")
            
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("""
                ### 🎨 二次元模式
                *日系动漫风格*
                
                生成动漫角色形象
                - 30+ 预设角色
                - 6个角度生成
                - 支持自定义提示词
                - ✅ 支持6个角度
                """)
                anime_btn = gr.Button("🎭 进入二次元模式", variant="primary", size="lg")
        
        # ========== 多画风模块 ==========
        gr.Markdown("""
        ---
        ## 🎨 多画风迁移
        *上传一张照片，转换为不同艺术风格*
        """)
        
        with gr.Row():
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("""
                ### 🎬 真实感画风
                *摄影/电影质感*
                
                生成真实感艺术影像
                - 电影级光影
                - 胶片质感
                - 10种预设画风
                - 🎨 专注画风迁移
                """)
                realistic_btn = gr.Button("🎭 进入真实感画风", variant="primary", size="lg")
            
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("""
                ### 🤖 2.5D多画风
                *赛博朋克/水彩/魔法*
                
                生成风格化艺术形象
                - 赛博朋克/攻壳机动队
                - 水彩/魔法/摇滚
                - 10种预设画风
                - 🎨 专注画风迁移
                """)
                scifi_btn = gr.Button("🎭 进入2.5D画风", variant="primary", size="lg")
        
        gr.Markdown("""
        ---
        ### 📌 使用说明
        
        | 模块 | 模式 | 端口 | 输出 | 说明 |
        |------|------|------|------|------|
        | **多角度** | 写真模式 | 7861 | 6张 | 真实感人像，6个角度 |
        | **多角度** | 二次元模式 | 7862 | 6张 | 日系动漫，6个角度 |
        | **多画风** | 真实感画风 | 7864 | 1张 | 摄影/电影质感，画风迁移 |
        | **多画风** | 2.5D画风 | 7865 | 1张 | 赛博朋克/水彩等，画风迁移 |
        
        > 💡 **提示**：
        > - 多角度模式：适合需要展示同一人物不同角度的场景
        > - 多画风模式：单张输出，适合探索不同艺术风格
        > - 请确保 ComfyUI 已启动（http://127.0.0.1:8188）
        """)
        
        # 按钮事件
        portrait_btn.click(fn=launch_portrait, inputs=[], outputs=[])
        anime_btn.click(fn=launch_anime, inputs=[], outputs=[])
        realistic_btn.click(fn=launch_realistic, inputs=[], outputs=[])
        scifi_btn.click(fn=launch_scifi, inputs=[], outputs=[])
    
    return demo


def open_browser(url, delay=1.5):
    threading.Timer(delay, lambda: webbrowser.open(url)).start()


if __name__ == "__main__":
    # 启动前检查所有端口
    for port in [7861, 7862, 7864, 7865]:
        ensure_port_free(port)
    
    demo = create_launcher()
    local_url = "http://127.0.0.1:7860"
    
    print(f"🚀 正在启动 FaceOrbit 启动器...")
    print(f"📍 启动器地址: {local_url}")
    print(f"📌 ========== 模式说明 ==========")
    print(f"📐 多角度模块：")
    print(f"   - 写真模式 (端口 7861)：真实感人像，6角度")
    print(f"   - 二次元模式 (端口 7862)：日系动漫，6角度")
    print(f"🎨 多画风模块：")
    print(f"   - 真实感画风 (端口 7864)：摄影/电影质感，单张")
    print(f"   - 2.5D画风 (端口 7865)：赛博朋克/水彩等，单张")
    print(f"=================================")
    
    open_browser(local_url)
    
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        theme=gr.themes.Soft()
    )