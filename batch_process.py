#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量处理入口脚本
"""

import sys
from pathlib import Path
from modules.calculator import Calculator
from modules.storage import Storage
from modules.batch_processor import BatchProcessor


def main():
    if len(sys.argv) < 2:
        print("用法: python batch_process.py <输入文件>")
        print("支持的文件格式: .txt, .json, .csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 初始化
    calc = Calculator('local.db')
    storage = Storage('local.db')
    processor = BatchProcessor(calc, storage)
    
    # 处理文件
    result = processor.process_file(input_file)
    
    if result['success']:
        print(f"\n批处理成功完成！")
        print(f"结果已保存到: {result['output_file']}")
    else:
        print(f"\n批处理失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
