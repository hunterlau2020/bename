import json
import sqlite3
from typing import Dict, List

class IndustryAnalyzer:
    def __init__(self, rules_path_wuxing: str = 'data/industry_wuxing.json',
                 lucky_chars_path: str = 'data/industry_lucky_chars.json',
                 db_path: str = 'local.db'):
        self.industry_config = self._load_json(rules_path_wuxing)
        self.lucky_chars = self._load_json(lucky_chars_path)
        self.db_path = db_path
        self._char_wuxing_cache: Dict[str, str] = {}

    def _load_json(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

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

    def calculate_wuxing_match_score(self, main_name: str, industry_code: str,
                                     xiyong_shen: List[str], ji_shen: List[str] = None) -> Dict:
        if ji_shen is None:
            ji_shen = []
        industry = self.industry_config.get(industry_code, {})
        industry_wuxing = industry.get('primary_wuxing', '')

        score = 0
        wuxing_dist: Dict[str, int] = {}
        match_detail: List[str] = []
        xiyong_match_score = 0

        for char in main_name:
            char_wuxing = self._get_char_wuxing(char)
            if not char_wuxing:
                continue
            wuxing_dist[char_wuxing] = wuxing_dist.get(char_wuxing, 0) + 1

            if char_wuxing in xiyong_shen:
                score += 15
                xiyong_match_score += 15
                match_detail.append(f"{char}({char_wuxing}) 为喜用神 +15")
            elif self._sheng_relation(char_wuxing, xiyong_shen):
                score += 10
                xiyong_match_score += 10
                match_detail.append(f"{char}({char_wuxing}) 生喜用神 +10")

            if char_wuxing in ji_shen:
                score -= 25
                match_detail.append(f"{char}({char_wuxing}) 为忌神 -25")

            if self._sheng_relation(char_wuxing, [industry_wuxing]):
                score += 5
                match_detail.append(f"{char}({char_wuxing}) 生行业({industry_wuxing}) +5")
            elif char_wuxing == industry_wuxing:
                score += 3
                match_detail.append(f"{char}({char_wuxing}) 同行业({industry_wuxing}) +3")

        if len(wuxing_dist) >= 3:
            score += 5
            match_detail.append(f"五行平衡 {len(wuxing_dist)}种 +5")

        normalized_score = max(0, min(100, 50 + score))
        normalized_xiyong_score = max(0, min(100, 50 + xiyong_match_score))
        return {
            'wuxing_dist': wuxing_dist,
            'xiyong_match_score': normalized_xiyong_score,
            'match_score': normalized_score,
            'match_detail': match_detail,
            'suggestions': []
        }

    def calculate_lucky_char_score(self, main_name: str, industry_code: str) -> Dict:
        lucky = self.lucky_chars.get(industry_code, {})
        found = []
        score = 0
        detail = []
        for ch in main_name:
            if ch in lucky:
                bonus = int(lucky[ch].get('score_bonus', 3))
                score += bonus
                found.append(ch)
                detail.append(f"{ch} 为{industry_code}行业高频字 +{bonus}")
        # 推荐Top5
        missing = []
        sorted_chars = sorted(lucky.items(), key=lambda x: x[1].get('frequency', 50), reverse=True)[:5]
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
                         xiyong_shen: List[str], ji_shen: List[str] = None) -> Dict:
        wx = self.calculate_wuxing_match_score(main_name, industry_code, xiyong_shen, ji_shen)
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
        # 简要输出行业五行对照
        lines = ["行业五行对照:"]
        for code, info in self.industry_config.items():
            lines.append(f"- {info.get('industry_name','')}({code}) 主五行: {info.get('primary_wuxing','')} 次五行: {info.get('secondary_wuxing','')}")
        return "\n".join(lines)
