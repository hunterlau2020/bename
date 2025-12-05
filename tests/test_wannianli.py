#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试万年历数据
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_wannianli_data():
    """测试万年历数据"""
    print("=" * 60)
    print("万年历数据测试")
    print("=" * 60)
    
    data_file = Path(__file__).parent.parent / "data" / "wannianli.json"
    
    if not data_file.exists():
        print(f"\n✗ 文件不存在: {data_file}")
        return
    
    print(f"\n加载数据文件: {data_file}")
    print(f"文件大小: {data_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n✓ 加载成功")
        print(f"  版本: {data['version']}")
        print(f"  描述: {data['description']}")
        print(f"  日期范围: {data['date_range']['start']} 至 {data['date_range']['end']}")
        print(f"  总记录数: {data['total_records']}")
        
        records = data['data']
        
        # 测试查询几个特殊日期
        test_dates = [
            '1970-01-01 00:00:00',  # 第一条记录
            '2000-01-01 00:00:00',  # 千禧年
            '2024-02-04 00:00:00',  # 立春
            '2099-12-31 00:00:00',  # 最后一天
        ]
        
        print(f"\n测试查询:")
        for test_date in test_dates:
            # 查找记录
            record = next((r for r in records if r['gregorian_date'] == test_date), None)
            
            if record:
                print(f"\n  日期: {test_date}")
                print(f"  ✓ 找到记录")
                print(f"    农历: {record['lunar_date']} ({record['lunar_month']}{record['lunar_day']})")
                print(f"    干支: {record['year_ganzhi']}年 {record['month_ganzhi']}月 {record['day_ganzhi']}日")
                print(f"    生肖: {record['zodiac']}")
                if record['solar_term']:
                    print(f"    节气: {record['solar_term']}")
                if record['gregorian_festival']:
                    print(f"    节日: {record['gregorian_festival']}")
                if record['lunar_festival']:
                    print(f"    农历节日: {record['lunar_festival']}")
            else:
                print(f"\n  日期: {test_date}")
                print(f"  ✗ 未找到记录")
        
        # 统计节气
        print(f"\n统计节气:")
        solar_terms = {}
        for record in records:
            if record['solar_term']:
                term = record['solar_term']
                solar_terms[term] = solar_terms.get(term, 0) + 1
        
        print(f"  共有 {len(solar_terms)} 个节气")
        for term, count in sorted(solar_terms.items()):
            print(f"    {term}: {count}次")
        
        # 统计节日
        print(f"\n统计公历节日:")
        gregorian_festivals = {}
        for record in records:
            if record['gregorian_festival']:
                festival = record['gregorian_festival']
                gregorian_festivals[festival] = gregorian_festivals.get(festival, 0) + 1
        
        print(f"  共有 {len(gregorian_festivals)} 个公历节日")
        for festival, count in sorted(gregorian_festivals.items(), key=lambda x: -x[1])[:10]:
            print(f"    {festival}: {count}次")
        
        print(f"\n{'=' * 60}")
        print("测试完成")
        print(f"{'=' * 60}")
        
    except Exception as e:
        print(f"\n✗ 加载失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_wannianli_data()
