# -*- coding: utf-8 -*-
"""
测试万年历数据在八字计算中的应用
"""

import sqlite3
from datetime import datetime
from modules.calculator import Calculator

def test_wannianli_query():
    """测试万年历数据查询"""
    print("=" * 60)
    print("测试 1: 万年历数据查询")
    print("=" * 60)
    
    db_path = 'local.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 测试几个特殊日期
    test_dates = [
        '1970-01-01',  # 元旦
        '2000-02-04',  # 立春附近
        '2024-02-10',  # 春节
        '2024-12-05',  # 今天
    ]
    
    for date_str in test_dates:
        cursor.execute('''
        SELECT gregorian_date, year_ganzhi, month_ganzhi, day_ganzhi, 
               lunar_show, solar_term, zodiac
        FROM wannianli
        WHERE gregorian_date = ?
        ''', (date_str,))
        
        row = cursor.fetchone()
        if row:
            print(f"\n日期: {row[0]}")
            print(f"  年柱: {row[1]}")
            print(f"  月柱: {row[2]}")
            print(f"  日柱: {row[3]}")
            print(f"  农历: {row[4]}")
            print(f"  节气: {row[5] or '无'}")
            print(f"  生肖: {row[6]}")
        else:
            print(f"\n日期: {date_str} - 未找到数据")
    
    conn.close()


def test_bazi_calculation():
    """测试八字计算是否使用万年历"""
    print("\n" + "=" * 60)
    print("测试 2: 八字计算（使用万年历）")
    print("=" * 60)
    
    calc = Calculator()
    
    # 测试案例
    test_cases = [
        {
            'name': '测试1（立春）',
            'birth_dt': datetime(2000, 2, 4, 12, 0, 0),
            'longitude': 120.0,
            'latitude': 30.0
        },
        {
            'name': '测试2（立春前）',
            'birth_dt': datetime(2000, 2, 3, 12, 0, 0),
            'longitude': 120.0,
            'latitude': 30.0
        },
        {
            'name': '测试3（春节）',
            'birth_dt': datetime(2024, 2, 10, 8, 0, 0),
            'longitude': 120.0,
            'latitude': 30.0
        },
    ]
    
    for case in test_cases:
        print(f"\n【{case['name']}】")
        print(f"出生时间: {case['birth_dt']}")
        
        try:
            result = calc.calculate_bazi(
                case['birth_dt'],
                case['longitude'],
                case['latitude']
            )
            
            print(f"八字: {result['bazi_str']}")
            print(f"农历: {result.get('lunar_date', '无')}")
            print(f"五行: {result.get('wuxing', '无')}")
            print(f"评分: {result.get('score', 0)}")
            
            # 分析干支来源
            bazi_parts = result['bazi_str'].split()
            if len(bazi_parts) == 4:
                print(f"  年柱: {bazi_parts[0]}")
                print(f"  月柱: {bazi_parts[1]}")
                print(f"  日柱: {bazi_parts[2]}")
                print(f"  时柱: {bazi_parts[3]}")
        except Exception as e:
            print(f"计算失败: {e}")


def test_lunar_conversion():
    """测试农历转换"""
    print("\n" + "=" * 60)
    print("测试 3: 农历转换（使用万年历）")
    print("=" * 60)
    
    calc = Calculator()
    
    test_dates = [
        datetime(1970, 1, 1, 12, 0, 0),
        datetime(2000, 2, 4, 12, 0, 0),
        datetime(2024, 2, 10, 8, 0, 0),
        datetime(2024, 12, 5, 15, 0, 0),
    ]
    
    for dt in test_dates:
        lunar_str = calc._solar_to_lunar(dt)
        print(f"{dt.strftime('%Y-%m-%d %H:%M')} => {lunar_str}")


if __name__ == '__main__':
    test_wannianli_query()
    test_bazi_calculation()
    test_lunar_conversion()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
