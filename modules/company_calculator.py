import json
from typing import Dict, Any, List
from .company_parser import parse_company_name
from .bazi_calculator import BaziCalculator
from datetime import datetime
from .industry_analyzer import IndustryAnalyzer
from .shengxiao_analyzer import ShengxiaoAnalyzer
from .ziyi_analyzer import ZiyiAnalyzer
from .wuge_calculator import WugeCalculator

class CompanyCalculator:
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.industry_analyzer = IndustryAnalyzer(
            rules_path_wuxing=f'{data_dir}/industry_wuxing.json',
            lucky_chars_path=f'{data_dir}/industry_lucky_chars.json'
        )
        self.wuge_calc = WugeCalculator()
        self.sx_analyzer = ShengxiaoAnalyzer()
        self.ziyi_analyzer = ZiyiAnalyzer()

    def analyze_single(self, full_name: str, bazi_info: Dict[str, Any]) -> Dict[str, Any]:
        parsed = parse_company_name(full_name)
        # 从八字中提取喜用神与忌神
        xiyong_shen: List[str] = bazi_info.get('xiyong_shen', [])
        ji_shen: List[str] = bazi_info.get('ji_shen', [])
        industry_code: str = parsed.get('industry_code', '')

        # 行业分析
        industry_result = self.industry_analyzer.analyze_industry(parsed['main_name'], industry_code, xiyong_shen, ji_shen)
        # 补充行业主五行便于入库展示
        try:
            ind_cfg = self.industry_analyzer.industry_config.get(industry_code, {})
            industry_result['industry_wuxing'] = ind_cfg.get('primary_wuxing', '')
        except Exception:
            pass

        # 五格计算：全称与主名两套
        full_surname = parsed.get('prefix', '') or ''
        full_given = parsed.get('main_name', '') or ''
        wuge_full = self.wuge_calc.calculate_wuge(full_surname, full_given)

        # 主名拆分为姓/名
        main = parsed.get('main_name', '') or ''
        split = self._split_main_for_wuge(main)
        wuge_main = self.wuge_calc.calculate_wuge(split['surname'], split['given'])

        # 五格评分（占比15%）：取两套的均值
        wuge_total = int((wuge_full.get('score', 0) + wuge_main.get('score', 0)) / 2)

        # 八字匹配占比35%（此处作为占位，使用xiyong_match做替代或从bazi_info传入）
        bazi_match_score = int(bazi_info.get('bazi_match_score', industry_result['xiyong_match_score']))

        # 生肖与字义分析
        shengxiao_detail = {}
        ziyi_detail = {}
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
            # 字义：不依赖生日
            ziyi_detail = self.ziyi_analyzer.analyze_ziyi(main_for_eval)
        except Exception:
            pass

        # 生肖占比5%
        shengxiao_score = int((shengxiao_detail.get('score') if shengxiao_detail else bazi_info.get('shengxiao_score', 75)) or 75)

        # 字义音形占比5%
        ziyi_score = int((ziyi_detail.get('score') if ziyi_detail else bazi_info.get('ziyi_score', 75)) or 75)

        # 喜用神匹配度单独占比20%，直接使用行业分析产出的xiyong_match_score
        xiyong_match_score = int(industry_result['xiyong_match_score'])

        total_score = int(
            wuge_total * 0.15 +
            (industry_result['total_score']) * 0.20 +
            bazi_match_score * 0.35 +
            xiyong_match_score * 0.20 +
            shengxiao_score * 0.05 +
            ziyi_score * 0.05
        )

        return {
            'parsed': parsed,
            'scores': {
                'wuge_score': wuge_total,
                'industry_score': industry_result['total_score'],
                'bazi_match_score': bazi_match_score,
                'xiyong_match_score': xiyong_match_score,
                'shengxiao_score': shengxiao_score,
                'ziyi_score': ziyi_score,
                'total_score': total_score,
                'grade': self._grade(total_score)
            },
            'industry_detail': industry_result,
            'wuge_full': wuge_full,
            'wuge_main': wuge_main,
            'main_split': split,
            'shengxiao_detail': shengxiao_detail,
            'ziyi_detail': ziyi_detail
        }

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
            'bazi_match_score': int(res.get('score', 75)),
            'birth_time': birth_time
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

    def batch_analyze(self, names: List[str], bazi_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [self.analyze_single(n, bazi_info) for n in names]

    def compare(self, name_a: str, name_b: str, bazi_info: Dict[str, Any]) -> Dict[str, Any]:
        a = self.analyze_single(name_a, bazi_info)
        b = self.analyze_single(name_b, bazi_info)
        return {
            'a': a,
            'b': b,
            'better': 'A' if a['scores']['total_score'] >= b['scores']['total_score'] else 'B'
        }
