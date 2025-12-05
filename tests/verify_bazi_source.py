# -*- coding: utf-8 -*-
"""验证八字计算使用万年历数据"""
import logging
from datetime import datetime
from modules.calculator import Calculator

# 启用日志查看详细信息
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

calc = Calculator()

print("=" * 60)
print("验证八字计算是否使用万年历数据")
print("=" * 60)

test_date = datetime(2000, 2, 4, 12, 0, 0)
print(f"\n测试日期: {test_date}")
print("-" * 60)

result = calc.calculate_bazi(test_date, 120.0, 30.0)

print("\n计算结果:")
print(f"八字: {result['bazi_str']}")
print(f"农历: {result['lunar_date']}")
print(f"五行: {result['wuxing']}")

print("\n" + "=" * 60)
print("如果日志中显示'使用万年历数据计算八字'，则说明成功！")
print("=" * 60)
