# -*- coding: utf-8 -*-
"""
称骨算命模块 - 称骨重量计算和命书查询
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class ChengguCalculator:
    """称骨算命计算器"""
    
    def __init__(self, db_path: str = 'local.db'):
        """初始化称骨计算器"""
        self.db_path = db_path
    
    def calculate_chenggu(self, birth_dt: datetime, wannianli_data: Dict = None) -> Dict:
        """称骨算命计算
        
        Args:
            birth_dt: 出生日期时间
            wannianli_data: 万年历数据（可选）
            
        Returns:
            包含骨重、命书和评价的字典
        """
        logger.info(f"计算称骨: {birth_dt}")
        
        # 获取农历信息
        if wannianli_data and wannianli_data.get('lunar_date'):
            try:
                lunar_date_parts = wannianli_data['lunar_date'].split('-')
                lunar_year = int(lunar_date_parts[0])
                lunar_month = int(lunar_date_parts[1])
                lunar_day = int(lunar_date_parts[2])
            except:
                lunar_year = birth_dt.year
                lunar_month = birth_dt.month
                lunar_day = birth_dt.day
        else:
            # 降级到使用阳历
            lunar_year = birth_dt.year
            lunar_month = birth_dt.month
            lunar_day = birth_dt.day
        
        # 计算时辰序号(0-11)
        hour = birth_dt.hour
        shichen_idx = (hour + 1) // 2 % 12
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 1. 查询年骨重
            cursor.execute('''
            SELECT weight FROM chenggu_weights 
            WHERE type='year' AND value=?
            ''', (lunar_year,))
            row = cursor.fetchone()
            year_weight = row[0] if row else 0
            
            # 2. 查询月骨重
            cursor.execute('''
            SELECT weight FROM chenggu_weights 
            WHERE type='month' AND value=?
            ''', (lunar_month,))
            row = cursor.fetchone()
            month_weight = row[0] if row else 0
            
            # 3. 查询日骨重
            cursor.execute('''
            SELECT weight FROM chenggu_weights 
            WHERE type='day' AND value=?
            ''', (lunar_day,))
            row = cursor.fetchone()
            day_weight = row[0] if row else 0
            
            # 4. 查询时骨重
            cursor.execute('''
            SELECT weight FROM chenggu_weights 
            WHERE type='hour' AND value=?
            ''', (shichen_idx,))
            row = cursor.fetchone()
            hour_weight = row[0] if row else 0
            
            # 5. 计算总骨重
            total_weight = year_weight + month_weight + day_weight + hour_weight
            total_weight = round(total_weight, 1)
            
            logger.info(f"称骨详情: 年{year_weight} + 月{month_weight} + 日{day_weight} + 时{hour_weight} = {total_weight}两")
            
            # 6. 查询命书(查找最接近的骨重)
            cursor.execute('''
            SELECT weight, fortune_text FROM chenggu_fortune
            ORDER BY ABS(weight - ?) ASC
            LIMIT 1
            ''', (total_weight,))
            row = cursor.fetchone()
            
            if row:
                fortune_text = row[1]
            else:
                fortune_text = "未找到对应命书"
            
            # 7. 根据骨重给出评价
            if total_weight <= 2.1:
                comment = "薄命之格，多灾多难"
            elif total_weight <= 3.0:
                comment = "命运较苦，需自强不息"
            elif total_weight <= 4.4:
                comment = "命运中等，衣食无忧"
            elif total_weight < 6.0:
                comment = "命运极佳，大富大贵"
            else:
                comment = "极尊贵之命，富贵显赫，常为王侯将相之格"
            
            return {
                'weight': total_weight,
                'fortune_text': fortune_text,
                'comment': comment
            }
            
        except Exception as e:
            logger.error(f"称骨算命计算失败: {e}")
            return {
                'weight': 0,
                'fortune_text': "计算失败",
                'comment': "数据不完整"
            }
        finally:
            conn.close()
