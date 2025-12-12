from typing import Dict

# 行业后缀到行业代码的简易映射
_INDUSTRY_SUFFIX_TO_CODE = {
    '科技': 'tech',
    '网络': 'tech',
    '资本管理': 'finance',
    '国际': 'trade',
    '贸易': 'trade',
    '制造': 'manufacture',
    '餐饮': 'catering',
    '教育': 'education',
    '文化': 'culture',
    '医疗': 'medical'
}

class CompanyParser:
    """解析公司名称结构：[行政区划] + [主名/字号] + [行业/后缀] + [组织形式]"""

    def parse(self, full_name: str) -> Dict:
        org_forms = ['有限公司', '股份有限公司', '有限合伙', '集团', '中心']
        industry_suffixes = list(_INDUSTRY_SUFFIX_TO_CODE.keys())
        prefix_candidates = ['北京', '上海', '深圳', '广州', '杭州', '南京', '天津', '重庆', '武汉', '成都', '香港', '澳门']

        name = full_name.strip()
        org_form = ''
        for of in org_forms:
            if name.endswith(of):
                org_form = of
                name = name[:-len(of)]
                break

        industry_suffix = ''
        for suf in industry_suffixes:
            if name.endswith(suf):
                industry_suffix = suf
                name = name[:-len(suf)]
                break

        prefix = ''
        for pre in prefix_candidates:
            if name.startswith(pre):
                prefix = pre
                name = name[len(pre):]
                break

        main = name
        industry_code = _INDUSTRY_SUFFIX_TO_CODE.get(industry_suffix, '')
        return {
            'full_name': full_name,
            'prefix': prefix,
            'main_name': main,
            'industry_suffix': industry_suffix,
            'industry_code': industry_code,
            'org_form': org_form,
        }


def parse_company_name(full_name: str) -> Dict:
    """提供函数接口以便 CompanyCalculator 调用"""
    return CompanyParser().parse(full_name)
