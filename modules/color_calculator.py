# -*- coding: utf-8 -*-
"""
颜色推荐模块 - 根据五行喜用神推荐吉祥颜色
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class ColorCalculator:
    """颜色推荐计算器"""
    
    def __init__(self):
        """初始化颜色计算器"""
        # 五行颜色对应表
        self.WUXING_COLOR = {
            '木': '绿色、青色、翠色',
            '火': '红色、紫色、粉色',
            '土': '黄色、棕色、咖啡色',
            '金': '白色、金色、银色',
            '水': '黑色、蓝色、灰色'
        }
    
    def get_lucky_colors(self, xiyong_shen: List[str]) -> str:
        """根据喜用神获取吉祥颜色
        
        Args:
            xiyong_shen: 喜用神列表
            
        Returns:
            吉祥颜色字符串
        """
        logger.info(f"获取吉祥颜色: 喜用神={xiyong_shen}")
        
        colors = []
        for wx in xiyong_shen:
            color = self.WUXING_COLOR.get(wx, '')
            if color:
                colors.append(color)
        
        result = '、'.join(colors)
        logger.info(f"吉祥颜色: {result}")
        
        return result
    
    def get_color_by_wuxing(self, wuxing: str) -> str:
        """根据五行获取颜色
        
        Args:
            wuxing: 五行
            
        Returns:
            颜色字符串
        """
        return self.WUXING_COLOR.get(wuxing, '')
