# -*- coding: utf-8 -*-
"""
字义音形分析模块 - 姓名字义、音律、字形分析
基于康熙字典的吉凶和拼音音调分析
"""

import sqlite3
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


class ZiyiAnalyzer:
    """字义音形分析器"""
    
    def __init__(self, db_path: str = 'local.db'):
        """初始化字义分析器
        
        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
    
    def _get_char_info(self, char: str) -> Dict:
        """获取单个字的康熙字典信息
        
        Args:
            char: 单个汉字
            
        Returns:
            字符信息字典
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT character, traditional, pinyin, luck, wuxing, radical
                FROM kangxi_strokes 
                WHERE character = ?
            """, (char,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'character': row[0],
                    'traditional': row[1] or row[0],
                    'pinyin': row[2] or '',
                    'luck': row[3] or '中',
                    'wuxing': row[4] or '未知',
                    'radical': row[5] or '未知'
                }
        except Exception as e:
            logger.error(f"查询字符信息失败: {e}")
        
        return {
            'character': char,
            'traditional': char,
            'pinyin': '',
            'luck': '中',
            'wuxing': '未知',
            'radical': '未知'
        }
    
    def _extract_tone(self, pinyin: str) -> int:
        """提取拼音音调
        
        Args:
            pinyin: 拼音字符串（如 'zhāng', 'wáng'）
            
        Returns:
            音调 (1-4)，无音调返回 0
        """
        if not pinyin:
            return 0
        
        # 声调对应的拼音字母
        tone_map = {
            'ā': 1, 'á': 1, 'ǎ': 1, 'à': 1,
            'ē': 2, 'é': 2, 'ě': 2, 'è': 2,
            'ī': 3, 'í': 3, 'ǐ': 3, 'ì': 3,
            'ō': 4, 'ó': 4, 'ǒ': 4, 'ò': 4,
            'ū': 5, 'ú': 5, 'ǔ': 5, 'ù': 5,
            'ǖ': 6, 'ǘ': 6, 'ǚ': 6, 'ǜ': 6
        }
        
        # 四声对应
        first_tone = ['ā', 'ē', 'ī', 'ō', 'ū', 'ǖ']  # 阴平
        second_tone = ['á', 'é', 'í', 'ó', 'ú', 'ǘ']  # 阳平
        third_tone = ['ǎ', 'ě', 'ǐ', 'ǒ', 'ǔ', 'ǚ']  # 上声
        fourth_tone = ['à', 'è', 'ì', 'ò', 'ù', 'ǜ']  # 去声
        
        for char in pinyin:
            if char in first_tone:
                return 1
            elif char in second_tone:
                return 2
            elif char in third_tone:
                return 3
            elif char in fourth_tone:
                return 4
        
        return 0  # 轻声或无音调
    
    def _analyze_luck(self, chars_info: List[Dict]) -> Dict:
        """分析字义吉凶
        
        Args:
            chars_info: 字符信息列表
            
        Returns:
            吉凶分析结果
        """
        luck_score = {
            '吉': 100,
            '大吉': 100,
            '中': 75,
            '凶': 50,
            '大凶': 30,
            '未知': 70
        }
        
        total_score = 0
        luck_details = []
        
        for info in chars_info:
            char = info['traditional']
            luck = info['luck']
            score = luck_score.get(luck, 70)
            total_score += score
            
            luck_details.append(f"{char}({luck})")
        
        avg_score = total_score / len(chars_info) if chars_info else 70
        
        # 评价
        if avg_score >= 90:
            comment = "字义吉祥，寓意美好"
        elif avg_score >= 75:
            comment = "字义中和，寓意平和"
        else:
            comment = "字义欠佳，建议慎用"
        
        return {
            'score': round(avg_score),
            'details': luck_details,
            'comment': comment
        }
    
    def _analyze_tone(self, chars_info: List[Dict]) -> Dict:
        """分析音韵音调
        
        Args:
            chars_info: 字符信息列表
            
        Returns:
            音调分析结果
        """
        tones = []
        tone_names = ['', '阴平', '阳平', '上声', '去声']
        
        for info in chars_info:
            tone = self._extract_tone(info['pinyin'])
            if tone > 0:
                tones.append(tone)
        
        if not tones:
            return {
                'score': 70,
                'pattern': '无音调信息',
                'comment': '缺少拼音数据'
            }
        
        # 音调模式分析
        tone_pattern = ''.join([tone_names[t] for t in tones])
        
        # 评分规则
        score = 80  # 基础分
        comment_parts = []
        
        # 1. 避免全部相同音调（单调）
        if len(set(tones)) == 1:
            score -= 10
            comment_parts.append("音调单一")
        else:
            comment_parts.append("音调多变")
        
        # 2. 平仄协调（简化规则）
        # 平声：1,2声（阴平、阳平）
        # 仄声：3,4声（上声、去声）
        ping = sum(1 for t in tones if t in [1, 2])
        ze = sum(1 for t in tones if t in [3, 4])
        
        if ping > 0 and ze > 0:
            score += 10
            comment_parts.append("平仄相间")
        
        # 3. 理想模式：平-仄或仄-平（适合两字名）
        if len(tones) == 2:
            if (tones[0] in [1, 2] and tones[1] in [3, 4]) or \
               (tones[0] in [3, 4] and tones[1] in [1, 2]):
                score += 10
                comment_parts.append("音韵和谐")
        
        # 4. 避免拗口（连续上声）
        for i in range(len(tones) - 1):
            if tones[i] == 3 and tones[i+1] == 3:
                score -= 10
                comment_parts.append("连上声拗口")
                break
        
        # 限制分数范围
        score = max(60, min(100, score))
        
        return {
            'score': score,
            'pattern': tone_pattern,
            'tones': tones,
            'comment': '，'.join(comment_parts)
        }
    
    def analyze_ziyi(self, name: str) -> Dict:
        """字义音形分析
        
        Args:
            name: 姓名
            
        Returns:
            字义音形分析结果字典，包含：
            - score: 总分
            - luck_analysis: 吉凶分析
            - tone_analysis: 音调分析
            - analysis: 综合分析文本
        """
        logger.info(f"分析字义音形: {name}")
        
        # 获取每个字的信息
        chars_info = [self._get_char_info(char) for char in name]
        
        # 1. 字义吉凶分析
        luck_result = self._analyze_luck(chars_info)
        
        # 2. 音韵音调分析
        tone_result = self._analyze_tone(chars_info)
        
        # 3. 综合评分（字义70%，音韵30%）
        total_score = round(luck_result['score'] * 0.7 + tone_result['score'] * 0.3)
        
        # 4. 生成分析文本
        analysis_parts = []
        
        # 字义部分
        analysis_parts.append(f"【字义吉凶】{' '.join(luck_result['details'])} - {luck_result['comment']}")
        
        # 音韵部分
        if tone_result['pattern'] != '无音调信息':
            analysis_parts.append(f"【音韵分析】{tone_result['pattern']} - {tone_result['comment']}")
        
        # 综合评价
        if total_score >= 85:
            overall = "字义音韵俱佳，是理想的姓名"
        elif total_score >= 75:
            overall = "字义音韵良好，姓名较为合适"
        elif total_score >= 65:
            overall = "字义音韵尚可，姓名可以接受"
        else:
            overall = "字义音韵欠佳，建议斟酌"
        
        analysis_parts.append(f"【综合评价】{overall}")
        
        return {
            'score': total_score,
            'luck_analysis': luck_result,
            'tone_analysis': tone_result,
            'analysis': '\n'.join(analysis_parts),
            'chars_detail': chars_info
        }
