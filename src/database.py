import os
import sys
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Law:
    id: str
    title: str
    type: str
    type_code: str
    status: str
    status_code: str
    office: str
    publish: Optional[str]
    expiry: Optional[str]
    content: str
    url: str
    updated_at: str
    has_content: int
    source: str

@dataclass
class LawArticle:
    id: int
    law_id: str
    article_num: str
    article_text: str
    chapter: str
    sort_order: int
    verified: int

@dataclass
class Topic:
    id: int
    name: str
    description: str
    created_at: str

class Database:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # 检测是否是 PyInstaller 打包后的环境
            if getattr(sys, 'frozen', False):
                # PyInstaller 打包后的临时目录
                bundle_dir = sys._MEIPASS
                bundled_db = os.path.join(bundle_dir, 'laws_dev.db')
                if os.path.exists(bundled_db):
                    db_path = bundled_db
                else:
                    # 检查 EXE 所在目录
                    exe_dir = os.path.dirname(sys.executable)
                    exe_db = os.path.join(exe_dir, 'laws_dev.db')
                    if os.path.exists(exe_db):
                        db_path = exe_db
                    else:
                        db_path = bundled_db  # 使用默认路径
            else:
                # 开发环境：优先使用用户桌面上的数据库
                desktop_db = Path.home() / "Desktop" / "laws_dev.db"
                if desktop_db.exists():
                    db_path = str(desktop_db)
                else:
                    # 否则使用项目目录下的数据库
                    db_path = os.path.join(os.path.dirname(__file__), "..", "assets", "laws.db")

        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        return self

    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ==================== 法律查询方法 ====================

    def get_laws_by_type(self, type_code: Optional[str] = None) -> List[Law]:
        """按位阶获取法律列表"""
        if type_code:
            sql = """
                SELECT * FROM laws
                WHERE type_code = ?
                ORDER BY publish DESC, title
            """
            self.cursor.execute(sql, (type_code,))
        else:
            sql = "SELECT * FROM laws ORDER BY type_code, publish DESC, title"
            self.cursor.execute(sql)

        rows = self.cursor.fetchall()
        return [self._row_to_law(row) for row in rows]

    def get_law_by_id(self, law_id: str) -> Optional[Law]:
        """根据ID获取法律"""
        sql = "SELECT * FROM laws WHERE id = ?"
        self.cursor.execute(sql, (law_id,))
        row = self.cursor.fetchone()
        return self._row_to_law(row) if row else None

    def search_laws_by_title(self, keyword: str) -> List[Law]:
        """按标题搜索法律"""
        sql = """
            SELECT * FROM laws
            WHERE title LIKE ?
            ORDER BY type_code, publish DESC
        """
        self.cursor.execute(sql, (f"%{keyword}%",))
        rows = self.cursor.fetchall()
        return [self._row_to_law(row) for row in rows]

    def fulltext_search(self, keyword: str) -> List[Dict[str, Any]]:
        """全文搜索（使用FTS5或LIKE回退）"""
        results = []

        # 先尝试FTS5搜索
        try:
            sql = """
                SELECT laws.*, laws_fts.rank as score
                FROM laws_fts
                JOIN laws ON laws.id = laws_fts.rowid
                WHERE laws_fts MATCH ?
                ORDER BY score DESC
                LIMIT 100
            """
            self.cursor.execute(sql, (keyword,))
            rows = self.cursor.fetchall()
            if rows:
                return [dict(row) for row in rows]
        except:
            pass

        # FTS失败或无果，使用LIKE搜索content字段
        try:
            sql = """
                SELECT * FROM laws
                WHERE content LIKE ? OR title LIKE ?
                ORDER BY publish DESC
                LIMIT 100
            """
            pattern = f"%{keyword}%"
            self.cursor.execute(sql, (pattern, pattern))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"搜索错误: {e}")
            return []

    def search_cases(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索案例（标题、摘要、事实、争议焦点、裁判结果）"""
        try:
            sql = """
                SELECT id, title, case_type, summary, facts, issues, ruling, tags, created_at
                FROM cases
                WHERE title LIKE ?
                   OR summary LIKE ?
                   OR facts LIKE ?
                   OR issues LIKE ?
                   OR ruling LIKE ?
                   OR tags LIKE ?
                ORDER BY updated_at DESC
                LIMIT 50
            """
            pattern = f"%{keyword}%"
            self.cursor.execute(sql, (pattern, pattern, pattern, pattern, pattern, pattern))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"案例搜索错误: {e}")
            return []

    def get_law_articles(self, law_id: str) -> List[LawArticle]:
        """获取法律的所有条文"""
        sql = """
            SELECT * FROM law_articles
            WHERE law_id = ?
            ORDER BY sort_order, id
        """
        self.cursor.execute(sql, (law_id,))
        rows = self.cursor.fetchall()
        return [self._row_to_article(row) for row in rows]

    def get_article_by_number(self, law_id: str, article_num: str) -> Optional[LawArticle]:
        """根据条文编号获取条文"""
        sql = """
            SELECT * FROM law_articles
            WHERE law_id = ? AND article_num = ?
        """
        self.cursor.execute(sql, (law_id, article_num))
        row = self.cursor.fetchone()
        return self._row_to_article(row) if row else None

    # ==================== 分类/主题查询 ====================

    def get_type_hierarchy(self) -> Dict[str, List[Law]]:
        """获取按位阶分层的法律"""
        type_order = ['flfg', 'xzfg', 'bmgz', 'dfxfg', 'dfzfg', 'sfjs', 'qt']
        type_names = {
            'flfg': '法律',
            'xzfg': '行政法规',
            'bmgz': '部门规章',
            'dfxfg': '地方性法规',
            'dfzfg': '地方政府规章',
            'sfjs': '司法解释',
            'qt': '其他'
        }

        result = {}
        for type_code in type_order:
            laws = self.get_laws_by_type(type_code)
            if laws:
                result[type_names.get(type_code, type_code)] = laws
        return result

    def get_all_topics(self) -> List[Topic]:
        """获取所有主题分类"""
        sql = "SELECT * FROM topics ORDER BY name"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return [self._row_to_topic(row) for row in rows]

    def get_laws_by_topic(self, topic_id: int) -> List[Law]:
        """获取主题下的法律"""
        sql = """
            SELECT laws.* FROM laws
            JOIN topic_laws ON laws.id = topic_laws.law_id
            WHERE topic_laws.topic_id = ?
            ORDER BY topic_laws.sort_order
        """
        self.cursor.execute(sql, (topic_id,))
        rows = self.cursor.fetchall()
        return [self._row_to_law(row) for row in rows]

    # ==================== 辅助方法 ====================

    def _row_to_law(self, row) -> Law:
        return Law(
            id=row['id'],
            title=row['title'],
            type=row['type'],
            type_code=row['type_code'],
            status=row['status'],
            status_code=row['status_code'],
            office=row['office'],
            publish=row['publish'],
            expiry=row['expiry'],
            content=row['content'] or '',
            url=row['url'] or '',
            updated_at=row['updated_at'],
            has_content=row['has_content'],
            source=row['source']
        )

    def _row_to_article(self, row) -> LawArticle:
        return LawArticle(
            id=row['id'],
            law_id=row['law_id'],
            article_num=row['article_num'],
            article_text=row['article_text'],
            chapter=row['chapter'] or '',
            sort_order=row['sort_order'],
            verified=row['verified']
        )

    def _row_to_topic(self, row) -> Topic:
        return Topic(
            id=row['id'],
            name=row['name'],
            description=row['description'] or '',
            created_at=row['created_at']
        )
