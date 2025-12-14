import sqlite3
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class IndustryAnalyzer:
    # 生肖五行映射表（与生肖分析器保持一致）
    SHENGXIAO_WUXING = {
        '鼠': '水', '牛': '土', '虎': '木', '兔': '木', '龙': '土', '蛇': '火',
        '马': '火', '羊': '土', '猴': '金', '鸡': '金', '狗': '土', '猪': '水',
    }
    
    def __init__(self, db_path: str = 'local.db'):
        # 按用户要求：统一从数据库读取，构造函数仅保留 db_path
        self.db_path = db_path
        self._char_wuxing_cache: Dict[str, str] = {}

    def _get_industry_wuxing(self, industry_code: str) -> str:
        """从数据库获取行业主五行"""
        if not industry_code:
            return ''
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('SELECT primary_wuxing FROM industry_config WHERE industry_code = ?', (industry_code,))
            row = cur.fetchone()
            return row[0] if row and row[0] else ''
        except Exception:
            return ''
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _get_lucky_chars(self, industry_code: str) -> Dict[str, Dict]:
        """从数据库获取行业吉祥字信息，返回 {char: meta} 结构"""
        result: Dict[str, Dict] = {}
        if not industry_code:
            return result
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('''
                SELECT character, char_wuxing, frequency, score_bonus, meaning, examples
                FROM industry_lucky_chars
                WHERE industry_code = ?
            ''', (industry_code,))
            rows = cur.fetchall()
            for ch, ch_wx, freq, bonus, meaning, examples in rows:
                meta = {
                    'char_wuxing': ch_wx or '',
                    'frequency': freq if freq is not None else 0,
                    'score_bonus': bonus if bonus is not None else 0,
                    'meaning': meaning or '',
                    'examples': []
                }
                # examples 为JSON字符串，尝试解析
                if examples:
                    try:
                        import json as _json
                        parsed = _json.loads(examples)
                        if isinstance(parsed, list):
                            meta['examples'] = parsed
                    except Exception:
                        pass
                result[ch] = meta
            return result
        except Exception:
            return result
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _sheng_relation(self, wx1: str, wx_list: List[str]) -> bool:
        sheng_map = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return wx1 and sheng_map.get(wx1) in wx_list

    def _ke_relation(self, wx1: str, wx2: str) -> bool:
        ke_map = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
        return wx1 and wx2 and ke_map.get(wx1) == wx2

    def _get_char_wuxing(self, ch: str) -> str:
        # 优先缓存
        if ch in self._char_wuxing_cache:
            return self._char_wuxing_cache[ch]
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('SELECT wuxing FROM kangxi_strokes WHERE character = ?', (ch,))
            row = cur.fetchone()
            wx = row[0] if row and row[0] else ''
            self._char_wuxing_cache[ch] = wx
            return wx
        except Exception:
            return ''
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _analyze_industry_supplement(self, industry_wuxing: str, xiyong_shen: List[str]) -> Dict:
        """分析行业五行是否补益负责人喜用神（关键原则1）
        
        返回：
        {
            'is_supplement': bool,  # 是否补益
            'description': str,      # 补益方式说明
            'score': int,           # 加分（补益）或减分（不补益）
        }
        """
        if not industry_wuxing:
            return {'is_supplement': False, 'description': '行业五行未定义', 'score': 0}
        
        if not xiyong_shen:
            return {'is_supplement': False, 'description': '未定义喜用神', 'score': 0}
        
        # 检查行业五行是否等于或生助喜用神
        if industry_wuxing in xiyong_shen:
            return {
                'is_supplement': True,
                'description': f'行业五行({industry_wuxing})直接为喜用神',
                'score': 10
            }
        elif self._sheng_relation(industry_wuxing, xiyong_shen):
            return {
                'is_supplement': True,
                'description': f'行业五行({industry_wuxing})生喜用神({",".join(xiyong_shen)})',
                'score': 8
            }
        else:
            return {
                'is_supplement': False,
                'description': f'行业五行({industry_wuxing})不补益喜用神({",".join(xiyong_shen)})',
                'score': -5
            }

    def _analyze_name_support(self, main_name: str, xiyong_shen: List[str]) -> Dict:
        """分析名称五行是否生助或相同于喜用神（关键原则2）
        
        返回：
        {
            'name_wuxing_dist': Dict[str, int],  # 名称五行分布
            'support_ratio': float,  # 支持率（0-1）
            'description': str,      # 详细说明
            'score': int,           # 评分
        }
        """
        name_wuxing = {}
        for ch in main_name:
            wx = self._get_char_wuxing(ch)
            if wx:
                name_wuxing[wx] = name_wuxing.get(wx, 0) + 1
        
        if not name_wuxing:
            return {
                'name_wuxing_dist': {},
                'support_ratio': 0,
                'description': '无法识别名称五行',
                'score': 0
            }
        
        support_count = 0
        support_details = []
        
        for wx, count in name_wuxing.items():
            if wx in xiyong_shen:
                support_count += count
                support_details.append(f'{wx}({count}个)为喜用神')
            elif self._sheng_relation(wx, xiyong_shen):
                support_count += count
                support_details.append(f'{wx}({count}个)生喜用神')
        
        total_chars = sum(name_wuxing.values())
        support_ratio = support_count / total_chars if total_chars > 0 else 0
        
        if support_ratio >= 0.8:
            score = 15
            assessment = '优秀'
        elif support_ratio >= 0.5:
            score = 10
            assessment = '良好'
        elif support_ratio >= 0.3:
            score = 5
            assessment = '尚可'
        else:
            score = -5
            assessment = '不佳'
        
        return {
            'name_wuxing_dist': name_wuxing,
            'support_ratio': round(support_ratio, 2),
            'description': f'名称五行支持度{assessment}({", ".join(support_details)})',
            'score': score
        }

    def _analyze_ke_prohibition(self, main_name: str, xiyong_shen: List[str]) -> Dict:
        """分析是否存在克制喜用神的五行（关键原则3 - 禁忌）
        
        返回：
        {
            'has_ke': bool,         # 是否存在克制
            'ke_details': List[str],  # 克制详情
            'score': int,           # 减分
        }
        """
        ke_details = []
        penalty = 0
        
        for ch in main_name:
            char_wx = self._get_char_wuxing(ch)
            if not char_wx:
                continue
            
            # 检查这个五行是否克制喜用神中的任何一个
            for xiyong_wx in xiyong_shen:
                if self._ke_relation(char_wx, xiyong_wx):
                    ke_details.append(f'{ch}({char_wx})克喜用神({xiyong_wx})')
                    penalty -= 20
        
        return {
            'has_ke': len(ke_details) > 0,
            'ke_details': ke_details,
            'score': penalty
        }

    def _analyze_relative_principles(self, main_name: str, industry_wuxing: str, 
                                     shengxiao_wuxing: str = '') -> Dict:
        """分析相对原则
        
        1. 行业五行宜生名称五行
        2. 名称五行宜与生肖五行协调
        3. 生肖五行宜生助喜用神（这个在此处作为信息，具体评分由其他模块处理）
        
        返回：
        {
            'industry_support_name': Dict,   # 行业五行与名称的关系
            'name_shengxiao_harmony': Dict,  # 名称五行与生肖的协调性
        }
        """
        name_wuxing = {}
        for ch in main_name:
            wx = self._get_char_wuxing(ch)
            if wx:
                name_wuxing[wx] = name_wuxing.get(wx, 0) + 1
        
        result = {
            'industry_support_name': {'supports': False, 'details': []},
            'name_shengxiao_harmony': {'harmony_score': 0, 'details': []}
        }
        
        # 检查行业五行是否生名称五行
        if industry_wuxing:
            for name_wx in name_wuxing.keys():
                if self._sheng_relation(industry_wuxing, [name_wx]):
                    result['industry_support_name']['supports'] = True
                    result['industry_support_name']['details'].append(
                        f'行业五行({industry_wuxing})生名称五行({name_wx})'
                    )
                elif industry_wuxing == name_wx:
                    result['industry_support_name']['details'].append(
                        f'行业五行({industry_wuxing})与名称五行({name_wx})相同'
                    )
        
        # 检查名称五行与生肖五行的协调性
        if shengxiao_wuxing:
            harmony_score = 0
            for name_wx, count in name_wuxing.items():
                if name_wx == shengxiao_wuxing:
                    harmony_score += count * 2
                    result['name_shengxiao_harmony']['details'].append(
                        f'名称五行({name_wx})与生肖五行({shengxiao_wuxing})相同'
                    )
                elif self._sheng_relation(name_wx, [shengxiao_wuxing]):
                    harmony_score += count
                    result['name_shengxiao_harmony']['details'].append(
                        f'名称五行({name_wx})生生肖五行({shengxiao_wuxing})'
                    )
            
            result['name_shengxiao_harmony']['harmony_score'] = harmony_score
        
        return result

    def calculate_wuxing_match_score(self, main_name: str, industry_code: str,
                                     xiyong_shen: List[str], ji_shen: List[str] = None,
                                     shengxiao: str = '', shengxiao_wuxing: str = '') -> Dict:
        """计算五行匹配分，集成关键原则和相对原则分析
        
        Args:
            main_name: 名称
            industry_code: 行业代码
            xiyong_shen: 喜用神列表
            ji_shen: 忌神列表
            shengxiao: 生肖名称（如'龙'）
            shengxiao_wuxing: 生肖五行
        
        Returns:
            Dict with:
            - wuxing_dist: 名称五行分布
            - match_score: 匹配总分
            - xiyong_match_score: 喜用神匹配分
            - critical_principles: 关键原则检查结果
            - relative_principles: 相对原则评分
            - match_detail: 详细说明
        """
        if ji_shen is None:
            ji_shen = []
        
        # 行业主五行来自数据库
        industry_wuxing = self._get_industry_wuxing(industry_code)
        
        # 如果未传入生肖五行，从生肖名称推导
        if not shengxiao_wuxing and shengxiao:
            shengxiao_wuxing = self.SHENGXIAO_WUXING.get(shengxiao, '')

        score = 0
        wuxing_dist: Dict[str, int] = {}
        match_detail: List[str] = []
        xiyong_match_score = 0

        logger.info(f"五行分析: 喜用神={xiyong_shen}, 忌神={ji_shen}, 行业五行={industry_wuxing}, 生肖={shengxiao}({shengxiao_wuxing})")
        
        # ============ 关键原则分析 ============
        critical_principles = {
            'industry_supplement_xiyong': self._analyze_industry_supplement(industry_wuxing, xiyong_shen),
            'name_support_xiyong': {},
            'ke_prohibition': {}
        }
        
        # ============ 名称五行处理 ============
        for char in main_name:
            char_wuxing = self._get_char_wuxing(char)
            if not char_wuxing:
                continue
            wuxing_dist[char_wuxing] = wuxing_dist.get(char_wuxing, 0) + 1

            # 忌神优先级最高：若为忌神，直接记减分
            if char_wuxing in ji_shen:
                score -= 25
                match_detail.append(f"{char}({char_wuxing}) 为忌神 -25")
            
            # 喜用神匹配
            if char_wuxing in xiyong_shen:
                score += 15
                xiyong_match_score += 15
                match_detail.append(f"{char}({char_wuxing}) 为喜用神 +15")
            elif self._sheng_relation(char_wuxing, xiyong_shen):
                score += 10
                xiyong_match_score += 10
                match_detail.append(f"{char}({char_wuxing}) 生喜用神 +10")

            # 行业五行匹配
            if self._sheng_relation(char_wuxing, [industry_wuxing]):
                score += 5
                match_detail.append(f"{char}({char_wuxing}) 生行业({industry_wuxing}) +5")
            elif char_wuxing == industry_wuxing:
                score += 3
                match_detail.append(f"{char}({char_wuxing}) 同行业({industry_wuxing}) +3")

        # ============ 关键原则2：名称五行支持度 ============
        critical_principles['name_support_xiyong'] = self._analyze_name_support(main_name, xiyong_shen)
        score += critical_principles['name_support_xiyong']['score']
        if critical_principles['name_support_xiyong']['description']:
            match_detail.append(f"[关键] {critical_principles['name_support_xiyong']['description']}")
        
        # ============ 关键原则3：克制禁忌检查 ============
        critical_principles['ke_prohibition'] = self._analyze_ke_prohibition(main_name, xiyong_shen)
        score += critical_principles['ke_prohibition']['score']
        for ke_detail in critical_principles['ke_prohibition']['ke_details']:
            match_detail.append(f"[禁忌警告] {ke_detail}")

        # 五行平衡加分
        if len(wuxing_dist) >= 3:
            score += 5
            match_detail.append(f"五行平衡 {len(wuxing_dist)}种 +5")

        # ============ 相对原则分析 ============
        relative_principles = self._analyze_relative_principles(main_name, industry_wuxing, shengxiao_wuxing)
        if relative_principles['industry_support_name']['supports']:
            score += 3
            match_detail.append(f"[相对] 行业五行生名称五行 +3")
        
        if relative_principles['name_shengxiao_harmony']['harmony_score'] > 0:
            harmony_bonus = min(5, relative_principles['name_shengxiao_harmony']['harmony_score'])
            score += harmony_bonus
            match_detail.append(f"[相对] 名称与生肖五行协调 +{harmony_bonus}")

        # 增加行业补益分
        score += critical_principles['industry_supplement_xiyong']['score']
        if critical_principles['industry_supplement_xiyong']['description']:
            match_detail.append(f"[原则] {critical_principles['industry_supplement_xiyong']['description']}")

        normalized_score = max(0, min(100, 50 + score))
        normalized_xiyong_score = max(0, min(100, 50 + xiyong_match_score))
        
        return {
            'wuxing_dist': wuxing_dist,
            'xiyong_match_score': normalized_xiyong_score,
            'match_score': normalized_score,
            'match_detail': match_detail,
            'critical_principles': critical_principles,  # 关键原则检查结果
            'relative_principles': relative_principles,   # 相对原则分析结果
            'suggestions': []
        }

    def calculate_lucky_char_score(self, main_name: str, industry_code: str) -> Dict:
        # 从数据库读取行业吉祥字
        lucky = self._get_lucky_chars(industry_code)
        found: List[str] = []
        score = 0
        detail: List[str] = []
        for ch in main_name:
            if ch in lucky:
                bonus = int(lucky[ch].get('score_bonus', 3) or 3)
                score += bonus
                found.append(ch)
                detail.append(f"{ch} 为{industry_code}行业高频字 +{bonus}")
        # 推荐Top5（按frequency降序）
        missing = []
        sorted_chars = sorted(lucky.items(), key=lambda x: x[1].get('frequency', 0) or 0, reverse=True)[:5]
        for ch, info in sorted_chars:
            if ch not in main_name:
                missing.append({'char': ch, 'meaning': info.get('meaning', ''), 'examples': info.get('examples', [])})
        return {
            'lucky_chars_found': found,
            'lucky_char_score': min(score, 30),
            'detail': detail,
            'missing_chars': missing
        }

    def analyze_industry(self, main_name: str, industry_code: str,
                         xiyong_shen: List[str], ji_shen: List[str] = None,
                         shengxiao: str = '', shengxiao_wuxing: str = '') -> Dict:
        """完整的行业五行分析，包含关键原则和相对原则"""
        wx = self.calculate_wuxing_match_score(main_name, industry_code, xiyong_shen, ji_shen,
                                              shengxiao, shengxiao_wuxing)
        lc = self.calculate_lucky_char_score(main_name, industry_code)
        total = int(wx['match_score'] * 0.65 + (lc['lucky_char_score'] / 30 * 100) * 0.35)
        grade = '不推荐'
        if total >= 90:
            grade = '极佳'
        elif total >= 80:
            grade = '优秀'
        elif total >= 70:
            grade = '良好'
        elif total >= 60:
            grade = '及格'
        return {
            'wuxing_analysis': wx,
            'lucky_char_analysis': lc,
            'xiyong_match_score': wx.get('xiyong_match_score', 50),
            'total_score': total,
            'grade': grade,
            'suggestions': []
        }

    def show_help_table(self) -> str:
        # 简要输出行业五行对照（从数据库）
        lines = ["行业五行对照:"]
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('SELECT industry_code, industry_name, primary_wuxing, secondary_wuxing FROM industry_config')
            for code, name, primary, secondary in cur.fetchall():
                lines.append(f"- {name}({code}) 主五行: {primary or ''} 次五行: {secondary or ''}")
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass
        return "\n".join(lines)
