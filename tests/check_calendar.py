# -*- coding: utf-8 -*-
"""检查 ch_calendar.xls 文件结构"""
import pandas as pd

try:
    df = pd.read_excel('predata/ch_calendar.xls', engine='xlrd')
    print("文件列名：")
    print(df.columns.tolist())
    print(f"\n总行数: {len(df)}")
    print("\n前5行数据：")
    print(df.head())
    print("\n数据类型：")
    print(df.dtypes)
except Exception as e:
    print(f"错误: {e}")
