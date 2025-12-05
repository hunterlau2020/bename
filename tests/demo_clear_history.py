#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清空历史记录功能演示
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.calculator import Calculator
from modules.storage import Storage

def demo_clear_history():
    """演示清空历史记录功能"""
    print("=" * 70)
    print("清空历史记录功能演示")
    print("=" * 70)
    
    calculator = Calculator()
    storage = Storage()
    
    # 1. 创建一些测试数据
    print("\n步骤 1: 创建测试数据")
    print("-" * 70)
    
    test_data = [
        ('张', '三', '男', '1990-01-01 10:00', 116.4, 39.9),
        ('李', '四', '女', '1995-05-15 14:30', 121.5, 31.2),
        ('王', '五', '男', '2000-12-20 08:00', 113.3, 23.1),
    ]
    
    for surname, given_name, gender, birth_time, lon, lat in test_data:
        try:
            result = calculator.calculate_name(surname, given_name, gender, birth_time, lon, lat)
            storage.save_test_result(result)
            full_name = surname + given_name
            print(f"  ✓ 已保存: {full_name} (综合评分: {result['comprehensive_score']}分)")
        except Exception as e:
            full_name = surname + given_name
            print(f"  ✗ 保存失败: {full_name} - {e}")
    
    # 2. 查看当前记录数
    count = storage.get_records_count()
    print(f"\n步骤 2: 当前历史记录数")
    print("-" * 70)
    print(f"  共有 {count} 条历史记录")
    
    # 3. 查看历史记录列表
    print(f"\n步骤 3: 历史记录列表")
    print("-" * 70)
    history = storage.query_history(limit=10)
    for i, record in enumerate(history, 1):
        print(f"  {i}. {record['name']} ({record['gender']}) - "
              f"{record['birth_time']} - 评分: {record['score']}分")
    
    # 4. 演示清空功能
    print(f"\n步骤 4: 清空历史记录")
    print("-" * 70)
    print("\n【方法一：命令行方式】")
    print("  命令: python bazi.py --clear-history")
    print("  说明: 直接从命令行清空所有历史记录")
    
    print("\n【方法二：交互界面方式】")
    print("  步骤: python bazi.py")
    print("       在姓名输入提示下输入 'clear'")
    print("  说明: 在交互式界面中清空历史记录")
    
    print("\n【方法三：程序调用】")
    print("  代码: storage.clear_all_records()")
    print(f"  执行: ", end="")
    
    if storage.clear_all_records():
        print("✓ 清空成功")
        print(f"  当前记录数: {storage.get_records_count()}")
    else:
        print("✗ 清空失败")
    
    print("\n" + "=" * 70)
    print("演示完成")
    print("=" * 70)

if __name__ == '__main__':
    demo_clear_history()
