@echo off
chcp 65001 >nul
echo ============================================
echo   劳动法数据库 - Windows 便携版打包
echo ============================================
echo.

REM 激活虚拟环境
call venv\Scripts\activate.bat 2>nul || (
    echo 请先运行 build-windows.bat 创建虚拟环境
    pause
    exit /b 1
)

echo [1/2] 清理旧构建...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo [2/2] 打包（目录模式，启动更快）...
pyinstaller ^
  --name="劳动法数据库" ^
  --windowed ^
  --onedir ^
  --clean ^
  --noconfirm ^
  --add-data="%USERPROFILE%\Desktop\laws_dev.db;." ^
  --hidden-import=PyQt6.sip ^
  --hidden-import=sqlite3 ^
  --icon=assets\icon.ico ^
  main.py

if errorlevel 1 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ============================================
echo   打包成功！
echo ============================================
echo.
echo 输出目录: dist\劳动法数据库\
echo 运行方式: 双击 dist\劳动法数据库\劳动法数据库.exe
echo.
pause
