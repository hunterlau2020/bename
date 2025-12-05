# -*- coding: utf-8 -*-
"""测试早期日期（1900-1969）的八字计算"""
import logging
from datetime import datetime
from modules.calculator import Calculator

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

calc = Calculator()

print("=" * 60)
print("测试早期日期的八字计算（1900-1969）")
print("=" * 60)

test_cases = [
    datetime(1900, 1, 1, 12, 0, 0),  # 1900年元旦
    datetime(1949, 10, 1, 15, 0, 0), # 开国大典
    datetime(1969, 12, 31, 18, 0, 0), # 1969年最后一天
]

for birth_dt in test_cases:
    print(f"\n{'='*60}")
    print(f"测试日期: {birth_dt}")
    print('-' * 60)
    
    result = calc.calculate_bazi(birth_dt, 120.0, 30.0)
    
    print(f"八字: {result['bazi_str']}")
    print(f"农历: {result['lunar_date']}")
    print(f"五行: {result['wuxing']}")
    print(f"评分: {result['score']}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
