# 数据管理指南

## 概述

本工具提供了多种数据管理功能，帮助用户维护和管理数据库中的数据。

## 数据表分类

### 资源数据表
包含程序运行所需的基础数据：

| 表名 | 说明 | 数据来源 |
|------|------|----------|
| wannianli | 万年历数据 (1900-2099) | ch_calendar.xls + wannianli.json |
| kangxi_strokes | 康熙字典笔画 | kangxi-strokes.json |
| wuxing_nayin | 五行纳音 | wuxing-nayin.json |
| shuli_wuxing | 数理五行 | shuli-wuxing.json |
| sancai_jixiong | 三才吉凶 | sancai-jixiong.json |
| shengxiao_xiji | 生肖喜忌 | shengxiao-xiji.json |
| chenggu_weights | 称骨重量表 | chenggu-weights.json |
| chenggu_fortune | 称骨命理 | chenggu-fortune.json |

### 历史记录表
存储用户的测算历史和结果：

| 表名 | 说明 |
|------|------|
| test_records | 测算请求记录 |
| wuge_results | 五格测算结果 |
| bazi_results | 八字测算结果 |
| ziyi_results | 字义分析结果 |
| shengxiao_results | 生肖分析结果 |
| chenggu_results | 称骨算命结果 |

## 功能对比

### 1. 查看数据表统计 (--show-tables)

**用途**: 查看所有数据表的记录数统计

**使用方法**:
```bash
python bazi.py --show-tables
```

**输出示例**:
```
数据表统计信息:
============================================================

资源数据表:
  wannianli           :   73,049 条
  kangxi_strokes      :   34,683 条
  wuxing_nayin        :       64 条
  shuli_wuxing        :       81 条
  sancai_jixiong      :       90 条
  shengxiao_xiji      :       96 条

历史记录表:
  test_records        :        7 条
  wuge_results        :       11 条
  bazi_results        :       11 条
  ziyi_results        :       11 条
  shengxiao_results   :       11 条
  chenggu_results     :       11 条

============================================================
资源数据总计:  108,063 条
历史记录总计:       62 条
```

**适用场景**:
- 检查数据加载状态
- 清空数据前确认影响范围
- 了解数据库整体状况

### 2. 清空历史记录 (--clear-history)

**用途**: 清空测算历史记录，保留资源数据

**使用方法**:
```bash
python bazi.py --clear-history
```

**影响范围**:
- ✗ 删除所有历史记录表数据
- ✓ 保留所有资源数据表
- ✓ 程序可以继续正常使用

**确认方式**: 简单确认 (yes/no)

**适用场景**:
- 定期清理测算历史
- 释放数据库空间
- 重新开始测算记录
- 导出历史数据后清理

**注意事项**:
- 不影响程序功能
- 无需重新加载资源数据
- 操作相对安全

### 3. 清空所有数据表 (--clear-all-data)

**用途**: 清空所有数据表，包括资源数据和历史记录

**使用方法**:
```bash
python bazi.py --clear-all-data
```

**影响范围**:
- ✗ 删除所有历史记录表数据
- ✗ 删除所有资源数据表数据
- ✗ 程序无法正常使用（需重新加载资源）

**确认方式**: 严格确认 (输入 'DELETE ALL')

**适用场景**:
- 完全重置数据库
- 更新资源数据文件后重新加载
- 清理损坏的数据
- 数据库迁移前清空

**注意事项**:
- ⚠️ 高危操作，不可恢复
- ⚠️ 需要手动输入 'DELETE ALL' 确认
- ⚠️ 清空后必须使用 --reload-data 重新加载资源
- ⚠️ 建议在清空前先使用 --show-tables 查看数据

## 数据恢复

### 重新加载资源数据

使用 `--reload-data` 参数重新加载所有资源数据：

```bash
python bazi.py --reload-data
```

**加载内容**:
- 万年历数据 (ch_calendar.xls → wannianli)
- 康熙字典笔画 (kangxi-strokes.json)
- 五行纳音 (wuxing-nayin.json)
- 数理五行 (shuli-wuxing.json)
- 三才吉凶 (sancai-jixiong.json)
- 生肖喜忌 (shengxiao-xiji.json)
- 称骨数据 (chenggu-weights.json + chenggu-fortune.json)

**加载时间**: 约 10-30 秒（取决于数据量）

## 操作流程示例

### 场景1: 定期清理历史记录

```bash
# 1. 查看当前数据量
python bazi.py --show-tables

# 2. 清空历史记录
python bazi.py --clear-history
# 输入: yes

# 3. 确认清理结果
python bazi.py --show-tables
```

### 场景2: 完全重置数据库

```bash
# 1. 查看当前数据量
python bazi.py --show-tables

# 2. 清空所有数据
python bazi.py --clear-all-data
# 输入: DELETE ALL

# 3. 重新加载资源数据
python bazi.py --reload-data

# 4. 确认加载结果
python bazi.py --show-tables
```

### 场景3: 更新资源数据文件

```bash
# 1. 备份旧数据（可选）
cp local.db local.db.backup

# 2. 清空所有数据
python bazi.py --clear-all-data
# 输入: DELETE ALL

# 3. 替换资源数据文件
cp new-kangxi-strokes.json kangxi-strokes.json

# 4. 重新加载资源数据
python bazi.py --reload-data

# 5. 验证加载结果
python bazi.py --show-tables
```

## 安全建议

1. **定期备份**: 在执行清空操作前，建议先备份 `local.db` 文件
2. **先查看后操作**: 使用 `--show-tables` 查看数据后再决定是否清空
3. **谨慎使用 --clear-all-data**: 此操作会删除所有资源数据，需要重新加载
4. **测试环境先试**: 在生产环境使用前，先在测试环境验证操作流程

## 常见问题

### Q1: --clear-history 和 --clear-all-data 有什么区别？

**A**: 
- `--clear-history`: 只清空历史记录，保留资源数据，程序可继续使用
- `--clear-all-data`: 清空所有数据（包括资源），需要重新加载资源才能使用

### Q2: 清空数据后如何恢复？

**A**: 
- 历史记录无法恢复（建议清空前导出）
- 资源数据使用 `--reload-data` 重新加载

### Q3: --reload-data 会删除现有数据吗？

**A**: 不会。`--reload-data` 只会添加缺失的资源数据，不会删除现有数据。

### Q4: 如何只清空某一类数据？

**A**: 目前只支持：
- 清空历史记录: `--clear-history`
- 清空所有数据: `--clear-all-data`

如需更精细的控制，请直接操作 SQLite 数据库。

### Q5: 清空数据会影响正在运行的程序吗？

**A**: 不会。每次调用都是独立的数据库连接。但不建议在批量处理时清空数据。

## 相关文档

- [批量处理格式说明](batch_input_format.md)
- [命令行参数说明](../README.md#命令行参数)
- [数据加载说明](DATA_LOADING.md)
