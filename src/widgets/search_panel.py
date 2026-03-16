#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索面板组件 - 浅色主题（简化为当前法律内搜索）
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.database import Database


class SearchPanel(QWidget):
    """搜索面板 - 简化为当前法律内搜索"""

    law_selected = pyqtSignal(str)  # law_id
    article_selected = pyqtSignal(str, str)  # law_id, article_num

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_law_id = None
        self.setVisible(False)
        self.setStyleSheet("background-color: #ffffff;")
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 标题
        title = QLabel("🔍 当前法律内搜索")
        title_font = QFont("PingFang SC", 12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976d2;")
        layout.addWidget(title)

        # 提示文字
        hint = QLabel("在正在阅读的法律中搜索条文")
        hint.setStyleSheet("color: #757575; font-size: 11px;")
        layout.addWidget(hint)

        # 搜索输入
        input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词...")
        self.search_input.setStyleSheet("""
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
        self.search_input.returnPressed.connect(self._do_search)
        input_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("搜索")
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        self.search_btn.clicked.connect(self._do_search)
        input_layout.addWidget(self.search_btn)
        layout.addLayout(input_layout)

        # 结果统计
        self.stats_label = QLabel("请输入关键词进行搜索")
        self.stats_label.setStyleSheet("color: #757575;")
        layout.addWidget(self.stats_label)

        # 搜索结果列表 - 浅色主题
        self.results_list = QListWidget()
        self.results_list.setAlternatingRowColors(True)
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                color: #212121;
            }
            QListWidget::item {
                padding: 10px;
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
        self.results_list.itemClicked.connect(self._on_result_clicked)
        self.results_list.itemDoubleClicked.connect(self._on_result_double_clicked)

        layout.addWidget(self.results_list)

        layout.addStretch()

        # 底部按钮
        btn_layout = QHBoxLayout()

        clear_btn = QPushButton("清除")
        clear_btn.setStyleSheet("""
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
        clear_btn.clicked.connect(self.clear_results)
        btn_layout.addWidget(clear_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(lambda: self.setVisible(False))
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
    
    def set_current_law(self, law_id: str):
        """设置当前法律"""
        self.current_law_id = law_id
        self.clear_results()

    def search(self, keyword: str = None):
        """执行搜索"""
        if keyword:
            self.search_input.setText(keyword)
        self._do_search()
        self.setVisible(True)

    def _do_search(self):
        """执行当前法律内搜索"""
        keyword = self.search_input.text().strip()
        if not keyword:
            return

        if not self.current_law_id:
            self.stats_label.setText("请先选择一部法律")
            return

        self.results_list.clear()
        self.stats_label.setText("搜索中...")

        try:
            # 在当前法律的条文中搜索
            sql = """
                SELECT * FROM law_articles
                WHERE law_id = ? AND article_text LIKE ?
                ORDER BY sort_order, id
            """
            pattern = f"%{keyword}%"
            self.db.cursor.execute(sql, (self.current_law_id, pattern))
            rows = self.db.cursor.fetchall()

            self._display_article_results(rows, keyword)
        except Exception as e:
            self.stats_label.setText(f"搜索出错：{str(e)}")
            return

        count = self.results_list.count()
        if count == 0:
            self.stats_label.setText(f"未找到包含「{keyword}」的条文")
        else:
            self.stats_label.setText(f"找到 {count} 条相关条文")

    def _display_article_results(self, rows, keyword: str):
        """显示条文搜索结果"""
        for row in rows:
            item = QListWidgetItem()
            article_num = row['article_num']
            display = f"第{article_num}条"
            if row['chapter']:
                display = f"{row['chapter']} - {display}"
            item.setText(display)
            item.setData(Qt.ItemDataRole.UserRole, {
                "type": "article",
                "law_id": row['law_id'],
                "article_num": article_num
            })

            # 截取包含关键词的上下文
            text = row['article_text']
            idx = text.lower().find(keyword.lower())
            if idx >= 0:
                start = max(0, idx - 30)
                end = min(len(text), idx + len(keyword) + 30)
                context = text[start:end]
                item.setToolTip(f"...{context}...")

            self.results_list.addItem(item)

    def _on_result_clicked(self, item: QListWidgetItem):
        """结果点击"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        if data["type"] == "article":
            self.stats_label.setText(f"条文编号：{data['article_num']}")

    def _on_result_double_clicked(self, item: QListWidgetItem):
        """结果双击 - 跳转到条文"""
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        if data["type"] == "article":
            self.article_selected.emit(data['law_id'], data['article_num'])

    def clear_results(self):
        """清除结果"""
        self.results_list.clear()
        self.search_input.clear()
        self.stats_label.setText("请输入关键词进行搜索")
