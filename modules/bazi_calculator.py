# -*- coding: utf-8 -*-
"""
八字计算模块 - 生辰八字相关计算
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

try:
    from lunarcalendar import Converter, Solar, Lunar
    LUNAR_AVAILABLE = True
except ImportError:
    LUNAR_AVAILABLE = False
    logger.warning("lunarcalendar库未安装，农历功能不可用")


class BaziCalculator:
    """八字计算器"""
    
    def __init__(self, db_path: str = 'local.db'):
        """初始化八字计算器"""
        self.db_path = db_path
        
        # 天干地支
        self.TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        self.DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        # 天干五行
        self.TIANGAN_WUXING = {
            '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
            '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
        }
        
        # 地支五行
        self.DIZHI_WUXING = {
            '寅': '木', '卯': '木', '巳': '火', '午': '火',
            '辰': '土', '戌': '土', '丑': '土', '未': '土',
            '申': '金', '酉': '金', '亥': '水', '子': '水'
        }
        
        # 五行生克
        self.WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        self.WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        self.WUXING_SHENG_SEQUENCE = ['木', '火', '土', '金', '水']
        
        # 生肖
        self.SHENGXIAO = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        
        # 天干地支索引
        self.TIANGAN_INDEX = {tg: i for i, tg in enumerate(self.TIANGAN)}
        self.DIZHI_INDEX = {dz: i for i, dz in enumerate(self.DIZHI)}
        
        # 天干强度表 (12个月x10个天干)
        self.TIANGAN_STRENGTH = [
            [1200, 1200, 1000, 1000, 1000, 1000, 1000, 1000, 1200, 1200],  # 子月
            [1060, 1060, 1000, 1000, 1100, 1100, 1140, 1140, 1100, 1100],  # 丑月
            [1140, 1140, 1200, 1200, 1060, 1060, 1000, 1000, 1000, 1000],  # 寅月
            [1200, 1200, 1200, 1200, 1000, 1000, 1000, 1000, 1000, 1000],  # 卯月
            [1100, 1100, 1060, 1060, 1100, 1100, 1100, 1100, 1040, 1040],  # 辰月
            [1000, 1000, 1140, 1140, 1140, 1140, 1060, 1060, 1060, 1060],  # 巳月
            [1000, 1000, 1200, 1200, 1200, 1200, 1000, 1000, 1000, 1000],  # 午月
            [1040, 1040, 1100, 1100, 1160, 1160, 1100, 1100, 1000, 1000],  # 未月
            [1060, 1060, 1000, 1000, 1000, 1000, 1140, 1140, 1200, 1200],  # 申月
            [1000, 1000, 1000, 1000, 1000, 1000, 1200, 1200, 1200, 1200],  # 酉月
            [1000, 1000, 1040, 1040, 1140, 1140, 1160, 1160, 1060, 1060],  # 戌月
            [1200, 1200, 1000, 1000, 1000, 1000, 1000, 1000, 1140, 1140],  # 亥月
        ]
        
        # 地支藏干强度表
        self.DIZHI_CANGGAN = [
            # 子 - 癸
            {'癸': [1200, 1100, 1000, 1000, 1040, 1060, 1000, 1000, 1200, 1200, 1060, 1140]},
            # 丑 - 癸辛己
            {'癸': [360, 330, 300, 300, 312, 318, 300, 300, 360, 360, 318, 342],
             '辛': [200, 228, 200, 200, 230, 212, 200, 220, 228, 248, 232, 200],
             '己': [500, 550, 530, 500, 550, 570, 600, 580, 500, 500, 570, 500]},
            # 寅 - 丙甲（注：原注释说应是甲丙戊，但实际数据只有丙甲两个藏干）
            {'丙': [300, 300, 360, 360, 318, 342, 360, 330, 300, 300, 342, 318],
             '甲': [840, 742, 798, 840, 770, 700, 700, 728, 742, 700, 700, 840]},
            # 卯 - 乙
            {'乙': [1200, 1060, 1140, 1200, 1100, 1000, 1000, 1040, 1060, 1000, 1000, 1200]},
            # 辰 - 乙癸戊
            {'乙': [360, 318, 342, 360, 330, 300, 300, 312, 318, 300, 300, 360],
             '癸': [240, 220, 200, 200, 208, 200, 200, 200, 240, 240, 212, 228],
             '戊': [500, 550, 530, 500, 550, 600, 600, 580, 500, 500, 570, 500]},
            # 巳 - 庚丙（注：丙火为主气，强度极高）
            {'庚': [300, 342, 300, 300, 330, 300, 300, 330, 342, 360, 348, 300],
             '丙': [700, 700, 840, 840, 742, 840, 840, 798, 700, 700, 728, 742]},
            # 午 - 丁（注：只有丁火一个藏干，为纯火之地）
            {'丁': [1000, 1000, 1200, 1200, 1060, 1140, 1200, 1100, 1000, 1000, 1040, 1060]},
            # 未 - 丁乙己
            {'丁': [300, 300, 360, 360, 318, 342, 360, 330, 300, 300, 312, 318],
             '乙': [240, 212, 228, 240, 220, 200, 200, 208, 212, 200, 200, 240],
             '己': [500, 550, 530, 500, 550, 570, 600, 580, 500, 500, 570, 500]},
            # 申 - 壬庚戊
            {'壬': [360, 330, 300, 300, 312, 318, 300, 300, 360, 360, 318, 342],
             '庚': [700, 798, 700, 700, 770, 742, 700, 770, 798, 840, 812, 700]},
            # 酉 - 辛
            {'辛': [1000, 1140, 1000, 1000, 1100, 1060, 1000, 1100, 1140, 1200, 1160, 1000]},
            # 戌 - 辛丁戊
            {'辛': [300, 342, 300, 300, 330, 318, 300, 330, 342, 360, 348, 300],
             '丁': [200, 200, 240, 240, 212, 228, 240, 220, 200, 200, 208, 212],
             '戊': [500, 550, 530, 500, 550, 570, 600, 580, 500, 500, 570, 500]},
            # 亥 - 甲壬
            {'甲': [360, 318, 342, 360, 330, 300, 300, 312, 318, 300, 300, 360],
             '壬': [840, 770, 700, 700, 728, 742, 700, 700, 840, 840, 724, 798]},
        ]
        
        # 四季用神速查表（来自传统命理典籍）
        self.SIJI_YONGSHEN_TABLE = {
            '木': {
                '春季': {
                    'yongshen': '火',
                    'theory': '初春木旺，需火泄秀',
                    'must_have': '火',
                    'better_have': '水、土',
                    'avoid': '金（克木）',
                    'bad_pattern': '木多无火（郁而不发）'
                },
                '夏季': {
                    'yongshen': '水',
                    'theory': '夏月木火俱旺，需水润局',
                    'must_have': '水',
                    'better_have': '金（生水）',
                    'avoid': '火（炎燥）、土（克水）',
                    'bad_pattern': '火土炎燥而无水'
                },
                '秋季': {
                    'yongshen': '水',
                    'theory': '金旺克木，水生木为用',
                    'must_have': '水',
                    'better_have': '土（泄金）',
                    'avoid': '金（克重）',
                    'bad_pattern': '金多木折'
                },
                '冬季': {
                    'yongshen': '火',
                    'theory': '冬月水寒木冻，需火暖局',
                    'must_have': '火',
                    'better_have': '土、木',
                    'avoid': '水（太寒）、金（无火）',
                    'bad_pattern': '水多木漂而无火'
                }
            },
            '火': {
                '春季': {
                    'yongshen': '水',
                    'theory': '春木助火，火势炎上',
                    'must_have': '水',
                    'better_have': '金（生水）',
                    'avoid': '木（火旺）、土（晦火）',
                    'bad_pattern': '木多火炽而无水制'
                },
                '夏季': {
                    'yongshen': '水',
                    'theory': '夏月火炎，水为急需',
                    'must_have': '水',
                    'better_have': '金（生水源）',
                    'avoid': '木火（炎燥太过）',
                    'bad_pattern': '火炎土燥无水'
                },
                '秋季': {
                    'yongshen': '木',
                    'theory': '金旺火囚，木生火为用',
                    'must_have': '木',
                    'better_have': '土',
                    'avoid': '水（灭火）、金（克木）',
                    'bad_pattern': '金水旺而无木'
                },
                '冬季': {
                    'yongshen': '木',
                    'theory': '冬月水旺火灭，木生火为急',
                    'must_have': '木',
                    'better_have': '土',
                    'avoid': '水（克火）',
                    'bad_pattern': '水多火灭'
                }
            },
            '土': {
                '春季': {
                    'yongshen': '火',
                    'theory': '春月木旺克土，火生土为用',
                    'must_have': '火',
                    'better_have': '金、土',
                    'avoid': '木（克土太过）',
                    'bad_pattern': '木多土崩无火'
                },
                '夏季': {
                    'yongshen': '水',
                    'theory': '夏月土燥，水润土为用',
                    'must_have': '水',
                    'better_have': '金（生水）',
                    'avoid': '火（燥土）',
                    'bad_pattern': '火炎土焦无水'
                },
                '秋季': {
                    'yongshen': '火',
                    'theory': '金旺泄土，火生土为用',
                    'must_have': '火',
                    'better_have': '木',
                    'avoid': '金（泄土气）',
                    'bad_pattern': '金多土弱无火'
                },
                '冬季': {
                    'yongshen': '火',
                    'theory': '冬月土寒，火暖土为用',
                    'must_have': '火',
                    'better_have': '土',
                    'avoid': '木（克土）、水（寒湿）',
                    'bad_pattern': '水多土流无火'
                }
            },
            '金': {
                '春季': {
                    'yongshen': '土',
                    'theory': '春月木旺金缺，土生金为用',
                    'must_have': '土',
                    'better_have': '火（炼金）',
                    'avoid': '木（克金）',
                    'bad_pattern': '木旺金缺无土'
                },
                '夏季': {
                    'yongshen': '水',
                    'theory': '夏月火旺金熔，水泄秀为用',
                    'must_have': '水',
                    'better_have': '土（生金）',
                    'avoid': '火（克金）、木（生火）',
                    'bad_pattern': '火旺金熔无水'
                },
                '秋季': {
                    'yongshen': '火',
                    'theory': '金旺需火锻炼成器',
                    'must_have': '火',
                    'better_have': '木（生火）',
                    'avoid': '金（太旺）、土（埋金）',
                    'bad_pattern': '金多无火锻炼'
                },
                '冬季': {
                    'yongshen': '火',
                    'theory': '冬月水寒金冷，火暖金为用',
                    'must_have': '火、土',
                    'better_have': '',
                    'avoid': '无火、土反而有金、水',
                    'bad_pattern': '木多而无火'
                }
            },
            '水': {
                '春季': {
                    'yongshen': '金',
                    'theory': '春木泄水，金生水为用',
                    'must_have': '金',
                    'better_have': '土（制木）',
                    'avoid': '木（泄水）',
                    'bad_pattern': '木多水缩无金'
                },
                '夏季': {
                    'yongshen': '金',
                    'theory': '夏月水弱，金生水为用',
                    'must_have': '金',
                    'better_have': '水',
                    'avoid': '火（克金）、土（克水）',
                    'bad_pattern': '火土旺而无金水'
                },
                '秋季': {
                    'yongshen': '木',
                    'theory': '金多水浊，木泄秀为用',
                    'must_have': '木',
                    'better_have': '火',
                    'avoid': '土（克水）、金（水浊）',
                    'bad_pattern': '金多水浊无木'
                },
                '冬季': {
                    'yongshen': '火',
                    'theory': '冬月水寒，火暖局为用',
                    'must_have': '火',
                    'better_have': '土',
                    'avoid': '金（助水）、水（太寒）',
                    'bad_pattern': '水多无火土'
                }
            }
        }
    
    def calculate_bazi(self, birth_dt: datetime, wannianli_data: dict, longitude: float,
                      latitude: float) -> Dict:
        """计算生辰八字
        
        Args:
            birth_dt: 出生日期时间
            wannianli_data: 万年历数据
            longitude: 经度
            latitude: 纬度
            
        Returns:
            八字计算结果字典
        """
        logger.info(f"计算生辰八字: {birth_dt}")
        
        # 1. 计算真太阳时
        true_solar_time = self._calculate_true_solar_time(birth_dt, longitude)
        
        if wannianli_data:
            # 使用万年历数据
            year_gz = wannianli_data['year_ganzhi']
            month_gz = wannianli_data['month_ganzhi']
            day_gz = wannianli_data['day_ganzhi']
            lunar_date = self._solar_to_lunar(birth_dt)
            logger.info(f"使用万年历数据计算八字: {year_gz} {month_gz} {day_gz}")
            
            # 解析农历日期
            lunar_date_str = wannianli_data.get('lunar_date', '')
            if lunar_date_str:
                try:
                    lunar_year, lunar_month, lunar_day = self._parse_lunar_date(lunar_date_str)
                except (ValueError, IndexError) as e:
                    logger.warning(f"解析农历日期失败: {lunar_date_str}, {e}")
                    raise ValueError("万年历数据格式错误，无法解析农历日期:" + lunar_date_str)
            else:
                raise ValueError("万年历数据缺少农历日期:" + birth_dt.strftime("%Y-%m-%d"))
        else:
            # 降级：使用传统算法
            logger.warning("万年历数据不可用，使用传统算法")
            lunar_obj, lunar_year, lunar_month, lunar_day, is_leap = self._solar_to_lunar_full(birth_dt)
            year_gz = self._get_year_ganzhi_by_lichun(birth_dt, lunar_year)
            month_gz = self._get_month_ganzhi_by_jieqi(birth_dt, year_gz)
            day_gz = self._get_day_ganzhi(birth_dt)
            lunar_date = self._solar_to_lunar(birth_dt)
        
        # 5. 计算时柱
        hour_gz = self._get_hour_ganzhi(true_solar_time, day_gz)
        
        bazi_str = f"{year_gz} {month_gz} {day_gz} {hour_gz}"
        
        # 6. 五行统计
        wuxing_count = self._count_wuxing(bazi_str)
        
        # 7. 查询纳音
        nayin_str = self._get_nayin(year_gz, month_gz, day_gz, hour_gz)
        
        # 8. 计算五行强度和同类异类
        rizhu = day_gz[0]
        wuxing_strength = self._calculate_wuxing_strength(bazi_str)
        tongyi_list, tongyi_strength, yilei_list, yilei_strength = \
            self._calculate_tongyi_yilei(rizhu, wuxing_strength)
        
        # 计算总强度和百分比
        total_strength = tongyi_strength + yilei_strength
        tongyi_percent = (tongyi_strength / total_strength * 100) if total_strength > 0 else 0
        yilei_percent = (yilei_strength / total_strength * 100) if total_strength > 0 else 0
        
        # 9. 确定喜用神
        xiyong_result = self._determine_xiyongshen(rizhu, wuxing_count, lunar_month, bazi_str)
        if isinstance(xiyong_result, tuple) and len(xiyong_result) == 3:
            xiyong_shen, ji_shen, xiyong_desc = xiyong_result
        else:
            xiyong_shen, ji_shen = xiyong_result
            xiyong_desc = ""
        
        # 10. 四季用神参考
        solar_term = wannianli_data.get('solar_term', '') if wannianli_data else ''
        siji_yongshen = self._get_siji_yongshen(rizhu, birth_dt, solar_term)
        
        result = {
            'bazi_str': bazi_str,
            'wuxing': self._get_wuxing_str(bazi_str),
            'nayin': nayin_str,
            'geshu': wuxing_count,
            'wuxing_strength': wuxing_strength,
            'tongyi': {
                'elements': tongyi_list,
                'strength': tongyi_strength,
                'percent': tongyi_percent
            },
            'yilei': {
                'elements': yilei_list,
                'strength': yilei_strength,
                'percent': yilei_percent
            },
            'rizhu': rizhu,
            'siji': siji_yongshen,
            'xiyong_shen': xiyong_shen,
            'xiyong_desc': xiyong_desc,
            'ji_shen': ji_shen,
            'score': self._calculate_bazi_score(wuxing_count, xiyong_shen),
            'lunar_date': lunar_date
        }
        
        return result
    
    def _parse_lunar_date(self, lunar_date_str: str) -> Tuple[int, int, int]:
        """解析农历日期字符串"""
        lunar_date_parts = lunar_date_str.split('-')
        lunar_year = int(lunar_date_parts[0])
        lunar_month = int(lunar_date_parts[1])
        lunar_day = int(lunar_date_parts[2])
        return lunar_year, lunar_month, lunar_day
    
    def _solar_to_lunar(self, solar_dt: datetime) -> str:
        """阳历转农历（返回字符串）"""
        wannianli_data = self._get_ganzhi_from_wannianli(solar_dt)
        if wannianli_data and wannianli_data.get('lunar_show'):
            hour = solar_dt.hour
            shichen_names = ['子时', '丑时', '寅时', '卯时', '辰时', '巳时',
                           '午时', '未时', '申时', '酉时', '戌时', '亥时']
            shichen = shichen_names[(hour + 1) // 2 % 12]
            return f"{wannianli_data['lunar_show']} {shichen}"
        
        if not LUNAR_AVAILABLE:
            return "农历功能不可用（请安装lunarcalendar库）"
        
        try:
            solar = Solar(solar_dt.year, solar_dt.month, solar_dt.day)
            lunar = Converter.Solar2Lunar(solar)
            hour = solar_dt.hour
            shichen_names = ['子时', '丑时', '寅时', '卯时', '辰时', '巳时',
                           '午时', '未时', '申时', '酉时', '戌时', '亥时']
            shichen = shichen_names[(hour + 1) // 2 % 12]
            month_str = f"{lunar.month}月" if not lunar.isleap else f"闰{lunar.month}月"
            return f"{lunar.year}年{month_str}{lunar.day}日{shichen}"
        except Exception as e:
            logger.error(f"农历转换失败: {e}")
            return "农历转换失败"
    
    def _solar_to_lunar_full(self, solar_dt: datetime) -> Tuple:
        """阳历转农历（返回完整信息）"""
        if not LUNAR_AVAILABLE:
            return None, solar_dt.year, solar_dt.month, solar_dt.day, False
        
        try:
            solar = Solar(solar_dt.year, solar_dt.month, solar_dt.day)
            lunar = Converter.Solar2Lunar(solar)
            return lunar, lunar.year, lunar.month, lunar.day, lunar.isleap
        except Exception as e:
            logger.error(f"农历转换失败: {e}")
            return None, solar_dt.year, solar_dt.month, solar_dt.day, False
    
    def _calculate_true_solar_time(self, birth_dt: datetime, longitude: float) -> datetime:
        """计算真太阳时"""
        time_diff_minutes = (longitude - 120) * 4
        return birth_dt + timedelta(minutes=time_diff_minutes)
    
    def _get_ganzhi_from_wannianli(self, birth_dt: datetime) -> Dict:
        """从万年历数据库查询干支信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            date_str = birth_dt.strftime('%Y-%m-%d')
            cursor.execute('''
            SELECT year_ganzhi, month_ganzhi, day_ganzhi, solar_term, zodiac,
                   lunar_date, lunar_show, gregorian_festival, lunar_festival
            FROM wannianli
            WHERE gregorian_date = ?
            ''', (date_str,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'year_ganzhi': row[0],
                    'month_ganzhi': row[1],
                    'day_ganzhi': row[2],
                    'solar_term': row[3] or '',
                    'zodiac': row[4] or '',
                    'lunar_date': row[5] or '',
                    'lunar_show': row[6] or '',
                    'gregorian_festival': row[7] or '',
                    'lunar_festival': row[8] or ''
                }
            else:
                logger.warning(f"万年历中未找到日期: {date_str}")
                return None
                
        except Exception as e:
            logger.error(f"查询万年历失败: {e}")
            return None
        finally:
            conn.close()
    
    def _get_year_ganzhi_by_lichun(self, birth_dt: datetime, lunar_year: int) -> str:
        """根据立春节气获取年柱干支"""
        wannianli_data = self._get_ganzhi_from_wannianli(birth_dt)
        if wannianli_data:
            return wannianli_data['year_ganzhi']
        
        logger.warning("万年历查询失败，使用简化算法计算年柱")
        year = birth_dt.year
        month = birth_dt.month
        day = birth_dt.day
        
        if month == 1 or (month == 2 and day < 4):
            year = year - 1
        
        tian_idx = (year - 4) % 10
        di_idx = (year - 4) % 12
        return self.TIANGAN[tian_idx] + self.DIZHI[di_idx]
    
    def _get_month_ganzhi_by_jieqi(self, birth_dt: datetime, year_gz: str) -> str:
        """根据节气获取月柱干支"""
        wannianli_data = self._get_ganzhi_from_wannianli(birth_dt)
        if wannianli_data:
            return wannianli_data['month_ganzhi']
        
        logger.warning("万年历查询失败，使用简化算法计算月柱")
        month = birth_dt.month
        day = birth_dt.day
        
        # 简化的节气判断
        if (month == 2 and day >= 4) or (month == 3 and day < 6):
            jieqi_month = 1
        elif (month == 3 and day >= 6) or (month == 4 and day < 5):
            jieqi_month = 2
        elif (month == 4 and day >= 5) or (month == 5 and day < 6):
            jieqi_month = 3
        elif (month == 5 and day >= 6) or (month == 6 and day < 6):
            jieqi_month = 4
        elif (month == 6 and day >= 6) or (month == 7 and day < 8):
            jieqi_month = 5
        elif (month == 7 and day >= 8) or (month == 8 and day < 8):
            jieqi_month = 6
        elif (month == 8 and day >= 8) or (month == 9 and day < 8):
            jieqi_month = 7
        elif (month == 9 and day >= 8) or (month == 10 and day < 9):
            jieqi_month = 8
        elif (month == 10 and day >= 9) or (month == 11 and day < 8):
            jieqi_month = 9
        elif (month == 11 and day >= 8) or (month == 12 and day < 7):
            jieqi_month = 10
        elif (month == 12 and day >= 7) or (month == 1 and day < 6):
            jieqi_month = 11
        else:
            jieqi_month = 12
        
        dizhi_map = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1]
        dizhi_idx = dizhi_map[jieqi_month - 1]
        
        year_tian = year_gz[0]
        year_tian_idx = self.TIANGAN.index(year_tian)
        
        month_tiangan_start = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]
        zheng_yue_tiangan = month_tiangan_start[year_tian_idx]
        
        tiangan_idx = (zheng_yue_tiangan + jieqi_month - 1) % 10
        
        return self.TIANGAN[tiangan_idx] + self.DIZHI[dizhi_idx]
    
    def _get_day_ganzhi(self, birth_dt: datetime) -> str:
        """获取日柱干支"""
        wannianli_data = self._get_ganzhi_from_wannianli(birth_dt)
        if wannianli_data:
            return wannianli_data['day_ganzhi']
        
        logger.warning("万年历查询失败，使用简化算法计算日柱")
        base_date = datetime(2000, 1, 1)
        days = (birth_dt - base_date).days
        gz_idx = days % 60
        return self.TIANGAN[gz_idx % 10] + self.DIZHI[gz_idx % 12]
    
    def _get_hour_ganzhi(self, true_time: datetime, day_gz: str) -> str:
        """获取时柱干支"""
        hour = true_time.hour
        shichen_idx = (hour + 1) // 2 % 12
        
        day_tian = day_gz[0]
        day_tian_idx = self.TIANGAN.index(day_tian)
        
        hour_tian_idx = (day_tian_idx * 2 + shichen_idx) % 10
        
        return self.TIANGAN[hour_tian_idx] + self.DIZHI[shichen_idx]
    
    def _count_wuxing(self, bazi_str: str) -> Dict[str, int]:
        """统计五行个数"""
        count = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
        
        for char in bazi_str:
            if char in self.TIANGAN_WUXING:
                wx = self.TIANGAN_WUXING[char]
                count[wx] += 1
            elif char in self.DIZHI_WUXING:
                wx = self.DIZHI_WUXING[char]
                count[wx] += 1
        
        return count
    
    def _get_wuxing_str(self, bazi_str: str) -> str:
        """获取五行字符串"""
        result = []
        for pair in bazi_str.split():
            if len(pair) == 2:
                tian_wx = self.TIANGAN_WUXING.get(pair[0], '?')
                di_wx = self.DIZHI_WUXING.get(pair[1], '?')
                result.append(f"{tian_wx}{di_wx}")
        return ' '.join(result)
    
    def _get_nayin(self, year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> str:
        """获取纳音"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            nayin_list = []
            for gz in [year_gz, month_gz, day_gz, hour_gz]:
                cursor.execute(
                    'SELECT nayin FROM wuxing_nayin WHERE ganzhi = ?',
                    (gz,)
                )
                row = cursor.fetchone()
                if row:
                    nayin_list.append(row[0])
                else:
                    logger.warning(f"未找到干支 '{gz}' 的纳音，使用未知")
                    nayin_list.append('未知')
            
            return ' '.join(nayin_list)
            
        except Exception as e:
            logger.error(f"查询纳音失败: {e}")
            return "纳音查询失败"
        finally:
            conn.close()
    
    def _calculate_wuxing_strength(self, bazi_str: str) -> Dict[str, int]:
        """计算五行强度"""
        strength = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        
        bazi_parts = bazi_str.split()
        if len(bazi_parts) != 4:
            logger.warning(f"八字格式错误: {bazi_str}")
            return strength
        
        month_dizhi = bazi_parts[1][1]
        month_idx = self.DIZHI_INDEX.get(month_dizhi, 0)
        
        try:
            for i, pillar in enumerate(bazi_parts):
                if len(pillar) != 2:
                    continue
                
                tiangan = pillar[0]
                dizhi = pillar[1]
                
                # 计算天干强度
                if tiangan in self.TIANGAN_INDEX:
                    tg_idx = self.TIANGAN_INDEX[tiangan]
                    tg_strength = self.TIANGAN_STRENGTH[month_idx][tg_idx]
                    tg_wuxing = self.TIANGAN_WUXING[tiangan]
                    strength[tg_wuxing] += tg_strength
                    logger.debug(f"{tiangan}({tg_wuxing}): +{tg_strength}")
                
                # 计算地支藏干强度
                if dizhi in self.DIZHI_INDEX:
                    dz_idx = self.DIZHI_INDEX[dizhi]
                    canggan_dict = self.DIZHI_CANGGAN[dz_idx]
                    
                    for canggan_tg, strength_list in canggan_dict.items():
                        cg_strength = strength_list[month_idx]
                        cg_wuxing = self.TIANGAN_WUXING[canggan_tg]
                        strength[cg_wuxing] += cg_strength
                        logger.debug(f"{dizhi}藏{canggan_tg}({cg_wuxing}): +{cg_strength}")
            
            logger.info(f"五行强度: {strength}")
            
        except Exception as e:
            logger.error(f"计算五行强度失败: {e}")
        
        return strength
    
    def _calculate_tongyi_yilei(self, rizhu: str, strength: Dict[str, int]) -> Tuple[List[str], int, List[str], int]:
        """计算同类和异类"""
        rizhu_wx = self.TIANGAN_WUXING[rizhu]
        
        # 找到生日主的五行
        sheng_rizhu_wx = None
        for wx, sheng_wx in self.WUXING_SHENG.items():
            if sheng_wx == rizhu_wx:
                sheng_rizhu_wx = wx
                break
        
        # 同类
        tongyi = [rizhu_wx]
        tongyi_strength = strength[rizhu_wx]
        
        if sheng_rizhu_wx:
            tongyi.append(sheng_rizhu_wx)
            tongyi_strength += strength[sheng_rizhu_wx]
        
        # 异类
        yilei = []
        yilei_strength = 0
        for wx in self.WUXING_SHENG_SEQUENCE:
            if wx not in tongyi:
                yilei.append(wx)
                yilei_strength += strength[wx]
        
        logger.info(f"同类: {tongyi} 强度: {tongyi_strength}")
        logger.info(f"异类: {yilei} 强度: {yilei_strength}")
        
        return tongyi, tongyi_strength, yilei, yilei_strength
    
    def _determine_xiyongshen(self, rizhu: str, wuxing_count: Dict, month: int, 
                             bazi_str: str = None, threshold: float = 0.55) -> Tuple[List, List]:
        """确定喜用神和忌神（高级版：含调候、优先级、十神标签）
        
        Args:
            rizhu: 日主天干
            wuxing_count: 五行个数统计（用于降级判断）
            month: 月份（保留兼容性）
            bazi_str: 八字字符串
            threshold: 判断身强的阈值，默认55%（>55%为身强）
            
        Returns:
            (喜用神列表, 忌神列表)
        """
        rizhu_wx = self.TIANGAN_WUXING.get(rizhu, '土')
        
        if bazi_str:
            try:
                # 计算五行强度
                strength = self._calculate_wuxing_strength(bazi_str)
                tongyi_list, tongyi_strength, yilei_list, yilei_strength = \
                    self._calculate_tongyi_yilei(rizhu, strength)
                
                # 计算同类比例
                total_strength = tongyi_strength + yilei_strength
                if total_strength == 0:
                    raise ValueError("五行强度总和，数据异常")
                
                tongyi_ratio = tongyi_strength / total_strength
                
                # 判断日主强弱
                if tongyi_ratio >= threshold:
                    strength_status = 'strong'  # 身强
                elif tongyi_ratio <= (1 - threshold):
                    strength_status = 'weak'    # 身弱
                else:
                    strength_status = 'balanced'  # 中和
                
                # === 五行生克关系表（十神体系）===
                wuxing_relations = {
                    '木': {'sheng_wo': '水', 'wo_sheng': '火', 'ke_wo': '金', 'wo_ke': '土'},
                    '火': {'sheng_wo': '木', 'wo_sheng': '土', 'ke_wo': '水', 'wo_ke': '金'},
                    '土': {'sheng_wo': '火', 'wo_sheng': '金', 'ke_wo': '木', 'wo_ke': '水'},
                    '金': {'sheng_wo': '土', 'wo_sheng': '水', 'ke_wo': '火', 'wo_ke': '木'},
                    '水': {'sheng_wo': '金', 'wo_sheng': '木', 'ke_wo': '土', 'wo_ke': '火'},
                }
                rel = wuxing_relations[rizhu_wx]
                
                # 十神名称映射
                shishen_names = {
                    rel['sheng_wo']: "印星",
                    rizhu_wx: "比劫",
                    rel['ke_wo']: "官杀",
                    rel['wo_ke']: "财星",
                    rel['wo_sheng']: "食伤"
                }
                
                # === 基础喜忌判断 ===
                base_xiyong = []
                base_jishen = []
                
                if strength_status == 'strong':
                    # 身强：喜克泄耗（官杀、食伤、财）
                    base_xiyong = [rel['ke_wo'], rel['wo_sheng'], rel['wo_ke']]
                    base_jishen = [rel['sheng_wo'], rizhu_wx]
                elif strength_status == 'weak':
                    # 身弱：喜生扶（印、比劫）
                    base_xiyong = [rel['sheng_wo'], rizhu_wx]
                    base_jishen = [rel['ke_wo'], rel['wo_sheng'], rel['wo_ke']]
                else:  # balanced
                    base_xiyong = []
                    base_jishen = []
                
                # === 调候用神（穷通宝鉴精简版）===
                # 提取月支
                month_zhi = bazi_str.split()[1][1] if len(bazi_str.split()) >= 2 else None
                tiaohou_wu = self._get_tiaohou_yongshen(rizhu, month_zhi)
                
                # === 按强度和角色分级 ===
                def get_wu_status(wu):
                    """判断五行强度状态"""
                    s = strength.get(wu, 0)
                    if s < 100:
                        return "极弱"
                    elif s < 500:
                        return "弱"
                    elif s < 1500:
                        return "中"
                    else:
                        return "旺"
                
                # 构建用神体系（用神、喜神、闲神）
                yongshen = []   # 核心用神（急需且力量不足）
                xishen = []     # 喜神（有益但非急需）
                jishen = []     # 忌神
                
                for wu in self.WUXING_SHENG_SEQUENCE:
                    wu_strength_status = get_wu_status(wu)
                    shishen_label = shishen_names.get(wu, "闲神")
                    
                    if wu in base_xiyong:
                        # 喜用五行：根据强度决定是用神还是喜神
                        if wu_strength_status in ["极弱", "弱"]:
                            # 缺而急需 → 用神
                            label = f"{wu}({shishen_label})"
                            # 调候用神优先
                            if wu == tiaohou_wu:
                                yongshen.insert(0, label)  # 调候用神置顶
                            else:
                                yongshen.append(label)
                        elif wu_strength_status == "中":
                            # 适中 → 喜神
                            xishen.append(f"{wu}({shishen_label})")
                        # 旺的情况不列入（已经够旺了）
                    elif wu in base_jishen:
                        jishen.append(f"{wu}({shishen_label})")
                
                # 合并用神和喜神为喜用神列表
                xiyong_labels = yongshen + xishen
                
                # === 生成专业描述 ===
                formatted_desc = ""
                if strength_status == 'strong':
                    theory = "身强喜克泄耗"
                    if yongshen:
                        desc = f"用神为{'/'.join(yongshen)}"
                    else:
                        desc = "五行流通为宜"
                    if xishen:
                        desc += f"，喜神为{'/'.join(xishen)}"
                    if tiaohou_wu:
                        tiaohou_label = f"{tiaohou_wu}({shishen_names.get(tiaohou_wu, '调候')})"
                        desc += f"；调候用神为{tiaohou_label}"
                    
                    logger.info(f"日主{rizhu}({rizhu_wx})身强 同类:{tongyi_ratio:.1%} {theory} | {desc}")
                    formatted_desc = f"日主{rizhu}({rizhu_wx})身强 同类:{tongyi_ratio:.1%} {theory} | {desc}"
                    
                elif strength_status == 'weak':
                    theory = "身弱喜生扶"
                    if yongshen:
                        desc = f"用神为{'/'.join(yongshen)}"
                    else:
                        desc = "宜扶助日主"
                    if xishen:
                        desc += f"，喜神为{'/'.join(xishen)}"
                    if tiaohou_wu:
                        tiaohou_label = f"{tiaohou_wu}({shishen_names.get(tiaohou_wu, '调候')})"
                        desc += f"；调候用神为{tiaohou_label}"
                    
                    logger.info(f"日主{rizhu}({rizhu_wx})身弱 同类:{tongyi_ratio:.1%} {theory} | {desc}")
                    formatted_desc = f"日主{rizhu}({rizhu_wx})身弱 同类:{tongyi_ratio:.1%} {theory} | {desc}"
                    
                else:  # balanced
                    logger.info(f"日主{rizhu}({rizhu_wx})中和 同类:{tongyi_ratio:.1%} 五行平衡，顺其自然")
                    formatted_desc = f"日主{rizhu}({rizhu_wx})中和 同类:{tongyi_ratio:.1%} 五行平衡，顺其自然"
                    if tiaohou_wu:
                        tiaohou_label = f"{tiaohou_wu}({shishen_names.get(tiaohou_wu, '调候')})"
                        xiyong_labels = [tiaohou_label]  # 中和八字，调候为主
                
                # 提取纯五行列表（去除标签）
                xiyong_pure = [label.split('(')[0] for label in xiyong_labels]
                jishen_pure = [label.split('(')[0] for label in jishen]
                
                # 去重
                xiyong_pure = list(dict.fromkeys(xiyong_pure))
                jishen_pure = list(dict.fromkeys(jishen_pure))
                
                return xiyong_pure, jishen_pure, formatted_desc
                
            except Exception as e:
                logger.warning(f"高级喜用神计算失败，使用简化方法: {e}")
        
        # 降级到简化判断（基于五行个数）
        xiyong = []
        ji = []
        
        for wx, count in wuxing_count.items():
            if count == 0:
                xiyong.append(wx)
            elif count >= 3:
                ji.append(wx)
        
        if not xiyong:
            xiyong = [self.WUXING_SHENG.get(rizhu_wx, '土')]
        
        logger.info(f"使用简化方法: 喜用神={xiyong}, 忌神={ji}")
        
        return xiyong, ji
    
    def _get_tiaohou_yongshen(self, rizhu: str, month_zhi: str) -> str:
        """获取调候用神（基于穷通宝鉴）
        
        调候：调和气候，冬月用火暖，夏月用水润
        
        Args:
            rizhu: 日主天干
            month_zhi: 月支地支
            
        Returns:
            调候用神五行，如 '火'、'水' 等，无则返回 None
        """
        # 穷通宝鉴调候表（精简版，仅冬夏关键月）
        tiaohou_table = {
            # 冬月（水冷，需火暖）
            '子': {'甲': '丙', '乙': '丙', '丙': '壬', '丁': '甲', '戊': '丙', 
                   '己': '丙', '庚': '丁', '辛': '丁', '壬': '丙', '癸': '丙'},
            '丑': {'甲': '丙', '乙': '丙', '丙': '壬', '丁': '甲', '戊': '丙', 
                   '己': '丙', '庚': '丁', '辛': '丁', '壬': '丙', '癸': '丙'},
            '亥': {'甲': '庚', '乙': '丙', '丙': '壬', '丁': '甲', '戊': '丙', 
                   '己': '丙', '庚': '丁', '辛': '丁', '壬': '丙', '癸': '丙'},
            # 夏月（火炎，需水济）
            '午': {'甲': '壬', '乙': '癸', '丙': '壬', '丁': '壬', '戊': '壬', 
                   '己': '癸', '庚': '壬', '辛': '壬', '壬': '辛', '癸': '辛'},
            '巳': {'甲': '庚', '乙': '癸', '丙': '壬', '丁': '壬', '戊': '甲', 
                   '己': '甲', '庚': '壬', '辛': '壬', '壬': '辛', '癸': '辛'},
            '未': {'甲': '癸', '乙': '癸', '丙': '壬', '丁': '壬', '戊': '甲', 
                   '己': '甲', '庚': '壬', '辛': '壬', '壬': '辛', '癸': '辛'},
        }
        
        if not month_zhi or month_zhi not in tiaohou_table:
            return None
        
        if rizhu not in tiaohou_table[month_zhi]:
            return None
        
        tiaohou_tiangan = tiaohou_table[month_zhi][rizhu]
        tiaohou_wuxing = self.TIANGAN_WUXING.get(tiaohou_tiangan)
        
        return tiaohou_wuxing
    
    def _get_siji_yongshen(self, rizhu: str, birth_dt: datetime, solar_term: str = '') -> str:
        """获取四季用神参考（返回详细描述）
        
        Args:
            rizhu: 日主天干
            birth_dt: 出生日期时间
            solar_term: 节气名称（可选）
            
        Returns:
            格式化的四季用神描述，如：
            "日主天干金生于冬季,必须有火、土相助，忌无火、土反而有金、水，忌木多而无火。"
        """
        rizhu_wx = self.TIANGAN_WUXING.get(rizhu, '土')
        
        spring_terms = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨']
        summer_terms = ['立夏', '小满', '芒种', '夏至', '小暑', '大暑']
        autumn_terms = ['立秋', '处暑', '白露', '秋分', '寒露', '霜降']
        winter_terms = ['立冬', '小雪', '大雪', '冬至', '小寒', '大寒']
        
        # 判断季节
        if solar_term:
            if solar_term in spring_terms:
                season = "春季"
            elif solar_term in summer_terms:
                season = "夏季"
            elif solar_term in autumn_terms:
                season = "秋季"
            elif solar_term in winter_terms:
                season = "冬季"
            else:
                season = self._get_season_by_month(birth_dt.month)
        else:
            season = self._get_season_by_solar_term_query(birth_dt)
        
        # 从速查表获取详细信息
        if rizhu_wx in self.SIJI_YONGSHEN_TABLE and season in self.SIJI_YONGSHEN_TABLE[rizhu_wx]:
            siji_info = self.SIJI_YONGSHEN_TABLE[rizhu_wx][season]
            
            # 构建描述
            desc_parts = [f"日主天干{rizhu_wx}生于{season}"]
            
            # 必须有
            if siji_info['must_have']:
                desc_parts.append(f"必须有{siji_info['must_have']}相助")
            
            # 更好有
            if siji_info['better_have']:
                desc_parts.append(f"{siji_info['better_have']}为佳")
            
            # 忌讳
            if siji_info['avoid']:
                desc_parts.append(f"忌{siji_info['avoid']}")
            
            # 不良格局
            if siji_info['bad_pattern']:
                desc_parts.append(f"忌{siji_info['bad_pattern']}")
            
            return "，".join(desc_parts) + "。"
        
        # 降级：返回简单描述
        return f"日主天干{rizhu_wx}生于{season}"
    
    def _get_season_by_month(self, month: int) -> str:
        """根据月份判断季节"""
        if 2 <= month <= 4:
            return "春季"
        elif 5 <= month <= 7:
            return "夏季"
        elif 8 <= month <= 10:
            return "秋季"
        else:
            return "冬季"
    
    def _get_season_by_solar_term_query(self, birth_dt: datetime) -> str:
        """查询数据库获取节气判断季节"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            date_str = birth_dt.strftime('%Y-%m-%d')
            
            cursor.execute('''
            SELECT solar_term FROM wannianli
            WHERE gregorian_date <= ? AND solar_term IS NOT NULL AND solar_term != ''
            ORDER BY gregorian_date DESC
            LIMIT 1
            ''', (date_str,))
            
            row = cursor.fetchone()
            
            if row and row[0]:
                solar_term = row[0]
                
                spring_terms = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨']
                summer_terms = ['立夏', '小满', '芒种', '夏至', '小暑', '大暑']
                autumn_terms = ['立秋', '处暑', '白露', '秋分', '寒露', '霜降']
                winter_terms = ['立冬', '小雪', '大雪', '冬至', '小寒', '大寒']
                
                if solar_term in spring_terms:
                    return "春季"
                elif solar_term in summer_terms:
                    return "夏季"
                elif solar_term in autumn_terms:
                    return "秋季"
                elif solar_term in winter_terms:
                    return "冬季"
            
            logger.warning(f"未找到节气信息，使用月份判断季节")
            return self._get_season_by_month(birth_dt.month)
            
        except Exception as e:
            logger.error(f"查询节气失败: {e}")
            return self._get_season_by_month(birth_dt.month)
        finally:
            conn.close()
    
    def _calculate_bazi_score(self, wuxing_count: Dict, xiyong_shen: List) -> int:
        """计算八字评分"""
        score = 50
        
        max_count = max(wuxing_count.values())
        min_count = min(wuxing_count.values())
        if max_count - min_count <= 2:
            score += 30
        elif max_count - min_count <= 4:
            score += 20
        else:
            score += 10
        
        score += len(xiyong_shen) * 5
        
        return min(100, score)
