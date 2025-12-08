# -*- coding: utf-8 -*-
"""
生肖喜忌分析模块 - 生肖分析和喜忌用字推荐
基于传统生肖喜忌理论，分析姓名中的字根是否符合生肖特性
"""

import logging
from datetime import datetime
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class ShengxiaoAnalyzer:
    """生肖喜忌分析器"""
    
    def __init__(self, db_path: str = 'local.db'):
        """初始化生肖分析器
        
        Args:
            db_path: 数据库文件路径
        """
        # 生肖列表
        self.SHENGXIAO = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        
        # 数据库路径
        self.db_path = db_path
        
        # 加载生肖喜忌数据
        self.shengxiao_data = self._load_shengxiao_data()
    
    def _load_shengxiao_data(self) -> Dict:
        """从数据库加载生肖喜忌数据
        
        Returns:
            生肖数据字典 {生肖: {xi_zigen: [], ji_zigen: [], comment: ''}}
        """
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查询生肖喜忌数据
            cursor.execute("""
                SELECT DISTINCT shengxiao, xi_zigen, ji_zigen, comment
                FROM shengxiao_xiji
                ORDER BY 
                    CASE shengxiao
                        WHEN '鼠' THEN 1 WHEN '牛' THEN 2 WHEN '虎' THEN 3
                        WHEN '兔' THEN 4 WHEN '龙' THEN 5 WHEN '蛇' THEN 6
                        WHEN '马' THEN 7 WHEN '羊' THEN 8 WHEN '猴' THEN 9
                        WHEN '鸡' THEN 10 WHEN '狗' THEN 11 WHEN '猪' THEN 12
                    END
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            # 转换为字典格式
            shengxiao_dict = {}
            for row in rows:
                shengxiao = row[0]
                xi_zigen = row[1].split(',') if row[1] else []
                ji_zigen = row[2].split(',') if row[2] else []
                comment = row[3] or ''
                
                shengxiao_dict[shengxiao] = {
                    'xi_zigen': xi_zigen,
                    'ji_zigen': ji_zigen,
                    'comment': comment
                }
            
            logger.info(f"成功从数据库加载生肖数据: {len(shengxiao_dict)}个生肖")
            return shengxiao_dict
            
        except Exception as e:
            logger.error(f"加载生肖数据失败: {e}")
            return {}
    
    def _get_radical_from_db(self, char: str) -> str:
        """从康熙字典数据库获取部首
        
        Args:
            char: 汉字
            
        Returns:
            部首字符串
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT radical FROM kangxi_strokes WHERE character = ?
            """, (char,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                return row[0]
        except Exception as e:
            logger.debug(f"查询部首失败: {e}")
        
        return ''
    
    def _extract_radicals(self, name: str) -> Set[str]:
        """提取姓名中的字根（部首和偏旁）
        
        Args:
            name: 姓名
            
        Returns:
            字根集合
        """
        radicals = set()
        
        # 常见字根映射（扩展版）
        radical_map = {
            # 水相关（氵、水）
            '江': '氵', '河': '氵', '海': '氵', '湖': '氵', '波': '氵', '洋': '氵',
            '涛': '氵', '浩': '氵', '清': '氵', '淼': '氵', '沁': '氵', '泽': '氵',
            '汉': '氵', '沐': '氵', '沛': '氵', '汶': '氵', '沙': '氵', '沫': '氵',
            '泉': '氵', '泊': '氵', '沿': '氵', '泳': '氵', '洁': '氵', '洪': '氵',
            '津': '氵', '洲': '氵', '流': '氵', '润': '氵', '涵': '氵', '淑': '氵',
            '渊': '氵', '溪': '氵', '滨': '氵', '漫': '氵', '澜': '氵', '潮': '氵',
            '水': '水',
            
            # 木相关
            '林': '木', '森': '木', '树': '木', '松': '木', '柏': '木', '杨': '木',
            '桐': '木', '梅': '木', '梓': '木', '楠': '木', '榕': '木', '栋': '木',
            
            # 草相关
            '芳': '艹', '花': '艹', '莉': '艹', '萍': '艹', '菲': '艹', '蕾': '艹',
            '茜': '艹', '薇': '艹', '蓉': '艹', '萱': '艹', '芬': '艹', '茹': '艹',
            '英': '艹', '荣': '艹', '华': '艹', '菁': '艹', '芸': '艹', '芮': '艹',
            
            # 禾相关
            '秀': '禾', '秋': '禾', '程': '禾', '稼': '禾', '穗': '禾', '颖': '禾',
            '和': '禾', '利': '禾', '种': '禾',
            
            # 金相关
            '鑫': '金', '钧': '金', '铭': '金', '锋': '金', '钢': '金', '铁': '金',
            '锦': '金', '银': '金', '钊': '金', '钰': '金', '镇': '金', '锐': '金',
            
            # 火日相关
            '炎': '火', '烨': '火', '焱': '火', '煜': '火', '烁': '火', '炯': '火',
            '明': '日', '晨': '日', '昌': '日', '旭': '日', '晓': '日', '昊': '日',
            '晖': '日', '暄': '日', '曦': '日', '晴': '日', '昱': '日',
            
            # 山相关
            '山': '山', '岳': '山', '峰': '山', '峻': '山', '崇': '山', '岩': '山',
            '嵩': '山', '岚': '山', '峥': '山',
            
            # 田相关
            '田': '田', '畅': '田', '畴': '田', '略': '田', '番': '田',
            
            # 口宀相关
            '吉': '口', '君': '口', '哲': '口', '品': '口', '唯': '口', '启': '口',
            '宇': '宀', '宏': '宀', '宁': '宀', '安': '宀', '宸': '宀', '宜': '宀',
            '家': '宀', '宝': '宀', '富': '宀', '宽': '宀', '寅': '宀',
            
            # 王相关
            '王': '王', '玉': '王', '珍': '王', '珠': '王', '琳': '王', '瑶': '王',
            '琪': '王', '瑾': '王', '璐': '王', '璇': '王', '环': '王', '琦': '王',
            
            # 人相关
            '伟': '人', '仁': '人', '佳': '人', '俊': '人', '杰': '人', '健': '人',
            '伦': '人', '修': '人', '信': '人', '倩': '人', '亿': '人', '仪': '人',
            
            # 心月肉相关
            '心': '心', '忠': '心', '思': '心', '慧': '心', '怡': '心', '恒': '心',
            '月': '月', '朋': '月', '有': '月', '朗': '月', '朝': '月', '期': '月',
            '胜': '肉', '育': '肉', '胡': '肉', '能': '肉',
            
            # 车相关
            '车': '车', '轩': '车', '辉': '车', '辰': '车', '轮': '车',
            
            # 衣彡巾相关
            '裕': '衣', '初': '衣', '裳': '衣', '袁': '衣',
            '彩': '彡', '彬': '彡', '彦': '彡', '影': '彡',
            '帆': '巾', '帅': '巾', '帮': '巾', '常': '巾',
            
            # 其他
            '龙': '龙', '虎': '虎', '马': '马', '羊': '羊', '鱼': '鱼',
            '云': '云', '雨': '雨', '雪': '雨', '雷': '雨', '霖': '雨',
            
            # 豆米相关
            '豆': '豆', '豪': '豆', '登': '豆', '澄': '豆',
            '米': '米', '精': '米', '粮': '米', '粉': '米',
            
            # 犬相关
            '狗': '犬', '狼': '犬', '猛': '犬', '猪': '犬', '狮': '犬',
            
            # 刀血相关
            '刀': '刀', '刃': '刀', '刚': '刀', '剑': '刀', '利': '刀',
            '血': '血',
            
            # 石相关
            '石': '石', '岩': '石', '碑': '石', '硕': '石',
            
            # 示相关
            '示': '示', '祥': '示', '福': '示', '礼': '示', '祺': '示',
            
            # 辰酉相关
            '辰': '辰', '龙': '辰', '晨': '辰',
            '酉': '酉', '鸡': '酉', '醇': '酉',
            
            # 虫相关
            '虫': '虫', '蝶': '虫', '蜂': '虫', '虹': '虫',
        }
        
        # 提取名字中的字根
        for char in name:
            # 1. 首先查找手动映射
            if char in radical_map:
                radicals.add(radical_map[char])
            
            # 2. 从数据库查询部首
            db_radical = self._get_radical_from_db(char)
            if db_radical:
                radicals.add(db_radical)
            
            # 3. 添加字符本身（用于完全匹配）
            radicals.add(char)
        
        return radicals
    
    def _calculate_score(self, name_radicals: Set[str], xi_zigen: List[str], 
                        ji_zigen: List[str]) -> Dict:
        """计算生肖喜忌评分
        
        Args:
            name_radicals: 姓名中的字根
            xi_zigen: 喜用字根列表
            ji_zigen: 忌用字根列表
            
        Returns:
            评分结果 {score: int, xi_count: int, ji_count: int, xi_found: [], ji_found: []}
        """
        # 同义字根映射（处理不同表示方式）
        synonym_map = {
            '水': ['水', '氵'],
            '氵': ['水', '氵'],
            '艹': ['艹', '草'],
            '草': ['艹', '草'],
        }
        
        # 扩展姓名字根（添加同义字根）
        expanded_radicals = set(name_radicals)
        for radical in list(name_radicals):
            if radical in synonym_map:
                expanded_radicals.update(synonym_map[radical])
        
        # 找出匹配的喜用字根
        xi_found = []
        for zg in xi_zigen:
            if zg in expanded_radicals:
                xi_found.append(zg)
            elif zg in synonym_map:
                # 检查同义字根
                if any(syn in expanded_radicals for syn in synonym_map[zg]):
                    xi_found.append(zg)
        
        # 找出匹配的忌用字根
        ji_found = []
        for zg in ji_zigen:
            if zg in expanded_radicals:
                ji_found.append(zg)
            elif zg in synonym_map:
                # 检查同义字根
                if any(syn in expanded_radicals for syn in synonym_map[zg]):
                    ji_found.append(zg)
        
        # 基础分
        base_score = 75
        
        # 每个喜用字根 +5分
        xi_bonus = len(xi_found) * 5
        
        # 每个忌用字根 -10分
        ji_penalty = len(ji_found) * 10
        
        # 计算最终分数
        final_score = base_score + xi_bonus - ji_penalty
        
        # 限制分数范围 50-100
        final_score = max(50, min(100, final_score))
        
        return {
            'score': final_score,
            'xi_count': len(xi_found),
            'ji_count': len(ji_found),
            'xi_found': xi_found,
            'ji_found': ji_found
        }
    
    def analyze_shengxiao(self, name: str, birth_dt: datetime) -> Dict:
        """生肖喜忌分析
        
        Args:
            name: 姓名
            birth_dt: 出生日期
            
        Returns:
            生肖分析结果字典，包含：
            - shengxiao: 生肖
            - xi_zigen: 喜用字根列表
            - ji_zigen: 忌用字根列表
            - score: 评分
            - xi_found: 找到的喜用字根
            - ji_found: 找到的忌用字根
            - comment: 生肖特性说明
            - analysis: 详细分析
        """
        logger.info(f"分析生肖喜忌: {name}, 出生日期: {birth_dt}")
        
        # 1. 确定生肖（农历年）
        shengxiao_idx = (birth_dt.year - 4) % 12
        shengxiao = self.SHENGXIAO[shengxiao_idx]
        
        # 2. 获取该生肖的喜忌数据
        if shengxiao not in self.shengxiao_data:
            logger.warning(f"未找到生肖数据: {shengxiao}")
            return {
                'shengxiao': shengxiao,
                'xi_zigen': [],
                'ji_zigen': [],
                'score': 75,
                'analysis': f'生肖{shengxiao}，暂无详细分析'
            }
        
        shengxiao_info = self.shengxiao_data[shengxiao]
        xi_zigen = shengxiao_info['xi_zigen']
        ji_zigen = shengxiao_info['ji_zigen']
        comment = shengxiao_info['comment']
        
        # 3. 提取姓名中的字根
        name_radicals = self._extract_radicals(name)
        
        # 4. 计算评分
        score_result = self._calculate_score(name_radicals, xi_zigen, ji_zigen)
        
        # 5. 生成分析文本
        analysis_parts = []
        
        # 生肖特性
        analysis_parts.append(f"生肖{shengxiao}：{comment}")
        
        # 喜用字根分析
        if score_result['xi_found']:
            xi_str = '、'.join(score_result['xi_found'])
            analysis_parts.append(f"[+] 姓名含喜用字根：{xi_str}")
        else:
            analysis_parts.append(f"[O] 姓名未含喜用字根")
        
        # 忌用字根分析
        if score_result['ji_found']:
            ji_str = '、'.join(score_result['ji_found'])
            analysis_parts.append(f"[-] 姓名含忌用字根：{ji_str}（建议避免）")
        else:
            analysis_parts.append(f"[+] 姓名未含忌用字根")
        
        # 综合评价
        score = score_result['score']
        if score >= 85:
            evaluation = "姓名与生肖十分相合，字根选择理想"
        elif score >= 75:
            evaluation = "姓名与生肖较为相合，字根选择适宜"
        elif score >= 65:
            evaluation = "姓名与生肖基本相合，字根选择尚可"
        else:
            evaluation = "姓名与生肖不够相合，建议调整字根"
        
        analysis_parts.append(f"评价：{evaluation}")
        
        return {
            'shengxiao': shengxiao,
            'xi_zigen': xi_zigen,
            'ji_zigen': ji_zigen,
            'xi_found': score_result['xi_found'],
            'ji_found': score_result['ji_found'],
            'score': score,
            'comment': comment,
            'analysis': '\n'.join(analysis_parts)
        }
