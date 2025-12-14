import json
import sqlite3
import logging
from typing import Dict, Any, List
from .company_parser import parse_company_name
from .bazi_calculator import BaziCalculator
from datetime import datetime
from .industry_analyzer import IndustryAnalyzer
from .shengxiao_analyzer import ShengxiaoAnalyzer
from .ziyi_analyzer import ZiyiAnalyzer
from .wuge_calculator import WugeCalculator

logger = logging.getLogger(__name__)

class CompanyCalculator:
    def __init__(self, data_dir: str = 'data', db_path: str = 'local.db'):
        self.data_dir = data_dir
        self.db_path = db_path
        self.industry_analyzer = IndustryAnalyzer(db_path=db_path)
        self.wuge_calc = WugeCalculator(db_path=db_path)
        self.sx_analyzer = ShengxiaoAnalyzer(db_path=db_path)
        self.ziyi_analyzer = ZiyiAnalyzer(db_path=db_path)

    def analyze_single(self, prefix_name: str, main_name: str, suffix_name: str, form_org: str,
                       full_name: str, industry_type, bazi_info: Dict[str, Any]) -> Dict[str, Any]:
        # 按用户要求：不在程序内拆分/拼接公司名，直接使用传入的全称
        parsed = {
            'full_name': full_name,
            'main_name': main_name,
            'prefix': prefix_name,
            'industry_code': suffix_name
        }
        # 从八字中提取喜用神与忌神
        xiyong_shen: List[str] = bazi_info.get('xiyong_shen', [])
        ji_shen: List[str] = bazi_info.get('ji_shen', [])
        industry_code: str = parsed.get('industry_code', '')
        
        # 通过数据库解析中文行业名到标准industry_code（移除硬编码）
        for test_industry in [industry_type, industry_code]:
            try:
                industry_en_code = self._resolve_industry_code(test_industry)
                logger.info(f"Resolved industry code: {test_industry} -> {industry_en_code}")
                break
            except Exception as e:
                logger.error(f"Failed to resolve industry code for '{test_industry}': {e}")

        # 生肖与字义分析（提前进行以获取生肖五行信息）
        shengxiao_detail = {}
        ziyi_detail = {}
        shengxiao_name = ''
        shengxiao_wuxing = ''
        try:
            # 优先使用主名做分析（更贴近字号）
            main_for_eval = parsed.get('main_name') or parsed.get('full_name') or full_name
            # 生肖：需要出生日期，若无则跳过并给中性分
            birth_dt = None
            birth_time_str = (bazi_info or {}).get('birth_time') or (bazi_info or {}).get('birth_dt')
            if isinstance(birth_time_str, str) and len(birth_time_str) >= 10:
                # 仅取日期部分
                date_part = birth_time_str[:10]
                try:
                    birth_dt = datetime.strptime(date_part, "%Y-%m-%d")
                except Exception:
                    birth_dt = None
            if birth_dt:
                shengxiao_detail = self.sx_analyzer.analyze_shengxiao(main_for_eval, birth_dt)
                shengxiao_name = shengxiao_detail.get('shengxiao', '')
                shengxiao_wuxing = shengxiao_detail.get('wuxing', '')
            # 字义：不依赖生日
            ziyi_detail = self.ziyi_analyzer.analyze_ziyi(main_for_eval)
        except Exception:
            pass
        # 五行与喜用神分析（独立于行业，但包含生肖五行信息）
        wuxing_result = self.industry_analyzer.calculate_wuxing_match_score(
            parsed['main_name'], industry_en_code, xiyong_shen, ji_shen,
            shengxiao_name, shengxiao_wuxing
        )
        
        # 行业吉祥字分析
        lucky_char_result = self.industry_analyzer.calculate_lucky_char_score(parsed['main_name'], industry_en_code)
        
        # 获取喜用神描述
        xiyong_desc = bazi_info.get('xiyong_desc', '')
        
        # 行业综合评分
        industry_total_score = int(wuxing_result['match_score'] * 0.65 + (lucky_char_result['lucky_char_score'] / 30 * 100) * 0.35)
        industry_grade = '不推荐'
        if industry_total_score >= 90:
            industry_grade = '极佳'
        elif industry_total_score >= 80:
            industry_grade = '优秀'
        elif industry_total_score >= 70:
            industry_grade = '良好'
        elif industry_total_score >= 60:
            industry_grade = '及格'
        
        # 补充行业主五行
        industry_wuxing = ''
        try:
            industry_wuxing = self.industry_analyzer._get_industry_wuxing(industry_en_code)
        except Exception:
            pass

        # 五格计算：全称与主名两套
        # 五格计算统一使用“全称作为名”，不做自动拆分
        wuge_full = self.wuge_calc.calculate_wuge('', parsed.get('full_name', '') or '')

        # 主名拆分为姓/名
        # 主名五格：同样不做拆分，避免误判
        main = parsed.get('main_name', '') or ''
        split = {'surname': '', 'given': main}
        wuge_main = self.wuge_calc.calculate_wuge('', main)

        # 五格评分（占比15%）：取两套的均值
        wuge_total = int((wuge_full.get('score', 0) + wuge_main.get('score', 0)) / 2)

        # 八字匹配占比35%（此处作为占位，使用xiyong_match做替代或从bazi_info传入）
        bazi_match_score = int(bazi_info.get('bazi_match_score', wuxing_result['xiyong_match_score']))

        # 生肖占比5%
        shengxiao_score = int((shengxiao_detail.get('score') if shengxiao_detail else bazi_info.get('shengxiao_score', 75)) or 75)

        # 字义音形占比5%
        ziyi_score = int((ziyi_detail.get('score') if ziyi_detail else bazi_info.get('ziyi_score', 75)) or 75)

        # 喜用神匹配度单独占比20%
        xiyong_match_score = int(wuxing_result['xiyong_match_score'])

        total_score = int(
            wuge_total * 0.15 +
            industry_total_score * 0.20 +
            bazi_match_score * 0.35 +
            xiyong_match_score * 0.20 +
            shengxiao_score * 0.05 +
            ziyi_score * 0.05
        )

        # 逐字清单（全称与主名）
        char_details = {
            'full_name': self._get_char_details(full_name),
            'main_name': self._get_char_details(parsed.get('main_name') or '')
        }

        return {
            'parsed': parsed,
            'scores': {
                'wuge_score': wuge_total,
                'industry_score': industry_total_score,
                'bazi_match_score': bazi_match_score,
                'xiyong_match_score': xiyong_match_score,
                'shengxiao_score': shengxiao_score,
                'ziyi_score': ziyi_score,
                'total_score': total_score,
                'grade': self._grade(total_score)
            },
            'wuxing_analysis': {
                'wuxing_dist': wuxing_result['wuxing_dist'],
                'match_score': wuxing_result['match_score'],
                'xiyong_match_score': wuxing_result['xiyong_match_score'],
                'match_detail': wuxing_result['match_detail'],
                'critical_principles': wuxing_result.get('critical_principles', {}),
                'relative_principles': wuxing_result.get('relative_principles', {})
            },
            'industry_detail': {
                'industry_code': industry_code,
                'industry_wuxing': industry_wuxing,
                'lucky_chars_found': lucky_char_result['lucky_chars_found'],
                'lucky_char_score': lucky_char_result['lucky_char_score'],
                'lucky_char_detail': lucky_char_result['detail'],
                'suggested_chars': lucky_char_result['missing_chars'],
                'total_score': industry_total_score,
                'grade': industry_grade,
                'calculation_steps': [
                    {
                        'step': '五行匹配分',
                        'value': wuxing_result['match_score'],
                        'description': f"五行分布: {wuxing_result['wuxing_dist']}, 权重: 65%"
                    },
                    {
                        'step': '吉祥字匹配分',
                        'value': lucky_char_result['lucky_char_score'],
                        'description': f"找到吉祥字: {', '.join(lucky_char_result['lucky_chars_found']) or '无'}, 权重: 35%"
                    },
                    {
                        'step': '行业综合得分',
                        'value': industry_total_score,
                        'description': f"{wuxing_result['match_score']} × 0.65 + ({lucky_char_result['lucky_char_score']} / 30 × 100) × 0.35 = {industry_total_score}",
                        'evaluation': industry_grade
                    }
                ],
                'calculation_summary': f"五行{wuxing_result['match_score']:.0f} × 0.65 + 吉字{lucky_char_result['lucky_char_score']:.0f} × 0.35 = {industry_total_score}分"
            },
            'wuge_full': wuge_full,
            'wuge_main': wuge_main,
            'main_split': split,
            'shengxiao_detail': shengxiao_detail,
            'ziyi_detail': ziyi_detail,
            'bazi_detail': {
                'bazi_str': bazi_info.get('bazi_str'),
                'wuxing': bazi_info.get('wuxing'),
                'lunar_date': bazi_info.get('lunar_date'),
                'xiyong_shen': bazi_info.get('xiyong_shen', []),
                'ji_shen': bazi_info.get('ji_shen', []),
                'xiyong_desc': xiyong_desc,
                'rizhu': bazi_info.get('rizhu'),
                'tongyi': bazi_info.get('tongyi'),
                'yilei': bazi_info.get('yilei'),
                'siji': bazi_info.get('siji')
            },
            'char_details': char_details
        }

    def _resolve_industry_code(self, industry_name_or_code: str) -> str:
        """通过数据库将用户输入的行业中文名映射到标准industry_code。
        若传入已为code则直接返回；找不到则返回原值或空字符串。
        """
        name = (industry_name_or_code or '').strip()
        if not name:
            raise Exception("行业名称或代码不能为空")
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            # 优先按中文名精确匹配
            cur.execute('SELECT industry_code FROM industry_config WHERE industry_name = ?', (name,))
            row = cur.fetchone()
            if row and row[0]:
                return row[0]
            # 其次按code匹配（用户可能直接传code）
            cur.execute('SELECT industry_code FROM industry_config WHERE industry_code = ?', (name,))
            row = cur.fetchone()
            if row and row[0]:
                return row[0]
            # 可选：按LIKE模糊匹配（避免误匹配，保守处理）
            cur.execute('SELECT industry_code FROM industry_config WHERE industry_name LIKE ?', (f'%{name}%',))
            row = cur.fetchone()
            if row and row[0]:
                return row[0]
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass
        raise Exception("无法解析行业名称或代码: {}".format(industry_name_or_code))

    def build_bazi_info(self, birth_time: str, longitude: float, latitude: float) -> Dict[str, Any]:
        """桥接个人版八字计算，生成公司版所需的 bazi_info。
        Args:
            birth_time: 出生时间，格式 'YYYY-MM-DD HH:MM'
            longitude: 经度
            latitude: 纬度
        Returns:
            dict: 包含 'xiyong_shen', 'ji_shen', 'bazi_match_score'
        """
        try:
            dt = datetime.strptime(birth_time, "%Y-%m-%d %H:%M")
        except ValueError:
            # 尝试无分钟格式
            dt = datetime.strptime(birth_time, "%Y-%m-%d %H")
        bazi_calc = BaziCalculator()
        # 优先从万年历表获取当日干支数据，传入以避免降级路径与警告
        try:
            wn = bazi_calc._get_ganzhi_from_wannianli(dt)
        except Exception:
            wn = None
        res = bazi_calc.calculate_bazi(dt, wannianli_data=wn, longitude=longitude, latitude=latitude)
        return {
            'xiyong_shen': res.get('xiyong_shen', []),
            'ji_shen': res.get('ji_shen', []),
            'xiyong_desc': res.get('xiyong_desc', ''),
            'bazi_match_score': int(res.get('score', 75)),
            'birth_time': birth_time,
            'bazi_str': res.get('bazi_str'),
            'wuxing': res.get('wuxing'),
            'lunar_date': res.get('lunar_date'),
            'rizhu': res.get('rizhu'),
            'tongyi': res.get('tongyi'),
            'yilei': res.get('yilei'),
            'siji': res.get('siji')
        }

    def _grade(self, total: int) -> str:
        if total >= 90:
            return '极佳'
        if total >= 80:
            return '优秀'
        if total >= 70:
            return '良好'
        if total >= 60:
            return '及格'
        return '不推荐'

    def _calc_wuge_score(self, name: str) -> int:
        # 简化版五格评分：以长度映射到区间
        n = len(name)
        if n <= 2:
            return 60
        if n == 3:
            return 75
        if n == 4:
            return 85
        if n == 5:
            return 90
        return 80

    def _split_main_for_wuge(self, main: str) -> Dict[str, str]:
        n = len(main or '')
        if n <= 1:
            return {'surname': '', 'given': main or ''}
        if n == 2:
            return {'surname': main[0], 'given': main[1]}
        if n == 3:
            return {'surname': main[0], 'given': main[1:]}
        if n == 4:
            return {'surname': main[:2], 'given': main[2:]}
        # n > 4 视为双姓复名
        return {'surname': main[:2], 'given': main[2:]}

    def _get_char_details(self, text: str) -> List[Dict[str, Any]]:
        if not text:
            return []
        items: List[Dict[str, Any]] = []
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            for ch in text:
                cur.execute(
                    "SELECT traditional, pinyin, strokes, wuxing, luck FROM kangxi_strokes WHERE character=?",
                    (ch,)
                )
                row = cur.fetchone()
                if row:
                    trad, pinyin, strokes, wuxing, luck = row
                    items.append({
                        'char': ch,
                        'traditional': trad or ch,
                        'pinyin': pinyin or '',
                        'strokes': strokes,
                        'element': wuxing or '',
                        'luck': luck or ''
                    })
                else:
                    items.append({
                        'char': ch,
                        'traditional': ch,
                        'pinyin': '',
                        'strokes': None,
                        'element': '',
                        'luck': ''
                    })
        except Exception as e:
            logger.exception(f"查询字符详情失败 for text={text}: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass
        return items

    def batch_analyze(self, names: List[str], industry_type, bazi_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        # TXT批量模式：names是完整公司名列表，逐个分析
        results = []
        for full_name in names:
            # 不做拆分，传入空字段
            result = self.analyze_single('', full_name, '', '', full_name, industry_type, bazi_info)
            results.append(result)
        return results

    def compare(self, name_a: str, name_b: str, bazi_info: Dict[str, Any]) -> Dict[str, Any]:
        a = self.analyze_single('', name_a, '', '', name_a, bazi_info)
        b = self.analyze_single('', name_b, '', '', name_b, bazi_info)
        return {
            'a': a,
            'b': b,
            'better': 'A' if a['scores']['total_score'] >= b['scores']['total_score'] else 'B'
        }
