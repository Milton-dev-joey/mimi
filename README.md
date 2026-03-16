# 劳动法数据库桌面应用

基于 PyQt6 的本地化中国劳动法律法规检索系统。

## ✅ 已实现功能

### Phase 1: 基础框架 ✅
- [x] 项目结构搭建
- [x] 数据库连接层（自动检测桌面 laws_dev.db）
- [x] 暗色主题界面
- [x] 法律树形列表（按位阶分类）
- [x] 内容阅读器（条文展示、目录导航）
- [x] 搜索面板（标题/全文/条文搜索）

### Phase 2: 检索功能 ✅
- [x] 标题搜索
- [x] 全文搜索（FTS5）
- [x] 条文搜索
- [x] 搜索结果高亮
- [x] 搜索历史记录
- [x] 上下文提取

### Phase 3: 用户功能 ✅
- [x] 批注系统（添加/查询/修改/删除）
- [x] 案件管理（现实案件 + 参考案例）
- [x] 个人笔记
- [x] 关联法律条文
- [x] 标签系统

### Phase 4: 打包发布 ✅
- [x] 打包脚本（build.py - macOS）
- [x] Windows 打包脚本（build-windows.bat）
- [x] GitHub Actions 自动打包
- [ ] Windows EXE 代码签名（可选）

---

## 📁 项目结构

```
labor-law-db/
├── main.py                  # 入口文件
├── requirements.txt         # 依赖列表
├── build.py                # 打包脚本
├── run.sh                  # macOS/Linux 启动脚本
├── run.bat                 # Windows 启动脚本
├── README.md               # 项目说明
├── demo.py                 # 搜索功能演示
├── demo_user.py            # 用户功能演示
├── src/
│   ├── database.py         # 数据库核心操作
│   ├── search_utils.py     # 搜索工具（高亮、历史）
│   ├── user_data.py        # 用户数据管理（批注、案件、笔记）
│   ├── main_window.py      # 主窗口
│   └── widgets/
│       ├── __init__.py
│       ├── law_tree.py         # 法律树形列表
│       ├── content_view.py     # 内容展示区
│       └── search_panel.py     # 搜索面板
└── assets/
```

---

## 🚀 快速开始

### 方式一：自动启动脚本

**macOS/Linux:**
```bash
cd labor-law-db
chmod +x run.sh
./run.sh
```

**Windows:**
```cmd
cd labor-law-db
run.bat
```

### 方式二：手动运行

```bash
# 1. 创建虚拟环境
python3 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行
python main.py
```

---

## 📊 数据统计

当前数据库包含：
- **415 部法律**（涵盖劳动相关法律）
- **37 部法律**（全国人大颁布）
- **40 部行政法规**（国务院颁布）
- **301 部地方性法规**（各省市）
- **28 部司法解释**（最高法/最高检）

---

## 🔍 搜索功能

### 支持的搜索模式
1. **标题搜索** - 搜索法律标题
2. **全文搜索** - 使用 FTS5 全文检索
3. **条文搜索** - 搜索具体法律条文内容

### 搜索特性
- 关键词高亮显示
- 搜索结果上下文提取
- 搜索历史自动保存
- 按位阶筛选

---

## 📝 用户功能

### 批注系统
- 对整部法律添加批注
- 对具体条文添加批注
- 支持标签分类

### 案件管理
- **现实案件** - 记录办理的真实案件
- **参考案件** - 收集的指导案例、典型案例
- 关联相关法律条文
- 标签系统便于分类

### 个人笔记
- 独立笔记管理
- 可关联法律条文
- 支持标签

---

## 📦 打包成独立应用

### macOS (.app)
```bash
python build.py
```
输出：`dist/劳动法数据库.app`

### Windows (.exe)

#### 方式一：GitHub Actions 自动打包（推荐）
1. 将代码推送到 GitHub
2. 进入 Actions 页面下载 EXE
3. 或手动触发：Actions → Build Windows EXE → Run workflow

#### 方式二：Windows 本地打包
在 Windows 电脑上：
```batch
cd labor-law-db
build-windows.bat
```
输出：`dist/劳动法数据库.exe`

详细说明见 [WINDOWS_BUILD.md](WINDOWS_BUILD.md)

---

## 🛠️ 开发指南

### 添加新的数据库表
在 `src/user_data.py` 的 `_ensure_tables()` 方法中添加。

### 添加新的搜索功能
在 `src/search_utils.py` 的 `AdvancedSearch` 类中添加。

### 添加新的 UI 组件
在 `src/widgets/` 目录下创建新的组件类，然后在 `main_window.py` 中引用。

---

## 📋 待开发清单

- [ ] 收藏功能 UI 完善
- [ ] 法律文本导出（PDF/Word）
- [ ] 数据导入/导出（备份功能）
- [ ] 在线更新法律数据
- [ ] 智能推荐相关法条
- [ ] 案件时间线可视化

---

## 📄 许可证

本项目为私人使用开发，基于 MIT 许可证开源。
