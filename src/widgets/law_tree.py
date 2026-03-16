#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法律位阶树形列表组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QLineEdit, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from src.database import Database, Law


class LawTreeWidget(QWidget):
    """法律树形列表"""
    
    law_selected = pyqtSignal(str)  # 发送法律ID
    
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_filter = None
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel("📚 法律法规")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # 快速筛选
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("筛选当前列表...")
        self.filter_input.textChanged.connect(self._filter_tree)
        filter_layout.addWidget(self.filter_input)
        
        clear_btn = QPushButton("清除")
        clear_btn.setMaximumWidth(50)
        clear_btn.clicked.connect(self.filter_input.clear)
        filter_layout.addWidget(clear_btn)
        layout.addLayout(filter_layout)
        
        # 树形控件
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # 设置字体
        tree_font = QFont("PingFang SC", 10)
        self.tree.setFont(tree_font)
        
        layout.addWidget(self.tree)
    
    def load_data(self):
        """加载数据"""
        self.tree.clear()
        
        # 按位阶分组
        type_hierarchy = self.db.get_type_hierarchy()
        
        # 位阶排序和中文名映射
        type_order = ['法律', '行政法规', '部门规章', '地方性法规', '地方政府规章', '司法解释', '其他']
        
        for type_name in type_order:
            if type_name not in type_hierarchy:
                continue
            
            laws = type_hierarchy[type_name]
            if not laws:
                continue
            
            # 创建位阶节点
            type_item = QTreeWidgetItem(self.tree)
            type_item.setText(0, f"{type_name} ({len(laws)})")
            type_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "category", "name": type_name})
            type_item.setExpanded(True)
            
            # 添加法律子项
            for law in laws:
                law_item = QTreeWidgetItem(type_item)
                law_item.setText(0, law.title)
                law_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "law", "id": law.id})
                
                # 根据状态设置颜色
                if law.status == "已废止":
                    law_item.setForeground(0, Qt.GlobalColor.gray)
                elif law.status == "已修改":
                    law_item.setForeground(0, Qt.GlobalColor.yellow)
    
    def filter_by_type(self, type_code: str = None):
        """按位阶筛选"""
        self.current_filter = type_code
        self.load_data()
    
    def _filter_tree(self, text: str):
        """树形筛选"""
        text = text.lower()
        
        for i in range(self.tree.topLevelItemCount()):
            category_item = self.tree.topLevelItem(i)
            category_visible = False
            
            for j in range(category_item.childCount()):
                law_item = category_item.child(j)
                law_text = law_item.text(0).lower()
                
                if text in law_text:
                    law_item.setHidden(False)
                    category_visible = True
                else:
                    law_item.setHidden(True)
            
            category_item.setHidden(not category_visible)
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """单击处理"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data.get("type") == "law":
            law_id = data.get("id")
            self.law_selected.emit(law_id)
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """双击展开/折叠"""
        item.setExpanded(not item.isExpanded())
