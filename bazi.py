#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
姓名测试软件 - 主程序入口
Author: Auto Generated
Date: 2025-12-03
"""

import sys
import argparse
import logging
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.loader import DataLoader
from modules.ui import UserInterface
from modules.helper import Helper

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='姓名测试软件 - 基于传统命理学的姓名分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python bazi.py              # 启动交互界面
  python bazi.py -t           # 启动姓名测试
  python bazi.py -b names.txt # 批量处理模式
  python bazi.py -v           # 显示版本信息
  python bazi.py --reload-data     # 重新加载数据
  python bazi.py --clear-history   # 清空历史记录
  python bazi.py --clear-all-data  # 清空所有数据表
  python bazi.py --show-tables     # 显示数据表统计
  python bazi.py --geo-help        # 显示经纬度查询帮助
        """
    )
    parser.add_argument('-t', '--test', action='store_true', help='开始姓名测试')
    parser.add_argument('-v', '--version', action='store_true', help='显示版本信息')
    parser.add_argument('-b', '--batch', type=str, metavar='FILE', help='批量处理模式，从文件读取姓名信息')
    parser.add_argument('--reload-data', action='store_true', help='重新加载资源数据')
    parser.add_argument('--clear-history', action='store_true', help='清空所有历史计算结果')
    parser.add_argument('--clear-all-data', action='store_true', help='清空所有数据表（包括资源数据）')
    parser.add_argument('--show-tables', action='store_true', help='显示所有数据表统计信息')
    parser.add_argument('--geo-help', action='store_true', help='显示经纬度查询帮助')
    
    args = parser.parse_args()
    
    try:
        # 显示版本信息
        if args.version:
            print("姓名测试软件 v1.0")
            print("基于传统命理学的姓名分析工具")
            print("Copyright © 2025")
            return 0
        
        # 显示经纬度帮助信息
        if args.geo_help:
            Helper.show_help()
            return 0
        
        # 显示数据表统计信息
        if args.show_tables:
            from modules.storage import Storage
            storage = Storage()
            tables_info = storage.get_all_tables_info()
            
            if not tables_info:
                print("\n数据库中没有数据表")
                return 0
            
            print("\n数据表统计信息:")
            print("=" * 60)
            
            # 分类显示
            resource_tables = ['kangxi', 'ziyi', 'nayin', 'shuli', 'sancai', 
                             'shengxiao', 'chenggu', 'wannianli']
            result_tables = ['test_records', 'wuge_results', 'bazi_results', 
                           'ziyi_results', 'shengxiao_results', 'chenggu_results']
            
            print("\n资源数据表:")
            total_resource = 0
            for table in resource_tables:
                if table in tables_info:
                    count = tables_info[table]
                    total_resource += count
                    print(f"  {table:20s}: {count:>8,} 条")
            
            print(f"\n历史记录表:")
            total_result = 0
            for table in result_tables:
                if table in tables_info:
                    count = tables_info[table]
                    total_result += count
                    print(f"  {table:20s}: {count:>8,} 条")
            
            print("\n" + "=" * 60)
            print(f"资源数据总计: {total_resource:>8,} 条")
            print(f"历史记录总计: {total_result:>8,} 条")
            return 0
        
        # 清空历史记录
        if args.clear_history:
            from modules.storage import Storage
            storage = Storage()
            count = storage.get_records_count()
            if count == 0:
                print("\n当前没有历史记录")
                return 0
            
            print(f"\n当前共有 {count} 条历史记录")
            confirm = input("确认清空所有历史记录？(yes/no): ").strip().lower()
            if confirm in ['yes', 'y', '是']:
                if storage.clear_all_records():
                    print("✓ 历史记录已清空")
                    logger.info("用户清空了历史记录")
                else:
                    print("✗ 清空失败，请查看日志")
                    return 1
            else:
                print("操作已取消")
            return 0
        
        # 清空所有数据表
        if args.clear_all_data:
            from modules.storage import Storage
            storage = Storage()
            tables_info = storage.get_all_tables_info()
            
            if not tables_info:
                print("\n数据库中没有数据")
                return 0
            
            print("\n⚠️  警告：此操作将清空所有数据表！")
            print("=" * 60)
            for table, count in sorted(tables_info.items()):
                print(f"  {table:20s}: {count:>8,} 条")
            print("=" * 60)
            
            total = sum(tables_info.values())
            print(f"\n总计将删除 {total:,} 条记录")
            print("此操作不可恢复，请谨慎操作！\n")
            
            confirm = input("确认清空所有数据表？请输入 'DELETE ALL' 确认: ").strip()
            if confirm == 'DELETE ALL':
                print("\n正在清空数据表...")
                if storage.clear_all_data():
                    print("✓ 所有数据表已清空")
                    print("提示: 使用 --reload-data 重新加载资源数据")
                    logger.warning("用户清空了所有数据表")
                else:
                    print("✗ 清空失败，请查看日志")
                    return 1
            else:
                print("操作已取消")
            return 0
        
        # 初始化数据加载器
        logger.info("初始化数据加载器...")
        loader = DataLoader()
        
        # 重新加载数据
        if args.reload_data:
            logger.info("开始重新加载资源数据...")
            result = loader.load_all_resources(force_reload=True)
            if result['success']:
                logger.info("资源数据加载成功")
                print("\n资源数据加载完成！")
                for resource, stats in result['statistics'].items():
                    print(f"  {resource}: 成功 {stats['success']}, 失败 {stats['failed']}")
            else:
                logger.error("资源数据加载失败")
                print("\n资源数据加载失败，请检查日志文件")
                return 1
        else:
            # 检查资源完整性
            integrity = loader.check_resource_integrity()
            if not integrity['complete']:
                logger.warning("资源数据不完整，开始自动加载...")
                result = loader.load_all_resources(force_reload=False)
                if not result['success']:
                    logger.error("资源数据加载失败")
                    print("\n错误：资源数据加载失败，请使用 --reload-data 参数重新加载")
                    return 1
        
        # 批量处理模式
        if args.batch:
            logger.info(f"启动批量处理模式，输入文件: {args.batch}")
            from modules.calculator import Calculator
            from modules.storage import Storage
            from modules.batch_processor import BatchProcessor
            
            calculator = Calculator()
            storage = Storage()
            processor = BatchProcessor(calculator, storage)
            
            result = processor.process_file(args.batch)
            if result['success']:
                print(f"\n✓ 批量处理完成")
                print(f"  成功: {result['success_count']} 条")
                print(f"  失败: {result['failed_count']} 条")
                print(f"  结果已保存到: {result['output_file']}")
            else:
                print(f"\n✗ 批量处理失败: {result.get('error', '未知错误')}")
                return 1
            return 0
        
        # 启动交互界面
        if args.test or len(sys.argv) == 1:
            logger.info("启动用户界面...")
            from modules.calculator import Calculator
            from modules.storage import Storage
            
            calculator = Calculator()
            storage = Storage()
            ui = UserInterface(calculator, storage)
            ui.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n程序已中断")
        return 0
    except Exception as e:
        logger.exception(f"程序运行出错: {e}")
        print(f"\n错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
