@echo off
chcp 65001 >nul
title FaceOrbit - AI形象生成器

echo ========================================
echo    FaceOrbit - AI形象生成器
echo ========================================
echo.
echo 正在检查环境...

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

:: 检查依赖
echo [1/4] 检查依赖包...
pip show gradio >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖包...
    pip install gradio requests pillow
)

:: 检查 ComfyUI
echo [2/4] 检查 ComfyUI 状态...
set COMFYUI_DIR=D:\PixelSmile\ComfyUI-aki\ComfyUI-aki-v3\ComfyUI
if not exist "%COMFYUI_DIR%\main.py" (
    echo [警告] 未找到 ComfyUI，请确认路径是否正确
)

:: 清理端口（可选，避免冲突）
echo [3/4] 清理端口...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7861 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7862 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7863 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7864 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7865 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: 启动启动器
echo [4/4] 启动 FaceOrbit...
echo.
echo ========================================
echo   启动成功！
echo   请在浏览器中访问: http://127.0.0.1:7860
echo ========================================
echo.
echo 提示: 
echo   - 写真模式端口: 7861
echo   - 二次元模式端口: 7862
echo   - 立体感动漫端口: 7863
echo   - 影视明星端口: 7864
echo   - 科幻感动漫端口: 7865
echo.
echo 关闭此窗口将同时关闭所有模式
echo ========================================

:: 切换到项目目录并启动
cd /d D:\PixelSmile\FaceOrbit
python launcher.py

pause