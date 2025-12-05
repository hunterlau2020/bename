#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试 - 验证query_test_result修复
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.storage import Storage

def test_query():
    """测试查询已保存的结果"""
    storage = Storage()
    
    # 查询之前保存的"刘德华"
    print("查询已保存的测试结果...")
    result = storage.query_test_result(
        '刘德华',
        '男',
        '1961-09-27 10:30',
        114.17,
        22.32
    )
    
    if result:
        print("\n✓ 查询成功")
        print(f"姓名: {result['name']}")
        print(f"综合评分: {result['comprehensive_score']}")
        
        # 检查关键字段
        required_keys = ['wuge', 'bazi', 'ziyi', 'shengxiao', 'chenggu']
        print("\n数据完整性检查:")
        for key in required_keys:
            if key in result:
                print(f"  ✓ {key}: 存在")
                if key == 'wuge' and 'score' in result[key]:
                    print(f"      得分: {result[key]['score']}分")
                elif key == 'bazi' and 'score' in result[key]:
                    print(f"      得分: {result[key]['score']}分")
            else:
                print(f"  ✗ {key}: 缺失")
    else:
        print("✗ 查询失败或无数据")

if __name__ == '__main__':
    test_query()
