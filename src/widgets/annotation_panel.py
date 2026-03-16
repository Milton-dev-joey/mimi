#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强批注面板 - 支持精确到条款/文本段落的批注
类似 Word 的批注功能
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QDialog, QLineEdit, QComboBox, QMessageBox, QMenu,
    QTextBrowser, QSplitter, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QTextCursor, QColor

from src.database import Database
from src.user_data import UserDataManager, Annotation


class TextSelectionAnnotator(QDialog):
    """文本选择批注对话框 - 选中特定文本后添加批注"""
    def __init__(self, selected_text: str, law_id: str, article_num: str = "", 
                 parent=None):
        super().__init__(parent)
        self.selected_text = selected_text
        self.law_id = law_id
        self.article_num = article_num
        
        self.setWindowTitle("添加批注")
        self.setMinimumSize(500, 400)
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 选中的文本显示
        selected_label = QLabel("📍 选中内容:")
        selected_label.setStyleSheet("color: #569cd6; font-weight: bold;")
        layout.addWidget(selected_label)
        
        self.selected_display = QTextBrowser()
        self.selected_display.setMaximumHeight(100)
        self.selected_display.setStyleSheet("""
            QTextBrowser {
                background-color: #dcdcaa;
                color: #1e1e1e;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        self.selected_display.setText(self.selected_text)
        layout.addWidget(self.selected_display)
        
        # 位置信息
        location = f"法律: {self.law_id}"
        if self.article_num:
            location += f" | 条款: 第{self.article_num}条"
        
        loc_label = QLabel(location)
        loc_label.setStyleSheet("color: #858585; font-size: 11px;")
        layout.addWidget(loc_label)
        
        # 标签输入
        tag_layout = QHBoxLayout()
        tag_layout.addWidget(QLabel("标签:"))
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("用逗号分隔，如: 重点, 经济补偿, 计算标准")
        tag_layout.addWidget(self.tag_input)
        layout.addLayout(tag_layout)
        
        # 内容编辑
        content_label = QLabel("📝 批注内容:")
        content_label.setStyleSheet("color: #4ec9b0; font-weight: bold;")
        layout.addWidget(content_label)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("在此输入批注内容...")
        self.content_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d30;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.content_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 保存批注")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 24px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _save(self):
        """保存"""
        content = self.content_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "提示", "请输入批注内容")
            return
        
        self.result_data = {
            'content': content,
            'tags': [t.strip() for t in self.tag_input.text().split(",") if t.strip()],
            'selected_text': self.selected_text,
            'law_id': self.law_id,
            'article_num': self.article_num
        }
        self.accept()
    
    def get_data(self):
        """获取数据"""
        return getattr(self, 'result_data', None)


class AnnotationItem(QFrame):
    """批注项显示组件"""
    edit_clicked = pyqtSignal(int)  # anno_id
    delete_clicked = pyqtSignal(int)  # anno_id
    
    def __init__(self, annotation: Annotation, parent=None):
        super().__init__(parent)
        self.annotation = annotation
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            AnnotationItem {
                background-color: #2d2d30;
                border-left: 3px solid #0e639c;
                border-radius: 4px;
                padding: 10px;
                margin: 5px 0;
            }
        """)
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        
        # 头部：条款信息 + 操作按钮
        header = QHBoxLayout()
        
        if self.annotation.article_num:
            article_label = QLabel(f"📍 第{self.annotation.article_num}条")
            article_label.setStyleSheet("color: #569cd6; font-weight: bold;")
            header.addWidget(article_label)
        
        header.addStretch()
        
        # 编辑按钮
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(28, 28)
        edit_btn.setStyleSheet("background: transparent; border: none;")
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.annotation.id))
        header.addWidget(edit_btn)
        
        # 删除按钮
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("background: transparent; border: none;")
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.annotation.id))
        header.addWidget(delete_btn)
        
        layout.addLayout(header)
        
        # 批注内容
        content = QLabel(self.annotation.content)
        content.setWordWrap(True)
        content.setStyleSheet("color: #cccccc; font-size: 13px; padding: 5px 0;")
        layout.addWidget(content)
        
        # 标签
        if self.annotation.tags:
            tags = QLabel(f"🏷️ {', '.join(self.annotation.tags)}")
            tags.setStyleSheet("color: #858585; font-size: 11px;")
            layout.addWidget(tags)
        
        # 时间
        time_str = self.annotation.created_at[:10] if len(self.annotation.created_at) > 10 else self.annotation.created_at
        time_label = QLabel(f"🕐 {time_str}")
        time_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(time_label)


