#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaceOrbit 启动器 - 选择形象生成模式
"""

import subprocess
import sys
import os
import webbrowser
import threading
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import gradio as gr
except ImportError:
    print("请先安装 gradio: pip install gradio")
    sys.exit(1)


def launch_with_delay(port, script_name, delay=5):
    """启动子进程，等待指定时间后打开浏览器"""
    def _launch():
        print(f"🚀 正在启动 {script_name}...")
        process = subprocess.Popen([sys.executable, script_name])
        print(f"⏳ 等待 {delay} 秒让服务启动...")
        time.sleep(delay)
        print(f"🌐 打开浏览器: http://127.0.0.1:{port}")
        webbrowser.open(f"http://127.0.0.1:{port}")
    
    threading.Thread(target=_launch, daemon=True).start()


def launch_portrait():
    launch_with_delay(7861, "portrait.py")


def launch_anime():
    launch_with_delay(7862, "anime.py")


def launch_ghostmix():
    launch_with_delay(7863, "ghostmix.py")


def launch_cinema():
    launch_with_delay(7864, "cinema.py")


def create_launcher():
    """创建启动页面"""
    with gr.Blocks(title="FaceOrbit - AI形象生成器", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🎨 FaceOrbit - AI形象生成器
        
        ### 选择你的创作风格
        """)
        
        with gr.Row():
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("""
                ## 📸 写真模式
                *真实感人像*
                
                生成高度逼真的人物肖像
                - 保留原片质感
                - 适合证件照/职业照
                - 自然肤色与细节
                """)
                portrait_btn = gr.Button("🎭 进入写真模式", variant="primary", size="lg")
            
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("""
                ## 🎨 二次元模式
                *日系动漫风格*
                
                生成动漫角色形象
                - 30+ 预设角色
                - 6个角度生成
                - 支持自定义提示词
                """)
                anime_btn = gr.Button("🎭 进入二次元模式", variant="primary", size="lg")
            
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("""
                ## ✨ 立体感动漫
                *2.5D游戏CG*
                
                生成立体感十足的动漫角色
                - 游戏角色质感
                - 更丰富的细节
                - 适合游戏原画风格
                """)
                ghostmix_btn = gr.Button("🎭 进入立体感动漫", variant="primary", size="lg")
            
            with gr.Column(scale=1, min_width=250):
                gr.Markdown("""
                ## 🎬 影视明星
                *电影质感*
                
                生成电影剧照风格
                - 好莱坞级光影
                - 胶片质感
                - 适合演员/模特
                """)
                cinema_btn = gr.Button("🎭 进入影视明星", variant="primary", size="lg")
        
        gr.Markdown("""
        ---
        ### 📌 使用说明
        
        1. 点击任意模式按钮，将自动启动该模式的 Web 界面
        2. 每个模式独立运行在不同端口：
           - 写真模式：7861
           - 二次元模式：7862
           - 立体感动漫：7863
           - 影视明星：7864
        3. 首次启动需要等待 5-10 秒，浏览器会自动打开
        4. 请确保 ComfyUI 已启动（http://127.0.0.1:8188）
        
        ⚠️ 如果页面打不开，请稍等片刻后手动刷新
        """)
        
        # 按钮事件
        portrait_btn.click(fn=launch_portrait, inputs=[], outputs=[])
        anime_btn.click(fn=launch_anime, inputs=[], outputs=[])
        ghostmix_btn.click(fn=launch_ghostmix, inputs=[], outputs=[])
        cinema_btn.click(fn=launch_cinema, inputs=[], outputs=[])
    
    return demo


def open_browser(url, delay=1.5):
    threading.Timer(delay, lambda: webbrowser.open(url)).start()


if __name__ == "__main__":
    demo = create_launcher()
    local_url = "http://127.0.0.1:7860"
    
    print(f"🚀 正在启动 FaceOrbit 启动器...")
    print(f"📍 启动器地址: {local_url}")
    print(f"📌 请选择要进入的形象生成模式")
    print(f"💡 提示：点击按钮后请等待 5-10 秒，浏览器会自动打开对应页面")
    
    open_browser(local_url)
    
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7860,
        theme=gr.themes.Soft()
    )