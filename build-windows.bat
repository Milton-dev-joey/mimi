@echo off
chcp 65001 >nul
echo ============================================
echo   劳动法数据库 - Windows 打包工具
echo ============================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo [1/4] 创建虚拟环境...
    python -m venv venv
)

echo [2/4] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/4] 安装依赖...
pip install -q --upgrade pip
pip install -q pyinstaller
pip install -q -r requirements.txt

REM 检查数据库
if not exist "%USERPROFILE%\Desktop\laws_dev.db" (
    echo.
    echo [警告] 未在桌面找到 laws_dev.db 数据库文件！
    echo 请将数据库文件放在: %USERPROFILE%\Desktop\
    echo.
    pause
    exit /b 1
)

echo [4/4] 开始打包...
echo.

REM 清理旧构建
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 打包命令
pyinstaller ^
  --name="劳动法数据库" ^
  --windowed ^
  --onefile ^
  --clean ^
  --noconfirm ^
  --add-data="%USERPROFILE%\Desktop\laws_dev.db;." ^
  --hidden-import=PyQt6.sip ^
  --hidden-import=sqlite3 ^
  --icon=assets\icon.ico ^
  main.py

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ============================================
echo   打包成功！
echo ============================================
echo.
echo 输出文件: dist\劳动法数据库.exe
echo.
echo 使用说明:
echo   1. 将 劳动法数据库.exe 和 laws_dev.db 放在同一目录
echo   2. 双击运行 劳动法数据库.exe
echo.
echo 文件大小:
for %%I in (dist\劳动法数据库.exe) do (
    echo   %%~zI 字节 (约 %%~zI / 1024 / 1024 MB)
)
echo.
pause