class AnnotationPanel(QWidget):
    """增强批注面板 - 支持精确到条款和选中文本"""
    annotation_updated = pyqtSignal()
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.udm = UserDataManager(db.conn)
        self.current_law_id = None
        self.current_article_num = None
        self.current_law_title = ""
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel("📝 批注管理")
        title_font = QFont("PingFang SC", 14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #cccccc;")
        layout.addWidget(title)
        
        # 使用说明
        help_label = QLabel("💡 在法律内容中选中文字，右键可添加批注")
        help_label.setStyleSheet("color: #858585; font-size: 11px; padding: 5px;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        # 位置信息
        self.location_frame = QFrame()
        self.location_frame.setStyleSheet("""
            QFrame {
                background-color: #094771;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        location_layout = QVBoxLayout(self.location_frame)
        location_layout.setContentsMargins(10, 8, 10, 8)
        location_layout.setSpacing(4)
        
        self.location_title = QLabel("未选择法律")
        self.location_title.setStyleSheet("color: #cccccc; font-weight: bold; font-size: 13px;")
        location_layout.addWidget(self.location_title)
        
        self.location_article = QLabel("")
        self.location_article.setStyleSheet("color: #569cd6; font-size: 11px;")
        location_layout.addWidget(self.location_article)
        
        layout.addWidget(self.location_frame)
        
        # 快速添加批注按钮
        self.add_btn = QPushButton("➕ 添加批注")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #666;
            }
        """)
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._add_annotation)
        layout.addWidget(self.add_btn)
        
        # 筛选
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("🔍 筛选批注...")
        self.filter_input.textChanged.connect(self._filter_annotations)
        filter_layout.addWidget(self.filter_input)
        
        clear_btn = QPushButton("清除")
        clear_btn.setFixedWidth(60)
        clear_btn.clicked.connect(self.filter_input.clear)
        filter_layout.addWidget(clear_btn)
        layout.addLayout(filter_layout)
        
        # 批注列表区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.anno_container = QWidget()
        self.anno_layout = QVBoxLayout(self.anno_container)
        self.anno_layout.setContentsMargins(0, 0, 0, 0)
        self.anno_layout.setSpacing(8)
        self.anno_layout.addStretch()
        
        scroll.setWidget(self.anno_container)
        layout.addWidget(scroll)
        
        # 统计
        self.stats_label = QLabel("暂无批注")
        self.stats_label.setStyleSheet("color: #858585; font-size: 11px; padding: 5px;")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)
    
    def set_location(self, law_id: str, article_num: str = "", law_title: str = ""):
        """设置当前位置"""
        self.current_law_id = law_id
        self.current_article_num = article_num
        self.current_law_title = law_title if law_title else law_id
        
        self.location_title.setText(self.current_law_title)
        if article_num:
            self.location_article.setText(f"当前条款: 第{article_num}条")
        else:
            self.location_article.setText("点击条款可定位批注")
        
        self.add_btn.setEnabled(True)
        self._load_annotations()
    
    def add_annotation_for_selection(self, selected_text: str, article_num: str = ""):
        """为选中的文本添加批注"""
        if not self.current_law_id:
            QMessageBox.warning(self, "提示", "请先选择法律")
            return
        
        dialog = TextSelectionAnnotator(
            selected_text,
            self.current_law_id,
            article_num or self.current_article_num,
            parent=self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data:
                self.udm.add_annotation(
                    law_id=data['law_id'],
                    article_num=data['article_num'],
                    content=f"【选中: {data['selected_text'][:30]}...】\n\n{data['content']}",
                    tags=data['tags']
                )
                self._load_annotations()
                self.annotation_updated.emit()
    
    def _load_annotations(self):
        """加载批注列表"""
        # 清除现有批注项（保留 stretch）
        while self.anno_layout.count() > 1:
            item = self.anno_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.current_law_id:
            self.stats_label.setText("请先选择法律")
            return
        
        annotations = self.udm.get_annotations(
            self.current_law_id,
            self.current_article_num if self.current_article_num else None
        )
        
        # 存储批注用于筛选
        self.all_annotations = annotations
        
        self._display_annotations(annotations)
    
    def _display_annotations(self, annotations):
        """显示批注列表"""
        # 清除现有
        while self.anno_layout.count() > 1:
            item = self.anno_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not annotations:
            empty_label = QLabel("暂无批注，选中文字添加")
            empty_label.setStyleSheet("color: #666; padding: 20px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.anno_layout.insertWidget(0, empty_label)
            self.stats_label.setText("暂无批注")
        else:
            for anno in annotations:
                item = AnnotationItem(anno)
                item.edit_clicked.connect(self._edit_annotation)
                item.delete_clicked.connect(self._delete_annotation)
                self.anno_layout.insertWidget(self.anno_layout.count() - 1, item)
            
            self.stats_label.setText(f"共 {len(annotations)} 条批注")
    
    def _filter_annotations(self, text: str):
        """筛选批注"""
        if not text:
            self._display_annotations(self.all_annotations)
            return
        
        filtered = [a for a in self.all_annotations 
                   if text.lower() in a.content.lower() 
                   or any(text.lower() in t.lower() for t in a.tags)]
        self._display_annotations(filtered)
    
    def _add_annotation(self):
        """添加批注"""
        if not self.current_law_id:
            QMessageBox.warning(self, "提示", "请先选择法律")
            return
        
        # 简单批注对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("添加批注")
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"📍 {self.current_law_title}"))
        if self.current_article_num:
            layout.addWidget(QLabel(f"条款: 第{self.current_article_num}条"))
        
        tag_input = QLineEdit()
        tag_input.setPlaceholderText("标签，用逗号分隔")
        layout.addWidget(tag_input)
        
        content_edit = QTextEdit()
        content_edit.setPlaceholderText("输入批注内容...")
        layout.addWidget(content_edit)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
            }
        """)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        def do_save():
            content = content_edit.toPlainText().strip()
            if not content:
                QMessageBox.warning(dialog, "提示", "请输入内容")
                return
            
            tags = [t.strip() for t in tag_input.text().split(",") if t.strip()]
            self.udm.add_annotation(
                self.current_law_id,
                self.current_article_num,
                content,
                tags
            )
            dialog.accept()
        
        save_btn.clicked.connect(do_save)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_annotations()
            self.annotation_updated.emit()
    
    def _edit_annotation(self, anno_id: int):
        """编辑批注"""
        annotations = self.udm.get_annotations(self.current_law_id)
        anno = next((a for a in annotations if a.id == anno_id), None)
        if not anno:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑批注")
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        tag_input = QLineEdit()
        tag_input.setText(", ".join(anno.tags))
        layout.addWidget(QLabel("标签:"))
        layout.addWidget(tag_input)
        
        content_edit = QTextEdit()
        content_edit.setPlainText(anno.content)
        layout.addWidget(QLabel("内容:"))
        layout.addWidget(content_edit)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(lambda: self._do_edit(dialog, anno_id, content_edit, tag_input))
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec()
    
    def _do_edit(self, dialog, anno_id, content_edit, tag_input):
        """执行编辑"""
        content = content_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(dialog, "提示", "请输入内容")
            return
        
        tags = [t.strip() for t in tag_input.text().split(",") if t.strip()]
        self.udm.update_annotation(anno_id, content, tags)
        dialog.accept()
        self._load_annotations()
        self.annotation_updated.emit()
    
    def _delete_annotation(self, anno_id: int):
        """删除批注"""
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这条批注吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.udm.delete_annotation(anno_id)
            self._load_annotations()
            self.annotation_updated.emit()
