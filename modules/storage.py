# -*- coding: utf-8 -*-
"""
存储模块 - 管理姓名测试结果的持久化存储
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class Storage:
    """数据存储管理类"""
    
    def __init__(self, db_path: str = 'local.db'):
        """初始化存储模块"""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 创建测试记录主表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT NOT NULL,
                birth_time TEXT NOT NULL,
                longitude REAL NOT NULL,
                latitude REAL NOT NULL,
                comprehensive_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, birth_time, longitude, latitude)
            )
            ''')
            
            # 创建三才五格结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS wuge_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                tiange_num INTEGER,
                tiange_element TEXT,
                tiange_fortune TEXT,
                renge_num INTEGER,
                renge_element TEXT,
                renge_fortune TEXT,
                dige_num INTEGER,
                dige_element TEXT,
                dige_fortune TEXT,
                waige_num INTEGER,
                waige_element TEXT,
                waige_fortune TEXT,
                zongge_num INTEGER,
                zongge_element TEXT,
                zongge_fortune TEXT,
                sancai TEXT,
                score INTEGER,
                FOREIGN KEY (record_id) REFERENCES test_records(id)
            )
            ''')
            
            # 创建八字结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS bazi_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                bazi_str TEXT,
                wuxing TEXT,
                nayin TEXT,
                wuxing_geshu TEXT,
                wuxing_strength TEXT,
                tongyi_elements TEXT,
                tongyi_strength INTEGER,
                tongyi_percent REAL,
                yilei_elements TEXT,
                yilei_strength INTEGER,
                yilei_percent REAL,
                rizhu_qiangruo TEXT,
                siji_yongshen TEXT,
                xiyong_shen TEXT,
                ji_shen TEXT,
                jixiang_color TEXT,
                score INTEGER,
                FOREIGN KEY (record_id) REFERENCES test_records(id)
            )
            ''')
            
            # 创建字义音形结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ziyi_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                analysis TEXT,
                score INTEGER,
                FOREIGN KEY (record_id) REFERENCES test_records(id)
            )
            ''')
            
            # 创建生肖结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS shengxiao_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                shengxiao TEXT,
                xi_zigen TEXT,
                ji_zigen TEXT,
                score INTEGER,
                FOREIGN KEY (record_id) REFERENCES test_records(id)
            )
            ''')
            
            # 创建称骨结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS chenggu_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                bone_weight REAL NOT NULL,
                fortune_text TEXT,
                comment TEXT,
                FOREIGN KEY (record_id) REFERENCES test_records(id)
            )
            ''')
            
            conn.commit()
            
            # 检查并迁移表结构
            self._migrate_database(cursor)
            conn.commit()
            
            logger.info("数据库初始化完成")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库初始化失败: {e}")
            raise
        finally:
            conn.close()
    
    def _migrate_database(self, cursor):
        """迁移数据库表结构（添加新字段）"""
        try:
            # 检查 bazi_results 表是否有新字段
            cursor.execute("PRAGMA table_info(bazi_results)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # 添加缺失的字段
            new_columns = [
                ('wuxing_strength', 'TEXT'),
                ('tongyi_elements', 'TEXT'),
                ('tongyi_strength', 'INTEGER'),
                ('tongyi_percent', 'REAL'),
                ('yilei_elements', 'TEXT'),
                ('yilei_strength', 'INTEGER'),
                ('yilei_percent', 'REAL')
            ]
            
            for col_name, col_type in new_columns:
                if col_name not in columns:
                    logger.info(f"添加字段: bazi_results.{col_name}")
                    cursor.execute(f"ALTER TABLE bazi_results ADD COLUMN {col_name} {col_type}")
            
            # 创建公司版相关表（若不存在）
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_test_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                prefix TEXT,
                main_name TEXT,
                industry_suffix TEXT,
                industry_code TEXT,
                org_form TEXT,
                industry_type TEXT,
                owner_name TEXT,
                owner_gender TEXT,
                owner_birth_time TEXT,
                owner_longitude REAL,
                owner_latitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(full_name, owner_name, owner_birth_time, owner_longitude, owner_latitude)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                wuge_score INTEGER,
                industry_score INTEGER,
                bazi_match_score INTEGER,
                xiyong_match_score INTEGER,
                shengxiao_score INTEGER,
                ziyi_score INTEGER,
                total_score INTEGER,
                grade TEXT,
                FOREIGN KEY (record_id) REFERENCES company_test_records(id)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_industry_detail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER NOT NULL,
                detail_json TEXT NOT NULL,
                FOREIGN KEY (record_id) REFERENCES company_test_records(id)
            )
            ''')

            # SRD: 公司五格结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_wuge_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                surname TEXT,
                given_name TEXT,
                test_id INTEGER NOT NULL,
                tiange INTEGER, tiange_element TEXT, tiange_meaning TEXT,
                renge INTEGER, renge_element TEXT, renge_meaning TEXT,
                dige INTEGER, dige_element TEXT, dige_meaning TEXT,
                waige INTEGER, waige_element TEXT, waige_meaning TEXT,
                zongge INTEGER, zongge_element TEXT, zongge_meaning TEXT,
                sancai TEXT,
                sancai_meaning TEXT,
                wuge_score INTEGER,
                plan TEXT,
                FOREIGN KEY (test_id) REFERENCES company_test_records(id)
            )
            ''')

            # SRD: 公司行业特性分析表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_industry_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                industry_type TEXT,
                industry_wuxing TEXT,
                name_wuxing_dist TEXT,
                wuxing_match_score INTEGER,
                xiyong_match_score INTEGER,
                lucky_chars TEXT,
                lucky_char_score INTEGER,
                total_score INTEGER,
                suggestions TEXT,
                FOREIGN KEY (test_id) REFERENCES company_test_records(id)
            )
            ''')

            # 公司版：生肖分析结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_shengxiao_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                shengxiao TEXT,
                wuxing TEXT,
                sanhe TEXT,
                liuhe TEXT,
                xi_found TEXT,
                ji_found TEXT,
                wuxing_details TEXT,
                sanhe_found TEXT,
                score INTEGER,
                analysis TEXT,
                calculation_summary TEXT,
                calculation_steps TEXT,
                recommended_xi_wuxing TEXT,
                recommended_ji_wuxing TEXT,
                recommended_xi_shengxiao TEXT,
                recommended_ji_shengxiao TEXT,
                FOREIGN KEY (test_id) REFERENCES company_test_records(id)
            )
            ''')

            # 公司版：字义音形分析结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS company_ziyi_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                luck_details TEXT,
                luck_score INTEGER,
                luck_comment TEXT,
                tone_pattern TEXT,
                tones TEXT,
                tone_score INTEGER,
                tone_comment TEXT,
                total_score INTEGER,
                analysis TEXT,
                chars_detail TEXT,
                FOREIGN KEY (test_id) REFERENCES company_test_records(id)
            )
            ''')

            # 去重并添加唯一索引，保证“同一测试仅保留一次”
            # 1) 先删除重复数据，保留每个唯一键下的最新一条（MAX(id)）
            try:
                cursor.execute('''
                    DELETE FROM company_scores
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM company_scores GROUP BY record_id
                    )
                ''')
            except Exception:
                pass

            try:
                cursor.execute('''
                    DELETE FROM company_industry_detail
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM company_industry_detail GROUP BY record_id
                    )
                ''')
            except Exception:
                pass

            try:
                cursor.execute('''
                    DELETE FROM company_industry_analysis
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM company_industry_analysis GROUP BY test_id
                    )
                ''')
            except Exception:
                pass

            try:
                cursor.execute('''
                    DELETE FROM company_wuge_results
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM company_wuge_results GROUP BY test_id, plan
                    )
                ''')
            except Exception:
                pass

            try:
                cursor.execute('''
                    DELETE FROM company_shengxiao_analysis
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM company_shengxiao_analysis GROUP BY test_id
                    )
                ''')
            except Exception:
                pass

            try:
                cursor.execute('''
                    DELETE FROM company_ziyi_analysis
                    WHERE id NOT IN (
                        SELECT MAX(id) FROM company_ziyi_analysis GROUP BY test_id
                    )
                ''')
            except Exception:
                pass

            # 2) 添加唯一索引（若不存在）
            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS uq_company_scores_record
                ON company_scores(record_id)
            ''')

            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS uq_company_industry_detail_record
                ON company_industry_detail(record_id)
            ''')

            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS uq_company_industry_analysis_test
                ON company_industry_analysis(test_id)
            ''')

            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS uq_company_wuge_results_test_plan
                ON company_wuge_results(test_id, plan)
            ''')

            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS uq_company_shengxiao_analysis_test
                ON company_shengxiao_analysis(test_id)
            ''')

            cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS uq_company_ziyi_analysis_test
                ON company_ziyi_analysis(test_id)
            ''')
            
        except Exception as e:
            logger.warning(f"数据库迁移失败: {e}")

    def save_company_result(self, result: Dict) -> Optional[int]:
        """保存公司版单条分析结果
        期望结构：
          {
            'parsed': {...},
            'scores': {...},
            'industry_detail': {...},
            'owner': {...}
          }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            parsed = result.get('parsed') or {}
            owner = result.get('owner') or {}
            full_name = parsed.get('full_name') or result.get('full_name') or ''
            # 插入主记录
            cursor.execute('''
            INSERT OR IGNORE INTO company_test_records
            (full_name, prefix, main_name, industry_suffix, industry_code, org_form, industry_type,
             owner_name, owner_gender, owner_birth_time, owner_longitude, owner_latitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                full_name,
                parsed.get('prefix', ''),
                parsed.get('main_name', ''),
                parsed.get('industry_suffix', ''),
                parsed.get('industry_code', ''),
                parsed.get('org_form', ''),
                parsed.get('industry_type', ''),
                owner.get('name', ''),
                owner.get('gender', ''),
                owner.get('birth_time') or owner.get('birth', ''),
                float(owner.get('longitude')) if owner.get('longitude') not in (None, '') else None,
                float(owner.get('latitude')) if owner.get('latitude') not in (None, '') else None,
            ))

            # 获取或回查 record_id（INSERT OR IGNORE 时 lastrowid 可能为0）
            record_id = cursor.lastrowid
            if not record_id:
                cursor.execute('''
                SELECT id FROM company_test_records
                WHERE full_name=? AND owner_name=? AND (owner_birth_time=? OR owner_birth_time IS NULL)
                      AND (owner_longitude IS ? OR owner_longitude=?) AND (owner_latitude IS ? OR owner_latitude=?)
                ''', (
                    full_name,
                    owner.get('name', ''),
                    owner.get('birth_time') or owner.get('birth', ''),
                    float(owner.get('longitude')) if owner.get('longitude') not in (None, '') else None,
                    float(owner.get('longitude')) if owner.get('longitude') not in (None, '') else None,
                    float(owner.get('latitude')) if owner.get('latitude') not in (None, '') else None,
                    float(owner.get('latitude')) if owner.get('latitude') not in (None, '') else None,
                ))
                row = cursor.fetchone()
                record_id = row[0] if row else None

            if not record_id:
                conn.rollback()
                return None

            # 插入分数
            scores = result.get('scores') or {}
            cursor.execute('''
            INSERT OR REPLACE INTO company_scores
            (record_id, wuge_score, industry_score, bazi_match_score, xiyong_match_score, shengxiao_score, ziyi_score, total_score, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record_id,
                scores.get('wuge_score'),
                scores.get('industry_score'),
                scores.get('bazi_match_score'),
                scores.get('xiyong_match_score'),
                scores.get('shengxiao_score'),
                scores.get('ziyi_score'),
                scores.get('total_score'),
                scores.get('grade'),
            ))

            # 插入行业详情（旧表保留）
            detail_json = json.dumps(result.get('industry_detail', {}), ensure_ascii=False)
            cursor.execute('''
            INSERT OR REPLACE INTO company_industry_detail (record_id, detail_json)
            VALUES (?, ?)
            ''', (record_id, detail_json))

            # 插入SRD-行业特性分析（新表）
            ind = result.get('industry_detail') or {}
            wxa = (ind.get('wuxing_analysis') or {})
            lca = (ind.get('lucky_char_analysis') or {})
            cursor.execute('''
            INSERT OR REPLACE INTO company_industry_analysis (
                test_id, industry_type, industry_wuxing, name_wuxing_dist, wuxing_match_score,
                xiyong_match_score, lucky_chars, lucky_char_score, total_score, suggestions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record_id,
                (result.get('parsed') or {}).get('industry_type', ''),
                ind.get('industry_wuxing', ''),
                json.dumps(wxa.get('wuxing_dist', {}), ensure_ascii=False),
                int(wxa.get('match_score', 0)) if wxa.get('match_score') is not None else None,
                int(ind.get('xiyong_match_score', 0)) if ind.get('xiyong_match_score') is not None else None,
                json.dumps(lca.get('lucky_chars_found', []), ensure_ascii=False),
                int(lca.get('lucky_char_score', 0)) if lca.get('lucky_char_score') is not None else None,
                int(ind.get('total_score', 0)) if ind.get('total_score') is not None else None,
                json.dumps(ind.get('suggestions', []), ensure_ascii=False)
            ))

            # 插入五格结果（全称/主名两套方案）
            def _insert_wuge(plan_name: str, wuge: Dict, surname: str, given_name: str):
                if not wuge:
                    return
                cursor.execute('''
                INSERT OR REPLACE INTO company_wuge_results (
                    surname, given_name, test_id,
                    tiange, tiange_element, tiange_meaning,
                    renge, renge_element, renge_meaning,
                    dige, dige_element, dige_meaning,
                    waige, waige_element, waige_meaning,
                    zongge, zongge_element, zongge_meaning,
                    sancai, sancai_meaning, wuge_score, plan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    surname, given_name, record_id,
                    wuge.get('tiange', {}).get('num'), wuge.get('tiange', {}).get('element'), wuge.get('tiange', {}).get('meaning'),
                    wuge.get('renge', {}).get('num'), wuge.get('renge', {}).get('element'), wuge.get('renge', {}).get('meaning'),
                    wuge.get('dige', {}).get('num'), wuge.get('dige', {}).get('element'), wuge.get('dige', {}).get('meaning'),
                    wuge.get('waige', {}).get('num'), wuge.get('waige', {}).get('element'), wuge.get('waige', {}).get('meaning'),
                    wuge.get('zongge', {}).get('num'), wuge.get('zongge', {}).get('element'), wuge.get('zongge', {}).get('meaning'),
                    wuge.get('sancai', ''), wuge.get('sancai_meaning', ''), wuge.get('score', 0), plan_name
                ))

            parsed = result.get('parsed') or {}
            w_full = result.get('wuge_full')
            w_main = result.get('wuge_main')
            _insert_wuge('全称', w_full, parsed.get('prefix', ''), parsed.get('main_name', ''))
            # 主名方案的 surname/given 需要由计算阶段提供以便入库，这里尝试从 result 附加字段读取
            split = result.get('main_split') or {}
            _insert_wuge('主名', w_main, split.get('surname', ''), split.get('given', ''))

            # 插入生肖与字义分析（如有）
            shengxiao = result.get('shengxiao_detail') or {}
            if shengxiao:
                cursor.execute('''
                INSERT OR REPLACE INTO company_shengxiao_analysis (
                    test_id, shengxiao, wuxing, sanhe, liuhe,
                    xi_found, ji_found, wuxing_details, sanhe_found,
                    score, analysis, calculation_summary, calculation_steps,
                    recommended_xi_wuxing, recommended_ji_wuxing, recommended_xi_shengxiao, recommended_ji_shengxiao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record_id,
                    shengxiao.get('shengxiao'),
                    shengxiao.get('wuxing'),
                    json.dumps(shengxiao.get('sanhe') or [], ensure_ascii=False),
                    shengxiao.get('liuhe'),
                    json.dumps(shengxiao.get('xi_found') or [], ensure_ascii=False),
                    json.dumps(shengxiao.get('ji_found') or [], ensure_ascii=False),
                    json.dumps(shengxiao.get('wuxing_details') or [], ensure_ascii=False),
                    json.dumps(shengxiao.get('sanhe_found') or [], ensure_ascii=False),
                    int(shengxiao.get('score')) if shengxiao.get('score') is not None else None,
                    shengxiao.get('analysis'),
                    shengxiao.get('calculation_summary'),
                    json.dumps(shengxiao.get('calculation_steps') or [], ensure_ascii=False),
                    json.dumps(shengxiao.get('recommended_xi_wuxing') or [], ensure_ascii=False),
                    json.dumps(shengxiao.get('recommended_ji_wuxing') or [], ensure_ascii=False),
                    json.dumps(shengxiao.get('recommended_xi_shengxiao') or [], ensure_ascii=False),
                    json.dumps(shengxiao.get('recommended_ji_shengxiao') or [], ensure_ascii=False),
                ))

            ziyi = result.get('ziyi_detail') or {}
            if ziyi:
                luck = ziyi.get('luck_analysis') or {}
                tone = ziyi.get('tone_analysis') or {}
                cursor.execute('''
                INSERT OR REPLACE INTO company_ziyi_analysis (
                    test_id, luck_details, luck_score, luck_comment,
                    tone_pattern, tones, tone_score, tone_comment,
                    total_score, analysis, chars_detail
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record_id,
                    json.dumps(luck.get('details') or [], ensure_ascii=False),
                    int(luck.get('score')) if luck.get('score') is not None else None,
                    luck.get('comment'),
                    tone.get('pattern'),
                    json.dumps(tone.get('tones') or [], ensure_ascii=False),
                    int(tone.get('score')) if tone.get('score') is not None else None,
                    tone.get('comment'),
                    int(ziyi.get('score')) if ziyi.get('score') is not None else None,
                    ziyi.get('analysis'),
                    json.dumps(ziyi.get('chars_detail') or [], ensure_ascii=False)
                ))

            conn.commit()
            return record_id
        except Exception as e:
            conn.rollback()
            logger.error(f"保存公司版结果失败: {e}")
            return None
        finally:
            conn.close()

    def get_company_history(self, limit: int = 20) -> List[Dict]:
        """查询公司版历史记录，按时间倒序返回最近N条
        返回字段：id, full_name, industry_type, owner_name, owner_birth_time, created_at,
                 total_score, grade, wuge_score, industry_score, bazi_match_score, xiyong_match_score
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT t.id,
                       t.full_name,
                       t.industry_type,
                       t.owner_name,
                       t.owner_birth_time,
                       t.created_at,
                       s.total_score,
                       s.grade,
                       s.wuge_score,
                       s.industry_score,
                       s.bazi_match_score,
                       s.xiyong_match_score
                FROM company_test_records t
                LEFT JOIN company_scores s ON s.record_id = t.id
                ORDER BY t.id DESC
                LIMIT ?
            ''', (int(limit),))
            rows = cursor.fetchall()
            cols = [
                'id','full_name','industry_type','owner_name','owner_birth_time','created_at',
                'total_score','grade','wuge_score','industry_score','bazi_match_score','xiyong_match_score'
            ]
            return [dict(zip(cols, r)) for r in rows]
        finally:
            conn.close()

    def clear_company_history(self) -> int:
        """清空公司版历史记录，返回删除的主记录条数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # 先清子表，再清主表
            for table, key in [
                ('company_wuge_results', 'test_id'),
                ('company_industry_analysis', 'test_id'),
                ('company_shengxiao_analysis', 'test_id'),
                ('company_ziyi_analysis', 'test_id'),
                ('company_industry_detail', 'record_id'),
                ('company_scores', 'record_id'),
            ]:
                cursor.execute(f'DELETE FROM {table}')
            cursor.execute('SELECT COUNT(*) FROM company_test_records')
            count = cursor.fetchone()[0] or 0
            cursor.execute('DELETE FROM company_test_records')
            conn.commit()
            return int(count)
        except Exception:
            conn.rollback()
            return 0
        finally:
            conn.close()
    
    def save_test_result(self, result_dict: Dict) -> Optional[int]:
        """
        保存测试结果
        :param result_dict: 计算模块返回的结果字典
        :return: 成功返回record_id，失败返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 插入主记录
            cursor.execute('''
            INSERT OR REPLACE INTO test_records 
            (name, gender, birth_time, longitude, latitude, comprehensive_score)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                result_dict['name'],
                result_dict['gender'],
                result_dict['birth_time'],
                result_dict['longitude'],
                result_dict['latitude'],
                result_dict['comprehensive_score']
            ))
            
            record_id = cursor.lastrowid
            
            # 插入五格结果
            if 'wuge' in result_dict:
                wuge = result_dict['wuge']
                cursor.execute('''
                INSERT INTO wuge_results 
                (record_id, tiange_num, tiange_element, tiange_fortune,
                 renge_num, renge_element, renge_fortune,
                 dige_num, dige_element, dige_fortune,
                 waige_num, waige_element, waige_fortune,
                 zongge_num, zongge_element, zongge_fortune,
                 sancai, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record_id,
                    wuge['tiange']['num'], wuge['tiange']['element'], wuge['tiange']['fortune'],
                    wuge['renge']['num'], wuge['renge']['element'], wuge['renge']['fortune'],
                    wuge['dige']['num'], wuge['dige']['element'], wuge['dige']['fortune'],
                    wuge['waige']['num'], wuge['waige']['element'], wuge['waige']['fortune'],
                    wuge['zongge']['num'], wuge['zongge']['element'], wuge['zongge']['fortune'],
                    wuge['sancai'], wuge['score']
                ))
            
            # 插入八字结果
            if 'bazi' in result_dict:
                bazi = result_dict['bazi']
                cursor.execute('''
                INSERT INTO bazi_results 
                (record_id, bazi_str, wuxing, nayin, wuxing_geshu, wuxing_strength,
                 tongyi_elements, tongyi_strength, tongyi_percent,
                 yilei_elements, yilei_strength, yilei_percent,
                 rizhu_qiangruo, siji_yongshen, xiyong_shen, ji_shen, jixiang_color, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record_id,
                    bazi['bazi_str'],
                    bazi['wuxing'],
                    bazi['nayin'],
                    json.dumps(bazi.get('geshu', {}), ensure_ascii=False),
                    json.dumps(bazi.get('wuxing_strength', {}), ensure_ascii=False),
                    json.dumps(bazi.get('tongyi', {}).get('elements', []), ensure_ascii=False),
                    bazi.get('tongyi', {}).get('strength', 0),
                    bazi.get('tongyi', {}).get('percent', 0),
                    json.dumps(bazi.get('yilei', {}).get('elements', []), ensure_ascii=False),
                    bazi.get('yilei', {}).get('strength', 0),
                    bazi.get('yilei', {}).get('percent', 0),
                    bazi.get('rizhu', ''),
                    bazi.get('siji', ''),
                    json.dumps(bazi.get('xiyong_shen', []), ensure_ascii=False),
                    json.dumps(bazi.get('ji_shen', []), ensure_ascii=False),
                    bazi.get('color', ''),
                    bazi['score']
                ))
            
            # 插入字义结果
            if 'ziyi' in result_dict:
                ziyi = result_dict['ziyi']
                cursor.execute('''
                INSERT INTO ziyi_results (record_id, analysis, score)
                VALUES (?, ?, ?)
                ''', (record_id, ziyi['analysis'], ziyi['score']))
            
            # 插入生肖结果
            if 'shengxiao' in result_dict:
                sx = result_dict['shengxiao']
                cursor.execute('''
                INSERT INTO shengxiao_results 
                (record_id, shengxiao, xi_zigen, ji_zigen, score)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    record_id,
                    sx['shengxiao'],
                    json.dumps(sx.get('xi_zigen', []), ensure_ascii=False),
                    json.dumps(sx.get('ji_zigen', []), ensure_ascii=False),
                    sx['score']
                ))
            
            # 插入称骨结果
            if 'chenggu' in result_dict:
                cg = result_dict['chenggu']
                cursor.execute('''
                INSERT INTO chenggu_results 
                (record_id, bone_weight, fortune_text, comment)
                VALUES (?, ?, ?, ?)
                ''', (
                    record_id,
                    cg['weight'],
                    cg.get('fortune_text', ''),
                    cg.get('comment', '')
                ))
            
            conn.commit()
            logger.info(f"测试结果保存成功，记录ID: {record_id}")
            return record_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"保存测试结果失败: {e}")
            return None
        finally:
            conn.close()
    
    def query_test_result(self, name: str, gender: str, birth_time: str, 
                         longitude: float, latitude: float) -> Optional[Dict]:
        """
        查询测试结果
        :return: 存在返回结果字典，不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 查询主记录
            cursor.execute('''
            SELECT id, name, gender, birth_time, longitude, latitude, comprehensive_score
            FROM test_records
            WHERE name=? AND gender=? AND birth_time=? AND longitude=? AND latitude=?
            ''', (name, gender, birth_time, longitude, latitude))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            record_id = row[0]
            result = {
                'name': row[1],
                'gender': row[2],
                'birth_time': row[3],
                'longitude': row[4],
                'latitude': row[5],
                'comprehensive_score': row[6]
            }
            
            # 查询五格结果
            cursor.execute('''
            SELECT tiange_num, tiange_element, tiange_fortune,
                   renge_num, renge_element, renge_fortune,
                   dige_num, dige_element, dige_fortune,
                   waige_num, waige_element, waige_fortune,
                   zongge_num, zongge_element, zongge_fortune,
                   sancai, score
            FROM wuge_results WHERE record_id=?
            ''', (record_id,))
            wuge_row = cursor.fetchone()
            if wuge_row:
                result['wuge'] = {
                    'tiange': {'num': wuge_row[0], 'element': wuge_row[1], 'fortune': wuge_row[2]},
                    'renge': {'num': wuge_row[3], 'element': wuge_row[4], 'fortune': wuge_row[5]},
                    'dige': {'num': wuge_row[6], 'element': wuge_row[7], 'fortune': wuge_row[8]},
                    'waige': {'num': wuge_row[9], 'element': wuge_row[10], 'fortune': wuge_row[11]},
                    'zongge': {'num': wuge_row[12], 'element': wuge_row[13], 'fortune': wuge_row[14]},
                    'sancai': wuge_row[15],
                    'score': wuge_row[16]
                }
            
            # 查询八字结果
            cursor.execute('''
            SELECT bazi_str, wuxing, nayin, wuxing_geshu, rizhu_qiangruo,
                   siji_yongshen, xiyong_shen, ji_shen, jixiang_color, score
            FROM bazi_results WHERE record_id=?
            ''', (record_id,))
            bazi_row = cursor.fetchone()
            if bazi_row:
                result['bazi'] = {
                    'bazi_str': bazi_row[0],
                    'wuxing': bazi_row[1],
                    'nayin': bazi_row[2],
                    'geshu': json.loads(bazi_row[3]) if bazi_row[3] else {},
                    'rizhu': bazi_row[4],
                    'siji': bazi_row[5],
                    'xiyong_shen': json.loads(bazi_row[6]) if bazi_row[6] else [],
                    'ji_shen': json.loads(bazi_row[7]) if bazi_row[7] else [],
                    'color': bazi_row[8],
                    'score': bazi_row[9]
                }
            
            # 查询字义结果
            cursor.execute('''
            SELECT analysis, score FROM ziyi_results WHERE record_id=?
            ''', (record_id,))
            ziyi_row = cursor.fetchone()
            if ziyi_row:
                result['ziyi'] = {
                    'analysis': ziyi_row[0],
                    'score': ziyi_row[1]
                }
            
            # 查询生肖结果
            cursor.execute('''
            SELECT shengxiao, xi_zigen, ji_zigen, score
            FROM shengxiao_results WHERE record_id=?
            ''', (record_id,))
            sx_row = cursor.fetchone()
            if sx_row:
                result['shengxiao'] = {
                    'shengxiao': sx_row[0],
                    'xi_zigen': json.loads(sx_row[1]) if sx_row[1] else [],
                    'ji_zigen': json.loads(sx_row[2]) if sx_row[2] else [],
                    'score': sx_row[3]
                }
            
            # 查询称骨结果
            cursor.execute('''
            SELECT bone_weight, fortune_text, comment
            FROM chenggu_results WHERE record_id=?
            ''', (record_id,))
            cg_row = cursor.fetchone()
            if cg_row:
                result['chenggu'] = {
                    'weight': cg_row[0],
                    'fortune_text': cg_row[1],
                    'comment': cg_row[2]
                }
            
            return result
            
        except Exception as e:
            logger.error(f"查询测试结果失败: {e}")
            return None
        finally:
            conn.close()
    
    def query_history(self, limit: int = 10) -> List[Dict]:
        """查询历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT name, gender, birth_time, comprehensive_score, created_at
            FROM test_records
            ORDER BY created_at DESC
            LIMIT ?
            ''', (limit,))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'name': row[0],
                    'gender': row[1],
                    'birth_time': row[2],
                    'score': row[3],
                    'created_at': row[4]
                })
            
            return records
            
        except Exception as e:
            logger.error(f"查询历史记录失败: {e}")
            return []
        finally:
            conn.close()
    
    def delete_record(self, record_id: int) -> bool:
        """删除记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM test_records WHERE id=?', (record_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"删除记录失败: {e}")
            return False
        finally:
            conn.close()
    
    def clear_all_records(self) -> bool:
        """清空所有历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 删除所有关联表的数据
            cursor.execute('DELETE FROM chenggu_results')
            cursor.execute('DELETE FROM shengxiao_results')
            cursor.execute('DELETE FROM ziyi_results')
            cursor.execute('DELETE FROM bazi_results')
            cursor.execute('DELETE FROM wuge_results')
            cursor.execute('DELETE FROM test_records')
            
            conn.commit()
            logger.info("历史记录已清空")
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"清空历史记录失败: {e}")
            return False
        finally:
            conn.close()
    
    def get_records_count(self) -> int:
        """获取历史记录总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM test_records')
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"查询记录数失败: {e}")
            return 0
        finally:
            conn.close()
    
    def clear_all_data(self) -> bool:
        """清空所有数据表（包括资源数据和历史记录）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # 清空所有表
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':  # 跳过系统表
                    cursor.execute(f'DELETE FROM {table_name}')
                    logger.info(f"已清空表: {table_name}")
            
            # 重置自增ID
            cursor.execute("DELETE FROM sqlite_sequence")
            
            conn.commit()
            logger.info("所有数据表已清空")
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"清空所有数据表失败: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_tables_info(self) -> Dict[str, int]:
        """获取所有表的记录数统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = cursor.fetchall()
            
            info = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                info[table_name] = count
            
            return info
        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
            return {}
        finally:
            conn.close()
