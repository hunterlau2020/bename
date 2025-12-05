#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试外格计算逻辑修复
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.calculator import Calculator

def test_waige_calculation():
    """测试外格计算逻辑"""
    print("=" * 70)
    print("外格计算逻辑测试")
    print("=" * 70)
    
    calculator = Calculator()
    
    # 测试用例
    test_cases = [
        {
            'name': '王五',
            'type': '单姓单名',
            'expected_rule': '固定为2（即1+1）',
            'description': '姓氏笔画:4, 名字笔画:4'
        },
        {
            'name': '张小明',
            'type': '单姓双名',
            'expected_rule': '名字最后一字笔画 + 1',
            'description': '姓氏笔画:11, 名字1笔画:3, 名字2笔画:8 → 外格=8+1=9'
        },
        {
            'name': '李建国',
            'type': '单姓双名',
            'expected_rule': '名字最后一字笔画 + 1',
            'description': '姓氏笔画:7, 名字1笔画:9, 名字2笔画:11 → 外格=11+1=12'
        },
        {
            'name': '欧阳飞',
            'type': '复姓单名',
            'expected_rule': '姓氏第一个字笔画 + 1',
            'description': '姓氏1笔画:15, 姓氏2笔画:12, 名字笔画:9 → 外格=15+1=16'
        },
        {
            'name': '司马相如',
            'type': '复姓双名',
            'expected_rule': '姓氏第一个字笔画 + 名字最后一个字笔画',
            'description': '姓氏1笔画:5, 姓氏2笔画:10, 名字1笔画:9, 名字2笔画:6 → 外格=5+6=11'
        }
    ]
    
    print("\n测试结果：\n")
    
    for i, case in enumerate(test_cases, 1):
        name = case['name']
        
        try:
            # 获取笔画数
            strokes = calculator._get_strokes(name)
            strokes_str = ', '.join([f"{c}:{s}" for c, s in zip(name, strokes)])
            
            # 计算五格
            result = calculator.calculate_wuge(name)
            waige = result['waige']['num']
            
            print(f"{i}. 【{case['type']}】 {name}")
            print(f"   笔画: {strokes_str}")
            print(f"   外格: {waige}")
            print(f"   规则: {case['expected_rule']}")
            print(f"   说明: {case['description']}")
            print()
            
        except Exception as e:
            print(f"{i}. 【{case['type']}】 {name}")
            print(f"   ✗ 错误: {e}")
            print()
    
    print("=" * 70)
    print("测试完成")
    print("=" * 70)
    print("\n外格计算规则：")
    print("  · 单姓单名：固定为 2（即 1+1）")
    print("  · 单姓双名：名字最后一字笔画 + 1")
    print("  · 复姓单名：姓氏第一个字笔画 + 1")
    print("  · 复姓双名：姓氏第一个字笔画 + 名字最后一个字笔画")

if __name__ == '__main__':
    test_waige_calculation()
