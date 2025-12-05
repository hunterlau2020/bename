# -*- coding: utf-8 -*-
"""验证合并后的万年历数据"""
import json

print("=" * 60)
print("验证万年历数据")
print("=" * 60)

with open('data/wannianli.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\n版本: {data['version']}")
print(f"描述: {data['description']}")
print(f"数据源: {data['source']}")
print(f"总记录数: {data['total_records']}")
print(f"日期范围: {data['date_range']['start']} 至 {data['date_range']['end']}")

records = data['data']

print(f"\n实际记录数: {len(records)}")

# 测试几个关键日期
test_dates = ['1900-01-01', '1950-10-01', '1969-12-31', '1970-01-01', '2000-02-04']

print("\n关键日期测试:")
for date in test_dates:
    record = next((r for r in records if r['gregorian_date'].startswith(date)), None)
    if record:
        print(f"\n  {date}:")
        print(f"    农历: {record['lunar_show']}")
        print(f"    干支: {record['year_ganzhi']} {record['month_ganzhi']} {record['day_ganzhi']}")
        print(f"    生肖: {record['zodiac']}")
        if record['solar_term']:
            print(f"    节气: {record['solar_term']}")
        if record['shen_wei']:
            print(f"    神位: {record['shen_wei'][:50]}...")
    else:
        print(f"\n  {date}: 未找到")

# 统计年份分布
years = {}
for record in records:
    year = record['gregorian_date'][:4]
    years[year] = years.get(year, 0) + 1

print(f"\n年份统计:")
print(f"  最早年份: {min(years.keys())}")
print(f"  最晚年份: {max(years.keys())}")
print(f"  总年数: {len(years)}")

# 验证连续性
sorted_dates = sorted([r['gregorian_date'].split()[0] for r in records])
print(f"\n连续性检查:")
print(f"  第一条: {sorted_dates[0]}")
print(f"  最后一条: {sorted_dates[-1]}")

print("\n" + "=" * 60)
print("验证完成！")
print("=" * 60)
