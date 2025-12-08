# -*- coding: utf-8 -*-
"""
计算模块 - 核心计算引擎，执行各项命理学计算
重构版：使用模块化设计，将功能拆分到独立模块
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Tuple

# 导入各个功能模块
from .bazi_calculator import BaziCalculator
from .wuge_calculator import WugeCalculator
from .chenggu_calculator import ChengguCalculator
from .color_calculator import ColorCalculator
from .shengxiao_analyzer import ShengxiaoAnalyzer
from .ziyi_analyzer import ZiyiAnalyzer

logger = logging.getLogger(__name__)


class Calculator:
    """计算引擎类 - 协调各个功能模块完成综合命理计算"""
    
    def __init__(self, db_path: str = 'local.db'):
        """初始化计算模块
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        
        # 初始化各个功能模块
        self.bazi_calc = BaziCalculator(db_path)
        self.wuge_calc = WugeCalculator(db_path)
        self.chenggu_calc = ChengguCalculator(db_path)
        self.color_calc = ColorCalculator()
        self.shengxiao_analyzer = ShengxiaoAnalyzer()
        self.ziyi_analyzer = ZiyiAnalyzer(db_path)
    
    def calculate_name(self, surname: str, given_name: str, gender: str, birth_time: str,
                      longitude: float, latitude: float) -> Dict:
        """执行完整的姓名测试计算
        
        Args:
            surname: 姓氏
            given_name: 名字
            gender: 性别
            birth_time: 出生时间 (YYYY-MM-DD HH:MM)
            longitude: 经度
            latitude: 纬度
            
        Returns:
            完整的计算结果字典
        """
        try:
            full_name = surname + given_name
            logger.info(f"开始计算: {surname}(姓) {given_name}(名), {gender}, {birth_time}")
            
            # 解析出生时间
            birth_dt = datetime.strptime(birth_time, '%Y-%m-%d %H:%M')
            
            # 1. 数据验证
            self._validate_input(full_name, gender, birth_dt, longitude, latitude)
            
            # 2. 优先从万年历获取完整信息
            wannianli_data = self.bazi_calc._get_ganzhi_from_wannianli(birth_dt)
            
            # 3. 三才五格计算（使用WugeCalculator）
            wuge_result = self.wuge_calc.calculate_wuge(surname, given_name)
            
            # 4. 生辰八字计算（使用BaziCalculator）
            bazi_result = self.bazi_calc.calculate_bazi(birth_dt, wannianli_data, longitude, latitude)
            
            # 5. 吉祥颜色推荐（使用ColorCalculator）
            bazi_result['color'] = self.color_calc.get_lucky_colors(bazi_result['xiyong_shen'])
            
            # 6. 字义音形分析（使用ZiyiAnalyzer）
            ziyi_result = self.ziyi_analyzer.analyze_ziyi(full_name)
            
            # 7. 生肖喜忌分析（使用ShengxiaoAnalyzer）
            shengxiao_result = self.shengxiao_analyzer.analyze_shengxiao(full_name, birth_dt)
            
            # 8. 称骨算命计算（使用ChengguCalculator）
            chenggu_result = self.chenggu_calc.calculate_chenggu(birth_dt, wannianli_data)
            
            # 9. 综合评分
            comprehensive_score = self._calculate_comprehensive_score(
                wuge_result['score'],
                bazi_result['score'],
                ziyi_result['score'],
                shengxiao_result['score']
            )
            
            # 组装结果
            result = {
                'name': full_name,
                'surname': surname,
                'given_name': given_name,
                'gender': gender,
                'birth_time': birth_time,
                'longitude': longitude,
                'latitude': latitude,
                'comprehensive_score': comprehensive_score,
                'wuge': wuge_result,
                'bazi': bazi_result,
                'ziyi': ziyi_result,
                'shengxiao': shengxiao_result,
                'chenggu': chenggu_result,
                'suggestion': self._generate_suggestion(comprehensive_score),
                'calc_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            logger.info(f"计算完成，综合评分: {comprehensive_score}")
            return result
            
        except Exception as e:
            logger.exception(f"计算过程出错: {e}")
            raise
    
    def _validate_input(self, name: str, gender: str, birth_dt: datetime,
                       longitude: float, latitude: float):
        """验证输入数据
        
        Args:
            name: 完整姓名
            gender: 性别
            birth_dt: 出生日期时间
            longitude: 经度
            latitude: 纬度
            
        Raises:
            ValueError: 数据验证失败
        """
        # 验证姓名
        if not name or len(name) < 2 or len(name) > 4:
            raise ValueError("姓名长度必须为2-4个汉字")
        
        for char in name:
            if not '\u4e00' <= char <= '\u9fff':
                raise ValueError(f"姓名包含非法字符: {char}")
        
        # 验证性别
        if gender not in ['男', '女']:
            raise ValueError("性别必须为'男'或'女'")
        
        # 验证日期
        if birth_dt > datetime.now():
            raise ValueError("出生日期不能大于当前日期")
        
        if birth_dt.year < 1900 or birth_dt.year > 2100:
            raise ValueError("出生年份必须在1900-2100之间")
        
        # 验证经纬度
        if not (73.0 <= longitude <= 135.0):
            raise ValueError("经度必须在73.0-135.0之间")
        
        if not (3.0 <= latitude <= 54.0):
            raise ValueError("纬度必须在3.0-54.0之间")
    
    def _calculate_comprehensive_score(self, wuge_score: int, bazi_score: int,
                                      ziyi_score: int, shengxiao_score: int) -> int:
        """计算综合评分
        
        Args:
            wuge_score: 五格评分
            bazi_score: 八字评分
            ziyi_score: 字义音形评分
            shengxiao_score: 生肖评分
            
        Returns:
            综合评分
        """
        score = (wuge_score * 0.3 + bazi_score * 0.4 + 
                ziyi_score * 0.15 + shengxiao_score * 0.15)
        return round(score)
    
    def _generate_suggestion(self, score: int) -> str:
        """根据综合评分生成建议
        
        Args:
            score: 综合评分
            
        Returns:
            建议文本
        """
        if score >= 90:
            return "姓名配置极佳，各项指标优秀，建议继续使用。"
        elif score >= 75:
            return "姓名整体配置良好，建议继续使用。"
        elif score >= 60:
            return "姓名配置一般，可以考虑改进。"
        else:
            return "姓名配置欠佳，建议考虑改名。"
    
    # ===== 以下方法保留以兼容旧代码，直接委托给相应的模块 =====
    
    def calculate_wuge(self, surname: str, given_name: str) -> Dict:
        """计算三才五格（委托给WugeCalculator）"""
        return self.wuge_calc.calculate_wuge(surname, given_name)
    
    def calculate_bazi(self, birth_dt: datetime, wannianli_data: dict, 
                      longitude: float, latitude: float) -> Dict:
        """计算生辰八字（委托给BaziCalculator）"""
        return self.bazi_calc.calculate_bazi(birth_dt, wannianli_data, longitude, latitude)
    
    def analyze_ziyi(self, name: str) -> Dict:
        """字义音形分析（委托给ZiyiAnalyzer）"""
        return self.ziyi_analyzer.analyze_ziyi(name)
    
    def analyze_shengxiao(self, name: str, birth_dt: datetime) -> Dict:
        """生肖喜忌分析（委托给ShengxiaoAnalyzer）"""
        return self.shengxiao_analyzer.analyze_shengxiao(name, birth_dt)
    
    def calculate_chenggu(self, birth_dt: datetime) -> Dict:
        """称骨算命计算（委托给ChengguCalculator）"""
        wannianli_data = self.bazi_calc._get_ganzhi_from_wannianli(birth_dt)
        return self.chenggu_calc.calculate_chenggu(birth_dt, wannianli_data)
