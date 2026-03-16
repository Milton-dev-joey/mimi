@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate

REM 安装依赖
pip install -q -r requirements.txt

REM 运行应用
python main.py
