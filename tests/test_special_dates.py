import json

# 读取数据
with open('data/wannianli.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

data = json_data.get('data', [])

# 测试特殊日期格式
print('特殊日期格式转换测试:\n')

# 正月（1月）
print('【正月测试】')
records = [r for r in data if '正月' in r.get('lunar_show', '')][:3]
for r in records:
    print(f"{r['gregorian_date']}: {r['lunar_show']} → {r['lunar_date']}")

# 冬月（11月）
print('\n【冬月测试】')
records = [r for r in data if '冬月' in r.get('lunar_show', '')][:3]
for r in records:
    print(f"{r['gregorian_date']}: {r['lunar_show']} → {r['lunar_date']}")

# 腊月（12月）
print('\n【腊月测试】')
records = [r for r in data if '腊月' in r.get('lunar_show', '')][:3]
for r in records:
    print(f"{r['gregorian_date']}: {r['lunar_show']} → {r['lunar_date']}")

# 初一到初十
print('\n【初X测试】')
records = [r for r in data if '初一' in r.get('lunar_show', '') or '初五' in r.get('lunar_show', '') or '初十' in r.get('lunar_show', '')][:3]
for r in records:
    print(f"{r['gregorian_date']}: {r['lunar_show']} → {r['lunar_date']}")

# 廿X
print('\n【廿X测试】')
records = [r for r in data if '廿' in r.get('lunar_show', '')][:3]
for r in records:
    print(f"{r['gregorian_date']}: {r['lunar_show']} → {r['lunar_date']}")

# 三十
print('\n【三十测试】')
records = [r for r in data if '三十' in r.get('lunar_show', '')][:3]
for r in records:
    print(f"{r['gregorian_date']}: {r['lunar_show']} → {r['lunar_date']}")
