#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能演示和测试脚本
"""
import sys
sys.path.insert(0, 'src')

from database import Database
from search_utils import SearchManager, TextHighlighter, AdvancedSearch


def demo_search():
    """演示搜索功能"""
    print("=" * 60)
    print("劳动法数据库 - 搜索功能演示")
    print("=" * 60)
    
    db = Database()
    db.connect()
    
    # 1. 基础搜索
    print("\n【1. 标题搜索 - '劳动合同'】")
    results = db.search_laws_by_title("劳动合同")
    print(f"找到 {len(results)} 条结果：")
    for law in results[:5]:
        print(f"  • {law.title}")
    
    # 2. 全文搜索
    print("\n【2. 全文搜索 - '经济补偿'】")
    results = db.fulltext_search("经济补偿")
    print(f"找到 {len(results)} 条结果")
    if results:
        print(f"  第一结果：{results[0].get('title', 'N/A')}")
    
    # 3. 高级搜索（带筛选）
    print("\n【3. 高级搜索 - '工资' + 法律位阶】")
    adv = AdvancedSearch(db.conn)
    results = adv.search_with_filters("工资", type_code="flfg")
    print(f"找到 {len(results)} 条结果")
    for row in results[:5]:
        print(f"  • {row.get('title')}")
    
    # 4. 搜索历史
    print("\n【4. 搜索历史记录】")
    sm = SearchManager(db.conn)
    sm.add_history("劳动合同", "title", len(results))
    sm.add_history("经济补偿", "fulltext", 10)
    history = sm.get_history(limit=10)
    print(f"最近 {len(history)} 条搜索记录：")
    for h in history:
        print(f"  • [{h.mode}] {h.query} ({h.result_count}条结果)")
    
    # 5. 文本高亮
    print("\n【5. 文本高亮示例】")
    text = "用人单位应当按照劳动合同约定支付劳动者工资。"
    highlighted = TextHighlighter.highlight_text(text, ["劳动", "工资"])
    print(f"原文：{text}")
    print(f"高亮：{highlighted[:200]}...")
    
    # 6. 上下文提取
    print("\n【6. 上下文提取】")
    long_text = "这是前面的一些文字。用人单位应当按照劳动合同约定支付劳动者工资。这是后面的一些文字。"
    context = TextHighlighter.extract_context(long_text, "工资", 20)
    print(f"上下文：...{context}...")
    
    # 7. 按位阶浏览
    print("\n【7. 法律位阶分布】")
    hierarchy = db.get_type_hierarchy()
    for type_name, laws in hierarchy.items():
        print(f"  • {type_name}: {len(laws)} 部")
    
    # 8. 获取法律详情
    print("\n【8. 法律详情示例 - 劳动合同法】")
    cursor = db.cursor
    cursor.execute("SELECT id FROM laws WHERE title LIKE '%劳动合同法%' LIMIT 1")
    row = cursor.fetchone()
    if row:
        law_id = row['id']
        law = db.get_law_by_id(law_id)
        articles = db.get_law_articles(law_id)
        print(f"  标题：{law.title}")
        print(f"  位阶：{law.type}")
        print(f"  发布日期：{law.publish}")
        print(f"  状态：{law.status}")
        print(f"  条文数量：{len(articles)} 条")
        if articles:
            print(f"  示例条文：第{articles[0].article_num}条 {articles[0].article_text[:50]}...")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    demo_search()
