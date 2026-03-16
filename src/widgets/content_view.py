#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法律内容展示组件 - 浅色主题
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser,
    QLabel, QPushButton, QComboBox, QScrollArea,
    QFrame, QSplitter, QTabWidget, QLineEdit, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QTextCursor

from src.database import Database, Law, LawArticle


class ContentViewWidget(QWidget):
    """法律内容展示区 - 浅色主题"""
    
    article_clicked = pyqtSignal(str, str)  # law_id, article_num
    text_selected = pyqtSignal(str)  # selected_text
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_law = None
        self.articles = []
        self.setStyleSheet("background-color: #ffffff;")
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 顶部信息栏 - 浅色
        self.header = QFrame()
        self.header.setFrameShape(QFrame.Shape.StyledPanel)
        self.header.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
        """)
        header_layout = QVBoxLayout(self.header)
        header_layout.setSpacing(8)
        
        # 法律标题
        self.title_label = QLabel("请选择法律")
        title_font = QFont("PingFang SC", 16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("color: #1976d2;")
        header_layout.addWidget(self.title_label)
        
        # 元信息行
        meta_layout = QHBoxLayout()
        
        self.meta_label = QLabel("")
        self.meta_label.setStyleSheet("color: #757575;")
        meta_layout.addWidget(self.meta_label)
        meta_layout.addStretch()
        
        # 收藏按钮
        self.fav_btn = QPushButton("☆ 收藏")
        self.fav_btn.setMaximumWidth(80)
        self.fav_btn.setStyleSheet("""
            QPushButton {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 1px solid #1976d2;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover {
                background-color: #1976d2;
                color: white;
            }
        """)
        meta_layout.addWidget(self.fav_btn)
        
        header_layout.addLayout(meta_layout)
        layout.addWidget(self.header)
        
        # 内容区域
        content_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 目录导航
        self.toc_widget = QWidget()
        self.toc_widget.setStyleSheet("background-color: #fafafa;")
        toc_layout = QVBoxLayout(self.toc_widget)
        toc_layout.setContentsMargins(0, 0, 0, 0)
        
        toc_label = QLabel("📋 条文目录")
        toc_label.setStyleSheet("font-weight: bold; color: #424242;")
        toc_layout.addWidget(toc_label)
        
        self.toc_combo = QComboBox()
        self.toc_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.toc_combo.currentIndexChanged.connect(self._on_toc_selected)
        toc_layout.addWidget(self.toc_combo)
        
        content_splitter.addWidget(self.toc_widget)
        self.toc_widget.setMaximumHeight(100)
        
        # 内容阅读器 - 浅色主题
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                color: #212121;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 12px;
                line-height: 1.8;
            }
        """)
        
        # 设置字体
        content_font = QFont("PingFang SC", 11)
        content_font.setStyleHint(QFont.StyleHint.SansSerif)
        self.content_browser.setFont(content_font)
        
        # 启用上下文菜单
        self.content_browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.content_browser.customContextMenuRequested.connect(self._show_context_menu)
        
        content_splitter.addWidget(self.content_browser)
        content_splitter.setSizes([80, 600])
        
        layout.addWidget(content_splitter)
        
        # 底部工具栏
        toolbar = QHBoxLayout()
        
        self.prev_btn = QPushButton("◀ 上一条")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #424242;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.prev_btn.clicked.connect(self._prev_article)
        self.prev_btn.setEnabled(False)
        toolbar.addWidget(self.prev_btn)
        
        toolbar.addStretch()
        
        self.article_nav = QLabel("")
        self.article_nav.setStyleSheet("color: #757575;")
        toolbar.addWidget(self.article_nav)
        
        toolbar.addStretch()
        
        self.next_btn = QPushButton("下一条 ▶")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #424242;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.next_btn.clicked.connect(self._next_article)
        self.next_btn.setEnabled(False)
        toolbar.addWidget(self.next_btn)
        
        layout.addLayout(toolbar)
    
    def load_law(self, law_id: str):
        """加载法律"""
        law = self.db.get_law_by_id(law_id)
        if not law:
            return
        
        self.current_law = law
        self.articles = self.db.get_law_articles(law_id)
        
        # 更新标题
        self.title_label.setText(law.title)
        
        # 更新元信息
        meta_parts = []
        if law.type:
            meta_parts.append(f"位阶：{law.type}")
        if law.publish:
            meta_parts.append(f"发布：{law.publish}")
        if law.status and law.status != "未知":
            meta_parts.append(f"状态：{law.status}")
        if law.office:
            meta_parts.append(f"发布机关：{law.office}")
        
        self.meta_label.setText(" | ".join(meta_parts))
        
        # 更新目录
        self._update_toc()
        
        # 渲染内容
        self._render_content()
    
    def load_article(self, law_id: str, article_num: str):
        """跳转到指定条文"""
        if not self.current_law or self.current_law.id != law_id:
            self.load_law(law_id)
        
        # 在内容中查找并高亮
        search_text = f"第{article_num}条"
        self.content_browser.find(search_text)
    
    def _update_toc(self):
        """更新目录"""
        self.toc_combo.clear()
        self.toc_combo.addItem("-- 选择条文 --", "")
        
        for article in self.articles:
            display = f"第{article.article_num}条"
            if article.chapter:
                display = f"{article.chapter} - {display}"
            self.toc_combo.addItem(display, article.article_num)
    
    def _render_content(self):
        """渲染法律内容 - 浅色主题"""
        if not self.current_law:
            return
        
        html_parts = []
        
        # 添加样式 - 浅色主题
        html_parts.append("""
        <style>
            body {
                font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
                font-size: 14px;
                line-height: 1.8;
                color: #212121;
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #1976d2;
                font-size: 20px;
                border-bottom: 2px solid #1976d2;
                padding-bottom: 10px;
            }
            h2 {
                color: #424242;
                font-size: 16px;
                margin-top: 20px;
            }
            .article {
                margin: 15px 0;
                padding: 10px;
                background: #fafafa;
                border-left: 3px solid #1976d2;
            }
            .article-num {
                color: #1976d2;
                font-weight: bold;
            }
            .chapter {
                color: #d32f2f;
                font-size: 15px;
                margin: 20px 0 10px 0;
                padding: 5px 0;
                border-bottom: 1px solid #e0e0e0;
            }
        </style>
        """)
        
        # 添加标题
        html_parts.append(f"<h1>{self.current_law.title}</h1>")
        
        # 如果有内容直接显示
        if self.current_law.content:
            content = self.current_law.content.replace('\n', '<br>')
            html_parts.append(f"<div>{content}</div>")
        
        # 显示结构化条文
        if self.articles:
            html_parts.append("<h2>条文</h2>")
            
            current_chapter = None
            for article in self.articles:
                # 显示章节标题
                if article.chapter and article.chapter != current_chapter:
                    current_chapter = article.chapter
                    html_parts.append(f'<div class="chapter">{current_chapter}</div>')
                
                # 显示条文
                html_parts.append(f'''
                <div class="article" id="article-{article.article_num}">
                    <span class="article-num">第{article.article_num}条</span> 
                    {article.article_text}
                </div>
                ''')
        
        html = "\n".join(html_parts)
        self.content_browser.setHtml(html)
        
        # 更新导航按钮状态
        self.prev_btn.setEnabled(len(self.articles) > 0)
        self.next_btn.setEnabled(len(self.articles) > 0)
    
    def _on_toc_selected(self, index: int):
        """目录选择"""
        if index <= 0:
            return
        
        article_num = self.toc_combo.currentData()
        if article_num:
            self.load_article(self.current_law.id, article_num)
    
    def _prev_article(self):
        """上一条"""
        current = self.toc_combo.currentIndex()
        if current > 1:
            self.toc_combo.setCurrentIndex(current - 1)
    
    def _next_article(self):
        """下一条"""
        current = self.toc_combo.currentIndex()
        if current < self.toc_combo.count() - 1:
            self.toc_combo.setCurrentIndex(current + 1)
    
    def _show_context_menu(self, position):
        """显示右键菜单 - 支持选中文字添加批注"""
        # 获取选中的文本
        cursor = self.content_browser.textCursor()
        selected_text = cursor.selectedText().strip()
        
        menu = QMenu(self)
        menu.setStyleSheet("""
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
        
        if selected_text:
            # 如果有选中的文字，显示添加批注选项
            anno_action = menu.addAction(f"📝 对选中文字添加批注")
            anno_action.triggered.connect(lambda: self.text_selected.emit(selected_text))
            
            menu.addSeparator()
        
        # 复制选项
        copy_action = menu.addAction("复制")
        copy_action.triggered.connect(self.content_browser.copy)
        
        menu.addSeparator()
        
        # 选择全部
        select_all_action = menu.addAction("选择全部")
        select_all_action.triggered.connect(self.content_browser.selectAll)
        
        menu.exec(self.content_browser.mapToGlobal(position))
