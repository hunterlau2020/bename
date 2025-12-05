#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
康熙字典数据转换工具
将多个源文件合并转换为 kangxi.json 格式
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import pandas as pd
except ImportError:
    print("错误: 需要安装 pandas 库")
    print("请运行: pip install pandas openpyxl")
    sys.exit(1)


class KangxiConverter:
    """康熙字典数据转换器"""
    
    def __init__(self):
        self.unihan_strokes = {}  # Unicode -> 笔画数
        self.unihan_pinyin = {}   # Unicode -> 拼音
        self.unihan_simplified = {}  # Unicode -> 简体字Unicode
        
    def char_to_unicode_str(self, char: str) -> str:
        """
        将汉字转换为 U+XXXX 格式
        :param char: 单个汉字
        :return: U+XXXX 格式字符串
        """
        if not char or len(char) == 0:
            return ""
        code_point = ord(char[0])
        return f"U+{code_point:04X}"
    
    def unicode_str_to_char(self, unicode_str: str) -> str:
        """
        将 U+XXXX 格式转换为汉字
        :param unicode_str: U+XXXX 格式字符串
        :return: 汉字
        """
        if not unicode_str or not unicode_str.startswith("U+"):
            return ""
        try:
            code_point = int(unicode_str[2:], 16)
            return chr(code_point)
        except (ValueError, OverflowError):
            return ""
    
    def load_unihan_strokes(self, file_path: str):
        """
        加载 Unihan_IRGSources.txt 中的笔画数据
        :param file_path: 文件路径
        """
        print(f"正在加载笔画数据: {file_path}")
        count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        unicode_str = parts[0]
                        field_type = parts[1]
                        
                        # 只处理 kTotalStrokes 字段
                        if field_type == 'kTotalStrokes':
                            # 笔画数可能有多个值，取第一个
                            strokes_str = parts[2].split()[0]
                            try:
                                strokes = int(strokes_str)
                                self.unihan_strokes[unicode_str] = strokes
                                count += 1
                            except ValueError:
                                pass
            
            print(f"  加载了 {count} 个汉字的笔画数据")
        except FileNotFoundError:
            print(f"  警告: 文件不存在 - {file_path}")
        except Exception as e:
            print(f"  错误: 加载失败 - {e}")
    
    def load_unihan_readings(self, file_path: str):
        """
        加载 Unihan_Readings.txt 中的拼音数据
        :param file_path: 文件路径
        """
        print(f"正在加载拼音数据: {file_path}")
        count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        unicode_str = parts[0]
                        field_type = parts[1]
                        
                        # 只处理 kMandarin 字段（普通话拼音）
                        if field_type == 'kMandarin':
                            # 拼音可能有多个，取第一个，并转为小写
                            pinyin = parts[2].split()[0].lower()
                            self.unihan_pinyin[unicode_str] = pinyin
                            count += 1
            
            print(f"  加载了 {count} 个汉字的拼音数据")
        except FileNotFoundError:
            print(f"  警告: 文件不存在 - {file_path}")
        except Exception as e:
            print(f"  错误: 加载失败 - {e}")
    
    def load_unihan_variants(self, file_path: str):
        """
        加载 Unihan_Variants.txt 中的简繁体对应关系
        :param file_path: 文件路径
        """
        print(f"正在加载简繁体数据: {file_path}")
        count = 0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        unicode_str = parts[0]
                        field_type = parts[1]
                        
                        # 只处理 kSimplifiedVariant 字段（简体字变体）
                        if field_type == 'kSimplifiedVariant':
                            # 简体字可能有多个，取第一个
                            simplified_unicode = parts[2].split()[0]
                            self.unihan_simplified[unicode_str] = simplified_unicode
                            count += 1
            
            print(f"  加载了 {count} 个汉字的简繁体对应关系")
        except FileNotFoundError:
            print(f"  警告: 文件不存在 - {file_path}")
        except Exception as e:
            print(f"  错误: 加载失败 - {e}")
    
    def load_kangxi_excel(self, file_path: str) -> List[str]:
        """
        加载康熙字典.xls文件的第一列汉字（或从.txt文件读取）
        :param file_path: Excel文件路径或txt文件路径
        :return: 汉字列表
        """
        print(f"正在加载康熙字典: {file_path}")
        
        # 如果是txt文件，直接读取
        file_path_obj = Path(file_path)
        txt_path = file_path_obj.parent / f"{file_path_obj.stem}.txt"
        
        if txt_path.exists():
            print(f"  发现文本格式文件: {txt_path.name}")
            try:
                with open(txt_path, 'r', encoding='utf-8') as f:
                    characters = [line.strip() for line in f if line.strip()]
                print(f"  成功加载 {len(characters)} 个汉字")
                if characters:
                    print(f"  示例: {', '.join(characters[:5])}")
                return characters
            except Exception as e:
                print(f"  警告: 文本文件读取失败 - {e}")
                print(f"  将尝试读取Excel文件...")
        
        try:
            # 尝试不同的方法读取Excel文件
            df = None
            last_error = None
            
            # 方法1: 尝试 openpyxl (适用于 .xlsx)
            try:
                df = pd.read_excel(file_path, header=None, engine='openpyxl')
                print(f"  使用引擎: openpyxl")
            except Exception as e1:
                last_error = e1
                
                # 方法2: 尝试 xlrd (适用于老版本 .xls)
                try:
                    import xlrd
                    # 使用 formatting_info=False 避免编码问题
                    df = pd.read_excel(file_path, header=None, engine='xlrd')
                    print(f"  使用引擎: xlrd")
                except Exception as e2:
                    last_error = e2
                    
                    # 方法3: 尝试使用 pyxlsb (二进制格式)
                    try:
                        df = pd.read_excel(file_path, header=None, engine='pyxlsb')
                        print(f"  使用引擎: pyxlsb")
                    except Exception as e3:
                        last_error = e3
                        
                        # 方法4: 尝试直接用 xlrd 读取并忽略格式
                        try:
                            import xlrd
                            workbook = xlrd.open_workbook(file_path, formatting_info=False, 
                                                         encoding_override='utf-8', 
                                                         on_demand=True)
                            sheet = workbook.sheet_by_index(0)
                            data = []
                            for row_idx in range(sheet.nrows):
                                row_data = []
                                for col_idx in range(sheet.ncols):
                                    try:
                                        cell = sheet.cell(row_idx, col_idx)
                                        row_data.append(cell.value)
                                    except:
                                        row_data.append(None)
                                data.append(row_data)
                            df = pd.DataFrame(data)
                            print(f"  使用引擎: xlrd (直接读取)")
                        except Exception as e4:
                            last_error = e4
            
            if df is None or df.empty:
                raise Exception(f"无法读取Excel文件\n最后的错误: {last_error}")
            
            print(f"  Excel维度: {df.shape[0]} 行 × {df.shape[1]} 列")
            
            # 获取第一列数据
            first_column = df.iloc[:, 0].tolist()
            
            # 过滤空值和非字符串值
            characters = []
            for idx, item in enumerate(first_column):
                if pd.notna(item):
                    # 转换为字符串
                    item_str = str(item)
                    if len(item_str) > 0:
                        # 只取每个单元格的第一个字符
                        char = item_str[0]
                        # 判断是否为CJK统一汉字
                        if '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf' or '\U00020000' <= char <= '\U0002a6df':
                            characters.append(char)
                        elif idx < 10:  # 只显示前10个非汉字的示例
                            print(f"  跳过第{idx+1}行非汉字数据: {repr(item_str[:20])}")
            
            print(f"  成功加载 {len(characters)} 个汉字")
            
            # 显示前5个汉字作为示例
            if characters:
                sample = characters[:5]
                print(f"  示例: {', '.join(sample)}")
            
            return characters
            
        except FileNotFoundError:
            print(f"  ✗ 错误: 文件不存在")
            print(f"     路径: {file_path}")
            return []
        except ImportError as e:
            print(f"  ✗ 错误: 缺少必要的库")
            print(f"     {e}")
            print(f"     请运行: pip install openpyxl xlrd")
            return []
        except Exception as e:
            print(f"  ✗ 错误: 加载失败")
            print(f"     详细信息: {type(e).__name__}: {e}")
            import traceback
            print(f"     {traceback.format_exc()}")
            return []
    
    def get_radical(self, char: str) -> str:
        """
        获取汉字部首（简单实现，可后续扩展）
        :param char: 汉字
        :return: 部首
        """
        # 这里可以添加更复杂的部首查询逻辑
        # 暂时返回空字符串，让后续手动填充或使用其他工具
        return ""
    
    def convert_character(self, traditional_char: str) -> Optional[Dict]:
        """
        转换单个汉字的所有信息
        :param traditional_char: 繁体字
        :return: 包含所有字段的字典
        """
        # 1. 获取 Unicode 编码
        unicode_str = self.char_to_unicode_str(traditional_char)
        if not unicode_str:
            return None
        
        # 2. 获取笔画数
        strokes = self.unihan_strokes.get(unicode_str, 0)
        if strokes == 0:
            print(f"  警告: {traditional_char} ({unicode_str}) 未找到笔画数据")
        
        # 3. 获取拼音
        pinyin = self.unihan_pinyin.get(unicode_str, "")
        if not pinyin:
            print(f"  警告: {traditional_char} ({unicode_str}) 未找到拼音数据")
        
        # 4. 获取简体字
        simplified_char = traditional_char  # 默认为繁体字本身
        
        if unicode_str in self.unihan_simplified:
            simplified_unicode = self.unihan_simplified[unicode_str]
            # 检查简体字是否与繁体字不同
            if simplified_unicode != unicode_str:
                simplified_char = self.unicode_str_to_char(simplified_unicode)
                if not simplified_char:
                    simplified_char = traditional_char
        
        # 5. 获取部首（暂时留空）
        radical = self.get_radical(traditional_char)
        
        return {
            "character": simplified_char,
            "traditional": traditional_char,
            "strokes": strokes,
            "pinyin": pinyin,
            "radical": radical
        }
    
    def convert_all(self, kangxi_excel: str, irg_sources: str, 
                   readings: str, variants: str, output_json: str):
        """
        执行完整的转换流程
        :param kangxi_excel: 康熙字典Excel文件路径
        :param irg_sources: Unihan_IRGSources.txt 路径
        :param readings: Unihan_Readings.txt 路径
        :param variants: Unihan_Variants.txt 路径
        :param output_json: 输出的JSON文件路径
        """
        print("=" * 60)
        print("康熙字典数据转换工具")
        print("=" * 60)
        
        # 1. 加载 Unihan 数据
        print("\n步骤 1: 加载 Unihan 数据库")
        self.load_unihan_strokes(irg_sources)
        self.load_unihan_readings(readings)
        self.load_unihan_variants(variants)
        
        # 2. 加载康熙字典汉字列表
        print("\n步骤 2: 加载康熙字典汉字列表")
        characters = self.load_kangxi_excel(kangxi_excel)
        
        if not characters:
            print("\n错误: 没有加载到任何汉字数据")
            return
        
        # 3. 转换每个汉字
        print(f"\n步骤 3: 转换 {len(characters)} 个汉字")
        converted_data = []
        success_count = 0
        skipped_no_pinyin = 0
        
        for i, char in enumerate(characters, 1):
            result = self.convert_character(char)
            if result:
                # 过滤掉没有拼音的字（通常是生僻字）
                if result.get('pinyin', ''):
                    converted_data.append(result)
                    success_count += 1
                else:
                    skipped_no_pinyin += 1
            
            # 每100个字显示一次进度
            if i % 100 == 0:
                print(f"  进度: {i}/{len(characters)} ({i*100//len(characters)}%)")
        
        print(f"  完成: 成功转换 {success_count}/{len(characters)} 个汉字")
        print(f"  跳过: {skipped_no_pinyin} 个无拼音的生僻字")
        
        # 4. 去重处理：如果简体字相同，保留繁简不同的
        print(f"\n步骤 4: 去重处理")
        unique_data = {}  # 使用字典，key为简体字
        duplicate_count = 0
        kept_count = 0
        
        for item in converted_data:
            simplified = item['character']
            traditional = item['traditional']
            
            if simplified not in unique_data:
                # 第一次出现，直接添加
                unique_data[simplified] = item
            else:
                # 简体字重复
                existing = unique_data[simplified]
                
                # 判断哪个是繁简相同的
                is_current_same = (simplified == traditional)
                is_existing_same = (existing['character'] == existing['traditional'])
                
                if is_current_same and not is_existing_same:
                    # 当前是繁简相同，已存在的是繁简不同 -> 删除当前，保留已存在
                    print(f"  重复汉字：删除 - {simplified}(简) {traditional}(繁)")
                    print(f"  重复汉字：保留 - {existing['character']}(简) {existing['traditional']}(繁)")
                    duplicate_count += 1
                elif not is_current_same and is_existing_same:
                    # 当前是繁简不同，已存在的是繁简相同 -> 删除已存在，保留当前
                    print(f"  重复汉字：删除 - {existing['character']}(简) {existing['traditional']}(繁)")
                    print(f"  重复汉字：保留 - {simplified}(简) {traditional}(繁)")
                    unique_data[simplified] = item
                    duplicate_count += 1
                elif is_current_same and is_existing_same:
                    # 都是繁简相同 -> 删除当前（保留第一个）
                    print(f"  重复汉字：删除 - {simplified}(简) {traditional}(繁)")
                    duplicate_count += 1
                else:
                    # 都是繁简不同 -> 保留笔画数更多的（通常是正字）
                    if item['strokes'] > existing['strokes']:
                        print(f"  重复汉字：删除 - {existing['character']}(简) {existing['traditional']}(繁) 笔画{existing['strokes']}")
                        print(f"  重复汉字：保留 - {simplified}(简) {traditional}(繁) 笔画{item['strokes']}")
                        unique_data[simplified] = item
                    else:
                        print(f"  重复汉字：删除 - {simplified}(简) {traditional}(繁) 笔画{item['strokes']}")
                        print(f"  重复汉字：保留 - {existing['character']}(简) {existing['traditional']}(繁) 笔画{existing['strokes']}")
                    duplicate_count += 1
        
        # 转换回列表
        converted_data = list(unique_data.values())
        kept_count = len(converted_data)
        
        print(f"  去重完成: 删除 {duplicate_count} 个重复，保留 {kept_count} 个唯一汉字")
        
        # 5. 保存为 JSON
        print(f"\n步骤 5: 保存到 {output_json}")
        output_data = {
            "version": "1.0",
            "description": "康熙字典笔画数据",
            "data": converted_data
        }
        
        try:
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            print(f"  成功: 已保存 {len(converted_data)} 条记录")
        except Exception as e:
            print(f"  错误: 保存失败 - {e}")
        
        print("\n" + "=" * 60)
        print("转换完成!")
        print("=" * 60)


