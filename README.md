# 姓名测试软件

基于传统命理学的姓名分析系统

## 功能特点

- 三才五格分析
- 生辰八字计算（支持1900-2099年）
- 字义音形分析
- 生肖喜忌分析
- 称骨算命
- 综合评分
- 批量处理（支持TXT/CSV/JSON格式）
- 历史记录管理

## 公司测名（SRD-公司版本）

在个人版基础上扩展公司名称测试：

- 公司名结构解析：[行政区划] + [字号/主名] + [行业/经营特点] + [组织形式]
- 两套五格计算：主名与全称（总格>81按行业惯例减81）
- 行业特性分析：五行匹配 + 行业吉祥字库；包含“喜用神匹配度”
- 综合评分：五格15% + 行业20% + 八字35% + 喜用20% + 生肖5% + 字义5%
- 负责人信息：性别必填、出生时间与经纬度必填（万年历优先）

### 快速开始

```powershell
# 交互式公司测名（含逐字清单展示）
python company_ceshi.py -c

# 批量公司测名（限制最多处理5条）
python company_ceshi.py -bc tests\company_batch.csv --export-company tests\out_company_batch.json

# 查看公司版批量结果（数组JSON）
python tests\view_company_batch_result.py tests\out_company_batch.json

# 行业五行对照表
python company_ceshi.py --industry-help

# 历史管理
python company_ceshi.py --company-history
python company_ceshi.py --clear-history
```

### 输出说明

- 交互模式会打印：名称结构、逐字清单（繁体/拼音/笔画/五行/凶吉）、主名/全称两套五格、分项评分与综合评分。
- 批量导出（JSON数组）包含：解析结构、行业分析细节、两套五格、生肖与字义分析、分项与综合评分，方便审计与复现。

## 📚 文档

详细文档请查看 [docs/](docs/) 目录：

- **[项目技术总览](docs/TECHNICAL_OVERVIEW.md)** - 项目结构、架构与数据流、运行与输出
- **[五行原则完整说明](docs/WUXING_PRINCIPLES_DOC.md)** - 关键/相对原则的实现与示例
- **[五行原则速查卡](docs/WUXING_QUICK_REFERENCE.md)** - 生克关系、行业/生肖五行速查
- **[实现总结](docs/IMPLEMENTATION_SUMMARY.md)** - 本次功能实现的概述与验证
- **[批量处理说明](docs/batch_input_format.md)** - 批量处理文件格式和使用方法
- **[数据管理指南](docs/DATA_MANAGEMENT_GUIDE.md)** - 数据表统计、清空和恢复操作
- **[历史记录管理](docs/CLEAR_HISTORY_GUIDE.md)** - 清空历史记录操作指南
- **[农历显示功能](docs/LUNAR_DISPLAY_FEATURE.md)** - 农历日期显示说明
- **[更多文档...](docs/README.md)** - 完整文档索引

## 安装使用

### 环境要求

- Python 3.8+
- SQLite 3

### 运行方式

```bash
# 启动交互界面
python bazi.py

# 开始姓名测试
python bazi.py -t

# 批量处理
python bazi.py -b tests/example_input.json
python tests/view_batch_result.py tests/example_input_result.json

# 公司版批量与查看（推荐放在 tests/ 路径）
python company_ceshi.py -bc tests/company_batch.csv --export-company tests/out_company_batch.json
python tests/view_company_batch_result.py tests/out_company_batch.json

# 查看帮助
python bazi.py -h

# 数据管理
python bazi.py --show-tables      # 显示数据表统计
python bazi.py --reload-data      # 重新加载资源数据
python bazi.py --clear-history    # 清空历史记录
python bazi.py --clear-all-data   # 清空所有数据表（需要重新加载资源）

# 显示经纬度查询帮助
python bazi.py --geo-help
```

### 技术文档入口（推荐）

如需了解程序结构与输出格式，请先阅读：

- 项目技术总览：见 [docs/TECHNICAL_OVERVIEW.md](docs/TECHNICAL_OVERVIEW.md)
- 输出JSON结构：见 [docs/OUTPUT_SCHEMA.md](docs/OUTPUT_SCHEMA.md)
- 五行原则详解与速查：见 [docs/WUXING_PRINCIPLES_DOC.md](docs/WUXING_PRINCIPLES_DOC.md) 与 [docs/WUXING_QUICK_REFERENCE.md](docs/WUXING_QUICK_REFERENCE.md)

## 数据文件格式

所有数据文件存放在 `data/` 目录下，使用 JSON 格式：

### kangxi.json - 康熙字典笔画
```json
{
  "version": "1.0",
  "data": [
    {"character": "张", "strokes": 11}
  ]
}
```

### ziyi.json - 字义音形
```json
{
  "version": "1.0",
  "data": [
    {
      "character": "伟",
      "pinyin": "wei",
      "tones": [3],
      "bushou": "亻",
      "bihua": 11,
      "wuxing": "土",
      "meaning": "伟大、高大、杰出",
      "jixiong": "吉"
    }
  ]
}
```

## 查询经纬度坐标

1. 天地图：https://map.tianditu.gov.cn/
2. 高德地图：https://lbs.amap.com/demo/javascript-api/example/map/click-to-get-lnglat
3. 百度地图：https://api.map.baidu.com/lbsapi/getpoint/index.html

## 数据库说明

程序使用 SQLite 数据库 `local.db` 存储：

- 资源数据表（8个）：康熙笔画、字义音形、纳音五行、数理五行、三才配置、生肖喜忌、称骨命理、骨重表
- 结果数据表（公司/个人）：测试记录、五格结果、行业分析、生肖分析、字义分析、综合评分等（公司版新增 company_* 表）

## 日志文件

运行日志保存在 `logs/app.log`

## 开发规范

- 遵循 PEP 8 代码规范
- 使用 UTF-8 编码
- 函数添加类型注解
- 模块添加 docstring

## 版本信息

当前版本：v1.1

公司版当前版本：0.3.0-company

## 作者

HunterLau@HongKong

## 许可证

BSD License
