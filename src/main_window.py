#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口 - 动态布局
初始首页全屏，点击法律后收缩为左侧1/3，内容区占2/3
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QToolBar, QLineEdit,
    QPushButton, QLabel, QMessageBox, QMenu, QApplication,
    QSizePolicy, QTabWidget, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QShortcut

from src.widgets.law_tree import LawTreeWidget
from src.widgets.content_view import ContentViewWidget
from src.widgets.search_panel import SearchPanel
from src.widgets.dashboard import DashboardWidget
from src.widgets.annotation_panel import AnnotationPanel
from src.widgets.case_panel import CasePanel
from src.widgets.topic_panel import TopicWidget
from src.database import Database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("劳动法数据库 v1.0")
        self.setGeometry(100, 100, 1600, 1000)

        # 设置浅色主题
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
                padding: 5px;
            }
            QStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #e0e0e0;
                color: #757575;
            }
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #212121;
            }
            QMenuBar::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                color: #212121;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)

        # 状态跟踪
        self.is_fullscreen_dashboard = True

        # 初始化数据库
        self.db = Database()
        try:
            self.db.connect()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据库连接失败：{str(e)}")
            return

        self._create_ui()
        self._create_menu()
        self._create_toolbar()
        self._create_statusbar()
        self._setup_shortcuts()

        # 初始状态：全屏显示首页
        self._show_fullscreen_dashboard()

    def _create_ui(self):
        """创建主界面"""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 主分割器
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.main_splitter)

        # 左侧：导航区域（仪表盘/法律列表/案例）
        self.left_stack = QStackedWidget()
        self.left_stack.setMinimumWidth(350)

        # 1. 仪表盘（首页卡片）
        self.dashboard = DashboardWidget(self.db)
        self.dashboard.law_selected.connect(self._on_law_selected_from_dashboard)
        self.dashboard.case_selected.connect(self._on_case_selected)
        self.left_stack.addWidget(self.dashboard)

        # 2. 传统树形列表
        self.law_tree = LawTreeWidget(self.db)
        self.law_tree.law_selected.connect(self._on_law_selected)
        self.left_stack.addWidget(self.law_tree)

        # 3. 案例管理
        self.case_panel = CasePanel(self.db)
        self.left_stack.addWidget(self.case_panel)

        # 4. 专题页面
        self.topic_panel = TopicWidget(self.db)
        self.topic_panel.topic_selected.connect(self._on_topic_selected)
        self.left_stack.addWidget(self.topic_panel)

        self.main_splitter.addWidget(self.left_stack)

        # 右侧：内容区域（初始隐藏）
        self.right_widget = QWidget()
        right_layout = QHBoxLayout(self.right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # 创建内部水平分割器：内容区2/3，功能面板1/3
        self.right_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 内容展示区（占2/3）
        self.content_view = ContentViewWidget(self.db)
        self.content_view.text_selected.connect(self._on_text_selected_for_annotation)
        self.right_splitter.addWidget(self.content_view)

        # 多功能标签页（搜索/批注）- 浅色主题（占1/3）
        self.right_tabs = QTabWidget()
        self.right_tabs.setMinimumWidth(300)
        self.right_tabs.setMaximumWidth(500)
        self.right_tabs.setStyleSheet("""
            QTabWidget {
                background-color: #ffffff;
            }
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

        # 搜索面板（简化为仅保留基本搜索，高级搜索移到首页）
        self.search_panel = SearchPanel(self.db)
        self.search_panel.law_selected.connect(self._on_law_selected)
        self.search_panel.article_selected.connect(self._on_article_selected)
        self.right_tabs.addTab(self.search_panel, "🔍 搜索")

        # 批注面板
        self.annotation_panel = AnnotationPanel(self.db)
        self.right_tabs.addTab(self.annotation_panel, "📝 批注")

        self.right_splitter.addWidget(self.right_tabs)
        right_layout.addWidget(self.right_splitter)

        # 右侧内容区域默认隐藏
        self.right_widget.setVisible(False)
        self.main_splitter.addWidget(self.right_widget)

        # 保存分割器索引用于后续显示
        self.dashboard_index = 0
        self.right_widget_index = 1

    def _create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")

        dashboard_action = QAction("🏠 返回首页", self)
        dashboard_action.setShortcut("Ctrl+H")
        dashboard_action.triggered.connect(self._show_fullscreen_dashboard)
        view_menu.addAction(dashboard_action)

        view_menu.addSeparator()

        toggle_search = QAction("搜索面板", self)
        toggle_search.setShortcut("Ctrl+F")
        toggle_search.triggered.connect(self._toggle_search_panel)
        view_menu.addAction(toggle_search)

        toggle_anno = QAction("批注面板", self)
        toggle_anno.setShortcut("Ctrl+Shift+A")
        toggle_anno.triggered.connect(self._toggle_annotation_panel)
        view_menu.addAction(toggle_anno)

        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")

        stats_action = QAction("📊 数据统计", self)
        stats_action.triggered.connect(self._show_stats)
        tools_menu.addAction(stats_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # 返回首页按钮
        home_btn = QPushButton("🏠 首页")
        home_btn.setToolTip("返回首页 (Ctrl+H)")
        home_btn.clicked.connect(self._show_fullscreen_dashboard)
        toolbar.addWidget(home_btn)

        # 案例管理
        cases_btn = QPushButton("📁 案例")
        cases_btn.clicked.connect(self._show_cases)
        toolbar.addWidget(cases_btn)

        # 专题页面
        topics_btn = QPushButton("📚 专题")
        topics_btn.clicked.connect(self._show_topics)
        toolbar.addWidget(topics_btn)

        toolbar.addSeparator()

        # 弹性占位
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        # 批注按钮
        anno_btn = QPushButton("📝 批注")
        anno_btn.clicked.connect(self._toggle_annotation_panel)
        toolbar.addWidget(anno_btn)

        # 回到首页按钮（仅在非首页时显示）
        self.back_btn = QPushButton("← 返回")
        self.back_btn.setVisible(False)
        self.back_btn.clicked.connect(self._show_fullscreen_dashboard)
        toolbar.addWidget(self.back_btn)

    def _create_statusbar(self):
        """创建状态栏"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("欢迎使用劳动法数据库 - 点击法律卡片开始浏览")

        # 统计信息
        self.stats_label = QLabel()
        self.statusbar.addPermanentWidget(self.stats_label)
        self._update_stats()

    def _setup_shortcuts(self):
        """设置快捷键"""
        QShortcut(QKeySequence("Ctrl+H"), self, activated=self._show_fullscreen_dashboard)
        QShortcut(QKeySequence("Ctrl+1"), self, activated=self._show_cases)

    # ==================== 布局切换 ====================

    def _show_fullscreen_dashboard(self):
        """显示全屏首页"""
        self.is_fullscreen_dashboard = True
        self.left_stack.setCurrentIndex(0)  # 显示仪表盘
        self.right_widget.setVisible(False)

        # 调整分割器
        self.main_splitter.setSizes([self.main_splitter.width(), 0])

        # 更新按钮状态
        self.back_btn.setVisible(False)

        if hasattr(self, 'statusbar') and self.statusbar:
            self.statusbar.showMessage("首页 - 按位阶浏览法律，点击卡片查看详情")

    def _show_split_view(self):
        """显示分割视图：左侧1/3，右侧2/3"""
        self.is_fullscreen_dashboard = False
        self.right_widget.setVisible(True)

        # 设置分割比例：左侧约1/3，右侧约2/3
        total_width = self.main_splitter.width()
        self.main_splitter.setSizes([total_width // 3, total_width * 2 // 3])

        # 更新按钮状态
        self.back_btn.setVisible(True)

        # 调整右侧面板内部比例：内容区2/3，功能标签页1/3
        self._adjust_right_panel_ratio()

    # ==================== 事件处理 ====================

    def _on_law_selected_from_dashboard(self, law_id: str):
        """从首页选择法律 - 切换到分割视图"""
        self._show_split_view()
        self._on_law_selected(law_id)

    def _on_law_selected(self, law_id: str):
        """法律被选中"""
        # 如果不是从首页选择的，确保显示右侧内容区
        if self.is_fullscreen_dashboard:
            self._show_split_view()

        self.content_view.load_law(law_id)

        # 更新搜索面板的当前法律
        self.search_panel.set_current_law(law_id)

        # 获取法律标题
        law = self.db.get_law_by_id(law_id)
        if law:
            if hasattr(self, 'statusbar') and self.statusbar:
                self.statusbar.showMessage(f"正在查看: {law.title}")
            # 更新批注面板位置
            self.annotation_panel.set_location(law_id, "", law.title)

    def _on_article_selected(self, law_id: str, article_num: str):
        """条文被选中"""
        if self.is_fullscreen_dashboard:
            self._show_split_view()

        self.content_view.load_article(law_id, article_num)
        law = self.db.get_law_by_id(law_id)
        if law:
            self.annotation_panel.set_location(law_id, article_num, law.title)

    def _on_case_selected(self, case_id: int):
        """案例被选中 - 显示案例详情"""
        from src.user_data import UserDataManager
        from src.widgets.case_panel import CaseDetailDialog

        udm = UserDataManager(self.db.conn)
        case = udm.get_case_by_id(case_id)

        if case:
            dialog = CaseDetailDialog(case, self)
            dialog.exec()

    def _on_search_requested(self, keyword: str):
        """搜索请求 - 首页搜索后跳转"""
        # 切换到分割视图
        if self.is_fullscreen_dashboard:
            self._show_split_view()

        self.search_panel.search(keyword)
        self.right_tabs.setCurrentIndex(0)  # 切换到搜索标签
        if hasattr(self, 'statusbar') and self.statusbar:
            self.statusbar.showMessage(f"搜索: {keyword}")

    def _show_cases(self):
        """显示案例管理"""
        if self.is_fullscreen_dashboard:
            # 在首页模式下，切换到案例面板
            self.left_stack.setCurrentIndex(2)
            self.case_panel._load_cases()
            if hasattr(self, 'statusbar') and self.statusbar:
                self.statusbar.showMessage("案例管理 - 现实案件与参考案例")
        else:
            # 在分割视图下，在左侧显示案例
            self.left_stack.setCurrentIndex(2)
            self.case_panel._load_cases()

    def _show_topics(self):
        """显示专题页面"""
        if self.is_fullscreen_dashboard:
            self.left_stack.setCurrentIndex(3)
            if hasattr(self, 'statusbar') and self.statusbar:
                self.statusbar.showMessage("专题 - 劳动法律实务高频问题")
        else:
            # 在分割视图下，也切换到专题
            self.left_stack.setCurrentIndex(3)
            if hasattr(self, 'statusbar') and self.statusbar:
                self.statusbar.showMessage("专题 - 劳动法律实务高频问题")

    def _on_topic_selected(self, topic_id: str, topic_title: str):
        """专题被选中 - 可以在这里添加跳转逻辑"""
        # 可以在这里实现跳转到相关法律或搜索相关条文
        # 目前 TopicWidget 内部已处理提示
        pass

    def _toggle_search_panel(self):
        """切换搜索面板"""
        if self.is_fullscreen_dashboard:
            self._show_split_view()
        self.right_tabs.setCurrentIndex(0)

    def _toggle_annotation_panel(self):
        """切换批注面板"""
        if self.is_fullscreen_dashboard:
            self._show_split_view()
        self.right_tabs.setCurrentIndex(1)

    def _on_text_selected_for_annotation(self, selected_text: str):
        """处理选中文本添加批注"""
        # 切换到批注面板
        self.right_tabs.setCurrentIndex(1)
        # 调用批注面板的添加方法
        self.annotation_panel.add_annotation_for_selection(selected_text, "")

    # ==================== 其他功能 ====================

    def _show_stats(self):
        """显示统计"""
        from src.user_data import UserDataManager
        udm = UserDataManager(self.db.conn)

        cursor = self.db.cursor
        cursor.execute("SELECT COUNT(*) FROM laws")
        law_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM law_articles")
        article_count = cursor.fetchone()[0]

        user_stats = udm.get_stats()

        msg = f"""
        <h2>📊 数据统计</h2>
        <p><b>法律法规：</b>{law_count} 部</p>
        <p><b>法律条文：</b>{article_count} 条</p>
        <hr>
        <p><b>我的批注：</b>{user_stats['annotations']} 条</p>
        <p><b>我的案例：</b>{user_stats['cases']} 个</p>
        <p>  - 现实案件：{user_stats['actual_cases']} 个</p>
        <p>  - 参考案例：{user_stats['reference_cases']} 个</p>
        <p><b>我的笔记：</b>{user_stats['notes']} 条</p>
        """

        QMessageBox.about(self, "数据统计", msg)

    def _update_stats(self):
        """更新状态栏统计"""
        try:
            cursor = self.db.cursor
            cursor.execute("SELECT COUNT(*) FROM laws")
            law_count = cursor.fetchone()[0]
            self.stats_label.setText(f"📚 {law_count} 部法律")
        except:
            pass

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 劳动法数据库",
            """
            <h2>劳动法数据库 v1.0</h2>
            <p>一个本地化的中国劳动法律法规检索与管理工具</p>
            <hr>
            <p><b>主要功能：</b></p>
            <ul>
                <li>📚 按法律位阶卡片式浏览</li>
                <li>🔍 标题/全文/条文多模式搜索</li>
                <li>📝 精准条文批注（类似Word）</li>
                <li>📁 现实案件与参考案例管理</li>
            </ul>
            <hr>
            <p>数据库共收录 415 部劳动相关法律法规</p>
            <p><b>操作提示：</b></p>
            <ul>
                <li>首页点击法律卡片进入阅读模式</li>
                <li>选中条文文字可添加精准批注</li>
                <li>Ctrl+H 快速返回首页</li>
            </ul>
            """
        )

    def _adjust_right_panel_ratio(self):
        """调整右侧面板比例：内容区2/3，功能面板1/3"""
        right_width = self.right_splitter.width()
        # 内容区占2/3，功能标签页占1/3
        self.right_splitter.setSizes([right_width * 2 // 3, right_width // 3])

    def resizeEvent(self, event):
        """窗口大小改变时调整布局"""
        super().resizeEvent(event)

        if not self.is_fullscreen_dashboard:
            # 保持左侧约1/3的比例
            total_width = self.main_splitter.width()
            self.main_splitter.setSizes([total_width // 3, total_width * 2 // 3])
            # 同时调整右侧面板比例
            self._adjust_right_panel_ratio()

    def closeEvent(self, event):
        """关闭事件"""
        self.db.close()
        event.accept()
