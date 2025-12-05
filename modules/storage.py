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
            logger.info("数据库初始化完成")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库初始化失败: {e}")
            raise
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
                (record_id, bazi_str, wuxing, nayin, wuxing_geshu, rizhu_qiangruo,
                 siji_yongshen, xiyong_shen, ji_shen, jixiang_color, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record_id,
                    bazi['bazi_str'],
                    bazi['wuxing'],
                    bazi['nayin'],
                    json.dumps(bazi.get('geshu', {}), ensure_ascii=False),
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
