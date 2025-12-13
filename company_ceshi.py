import argparse
import json
import os
from pathlib import Path
from modules.company_calculator import CompanyCalculator
from modules.storage import Storage

VERSION = "0.3.0-company"


def main():
    parser = argparse.ArgumentParser(description="公司版名称分析 CLI")
    parser.add_argument('-c', '--company', action='store_true', help='启动公司名称测试')
    parser.add_argument('-bc', '--company-batch', type=str, metavar='FILE', help='公司名称批量处理（CSV或TXT）')
    parser.add_argument('-cc', '--company-compare', action='store_true', help='公司名方案对比模式（预留）')
    parser.add_argument('--company-history', action='store_true', help='查看公司测试历史记录')
    parser.add_argument('--clear-history', action='store_true', help='清空所有历史记录')
    parser.add_argument('--export-company', type=str, metavar='FILE', help='导出公司测试结果到JSON文件')
    parser.add_argument('--industry-help', action='store_true', help='显示行业五行对照表')
    parser.add_argument('-v', '--version', action='store_true', help='显示版本信息')

    args = parser.parse_args()
    if args.version:
        print(VERSION)
        return

    # 确保从项目根目录查找数据库
    script_dir = Path(__file__).parent
    db_path = script_dir / 'local.db'
    calc = CompanyCalculator(db_path=str(db_path))
    storage = Storage(db_path=str(db_path))
    if args.industry_help:
        print(calc.industry_analyzer.show_help_table())
        return

    # 历史查询
    if args.company_history:
        history = storage.get_company_history(limit=20)
        if not history:
            print('暂无公司历史记录')
            return
        # 简洁打印
        for item in history:
            print(f"[{item['id']}] {item['full_name']} | 行业: {item.get('industry_type') or '-'} | 负责人: {item.get('owner_name') or '-'} | 综合:{item.get('total_score')}/{item.get('grade') or '-'} | 五格:{item.get('wuge_score') or '-'} | 喜用:{item.get('xiyong_match_score') or '-'} | 时间:{item.get('created_at')}")
        return

    # 清空历史
    if args.clear_history:
        deleted = storage.clear_company_history()
        print(f'已清空公司历史记录，共 {deleted} 条')
        return

    # 交互式公司测试
    if args.company:
        print("交互式公司名称测试：按提示输入信息。")
        prefix_name = input("行政区划（如：北京、上海、深圳等）：").strip()
        main_name = input("字号（主名，例如：泽腾）：").strip()
        suffix_name = input("行业/经营特点（例如：科技、餐饮、贸易等）：").strip()
        form_org = input("组织形式（例如：有限公司、集团、股份有限公司等）：").strip()
        owner_name = input("负责人姓名（可选）：").strip()
        owner_gender = input("负责人性别（必填，男/女）：").strip()
        birth = input("负责人出生时间（YYYY-MM-DD HH:MM，必填）：").strip()
        lon_str = input("出生地经度（东经，必填）：").strip()
        lat_str = input("出生地纬度（北纬，必填）：").strip()

        # 基础校验
        def _is_chinese_only(s: str) -> bool:
            return all('\u4e00' <= ch <= '\u9fff' or ch == '·' for ch in s)

        # 校验四段名称
        for label, part in [("行政区划", prefix_name), ("字号(主名)", main_name), ("行业/经营特点", suffix_name), ("组织形式", form_org)]:
            if part and not _is_chinese_only(part):
                print(f"错误：{label} 只能包含汉字和'·'字符。")
                return
        if owner_gender not in ('男', '女'):
            print("错误：负责人性别必须为 男 或 女。")
            return
        # 解析与八字
        try:
            lon = float(lon_str)
            lat = float(lat_str)
        except Exception:
            print("错误：经纬度格式不正确，应为小数形式。")
            return
        # 经纬度范围
        if not (73 <= lon <= 135) or not (18 <= lat <= 54):
            print("警告：经纬度不在中国境内范围，计算可能不准确。")
        try:
            bazi_info = calc.build_bazi_info(birth, lon, lat)
            # 构造公司全称（由用户输入四段组成）
            full_name = ''.join(filter(None, [prefix_name, main_name, suffix_name, form_org]))
            # 新签名：prefix, main, suffix, form, full_name, bazi_info
            result = calc.analyze_single(prefix_name, main_name, suffix_name, form_org, full_name, bazi_info)
            result['owner'] = {
                'name': owner_name,
                'gender': owner_gender,
                'birth_time': birth,
                'longitude': lon,
                'latitude': lat
            }
            record_id = storage.save_company_result(result)
            if record_id:
                result['record_id'] = record_id
        except Exception as e:
            print(f"计算失败：{e}")
            return

        # 标准化展示
        parsed = result.get('parsed', {})
        print("\n—— 公司名称结构 ——")
        print(f"字号：{parsed.get('main_name','-')}")
        print(f"全称：{parsed.get('full_name','-')}")

        # 逐字清单：直接使用计算结果中的 char_details，避免查询失败导致空白
        print("\n—— 名称逐字清单 ——")
        print("字  繁体  拼音  笔画  五行  凶吉")
        char_details = result.get('char_details', {})
        for item in char_details.get('full_name', []) or []:
            print(f"{item.get('char','-')}  {item.get('traditional', item.get('char','-'))}  {item.get('pinyin','-')}  {item.get('strokes','-')}  {item.get('element','-')}  {item.get('luck','-')}")

        print("\n—— 三才五格（主名） ——")
        wm = result.get('wuge_main', {})
        print(f"天格({wm.get('tiange',{}).get('num','-')}/{wm.get('tiange',{}).get('element','-')}/{wm.get('tiange',{}).get('fortune','-')}) 人格({wm.get('renge',{}).get('num','-')}/{wm.get('renge',{}).get('element','-')}/{wm.get('renge',{}).get('fortune','-')}) 地格({wm.get('dige',{}).get('num','-')}/{wm.get('dige',{}).get('element','-')}/{wm.get('dige',{}).get('fortune','-')}) 外格({wm.get('waige',{}).get('num','-')}/{wm.get('waige',{}).get('element','-')}/{wm.get('waige',{}).get('fortune','-')}) 总格({wm.get('zongge',{}).get('num','-')}/{wm.get('zongge',{}).get('element','-')}/{wm.get('zongge',{}).get('fortune','-')})")
        print(wm.get('sancai_meaning',''))

        print("\n—— 三才五格（全称） ——")
        wf = result.get('wuge_full', {})
        print(f"天格({wf.get('tiange',{}).get('num','-')}/{wf.get('tiange',{}).get('element','-')}/{wf.get('tiange',{}).get('fortune','-')}) 人格({wf.get('renge',{}).get('num','-')}/{wf.get('renge',{}).get('element','-')}/{wf.get('renge',{}).get('fortune','-')}) 地格({wf.get('dige',{}).get('num','-')}/{wf.get('dige',{}).get('element','-')}/{wf.get('dige',{}).get('fortune','-')}) 外格({wf.get('waige',{}).get('num','-')}/{wf.get('waige',{}).get('element','-')}/{wf.get('waige',{}).get('fortune','-')}) 总格({wf.get('zongge',{}).get('num','-')}/{wf.get('zongge',{}).get('element','-')}/{wf.get('zongge',{}).get('fortune','-')})")
        print(wf.get('sancai_meaning',''))

        sc = result.get('scores', {})
        print("\n—— 综合评分 ——")
        print(f"综合评分：{sc.get('total_score','-')} 评级：{sc.get('grade','-')}")
        print(f"五格：{sc.get('wuge_score','-')} 行业：{sc.get('industry_score','-')} 八字：{sc.get('bazi_match_score','-')} 喜用匹配度：{sc.get('xiyong_match_score','-')} 生肖：{sc.get('shengxiao_score','-')} 字义：{sc.get('ziyi_score','-')}")
        return

    # 仅实现批量与导出，符合SRD的 -bc 流程
    if args.company_batch:
        file_path = args.company_batch
        default_bazi = {'xiyong_shen': ['木', '水'], 'ji_shen': ['土'], 'bazi_match_score': 75}
        if file_path.lower().endswith('.csv'):
            import csv
            results = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    if count >= 5:
                        break
                    # 使用数据文件中的公司名称字段，不做程序内拼接/拆分
                    full_name = (row.get('公司全称','') or row.get('公司名称','') or row.get('企业名称','') or '').strip()
                    # 若数据文件未提供统一的全称字段，才回退到拼接（保持兼容老格式）
                    if not full_name:
                        full_name = ''.join(filter(None, [
                            row.get('行政区划','').strip(),
                            row.get('字号(主名)','').strip(),
                            row.get('行业/经营特点','').strip(),
                            row.get('组织形式','').strip()
                        ]))
                    birth = row.get('出生时间','').strip()
                    lon = row.get('经度','').strip()
                    lat = row.get('纬度','').strip()
                    owner_name = row.get('负责人姓名','').strip()
                    owner_gender = row.get('负责人性别','').strip()
                    industry_type = row.get('行业类型','').strip()
                    if birth and lon and lat:
                        try:
                            bazi_info_row = calc.build_bazi_info(birth, float(lon), float(lat))
                        except Exception:
                            bazi_info_row = default_bazi
                    else:
                        bazi_info_row = default_bazi
                    # 为生肖分析提供日期回退：即使未能计算八字，也保留出生日期字符串
                    if 'birth_time' not in bazi_info_row and birth:
                        bazi_info_row['birth_time'] = birth
                    result_row = calc.analyze_single(row.get('行政区划','').strip(),
                                                     row.get('字号(主名)','').strip(), 
                                                     row.get('行业/经营特点','').strip(), 
                                                     row.get('组织形式','').strip(), 
                                                     full_name,bazi_info_row)
                    # 附加负责人信息与行业类型到结果，便于后续持久化与审计
                    result_row['owner'] = {
                        'name': owner_name,
                        'gender': owner_gender,
                        'birth_time': birth,
                        'longitude': lon,
                        'latitude': lat
                    }
                    if industry_type:
                        result_row['parsed']['industry_type'] = industry_type
                    # 落库
                    try:
                        record_id = storage.save_company_result(result_row)
                        if record_id:
                            result_row['record_id'] = record_id
                    except Exception:
                        pass
                    results.append(result_row)
                    count += 1
            output = results
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f if line.strip()][:4]
            out_items = calc.batch_analyze(names, default_bazi)
            # 批量落库
            output = []
            for item in out_items:
                try:
                    record_id = storage.save_company_result(item)
                    if record_id:
                        item['record_id'] = record_id
                except Exception:
                    pass
                output.append(item)

        # 自动导出到默认文件
        if not args.export_company:
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            args.export_company = f'tests/out_company_batch_{len(output)}.json'
        
        with open(args.export_company, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        print(f"\n批量测试完成，共处理 {len(output)} 条")
        print(f"结果已保存到: {args.export_company}")
        print("\n评分摘要:")
        for i, item in enumerate(output, 1):
            name = item.get('parsed', {}).get('full_name', '未知')
            score = item.get('scores', {}).get('total_score', 0)
            grade = item.get('scores', {}).get('grade', '-')
            print(f"  {i}. {name}: {score}分 ({grade})")
        return

    # 其他模式暂不实现，提示使用 -bc
    print('请使用 -bc FILE 进行批量测试（支持CSV/TXT）')


if __name__ == '__main__':
    main()
