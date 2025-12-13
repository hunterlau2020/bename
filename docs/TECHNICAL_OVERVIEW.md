# 项目技术总览

## 项目概览
- 目标：基于五行、八字、生肖、字义、五格，对公司名称进行综合评分与分析，并提供行业与字的建议。
- 主要特性：
  - 五行原则（关键+相对）完整评估
  - 行业主五行与吉祥字分析
  - 八字喜用/忌神与季节用神说明
  - 生肖喜忌字根与三合/六合关系
  - 字义音形与三才五格评分
  - 批量分析与结果查看脚本

## 目录结构
```
bename/
├─ modules/                # 核心模块
│  ├─ company_calculator.py      # 总调度：整合各分析模块并产出结果JSON
│  ├─ industry_analyzer.py       # 行业五行与吉祥字分析（含关键/相对原则）
│  ├─ shengxiao_analyzer.py      # 生肖喜忌、三合六合、五行协调分析
│  ├─ ziyi_analyzer.py           # 字义音形分析与评分
│  ├─ wuge_calculator.py         # 三才五格计算与评分
│  ├─ bazi_calculator.py         # 八字与喜用神、季节用神（集成）
│  ├─ company_parser.py          # 公司名解析（区划/字号/行业/组织）
│  ├─ storage.py                 # 数据存取与初始化（SQLite）
│  └─ ...
├─ data/                   # 配置/字典数据（JSON）
│  ├─ industry_wuxing.json       # 行业主/次五行表
│  ├─ industry_lucky_chars.json  # 行业高频吉祥字+示例
│  ├─ kangxi.json                # 康熙字典（繁体/笔画/五行）
│  ├─ wannianli.json             # 万年历基础数据
│  ├─ shengxiao.json             # 生肖辅助数据
│  └─ ...
├─ local.db               # SQLite数据库（kangxi_strokes、wannianli、shengxiao_xiji等）
├─ tests/                 # 测试与查看工具
│  ├─ view_company_batch_result.py   # 批量结果查看器（详尽展示）
│  ├─ out_company_batch_4.json       # 批量结果示例
│  ├─ test_*                         # 单/集成测试脚本
│  └─ ...
├─ company_ceshi.py       # 交互/批量分析入口（CLI）
├─ docs/WUXING_PRINCIPLES_DOC.md       # 五行原则完整说明
├─ docs/WUXING_QUICK_REFERENCE.md      # 五行原则速查
├─ docs/IMPLEMENTATION_SUMMARY.md      # 本次实现总结
└─ README.md             # 项目首页
```

## 核心架构与数据流
- `CompanyCalculator.analyze_single(prefix, main_name, suffix, form_org, full_name, bazi_info)`
  - 解析输入 → 执行生肖分析（获取生肖与五行）→ 执行行业五行分析（含关键/相对原则）→ 吉祥字分析 → 五格计算 → 八字/字义 → 汇总分项与总分 → 输出结构化JSON
- 模块职责：
  - `IndustryAnalyzer`：
    - `calculate_wuxing_match_score(...)`：名称五行分布、喜用匹配、行业补益、克制禁忌、相对原则（行业生名称、名称与生肖协调）；产出 `critical_principles` 与 `relative_principles`。
    - `calculate_lucky_char_score(...)`：行业高频字加分与Top5推荐。
  - `ShengxiaoAnalyzer`：生肖、五行、三合/六合、喜忌字根与与名称的五行关系评分。
  - `ZiyiAnalyzer`：字义音形分析、音韵评分、吉凶细节与综合评价。
  - `WugeCalculator`：主名/全称两套五格评分与三才含义。
  - `BaziCalculator`：喜用神、忌神、季节用神说明（集成到 `bazi_detail`）。

## 关键技术点
- 五行原则实现：
  - 关键原则：行业补益喜用（=或相生）、名称支持喜用（支持率计算）、克制禁忌（逐字克制检测）。
  - 相对原则：行业生名称、名称与生肖协调（相同+相生加分）。
- 数据查询：
  - 康熙字五行取自 SQLite `kangxi_strokes` 表（带缓存）。
  - 生肖数据取自 `shengxiao_xiji` 与万年历表。
- 输出结构：分层JSON，便于 viewer 脚本全面显示。

## 运行与使用
- 交互模式（公司版）：
```powershell
python company_ceshi.py -c
```
- 批量模式（从CSV）：
```powershell
python company_ceshi.py -b tests\company_batch.csv
# 输出：tests\out_company_batch_N.json（自动编号）
```
- 查看批量结果（完整展示）：
```powershell
python tests\view_company_batch_result.py tests\out_company_batch_4.json
```
- 快速验证五行原则（直接模块）：
```powershell
python test_wuxing_direct.py
Get-Content test_wuxing_direct_result.json | Select-Object -First 60
```

## 输出JSON结构（简表）
- `parsed`：输入解析（full_name、main_name、industry_code 等）
- `scores`：各分项与总分（五格/行业/八字/喜用/生肖/字义）
- `wuxing_analysis`：
  - `wuxing_dist`、`match_score`、`xiyong_match_score`、`match_detail`
  - `critical_principles`（行业补益、名称支持、克制禁忌）
  - `relative_principles`（行业生名称、名称与生肖协调）
- `industry_detail`：行业主五行、吉祥字、Top5推荐、计算步骤/公式、评级
- `wuge_full`/`wuge_main`：五格评分与三才含义
- `shengxiao_detail`：生肖、五行、三合/六合、喜忌字根、匹配明细、评价
- `ziyi_detail`：字义音形分析、音韵评分、吉义
- `char_details`：逐字清单（繁体、拼音、笔画、五行、凶吉）

## 依赖与环境
- Python 3.10+（建议）
- 数据库：SQLite（`local.db`）
- 依赖：`lunarcalendar`（万年历辅助）
```powershell
pip install -r requirements.txt
```

## 日志与配置
- 日志：各模块使用 `logging` 输出 INFO/ERROR（tests 中有日志演示）。
- 配置：
  - 行业/吉祥字：`data/industry_*.json`
  - 康熙/万年历/生肖：`local.db` 与 `data/*.json`

## 开发与测试
- 语法检查：
```powershell
python -m py_compile modules\industry_analyzer.py modules\company_calculator.py tests\view_company_batch_result.py
```
- 常用测试：
```powershell
python tests\test_wuxing_calculation.py
python tests\test_shengxiao_analysis.py
python tests\view_company_batch_result.py tests\out_company_batch_4.json | Select-Object -First 120
```

## 进一步工作
- 权重可配置化（五行与原则）
- 名称自动改良建议（替换字推荐）
- 结果导出 PDF/Word 报告
- 批量对比分析（改名前后差异）
