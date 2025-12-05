#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动化测试脚本 - 测试姓名分析功能
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.calculator import Calculator
from modules.storage import Storage

def test_name_analysis():
    """测试姓名分析功能"""
    print("=" * 60)
    print("姓名测试功能自动化测试")
    print("=" * 60)
    
    # 初始化
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
            'latitude': 22.32
        },
        {
            'surname': '李',
            'given_name': '小龙',
            'gender': '男',
            'birth_time': '1940-11-27 06:00',
            'longitude': 122.27,
            'latitude': 37.48
        }
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        full_name = test_data['surname'] + test_data['given_name']
        print(f"\n{'=' * 60}")
        print(f"测试案例 {i}: {full_name}")
        print(f"{'=' * 60}")
        
        try:
            # 执行计算
            print("\n正在计算...")
            result = calculator.calculate_name(
                test_data['surname'],
                test_data['given_name'],
                test_data['gender'],
                test_data['birth_time'],
                test_data['longitude'],
                test_data['latitude']
            )
            
            # 显示结果摘要
            print(f"\n✓ 计算成功")
            print(f"  姓名: {result['name']}")
            print(f"  综合评分: {result['comprehensive_score']}分")
            
            if 'wuge' in result:
                print(f"  五格得分: {result['wuge']['score']}分")
            else:
                print(f"  ✗ 缺少五格数据")
            
            if 'bazi' in result:
                print(f"  八字得分: {result['bazi']['score']}分")
                print(f"  八字: {result['bazi']['bazi_str']}")
            else:
                print(f"  ✗ 缺少八字数据")
            
            if 'ziyi' in result:
                print(f"  字义得分: {result['ziyi']['score']}分")
            else:
                print(f"  ✗ 缺少字义数据")
            
            if 'shengxiao' in result:
                print(f"  生肖得分: {result['shengxiao']['score']}分")
                print(f"  生肖: {result['shengxiao']['shengxiao']}")
            else:
                print(f"  ✗ 缺少生肖数据")
            
            # 保存结果
            print("\n正在保存结果...")
            record_id = storage.save_test_result(result)
            if record_id:
                print(f"✓ 保存成功，记录ID: {record_id}")
                
                # 测试查询
                print("\n正在从数据库读取...")
                cached_result = storage.query_test_result(
                    full_name,
                    test_data['gender'],
                    test_data['birth_time'],
                    test_data['longitude'],
                    test_data['latitude']
                )
                
                if cached_result:
                    print(f"✓ 读取成功")
                    # 验证数据完整性
                    required_keys = ['wuge', 'bazi', 'ziyi', 'shengxiao']
                    missing_keys = [key for key in required_keys if key not in cached_result]
                    
                    if missing_keys:
                        print(f"✗ 缺少数据: {', '.join(missing_keys)}")
                    else:
                        print(f"✓ 数据完整")
                else:
                    print(f"✗ 读取失败")
            else:
                print(f"✗ 保存失败")
            
        except Exception as e:
            print(f"\n✗ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("测试完成")
    print(f"{'=' * 60}")

if __name__ == '__main__':
    test_name_analysis()
