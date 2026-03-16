#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专题页面组件 - 劳动法律实务专题
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QStackedWidget, QTextEdit, QLineEdit, QListWidget, QListWidgetItem,
    QSizePolicy, QDialog, QTextBrowser
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.database import Database


class TopicCard(QFrame):
    """专题卡片 - 浅色主题"""
    topic_clicked = pyqtSignal(str)  # topic_id
    
    def __init__(self, topic_id: str, title: str, subtitle: str, icon: str = "📁", parent=None):
        super().__init__(parent)
        self.topic_id = topic_id
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(100)
        self.setMaximumHeight(120)
        # 浅色主题样式
        self.setStyleSheet("""
            TopicCard {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }
            TopicCard:hover {
                background-color: #e3f2fd;
                border-color: #1976d2;
            }
        """)
        self._create_ui(title, subtitle, icon)
    
    def _create_ui(self, title: str, subtitle: str, icon: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # 左侧图标
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("PingFang SC", 32))
        icon_label.setStyleSheet("background: transparent;")
        layout.addWidget(icon_label)
        
        # 右侧文字
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        title_label = QLabel(title)
        title_font = QFont("PingFang SC", 14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #212121; background: transparent;")
        text_layout.addWidget(title_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont("PingFang SC", 10))
        subtitle_label.setStyleSheet("color: #757575; background: transparent;")
        subtitle_label.setWordWrap(True)
        text_layout.addWidget(subtitle_label)
        
        layout.addLayout(text_layout, 1)
        layout.addStretch()
        
        # 箭头指示
        arrow = QLabel("›")
        arrow.setFont(QFont("PingFang SC", 20, QFont.Weight.Bold))
        arrow.setStyleSheet("color: #bdbdbd; background: transparent;")
        layout.addWidget(arrow)
    
    def mousePressEvent(self, event):
        self.topic_clicked.emit(self.topic_id)


class TopicWidget(QWidget):
    """专题页面 - 劳动法律实务专题"""
    topic_selected = pyqtSignal(str, str)  # topic_id, topic_title
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.setStyleSheet("background-color: #f5f5f5;")
        self._create_ui()
        self._load_topics()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题区
        title_card = QFrame()
        title_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        title_layout = QVBoxLayout(title_card)
        
        title = QLabel("📚 劳动法律实务专题")
        title_font = QFont("PingFang SC", 20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976d2;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        
        subtitle = QLabel("精选实务高频问题，快速定位法律依据")
        subtitle.setFont(QFont("PingFang SC", 11))
        subtitle.setStyleSheet("color: #757575;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_card)
        
        # 专题卡片容器 - 2列布局
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background-color: transparent;")
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(self.cards_container, 1)
        
        # 底部提示
        hint_label = QLabel("💡 点击专题卡片查看详细内容")
        hint_label.setFont(QFont("PingFang SC", 10))
        hint_label.setStyleSheet("color: #757575;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)
    
    def _load_topics(self):
        """加载专题卡片"""
        # 定义劳动法律实务常见专题
        topics = [
            {
                'id': 'indefinite_term',
                'title': '无固定期限劳动合同',
                'subtitle': '签订条件、视为订立、违法责任',
                'icon': '📅'
            },
            {
                'id': 'service_years',
                'title': '工龄连续计算',
                'subtitle': '非本人原因调动、关联企业、合并分立',
                'icon': '🔗'
            },
            {
                'id': 'social_insurance',
                'title': '社保缴纳争议',
                'subtitle': '未缴补缴、基数争议、赔偿标准',
                'icon': '💰'
            },
            {
                'id': 'work_injury',
                'title': '工伤认定与赔偿',
                'subtitle': '认定情形、伤残等级、赔偿项目',
                'icon': '🏥'
            },
            {
                'id': 'severance_pay',
                'title': '离职补偿金计算',
                'subtitle': 'N、N+1、2N适用情形及计算标准',
                'icon': '🧮'
            },
            {
                'id': 'overtime',
                'title': '加班费计算',
                'subtitle': '加班认定、计算基数、举证责任',
                'icon': '⏰'
            },
            {
                'id': 'termination',
                'title': '违法解除/终止',
                'subtitle': '违法情形、赔偿金、恢复劳动关系',
                'icon': '⚠️'
            },
            {
                'id': 'probation',
                'title': '试用期管理',
                'subtitle': '期限约定、工资标准、解除限制',
                'icon': '📝'
            },
            {
                'id': 'non_compete',
                'title': '竞业限制',
                'subtitle': '适用对象、补偿标准、违约金',
                'icon': '🔒'
            },
            {
                'id': 'annual_leave',
                'title': '年休假争议',
                'subtitle': '天数计算、未休补偿、时效问题',
                'icon': '🏖️'
            },
            {
                'id': 'maternity',
                'title': '女职工三期保护',
                'subtitle': '孕期、产期、哺乳期特殊保护',
                'icon': '👶'
            },
            {
                'id': 'labor_arbitration',
                'title': '劳动仲裁程序',
                'subtitle': '时效、管辖、证据、执行',
                'icon': '⚖️'
            }
        ]
        
        col = 0
        row = 0
        
        for topic in topics:
            card = TopicCard(
                topic['id'],
                topic['title'],
                topic['subtitle'],
                topic['icon']
            )
            card.topic_clicked.connect(self._on_topic_selected)
            self.cards_layout.addWidget(card, row, col)
            
            col += 1
            if col >= 2:  # 2列换行
                col = 0
                row += 1
    
    def _on_topic_selected(self, topic_id: str):
        """专题被选中"""
        # 找到对应的专题标题
        topics_map = {
            'indefinite_term': '无固定期限劳动合同',
            'service_years': '工龄连续计算',
            'social_insurance': '社保缴纳争议',
            'work_injury': '工伤认定与赔偿',
            'severance_pay': '离职补偿金计算',
            'overtime': '加班费计算',
            'termination': '违法解除/终止',
            'probation': '试用期管理',
            'non_compete': '竞业限制',
            'annual_leave': '年休假争议',
            'maternity': '女职工三期保护',
            'labor_arbitration': '劳动仲裁程序'
        }
        topic_title = topics_map.get(topic_id, '专题')
        self.topic_selected.emit(topic_id, topic_title)
        
        # 暂时显示提示，后续可扩展为详细内容页
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "专题",
            f"【{topic_title}】\n\n该专题内容正在完善中，敬请期待！\n\n您可以通过搜索功能查找相关法律条文。"
        )
