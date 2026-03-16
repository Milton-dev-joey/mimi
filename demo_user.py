#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据功能测试
"""
import sys
sys.path.insert(0, 'src')

from database import Database
from user_data import UserDataManager


def demo_user_data():
    """演示用户数据功能"""
    print("=" * 60)
    print("劳动法数据库 - 用户功能演示")
    print("=" * 60)
    
    db = Database()
    db.connect()
    
    # 初始化用户数据管理器
    udm = UserDataManager(db.conn)
    
    # 1. 添加批注
    print("\n【1. 添加批注】")
    
    # 获取一个法律ID作为示例
    cursor = db.cursor
    cursor.execute("SELECT id FROM laws WHERE title LIKE '%劳动合同法%' LIMIT 1")
    row = cursor.fetchone()
    if row:
        law_id = row['id']
        
        anno_id = udm.add_annotation(
            law_id=law_id,
            article_num="第四十七条",
            content="经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。",
            tags=["经济补偿", "重要条文"]
        )
        print(f"  添加批注成功，ID: {anno_id}")
        
        # 查询批注
        annotations = udm.get_annotations(law_id)
        print(f"  该法律共有 {len(annotations)} 条批注")
        for anno in annotations:
            print(f"    • 第{anno.article_num}条: {anno.content[:30]}...")
    
    # 2. 添加案件
    print("\n【2. 添加案件】")
    
    case_id = udm.add_case(
        title="张某诉某公司违法解除劳动合同案",
        case_type="actual",
        summary="公司以员工严重违纪为由解除合同，但规章制度未公示。",
        facts="员工张某在公司工作3年，因一次迟到被公司认定为严重违纪并解除劳动合同。",
        issues="1. 公司规章制度是否有效？2. 解除劳动合同是否合法？",
        ruling="法院认定公司规章制度未经民主程序制定并公示，不能作为解除依据，判决公司支付赔偿金。",
        notes="参考：劳动合同法第四条、第三十九条、第四十三条",
        related_laws=[
            {"law_id": "hf_000373", "article_num": "第四条"},
            {"law_id": "hf_000373", "article_num": "第三十九条"},
            {"law_id": "hf_000373", "article_num": "第四十三条"}
        ],
        tags=["违法解除", "规章制度", "赔偿金"]
    )
    print(f"  添加案件成功，ID: {case_id}")
    
    # 添加参考案件
    ref_case_id = udm.add_case(
        title="最高法指导案例 - 竞业限制纠纷",
        case_type="reference",
        summary="关于竞业限制补偿金支付标准的参考案例。",
        notes="适用于竞业限制相关案件办理",
        tags=["竞业限制", "参考案例"]
    )
    print(f"  添加参考案件成功，ID: {ref_case_id}")
    
    # 查询案件
    cases = udm.get_cases()
    print(f"  共有 {len(cases)} 个案件")
    for case in cases:
        type_label = "【现实】" if case.case_type == "actual" else "【参考】"
        print(f"    • {type_label} {case.title}")
    
    # 3. 添加笔记
    print("\n【3. 添加笔记】")
    
    note_id = udm.add_note(
        title="经济补偿金计算要点",
        content="""
        1. N的计算：按工作年限，每满一年支付一个月工资
        2. 月工资标准：解除前12个月平均工资
        3. 三倍封顶：月工资超过社平三倍的，按三倍计算，年限最多12年
        4. 上海2024年标准：社平工资12,307元/月，三倍36,921元/月
        """,
        related_law_id="hf_000373",
        related_article_num="第四十七条",
        tags=["经济补偿", "计算标准", "上海"]
    )
    print(f"  添加笔记成功，ID: {note_id}")
    
    # 查询笔记
    notes = udm.get_notes()
    print(f"  共有 {len(notes)} 条笔记")
    for note in notes:
        print(f"    • {note.title}")
        if note.related_law_id:
            print(f"      关联法律: {note.related_law_id} 第{note.related_article_num}条")
    
    # 4. 统计数据
    print("\n【4. 用户数据统计】")
    stats = udm.get_stats()
    for key, value in stats.items():
        print(f"  • {key}: {value}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("用户功能演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    demo_user_data()
