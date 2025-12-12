import argparse
import json
from modules.company_calculator import CompanyCalculator
from modules.storage import Storage

VERSION = "0.3.0-company"


def main():
    parser = argparse.ArgumentParser(description="公司版名称分析 CLI")
    parser.add_argument('-c', '--company', action='store_true', help='启动公司名称测试（预留）')
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

    calc = CompanyCalculator()
    storage = Storage()
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

    # 仅实现批量与导出，符合SRD的 -bc 流程
    if args.company_batch:
        file_path = args.company_batch
        default_bazi = {'xiyong_shen': ['木', '水'], 'ji_shen': ['土'], 'bazi_match_score': 75}
        if file_path.lower().endswith('.csv'):
            import csv
            results = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    full_name = ''.join(filter(None, [row.get('行政区划','').strip(), row.get('字号(主名)','').strip(), row.get('行业/经营特点','').strip(), row.get('组织形式','').strip()]))
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
                    result_row = calc.analyze_single(full_name, bazi_info_row)
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
            output = results
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f if line.strip()]
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

        if args.export_company:
            with open(args.export_company, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"已导出到 {args.export_company}")
        else:
            print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    # 其他模式暂不实现，提示使用 -bc
    print('请使用 -bc FILE 进行批量测试（支持CSV/TXT）')


if __name__ == '__main__':
    main()
