#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例管理面板
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QDialog, QLineEdit, QComboBox, QMessageBox, QMenu,
    QTabWidget, QFormLayout, QTextBrowser, QSplitter,
    QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.database import Database
from src.user_data import UserDataManager, Case


class CaseEditDialog(QDialog):
    """案例编辑对话框"""
    def __init__(self, case: Case = None, parent=None):
        super().__init__(parent)
        self.case = case
        self.setWindowTitle("编辑案例" if case else "添加案例")
        self.setMinimumSize(700, 600)
        self._create_ui()
        if case:
            self._load_data()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # 标题
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("案例标题")
        form_layout.addRow("标题*:", self.title_input)
        
        # 类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(["现实案件", "参考案例"])
        self.type_combo.setCurrentIndex(0)
        form_layout.addRow("类型:", self.type_combo)
        
        # 标签
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("用逗号分隔，如: 违法解除, 赔偿金, 2N")
        form_layout.addRow("标签:", self.tags_input)
        
        layout.addLayout(form_layout)
        
        # 摘要
        layout.addWidget(QLabel("案例摘要:"))
        self.summary_edit = QTextEdit()
        self.summary_edit.setPlaceholderText("简要描述案例要点...")
        self.summary_edit.setMaximumHeight(80)
        layout.addWidget(self.summary_edit)
        
        # 详细内容 - 使用标签页
        tabs = QTabWidget()
        
        # 事实
        self.facts_edit = QTextEdit()
        self.facts_edit.setPlaceholderText("案件事实...")
        tabs.addTab(self.facts_edit, "案件事实")
        
        # 争议焦点
        self.issues_edit = QTextEdit()
        self.issues_edit.setPlaceholderText("争议焦点...")
        tabs.addTab(self.issues_edit, "争议焦点")
        
        # 裁判结果
        self.ruling_edit = QTextEdit()
        self.ruling_edit.setPlaceholderText("裁判结果...")
        tabs.addTab(self.ruling_edit, "裁判结果")
        
        # 备注
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("其他备注信息...")
        tabs.addTab(self.notes_edit, "备注")
        
        layout.addWidget(tabs)
        
        # 相关法律
        layout.addWidget(QLabel("相关法律（JSON格式，可选）:"))
        self.laws_edit = QTextEdit()
        self.laws_edit.setPlaceholderText('[{"law_id": "hf_000373", "article_num": "第四十七条"}]')
        self.laws_edit.setMaximumHeight(60)
        layout.addWidget(self.laws_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
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
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_data(self):
        """加载现有数据"""
        if not self.case:
            return
        
        self.title_input.setText(self.case.title)
        self.type_combo.setCurrentIndex(0 if self.case.case_type == "actual" else 1)
        self.tags_input.setText(", ".join(self.case.tags))
        self.summary_edit.setPlainText(self.case.summary)
        self.facts_edit.setPlainText(self.case.facts)
        self.issues_edit.setPlainText(self.case.issues)
        self.ruling_edit.setPlainText(self.case.ruling)
        self.notes_edit.setPlainText(self.case.notes)
        
        import json
        self.laws_edit.setPlainText(json.dumps(self.case.related_laws, ensure_ascii=False, indent=2))
    
    def _save(self):
        """保存"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入案例标题")
            return
        
        case_type = "actual" if self.type_combo.currentIndex() == 0 else "reference"
        tags = [t.strip() for t in self.tags_input.text().split(",") if t.strip()]
        
        # 解析相关法律JSON
        related_laws = []
        laws_text = self.laws_edit.toPlainText().strip()
        if laws_text:
            try:
                import json
                related_laws = json.loads(laws_text)
            except:
                QMessageBox.warning(self, "提示", "相关法律JSON格式错误")
                return
        
        self.data = {
            'title': title,
            'case_type': case_type,
            'tags': tags,
            'summary': self.summary_edit.toPlainText(),
            'facts': self.facts_edit.toPlainText(),
            'issues': self.issues_edit.toPlainText(),
            'ruling': self.ruling_edit.toPlainText(),
            'notes': self.notes_edit.toPlainText(),
            'related_laws': related_laws
        }
        
        self.accept()
    
    def get_data(self):
        """获取数据"""
        return self.data


class CasePanel(QWidget):
    """案例管理面板"""
    case_selected = pyqtSignal(int)  # case_id
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.udm = UserDataManager(db.conn)
        self._create_ui()
        self._load_cases()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # 标题
        title = QLabel("📁 案例管理")
        title_font = QFont("PingFang SC", 13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #cccccc;")
        layout.addWidget(title)
        
        # 筛选
        filter_layout = QHBoxLayout()
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["全部", "现实案件", "参考案例"])
        self.type_filter.currentIndexChanged.connect(self._load_cases)
        filter_layout.addWidget(QLabel("类型:"))
        filter_layout.addWidget(self.type_filter)
        
        self.tag_filter = QLineEdit()
        self.tag_filter.setPlaceholderText("标签筛选...")
        self.tag_filter.returnPressed.connect(self._load_cases)
        filter_layout.addWidget(self.tag_filter)
        
        filter_btn = QPushButton("筛选")
        filter_btn.clicked.connect(self._load_cases)
        filter_layout.addWidget(filter_btn)
        
        layout.addLayout(filter_layout)
        
        # 添加按钮
        add_btn = QPushButton("+ 添加案例")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        add_btn.clicked.connect(self._add_case)
        layout.addWidget(add_btn)
        
        # 案例列表
        self.case_list = QListWidget()
        self.case_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #3c3c3c;
            }
            QListWidget::item:selected {
                background-color: #094771;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
        """)
        self.case_list.itemDoubleClicked.connect(self._view_case)
        self.case_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.case_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.case_list)
        
        # 统计
        self.stats_label = QLabel("暂无案例")
        self.stats_label.setStyleSheet("color: #858585; font-size: 11px;")
        layout.addWidget(self.stats_label)
    
    def _load_cases(self):
        """加载案例列表"""
        self.case_list.clear()
        
        # 获取筛选条件
        type_idx = self.type_filter.currentIndex()
        case_type = None if type_idx == 0 else ("actual" if type_idx == 1 else "reference")
        
        tag_text = self.tag_filter.text().strip()
        tags = [t.strip() for t in tag_text.split(",") if t.strip()] if tag_text else None
        
        # 查询
        cases = self.udm.get_cases(case_type=case_type, tags=tags)
        
        for case in cases:
            item = QListWidgetItem()
            
            # 类型标记
            type_mark = "【现实】" if case.case_type == "actual" else "【参考】"
            
            # 标签显示
            tags_str = f" [{', '.join(case.tags[:3])}]" if case.tags else ""
            
            # 摘要预览
            summary = case.summary[:30] + "..." if len(case.summary) > 30 else case.summary
            
            display = f"{type_mark} {case.title}{tags_str}\n    {summary}"
            
            item.setText(display)
            item.setData(Qt.ItemDataRole.UserRole, case.id)
            item.setToolTip(case.summary if case.summary else case.title)
            
            self.case_list.addItem(item)
        
        self.stats_label.setText(f"共 {len(cases)} 个案例")
    
    def _add_case(self):
        """添加案例"""
        dialog = CaseEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.udm.add_case(**data)
            self._load_cases()
    
    def _edit_case(self, case_id: int):
        """编辑案例"""
        case = self.udm.get_case_by_id(case_id)
        if not case:
            return
        
        dialog = CaseEditDialog(case, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.udm.update_case(case_id, **data)
            self._load_cases()
    
    def _delete_case(self, case_id: int):
        """删除案例"""
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这个案例吗？\n此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.udm.delete_case(case_id)
            self._load_cases()
    
    def _view_case(self, item: QListWidgetItem):
        """查看案例详情"""
        case_id = item.data(Qt.ItemDataRole.UserRole)
        case = self.udm.get_case_by_id(case_id)
        if not case:
            return
        
        dialog = CaseDetailDialog(case, self)
        dialog.exec()
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.case_list.itemAt(position)
        if not item:
            return
        
        case_id = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        view_action = menu.addAction("查看详情")
        view_action.triggered.connect(lambda: self._view_case(item))
        
        edit_action = menu.addAction("编辑")
        edit_action.triggered.connect(lambda: self._edit_case(case_id))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("删除")
        delete_action.triggered.connect(lambda: self._delete_case(case_id))
        
        menu.exec(self.case_list.mapToGlobal(position))


class CaseDetailDialog(QDialog):
    """案例详情对话框"""
    def __init__(self, case: Case, parent=None):
        super().__init__(parent)
        self.case = case
        self.setWindowTitle(case.title)
        self.setMinimumSize(600, 500)
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel(self.case.title)
        title_font = QFont("PingFang SC", 16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #569cd6;")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # 类型标签
        type_label = QLabel("现实案件" if self.case.case_type == "actual" else "参考案例")
        type_label.setStyleSheet("""
            color: #cccccc;
            background-color: #094771;
            padding: 4px 12px;
            border-radius: 4px;
            display: inline-block;
        """)
        layout.addWidget(type_label)
        
        # 标签
        if self.case.tags:
            tags_label = QLabel(f"标签: {', '.join(self.case.tags)}")
            tags_label.setStyleSheet("color: #858585; margin: 8px 0;")
            layout.addWidget(tags_label)
        
        # 内容
        content = QTextBrowser()
        html = self._build_html()
        content.setHtml(html)
        layout.addWidget(content)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def _build_html(self) -> str:
        """构建HTML内容"""
        sections = []
        
        if self.case.summary:
            sections.append(("摘要", self.case.summary))
        if self.case.facts:
            sections.append(("案件事实", self.case.facts))
        if self.case.issues:
            sections.append(("争议焦点", self.case.issues))
        if self.case.ruling:
            sections.append(("裁判结果", self.case.ruling))
        if self.case.notes:
            sections.append(("备注", self.case.notes))
        
        html_parts = ["""
        <style>
            body {
                font-family: "PingFang SC", sans-serif;
                font-size: 14px;
                line-height: 1.6;
                color: #d4d4d4;
            }
            h3 {
                color: #4ec9b0;
                border-bottom: 1px solid #3c3c3c;
                padding-bottom: 8px;
                margin-top: 20px;
            }
            p {
                margin: 10px 0;
            }
        </style>
        """]
        
        for title, content in sections:
            html_parts.append(f"<h3>{title}</h3>")
            html_parts.append(f"<p>{content.replace(chr(10), '<br>')}</p>")
        
        return "\n".join(html_parts)
