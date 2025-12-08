#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量处理结果查看工具
用法: python tests/view_batch_result.py tests/example_input_result_20251206_213416.json
"""

import json
import sys
from pathlib import Path


def format_wuge(wuge):
    """格式化五格信息"""
    lines = []
    lines.append("  【三才五格】")
    
    # 五格评分标记
    def ge_mark(fortune):
        if '吉' in fortune:
            return '[+]'
        elif '凶' in fortune:
            return '[-]'
        else:
            return '[~]'
    
    lines.append(f"    天格 {wuge['tiange']['num']}数({wuge['tiange']['element']}) {ge_mark(wuge['tiange']['fortune'])} {wuge['tiange']['fortune']}")
    if wuge['tiange'].get('meaning'):
        lines.append(f"      → {wuge['tiange']['meaning']}")
    
    lines.append(f"    人格 {wuge['renge']['num']}数({wuge['renge']['element']}) {ge_mark(wuge['renge']['fortune'])} {wuge['renge']['fortune']}")
    if wuge['renge'].get('meaning'):
        lines.append(f"      → {wuge['renge']['meaning']}")
    
    lines.append(f"    地格 {wuge['dige']['num']}数({wuge['dige']['element']}) {ge_mark(wuge['dige']['fortune'])} {wuge['dige']['fortune']}")
    if wuge['dige'].get('meaning'):
        lines.append(f"      → {wuge['dige']['meaning']}")
    
    lines.append(f"    外格 {wuge['waige']['num']}数({wuge['waige']['element']}) {ge_mark(wuge['waige']['fortune'])} {wuge['waige']['fortune']}")
    if wuge['waige'].get('meaning'):
        lines.append(f"      → {wuge['waige']['meaning']}")
    
    lines.append(f"    总格 {wuge['zongge']['num']}数({wuge['zongge']['element']}) {ge_mark(wuge['zongge']['fortune'])} {wuge['zongge']['fortune']}")
    if wuge['zongge'].get('meaning'):
        lines.append(f"      → {wuge['zongge']['meaning']}")
    
    lines.append(f"    三才: {wuge['sancai']}")
    if wuge.get('sancai_meaning'):
        lines.append(f"      → {wuge['sancai_meaning']}")
    
    lines.append(f"    评分: {wuge['score']}分")
    return "\n".join(lines)


def format_bazi(bazi):
    """格式化八字信息"""
    lines = []
    lines.append("  【生辰八字】")
    lines.append(f"    八字: {bazi['bazi_str']}")
    lines.append(f"    五行: {bazi['wuxing']}")
    lines.append(f"    日主: {bazi['rizhu']} ({bazi['siji']})")
    
    # 显示五行强度（带状态标记）
    if 'wuxing_strength' in bazi:
        strength = bazi['wuxing_strength']
        total = sum(strength.values())
        strength_parts = []
        for wx in ['木', '火', '土', '金', '水']:
            s = strength.get(wx, 0)
            percent = (s / total * 100) if total > 0 else 0
            # 强度状态标记
            if s < 100:
                mark = '(!极弱)'
            elif s < 500:
                mark = '(-弱)'
            elif s >= 1500:
                mark = '(+旺)'
            else:
                mark = ''
            strength_parts.append(f"{wx}{s}{mark}")
        lines.append(f"    强度: {' '.join(strength_parts)}")
    
    # 显示同类异类（更紧凑）
    if 'tongyi' in bazi and 'yilei' in bazi:
        tongyi = bazi['tongyi']
        yilei = bazi['yilei']
        tongyi_elem = ''.join(tongyi['elements'])
        yilei_elem = ''.join(yilei['elements'])
        
        lines.append(f"    同类({tongyi_elem}): {tongyi['strength']} ({tongyi['percent']:.1f}%)")
        lines.append(f"    异类({yilei_elem}): {yilei['strength']} ({yilei['percent']:.1f}%)")
    
    # 使用格式化的喜用神描述（如果有）
    if bazi.get('xiyong_desc'):
        lines.append(f"    {bazi['xiyong_desc']}")
    else:
        # 降级到简单格式
        if 'tongyi' in bazi and 'yilei' in bazi:
            tongyi = bazi['tongyi']
            # 判断身强身弱
            if tongyi['percent'] > 55:
                status = "身强，喜克泄耗"
            elif tongyi['percent'] < 45:
                status = "身弱，喜生扶"
            else:
                status = "中和"
            lines.append(f"    判断: {status}")
        
        # 喜用神和忌神
        xiyong_str = ', '.join(bazi['xiyong_shen'])
        ji_str = ', '.join(bazi['ji_shen']) if bazi.get('ji_shen') else '无'
        lines.append(f"    喜用神: {xiyong_str} | 忌神: {ji_str}")
    
    lines.append(f"    幸运色: {bazi['color']}")
    
    # 显示四季用神参考
    if bazi.get('siji'):
        siji = bazi['siji']
        # 如果是详细格式（较长），单独一行显示
        if len(siji) > 30:
            lines.append(f"    四季用神: {siji}")
        else:
            # 简短格式，放在季节信息后
            pass  # 已经在日主行显示了
    
    lines.append(f"    纳音: {bazi['nayin']}")
    lines.append(f"    农历: {bazi['lunar_date']}")
    lines.append(f"    评分: {bazi['score']}分")
    return "\n".join(lines)


def format_shengxiao(shengxiao):
    """格式化生肖信息"""
    lines = []
    lines.append("  【生肖喜忌】")
    
    # 生肖基本信息（包含五行）
    sx = shengxiao['shengxiao']
    wx = shengxiao.get('wuxing', '未知')
    lines.append(f"    生肖: {sx}({wx}) | 评分: {shengxiao['score']}分")
    
    # 三合六合信息
    if shengxiao.get('sanhe'):
        sanhe_str = '、'.join(shengxiao['sanhe'])
        liuhe = shengxiao.get('liuhe', '')
        if liuhe:
            lines.append(f"    三合: {sanhe_str} | 六合: {liuhe}")
        else:
            lines.append(f"    三合: {sanhe_str}")
    
    # 显示详细的五行关系
    if shengxiao.get('wuxing_details'):
        lines.append(f"    五行关系:")
        for detail in shengxiao['wuxing_details']:
            char = detail['char']
            wx = detail['wuxing']
            desc = detail['description']
            score = detail['score_change']
            sign = '+' if score >= 0 else ''
            lines.append(f"      {char}({wx}): {desc} {sign}{score}分")
    
    # 显示计算过程（跳过基础分和最终得分）
    if shengxiao.get('calculation_steps'):
        calc_lines = []
        for step in shengxiao['calculation_steps']:
            step_name = step['step']
            if step_name not in ['基础分', '最终得分']:
                step_value = step['value']
                step_desc = step['description']
                if isinstance(step_value, (int, float)) and step_value != 0:
                    sign = '+' if step_value >= 0 else ''
                    
                    # 对于五行关系，已经在上面显示了详细信息，这里只显示总分
                    if step_name == '五行关系':
                        calc_lines.append(f"      {step_name}总计: {sign}{step_value}分")
                    else:
                        # 显示其他加减分项
                        details = step.get('details', [])
                        if details:
                            detail_str = '、'.join(details)
                            calc_lines.append(f"      {step_name}: {sign}{step_value}分 [{detail_str}]")
                        else:
                            calc_lines.append(f"      {step_name}: {sign}{step_value}分 - {step_desc}")
        
        if calc_lines:
            lines.append(f"    计算过程:")
            lines.extend(calc_lines)
    
    # 建议的喜忌五行和生肖
    if shengxiao.get('recommended_xi_wuxing') or shengxiao.get('recommended_ji_wuxing'):
        xi_wx = shengxiao.get('recommended_xi_wuxing', [])
        ji_wx = shengxiao.get('recommended_ji_wuxing', [])
        xi_str = '、'.join(xi_wx) if xi_wx else '无'
        ji_str = '、'.join(ji_wx) if ji_wx else '无'
        lines.append(f"    建议五行: 喜{xi_str} | 忌{ji_str}")
    
    if shengxiao.get('recommended_xi_shengxiao') or shengxiao.get('recommended_ji_shengxiao'):
        xi_sx = shengxiao.get('recommended_xi_shengxiao', [])
        ji_sx = shengxiao.get('recommended_ji_shengxiao', [])
        xi_str = '、'.join(xi_sx) if xi_sx else '无'
        ji_str = '、'.join(ji_sx) if ji_sx else '无'
        lines.append(f"    建议生肖: 喜{xi_str} | 忌{ji_str}")
    
    # 传统的喜忌字根（折叠显示）
    lines.append(f"    喜字根: {', '.join(shengxiao['xi_zigen'][:10])}{'...' if len(shengxiao['xi_zigen']) > 10 else ''}")
    lines.append(f"    忌字根: {', '.join(shengxiao['ji_zigen'][:10])}{'...' if len(shengxiao['ji_zigen']) > 10 else ''}")
    
    # 生肖特性说明
    if shengxiao.get('comment'):
        lines.append(f"    特性: {shengxiao['comment']}")
    
    return "\n".join(lines)


def format_chenggu(chenggu):
    """格式化称骨信息"""
    lines = []
    lines.append("  【称骨算命】")
    lines.append(f"    骨重: {chenggu['weight']}两 ({chenggu['comment']})")
    lines.append(f"    命理: {chenggu['fortune_text']}")
    return "\n".join(lines)


def view_result(result_file):
    """查看批量处理结果"""
    if not Path(result_file).exists():
        print(f"错误: 文件不存在 - {result_file}")
        return
    
    with open(result_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 80)
    print(f"批量处理结果查看".center(76))
    print("=" * 80)
    print(f"输入文件: {data['input_file']}")
    print(f"处理时间: {data['process_time']}")
    print(f"总计: {data['total']} 条 | 成功: {data['success']} 条 | 失败: {data['failed']} 条")
    print("=" * 80)
    
    for idx, result in enumerate(data['results'], 1):
        print(f"\n【{idx}/{data['total']}】{result['name']}")
        print("-" * 80)
        
        if not result['success']:
            print(f"  [失败] {result['error']}")
            continue
        
        # 基本信息
        info = result['basic_info']
        print(f"  姓名: {info['surname']}{info['given_name']} | 性别: {info['gender']} | 出生: {info['birth_time']}")
        
        # 康熙字典信息
        if 'kangxi_info' in result and result['kangxi_info']:
            for kx in result['kangxi_info']:
                parts = [f"笔画={kx['strokes']}", f"部首={kx['radical']}"]
                if kx.get('wuxing') and kx['wuxing'] != '未知':
                    parts.append(f"五行={kx['wuxing']}")
                if kx.get('luck') and kx['luck'] != '未知':
                    parts.append(f"吉凶={kx['luck']}")
                print(f"    {kx.get('traditional', kx['character'])}: {', '.join(parts)}")
        
        if info.get('longitude') and info.get('latitude'):
            print(f"  地点: 东经 {info['longitude']}° 北纬 {info['latitude']}°")
        
        # 综合评分
        score = result['comprehensive_score']
        if score >= 90:
            level = "优秀"
        elif score >= 80:
            level = "良好"
        elif score >= 70:
            level = "中等"
        elif score >= 60:
            level = "及格"
        else:
            level = "较差"
        print(f"  综合评分: {score}分 ({level})\n")
        
        # 详细分析
        print(f"{format_wuge(result['wuge'])}\n")
        print(f"{format_bazi(result['bazi'])}\n")
        
        if 'ziyi' in result and result['ziyi'] and result['ziyi'].get('analysis'):
            print(f"  【字义音形】")
            print(f"    {result['ziyi']['analysis']}")
            print(f"    评分: {result['ziyi'].get('score', 0)}分\n")
        
        print(f"{format_shengxiao(result['shengxiao'])}\n")
        print(f"{format_chenggu(result['chenggu'])}")
        
        print("\n" + "=" * 80)


def main():
    if len(sys.argv) < 2:
        print("用法: python view_batch_result.py <结果文件路径>")
        print("示例: python tests/view_batch_result.py tests/example_input_result_20251206_213416.json")
        return
    
    result_file = sys.argv[1]
    view_result(result_file)


if __name__ == '__main__':
    main()
