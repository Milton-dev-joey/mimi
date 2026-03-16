#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卡片式首页组件 - 紧凑2列布局，浅色主题
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QStackedWidget, QTextEdit, QLineEdit, QListWidget, QListWidgetItem,
    QSizePolicy, QDialog, QTextBrowser, QTabWidget, QCheckBox, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.database import Database, Law


class LawCard(QFrame):
    """法律卡片 - 浅色主题紧凑版"""
    law_clicked = pyqtSignal(str)  # law_id
    
    def __init__(self, law: Law, parent=None):
        super().__init__(parent)
        self.law = law
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)
        # 浅色主题样式
        self.setStyleSheet("""
            LawCard {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 6px;
                margin: 2px;
            }
            LawCard:hover {
                background-color: #f5f5f5;
                border-color: #1976d2;
            }
        """)
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)
        
        # 标题 - 字号保持12pt
        title = QLabel(self.law.title)
        title_font = QFont("PingFang SC", 12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setWordWrap(True)
        title.setStyleSheet("color: #212121;")
        layout.addWidget(title)
        
        # 元信息 - 字号保持10pt
        meta = self.law.publish[:4] if self.law.publish else "未知"
        if self.law.status and self.law.status != "未知":
            meta += f" · {self.law.status}"
        
        meta_label = QLabel(meta)
        meta_label.setFont(QFont("PingFang SC", 10))
        meta_label.setStyleSheet("color: #757575;")
        layout.addWidget(meta_label)
        
        # 已废止状态灰显
        if self.law.status == "已废止":
            self.setStyleSheet(self.styleSheet().replace("#ffffff", "#f5f5f5"))
            title.setStyleSheet("color: #9e9e9e;")
    
    def mousePressEvent(self, event):
        self.law_clicked.emit(self.law.id)


class HierarchyCard(QFrame):
    """位阶卡片 - 浅色主题2列布局"""
    law_clicked = pyqtSignal(str)
    expand_clicked = pyqtSignal(str, list)
    
    def __init__(self, type_name: str, type_code: str, laws: list, parent=None):
        super().__init__(parent)
        self.type_name = type_name
        self.type_code = type_code
        self.all_laws = laws
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(350)
        # 浅色主题样式
        self.setStyleSheet("""
            HierarchyCard {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)
        
        # 头部
        header = QHBoxLayout()
        header.setSpacing(4)
        
        title = QLabel(f"{self.type_name}")
        title_font = QFont("PingFang SC", 12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976d2;")
        header.addWidget(title)
        
        count_label = QLabel(f"{len(self.all_laws)}部")
        count_label.setFont(QFont("PingFang SC", 9))
        count_label.setStyleSheet("color: #757575;")
        header.addWidget(count_label)
        
        header.addStretch()
        
        # 展开按钮
        self.toggle_btn = QPushButton("▼")
        self.toggle_btn.setFixedSize(24, 24)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.toggle_btn.setToolTip("展开查看全部")
        self.toggle_btn.clicked.connect(self._on_expand)
        header.addWidget(self.toggle_btn)
        
        layout.addLayout(header)
        
        # 选取重点法律（最多4个，确保一页显示）
        # 对于地方性法规，优先展示深圳的
        priority_keywords = ['劳动', '合同', '工伤', '保险', '工资', '就业', '休假']
        shenzhen_keywords = ['深圳', '深圳市']
        priority_laws = []
        
        # 如果是地方性法规，优先选深圳的
        if self.type_code == 'dfxfg':
            for law in self.all_laws:
                is_shenzhen = any(kw in law.title for kw in shenzhen_keywords)
                if is_shenzhen and len(priority_laws) < 4:
                    priority_laws.append(law)
        
        # 再按关键词筛选（补充到4个）
        for law in self.all_laws:
            if law in priority_laws:
                continue
            is_priority = any(kw in law.title for kw in priority_keywords)
            if is_priority and len(priority_laws) < 4:
                priority_laws.append(law)
        
        # 如果还不够4个，按顺序补充
        if len(priority_laws) < 4:
            for law in self.all_laws:
                if law not in priority_laws and len(priority_laws) < 4:
                    priority_laws.append(law)
        
        # 创建法律卡片
        for law in priority_laws:
            card = LawCard(law)
            card.law_clicked.connect(self.law_clicked.emit)
            layout.addWidget(card)
        
        layout.addStretch()
    
    def _on_expand(self):
        """展开按钮点击"""
        self.expand_clicked.emit(self.type_name, self.all_laws)


class AdvancedSearchDialog(QDialog):
    """高级检索对话框 - 浅色主题"""
    search_requested = pyqtSignal(str, dict)  # keyword, filters
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("高级检索")
        self.setMinimumSize(500, 400)
        self.setStyleSheet("background-color: #ffffff;")
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("🔍 高级检索")
        title.setFont(QFont("PingFang SC", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        layout.addWidget(title)
        
        # 搜索输入
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("关键词："))
        
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入搜索关键词...")
        self.keyword_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
            }
            QLineEdit:focus {
                border-color: #1976d2;
            }
        """)
        search_layout.addWidget(self.keyword_input)
        layout.addLayout(search_layout)
        
        # 搜索范围
        scope_group = QGroupBox("搜索范围")
        scope_group.setStyleSheet("""
            QGroupBox {
                color: #424242;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        scope_layout = QVBoxLayout(scope_group)
        
        self.search_laws = QCheckBox("法律法规（标题+全文）")
        self.search_laws.setChecked(True)
        self.search_laws.setStyleSheet("color: #424242;")
        scope_layout.addWidget(self.search_laws)
        
        self.search_cases = QCheckBox("案例（标题+摘要+事实+争议焦点+裁判结果）")
        self.search_cases.setChecked(True)
        self.search_cases.setStyleSheet("color: #424242;")
        scope_layout.addWidget(self.search_cases)
        
        layout.addWidget(scope_group)
        
        # 法律位阶筛选
        filter_group = QGroupBox("法律位阶筛选（仅对法律法规有效）")
        filter_group.setStyleSheet(scope_group.styleSheet())
        filter_layout = QVBoxLayout(filter_group)
        
        self.type_filter = QComboBox()
        self.type_filter.addItem("全部位阶", None)
        self.type_filter.addItem("法律", "flfg")
        self.type_filter.addItem("行政法规", "xzfg")
        self.type_filter.addItem("部门规章", "bmgz")
        self.type_filter.addItem("司法解释", "sfjs")
        self.type_filter.addItem("地方性法规", "dfxfg")
        self.type_filter.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        filter_layout.addWidget(self.type_filter)
        
        layout.addWidget(filter_group)
        
        # 案例类型筛选
        case_group = QGroupBox("案例类型筛选（仅对案例有效）")
        case_group.setStyleSheet(scope_group.styleSheet())
        case_layout = QHBoxLayout(case_group)
        
        self.case_type_filter = QComboBox()
        self.case_type_filter.addItem("全部类型", None)
        self.case_type_filter.addItem("现实案件", "actual")
        self.case_type_filter.addItem("参考案例", "reference")
        self.case_type_filter.setStyleSheet(self.type_filter.styleSheet())
        case_layout.addWidget(self.case_type_filter)
        
        layout.addWidget(case_group)
        
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #424242;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        search_btn = QPushButton("开始检索")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        search_btn.clicked.connect(self._on_search)
        btn_layout.addWidget(search_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_search(self):
        """执行搜索"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请输入搜索关键词")
            return
        
        filters = {
            'search_laws': self.search_laws.isChecked(),
            'search_cases': self.search_cases.isChecked(),
            'law_type': self.type_filter.currentData(),
            'case_type': self.case_type_filter.currentData()
        }
        
        self.search_requested.emit(keyword, filters)
        self.accept()


class CombinedSearchResultDialog(QDialog):
    """综合搜索结果对话框 - 包含法律和案例 - 浅色主题"""
    law_selected = pyqtSignal(str)  # law_id
    case_selected = pyqtSignal(int)  # case_id
    
    def __init__(self, keyword: str, law_results: list, case_results: list, db: Database, parent=None):
        super().__init__(parent)
        self.keyword = keyword
        self.law_results = law_results
        self.case_results = case_results
        self.db = db
        self.setWindowTitle(f'高级检索: "{keyword}"')
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("background-color: #ffffff;")
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel(f'🔍 "{self.keyword}" 的检索结果')
        title.setFont(QFont("PingFang SC", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        layout.addWidget(title)
        
        # 统计
        stats = f"找到 {len(self.law_results)} 部法律，{len(self.case_results)} 个案例"
        stats_label = QLabel(stats)
        stats_label.setStyleSheet("color: #757575;")
        layout.addWidget(stats_label)
        
        # 使用标签页展示结果
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab {
                background-color: #f5f5f5;
                color: #757575;
                padding: 10px 20px;
                border: 1px solid #e0e0e0;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #1976d2;
                border-bottom: 2px solid #1976d2;
            }
        """)
        
        # 法律结果页
        law_widget = self._create_law_list(self.keyword)
        tabs.addTab(law_widget, f"📚 法律法规 ({len(self.law_results)})")
        
        # 案例结果页
        case_widget = self._create_case_list()
        tabs.addTab(case_widget, f"📁 案例 ({len(self.case_results)})")
        
        layout.addWidget(tabs)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #212121;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def _create_law_list(self, keyword: str = "") -> QWidget:
        """创建法律结果列表，显示包含关键词的条文编号"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        if not self.law_results:
            label = QLabel("未找到相关法律")
            label.setStyleSheet("color: #757575;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return widget

        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                color: #212121;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)

        for law in self.law_results:
            law_id = law.id if hasattr(law, 'id') else law.get('id')
            title = law.title if hasattr(law, 'title') else law.get('title', '未知')
            law_type = law.type if hasattr(law, 'type') else law.get('type', '未知')
            publish = law.publish if hasattr(law, 'publish') else law.get('publish', '未知')

            # 查询该法律中包含关键词的条文编号
            article_nums = []
            if keyword:
                try:
                    sql = """
                        SELECT article_num FROM law_articles
                        WHERE law_id = ? AND article_text LIKE ?
                        ORDER BY sort_order, id
                        LIMIT 10
                    """
                    self.db.cursor.execute(sql, (law_id, f"%{keyword}%"))
                    rows = self.db.cursor.fetchall()
                    article_nums = [row['article_num'] for row in rows]
                except:
                    pass

            # 构建显示文本
            display = f"📄 {title}\n"
            display += f"   位阶: {law_type} | 发布: {publish or '未知'}"

            # 添加相关条文编号
            if article_nums:
                # 格式化条文编号，兼容"第X条"和纯数字两种格式
                formatted_articles = []
                for num in article_nums[:5]:
                    if isinstance(num, str) and ('第' in num and '条' in num):
                        # 已经是"第X条"格式
                        formatted_articles.append(num)
                    else:
                        # 纯数字，包装成"第X条"
                        formatted_articles.append(f"第{num}条")
                
                articles_str = "、".join(formatted_articles)
                if len(article_nums) > 5:
                    articles_str += f" 等{len(article_nums)}条"
                display += f"\n   📋 相关: {articles_str}"

            item = QListWidgetItem()
            item.setText(display)
            item.setData(Qt.ItemDataRole.UserRole, ('law', law_id))
            list_widget.addItem(item)

        list_widget.itemDoubleClicked.connect(self._on_item_selected)
        layout.addWidget(list_widget)
        return widget
    
    def _create_case_list(self) -> QWidget:
        """创建案例结果列表"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        if not self.case_results:
            label = QLabel("未找到相关案例")
            label.setStyleSheet("color: #757575;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return widget
        
        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                color: #212121;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #eeeeee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        
        for case in self.case_results:
            item = QListWidgetItem()
            case_id = case.get('id')
            title = case.get('title', '未知')
            case_type = case.get('case_type', 'actual')
            summary = case.get('summary', '')
            
            type_mark = "【现实】" if case_type == 'actual' else "【参考】"
            summary_preview = summary[:50] + "..." if len(summary) > 50 else summary
            
            display = f"{type_mark} {title}\n"
            display += f"   {summary_preview}"
            item.setText(display)
            item.setData(Qt.ItemDataRole.UserRole, ('case', case_id))
            item.setToolTip(summary if summary else title)
            list_widget.addItem(item)
        
        list_widget.itemDoubleClicked.connect(self._on_item_selected)
        layout.addWidget(list_widget)
        return widget
    
    def _on_item_selected(self, item: QListWidgetItem):
        """处理双击选择"""
        item_type, item_id = item.data(Qt.ItemDataRole.UserRole)
        if item_type == 'law':
            self.law_selected.emit(item_id)
        elif item_type == 'case':
            self.case_selected.emit(item_id)
        self.close()

class ExpandedLawsDialog(QDialog):
    """展开显示全部法律的弹窗 - 浅色主题2列"""
    law_selected = pyqtSignal(str)
    
    def __init__(self, type_name: str, laws: list, parent=None):
        super().__init__(parent)
        self.type_name = type_name
        self.laws = laws
        self.setWindowTitle(f"{type_name} - 全部 {len(laws)} 部法律")
        self.setMinimumSize(800, 700)
        self.setStyleSheet("background-color: #ffffff;")
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 标题
        title = QLabel(f"📚 {self.type_name}")
        title.setFont(QFont("PingFang SC", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2;")
        layout.addWidget(title)
        
        desc = QLabel(f"共 {len(self.laws)} 部法律，点击卡片查看详情")
        desc.setStyleSheet("color: #757575;")
        layout.addWidget(desc)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #ffffff; }")
        
        # 卡片容器 - 2列网格
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(6)
        grid.setContentsMargins(0, 0, 0, 0)
        
        col_count = 2
        for i, law in enumerate(self.laws):
            card = LawCard(law)
            card.law_clicked.connect(self._on_law_clicked)
            grid.addWidget(card, i // col_count, i % col_count)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #212121;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #bdbdbd;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def _on_law_clicked(self, law_id: str):
        self.law_selected.emit(law_id)
        self.close()


class DashboardWidget(QWidget):
    """仪表盘/首页组件 - 浅色主题2列布局"""
    law_selected = pyqtSignal(str)
    case_selected = pyqtSignal(int)  # case_id
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setStyleSheet("background-color: #f5f5f5;")
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 标题区 - 白色卡片背景
        title_card = QFrame()
        title_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        title_layout = QVBoxLayout(title_card)
        title_layout.setSpacing(8)
        
        title = QLabel("📚 中国劳动法律法规数据库")
        title_font = QFont("PingFang SC", 20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976d2;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        
        subtitle = QLabel("按法律位阶分类浏览 · 全文检索 · 批注管理 · 案例管理")
        subtitle.setFont(QFont("PingFang SC", 11))
        subtitle.setStyleSheet("color: #757575;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.addStretch()
        
        self.quick_search = QLineEdit()
        self.quick_search.setPlaceholderText("🔍 搜索标题和内容...")
        self.quick_search.setFixedWidth(400)
        self.quick_search.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #212121;
                border: 2px solid #1976d2;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #1565c0;
            }
        """)
        self.quick_search.returnPressed.connect(self._on_quick_search)
        search_layout.addWidget(self.quick_search)
        
        search_btn = QPushButton("搜索")
        search_btn.setFixedWidth(80)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        search_btn.clicked.connect(self._on_quick_search)
        search_layout.addWidget(search_btn)
        
        # 高级检索按钮
        adv_search_btn = QPushButton("高级检索")
        adv_search_btn.setFixedWidth(100)
        adv_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #1976d2;
                border: 2px solid #1976d2;
                border-radius: 20px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
            }
        """)
        adv_search_btn.clicked.connect(self._on_advanced_search)
        search_layout.addWidget(adv_search_btn)
        
        search_layout.addStretch()
        title_layout.addLayout(search_layout)
        layout.addWidget(title_card)
        
        # 卡片容器 - 2列布局
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background-color: transparent;")
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(8)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.cards_container, 1)
        
        # 底部统计
        self.stats_label = QLabel("")
        self.stats_label.setFont(QFont("PingFang SC", 10))
        self.stats_label.setStyleSheet("color: #757575;")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)
    
    def _load_data(self):
        """加载数据 - 2列紧凑布局"""
        hierarchy = self.db.get_type_hierarchy()
        
        type_order = [
            ('法律', 'flfg'),
            ('行政法规', 'xzfg'),
            ('部门规章', 'bmgz'),
            ('司法解释', 'sfjs'),
            ('地方性法规', 'dfxfg'),
            ('地方政府规章', 'dfzfg')
        ]
        
        total_laws = 0
        col = 0
        row = 0
        
        for type_name, type_code in type_order:
            if type_name not in hierarchy:
                continue
            
            laws = hierarchy[type_name]
            if not laws:
                continue
            
            total_laws += len(laws)
            card = HierarchyCard(type_name, type_code, laws)
            card.law_clicked.connect(self._on_law_selected)
            card.expand_clicked.connect(self._show_expanded_dialog)
            self.cards_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # 2列换行
                col = 0
                row += 1
        
        self.stats_label.setText(f"共收录 {total_laws} 部劳动相关法律法规")
    
    def _on_quick_search(self):
        """快速搜索"""
        keyword = self.quick_search.text().strip()
        if not keyword:
            return
        
        results = []
        title_results = self.db.search_laws_by_title(keyword)
        results.extend(title_results)
        
        content_results = self.db.fulltext_search(keyword)
        for result in content_results:
            law = self.db.get_law_by_id(result.get('id', result.get('law_id')))
            if law and law not in results:
                results.append(law)
        
        # 同时搜索案例
        case_results = self.db.search_cases(keyword)
        
        unique_results = []
        seen_ids = set()
        for law in results:
            if law.id not in seen_ids:
                unique_results.append(law)
                seen_ids.add(law.id)
        
        if not unique_results and not case_results:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "搜索结果", f'未找到包含 "{keyword}" 的相关内容')
            return
        
        dialog = CombinedSearchResultDialog(keyword, unique_results, case_results, self.db, self)
        dialog.law_selected.connect(self._on_law_selected)
        dialog.case_selected.connect(self.case_selected.emit)
        dialog.exec()
    
    def _on_advanced_search(self):
        """打开高级检索对话框"""
        dialog = AdvancedSearchDialog(self.db, self)
        dialog.search_requested.connect(self._execute_advanced_search)
        dialog.exec()
    
    def _execute_advanced_search(self, keyword: str, filters: dict):
        """执行高级检索"""
        law_results = []
        case_results = []
        
        # 搜索法律
        if filters.get('search_laws', True):
            # 标题搜索
            title_results = self.db.search_laws_by_title(keyword)
            law_results.extend(title_results)
            
            # 全文搜索
            content_results = self.db.fulltext_search(keyword)
            for result in content_results:
                law = self.db.get_law_by_id(result.get('id', result.get('law_id')))
                if law:
                    law_results.append(law)
            
            # 按位阶筛选
            law_type = filters.get('law_type')
            if law_type:
                law_results = [law for law in law_results if law.type_code == law_type]
        
        # 搜索案例
        if filters.get('search_cases', True):
            case_results = self.db.search_cases(keyword)
            
            # 按案例类型筛选
            case_type = filters.get('case_type')
            if case_type:
                case_results = [c for c in case_results if c.get('case_type') == case_type]
        
        # 去重
        unique_laws = []
        seen_ids = set()
        for law in law_results:
            if law.id not in seen_ids:
                unique_laws.append(law)
                seen_ids.add(law.id)
        
        if not unique_laws and not case_results:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "检索结果", f'未找到包含 "{keyword}" 的相关内容')
            return
        
        dialog = CombinedSearchResultDialog(keyword, unique_laws, case_results, self.db, self)
        dialog.law_selected.connect(self._on_law_selected)
        dialog.case_selected.connect(self.case_selected.emit)
        dialog.exec()
    
    def _on_law_selected(self, law_id: str):
        self.law_selected.emit(law_id)
    
    def _show_expanded_dialog(self, type_name: str, laws: list):
        dialog = ExpandedLawsDialog(type_name, laws, self)
        dialog.law_selected.connect(self._on_law_selected)
        dialog.exec()
