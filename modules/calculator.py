# -*- coding: utf-8 -*-
"""
计算模块 - 核心计算引擎，执行各项命理学计算
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

try:
    from lunarcalendar import Converter, Solar, Lunar
    LUNAR_AVAILABLE = True
except ImportError:
    LUNAR_AVAILABLE = False
    logger.warning("lunarcalendar库未安装，农历功能不可用")


class Calculator:
    """计算引擎类"""
    
    def __init__(self, db_path: str = 'local.db'):
        """初始化计算模块"""
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
        
        # 五行颜色
        self.WUXING_COLOR = {
            '木': '绿色、青色、翠色',
            '火': '红色、紫色、粉色',
            '土': '黄色、棕色、咖啡色',
            '金': '白色、金色、银色',
            '水': '黑色、蓝色、灰色'
        }
        
        # 生肖
        self.SHENGXIAO = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        
        # 天干索引
        self.TIANGAN_INDEX = {tg: i for i, tg in enumerate(self.TIANGAN)}
        # 地支索引
        self.DIZHI_INDEX = {dz: i for i, dz in enumerate(self.DIZHI)}
        
        '''
        旺: 1.2 (1200)
        相: 1.0 (1000)
        休: 0.8 (800)
        囚: 0.7 (700)
        死: 0.6 (600)
        '''
        # 天干强度表 (12个月x10个天干)
        # 每行代表一个地支月份（子丑寅卯辰巳午未申酉戌亥）
        # 每列代表一个天干（甲乙丙丁戊己庚辛壬癸）
        # https://github.com/allanpk716/BaziEval
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
        # 每个地支包含的天干及其强度（按12个月变化）
        self.DIZHI_CANGGAN = [
            # 子 - 癸
            {'癸': [1200, 1100, 1000, 1000, 1040, 1060, 1000, 1000, 1200, 1200, 1060, 1140]},
            # 丑 - 癸辛己
            {'癸': [360, 330, 300, 300, 312, 318, 300, 300, 360, 360, 318, 342],
             '辛': [200, 228, 200, 200, 230, 212, 200, 220, 228, 248, 232, 200],
             '己': [500, 550, 530, 500, 550, 570, 600, 580, 500, 500, 570, 500]},
            # 寅 - 丙甲戊（原文写的是丙甲，但标准应该是甲丙戊）
            {'丙': [300, 300, 360, 360, 318, 342, 360, 330, 300, 300, 342, 318],
             '甲': [840, 742, 798, 840, 770, 700, 700, 728, 742, 700, 700, 840]},
            # 卯 - 乙
            {'乙': [1200, 1060, 1140, 1200, 1100, 1000, 1000, 1040, 1060, 1000, 1000, 1200]},
            # 辰 - 乙癸戊
            {'乙': [360, 318, 342, 360, 330, 300, 300, 312, 318, 300, 300, 360],
             '癸': [240, 220, 200, 200, 208, 200, 200, 200, 240, 240, 212, 228],
             '戊': [500, 550, 530, 500, 550, 600, 600, 580, 500, 500, 570, 500]},
            # 巳 - 庚丙戊
            {'庚': [300, 342, 300, 300, 330, 300, 300, 330, 342, 360, 348, 300],
             '丙': [700, 700, 840, 840, 742, 840, 840, 798, 700, 700, 728, 742]},
            # 午 - 丁己
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
        
        # 五行生序（用于判断同类异类）
        self.WUXING_SHENG_SEQUENCE = ['木', '火', '土', '金', '水']
    
    def calculate_name(self, surname: str, given_name: str, gender: str, birth_time: str,
                      longitude: float, latitude: float) -> Dict:
        """
        执行完整的姓名测试计算
        
        :param surname: 姓氏
        :param given_name: 名字
        :param gender: 性别
        :param birth_time: 出生时间 (YYYY-MM-DD HH:MM)
        :param longitude: 经度
        :param latitude: 纬度
        :return: 计算结果字典
        """
        try:
            full_name = surname + given_name
            logger.info(f"开始计算: {surname}(姓) {given_name}(名), {gender}, {birth_time}")
            
            # 解析出生时间
            birth_dt = datetime.strptime(birth_time, '%Y-%m-%d %H:%M')

            # 2. 优先从万年历获取完整信息
            wannianli_data = self._get_ganzhi_from_wannianli(birth_dt)            
            # 1. 数据验证
            self._validate_input(full_name, gender, birth_dt, longitude, latitude)
            
            # 2. 三才五格计算
            wuge_result = self.calculate_wuge(surname, given_name)
            
            # 3. 生辰八字计算
            bazi_result = self.calculate_bazi(birth_dt, wannianli_data, longitude, latitude)
            
            # 4. 字义音形分析
            ziyi_result = self.analyze_ziyi(full_name)
            
            # 5. 生肖喜忌分析
            shengxiao_result = self.analyze_shengxiao(full_name, birth_dt)
            
            # 6. 称骨算命计算
            chenggu_result = self.calculate_chenggu(birth_dt)
            
            # 7. 综合评分
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
        """验证输入数据"""
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
    
    def calculate_wuge(self, surname: str, given_name: str) -> Dict:
        """计算三才五格"""
        full_name = surname + given_name
        logger.info(f"计算三才五格: {surname}(姓) + {given_name}(名) = {full_name}")
        
        # 获取姓氏和名字的笔画数
        surname_strokes = self._get_strokes(surname)
        given_strokes = self._get_strokes(given_name)
        
        # 判断姓氏类型和名字类型
        is_compound_surname = len(surname) == 2  # 复姓
        is_double_given = len(given_name) == 2    # 双名
        
        if len(surname) == 1 and len(given_name) == 1:
            # 单姓单名
            surname_stroke = surname_strokes[0]
            given_stroke = given_strokes[0]
            
            tiange = surname_stroke + 1
            renge = surname_stroke + given_stroke
            dige = given_stroke + 1  # 单名：名字笔画数 + 1
            waige = 2  # 单姓单名：固定为2（即1+1）
            zongge = surname_stroke + given_stroke
            
        elif len(surname) == 1 and len(given_name) == 2:
            # 单姓双名
            surname_stroke = surname_strokes[0]
            given1_stroke = given_strokes[0]
            given2_stroke = given_strokes[1]
            
            tiange = surname_stroke + 1
            renge = surname_stroke + given1_stroke
            dige = given1_stroke + given2_stroke  # 复名：所有名字字笔画之和（不加1）
            waige = given2_stroke + 1  # 单姓双名：名字最后一字笔画 + 1
            zongge = surname_stroke + given1_stroke + given2_stroke
            
        elif len(surname) == 2 and len(given_name) == 1:
            # 复姓单名
            surname1_stroke = surname_strokes[0]
            surname2_stroke = surname_strokes[1]
            given_stroke = given_strokes[0]
            
            tiange = surname1_stroke + surname2_stroke  # 两字姓氏笔画之和
            renge = surname2_stroke + given_stroke
            dige = given_stroke + 1  # 单名：笔画数 + 1
            waige = surname1_stroke + 1  # 复姓单名：姓氏第一个字笔画 + 1
            zongge = surname1_stroke + surname2_stroke + given_stroke
            
        elif len(surname) == 2 and len(given_name) == 2:
            # 复姓双名
            surname1_stroke = surname_strokes[0]
            surname2_stroke = surname_strokes[1]
            given1_stroke = given_strokes[0]
            given2_stroke = given_strokes[1]
            
            tiange = surname1_stroke + surname2_stroke
            renge = surname2_stroke + given1_stroke
            dige = given1_stroke + given2_stroke  # 复名：所有名字字笔画之和（不加1）
            waige = surname1_stroke + given2_stroke  # 复姓双名：姓氏第一个字笔画 + 名字最后一个字笔画
            zongge = surname1_stroke + surname2_stroke + given1_stroke + given2_stroke
        
        else:
            raise ValueError(f"不支持的姓名格式: 姓氏{len(surname)}字 + 名字{len(given_name)}字")
        
        # 判断五行和吉凶
        result = {
            'tiange': self._analyze_ge(tiange, '天格'),
            'renge': self._analyze_ge(renge, '人格'),
            'dige': self._analyze_ge(dige, '地格'),
            'waige': self._analyze_ge(waige, '外格'),
            'zongge': self._analyze_ge(zongge, '总格'),
            'sancai': '',
            'score': 0
        }
        
        # 三才配置
        tian_wx = result['tiange']['element']
        ren_wx = result['renge']['element']
        di_wx = result['dige']['element']
        result['sancai'] = f"{tian_wx}{ren_wx}{di_wx}"
        
        # 三才配置吉凶表 (格式: "天格-人格-地格")
        sancai_luck_map = {
            # 大吉配置
            "木木木": "大吉", "木木火": "大吉", "木木土": "大吉", "木火木": "大吉",
            "木火火": "大吉", "木火土": "大吉", "木土火": "大吉", "木土土": "大吉",
            "火木木": "大吉", "火木火": "大吉", "火木土": "大吉", "火火木": "大吉",
            "火火土": "大吉", "火土土": "大吉", "土火火": "大吉", "土火土": "大吉",
            "土土火": "大吉", "土土土": "大吉", "土金土": "大吉", "金土土": "大吉",
            
            # 吉配置
            "木木金": "吉", "木木水": "吉", "木火金": "吉", "木土金": "吉",
            "火火火": "吉", "火土金": "吉", "土土金": "吉", "土金金": "吉",
            "金土金": "吉", "金金土": "吉",
            
            # 凶配置
            "木金木": "凶", "木金金": "凶", "木金土": "凶", "木水木": "凶",
            "木水土": "凶", "火金木": "凶", "火金火": "凶", "火金土": "凶",
            "火水木": "凶", "火水土": "凶", "土木木": "凶", "土木火": "凶",
            "土木土": "凶", "土金木": "凶", "土水木": "凶", "土水土": "凶",
            "金木木": "凶", "金木火": "凶", "金木土": "凶", "金火木": "凶",
            "金火火": "凶", "金火土": "凶", "金土木": "凶", "金土水": "凶",
            "金金木": "凶", "金金火": "凶", "金金金": "凶", "金水木": "凶",
            "金水火": "凶", "金水土": "凶", "水木木": "凶", "水木火": "凶",
            "水木土": "凶", "水火木": "凶", "水火火": "凶", "水火土": "凶",
            "水土木": "凶", "水土火": "凶", "水土土": "凶", "水金木": "凶",
            "水金火": "凶", "水金土": "凶", "水水木": "凶", "水水火": "凶",
            "水水土": "凶",
        }
        sancai_config = result['sancai']
        # 查找吉凶
        if sancai_config in sancai_luck_map:
            result['sancai'] = f"{sancai_config} - {sancai_luck_map[sancai_config]}"
        else:
            judge_str = self._judge_by_wuxing(tian_wx, ren_wx, di_wx)
            result['sancai'] = f"{sancai_config} - {judge_str}"
                
        # 计算五格评分
        result['score'] = self._calculate_wuge_score(result)
        
        return result
    
    def _judge_by_wuxing(self, tian, ren, di):
        """根据五行生克关系判断吉凶"""
        # 天格与人格的关系
        tian_ren_relation = self._get_relation(tian, ren)
        
        # 人格与地格的关系
        ren_di_relation = self._get_relation(ren, di)
        
        # 判断吉凶
        if tian_ren_relation == "生" and ren_di_relation == "生":
            return "大吉"
        elif tian_ren_relation == "克" and ren_di_relation == "克":
            return "凶"
        elif tian_ren_relation == "同" and ren_di_relation == "同":
            return "半吉"
        elif (tian_ren_relation == '生' and ren_di_relation in ('同', '平')) or \
            (tian_ren_relation in ('同', '平') and ren_di_relation == '生'):
            return  '半吉'
        else:
            return  '平'
    
    def _get_relation(self, wuxing1, wuxing2):
        """判断两个五行之间的关系"""
        if wuxing1 == wuxing2:
            return "同"  # 相同
        elif self.WUXING_SHENG.get(wuxing1) == wuxing2:
            return "生"  # wuxing1生wuxing2
        elif self.WUXING_KE.get(wuxing1) == wuxing2:
            return "克"  # wuxing1克wuxing2
        else:
            return "平"  # 无直接生克
        
    def _get_strokes(self, name: str) -> List[int]:
        """从数据库获取笔画数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        strokes = []
        try:
            for char in name:
                cursor.execute(
                    'SELECT strokes FROM kangxi_strokes WHERE character=?',
                    (char,)
                )
                row = cursor.fetchone()
                if row:
                    strokes.append(row[0])
                else:
                    # 如果查不到，使用默认值
                    logger.warning(f"未找到字 '{char}' 的笔画数，使用默认值10")
                    strokes.append(10)
        finally:
            conn.close()
        
        return strokes
    
    def _analyze_ge(self, number: int, ge_name: str) -> Dict:
        """分析格的五行和吉凶"""
        # 数理五行
        #wuxing = ['木', '木', '火', '火', '土', '土', '金', '金', '水', '水'][number % 10]
        wuxing = ['水', '木', '木', '火', '火', '土', '土', '金', '金', '水'][number % 10]
        
        # 简化的吉凶判断（实际应从数据库查询）
        '''
        jixiong_map = {
            1: '大吉', 3: '大吉', 5: '大吉', 6: '吉', 7: '吉', 8: '吉',
            11: '大吉', 13: '大吉', 15: '大吉', 16: '吉', 17: '吉', 18: '吉',
            21: '大吉', 23: '大吉', 24: '大吉', 25: '吉', 29: '吉', 31: '大吉',
            32: '吉', 33: '大吉', 35: '吉', 37: '吉', 38: '半吉', 39: '吉',
            41: '吉', 45: '吉', 47: '吉', 48: '吉', 52: '吉', 57: '吉', 61: '吉',
            63: '吉', 65: '吉', 67: '吉', 68: '吉', 81: '吉'
        }
        '''
        # 若干吉数待确认: 48, 57, 61, 68, 73, 75, 26, 30, 49
        jixiong_map = {
            # 大吉数 (1-81)
            1: {"吉凶": "大吉", "含义": "天地开泰，繁荣发达，根基稳固", "类别": "首领运"},
            3: {"吉凶": "大吉", "含义": "进取如意，阴阳合和，名利双收，名利荣达，首领之数，富贵荣华。"},
            5: {"吉凶": "大吉", "含义": "五行之数，循环相生，圆通畅达，福祉无穷，福禄长寿，荣显家门。"},
            6: {"吉凶": "吉", "含义": "六爻之数，发展变化，天赋美德，吉祥安泰，家门隆昌，福禄有余。"},
            7: {"吉凶": "吉", "含义": "刚毅果断，独立权威，天赋之力", "类别": "刚强运"},
            8: {"吉凶": "吉", "含义": "意志刚健，勤勉发展，贯彻志望", "类别": "坚刚运"},
            11: {"吉凶": "大吉", "含义": "草木逢春，稳健着实，富贵荣达", "类别": "稳健运"},
            13: {"吉凶": "大吉", "含义": "智略超群，奇略纵横，成就大业", "类别": "艺能运"},
            15: {"吉凶": "大吉", "含义": "福寿圆满，涵养雅量，德高望重", "类别": "财富运"},
            16: {"吉凶": "大吉", "含义": "贵人得助，能获众望，成就大业", "类别": "首领运"},
            21: {"吉凶": "大吉", "含义": "天官赐福，明月光照，独立权威", "类别": "首领运"},
            23: {"吉凶": "大吉", "含义": "旭日东升，名显四方，渐次进展", "类别": "首领运"},
            24: {"吉凶": "吉", "含义": "家门余庆，钱财丰盈，白手成家", "类别": "财富运"},
            31: {"吉凶": "大吉", "含义": "春日花开，智勇得志，博得名利", "类别": "首领运"},
            32: {"吉凶": "大吉", "含义": "宝马金鞍，侥幸多望，前途无限", "类别": "财富运"},
            33: {"吉凶": "大吉", "含义": "旭日升天，鸾凤相会，名闻天下", "类别": "财富运"},
            35: {"吉凶": "吉", "含义": "温和平静，理智兼具，文艺技术", "类别": "温和运"},
            37: {"吉凶": "大吉", "含义": "权威显达，猛虎出林，德望成功", "类别": "权威运"},
            39: {"吉凶": "吉", "含义": "富贵荣华，财帛丰盈，暗藏险象，德泽四方，繁荣富贵", "类别": "首领运"},
            41: {"吉凶": "大吉", "含义": "天赋吉运，德望兼备，前途无限", "类别": "首领运"},
            45: {"吉凶": "吉", "含义": "顺风扬帆，新生泰和，富贵繁荣", "类别": "温和运"},
            47: {"吉凶": "大吉", "含义": "花开之象，万事如意，祯祥吉庆", "类别": "首领运"},
            48: {"吉凶": "大吉", "含义": "智谋兼备，德量荣达，威望成师", "类别": "德智运"},
            52: {"吉凶": "大吉", "含义": "卓识达眼，先见之明，智谋超群", "类别": "智慧运"},
            57: {"吉凶": "吉", "含义": "日照春松，寒雪青松，夜莺吟春，必遭一过，繁荣百世，名利双收。", "类别": "刚强运"},
            61: {"吉凶": "大吉", "含义": "牡丹芙蓉，花开富贵，名利双收", "类别": "名利运"},
            63: {"吉凶": "大吉", "含义": "舟归平海，富甲天下，德高望重", "类别": "财富运"},
            65: {"吉凶": "大吉", "含义": "巨流归海，富贵长寿，平安自在", "类别": "寿运"},
            67: {"吉凶": "大吉", "含义": "顺风通达，天赋幸运，四通八达", "类别": "通达运"},
            68: {"吉凶": "大吉", "含义": "智虑周密，志向坚定，勤勉力行", "类别": "智慧运"},
            73: {"吉凶": "半吉", "含义": "盛衰交加，徒有高志，无贯彻之勇，终世平安，先苦后甜。", "类别": "奋斗运"},
            81: {"吉凶": "大吉", "含义": "最极之数，还本归元，繁荣富贵", "类别": "首领运"},
            
            # 吉数
            17: {"吉凶": "半吉", "含义": "排除万难，权威刚强，如能容忍，功成名就", "类别": "刚强运"},
            18: {"吉凶": "吉", "含义": "铁镜重磨，权威显达，博得名利，事业有成", "类别": "艺能运"},
            25: {"吉凶": "吉", "含义": "资性英敏，才能奇特，克服傲慢，尚可成功，自成大业", "类别": "温和运"},
            29: {"吉凶": "半吉", "含义": "智谋优秀，财力归集，克服欲望难足，成就大业,", "类别": "首领运"},
            38: {"吉凶": "半吉", "含义": "意志薄弱，刻意经营，才识不凡", "类别": "艺能运"},
            51: {"吉凶": "半吉", "含义": "盛衰交加，一盛一衰，最终失败", "类别": "盛衰运"},
            58: {"吉凶": "半吉", "含义": "晚行遇月，沉浮多端，先苦后甜，宽宏扬名，富贵繁荣，晚景幸福。", "类别": "晚运"},
            71: {"吉凶": "半吉", "含义": "石上金花，内心劳苦，晚年幸福", "类别": "劳苦运"},
            75: {"吉凶": "半吉", "含义": "虽有吉相，无奈难成，退守保吉，进取易失，发迹甚迟", "类别": "温和运"},
            77: {"吉凶": "半吉", "含义": "先苦后甜，有贵有甜，晚年幸福", "类别": "晚运"},
            78: {"吉凶": "半吉", "含义": "祸福参半，先天智能，中年发达，晚景困苦，晚运凄凉。", "类别": "晚运"},
            
            # 凶数
            2: {"吉凶": "凶", "含义": "根基不牢，混沌未定，辛苦重来", "类别": "破坏运"},
            4: {"吉凶": "凶", "含义": "坎坷苦难，身遭劫难，凶煞不祥", "类别": "凶变运"},
            9: {"吉凶": "凶", "含义": "舟破浪急，兴尽凶始，多遇困难", "类别": "破舟进海"},
            10: {"吉凶": "凶", "含义": "万事终局，暗藏险恶，损耗破灭", "类别": "零暗运"},
            12: {"吉凶": "凶", "含义": "意志薄弱，家庭缘薄，谋事难成", "类别": "不足运"},
            14: {"吉凶": "凶", "含义": "忍得苦难，时来运转，但多破兆", "类别": "破兆运"},
            19: {"吉凶": "凶", "含义": "风云蔽日，成功虽早，辛苦重来", "类别": "多难运"},
            20: {"吉凶": "凶", "含义": "非业破运，灾难重重，万事难成", "类别": "破运"},
            22: {"吉凶": "凶", "含义": "秋草逢霜，怀才不遇，事不如意", "类别": "逆境运"},
            26: {"吉凶": "凶带吉", "含义": "变怪之谜，英雄豪杰，波澜重叠", "类别": "变怪运"},
            27: {"吉凶": "凶", "含义": "欲望无止，自我心强，多受诽谤", "类别": "刚情运"},
            28: {"吉凶": "凶", "含义": "阔水浮萍，遭难之数，四海飘泊", "类别": "遭难运"},
            30: {"吉凶": "半凶半吉", "含义": "浮沉不定，凶吉难变，绝处逢生，大起大落", "类别": "浮沉运"},
            34: {"吉凶": "凶", "含义": "破家之数，才识不凡，苦难不绝", "类别": "破家运"},
            36: {"吉凶": "凶", "含义": "风浪不静，枉费心力，事难如愿", "类别": "波澜运"},
            40: {"吉凶": "凶", "含义": "谨慎保安，豪胆迈进，退保平安", "类别": "退安运"},
            42: {"吉凶": "凶", "含义": "博识多能，精通世情，乏于力行", "类别": "多能运"},
            43: {"吉凶": "凶", "含义": "散财破产，外祥内苦，邪途残废", "类别": "散财运"},
            44: {"吉凶": "凶", "含义": "愁眉难展，悉锁眉间，悲惨不测", "类别": "烦闷运"},
            46: {"吉凶": "凶", "含义": "罗网系身，离祖成家，困苦不安", "类别": "离祖运"},
            49: {"吉凶": "半吉半凶", "含义": "吉凶难分，不断辛苦，沉浮不定，知难而退，自获天佑。", "类别": "忧闷运"}, 
            50: {"吉凶": "凶", "含义": "一成一败，吉凶参半，先得庇荫", "类别": "吉凶运"},
            53: {"吉凶": "凶", "含义": "忧心劳神，内忧外患，前景暗淡", "类别": "内忧运"},
            54: {"吉凶": "凶", "含义": "石上栽花，难得活运，忧闷频来", "类别": "石上栽花"},
            55: {"吉凶": "凶", "含义": "善恶相伴，外美内苦，和顺不实数，辛苦重来，难望成功。", "类别": "外祥内苦"},
            56: {"吉凶": "凶", "含义": "浪里行舟，历尽艰辛，事与愿违", "类别": "浪里行舟"},
            59: {"吉凶": "凶", "含义": "寒蝉悲风，时运不济，缺乏忍耐", "类别": "寒蝉悲风"},
            60: {"吉凶": "凶", "含义": "无谋无勇，心迷意乱，动摇不安", "类别": "无谋运"},
            62: {"吉凶": "凶", "含义": "衰败之象，内外不合，志望难达", "类别": "衰败运"},
            64: {"吉凶": "凶", "含义": "骨肉分离，孤独悲愁，难得心安", "类别": "骨肉分离"},
            66: {"吉凶": "凶", "含义": "进退维谷，艰难不堪，等待时机", "类别": "进退运"},
            69: {"吉凶": "凶", "含义": "动摇不安，常陷逆境，不得时运", "类别": "不安运"},
            70: {"吉凶": "凶", "含义": "残菊逢霜，空虚寂寞，惨淡忧闷", "类别": "残菊逢霜"},
            72: {"吉凶": "凶", "含义": "荣苦相伴，阴云覆月，外表吉祥，内实凶祸，晚运凄凉。", "类别": "劳苦运"},
            74: {"吉凶": "凶", "含义": "残花经霜，智能无用，辛苦不休", "类别": "残花经霜"},
            76: {"吉凶": "凶", "含义": "离散之数，倾覆之险，劳而无功", "类别": "离散运"},
            79: {"吉凶": "凶", "含义": "云头望月，身疲力尽，前途无光", "类别": "不遇运"},
            80: {"吉凶": "凶", "含义": "辛苦不绝，早入隐遁，安心立命", "类别": "隐遁运"},
        }
        

        fortune = jixiong_map.get(number, {'吉凶': '凶', '含义': '未知数理，难以预测', '类别': '未知运'})['吉凶']
        
        return {
            'num': number,
            'element': wuxing,
            'fortune': fortune
        }
    
    def _calculate_wuge_score(self, wuge: Dict) -> int:
        """计算五格评分"""
        score = 50  # 基础分
        
        # 根据吉凶加分
        fortune_scores = {'大吉': 10, '吉': 7, '半吉': 4, '凶': 0}
        for ge_key in ['tiange', 'renge', 'dige', 'waige', 'zongge']:
            fortune = wuge[ge_key]['fortune']
            score += fortune_scores.get(fortune, 0)
        
        return min(100, score)
    
    def calculate_bazi(self, birth_dt: datetime, wannianli_data: dict, longitude: float,
                      latitude: float) -> Dict:
        """计算生辰八字"""
        logger.info(f"计算生辰八字: {birth_dt}")
        
        # 1. 计算真太阳时
        true_solar_time = self._calculate_true_solar_time(birth_dt, longitude)
        
        if wannianli_data:
            # 使用万年历数据
            year_gz = wannianli_data['year_ganzhi']
            month_gz = wannianli_data['month_ganzhi']
            day_gz = wannianli_data['day_ganzhi']
            lunar_date = self._solar_to_lunar(birth_dt)  # 用于显示
            logger.info(f"使用万年历数据计算八字: {year_gz} {month_gz} {day_gz}")
            
            # 解析万年历中的农历日期字符串（格式：YYYY-MM-DD）
            lunar_date_str = wannianli_data.get('lunar_date', '')
            if lunar_date_str:
                try:
                    lunar_year, lunar_month, lunar_day = self.change_date_str2date(lunar_date_str)
                except (ValueError, IndexError) as e:
                    logger.warning(f"解析农历日期失败: {lunar_date_str}, {e}")
                    # 降级使用阳历年月日
                    raise ValueError("万年历数据格式错误，无法解析农历日期:" + lunar_date_str)
            else:
                # 没有农历数据，使用阳历
                raise ValueError("万年历数据缺少农历日期:" + birth_dt.strftime("%Y-%m-%d"))
        else:
            # 降级：使用传统算法
            logger.warning("万年历数据不可用，使用传统算法")
            lunar_obj, lunar_year, lunar_month, lunar_day, is_leap = self._solar_to_lunar_full(birth_dt)
            year_gz = self._get_year_ganzhi_by_lichun(birth_dt, lunar_year)
            month_gz = self._get_month_ganzhi_by_jieqi(birth_dt, year_gz)
            day_gz = self._get_day_ganzhi(birth_dt)
            lunar_date = self._solar_to_lunar(birth_dt)
        
        # 5. 计算时柱（根据真太阳时）
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
        
        # 9. 确定喜用神（传入 bazi_str 使用强度表方法）
        xiyong_shen, ji_shen = self._determine_xiyongshen(rizhu, wuxing_count, lunar_month, bazi_str)
        
        # 10. 四季用神参考（使用节气判断）
        solar_term = wannianli_data.get('solar_term', '') if wannianli_data else ''
        siji_yongshen = self._get_siji_yongshen(rizhu, birth_dt, solar_term)
        
        # 11. 吉祥颜色
        colors = [self.WUXING_COLOR.get(wx, '') for wx in xiyong_shen]
        
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
            'ji_shen': ji_shen,
            'color': '、'.join(colors),
            'score': self._calculate_bazi_score(wuxing_count, xiyong_shen),
            'lunar_date': lunar_date
        }
        
        return result

    def change_date_str2date(self, lunar_date_str):
        lunar_date_parts = lunar_date_str.split('-')
        lunar_year = int(lunar_date_parts[0])
        lunar_month = int(lunar_date_parts[1])
        lunar_day = int(lunar_date_parts[2])
        return lunar_year, lunar_month, lunar_day
    
    def _solar_to_lunar(self, solar_dt: datetime) -> str:
        """将阳历转换为农历（返回字符串）
        
        优先从万年历数据库查询，如果查询失败则使用lunarcalendar库
        """
        # 尝试从万年历查询
        wannianli_data = self._get_ganzhi_from_wannianli(solar_dt)
        if wannianli_data and wannianli_data.get('lunar_show'):
            # 时辰
            hour = solar_dt.hour
            shichen_names = ['子时', '丑时', '寅时', '卯时', '辰时', '巳时',
                           '午时', '未时', '申时', '酉时', '戌时', '亥时']
            shichen = shichen_names[(hour + 1) // 2 % 12]
            
            # 万年历中的 lunar_show 格式类似 "己酉年 腊月初四"
            return f"{wannianli_data['lunar_show']} {shichen}"
        
        # 降级到 lunarcalendar 库
        if not LUNAR_AVAILABLE:
            return "农历功能不可用（请安装lunarcalendar库）"
        
        try:
            solar = Solar(solar_dt.year, solar_dt.month, solar_dt.day)
            lunar = Converter.Solar2Lunar(solar)
            
            # 时辰
            hour = solar_dt.hour
            shichen_names = ['子时', '丑时', '寅时', '卯时', '辰时', '巳时',
                           '午时', '未时', '申时', '酉时', '戌时', '亥时']
            shichen = shichen_names[(hour + 1) // 2 % 12]
            
            # 月份
            month_str = f"{lunar.month}月" if not lunar.isleap else f"闰{lunar.month}月"
            
            return f"{lunar.year}年{month_str}{lunar.day}日{shichen}"
        except Exception as e:
            logger.error(f"农历转换失败: {e}")
            return "农历转换失败"
    
    def _solar_to_lunar_full(self, solar_dt: datetime) -> Tuple:
        """将阳历转换为农历（返回完整信息）
        返回: (lunar对象, 农历年, 农历月, 农历日, 是否闰月)
        """
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
        # 时差 = (出生地经度 - 120) × 4分钟
        time_diff_minutes = (longitude - 120) * 4
        from datetime import timedelta
        return birth_dt + timedelta(minutes=time_diff_minutes)
    
    def _get_year_ganzhi(self, year: int) -> str:
        """获取年柱干支（简化版，按阳历年）"""
        tian_idx = (year - 4) % 10
        di_idx = (year - 4) % 12
        return self.TIANGAN[tian_idx] + self.DIZHI[di_idx]
    
    def _get_ganzhi_from_wannianli(self, birth_dt: datetime) -> Dict:
        """从万年历数据库查询干支信息
        
        Args:
            birth_dt: 出生日期时间
            
        Returns:
            包含年月日干支的字典，如果查询失败返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 格式化日期为 YYYY-MM-DD
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
        """根据立春节气获取年柱干支
        
        优先从万年历数据库查询，如果查询失败则使用简化算法
        """
        # 尝试从万年历查询
        wannianli_data = self._get_ganzhi_from_wannianli(birth_dt)
        if wannianli_data:
            return wannianli_data['year_ganzhi']
        
        # 降级到简化算法
        logger.warning("万年历查询失败，使用简化算法计算年柱")
        year = birth_dt.year
        month = birth_dt.month
        day = birth_dt.day
        
        # 简化处理：立春大约在2月3-5日
        # 如果是1月或2月初（2月4日之前），使用上一年的干支
        if month == 1 or (month == 2 and day < 4):
            year = year - 1
        
        tian_idx = (year - 4) % 10
        di_idx = (year - 4) % 12
        return self.TIANGAN[tian_idx] + self.DIZHI[di_idx]
    
    def _get_month_ganzhi(self, year: int, month: int) -> str:
        """获取月柱干支（旧版本，按阳历月份）
        
        月份地支固定：寅卯辰巳午未申酉戌亥子丑（正月寅开始）
        月份天干由年份天干和月份决定（五虎遁月诀）
        """
        # 月份对应的地支（正月对应寅，从索引2开始）
        # 1月=寅(2), 2月=卯(3), 3月=辰(4), 4月=巳(5), 5月=午(6), 6月=未(7)
        # 7月=申(8), 8月=酉(9), 9月=戌(10), 10月=亥(11), 11月=子(0), 12月=丑(1)
        month_dizhi_map = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1]  # 1-12月对应的地支索引
        
        if month < 1 or month > 12:
            month = 1  # 默认正月
        
        dizhi_idx = month_dizhi_map[month - 1]
        
        # 年份天干（用于五虎遁月）
        year_tian_idx = (year - 4) % 10
        
        # 五虎遁月诀：甲己之年丙作首（甲己年正月起丙寅）
        # 甲(0)己(5)年从丙(2)开始，乙(1)庚(6)年从戊(4)开始
        # 丙(2)辛(7)年从庚(6)开始，丁(3)壬(8)年从壬(8)开始
        # 戊(4)癸(9)年从甲(0)开始
        month_tiangan_start = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]  # 对应年干0-9
        
        # 计算月份天干（正月天干 + 月份偏移）
        zheng_yue_tiangan = month_tiangan_start[year_tian_idx]
        tiangan_idx = (zheng_yue_tiangan + month - 1) % 10
        
        return self.TIANGAN[tiangan_idx] + self.DIZHI[dizhi_idx]
    
    def _get_month_ganzhi_by_jieqi(self, birth_dt: datetime, year_gz: str) -> str:
        """根据节气获取月柱干支
        
        优先从万年历数据库查询，如果查询失败则使用简化算法
        """
        # 尝试从万年历查询
        wannianli_data = self._get_ganzhi_from_wannianli(birth_dt)
        if wannianli_data:
            return wannianli_data['month_ganzhi']
        
        # 降级到简化算法
        logger.warning("万年历查询失败，使用简化算法计算月柱")
        month = birth_dt.month
        day = birth_dt.day
        
        # 简化的节气判断（使用近似日期）
        # 返回节气月序号（1-12对应寅-丑）
        if (month == 2 and day >= 4) or (month == 3 and day < 6):
            jieqi_month = 1  # 寅月（正月）
        elif (month == 3 and day >= 6) or (month == 4 and day < 5):
            jieqi_month = 2  # 卯月（二月）
        elif (month == 4 and day >= 5) or (month == 5 and day < 6):
            jieqi_month = 3  # 辰月（三月）
        elif (month == 5 and day >= 6) or (month == 6 and day < 6):
            jieqi_month = 4  # 巳月（四月）
        elif (month == 6 and day >= 6) or (month == 7 and day < 8):
            jieqi_month = 5  # 午月（五月）
        elif (month == 7 and day >= 8) or (month == 8 and day < 8):
            jieqi_month = 6  # 未月（六月）
        elif (month == 8 and day >= 8) or (month == 9 and day < 8):
            jieqi_month = 7  # 申月（七月）
        elif (month == 9 and day >= 8) or (month == 10 and day < 9):
            jieqi_month = 8  # 酉月（八月）
        elif (month == 10 and day >= 9) or (month == 11 and day < 8):
            jieqi_month = 9  # 戌月（九月）
        elif (month == 11 and day >= 8) or (month == 12 and day < 7):
            jieqi_month = 10  # 亥月（十月）
        elif (month == 12 and day >= 7) or (month == 1 and day < 6):
            jieqi_month = 11  # 子月（十一月）
        else:  # (month == 1 and day >= 6) or (month == 2 and day < 4)
            jieqi_month = 12  # 丑月（十二月）
        
        # 月份地支：寅卯辰巳午未申酉戌亥子丑
        # 索引：    2  3  4  5  6  7  8  9  10 11 0  1
        dizhi_map = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 1]
        dizhi_idx = dizhi_map[jieqi_month - 1]
        
        # 获取年干（从年柱干支中提取）
        year_tian = year_gz[0]
        year_tian_idx = self.TIANGAN.index(year_tian)
        
        # 五虎遁月诀：根据年干确定正月（寅月）的天干起点
        month_tiangan_start = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]  # 对应年干0-9
        zheng_yue_tiangan = month_tiangan_start[year_tian_idx]
        
        # 计算当前月的天干
        tiangan_idx = (zheng_yue_tiangan + jieqi_month - 1) % 10
        
        return self.TIANGAN[tiangan_idx] + self.DIZHI[dizhi_idx]
    
    def _get_day_ganzhi(self, birth_dt: datetime) -> str:
        """获取日柱干支
        
        优先从万年历数据库查询，如果查询失败则使用简化算法
        """
        # 尝试从万年历查询
        wannianli_data = self._get_ganzhi_from_wannianli(birth_dt)
        if wannianli_data:
            return wannianli_data['day_ganzhi']
        
        # 降级到简化算法
        logger.warning("万年历查询失败，使用简化算法计算日柱")
        base_date = datetime(2000, 1, 1)
        days = (birth_dt - base_date).days
        gz_idx = days % 60
        return self.TIANGAN[gz_idx % 10] + self.DIZHI[gz_idx % 12]
    
    def _get_hour_ganzhi(self, true_time: datetime, day_gz: str) -> str:
        """获取时柱干支"""
        hour = true_time.hour
        
        # 确定时辰
        shichen_idx = (hour + 1) // 2 % 12
        
        # 根据日干确定时干
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
        """获取纳音（从数据库查询）
        
        Args:
            year_gz: 年柱干支
            month_gz: 月柱干支
            day_gz: 日柱干支
            hour_gz: 时柱干支
            
        Returns:
            四柱纳音字符串，格式：年纳音 月纳音 日纳音 时纳音
        """
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
        """计算五行强度（基于天干地支强度表）
        
        Args:
            bazi_str: 八字字符串，格式：年柱 月柱 日柱 时柱
            
        Returns:
            五行强度字典 {'木': xxx, '火': xxx, '土': xxx, '金': xxx, '水': xxx}
        """
        strength = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        
        # 分解八字
        bazi_parts = bazi_str.split()
        if len(bazi_parts) != 4:
            logger.warning(f"八字格式错误: {bazi_str}")
            return strength
        
        # 获取月支索引（用于查询强度表）
        month_dizhi = bazi_parts[1][1]  # 月柱的地支
        month_idx = self.DIZHI_INDEX.get(month_dizhi, 0)
        
        try:
            # 遍历四柱
            for i, pillar in enumerate(bazi_parts):
                if len(pillar) != 2:
                    continue
                
                tiangan = pillar[0]  # 天干
                dizhi = pillar[1]    # 地支
                
                # 1. 计算天干强度
                if tiangan in self.TIANGAN_INDEX:
                    tg_idx = self.TIANGAN_INDEX[tiangan]
                    tg_strength = self.TIANGAN_STRENGTH[month_idx][tg_idx]
                    tg_wuxing = self.TIANGAN_WUXING[tiangan]
                    strength[tg_wuxing] += tg_strength
                    logger.debug(f"{tiangan}({tg_wuxing}): +{tg_strength}")
                
                # 2. 计算地支藏干强度
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
        """计算同类和异类
        
        同类: 日主五行 + 生日主的五行
        异类: 其他三个五行
        
        Args:
            rizhu: 日主天干
            strength: 五行强度字典
            
        Returns:
            (同类五行列表, 同类强度, 异类五行列表, 异类强度)
        """
        rizhu_wx = self.TIANGAN_WUXING[rizhu]
        
        # 找到生日主的五行
        sheng_rizhu_wx = None
        for wx, sheng_wx in self.WUXING_SHENG.items():
            if sheng_wx == rizhu_wx:
                sheng_rizhu_wx = wx
                break
        
        # 同类：日主五行 + 生日主的五行
        tongyi = [rizhu_wx]
        tongyi_strength = strength[rizhu_wx]
        
        if sheng_rizhu_wx:
            tongyi.append(sheng_rizhu_wx)
            tongyi_strength += strength[sheng_rizhu_wx]
        
        # 异类：其他五行
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
                             bazi_str: str = None) -> Tuple[List, List]:
        """确定喜用神和忌神
        
        Args:
            rizhu: 日主天干
            wuxing_count: 五行个数统计（旧方法，保留兼容）
            month: 出生月份
            bazi_str: 八字字符串（用于新方法计算）
            
        Returns:
            (喜用神列表, 忌神列表)
        """
        rizhu_wx = self.TIANGAN_WUXING.get(rizhu, '土')
        
        # 如果有八字字符串，使用强度表方法
        if bazi_str:
            try:
                # 计算五行强度
                strength = self._calculate_wuxing_strength(bazi_str)
                
                # 计算同类异类
                tongyi, tongyi_strength, yilei, yilei_strength = \
                    self._calculate_tongyi_yilei(rizhu, strength)
                
                xiyong = []
                ji = []
                
                # 判断日主强弱
                # 同类强度 > 异类强度：日主偏强，取异类为喜用神
                # 同类强度 < 异类强度：日主偏弱，取同类为喜用神
                if tongyi_strength > yilei_strength:
                    # 日主强，喜克泄耗（异类）
                    xiyong = yilei.copy()
                    ji = tongyi.copy()
                    logger.info("日主偏强，喜用神为异类（克泄耗）")
                else:
                    # 日主弱，喜生扶（同类）
                    xiyong = tongyi.copy()
                    ji = yilei.copy()
                    logger.info("日主偏弱，喜用神为同类（生扶）")
                
                return xiyong, ji
                
            except Exception as e:
                logger.warning(f"强度表方法计算失败，使用简化方法: {e}")
        
        # 降级到简化判断：缺什么补什么
        xiyong = []
        ji = []
        
        for wx, count in wuxing_count.items():
            if count == 0:
                xiyong.append(wx)
            elif count >= 3:
                ji.append(wx)
        
        if not xiyong:
            # 如果不缺，则取生扶日主的
            xiyong = [self.WUXING_SHENG.get(rizhu_wx, '土')]
        
        return xiyong, ji
    
    def _get_siji_yongshen(self, rizhu: str, birth_dt: datetime, solar_term: str = '') -> str:
        """获取四季用神参考
        
        根据节气判断季节：
        春季：立春 ~ 立夏前
        夏季：立夏 ~ 立秋前
        秋季：立秋 ~ 立冬前
        冬季：立冬 ~ 立春前
        
        Args:
            rizhu: 日主天干
            birth_dt: 出生日期
            solar_term: 当天的节气（如果有）
        """
        rizhu_wx = self.TIANGAN_WUXING.get(rizhu, '土')
        
        # 节气到季节的映射
        # 春季节气：立春、雨水、惊蛰、春分、清明、谷雨
        # 夏季节气：立夏、小满、芒种、夏至、小暑、大暑
        # 秋季节气：立秋、处暑、白露、秋分、寒露、霜降
        # 冬季节气：立冬、小雪、大雪、冬至、小寒、大寒
        
        spring_terms = ['立春', '雨水', '惊蛰', '春分', '清明', '谷雨']
        summer_terms = ['立夏', '小满', '芒种', '夏至', '小暑', '大暑']
        autumn_terms = ['立秋', '处暑', '白露', '秋分', '寒露', '霜降']
        winter_terms = ['立冬', '小雪', '大雪', '冬至', '小寒', '大寒']
        
        # 如果提供了节气，直接根据节气判断
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
                # 节气为空或非标准节气，降级到按月份判断
                season = self._get_season_by_month(birth_dt.month)
        else:
            # 没有节气信息，查询数据库获取最近的节气
            season = self._get_season_by_solar_term_query(birth_dt)
        
        return f"日主天干{rizhu_wx}生于{season}"
    
    def _get_season_by_month(self, month: int) -> str:
        """根据月份简单判断季节（降级方案）"""
        if 2 <= month <= 4:
            return "春季"
        elif 5 <= month <= 7:
            return "夏季"
        elif 8 <= month <= 10:
            return "秋季"
        else:
            return "冬季"
    
    def _get_season_by_solar_term_query(self, birth_dt: datetime) -> str:
        """通过查询数据库获取最近的节气来判断季节"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            date_str = birth_dt.strftime('%Y-%m-%d')
            
            # 查询当前日期之前最近的一个节气
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
            
            # 如果查询失败，降级到按月份判断
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
        
        # 五行平衡度
        max_count = max(wuxing_count.values())
        min_count = min(wuxing_count.values())
        if max_count - min_count <= 2:
            score += 30
        elif max_count - min_count <= 4:
            score += 20
        else:
            score += 10
        
        # 喜用神得力
        score += len(xiyong_shen) * 5
        
        return min(100, score)
    
    def analyze_ziyi(self, name: str) -> Dict:
        """字义音形分析"""
        logger.info(f"分析字义音形: {name}")
        
        # 简化分析
        score = 75  # 基础分
        
        analysis = f"姓名'{name}'字义音形分析结果"
        
        return {
            'analysis': analysis,
            'score': score
        }
    
    def analyze_shengxiao(self, name: str, birth_dt: datetime) -> Dict:
        """生肖喜忌分析"""
        logger.info(f"分析生肖喜忌: {name}")
        
        # 确定生肖
        shengxiao_idx = (birth_dt.year - 4) % 12
        shengxiao = self.SHENGXIAO[shengxiao_idx]
        
        score = 80  # 基础分
        
        return {
            'shengxiao': shengxiao,
            'xi_zigen': ['艹', '木', '禾'],
            'ji_zigen': ['火', '日'],
            'score': score
        }
    
    def calculate_chenggu(self, birth_dt: datetime) -> Dict:
        """称骨算命计算
        
        Args:
            birth_dt: 出生日期时间
            
        Returns:
            包含骨重、命书和评价的字典
        """
        logger.info(f"计算称骨: {birth_dt}")
        
        # 获取农历信息
        wannianli_data = self._get_ganzhi_from_wannianli(birth_dt)
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
            if total_weight < 3.0:
                comment = "命运较苦，需自强不息"
            elif total_weight < 4.0:
                comment = "命运一般，中等偏下"
            elif total_weight < 5.0:
                comment = "命运中等，衣食无忧"
            elif total_weight < 6.0:
                comment = "命运较好，富贵安康"
            else:
                comment = "命运极佳，大富大贵"
            
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
    
    def _calculate_comprehensive_score(self, wuge_score: int, bazi_score: int,
                                      ziyi_score: int, shengxiao_score: int) -> int:
        """计算综合评分"""
        score = (wuge_score * 0.3 + bazi_score * 0.4 + 
                ziyi_score * 0.15 + shengxiao_score * 0.15)
        return round(score)
    
    def _generate_suggestion(self, score: int) -> str:
        """生成建议"""
        if score >= 90:
            return "姓名配置极佳，各项指标优秀，建议继续使用。"
        elif score >= 75:
            return "姓名整体配置良好，建议继续使用。"
        elif score >= 60:
            return "姓名配置一般，可以考虑改进。"
        else:
            return "姓名配置欠佳，建议考虑改名。"