def convert_xls_with_com():
    """使用 Windows COM 接口转换Excel（仅Windows）"""
    base_dir = Path(__file__).parent
    xls_path = base_dir / "predata" / "康熙字典.xls"
    txt_path = base_dir / "predata" / "康熙字典.txt"
    
    print("=" * 60)
    print("Excel转文本工具 (COM方式)")
    print("=" * 60)
    print(f"输入: {xls_path}")
    print(f"输出: {txt_path}")
    
    try:
        import win32com.client
        print("\n启动 Excel...")
        
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        
        # 打开工作簿
        workbook = excel.Workbooks.Open(str(xls_path.absolute()))
        sheet = workbook.Worksheets(1)
        
        # 获取使用的行数
        used_range = sheet.UsedRange
        rows = used_range.Rows.Count
        print(f"总行数: {rows}")
        
        # 提取第一列
        characters = []
        for i in range(1, rows + 1):
            try:
                value = sheet.Cells(i, 1).Value
                if value:
                    value_str = str(value).strip()
                    if value_str and len(value_str) > 0:
                        char = value_str[0]
                        if '\u4e00' <= char <= '\u9fff':
                            characters.append(char)
                
                if i % 1000 == 0:
                    print(f"  进度: {i}/{rows}")
            except Exception as e:
                if i < 10:
                    print(f"警告: 第{i}行读取失败 - {e}")
        
        # 关闭Excel
        workbook.Close(SaveChanges=False)
        excel.Quit()
        
        print(f"\n提取到 {len(characters)} 个汉字")
        
        # 保存到文本文件
        with open(txt_path, 'w', encoding='utf-8') as f:
            for char in characters:
                f.write(char + '\n')
        
        print(f"✓ 成功保存到: {txt_path}")
        print(f"  前10个字符: {''.join(characters[:10])}")
        
        return 0
        
    except ImportError:
        print("\n✗ 需要安装 pywin32 库")
        print("  运行: pip install pywin32")
        return 1
    except Exception as e:
        print(f"\n✗ 转换失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


def convert_xls_to_txt():
    """将 Excel 文件转换为纯文本格式（备选方案）"""
    base_dir = Path(__file__).parent
    xls_path = base_dir / "predata" / "康熙字典.xls"
    
    print("=" * 60)
    print("Excel文件转换助手")
    print("=" * 60)
    print(f"\nExcel文件: {xls_path}")
    print(f"文件大小: {xls_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    print("\n检测到Excel文件存在编码问题。")
    print("请选择转换方式：\n")
    print("1. 使用 Windows COM（需要安装 Excel）")
    print("2. 手动转换（推荐）")
    print("3. 查看帮助文档")
    print()
    
    choice = input("请选择 (1/2/3): ").strip()
    
    if choice == '1':
        return convert_xls_with_com()
    elif choice == '2':
        print("\n" + "=" * 60)
        print("手动转换步骤:")
        print("=" * 60)
        print("1. 用 Microsoft Excel 打开文件:")
        print(f"   {xls_path}")
        print("2. 选择第一列的所有数据")
        print("3. 复制后粘贴到记事本")
        print("4. 保存为:")
        print(f"   {xls_path.parent / '康熙字典.txt'}")
        print("   （使用 UTF-8 编码）")
        print("\n完成后重新运行: python convert_tools.py")
        return 0
    elif choice == '3':
        help_file = base_dir / "KANGXI_CONVERT_HELP.md"
        print(f"\n请查看帮助文档: {help_file}")
        return 0
    else:
        print("无效选择")
        return 1


class LunarConverter:
    """万年历数据转换器"""
    
    def convert_lunar_sql_to_json(self, sql_path: str, output_json: str):
        """
        将 lunar.sql 转换为 wannianli.json
        :param sql_path: lunar.sql 文件路径
        :param output_json: 输出的 JSON 文件路径
        """
        print("=" * 60)
        print("万年历数据转换工具")
        print("=" * 60)
        print(f"输入: {sql_path}")
        print(f"输出: {output_json}")
        
        if not Path(sql_path).exists():
            print(f"\n✗ 错误: 文件不存在 - {sql_path}")
            return False
        
        print("\n正在解析 SQL 文件...")
        
        records = []
        
        try:
            with open(sql_path, 'r', encoding='utf-8') as f:
                line_count = 0
                for line in f:
                    line_count += 1
                    
                    # 跳过注释和空行
                    line_stripped = line.strip()
                    if not line_stripped or line_stripped.startswith('--') or line_stripped.startswith('/*') or line_stripped.startswith('SET') or line_stripped.startswith('DROP') or line_stripped.startswith('CREATE'):
                        continue
                    
                    # 检查是否是 INSERT 语句
                    if not line_stripped.upper().startswith('INSERT INTO'):
                        continue
                    
                    # 找到 VALUES 后的括号
                    values_start = line.find('VALUES (')
                    if values_start == -1:
                        values_start = line.find('VALUES(')
                        if values_start == -1:
                            continue
                        values_start += 7  # len('VALUES(')
                    else:
                        values_start += 8  # len('VALUES (')
                    
                    # 找到最后的分号前的右括号
                    values_end = line.rfind(');')
                    if values_end == -1:
                        continue
                    
                    # 提取值部分
                    values_str = line[values_start:values_end]
                    
                    # 解析值（处理引号和逗号）
                    values = self._parse_sql_values(values_str)
                    
                    if len(values) >= 29:  # 确保有足够的字段
                            record = {
                                'gregorian_date': values[0],  # 公历时间
                                'lunar_date': values[1],      # 农历时间（YYYY-MM-DD格式）
                                'lunar_show': values[2],       # 显示农历的日名称
                                'is_holiday': values[3] == '1',  # 是否节假日
                                'lunar_festival': values[4],   # 农历节日
                                'gregorian_festival': values[5],  # 公历节日
                                'yi': values[6],              # 宜
                                'ji': values[7],              # 忌
                                'shen_wei': values[8],        # 诸神位置
                                'tai_shen': values[9],        # 胎神位置
                                'chong': values[10],          # 冲煞
                                'sui_sha': values[11],        # 岁煞
                                'wuxing_jiazi': values[12],   # 甲子五行
                                'wuxing_year': values[13],    # 纳音五行年
                                'wuxing_month': values[14],   # 纳音五行月
                                'wuxing_day': values[15],     # 纳音五行日
                                'moon_phase': values[16],     # 月相
                                'star_east': values[17],      # 二十八星宿
                                'star_west': values[18],      # 星座
                                'peng_zu': values[19],        # 彭祖百忌
                                'jian_shen': values[20],      # 十二神-执位
                                'year_ganzhi': values[21],    # 天干地支年
                                'month_ganzhi': values[22],   # 天干地支月
                                'day_ganzhi': values[23],     # 天干地支日
                                'lunar_month_name': values[24],  # 农历月代名词
                                'zodiac': values[25],         # 生肖
                                'lunar_month': values[26],    # 农历月
                                'lunar_day': values[27],      # 农历日
                                'solar_term': values[28] if len(values) > 28 else '',  # 节气
                            }
                            records.append(record)
                    
                    # 每10000行显示进度
                    if line_count % 10000 == 0:
                        print(f"  已处理: {line_count} 行，解析出: {len(records)} 条记录")
            
            print(f"\n✓ 解析完成")
            print(f"  总行数: {line_count}")
            print(f"  有效记录数: {len(records)}")
            
            if records:
                # 显示日期范围
                first_date = records[0]['gregorian_date']
                last_date = records[-1]['gregorian_date']
                print(f"  日期范围: {first_date} 至 {last_date}")
                
                # 显示示例记录
                print(f"\n示例记录（第1条）:")
                sample = records[0]
                print(f"  公历: {sample['gregorian_date']}")
                print(f"  农历: {sample['lunar_date']} ({sample['lunar_month']}{sample['lunar_day']})")
                print(f"  干支: {sample['year_ganzhi']}年 {sample['month_ganzhi']}月 {sample['day_ganzhi']}日")
                print(f"  生肖: {sample['zodiac']}")
                if sample['solar_term']:
                    print(f"  节气: {sample['solar_term']}")
                if sample['gregorian_festival']:
                    print(f"  节日: {sample['gregorian_festival']}")
            
            # 保存为 JSON
            print(f"\n正在保存到 {output_json}...")
            output_data = {
                "version": "1.0",
                "description": "万年历数据（1970-2100）",
                "source": "lunar.sql",
                "date_range": {
                    "start": records[0]['gregorian_date'] if records else "",
                    "end": records[-1]['gregorian_date'] if records else ""
                },
                "total_records": len(records),
                "data": records
            }
            
            # 创建输出目录
            Path(output_json).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 成功保存 {len(records)} 条记录")
            
            return True
            
        except Exception as e:
            print(f"\n✗ 转换失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _parse_sql_values(self, values_str: str) -> List[str]:
        """
        解析 SQL VALUES 子句中的值
        :param values_str: VALUES 中的字符串（不含括号）
        :return: 值列表
        """
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        i = 0
        
        while i < len(values_str):
            char = values_str[i]
            
            if not in_quotes:
                if char in ("'", '"'):
                    # 开始引号
                    in_quotes = True
                    quote_char = char
                    i += 1
                elif char == ',' and current_value.strip():
                    # 字段分隔符（确保有内容才分隔）
                    values.append(current_value.strip())
                    current_value = ""
                    i += 1
                elif char == ',' and not current_value.strip():
                    # 空字段
                    values.append("")
                    i += 1
                elif char == ' ' and not current_value:
                    # 跳过前导空格
                    i += 1
                else:
                    # 普通字符（NULL等）
                    current_value += char
                    i += 1
            else:
                if char == quote_char:
                    # 检查是否是转义的引号
                    if i + 1 < len(values_str) and values_str[i + 1] == quote_char:
                        # 转义的引号，添加一个引号
                        current_value += quote_char
                        i += 2
                    else:
                        # 结束引号
                        in_quotes = False
                        quote_char = None
                        i += 1
                elif char == '\\' and i + 1 < len(values_str):
                    # 转义字符
                    next_char = values_str[i + 1]
                    if next_char == 'n':
                        current_value += '\n'
                    elif next_char == 't':
                        current_value += '\t'
                    elif next_char == 'r':
                        current_value += '\r'
                    elif next_char == '\\':
                        current_value += '\\'
                    elif next_char in ("'", '"'):
                        current_value += next_char
                    else:
                        current_value += next_char
                    i += 2
                else:
                    current_value += char
                    i += 1
        
        # 添加最后一个值
        values.append(current_value.strip())
        
        return values


def test_single_character():
    """测试单个汉字转换（用于调试）"""
    base_dir = Path(__file__).parent
    
    irg_sources = base_dir / "predata" / "Unihan" / "Unihan_IRGSources.txt"
    readings = base_dir / "predata" / "Unihan" / "Unihan_Readings.txt"
    variants = base_dir / "predata" / "Unihan" / "Unihan_Variants.txt"
    
    print("=" * 60)
    print("单字符测试模式")
    print("=" * 60)
    
    converter = KangxiConverter()
    
    # 加载必要数据
    if irg_sources.exists():
        converter.load_unihan_strokes(str(irg_sources))
    if readings.exists():
        converter.load_unihan_readings(str(readings))
    if variants.exists():
        converter.load_unihan_variants(str(variants))
    
    # 测试几个常见汉字
    test_chars = ["劉", "张", "王", "李", "陳"]
    
    print("\n测试结果:")
    for char in test_chars:
        result = converter.convert_character(char)
        if result:
            print(f"\n  繁体字: {char}")
            print(f"  简体字: {result['character']}")
            print(f"  笔画数: {result['strokes']}")
            print(f"  拼音: {result['pinyin']}")
            unicode_str = converter.char_to_unicode_str(char)
            print(f"  Unicode: {unicode_str}")


def convert_lunar_sql():
    """转换万年历 SQL 文件为 JSON"""
    base_dir = Path(__file__).parent
    
    sql_path = base_dir / "predata" / "lunar.sql"
    output_json = base_dir / "data" / "wannianli.json"
    
    if not sql_path.exists():
        print(f"✗ 错误: 文件不存在 - {sql_path}")
        return 1
    
    converter = LunarConverter()
    success = converter.convert_lunar_sql_to_json(str(sql_path), str(output_json))
    
    return 0 if success else 1


def show_help():
    """显示帮助信息"""
    print("=" * 60)
    print("数据转换工具")
    print("=" * 60)
    print("\n用法:")
    print("  python convert_tools.py [选项]")
    print("\n选项:")
    print("  --help, -h            显示此帮助信息")
    print("  --test                测试单个汉字转换")
    print("  --convert-xls         转换康熙字典 Excel 文件")
    print("  --convert-with-com    使用 COM 转换 Excel（仅Windows）")
    print("  --convert-lunar       转换万年历 SQL 文件为 JSON")
    print("  （无参数）            转换康熙字典（默认）")
    print("\n示例:")
    print("  python convert_tools.py --convert-lunar")
    print("  python convert_tools.py --test")
    print("\n文件说明:")
    print("  输入文件:")
    print("    - predata/康熙字典.xls         康熙字典数据")
    print("    - predata/Unihan/*.txt         Unicode 汉字数据库")
    print("    - predata/lunar.sql            万年历数据（1970-2099）")
    print("\n  输出文件:")
    print("    - data/kangxi_converted.json   康熙字典 JSON")
    print("    - data/wannianli.json          万年历 JSON")
    print("=" * 60)


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] in ('--help', '-h'):
            show_help()
            return 0
        elif sys.argv[1] == '--test':
            return test_single_character()
        elif sys.argv[1] == '--convert-xls' or sys.argv[1] == '--convert':
            return convert_xls_to_txt()
        elif sys.argv[1] == '--convert-with-com':
            return convert_xls_with_com()
        elif sys.argv[1] == '--convert-lunar' or sys.argv[1] == '--lunar':
            return convert_lunar_sql()
        else:
            print(f"未知选项: {sys.argv[1]}")
            print("使用 --help 查看帮助")
            return 1
    
    # 定义文件路径
    base_dir = Path(__file__).parent
    
    kangxi_excel = base_dir / "predata" / "康熙字典.xls"
    irg_sources = base_dir / "predata" / "Unihan" / "Unihan_IRGSources.txt"
    readings = base_dir / "predata" / "Unihan" / "Unihan_Readings.txt"
    variants = base_dir / "predata" / "Unihan" / "Unihan_Variants.txt"
    output_json = base_dir / "data" / "kangxi_converted.json"
    
    # 检查必需文件是否存在
    print("检查源文件...")
    print(f"工作目录: {base_dir}")
    print()
    
    all_exist = True
    for file_path, name in [
        (kangxi_excel, "康熙字典.xls"),
        (irg_sources, "Unihan_IRGSources.txt"),
        (readings, "Unihan_Readings.txt"),
        (variants, "Unihan_Variants.txt")
    ]:
        if file_path.exists():
            size = file_path.stat().st_size
            size_mb = size / 1024 / 1024
            print(f"  ✓ {name}")
            print(f"    大小: {size_mb:.2f} MB")
        else:
            print(f"  ✗ {name}")
            print(f"    期望路径: {file_path}")
            # 检查父目录是否存在
            if not file_path.parent.exists():
                print(f"    父目录不存在: {file_path.parent}")
            all_exist = False
    
    if not all_exist:
        print("\n" + "="*60)
        print("错误: 部分源文件缺失")
        print("="*60)
        print("\n请确保以下目录结构:")
        print("  predata/")
        print("  ├── 康熙字典.xls")
        print("  └── Unihan/")
        print("      ├── Unihan_IRGSources.txt")
        print("      ├── Unihan_Readings.txt")
        print("      └── Unihan_Variants.txt")
        print("\nUnihan数据库下载地址:")
        print("  https://www.unicode.org/Public/UNIDATA/Unihan.zip")
        return 1
    
    # 创建输出目录
    output_json.parent.mkdir(parents=True, exist_ok=True)
    
    # 执行转换
    converter = KangxiConverter()
    converter.convert_all(
        str(kangxi_excel),
        str(irg_sources),
        str(readings),
        str(variants),
        str(output_json)
    )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
