# 文档目录

本目录包含项目的所有技术文档、功能说明和使用指南。

## 📚 文档分类

### 用户指南

#### 批量处理
- **[batch_input_format.md](batch_input_format.md)** - 批量处理输入文件格式说明
  - 支持 TXT、CSV、JSON 三种格式
  - 包含示例文件和城市经纬度参考

#### 数据管理
- **[DATA_MANAGEMENT_GUIDE.md](DATA_MANAGEMENT_GUIDE.md)** - 数据管理完整指南
  - 数据表统计查看 (--show-tables)
  - 清空历史记录 (--clear-history)
  - 清空所有数据表 (--clear-all-data)
  - 数据恢复和安全建议

- **[CLEAR_HISTORY_GUIDE.md](CLEAR_HISTORY_GUIDE.md)** - 清空历史记录操作指南
  - 命令行清空方法
  - 交互界面清空方法
  - 注意事项和最佳实践

---

### 功能特性说明

#### 农历显示功能
- **[LUNAR_DISPLAY_FEATURE.md](LUNAR_DISPLAY_FEATURE.md)** - 农历日期显示功能
  - 农历日期显示格式
  - 数据来源和准确性
  - 使用示例

#### 分离姓名功能
- **[SEPARATED_NAME_FEATURE.md](SEPARATED_NAME_FEATURE.md)** - 姓名拆分显示功能
  - 姓氏和名字分离显示
  - 交互界面改进
  - 用户体验优化

---

### 技术文档

#### 八字计算
- **[STRENGTH_TABLE_FEATURE.md](STRENGTH_TABLE_FEATURE.md)** - 天干地支强度表功能
  - 五行强度精确计算
  - 同类异类分析
  - 喜用神科学判断
  - 月令旺衰理论应用

- **[BAZI_JIEQI_FIX.md](BAZI_JIEQI_FIX.md)** - 八字节气修复报告
  - 节气边界时辰处理
  - 月柱计算优化
  - 修复验证结果

#### 康熙字典
- **[KANGXI_CONVERT_HELP.md](KANGXI_CONVERT_HELP.md)** - 康熙字典数据转换帮助
  - Excel 数据导入流程
  - 字段映射说明
  - 常见问题解决

- **[KANGXI_FIX_REPORT.md](KANGXI_FIX_REPORT.md)** - 康熙字典数据修复报告
  - 数据清洗过程
  - 错误修复记录
  - 质量验证结果

#### 数据转换
- **[CONVERT_README.md](CONVERT_README.md)** - 数据转换工具说明
  - convert_tools.py 使用指南
  - 支持的数据格式
  - 转换流程说明

- **[万年历合并功能报告.md](万年历合并功能报告.md)** - 万年历数据合并报告
  - ch_calendar.xls 与 wannianli.json 合并
  - 数据范围扩展：1970-2099 → 1900-2099
  - 农历日期格式转换

#### 问题修复
- **[KEYERROR_FIX_REPORT.md](KEYERROR_FIX_REPORT.md)** - KeyError 错误修复报告
  - 问题诊断过程
  - 解决方案实施
  - 回归测试结果

---

## 📖 快速导航

### 按主题分类

**使用指南**
- 批量处理 → [batch_input_format.md](batch_input_format.md)
- 历史管理 → [CLEAR_HISTORY_GUIDE.md](CLEAR_HISTORY_GUIDE.md)

**功能特性**
- 农历显示 → [LUNAR_DISPLAY_FEATURE.md](LUNAR_DISPLAY_FEATURE.md)
- 姓名拆分 → [SEPARATED_NAME_FEATURE.md](SEPARATED_NAME_FEATURE.md)

**技术实现**
- 八字计算 → [BAZI_JIEQI_FIX.md](BAZI_JIEQI_FIX.md)
- 数据转换 → [CONVERT_README.md](CONVERT_README.md)
- 万年历合并 → [万年历合并功能报告.md](万年历合并功能报告.md)

**数据资源**
- 康熙字典 → [KANGXI_CONVERT_HELP.md](KANGXI_CONVERT_HELP.md), [KANGXI_FIX_REPORT.md](KANGXI_FIX_REPORT.md)

**问题修复**
- KeyError 修复 → [KEYERROR_FIX_REPORT.md](KEYERROR_FIX_REPORT.md)

---

## 🔍 文档更新记录

- **2025-12-06**: 创建文档目录索引
- **2025-12-06**: 整理并迁移所有技术文档到 docs 目录
- **2025-12-06**: 添加批量处理功能文档

---

## 📝 文档编写规范

1. **文件命名**: 使用英文，单词间用下划线或大写分隔
2. **格式**: 统一使用 Markdown 格式
3. **结构**: 包含标题、目录、正文、示例
4. **更新**: 重大更新需在文档开头注明日期和版本

---

## 💡 贡献指南

如需添加新文档或更新现有文档，请遵循以下步骤：

1. 确定文档类型（用户指南/功能说明/技术文档）
2. 使用清晰的标题和目录结构
3. 提供实际使用示例
4. 更新本 README 索引
