# -*- coding: utf-8 -*-
"""验证万年历数据"""
import sqlite3

conn = sqlite3.connect('local.db')
cursor = conn.cursor()

dates = ['2000-02-03', '2000-02-04', '2024-02-10']

for date in dates:
    cursor.execute('''
    SELECT gregorian_date, year_ganzhi, month_ganzhi, day_ganzhi, solar_term
    FROM wannianli WHERE gregorian_date = ?
    ''', (date,))
    
    row = cursor.fetchone()
    if row:
        print(f"{row[0]}: 年={row[1]} 月={row[2]} 日={row[3]} 节气={row[4] or '无'}")

conn.close()
