import json

# 读取数据
with open('data/wannianli.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# 提取记录数据
data = json_data.get('data', [])

# 检查前5条1900年的记录
print('1900年前5条记录:\n')
r1900 = [r for r in data if r['gregorian_date'].startswith('1900-')][:5]
for r in r1900:
    print(f"{r['gregorian_date']}: lunar_date='{r['lunar_date']}', lunar_show='{r['lunar_show']}'")

print('\n1970年前5条记录:\n')
r1970 = [r for r in data if r['gregorian_date'].startswith('1970-')][:5]
for r in r1970:
    print(f"{r['gregorian_date']}: lunar_date='{r['lunar_date']}', lunar_show='{r['lunar_show']}'")

# 统计转换情况
empty_count = sum(1 for r in data if not r['lunar_date'])
filled_count = len(data) - empty_count

# 按年份范围统计
before_1970 = [r for r in data if r['gregorian_date'] < '1970-01-01']
after_1970 = [r for r in data if r['gregorian_date'] >= '1970-01-01']

empty_before = sum(1 for r in before_1970 if not r['lunar_date'])
empty_after = sum(1 for r in after_1970 if not r['lunar_date'])

print(f"\n总记录数: {len(data)}")
print(f"  1900-1969: {len(before_1970)} 条，lunar_date为空: {empty_before} 条")
print(f"  1970-2099: {len(after_1970)} 条，lunar_date为空: {empty_after} 条")
print(f"\n总体lunar_date统计:")
print(f"  为空: {empty_count} 条")
print(f"  已填充: {filled_count} 条")
