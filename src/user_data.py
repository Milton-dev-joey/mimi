#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库扩展 - 用户功能表
批注、案件管理、个人笔记
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json


# ==================== 数据模型 ====================

@dataclass
class Annotation:
    """批注"""
    id: int
    law_id: str
    article_num: Optional[str]  # 空表示对整个法律的批注
    content: str
    tags: List[str]
    created_at: str
    updated_at: str


@dataclass
class Case:
    """案件"""
    id: int
    title: str
    case_type: str  # 'reference' 参考案件 / 'actual' 现实案件
    summary: str
    facts: str
    issues: str  # 争议焦点
    ruling: str  # 裁判结果
    notes: str
    related_laws: List[Dict[str, str]]  # [{"law_id": "xxx", "article_num": "xx"}]
    tags: List[str]
    attachments: List[str]  # 附件路径
    created_at: str
    updated_at: str


@dataclass
class UserNote:
    """用户笔记"""
    id: int
    title: str
    content: str
    related_law_id: Optional[str]
    related_article_num: Optional[str]
    tags: List[str]
    created_at: str
    updated_at: str


# ==================== 数据库管理器 ====================

class UserDataManager:
    """用户数据管理器"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.cursor = db_connection.cursor()
        self._ensure_tables()
    
    def _ensure_tables(self):
        """确保用户表存在"""
        
        # 批注表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                law_id TEXT NOT NULL REFERENCES laws(id),
                article_num TEXT DEFAULT '',
                content TEXT NOT NULL,
                tags TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # 创建索引
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_annotations_law 
            ON annotations(law_id, article_num)
        """)
        
        # 案件表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                case_type TEXT NOT NULL DEFAULT 'actual',
                summary TEXT DEFAULT '',
                facts TEXT DEFAULT '',
                issues TEXT DEFAULT '',
                ruling TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                related_laws TEXT DEFAULT '[]',
                tags TEXT DEFAULT '[]',
                attachments TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # 用户笔记表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                related_law_id TEXT DEFAULT '',
                related_article_num TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        self.conn.commit()
    
    # ==================== 批注 CRUD ====================
    
    def add_annotation(self, law_id: str, content: str, 
                      article_num: str = '', tags: List[str] = None) -> int:
        """添加批注"""
        now = datetime.now().isoformat()
        sql = """
            INSERT INTO annotations (law_id, article_num, content, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(sql, (
            law_id, article_num, content, 
            json.dumps(tags or [], ensure_ascii=False),
            now, now
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_annotations(self, law_id: str, article_num: str = None) -> List[Annotation]:
        """获取批注"""
        if article_num is not None:
            sql = "SELECT * FROM annotations WHERE law_id = ? AND article_num = ? ORDER BY created_at DESC"
            self.cursor.execute(sql, (law_id, article_num))
        else:
            sql = "SELECT * FROM annotations WHERE law_id = ? ORDER BY created_at DESC"
            self.cursor.execute(sql, (law_id,))
        
        rows = self.cursor.fetchall()
        return [self._row_to_annotation(row) for row in rows]
    
    def update_annotation(self, anno_id: int, content: str, tags: List[str] = None):
        """更新批注"""
        now = datetime.now().isoformat()
        sql = """
            UPDATE annotations 
            SET content = ?, tags = ?, updated_at = ?
            WHERE id = ?
        """
        self.cursor.execute(sql, (
            content, 
            json.dumps(tags or [], ensure_ascii=False),
            now, anno_id
        ))
        self.conn.commit()
    
    def delete_annotation(self, anno_id: int):
        """删除批注"""
        self.cursor.execute("DELETE FROM annotations WHERE id = ?", (anno_id,))
        self.conn.commit()
    
    # ==================== 案件 CRUD ====================
    
    def add_case(self, title: str, case_type: str = 'actual',
                summary: str = '', facts: str = '', issues: str = '',
                ruling: str = '', notes: str = '',
                related_laws: List[Dict] = None,
                tags: List[str] = None,
                attachments: List[str] = None) -> int:
        """添加案件"""
        now = datetime.now().isoformat()
        sql = """
            INSERT INTO cases (title, case_type, summary, facts, issues, ruling, notes,
                              related_laws, tags, attachments, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(sql, (
            title, case_type, summary, facts, issues, ruling, notes,
            json.dumps(related_laws or [], ensure_ascii=False),
            json.dumps(tags or [], ensure_ascii=False),
            json.dumps(attachments or [], ensure_ascii=False),
            now, now
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_cases(self, case_type: str = None, tags: List[str] = None) -> List[Case]:
        """获取案件列表"""
        conditions = []
        params = []
        
        if case_type:
            conditions.append("case_type = ?")
            params.append(case_type)
        
        if tags:
            # 简单实现：使用 LIKE 匹配标签
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')
            if tag_conditions:
                conditions.append(f"({' OR '.join(tag_conditions)})")
        
        if conditions:
            sql = f"SELECT * FROM cases WHERE {' AND '.join(conditions)} ORDER BY updated_at DESC"
        else:
            sql = "SELECT * FROM cases ORDER BY updated_at DESC"
        
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [self._row_to_case(row) for row in rows]
    
    def get_case_by_id(self, case_id: int) -> Optional[Case]:
        """根据ID获取案件"""
        self.cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
        row = self.cursor.fetchone()
        return self._row_to_case(row) if row else None
    
    def update_case(self, case_id: int, **kwargs):
        """更新案件"""
        allowed_fields = ['title', 'case_type', 'summary', 'facts', 
                         'issues', 'ruling', 'notes', 'related_laws', 'tags', 'attachments']
        
        updates = []
        params = []
        
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = ?")
                value = kwargs[field]
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                params.append(value)
        
        if not updates:
            return
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(case_id)
        
        sql = f"UPDATE cases SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(sql, params)
        self.conn.commit()
    
    def delete_case(self, case_id: int):
        """删除案件"""
        self.cursor.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        self.conn.commit()
    
    # ==================== 笔记 CRUD ====================
    
    def add_note(self, title: str, content: str,
                related_law_id: str = '', related_article_num: str = '',
                tags: List[str] = None) -> int:
        """添加笔记"""
        now = datetime.now().isoformat()
        sql = """
            INSERT INTO user_notes (title, content, related_law_id, related_article_num, 
                                   tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(sql, (
            title, content, related_law_id, related_article_num,
            json.dumps(tags or [], ensure_ascii=False),
            now, now
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_notes(self, related_law_id: str = None) -> List[UserNote]:
        """获取笔记"""
        if related_law_id:
            sql = "SELECT * FROM user_notes WHERE related_law_id = ? ORDER BY updated_at DESC"
            self.cursor.execute(sql, (related_law_id,))
        else:
            sql = "SELECT * FROM user_notes ORDER BY updated_at DESC"
            self.cursor.execute(sql)
        
        rows = self.cursor.fetchall()
        return [self._row_to_note(row) for row in rows]
    
    def update_note(self, note_id: int, **kwargs):
        """更新笔记"""
        allowed_fields = ['title', 'content', 'related_law_id', 
                         'related_article_num', 'tags']
        
        updates = []
        params = []
        
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = ?")
                value = kwargs[field]
                if isinstance(value, list):
                    value = json.dumps(value, ensure_ascii=False)
                params.append(value)
        
        if not updates:
            return
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(note_id)
        
        sql = f"UPDATE user_notes SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(sql, params)
        self.conn.commit()
    
    def delete_note(self, note_id: int):
        """删除笔记"""
        self.cursor.execute("DELETE FROM user_notes WHERE id = ?", (note_id,))
        self.conn.commit()
    
    # ==================== 统计 ====================
    
    def get_stats(self) -> Dict[str, int]:
        """获取用户数据统计"""
        stats = {}
        
        self.cursor.execute("SELECT COUNT(*) FROM annotations")
        stats['annotations'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM cases")
        stats['cases'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM cases WHERE case_type = 'reference'")
        stats['reference_cases'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM cases WHERE case_type = 'actual'")
        stats['actual_cases'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM user_notes")
        stats['notes'] = self.cursor.fetchone()[0]
        
        return stats
    
    # ==================== 辅助方法 ====================
    
    def _row_to_annotation(self, row) -> Annotation:
        return Annotation(
            id=row['id'],
            law_id=row['law_id'],
            article_num=row['article_num'] or None,
            content=row['content'],
            tags=json.loads(row['tags'] or '[]'),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def _row_to_case(self, row) -> Case:
        return Case(
            id=row['id'],
            title=row['title'],
            case_type=row['case_type'],
            summary=row['summary'],
            facts=row['facts'],
            issues=row['issues'],
            ruling=row['ruling'],
            notes=row['notes'],
            related_laws=json.loads(row['related_laws'] or '[]'),
            tags=json.loads(row['tags'] or '[]'),
            attachments=json.loads(row['attachments'] or '[]'),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def _row_to_note(self, row) -> UserNote:
        return UserNote(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            related_law_id=row['related_law_id'] or None,
            related_article_num=row['related_article_num'] or None,
            tags=json.loads(row['tags'] or '[]'),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
