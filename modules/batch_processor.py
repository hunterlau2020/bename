#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量处理模块 - 从文件读取姓名信息并批量计算
Author: Auto Generated
Date: 2025-12-06
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, calculator, storage):
        """
        初始化批量处理器
        :param calculator: Calculator 实例
        :param storage: Storage 实例
        """
        self.calculator = calculator
        self.storage = storage
    
    def process_file(self, input_file: str) -> Dict[str, Any]:
        """
        处理输入文件
        :param input_file: 输入文件路径（支持 .txt, .json, .csv）
        :return: 处理结果字典
        """
        file_path = Path(input_file)
        
        if not file_path.exists():
            return {
                'success': False,
                'error': f'文件不存在: {input_file}'
            }
        
        # 根据文件扩展名选择解析方法
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.json':
                records = self._parse_json(file_path)
            elif suffix == '.csv':
                records = self._parse_csv(file_path)
            else:  # .txt 或其他
                records = self._parse_txt(file_path)
            
            if not records:
                return {
                    'success': False,
                    'error': '文件中没有有效的记录'
                }
            
            # 批量处理
            results = self._batch_calculate(records)
            
            # 保存结果
            output_file = self._save_results(results, file_path)
            
            # 统计结果
            success_count = sum(1 for r in results if r['success'])
            failed_count = len(results) - success_count
            
            return {
                'success': True,
                'success_count': success_count,
                'failed_count': failed_count,
                'output_file': str(output_file),
                'results': results
            }
            
        except Exception as e:
            logger.exception(f"批量处理失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_json(self, file_path: Path) -> List[Dict]:
        """
        解析 JSON 格式文件
        格式示例:
        [
          {
            "name": "张三",
            "gender": "男",
            "birth_date": "1990-01-01",
            "birth_time": "10:30",
            "longitude": 116.4074,
            "latitude": 39.9042
          }
        ]
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            data = [data]
        
        records = []
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                logger.warning(f"跳过第 {idx+1} 条记录（格式错误）")
                continue
            
            # 验证必填字段
            if not all(key in item for key in ['name', 'gender', 'birth_date']):
                logger.warning(f"跳过第 {idx+1} 条记录（缺少必填字段）")
                continue
            
            records.append(item)
        
        return records
    
    def _parse_csv(self, file_path: Path) -> List[Dict]:
        """
        解析 CSV 格式文件
        格式示例:
        name,gender,birth_date,birth_time,longitude,latitude
        张三,男,1990-01-01,10:30,116.4074,39.9042
        李四,女,1992-05-20,14:00,,
        """
        import csv
        
        records = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                # 验证必填字段
                if not all(key in row for key in ['name', 'gender', 'birth_date']):
                    logger.warning(f"跳过第 {idx+2} 行（缺少必填字段）")
                    continue
                
                if not row['name'].strip():
                    logger.warning(f"跳过第 {idx+2} 行（姓名为空）")
                    continue
                
                # 转换数据类型
                record = {
                    'name': row['name'].strip(),
                    'gender': row['gender'].strip(),
                    'birth_date': row['birth_date'].strip(),
                }
                
                if 'birth_time' in row and row['birth_time'].strip():
                    record['birth_time'] = row['birth_time'].strip()
                
                if 'longitude' in row and row['longitude'].strip():
                    try:
                        record['longitude'] = float(row['longitude'])
                    except ValueError:
                        logger.warning(f"第 {idx+2} 行经度格式错误")
                
                if 'latitude' in row and row['latitude'].strip():
                    try:
                        record['latitude'] = float(row['latitude'])
                    except ValueError:
                        logger.warning(f"第 {idx+2} 行纬度格式错误")
                
                records.append(record)
        
        return records
    
    def _parse_txt(self, file_path: Path) -> List[Dict]:
        """
        解析 TXT 格式文件
        格式示例（每行一条记录，字段用空格或制表符分隔）:
        张三 男 1990-01-01 10:30 116.4074 39.9042
        李四 女 1992-05-20 14:00
        王五 男 1985-03-15
        
        或者使用键值对格式（每条记录用空行分隔）:
        name: 张三
        gender: 男
        birth_date: 1990-01-01
        birth_time: 10:30
        longitude: 116.4074
        latitude: 39.9042
        
        name: 李四
        gender: 女
        birth_date: 1992-05-20
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检测格式（检查非注释行中是否有键值对格式）
        has_keyvalue = False
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                if 'name:' in line.lower() or 'gender:' in line.lower():
                    has_keyvalue = True
                    break
        
        if has_keyvalue and '\n\n' in content:
            return self._parse_txt_keyvalue(content)
        else:
            return self._parse_txt_tabular(content)
    
    def _parse_txt_keyvalue(self, content: str) -> List[Dict]:
        """解析键值对格式的 TXT"""
        records = []
        blocks = content.strip().split('\n\n')
        
        for idx, block in enumerate(blocks):
            if not block.strip():
                continue
            
            record = {}
            for line in block.strip().split('\n'):
                if ':' not in line:
                    continue
                
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ['name', 'gender', 'birth_date', 'birth_time']:
                    record[key] = value
                elif key == 'longitude':
                    try:
                        record['longitude'] = float(value)
                    except ValueError:
                        logger.warning(f"第 {idx+1} 条记录经度格式错误")
                elif key == 'latitude':
                    try:
                        record['latitude'] = float(value)
                    except ValueError:
                        logger.warning(f"第 {idx+1} 条记录纬度格式错误")
            
            # 验证必填字段
            if not all(key in record for key in ['name', 'gender', 'birth_date']):
                logger.warning(f"跳过第 {idx+1} 条记录（缺少必填字段）")
                continue
            
            records.append(record)
        
        return records
    
    def _parse_txt_tabular(self, content: str) -> List[Dict]:
        """解析表格格式的 TXT"""
        records = []
        lines = content.strip().split('\n')
        
        line_no = 0
        for line in lines:
            line_no += 1
            # 跳过空行和注释行
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # 分隔符可以是空格或制表符
            parts = line.split()
            
            if len(parts) < 3:
                logger.warning(f"跳过第 {line_no} 行（字段不足）")
                continue
            
            record = {
                'name': parts[0],
                'gender': parts[1],
                'birth_date': parts[2],
            }
            
            if len(parts) >= 4:
                record['birth_time'] = parts[3]
            
            if len(parts) >= 5:
                try:
                    record['longitude'] = float(parts[4])
                except ValueError:
                    logger.warning(f"第 {line_no} 行经度格式错误")
            
            if len(parts) >= 6:
                try:
                    record['latitude'] = float(parts[5])
                except ValueError:
                    logger.warning(f"第 {line_no} 行纬度格式错误")
            
            records.append(record)
        
        return records
    
    def _batch_calculate(self, records: List[Dict]) -> List[Dict]:
        """
        批量计算
        :param records: 记录列表
        :return: 结果列表
        """
        results = []
        total = len(records)
        
        print(f"\n{'='*70}")
        print(f"开始批量处理 {total} 条记录")
        print(f"{'='*70}\n")
        
        for idx, record in enumerate(records, 1):
            print(f"[{idx}/{total}] {record['name']}", end=' ')
            
            try:
                # 准备参数
                name = record['name']
                gender = record['gender']
                birth_date = record['birth_date']
                birth_time_str = record.get('birth_time', '12:00')  # 默认中午
                longitude = record.get('longitude', 116.4074)  # 默认北京
                latitude = record.get('latitude', 39.9042)
                
                # 组合完整的出生时间
                birth_datetime = f"{birth_date} {birth_time_str}"
                
                # 分离姓和名（假设单姓，取第一个字为姓）
                surname = name[0]
                given_name = name[1:] if len(name) > 1 else ''
                
                if not given_name:
                    raise ValueError("姓名至少需要两个字")
                
                # 调用计算器
                result = self.calculator.calculate_name(
                    surname=surname,
                    given_name=given_name,
                    gender=gender,
                    birth_time=birth_datetime,
                    longitude=longitude,
                    latitude=latitude
                )
                
                # 保存到历史记录
                self.storage.save_test_result(result)
                
                results.append({
                    'success': True,
                    'name': name,
                    'result': result
                })
                
                # 显示八字信息
                bazi = result.get('bazi', {})
                score = result.get('comprehensive_score', 0)
                if bazi:
                    print(f"[成功] 综合评分: {score}分")
                    print(f"  八字: {bazi.get('bazi_str', '')}")
                    print(f"  日主: {bazi.get('rizhu', '')} - {bazi.get('siji', '')}")
                    
                    # 显示五行强度（更紧凑的格式）
                    if 'wuxing_strength' in bazi:
                        strength = bazi['wuxing_strength']
                        total_strength = sum(strength.values())
                        strength_parts = []
                        for wx in ['木', '火', '土', '金', '水']:
                            s = strength.get(wx, 0)
                            percent = (s / total_strength * 100) if total_strength > 0 else 0
                            # 强度状态标记
                            if s < 100:
                                mark = '!'
                            elif s < 500:
                                mark = '-'
                            elif s >= 1500:
                                mark = '+'
                            else:
                                mark = ''
                            strength_parts.append(f"{wx}{s}{mark}")
                        print(f"  五行: {' '.join(strength_parts)}  (!极弱 -弱 +旺)")
                    
                    # 显示同类异类和喜用神
                    if 'tongyi' in bazi and 'yilei' in bazi:
                        tongyi = bazi['tongyi']
                        yilei = bazi['yilei']
                        tongyi_elem = ''.join(tongyi['elements'])
                        yilei_elem = ''.join(yilei['elements'])
                        print(f"  同类({tongyi_elem}){tongyi['strength']}({tongyi['percent']:.1f}%) | "
                              f"异类({yilei_elem}){yilei['strength']}({yilei['percent']:.1f}%)")
                        
                        xiyong = bazi.get('xiyong_shen', [])
                        ji = bazi.get('ji_shen', [])
                        if tongyi['percent'] > 55:
                            status = "身强"
                        elif tongyi['percent'] < 45:
                            status = "身弱"
                        else:
                            status = "中和"
                        
                        print(f"  判断: {status} | 喜用: {','.join(xiyong)}", end='')
                        if ji:
                            print(f" | 忌: {','.join(ji)}")
                        else:
                            print()
                    
                    # 显示四季用神参考
                    if bazi.get('siji'):
                        siji = bazi['siji']
                        # 如果是详细格式，显示完整信息
                        if len(siji) > 20:  # 详细格式通常较长
                            print(f"  四季: {siji}")
                    
                    # 显示五格信息（紧凑格式）
                    if 'wuge' in result:
                        wuge = result['wuge']
                        print(f"  五格: 天{wuge['tiange']['num']}({wuge['tiange']['fortune']}) "
                              f"人{wuge['renge']['num']}({wuge['renge']['fortune']}) "
                              f"地{wuge['dige']['num']}({wuge['dige']['fortune']}) "
                              f"外{wuge['waige']['num']}({wuge['waige']['fortune']}) "
                              f"总{wuge['zongge']['num']}({wuge['zongge']['fortune']}) | {wuge['sancai']}")
                else:
                    print(f"[成功] 综合评分: {score}分")
                
            except ValueError as ve:
                error_msg = str(ve)
                results.append({
                    'success': False,
                    'name': record.get('name', '未知'),
                    'error': error_msg
                })
                print(f"[失败] {error_msg}")
                logger.error(f"数据验证失败 {name}: {error_msg}")
                
            except Exception as e:
                error_msg = str(e)
                results.append({
                    'success': False,
                    'name': record.get('name', '未知'),
                    'error': error_msg
                })
                print(f"[失败] {error_msg}")
                logger.exception(f"处理记录失败: {record}")
        
        print(f"\n{'='*70}")
        print(f"批量处理完成")
        print(f"总计: {total} 条 | 成功: {sum(1 for r in results if r['success'])} 条 | "
              f"失败: {sum(1 for r in results if not r['success'])} 条")
        print(f"{'='*70}\n")
        
        return results
    
    def _save_results(self, results: List[Dict], input_file: Path) -> Path:
        """
        保存结果到文件
        :param results: 结果列表
        :param input_file: 输入文件路径
        :return: 输出文件路径
        """
        # 生成输出文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = input_file.parent / f"{input_file.stem}_result.json"
        
        # 准备输出数据
        output_data = {
            'input_file': str(input_file),
            'process_time': timestamp,
            'total': len(results),
            'success': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': []
        }
        
        for item in results:
            if item['success']:
                # 提取完整信息
                result = item['result']
                output_data['results'].append({
                    'name': item['name'],
                    'success': True,
                    'basic_info': {
                        'surname': result.get('surname', ''),
                        'given_name': result.get('given_name', ''),
                        'gender': result.get('gender', ''),
                        'birth_time': result.get('birth_time', ''),
                        'longitude': result.get('longitude'),
                        'latitude': result.get('latitude')
                    },
                    'comprehensive_score': result.get('comprehensive_score', 0),
                    'wuge': result.get('wuge', {}),
                    'bazi': result.get('bazi', {}),
                    'ziyi': result.get('ziyi', {}),
                    'shengxiao': result.get('shengxiao', {}),
                    'chenggu': result.get('chenggu', {})
                })
            else:
                output_data['results'].append({
                    'name': item['name'],
                    'success': False,
                    'error': item.get('error', '未知错误')
                })
        
        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到: {output_file}")
        return output_file
