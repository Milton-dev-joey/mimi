#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 生成独立可执行文件
"""
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def get_platform_args():
    """根据平台获取特定参数"""
    system = platform.system()
    args = []
    
    if system == "Darwin":  # macOS
        args.extend([
            "--name=劳动法数据库",
            "--windowed",
        ])
        # macOS 不需要 --onefile，因为 .app 本身就是 bundle
        output_name = "劳动法数据库.app"
    elif system == "Windows":
        args.extend([
            "--name=劳动法数据库",
            "--windowed",
            "--onefile",
        ])
        output_name = "劳动法数据库.exe"
    else:  # Linux
        args.extend([
            "--name=labor-law-db",
            "--windowed",
            "--onefile",
        ])
        output_name = "labor-law-db"
    
    return args, output_name, system


def build():
    """打包应用程序"""
    print("=" * 60)
    print("劳动法数据库 - 打包工具")
    print("=" * 60)
    
    platform_args, output_name, system = get_platform_args()
    
    # 清理旧构建
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # 数据库路径
    db_path = Path.home() / "Desktop" / "laws_dev.db"
    if not db_path.exists():
        print(f"\n⚠️ 警告：未找到数据库文件 {db_path}")
        print("将使用项目目录下的数据库（如果存在）")
        db_path = Path("assets/laws.db")
    
    # 数据文件分隔符
    separator = ";" if system == "Windows" else ":"
    
    # PyInstaller 基础参数
    args = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
    ] + platform_args + [
        # 添加数据文件 - 数据库
        "--add-data", f"{db_path}{separator}.",
        # 隐藏导入
        "--hidden-import=PyQt6.sip",
        "--hidden-import=sqlite3",
        # 主程序
        "main.py"
    ]
    
    print(f"\n平台: {system}")
    print(f"数据库: {db_path}")
    print(f"输出: dist/{output_name}")
    print("\n开始打包...")
    print()
    
    result = subprocess.run(args)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ 打包成功！")
        print("=" * 60)
        print(f"\n📦 输出文件: dist/{output_name}")
        
        if system == "Darwin":
            print(f"\n📝 启动方式:")
            print(f"   双击打开: dist/劳动法数据库.app")
            print(f"   或命令行: open dist/劳动法数据库.app")
        elif system == "Windows":
            print(f"\n📝 将 EXE 和 laws_dev.db 放在同一目录下运行")
        
        # 显示文件大小
        try:
            if system == "Darwin":
                app_path = Path("dist/劳动法数据库.app")
                if app_path.exists():
                    # 计算总大小
                    total_size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
                    print(f"\n📊 应用大小: {total_size / 1024 / 1024:.1f} MB")
            else:
                exe_path = Path(f"dist/{output_name}")
                if exe_path.exists():
                    size = exe_path.stat().st_size
                    print(f"\n📊 文件大小: {size / 1024 / 1024:.1f} MB")
        except Exception as e:
            pass
            
    else:
        print("\n" + "=" * 60)
        print("❌ 打包失败")
        print("=" * 60)
        return 1
    
    return 0


def build_directory():
    """打包为目录模式（更快启动）"""
    print("=" * 50)
    print("劳动法数据库 - 打包工具（目录模式）")
    print("=" * 50)
    
    # 清理旧构建
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    args = [
        "pyinstaller",
        "--name=劳动法数据库",
        "--windowed",
        "--onedir",    # 目录模式
        "--clean",
        "--noconfirm",
        "--add-data", f"{Path.home()}/Desktop/laws_dev.db:.",
        "--hidden-import=PyQt6.sip",
        "--hidden-import=sqlite3",
        "main.py"
    ]
    
    print("\n开始打包...")
    result = subprocess.run(args, capture_output=False)
    
    if result.returncode == 0:
        print("\n✅ 打包成功！")
        print(f"\n输出目录: dist/劳动法数据库/")
    else:
        print("\n❌ 打包失败")
        return 1
    
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--dir":
        sys.exit(build_directory())
    else:
        sys.exit(build())
