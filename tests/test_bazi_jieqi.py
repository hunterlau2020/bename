#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试八字节气计算
验证立春和节气对年柱、月柱的影响
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.calculator import Calculator

def test_bazi_jieqi():
    """测试八字节气计算"""
    print("=" * 60)
    print("八字节气计算测试")
    print("=" * 60)
    
    calculator = Calculator()
    
    # 测试数据：重点测试立春前后和节气交界处的日期
    test_cases = [
        {
            'name': '立春前（应该算上一年）',
            'birth_time': '2024-02-03 10:00',  # 立春前
            'expected_year': '癸卯',  # 2023年
            'description': '2024年2月3日（立春约2月4日）'
        },
        {
            'name': '立春后（应该算当年）',
            'birth_time': '2024-02-05 10:00',  # 立春后
            'expected_year': '甲辰',  # 2024年
            'description': '2024年2月5日（立春约2月4日）'
        },
        {
            'name': '刘德华',
            'birth_time': '1961-09-27 10:30',
            'expected_year': '辛丑',  # 1961年
            'expected_month': '丁酉',  # 八月（白露-寒露）
            'description': '1961年9月27日（白露后）'
        },
        {
            'name': '周杰伦',
            'birth_time': '1979-01-18 20:00',
            'expected_year': '戊午',  # 1978年（立春前）
            'expected_month': '乙丑',  # 十二月（小寒-立春）
            'description': '1979年1月18日（立春前）'
        },
        {
            'name': '李小龙',
            'birth_time': '1940-11-27 06:00',
            'expected_year': '庚辰',  # 1940年
            'expected_month': '丁亥',  # 十月（立冬-大雪）
            'description': '1940年11月27日（立冬后）'
        },
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"测试案例 {i}: {test_data['name']}")
        print(f"说明: {test_data['description']}")
        print(f"{'=' * 60}")
        
        try:
            from datetime import datetime
            birth_dt = datetime.strptime(test_data['birth_time'], '%Y-%m-%d %H:%M')
            
            # 计算八字
            bazi_result = calculator.calculate_bazi(birth_dt, 114.0, 22.0)
            
            print(f"\n出生时间(阳历): {test_data['birth_time']}")
            print(f"出生时间(农历): {bazi_result['lunar_date']}")
            print(f"八字: {bazi_result['bazi_str']}")
            
            # 提取年柱和月柱
            parts = bazi_result['bazi_str'].split()
            year_pillar = parts[0]
            month_pillar = parts[1]
            
            print(f"\n年柱: {year_pillar}", end='')
            if 'expected_year' in test_data:
                if year_pillar == test_data['expected_year']:
                    print(f" ✓ (预期: {test_data['expected_year']})")
                else:
                    print(f" ✗ (预期: {test_data['expected_year']}，实际: {year_pillar})")
            else:
                print()
            
            print(f"月柱: {month_pillar}", end='')
            if 'expected_month' in test_data:
                if month_pillar == test_data['expected_month']:
                    print(f" ✓ (预期: {test_data['expected_month']})")
                else:
                    print(f" ✗ (预期: {test_data['expected_month']}，实际: {month_pillar})")
            else:
                print()
            
            print(f"\n✓ 测试完成")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("测试完成")
    print(f"{'=' * 60}")
    
    print("\n说明：")
    print("1. 年柱以立春为界，立春前算上一年，立春后算当年")
    print("2. 月柱以节气为界，不是农历初一")
    print("3. 每个月的节气分界日期会有1-2天的浮动")

if __name__ == '__main__':
    test_bazi_jieqi()
