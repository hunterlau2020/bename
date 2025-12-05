#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试分离姓氏和名字后的五格计算
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.calculator import Calculator

def test_separated_name_calculation():
    """测试分离姓名后的五格计算"""
    print("=" * 80)
    print("测试分离姓氏和名字后的五格计算")
    print("=" * 80)
    
    calculator = Calculator()
    
    test_cases = [
        {
            'surname': '王',
            'given_name': '五',
            'type': '单姓单名',
            'description': '最简单的2字名'
        },
        {
            'surname': '张',
            'given_name': '小明',
            'type': '单姓双名',
            'description': '常见的3字名'
        },
        {
            'surname': '李',
            'given_name': '建国',
            'type': '单姓双名',
            'description': '另一个3字名'
        },
        {
            'surname': '欧阳',
            'given_name': '飞',
            'type': '复姓单名',
            'description': '复姓+单名'
        },
        {
            'surname': '司马',
            'given_name': '相如',
            'type': '复姓双名',
            'description': '复姓+双名'
        },
        {
            'surname': '诸葛',
            'given_name': '亮',
            'type': '复姓单名',
            'description': '著名历史人物'
        }
    ]
    
    print("\n测试结果：\n")
    
    for i, case in enumerate(test_cases, 1):
        surname = case['surname']
        given_name = case['given_name']
        full_name = surname + given_name
        
        try:
            # 获取笔画数
            surname_strokes = calculator._get_strokes(surname)
            given_strokes = calculator._get_strokes(given_name)
            
            # 计算五格
            result = calculator.calculate_wuge(surname, given_name)
            
            print(f"{i}. 【{case['type']}】 {surname} + {given_name} = {full_name}")
            print(f"   说明: {case['description']}")
            print(f"   姓氏笔画: {' + '.join([str(s) for s in surname_strokes])} = {sum(surname_strokes)}")
            print(f"   名字笔画: {' + '.join([str(s) for s in given_strokes])} = {sum(given_strokes)}")
            print(f"   天格: {result['tiange']['num']} ({result['tiange']['element']}) {result['tiange']['fortune']}")
            print(f"   人格: {result['renge']['num']} ({result['renge']['element']}) {result['renge']['fortune']}")
            print(f"   地格: {result['dige']['num']} ({result['dige']['element']}) {result['dige']['fortune']}")
            print(f"   外格: {result['waige']['num']} ({result['waige']['element']}) {result['waige']['fortune']}")
            print(f"   总格: {result['zongge']['num']} ({result['zongge']['element']}) {result['zongge']['fortune']}")
            print(f"   三才: {result['sancai']}")
            print(f"   得分: {result['score']}分")
            print()
            
        except Exception as e:
            print(f"{i}. 【{case['type']}】 {surname} + {given_name}")
            print(f"   ✗ 错误: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 80)
    print("测试完成")
    print("=" * 80)
    print("\n【优势】")
    print("1. 明确区分单姓/复姓，计算更准确")
    print("2. 用户输入更直观，避免歧义")
    print("3. 不再需要复姓列表判断，直接根据输入确定")
    print("4. 支持所有复姓，不仅限于常见复姓")

if __name__ == '__main__':
    test_separated_name_calculation()
