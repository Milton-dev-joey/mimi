#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强搜索功能 - 搜索历史和高亮
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class SearchHistory:
    id: int
    query: str
    mode: str
    result_count: int
    created_at: str


class SearchManager:
    """搜索管理器"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def add_history(self, query: str, mode: str, result_count: int = 0):
        """添加搜索历史"""
        sql = """
            INSERT INTO search_history (query, mode, result_count, created_at)
            VALUES (?, ?, ?, ?)
        """
        self.cursor.execute(sql, (query, mode, result_count, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_history(self, limit: int = 20) -> List[SearchHistory]:
        """获取搜索历史"""
        sql = """
            SELECT * FROM search_history
            ORDER BY created_at DESC
            LIMIT ?
        """
        self.cursor.execute(sql, (limit,))
        rows = self.cursor.fetchall()
        return [SearchHistory(
            id=row['id'],
            query=row['query'],
            mode=row['mode'],
            result_count=row['result_count'],
            created_at=row['created_at']
        ) for row in rows]
    
    def clear_history(self):
        """清空搜索历史"""
        self.cursor.execute("DELETE FROM search_history")
        self.conn.commit()
    
    def get_hot_keywords(self, limit: int = 10) -> List[str]:
        """获取热门搜索词"""
        sql = """
            SELECT query, COUNT(*) as count
            FROM search_history
            GROUP BY query
            ORDER BY count DESC
            LIMIT ?
        """
        self.cursor.execute(sql, (limit,))
        return [row['query'] for row in self.cursor.fetchall()]


class TextHighlighter:
    """文本高亮工具"""
    
    @staticmethod
    def highlight_text(text: str, keywords: List[str], 
                      case_sensitive: bool = False) -> str:
        """
        高亮文本中的关键词
        
        Args:
            text: 原始文本
            keywords: 要高亮的关键词列表
            case_sensitive: 是否区分大小写
        
        Returns:
            带高亮标记的 HTML 文本
        """
        if not keywords:
            return text
        
        # 转义 HTML
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # 替换换行
        text = text.replace('\n', '<br>')
        
        # 高亮关键词
        for keyword in keywords:
            if not keyword:
                continue
            
            if case_sensitive:
                text = text.replace(
                    keyword,
                    f'<span style="background-color: #dcdcaa; color: #1e1e1e; padding: 2px 4px; border-radius: 2px;">{keyword}</span>'
                )
            else:
                # 不区分大小写的高亮
                import re
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                text = pattern.sub(
                    lambda m: f'<span style="background-color: #dcdcaa; color: #1e1e1e; padding: 2px 4px; border-radius: 2px;">{m.group()}</span>',
                    text
                )
        
        return text
    
    @staticmethod
    def extract_context(text: str, keyword: str, 
                       context_chars: int = 50) -> str:
        """
        提取关键词周围的上下文
        
        Args:
            text: 原始文本
            keyword: 关键词
            context_chars: 上下文字符数
        
        Returns:
            带省略号的上下文文本
        """
        if not keyword or not text:
            return text[:100] + "..."
        
        idx = text.lower().find(keyword.lower())
        if idx == -1:
            return text[:100] + "..."
        
        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(keyword) + context_chars)
        
        result = text[start:end]
        
        if start > 0:
            result = "..." + result
        if end < len(text):
            result = result + "..."
        
        return result


class AdvancedSearch:
    """高级搜索"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.cursor = db_connection.cursor()
    
    def search_with_filters(self, keyword: str, 
                           type_code: str = None,
                           status: str = None,
                           date_from: str = None,
                           date_to: str = None) -> List[Dict]:
        """
        带筛选条件的高级搜索
        """
        conditions = ["(title LIKE ? OR content LIKE ?)"]
        params = [f"%{keyword}%", f"%{keyword}%"]
        
        if type_code:
            conditions.append("type_code = ?")
            params.append(type_code)
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if date_from:
            conditions.append("publish >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("publish <= ?")
            params.append(date_to)
        
        sql = f"""
            SELECT * FROM laws
            WHERE {' AND '.join(conditions)}
            ORDER BY publish DESC
            LIMIT 100
        """
        
        self.cursor.execute(sql, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def fuzzy_search(self, keyword: str) -> List[Dict]:
        """
        模糊搜索（支持同义词扩展）
        """
        # 获取同义词
        synonyms = self._get_synonyms(keyword)
        all_terms = [keyword] + synonyms
        
        # 构建 OR 条件
        conditions = []
        params = []
        
        for term in all_terms:
            conditions.append("title LIKE ?")
            params.append(f"%{term}%")
        
        sql = f"""
            SELECT DISTINCT * FROM laws
            WHERE {' OR '.join(conditions)}
            ORDER BY publish DESC
            LIMIT 100
        """
        
        self.cursor.execute(sql, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def _get_synonyms(self, term: str) -> List[str]:
        """获取同义词"""
        sql = "SELECT expand FROM synonyms WHERE term = ?"
        self.cursor.execute(sql, (term,))
        return [row['expand'] for row in self.cursor.fetchall()]
