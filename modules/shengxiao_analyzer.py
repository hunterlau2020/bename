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
        
        # 生肖五行和三合关系
        self.SHENGXIAO_WUXING = {
            '鼠': {'wuxing': '水', 'sanhe': ['龙', '猴'], 'liuhe': '牛'},
            '牛': {'wuxing': '土', 'sanhe': ['蛇', '鸡'], 'liuhe': '鼠'},
            '虎': {'wuxing': '木', 'sanhe': ['马', '狗'], 'liuhe': '猪'},
            '兔': {'wuxing': '木', 'sanhe': ['羊', '猪'], 'liuhe': '狗'},
            '龙': {'wuxing': '土', 'sanhe': ['鼠', '猴'], 'liuhe': '鸡'},
            '蛇': {'wuxing': '火', 'sanhe': ['牛', '鸡'], 'liuhe': '猴'},
            '马': {'wuxing': '火', 'sanhe': ['虎', '狗'], 'liuhe': '羊'},
            '羊': {'wuxing': '土', 'sanhe': ['兔', '猪'], 'liuhe': '马'},
            '猴': {'wuxing': '金', 'sanhe': ['鼠', '龙'], 'liuhe': '蛇'},
            '鸡': {'wuxing': '金', 'sanhe': ['牛', '蛇'], 'liuhe': '龙'},
            '狗': {'wuxing': '土', 'sanhe': ['虎', '马'], 'liuhe': '兔'},
            '猪': {'wuxing': '水', 'sanhe': ['兔', '羊'], 'liuhe': '虎'},
        }
        
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
    
    def _get_shengxiao_from_wannianli(self, birth_date: str) -> str:
        """从万年历数据库查询生肖
        
        Args:
            birth_date: 出生日期，格式如 '1990-05-15'
            
        Returns:
            生肖名称，如 '马'
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT zodiac FROM wannianli WHERE gregorian_date = ?
            """, (birth_date,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                return row[0]
        except Exception as e:
            logger.warning(f"从万年历查询生肖失败: {e}")
        
        return ''
    
    def _get_char_wuxing(self, char: str) -> str:
        """从康熙字典数据库获取字的五行
        
        Args:
            char: 汉字
            
        Returns:
            五行属性（木、火、土、金、水）
        """
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT wuxing FROM kangxi_strokes WHERE character = ?
            """, (char,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                return row[0]
        except Exception as e:
            logger.debug(f"查询五行失败: {e}")
        
        return ''
    
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
    
    def _check_wuxing_relation(self, char_wuxing: str, shengxiao_wuxing: str) -> tuple:
        """检查字的五行与生肖五行的关系
        
        Args:
            char_wuxing: 字的五行
            shengxiao_wuxing: 生肖五行
            
        Returns:
            (关系类型, 分数加减, 说明文字)
            关系类型: 'sheng'(相生), 'ke'(相克), 'same'(同类), 'other'(其他)
        """
        # 五行相生关系：木生火、火生土、土生金、金生水、水生木
        sheng_map = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }
        
        # 五行相克关系：木克土、土克水、水克火、火克金、金克木
        ke_map = {
            '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
        }
        
        if not char_wuxing or not shengxiao_wuxing:
            return ('other', 0, '未知')
        
        # 同类五行
        if char_wuxing == shengxiao_wuxing:
            return ('same', 2, f'{char_wuxing}(同类扶持)')
        
        # 相生关系（字生生肖）
        if sheng_map.get(char_wuxing) == shengxiao_wuxing:
            return ('sheng', 3, f'{char_wuxing}生{shengxiao_wuxing}(相生助力)')
        
        # 被生关系（生肖生字）
        if sheng_map.get(shengxiao_wuxing) == char_wuxing:
            return ('bei_sheng', 1, f'{shengxiao_wuxing}生{char_wuxing}(耗泄)')
        
        # 相克关系（字克生肖）
        if ke_map.get(char_wuxing) == shengxiao_wuxing:
            return ('ke', -5, f'{char_wuxing}克{shengxiao_wuxing}(相克不利)')
        
        # 被克关系（生肖克字）
        if ke_map.get(shengxiao_wuxing) == char_wuxing:
            return ('bei_ke', -2, f'{shengxiao_wuxing}克{char_wuxing}(受克)')
        
        return ('other', 0, f'{char_wuxing}(无明显关系)')
    
    def _calculate_score(self, name_radicals: Set[str], xi_zigen: List[str], 
                        ji_zigen: List[str], sanhe_bonus: int = 0) -> Dict:
        """计算生肖喜忌评分
        
        Args:
            name_radicals: 姓名中的字根
            xi_zigen: 喜用字根列表
            ji_zigen: 忌用字根列表
            sanhe_bonus: 三合关系加分
            
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
        final_score = base_score + xi_bonus - ji_penalty + sanhe_bonus
        
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
            - wuxing: 生肖五行
            - sanhe: 三合生肖列表
            - liuhe: 六合生肖
            - xi_zigen: 喜用字根列表
            - ji_zigen: 忌用字根列表
            - score: 评分
            - xi_found: 找到的喜用字根
            - ji_found: 找到的忌用字根
            - sanhe_found: 找到的三合生肖字
            - comment: 生肖特性说明
            - analysis: 详细分析
        """
        logger.info(f"分析生肖喜忌: {name}, 出生日期: {birth_dt}")
        
        # 1. 从万年历确定生肖（使用公历日期查询）
        birth_date_str = birth_dt.strftime('%Y-%m-%d')
        shengxiao = self._get_shengxiao_from_wannianli(birth_date_str)
        
        # 如果万年历查询失败，使用传统算法（公历年减4再模12）
        if not shengxiao:
            logger.warning(f"万年历未找到 {birth_date_str}，使用传统算法")
            shengxiao_idx = (birth_dt.year - 4) % 12
            shengxiao = self.SHENGXIAO[shengxiao_idx]
        
        # 2. 获取生肖的五行和三合信息
        shengxiao_attrs = self.SHENGXIAO_WUXING.get(shengxiao, {
            'wuxing': '未知',
            'sanhe': [],
            'liuhe': ''
        })
        wuxing = shengxiao_attrs['wuxing']
        sanhe = shengxiao_attrs['sanhe']
        liuhe = shengxiao_attrs['liuhe']
        
        # 3. 获取该生肖的喜忌数据
        if shengxiao not in self.shengxiao_data:
            logger.warning(f"未找到生肖数据: {shengxiao}")
            return {
                'shengxiao': shengxiao,
                'wuxing': wuxing,
                'sanhe': sanhe,
                'liuhe': liuhe,
                'xi_zigen': [],
                'ji_zigen': [],
                'score': 75,
                'analysis': f'生肖{shengxiao}，五行属{wuxing}，暂无详细分析'
            }
        
        shengxiao_info = self.shengxiao_data[shengxiao]
        xi_zigen = shengxiao_info['xi_zigen']
        ji_zigen = shengxiao_info['ji_zigen']
        comment = shengxiao_info['comment']
        
        # 4. 提取姓名中的字根
        name_radicals = self._extract_radicals(name)
        
        # 5. 分析姓名中每个字的五行与生肖五行的关系
        wuxing_details = []
        wuxing_bonus = 0
        for char in name:
            char_wuxing = self._get_char_wuxing(char)
            if char_wuxing:
                relation_type, score_change, description = self._check_wuxing_relation(char_wuxing, wuxing)
                wuxing_details.append({
                    'char': char,
                    'wuxing': char_wuxing,
                    'relation': relation_type,
                    'score_change': score_change,
                    'description': description
                })
                wuxing_bonus += score_change
        
        # 6. 检查姓名中是否包含三合生肖字
        sanhe_found = []
        sanhe_bonus = 0
        for char in name:
            if char in sanhe:
                sanhe_found.append(char)
                sanhe_bonus += 3  # 每个三合生肖字加3分
            elif char == liuhe:
                sanhe_found.append(f"{char}(六合)")
                sanhe_bonus += 5  # 六合生肖字加5分
        
        # 7. 计算评分（包含五行加分）
        total_bonus = sanhe_bonus + wuxing_bonus
        score_result = self._calculate_score(name_radicals, xi_zigen, ji_zigen, total_bonus)
        
        # 8. 生成分析文本和计算过程
        analysis_parts = []
        calculation_steps = []  # 详细计算步骤
        
        # 生肖基本信息
        sanhe_str = '、'.join(sanhe)
        analysis_parts.append(f"生肖{shengxiao}：五行属{wuxing}，三合生肖为{sanhe_str}，六合生肖为{liuhe}")
        analysis_parts.append(f"特性：{comment}")
        
        # 计算步骤1: 基础分
        calculation_steps.append({
            'step': '基础分',
            'value': 75,
            'description': '生肖分析基础分'
        })
        
        # 五行分析
        if wuxing_details:
            wuxing_lines = []
            for detail in wuxing_details:
                wuxing_lines.append(f"{detail['char']}({detail['description']})")
            wuxing_str = '、'.join(wuxing_lines)
            if wuxing_bonus > 0:
                analysis_parts.append(f"[+] 姓名五行：{wuxing_str}")
            elif wuxing_bonus < 0:
                analysis_parts.append(f"[-] 姓名五行：{wuxing_str}")
            else:
                analysis_parts.append(f"[O] 姓名五行：{wuxing_str}")
            
            # 计算步骤2: 五行加减分
            if wuxing_bonus != 0:
                calculation_steps.append({
                    'step': '五行关系',
                    'value': wuxing_bonus,
                    'description': f'五行相生相克: {wuxing_bonus:+d}分',
                    'details': wuxing_details
                })
        
        # 三合关系分析
        if sanhe_found:
            sanhe_str = '、'.join(sanhe_found)
            analysis_parts.append(f"[+] 姓名含三合/六合生肖字：{sanhe_str}（增强运势）")
            # 计算步骤3: 三合加分
            calculation_steps.append({
                'step': '三合/六合',
                'value': sanhe_bonus,
                'description': f'三合/六合生肖字: +{sanhe_bonus}分',
                'details': sanhe_found
            })
        
        # 喜用字根分析
        if score_result['xi_found']:
            xi_str = '、'.join(score_result['xi_found'])
            analysis_parts.append(f"[+] 姓名含喜用字根：{xi_str}")
            # 计算步骤4: 喜用字根加分
            xi_bonus = len(score_result['xi_found']) * 5
            calculation_steps.append({
                'step': '喜用字根',
                'value': xi_bonus,
                'description': f"喜用字根{len(score_result['xi_found'])}个: +{xi_bonus}分",
                'details': score_result['xi_found']
            })
        else:
            analysis_parts.append(f"[O] 姓名未含喜用字根")
        
        # 忌用字根分析
        if score_result['ji_found']:
            ji_str = '、'.join(score_result['ji_found'])
            analysis_parts.append(f"[-] 姓名含忌用字根：{ji_str}（建议避免）")
            # 计算步骤5: 忌用字根扣分
            ji_penalty = len(score_result['ji_found']) * 10
            calculation_steps.append({
                'step': '忌用字根',
                'value': -ji_penalty,
                'description': f"忌用字根{len(score_result['ji_found'])}个: -{ji_penalty}分",
                'details': score_result['ji_found']
            })
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
        
        # 计算步骤6: 最终得分
        calculation_steps.append({
            'step': '最终得分',
            'value': score,
            'description': f'总分: {score}分 (限制在50-100之间)',
            'evaluation': evaluation
        })
        
        analysis_parts.append(f"评价：{evaluation}")
        
        # 生成计算过程说明
        calculation_summary = f"基础分75"
        if wuxing_bonus != 0:
            calculation_summary += f" {wuxing_bonus:+d}(五行)"
        if sanhe_bonus > 0:
            calculation_summary += f" +{sanhe_bonus}(三合)"
        if score_result['xi_found']:
            calculation_summary += f" +{len(score_result['xi_found'])*5}(喜用)"
        if score_result['ji_found']:
            calculation_summary += f" -{len(score_result['ji_found'])*10}(忌用)"
        calculation_summary += f" = {score}分"
        
        # 9. 生成建议的喜忌五行和生肖
        # 五行相生关系：木生火、火生土、土生金、金生水、水生木
        sheng_map = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }
        # 五行相克关系：木克土、土克水、水克火、火克金、金克木
        ke_map = {
            '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
        }
        
        # 建议喜用五行：生肖五行、生生肖的五行
        recommended_xi_wuxing = [wuxing]  # 同类五行
        for wx, sheng_wx in sheng_map.items():
            if sheng_wx == wuxing:  # 找到生生肖五行的五行
                if wx not in recommended_xi_wuxing:
                    recommended_xi_wuxing.append(wx)
        
        # 建议忌用五行：克生肖的五行、被生肖克的五行
        recommended_ji_wuxing = []
        for wx, ke_wx in ke_map.items():
            if ke_wx == wuxing:  # 找到克生肖的五行
                recommended_ji_wuxing.append(wx)
        if sheng_map.get(wuxing):  # 生肖生的五行（耗泄）
            recommended_ji_wuxing.append(sheng_map[wuxing])
        
        # 建议喜用生肖：三合、六合
        recommended_xi_shengxiao = list(sanhe) + [liuhe]
        
        # 建议忌用生肖：从注释中提取（如果有）
        recommended_ji_shengxiao = []
        # 根据传统理论，相冲的生肖（相差6位）
        chong_map = {
            '鼠': '马', '牛': '羊', '虎': '猴', '兔': '鸡', '龙': '狗', '蛇': '猪',
            '马': '鼠', '羊': '牛', '猴': '虎', '鸡': '兔', '狗': '龙', '猪': '蛇'
        }
        if shengxiao in chong_map:
            recommended_ji_shengxiao.append(chong_map[shengxiao])
        
        logger.info(f"生肖分析完成: {shengxiao}({wuxing}) {calculation_summary}")
        
        return {
            'shengxiao': shengxiao,
            'wuxing': wuxing,
            'sanhe': sanhe,
            'liuhe': liuhe,
            'xi_zigen': xi_zigen,
            'ji_zigen': ji_zigen,
            'xi_found': score_result['xi_found'],
            'ji_found': score_result['ji_found'],
            'sanhe_found': sanhe_found,
            'wuxing_details': wuxing_details,
            'score': score,
            'comment': comment,
            'analysis': '\n'.join(analysis_parts),
            'calculation_steps': calculation_steps,
            'calculation_summary': calculation_summary,
            'recommended_xi_wuxing': recommended_xi_wuxing,  # 新增：建议喜用五行
            'recommended_ji_wuxing': recommended_ji_wuxing,  # 新增：建议忌用五行
            'recommended_xi_shengxiao': recommended_xi_shengxiao,  # 新增：建议喜用生肖
            'recommended_ji_shengxiao': recommended_ji_shengxiao  # 新增：建议忌用生肖
        }
