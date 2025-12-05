"""
测试万年历数据查询和农历日期转换
"""
import sqlite3
from pathlib import Path

db_path = Path('local.db')

if not db_path.exists():
    print(f"数据库不存在: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("=" * 60)
print("万年历数据测试")
print("=" * 60)

# 测试关键日期
test_dates = [
    '1900-01-01',
    '1949-10-01',
    '1969-12-31',
    '1970-01-01',
    '2024-01-01'
]

print("\n测试日期查询:\n")
for date_str in test_dates:
    cursor.execute("""
        SELECT gregorian_date, lunar_date, lunar_show, 
               year_ganzhi, month_ganzhi, day_ganzhi, zodiac
        FROM wannianli 
        WHERE gregorian_date = ?
    """, (date_str,))
    
    result = cursor.fetchone()
    if result:
        print(f"公历: {result[0]}")
        print(f"  农历数字: {result[1]}")
        print(f"  农历显示: {result[2]}")
        print(f"  干支: {result[3]}年 {result[4]}月 {result[5]}日")
        print(f"  生肖: {result[6]}")
        print()
    else:
        print(f"未找到日期: {date_str}\n")

# 统计信息
cursor.execute("SELECT COUNT(*) FROM wannianli")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM wannianli WHERE lunar_date != ''")
with_lunar = cursor.fetchone()[0]

cursor.execute("SELECT MIN(gregorian_date), MAX(gregorian_date) FROM wannianli")
date_range = cursor.fetchone()

print(f"\n数据统计:")
print(f"  总记录数: {total}")
print(f"  有lunar_date: {with_lunar}")
print(f"  日期范围: {date_range[0]} 至 {date_range[1]}")

conn.close()
