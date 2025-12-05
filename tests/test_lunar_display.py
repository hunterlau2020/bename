#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试农历显示功能
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.calculator import Calculator
from modules.storage import Storage

def test_lunar_display():
    """测试农历显示功能"""
    print("=" * 60)
    print("农历显示功能测试")
    print("=" * 60)
    
    calculator = Calculator()
    storage = Storage()
    
    # 测试数据
    test_cases = [
        {
            'surname': '刘',
            'given_name': '德华',
            'gender': '男',
            'birth_time': '1961-09-27 10:30',
            'longitude': 114.17,
            'latitude': 22.32,
            'description': '刘德华'
        },
        {
            'surname': '周',
            'given_name': '杰伦',
            'gender': '男',
            'birth_time': '1979-01-18 20:00',
            'longitude': 121.47,
            'latitude': 25.04,
            'description': '周杰伦'
        }
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        full_name = test_data['surname'] + test_data['given_name']
        print(f"\n{'=' * 60}")
        print(f"测试案例 {i}: {test_data['description']}")
        print(f"{'=' * 60}")
        
        try:
            # 执行计算
            result = calculator.calculate_name(
                test_data['surname'],
                test_data['given_name'],
                test_data['gender'],
                test_data['birth_time'],
                test_data['longitude'],
                test_data['latitude']
            )
            
            # 显示结果
            print(f"\n【基本信息】")
            print(f"姓名: {result['name']}")
            print(f"性别: {result['gender']}")
            print(f"出生时间(阳历): {result['birth_time']}")
            
            # 显示农历
            if 'bazi' in result and 'lunar_date' in result['bazi']:
                lunar_date = result['bazi']['lunar_date']
                print(f"出生时间(农历): {lunar_date}")
            else:
                print(f"出生时间(农历): 未能获取")
            
            print(f"\n【八字信息】")
            print(f"八字: {result['bazi']['bazi_str']}")
            print(f"综合评分: {result['comprehensive_score']}分")
            
            print(f"\n✓ 测试成功")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("测试完成")
    print(f"{'=' * 60}")

if __name__ == '__main__':
    test_lunar_display()
