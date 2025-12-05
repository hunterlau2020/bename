#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证农历显示
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.calculator import Calculator
from modules.storage import Storage
from modules.ui import UserInterface

def quick_test():
    """快速测试一个姓名"""
    calculator = Calculator()
    storage = Storage()
    
    # 测试数据
    surname = '李'
    given_name = '小龙'
    gender = '男'
    birth_time = '1940-11-27 06:00'
    longitude = 122.27
    latitude = 37.48
    
    print("=" * 60)
    print("快速测试 - 农历显示功能")
    print("=" * 60)
    print(f"\n测试姓名: {surname}{given_name}")
    print(f"出生时间: {birth_time}")
    print(f"出生地: 经度{longitude}°, 纬度{latitude}°")
    print("\n正在计算...")
    
    # 执行计算
    result = calculator.calculate_name(
        surname, given_name, gender, birth_time, longitude, latitude
    )
    
    # 使用UI的显示方法
    ui = UserInterface(calculator, storage)
    ui._display_result(result)

if __name__ == '__main__':
    quick_test()
