#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模拟UI测试 - 验证完整流程
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.calculator import Calculator
from modules.storage import Storage
from modules.ui import UserInterface

def test_display():
    """测试显示功能"""
    calculator = Calculator()
    storage = Storage()
    ui = UserInterface(calculator, storage)
    
    # 获取已保存的结果
    print("从缓存读取测试结果...")
    result = storage.query_test_result(
        '刘德华',
        '男',
        '1961-09-27 10:30',
        114.17,
        22.32
    )
    
    if result:
        print("✓ 读取成功\n")
        try:
            # 调用UI的显示方法
            ui._display_result(result)
            print("\n✓ 显示成功 - 没有KeyError!")
        except KeyError as e:
            print(f"\n✗ KeyError仍然存在: {e}")
        except Exception as e:
            print(f"\n✗ 其他错误: {e}")
    else:
        print("✗ 没有找到测试数据")

if __name__ == '__main__':
    test_display()
