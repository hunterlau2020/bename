#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试UI中的清空历史功能
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.calculator import Calculator
from modules.storage import Storage
from modules.ui import UserInterface

def test_ui_clear():
    """测试UI清空功能"""
    calculator = Calculator()
    storage = Storage()
    ui = UserInterface(calculator, storage)
    
    # 检查当前记录数
    count = storage.get_records_count()
    print(f"当前历史记录数: {count}")
    
    if count > 0:
        print("\n测试 _handle_clear_history 方法...")
        print("=" * 60)
        ui._handle_clear_history()
        print("=" * 60)
        
        # 检查清空后的记录数
        new_count = storage.get_records_count()
        print(f"\n清空后历史记录数: {new_count}")
        
        if new_count == 0:
            print("✓ 清空成功!")
        else:
            print(f"✗ 清空失败，还有 {new_count} 条记录")
    else:
        print("没有历史记录，无需测试清空功能")

if __name__ == '__main__':
    test_ui_clear()
