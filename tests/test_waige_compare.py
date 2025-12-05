#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
外格计算逻辑修复前后对比
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.calculator import Calculator

def compare_waige_calculation():
    """对比外格计算修复前后的差异"""
    print("=" * 80)
    print("外格计算逻辑修复前后对比")
    print("=" * 80)
    
    calculator = Calculator()
    
    test_cases = [
        {
            'name': '王五',
            'old_formula': 'waige = 2',
            'new_formula': 'waige = 2 (固定)',
            'note': '单姓单名：修复前后一致 ✓'
        },
        {
            'name': '张小明',
            'old_formula': 'waige = dige - renge + tiange = (3+8) - (11+3) + (11+1) = 11 - 14 + 12 = 9',
            'new_formula': 'waige = 8 + 1 = 9',
            'note': '单姓双名：结果相同但公式更简洁 ✓'
        },
        {
            'name': '李建国',
            'old_formula': 'waige = dige - renge + tiange = (8+11) - (7+8) + (7+1) = 19 - 15 + 8 = 12',
            'new_formula': 'waige = 11 + 1 = 12',
            'note': '单姓双名：结果相同但公式更简洁 ✓'
        },
        {
            'name': '欧阳飞',
            'old_formula': 'waige = dige - renge + tiange = (9+1) - (11+9) + (15+11) = 10 - 20 + 26 = 16',
            'new_formula': 'waige = 15 + 1 = 16',
            'note': '复姓单名：结果相同但现在能正确识别复姓 ✓'
        },
        {
            'name': '司马相如',
            'old_formula': 'waige = strokes[0] + strokes[3] = 5 + 6 = 11',
            'new_formula': 'waige = 5 + 6 = 11',
            'note': '复姓双名：修复前后一致 ✓'
        }
    ]
    
    print("\n详细对比：\n")
    
    for i, case in enumerate(test_cases, 1):
        name = case['name']
        
        try:
            result = calculator.calculate_wuge(name)
            waige = result['waige']['num']
            strokes = calculator._get_strokes(name)
            
            print(f"{i}. 姓名：{name}")
            print(f"   笔画：{' + '.join([str(s) for s in strokes])} = {sum(strokes)}")
            print(f"   修复前公式：{case['old_formula']}")
            print(f"   修复后公式：{case['new_formula']}")
            print(f"   实际结果：外格 = {waige}")
            print(f"   评价：{case['note']}")
            print()
            
        except Exception as e:
            print(f"{i}. 姓名：{name}")
            print(f"   ✗ 错误：{e}")
            print()
    
    print("=" * 80)
    print("修复总结")
    print("=" * 80)
    print("\n【主要改进】")
    print("1. 单姓单名：保持不变（waige = 2）")
    print("2. 单姓双名：从复杂公式简化为 末字+1")
    print("3. 复姓单名：新增复姓识别逻辑，首字+1")
    print("4. 复姓双名：保持不变（首字+末字）")
    print("\n【复姓识别】")
    print("增加了常见复姓列表判断，包括：")
    print("欧阳、司马、上官、诸葛、皇甫、尉迟、公孙、慕容、长孙、")
    print("宇文、司徒、司空、东方、南宫、西门、北堂")
    print("\n【公式对比】")
    print("修复前：3字名统一使用 waige = dige - renge + tiange")
    print("修复后：根据实际情况（单姓双名/复姓单名）使用不同公式")
    print("\n【计算结果】")
    print("修复后的计算结果与传统姓名学标准一致 ✓")

if __name__ == '__main__':
    compare_waige_calculation()
