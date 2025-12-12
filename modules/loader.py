# -*- coding: utf-8 -*-
"""
加载模块 - 负责将依赖资源数据加载到数据库中
"""

import sqlite3
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataLoader:
    """数据加载管理类"""
    
    def __init__(self, db_path: str = 'local.db', data_dir: str = 'data'):
        """初始化加载模块"""
        self.db_path = db_path
        self.data_dir = Path(data_dir)
        self._init_resource_tables()
    
    def _init_resource_tables(self):
        """初始化资源表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 康熙字典笔画表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS kangxi_strokes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character TEXT NOT NULL UNIQUE,
                traditional TEXT,
                strokes INTEGER NOT NULL,
                pinyin TEXT,
                radical TEXT,
                bs_strokes INTEGER DEFAULT 0,
                ch_strokes INTEGER DEFAULT 0,
                luck TEXT,
                wuxing TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # 公司版：行业配置表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS industry_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                industry_code TEXT NOT NULL UNIQUE,
                industry_name TEXT NOT NULL,
                primary_wuxing TEXT,
                secondary_wuxing TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # 公司版：行业吉字符表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS industry_lucky_chars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                industry_code TEXT NOT NULL,
                character TEXT NOT NULL,
                char_wuxing TEXT,
                frequency INTEGER,
                score_bonus INTEGER,
                meaning TEXT,
                examples TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(industry_code, character)
            )
            ''')
            
            # 字义数据表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS character_meanings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character TEXT NOT NULL UNIQUE,
                pinyin TEXT NOT NULL,
                meaning TEXT NOT NULL,
                tone INTEGER,
                structure TEXT,
                radical TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 五行纳音对照表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS wuxing_nayin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ganzhi TEXT NOT NULL UNIQUE,
                nayin TEXT NOT NULL,
                wuxing TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 数理五行对照表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS shuli_wuxing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER NOT NULL UNIQUE,
                wuxing TEXT NOT NULL,
                jixiong TEXT NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 三才配置吉凶表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sancai_jixiong (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tian_wuxing TEXT NOT NULL,
                ren_wuxing TEXT NOT NULL,
                di_wuxing TEXT NOT NULL,
                jixiong TEXT NOT NULL,
                comment TEXT,
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tian_wuxing, ren_wuxing, di_wuxing)
            )
            ''')
            
            # 生肖喜忌表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS shengxiao_xiji (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shengxiao TEXT NOT NULL,
                xi_zigen TEXT NOT NULL,
                ji_zigen TEXT NOT NULL,
                xi_pianpang TEXT,
                ji_pianpang TEXT,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 称骨算命表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chenggu_fortune (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight REAL NOT NULL UNIQUE,
                fortune_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 称骨重量对照表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chenggu_weights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                value INTEGER NOT NULL,
                weight REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(type, value)
            )
            ''')
            
            # 万年历数据表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS wannianli (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gregorian_date DATE NOT NULL UNIQUE,
                lunar_date DATE,
                lunar_show TEXT,
                is_holiday BOOLEAN,
                lunar_festival TEXT,
                gregorian_festival TEXT,
                yi TEXT,
                ji TEXT,
                shen_wei TEXT,
                tai_shen TEXT,
                chong TEXT,
                sui_sha TEXT,
                wuxing_jiazi TEXT,
                wuxing_year TEXT,
                wuxing_month TEXT,
                wuxing_day TEXT,
                moon_phase TEXT,
                star_east TEXT,
                star_west TEXT,
                peng_zu TEXT,
                jian_shen TEXT,
                year_ganzhi TEXT NOT NULL,
                month_ganzhi TEXT NOT NULL,
                day_ganzhi TEXT NOT NULL,
                lunar_month_name TEXT,
                zodiac TEXT,
                lunar_month TEXT,
                lunar_day TEXT,
                solar_term TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 为万年历表创建索引以提高查询性能
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_wannianli_date 
            ON wannianli(gregorian_date)
            ''')
            
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_wannianli_ganzhi 
            ON wannianli(year_ganzhi, month_ganzhi, day_ganzhi)
            ''')
            
            # 数据加载记录表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_load_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT,
                record_count INTEGER,
                load_status TEXT NOT NULL,
                error_message TEXT,
                load_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
            logger.info("资源表初始化完成")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"资源表初始化失败: {e}")
            raise
        finally:
            conn.close()
    
    def load_all_resources(self, force_reload: bool = False) -> Dict:
        """加载所有资源"""
        result = {
            'success': True,
            'loaded': [],
            'failed': [],
            'statistics': {},
            'errors': []
        }
        
        resources = [
            ('kangxi', 'kangxi.json'),
            ('ziyi', 'ziyi.json'),
            ('nayin', 'nayin.json'),
            ('shuli', 'shuli_wuxing.json'),
            ('sancai', 'sancai.json'),
            ('shengxiao', 'shengxiao.json'),
            ('chenggu', 'chenggu.json'),
            ('wannianli', 'wannianli.json'),
            # 以下为公司版行业字库，作为外部资源登记加载记录，不入库
            ('industry_wuxing', 'industry_wuxing.json'),
            ('industry_lucky_chars', 'industry_lucky_chars.json')
        ]
        
        for resource_name, filename in resources:
            file_path = self.data_dir / filename
            
            if not file_path.exists():
                logger.warning(f"资源文件不存在: {file_path}")
                result['failed'].append(resource_name)
                result['errors'].append(f"{resource_name}: 文件不存在")
                continue
            
            try:
                load_result = self.load_resource(resource_name, str(file_path), force_reload)
                
                if load_result['success']:
                    result['loaded'].append(resource_name)
                    result['statistics'][resource_name] = {
                        'total': load_result['total'],
                        'success': load_result['success_count'],
                        'failed': load_result['failed_count']
                    }
                else:
                    result['failed'].append(resource_name)
                    result['errors'].extend(load_result.get('errors', []))
                    
            except Exception as e:
                logger.error(f"加载资源 {resource_name} 失败: {e}")
                result['failed'].append(resource_name)
                result['errors'].append(f"{resource_name}: {str(e)}")
        
        result['success'] = len(result['failed']) == 0
        return result
    
    def load_resource(self, resource_name: str, file_path: str, 
                     force_reload: bool = False) -> Dict:
        """加载单个资源"""
        logger.info(f"开始加载资源: {resource_name}")
        
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 计算文件哈希
            file_hash = self._calculate_file_hash(file_path)
            
            # 检查是否需要重新加载
            if not force_reload and self._is_loaded(resource_name, file_hash):
                logger.info(f"资源 {resource_name} 已是最新版本，跳过加载")
                return {
                    'success': True,
                    'total': 0,
                    'success_count': 0,
                    'failed_count': 0
                }
            
            # 公司版行业资源：特殊处理（导入到行业表）
            if resource_name in ('industry_wuxing', 'industry_lucky_chars'):
                import_result = self._import_data(resource_name, data)
                validation = {
                    'valid': True,
                    'total': import_result.get('count', 0),
                    'passed': import_result.get('count', 0),
                    'failed': 0
                }
                # 记录加载历史
                self._record_load_history(
                    resource_name, file_path, file_hash,
                    import_result['count'], 'success' if import_result['success'] else 'failed'
                )
                return {
                    'success': import_result['success'],
                    'total': validation['total'],
                    'success_count': import_result['count'],
                    'failed_count': validation['failed']
                }

            # 称骨数据特殊处理
            if resource_name == 'chenggu':
                # 称骨数据直接传递整个对象
                import_result = self._import_data(resource_name, data)
                validation = {
                    'valid': True,
                    'total': import_result.get('count', 0),
                    'passed': import_result.get('count', 0),
                    'failed': 0
                }
            else:
                # 验证数据
                validation = self.validate_resource_data(resource_name, data.get('data', []))
                
                if not validation['valid']:
                    logger.error(f"资源 {resource_name} 验证失败")
                    return {
                        'success': False,
                        'errors': validation['errors']
                    }
                
                # 导入数据
                import_result = self._import_data(resource_name, data.get('data', []))
            
            # 记录加载历史
            self._record_load_history(
                resource_name, file_path, file_hash,
                import_result['count'], 'success' if import_result['success'] else 'failed'
            )
            
            return {
                'success': import_result['success'],
                'total': validation['total'],
                'success_count': import_result['count'],
                'failed_count': validation['failed']
            }
            
        except Exception as e:
            logger.exception(f"加载资源 {resource_name} 出错: {e}")
            return {
                'success': False,
                'errors': [str(e)]
            }
    
    def validate_resource_data(self, resource_name: str, data: List) -> Dict:
        """验证资源数据"""
        result = {
            'valid': True,
            'total': len(data),
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        
        for idx, item in enumerate(data):
            try:
                if resource_name == 'kangxi':
                    self._validate_kangxi(item)
                elif resource_name == 'ziyi':
                    self._validate_ziyi(item)
                elif resource_name == 'wannianli':
                    self._validate_wannianli(item)
                # 添加其他资源的验证...
                
                result['passed'] += 1
                
            except ValueError as e:
                result['failed'] += 1
                result['errors'].append({
                    'index': idx,
                    'reason': str(e)
                })
        
        result['valid'] = result['failed'] == 0
        return result
    
    def _validate_kangxi(self, item: Dict):
        """验证康熙字典数据"""
        if 'character' not in item or len(item['character']) != 1:
            raise ValueError("字符必须为单个汉字")
        if 'strokes' not in item or not (1 <= item['strokes'] <= 64):
            raise ValueError("笔画数范围: 1-64")
        if 'pinyin' not in item or not item['pinyin']:
            raise ValueError("拼音不能为空")
    
    def _validate_ziyi(self, item: Dict):
        """验证字义数据"""
        if 'character' not in item or len(item['character']) != 1:
            raise ValueError("字符必须为单个汉字")
        if 'pinyin' not in item or not item['pinyin']:
            raise ValueError("拼音不能为空")
        if 'meaning' not in item or not item['meaning']:
            raise ValueError("字义不能为空")
    
    def _validate_wannianli(self, item: Dict):
        """验证万年历数据"""
        if 'gregorian_date' not in item or not item['gregorian_date']:
            raise ValueError("公历日期不能为空")
        if 'year_ganzhi' not in item or not item['year_ganzhi']:
            raise ValueError("年干支不能为空")
        if 'month_ganzhi' not in item or not item['month_ganzhi']:
            raise ValueError("月干支不能为空")
        if 'day_ganzhi' not in item or not item['day_ganzhi']:
            raise ValueError("日干支不能为空")
    
    def _import_data(self, resource_name: str, data) -> Dict:
        """导入数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        count = 0
        
        try:
            if resource_name == 'kangxi':
                for item in data:
                    cursor.execute('''
                    INSERT OR REPLACE INTO kangxi_strokes 
                    (character, traditional, strokes, pinyin, radical, bs_strokes, ch_strokes, luck, wuxing)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item['character'],
                        item.get('traditional', item['character']),
                        item['strokes'],
                        item.get('pinyin', ''),
                        item.get('radical', ''),
                        item.get('bs_strokes', 0),
                        item.get('ch_strokes', 0),
                        item.get('luck', ''),
                        item.get('wuxing', '')
                    ))
                    count += 1
            
            elif resource_name == 'ziyi':
                for item in data:
                    cursor.execute('''
                    INSERT OR REPLACE INTO character_meanings
                    (character, pinyin, meaning, tone, structure, radical)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        item['character'],
                        item['pinyin'],
                        item['meaning'],
                        item.get('tones', [0])[0] if item.get('tones') else 0,
                        item.get('structure', ''),
                        item.get('bushou', '')
                    ))
                    count += 1
            
            elif resource_name == 'nayin':
                for item in data:
                    cursor.execute('''
                    INSERT OR REPLACE INTO wuxing_nayin
                    (ganzhi, nayin, wuxing)
                    VALUES (?, ?, ?)
                    ''', (
                        item['ganzhi'],
                        item['nayin'],
                        item['wuxing']
                    ))
                    count += 1
            
            elif resource_name == 'shuli':
                for item in data:
                    cursor.execute('''
                    INSERT OR REPLACE INTO shuli_wuxing
                    (number, wuxing, jixiong, comment)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        item['number'],
                        item['wuxing'],
                        item.get('jixiong', ''),
                        item.get('comment', '')
                    ))
                    count += 1
            
            elif resource_name == 'sancai':
                for item in data:
                    # 从 "木木木" 格式拆分出天人地三才
                    sancai_str = item.get('sancai', '')
                    if len(sancai_str) == 3:
                        tian, ren, di = sancai_str[0], sancai_str[1], sancai_str[2]
                    else:
                        tian = item.get('tian', '')
                        ren = item.get('ren', '')
                        di = item.get('di', '')
                    
                    cursor.execute('''
                    INSERT OR REPLACE INTO sancai_jixiong
                    (tian_wuxing, ren_wuxing, di_wuxing, jixiong, comment, score)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        tian,
                        ren,
                        di,
                        item['jixiong'],
                        item.get('comment', ''),
                        item.get('score', 50)
                    ))
                    count += 1
            
            elif resource_name == 'shengxiao':
                for item in data:
                    # 将列表转换为逗号分隔的字符串
                    xi_zigen = item.get('xi_zigen', [])
                    ji_zigen = item.get('ji_zigen', [])
                    xi_pianpang = item.get('xi_pianpang', [])
                    ji_pianpang = item.get('ji_pianpang', [])
                    
                    cursor.execute('''
                    INSERT OR REPLACE INTO shengxiao_xiji
                    (shengxiao, xi_zigen, ji_zigen, xi_pianpang, ji_pianpang, comment)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        item['shengxiao'],
                        ','.join(xi_zigen) if isinstance(xi_zigen, list) else xi_zigen,
                        ','.join(ji_zigen) if isinstance(ji_zigen, list) else ji_zigen,
                        ','.join(xi_pianpang) if isinstance(xi_pianpang, list) else xi_pianpang,
                        ','.join(ji_pianpang) if isinstance(ji_pianpang, list) else ji_pianpang,
                        item.get('comment', '')
                    ))
                    count += 1
            
            elif resource_name == 'chenggu':
                # 处理骨重数据
                if 'weights' in data:
                    weights = data['weights']
                    # 处理年份骨重
                    if 'year' in weights:
                        for year_str, weight in weights['year'].items():
                            cursor.execute('''
                            INSERT OR REPLACE INTO chenggu_weights
                            (type, value, weight)
                            VALUES (?, ?, ?)
                            ''', ('year', int(year_str), float(weight)))
                            count += 1
                    
                    # 处理月份骨重
                    if 'month' in weights:
                        for month_str, weight in weights['month'].items():
                            cursor.execute('''
                            INSERT OR REPLACE INTO chenggu_weights
                            (type, value, weight)
                            VALUES (?, ?, ?)
                            ''', ('month', int(month_str), float(weight)))
                            count += 1
                    
                    # 处理日期骨重
                    if 'day' in weights:
                        for day_str, weight in weights['day'].items():
                            cursor.execute('''
                            INSERT OR REPLACE INTO chenggu_weights
                            (type, value, weight)
                            VALUES (?, ?, ?)
                            ''', ('day', int(day_str), float(weight)))
                            count += 1
                    
                    # 处理时辰骨重（需要转换时辰名称为序号）
                    if 'hour' in weights:
                        shichen_map = {
                            '子': 0, '丑': 1, '寅': 2, '卯': 3,
                            '辰': 4, '巳': 5, '午': 6, '未': 7,
                            '申': 8, '酉': 9, '戌': 10, '亥': 11
                        }
                        for shichen_name, weight in weights['hour'].items():
                            if shichen_name in shichen_map:
                                cursor.execute('''
                                INSERT OR REPLACE INTO chenggu_weights
                                (type, value, weight)
                                VALUES (?, ?, ?)
                                ''', ('hour', shichen_map[shichen_name], float(weight)))
                                count += 1
                
                # 处理命格数据
                if 'fortunes' in data:
                    for fortune in data['fortunes']:
                        # 使用平均值作为骨重
                        avg_weight = (fortune['min_weight'] + fortune['max_weight']) / 2
                        cursor.execute('''
                        INSERT OR REPLACE INTO chenggu_fortune
                        (weight, fortune_text)
                        VALUES (?, ?)
                        ''', (avg_weight, fortune['text']))
                        count += 1
            
            elif resource_name == 'wannianli':
                # 批量导入万年历数据以提高性能
                batch_size = 1000
                batch_data = []
                
                for item in data:
                    # 提取日期（去掉时间部分）
                    gregorian_date = item['gregorian_date'].split(' ')[0] if ' ' in item['gregorian_date'] else item['gregorian_date']
                    lunar_date = item.get('lunar_date', '').split(' ')[0] if item.get('lunar_date') and ' ' in item.get('lunar_date', '') else item.get('lunar_date', '')
                    
                    batch_data.append((
                        gregorian_date,
                        lunar_date,
                        item.get('lunar_show', ''),
                        item.get('is_holiday', False),
                        item.get('lunar_festival', ''),
                        item.get('gregorian_festival', ''),
                        item.get('yi', ''),
                        item.get('ji', ''),
                        item.get('shen_wei', ''),
                        item.get('tai_shen', ''),
                        item.get('chong', ''),
                        item.get('sui_sha', ''),
                        item.get('wuxing_jiazi', ''),
                        item.get('wuxing_year', ''),
                        item.get('wuxing_month', ''),
                        item.get('wuxing_day', ''),
                        item.get('moon_phase', ''),
                        item.get('star_east', ''),
                        item.get('star_west', ''),
                        item.get('peng_zu', ''),
                        item.get('jian_shen', ''),
                        item['year_ganzhi'],
                        item['month_ganzhi'],
                        item['day_ganzhi'],
                        item.get('lunar_month_name', ''),
                        item.get('zodiac', ''),
                        item.get('lunar_month', ''),
                        item.get('lunar_day', ''),
                        item.get('solar_term', '')
                    ))
                    
                    count += 1
                    
                    # 每批次提交一次
                    if len(batch_data) >= batch_size:
                        cursor.executemany('''
                        INSERT OR REPLACE INTO wannianli (
                            gregorian_date, lunar_date, lunar_show, is_holiday,
                            lunar_festival, gregorian_festival, yi, ji,
                            shen_wei, tai_shen, chong, sui_sha,
                            wuxing_jiazi, wuxing_year, wuxing_month, wuxing_day,
                            moon_phase, star_east, star_west, peng_zu, jian_shen,
                            year_ganzhi, month_ganzhi, day_ganzhi,
                            lunar_month_name, zodiac, lunar_month, lunar_day, solar_term
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', batch_data)
                        conn.commit()
                        logger.info(f"已导入 {count} 条万年历记录...")
                        batch_data = []
                
                # 提交剩余数据
                if batch_data:
                    cursor.executemany('''
                    INSERT OR REPLACE INTO wannianli (
                        gregorian_date, lunar_date, lunar_show, is_holiday,
                        lunar_festival, gregorian_festival, yi, ji,
                        shen_wei, tai_shen, chong, sui_sha,
                        wuxing_jiazi, wuxing_year, wuxing_month, wuxing_day,
                        moon_phase, star_east, star_west, peng_zu, jian_shen,
                        year_ganzhi, month_ganzhi, day_ganzhi,
                        lunar_month_name, zodiac, lunar_month, lunar_day, solar_term
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', batch_data)
            
            elif resource_name == 'industry_wuxing':
                # data 是 {industry_code: {industry_name, primary_wuxing, secondary_wuxing}}
                for code, info in (data or {}).items():
                    cursor.execute('''
                    INSERT OR REPLACE INTO industry_config
                    (industry_code, industry_name, primary_wuxing, secondary_wuxing)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        code,
                        info.get('industry_name', code),
                        info.get('primary_wuxing', ''),
                        info.get('secondary_wuxing', '')
                    ))
                    count += 1

            elif resource_name == 'industry_lucky_chars':
                # data 是 {industry_code: {char: {char_wuxing, frequency, score_bonus, meaning, examples}}}
                for code, chars in (data or {}).items():
                    for ch, meta in (chars or {}).items():
                        examples = meta.get('examples', [])
                        cursor.execute('''
                        INSERT OR REPLACE INTO industry_lucky_chars
                        (industry_code, character, char_wuxing, frequency, score_bonus, meaning, examples)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            code,
                            ch,
                            meta.get('char_wuxing', ''),
                            int(meta.get('frequency', 0)) if meta.get('frequency') is not None else None,
                            int(meta.get('score_bonus', 0)) if meta.get('score_bonus') is not None else None,
                            meta.get('meaning', ''),
                            json.dumps(examples, ensure_ascii=False) if isinstance(examples, list) else str(examples)
                        ))
                        count += 1
            
            conn.commit()
            logger.info(f"成功导入 {count} 条记录到 {resource_name}")
            return {'success': True, 'count': count}
            
        except Exception as e:
            conn.rollback()
            logger.error(f"导入数据失败: {e}")
            return {'success': False, 'count': 0}
        finally:
            conn.close()
    
    def check_resource_integrity(self) -> Dict:
        """检查资源完整性"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        result = {
            'complete': True,
            'missing_resources': [],
            'empty_tables': []
        }
        
        tables = [
            'kangxi_strokes',
            'character_meanings',
            'wuxing_nayin',
            'shuli_wuxing',
            'sancai_jixiong',
            'shengxiao_xiji',
            'chenggu_fortune',
            'chenggu_weights',
            'wannianli'
        ]
        
        try:
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                if count == 0:
                    result['empty_tables'].append(table)
                    result['complete'] = False
        
        finally:
            conn.close()
        
        return result
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    
    def _is_loaded(self, resource_name: str, file_hash: str) -> bool:
        """检查资源是否已加载"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT COUNT(*) FROM data_load_records
            WHERE resource_name=? AND file_hash=? AND load_status='success'
            ORDER BY load_time DESC LIMIT 1
            ''', (resource_name, file_hash))
            
            return cursor.fetchone()[0] > 0
        finally:
            conn.close()
    
    def _record_load_history(self, resource_name: str, file_path: str,
                            file_hash: str, record_count: int, status: str):
        """记录加载历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO data_load_records
            (resource_name, file_path, file_hash, record_count, load_status)
            VALUES (?, ?, ?, ?, ?)
            ''', (resource_name, file_path, file_hash, record_count, status))
            conn.commit()
        finally:
            conn.close()
