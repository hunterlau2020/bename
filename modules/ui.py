# -*- coding: utf-8 -*-
"""
用户界面模块 - 处理命令行交互
"""

import logging
import re
from datetime import datetime
from typing import Optional, Tuple, List, Dict

from .calculator import Calculator
from .storage import Storage

logger = logging.getLogger(__name__)


class UserInterface:
    """用户界面类"""
    
    def __init__(self, calculator: Calculator, storage: Storage):
        """初始化用户界面"""
        self.calculator = calculator
        self.storage = storage
    
    def run(self):
        """主运行循环"""
        self._show_welcome()
        
        while True:
            try:
                # 获取用户输入
                name_input = self._input_name()
                if name_input is None:
                    break
                
                surname, given_name = name_input
                full_name = surname + given_name
                
                # 检查是否是清空历史命令
                if surname.lower() == 'clear':
                    self._handle_clear_history()
                    continue
                
                gender = self._input_gender()
                if gender is None:
                    break
                
                birth_time = self._input_birth_time()
                if birth_time is None:
                    break
                
                longitude, latitude = self._input_coordinates()
                if longitude is None or latitude is None:
                    break
                
                # 查询缓存
                cached_result = self.storage.query_test_result(
                    full_name, gender, birth_time, longitude, latitude
                )
                
                if cached_result:
                    print("\n从缓存加载结果...")
                    result = cached_result
                else:
                    # 执行计算
                    print("\n正在计算，请稍候...")
                    result = self.calculator.calculate_name(
                        surname, given_name, gender, birth_time, longitude, latitude
                    )
                    
                    # 保存结果
                    self.storage.save_test_result(result)
                
                # 显示结果
                self._display_result(result)
                
                # 询问是否继续
                if not self._ask_continue():
                    break
                    
            except ValueError as e:
                print(f"\n输入错误: {e}")
                logger.warning(f"输入验证失败: {e}")
            except Exception as e:
                print(f"\n处理出错: {e}")
                logger.exception(f"运行时错误: {e}")
        
        print("\n感谢使用！再见！")
    
    def _show_welcome(self):
        """显示欢迎信息"""
        print("=" * 60)
        print("姓名测试软件 v1.0")
        print("基于传统命理学的姓名分析系统")
        print("=" * 60)
        print("\n提示: 输入 'clear' 清空历史记录\n")
    
    def _input_name(self) -> Optional[Tuple[str, str]]:
        """输入姓名（分别输入姓氏和名字）"""
        print("请分别输入姓氏和名字（输入'quit'退出）：")
        
        # 输入姓氏
        surname = input("姓氏 (1-2个汉字): ").strip()
        if surname.lower() == 'quit':
            return None
        
        # 验证姓氏格式
        if not surname or len(surname) < 1 or len(surname) > 2:
            raise ValueError("姓氏长度必须为1-2个汉字")
        
        for char in surname:
            if not '\u4e00' <= char <= '\u9fff':
                raise ValueError(f"姓氏包含非法字符: {char}")
        
        # 输入名字
        given_name = input("名字 (1-2个汉字): ").strip()
        if given_name.lower() == 'quit':
            return None
        
        # 验证名字格式
        if not given_name or len(given_name) < 1 or len(given_name) > 2:
            raise ValueError("名字长度必须为1-2个汉字")
        
        for char in given_name:
            if not '\u4e00' <= char <= '\u9fff':
                raise ValueError(f"名字包含非法字符: {char}")
        
        # 验证总长度
        full_name = surname + given_name
        if len(full_name) < 2 or len(full_name) > 4:
            raise ValueError(f"姓名总长度必须为2-4个汉字（当前: {len(full_name)}）")
        
        return (surname, given_name)
    
    def _input_gender(self) -> Optional[str]:
        """输入性别"""
        print("\n请输入性别（输入'quit'退出）：")
        gender = input("性别 (男/女): ").strip()
        
        if gender.lower() == 'quit':
            return None
        
        if gender not in ['男', '女']:
            raise ValueError("性别必须为'男'或'女'")
        
        return gender
    
    def _input_birth_time(self) -> Optional[str]:
        """输入出生时间"""
        print("\n请输入出生时间（输入'quit'退出）：")
        birth_time_str = input("出生时间 (YYYY-MM-DD HH:MM): ").strip()
        
        if birth_time_str.lower() == 'quit':
            return None
        
        # 验证时间格式
        try:
            birth_dt = datetime.strptime(birth_time_str, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("时间格式错误，请使用 YYYY-MM-DD HH:MM 格式")
        
        # 验证时间合理性
        if birth_dt > datetime.now():
            raise ValueError("出生时间不能晚于当前时间")
        
        if birth_dt.year < 1900 or birth_dt.year > 2100:
            raise ValueError("出生年份必须在1900-2100之间")
        
        return birth_time_str
    
    def _input_coordinates(self) -> Tuple[Optional[float], Optional[float]]:
        """输入经纬度坐标"""
        print("\n请输入出生地经纬度坐标（输入'quit'退出，输入'help'查看帮助）：")
        
        # 输入经度
        while True:
            lon_input = input("经度 (73.0-135.0): ").strip()
            
            if lon_input.lower() == 'quit':
                return None, None
            
            if lon_input.lower() == 'help':
                self._show_coord_help()
                continue
            
            try:
                longitude = float(lon_input)
                if not (73.0 <= longitude <= 135.0):
                    raise ValueError("经度必须在73.0-135.0之间")
                break
            except ValueError as e:
                print(f"输入错误: {e}")
        
        # 输入纬度
        while True:
            lat_input = input("纬度 (3.0-54.0): ").strip()
            
            if lat_input.lower() == 'quit':
                return None, None
            
            if lat_input.lower() == 'help':
                self._show_coord_help()
                continue
            
            try:
                latitude = float(lat_input)
                if not (3.0 <= latitude <= 54.0):
                    raise ValueError("纬度必须在3.0-54.0之间")
                break
            except ValueError as e:
                print(f"输入错误: {e}")
        
        return longitude, latitude
    
    def _show_coord_help(self):
        """显示坐标帮助信息"""
        print("\n" + "=" * 60)
        print("如何查询经纬度坐标：")
        print("1. 天地图：https://map.tianditu.gov.cn/")
        print("   在地图上点击地点，右键选择'坐标转换'即可查看")
        print("2. 高德地图/百度地图：")
        print("   在地图上点击地点，查看详情页中的坐标信息")
        print("3. 维基百科：")
        print("   搜索城市名称，通常在信息框中会显示经纬度")
        print("=" * 60 + "\n")
    
    def _get_kangxi_info(self, name: str) -> List[Dict]:
        """
        获取姓名中每个字的康熙字典信息
        :param name: 姓名
        :return: 字典信息列表
        """
        import sqlite3
        
        kangxi_info = []
        try:
            conn = sqlite3.connect('local.db')
            cursor = conn.cursor()
            
            for char in name:
                cursor.execute("""
                    SELECT character, traditional, strokes, radical, bs_strokes, wuxing, luck
                    FROM kangxi_strokes 
                    WHERE character = ?
                """, (char,))
                
                row = cursor.fetchone()
                if row:
                    kangxi_info.append({
                        'character': row[0],
                        'traditional': row[1] or row[0],
                        'strokes': row[2],
                        'radical': row[3] or '未知',
                        'bs_strokes': row[4] or 0,
                        'wuxing': row[5] or '未知',
                        'luck': row[6] or '未知'
                    })
                else:
                    kangxi_info.append({
                        'character': char,
                        'traditional': char,
                        'strokes': 0,
                        'radical': '未知',
                        'bs_strokes': 0,
                        'wuxing': '未知',
                        'luck': '未知'
                    })
            
            conn.close()
        except Exception as e:
            logger.error(f"查询康熙字典信息失败: {e}")
        
        return kangxi_info
    
    def _display_result(self, result: dict):
        """显示计算结果"""
        print("\n" + "=" * 60)
        print(f"姓名测试结果 - {result['name']}")
        print("=" * 60)
        
        # 基本信息
        print(f"\n【基本信息】")
        print(f"姓名: {result['name']}")
        
        # 显示康熙字典详细信息
        kangxi_info = self._get_kangxi_info(result['name'])
        if kangxi_info:
            for info in kangxi_info:
                parts = [f"笔画={info['strokes']}", f"部首={info['radical']}"]
                if info['wuxing'] != '未知':
                    parts.append(f"五行={info['wuxing']}")
                if info['luck'] != '未知':
                    parts.append(f"吉凶={info['luck']}")
                print(f"  {info['traditional']}: {', '.join(parts)}")
        
        print(f"性别: {result['gender']}")
        print(f"出生时间(阳历): {result['birth_time']}")
        
        # 显示农历出生时间
        if 'bazi' in result and 'lunar_date' in result['bazi']:
            lunar_date = result['bazi']['lunar_date']
            print(f"出生时间(农历): {lunar_date}")
        
        print(f"出生地坐标: 经度{result['longitude']}°, 纬度{result['latitude']}°")
        print(f"综合评分: {result['comprehensive_score']}分")
        
        # 五格分析
        print(f"\n【三才五格分析】(得分: {result['wuge']['score']}分)")
        wuge = result['wuge']
        print(f"天格: {wuge['tiange']['num']}({wuge['tiange']['element']}) {wuge['tiange']['fortune']}")
        print(f"人格: {wuge['renge']['num']}({wuge['renge']['element']}) {wuge['renge']['fortune']}")
        print(f"地格: {wuge['dige']['num']}({wuge['dige']['element']}) {wuge['dige']['fortune']}")
        print(f"外格: {wuge['waige']['num']}({wuge['waige']['element']}) {wuge['waige']['fortune']}")
        print(f"总格: {wuge['zongge']['num']}({wuge['zongge']['element']}) {wuge['zongge']['fortune']}")
        print(f"三才配置: {wuge['sancai']}")
        
        # 八字分析
        print(f"\n【生辰八字分析】(得分: {result['bazi']['score']}分)")
        bazi = result['bazi']
        print(f"八字: {bazi['bazi_str']}")
        print(f"五行: {bazi['wuxing']}")
        print(f"纳音: {bazi['nayin']}")
        print(f"五行个数: 金{bazi['geshu']['金']} 木{bazi['geshu']['木']} "
              f"水{bazi['geshu']['水']} 火{bazi['geshu']['火']} 土{bazi['geshu']['土']}")
        
        # 显示五行强度
        if 'wuxing_strength' in bazi:
            strength = bazi['wuxing_strength']
            total = sum(strength.values())
            print(f"五行强度: ", end='')
            strength_parts = []
            for wx in ['木', '火', '土', '金', '水']:
                s = strength.get(wx, 0)
                percent = (s / total * 100) if total > 0 else 0
                strength_parts.append(f"{wx}{s}({percent:.1f}%)")
            print(' '.join(strength_parts))
        
        # 显示同类异类
        if 'tongyi' in bazi and 'yilei' in bazi:
            tongyi = bazi['tongyi']
            yilei = bazi['yilei']
            print(f"同类({''.join(tongyi['elements'])}): {tongyi['strength']} ({tongyi['percent']:.1f}%)")
            print(f"异类({''.join(yilei['elements'])}): {yilei['strength']} ({yilei['percent']:.1f}%)")
            if tongyi['strength'] > yilei['strength']:
                print(f"日主偏强，喜克泄耗")
            else:
                print(f"日主偏弱，喜生扶")
        
        print(f"日主: {bazi['rizhu']}")
        print(f"喜用神: {' '.join(bazi['xiyong_shen'])}")
        print(f"忌神: {' '.join(bazi['ji_shen'])}")
        print(f"四季用神: {bazi['siji']}")
        print(f"吉祥颜色: {bazi['color']}")
        
        # 字义音形分析
        print(f"\n【字义音形分析】(得分: {result['ziyi']['score']}分)")
        ziyi = result['ziyi']
        
        # 显示字符详情（如果有）
        if 'chars_detail' in ziyi:
            chars_parts = []
            for char_info in ziyi['chars_detail']:
                char = char_info['traditional']
                luck = char_info['luck']
                chars_parts.append(f"{char}({luck})")
            print(f"字符: {' '.join(chars_parts)}")
        
        # 显示分析内容
        if 'analysis' in ziyi:
            for line in ziyi['analysis'].split('\n'):
                if line.strip():
                    print(f"{line}")
        else:
            print(f"{ziyi.get('analysis', '无详细分析')}")
        
        # 生肖喜忌分析
        print(f"\n【生肖喜忌分析】(得分: {result['shengxiao']['score']}分)")
        shengxiao = result['shengxiao']
        print(f"生肖: {shengxiao['shengxiao']}")
        print(f"喜用字根: {' '.join(shengxiao['xi_zigen'])}")
        print(f"忌用字根: {' '.join(shengxiao['ji_zigen'])}")
        
        # 称骨算命
        print(f"\n【称骨算命】")
        chenggu = result['chenggu']
        print(f"骨重: {chenggu['weight']}两")
        print(f"命书: {chenggu['fortune_text']}")
        print(f"评价: {chenggu['comment']}")
        
        # 综合建议
        print(f"\n【综合建议】")
        suggestion = result.get('suggestion', self._generate_default_suggestion(result['comprehensive_score']))
        print(f"{suggestion}")
        
        print("\n" + "=" * 60)
    
    def _generate_default_suggestion(self, score: int) -> str:
        """生成默认建议"""
        if score >= 90:
            return "该姓名综合评分优秀，各方面配置均佳，建议使用。"
        elif score >= 80:
            return "该姓名综合评分良好，整体配置较佳，可以考虑使用。"
        elif score >= 70:
            return "该姓名综合评分中等，有一定优势但也存在不足，可根据个人喜好决定。"
        elif score >= 60:
            return "该姓名综合评分偏低，建议参考五格、八字等具体分析后再做决定。"
        else:
            return "该姓名综合评分较低，建议重新考虑或调整姓名配置。"
    
    def _handle_clear_history(self):
        """处理清空历史记录"""
        count = self.storage.get_records_count()
        if count == 0:
            print("\n当前没有历史记录\n")
            return
        
        print(f"\n当前共有 {count} 条历史记录")
        confirm = input("确认清空所有历史记录？(yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y', '是']:
            if self.storage.clear_all_records():
                print("✓ 历史记录已清空\n")
            else:
                print("✗ 清空失败，请查看日志\n")
        else:
            print("操作已取消\n")
    
    def _ask_continue(self) -> bool:
        """询问是否继续"""
        while True:
            choice = input("\n是否继续测试其他姓名？(y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                print("\n" + "-" * 60 + "\n")
                return True
            elif choice in ['n', 'no', '否']:
                return False
            else:
                print("请输入 y 或 n")
