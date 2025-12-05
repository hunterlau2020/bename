import json

# 加载转换后的数据
with open('data/kangxi_converted.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

# 获取实际的数据数组
data = json_data.get('data', [])
print(f'总记录数: {len(data)}')

# 检查所有数据
invalid = []
for item in data:
    # 检查 character 字段
    if 'character' not in item or len(item['character']) != 1:
        invalid.append(('character', item))
        continue
    
    # 检查 strokes 字段
    if 'strokes' not in item or not isinstance(item['strokes'], int) or not (1 <= item['strokes'] <= 64):
        invalid.append(('strokes', item))
        continue
    
    # 检查 pinyin 字段
    if 'pinyin' not in item or not item['pinyin']:
        invalid.append(('pinyin', item))
        continue

print(f'\n总计无效记录数: {len(invalid)}')
if invalid:
    print('\n前5个无效记录示例:')
    for i, (reason, item) in enumerate(invalid[:5]):
        print(f"{i+1}. 原因: {reason}")
        print(f"   数据: {item}")
        print()
