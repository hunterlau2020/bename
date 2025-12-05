#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试TXT解析"""

from pathlib import Path

file_path = Path('example_input.txt')

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"文件内容:\n{content}")
print(f"\n检测: ':' in content = {':' in content}")
print(f"检测: '\\n\\n' in content = {chr(10)+chr(10) in content}")

lines = content.strip().split('\n')
print(f"\n总行数: {len(lines)}")

line_no = 0
for line in lines:
    line_no += 1
    # 跳过空行和注释行
    if not line.strip() or line.strip().startswith('#'):
        print(f"第 {line_no} 行 - 跳过（空行或注释）: {repr(line)}")
        continue
    
    parts = line.split()
    print(f"第 {line_no} 行 - 解析: {parts}")
    
    if len(parts) < 3:
        print(f"  字段不足（需要至少3个字段）")
    else:
        print(f"  有效记录: 姓名={parts[0]}, 性别={parts[1]}, 日期={parts[2]}")
