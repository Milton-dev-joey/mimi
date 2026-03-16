# Windows 版本打包指南

## 📋 前提条件

### 1. Windows 环境
- Windows 10/11 64位系统
- Python 3.11 或更高版本
- 数据库文件 `laws_dev.db`（放在桌面或项目目录）

### 2. 安装 Python
下载地址：https://www.python.org/downloads/windows/

安装时勾选 **"Add Python to PATH"**

---

## 🚀 打包方法

### 方法一：一键打包（推荐）

在 Windows 上打开命令提示符或 PowerShell：

```batch
# 进入项目目录
cd labor-law-db

# 运行打包脚本
build-windows.bat
```

打包完成后，文件位于 `dist/劳动法数据库.exe`

---

### 方法二：手动打包

```batch
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate.bat

# 3. 安装依赖
pip install pyinstaller
pip install -r requirements.txt

# 4. 打包单文件版本
pyinstaller --name="劳动法数据库" ^
  --windowed ^
  --onefile ^
  --add-data="%USERPROFILE%\Desktop\laws_dev.db;." ^
  --hidden-import=PyQt6.sip ^
  --hidden-import=sqlite3 ^
  main.py

# 或打包目录版本（启动更快）
pyinstaller --name="劳动法数据库" ^
  --windowed ^
  --onedir ^
  --add-data="%USERPROFILE%\Desktop\laws_dev.db;." ^
  --hidden-import=PyQt6.sip ^
  --hidden-import=sqlite3 ^
  main.py
```

---

## 📦 两种打包方式对比

| 特性 | 单文件模式 (onefile) | 目录模式 (onedir) |
|------|---------------------|------------------|
| 文件数量 | 1个 EXE | 1个文件夹 |
| 文件大小 | ~60-80MB | ~50-70MB |
| 启动速度 | 较慢（需要解压） | 较快 |
| 便携性 | 单文件，方便分享 | 文件夹，需要一起复制 |
| 推荐场景 | 分发给别人用 | 自己日常使用 |

---

## 📁 文件结构

打包后文件结构：

```
labor-law-db/
├── dist/
│   ├── 劳动法数据库.exe          # 单文件模式
│   └── 劳动法数据库/             # 目录模式
│       ├── 劳动法数据库.exe
│       └── ...其他文件
├── build/                        # 临时文件（可删除）
├── build-windows.bat             # Windows 打包脚本
├── build-windows-dir.bat         # Windows 便携版打包
└── ...
```

---

## 🎯 使用方式

### 方式一：EXE + 数据库分开

```
任意文件夹/
├── 劳动法数据库.exe
└── laws_dev.db          # 放在同一目录下
```

双击 `劳动法数据库.exe` 运行

### 方式二：数据库内置（修改代码）

如果想把数据库打包进 EXE 内部：

1. 将 `laws_dev.db` 复制到项目根目录
2. 修改 `src/database.py`：

```python
# 修改数据库路径查找逻辑
def __init__(self, db_path: Optional[str] = None):
    if db_path is None:
        # 优先使用打包后的路径
        import sys
        if getattr(sys, 'frozen', False):
            # PyInstaller 打包后的路径
            bundle_dir = sys._MEIPASS
            db_path = os.path.join(bundle_dir, 'laws_dev.db')
        else:
            # 开发环境
            db_path = os.path.join(os.path.dirname(__file__), '..', 'laws_dev.db')
    
    self.db_path = db_path
    ...
```

---

## 🔧 常见问题

### 1. 打包失败：找不到 PyQt6
```batch
pip install --upgrade PyQt6
```

### 2. 运行时闪退
```batch
# 使用命令行运行，查看错误信息
dist\劳动法数据库.exe
```

### 3. 数据库找不到
- 确保 `laws_dev.db` 和 EXE 在同一目录
- 或使用内置数据库方式（见上文）

### 4. 杀毒软件误报
PyInstaller 打包的程序有时会被误报，可以：
- 添加到杀毒软件白名单
- 使用 `--onefile` 模式减少误报
- 购买代码签名证书签名 EXE

---

## 🐧 在 macOS 上交叉编译 Windows 版本

**不推荐**，但可以使用 Docker/Wine：

```bash
# 安装 Wine
brew install wine

# 下载 Windows Python
# 然后使用 Wine 运行打包脚本
wine python build-windows.bat
```

更简单的方法是使用 GitHub Actions（见 `.github/workflows/build-windows.yml`）

---

## 📱 自动打包（GitHub Actions）

项目已配置 GitHub Actions，每次推送到 main 分支会自动打包：

1. 将代码推送到 GitHub
2. 进入 Actions 页面
3. 下载打包好的 EXE 文件

或手动触发：
- 进入 GitHub 仓库 → Actions → Build Windows EXE → Run workflow

---

## 🎨 自定义图标（可选）

准备 `.ico` 格式图标，放在 `assets/icon.ico`，打包时会自动应用。

转换工具：https://convertio.co/png-ico/
