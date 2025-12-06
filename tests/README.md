# 测试和示例文件目录

本目录包含所有测试脚本、验证工具和示例文件。

## 目录结构

### 测试脚本 (test_*.py)
- `test_bazi_jieqi.py` - 八字节气测试
- `test_display.py` - 显示功能测试
- `test_early_dates.py` - 早期日期测试（1900-1969）
- `test_lunar_display.py` - 农历显示测试
- `test_name_analysis.py` - 姓名分析测试
- `test_query.py` - 查询功能测试
- `test_separated_name.py` - 分离姓名测试
- `test_special_dates.py` - 特殊日期格式测试
- `test_txt_parse.py` - TXT文件解析测试
- `test_ui_clear.py` - UI清理测试
- `test_waige_compare.py` - 外格比较测试
- `test_waige_fix.py` - 外格修复测试
- `test_wannianli.py` - 万年历测试
- `test_wannianli_bazi.py` - 万年历八字测试
- `test_wannianli_db.py` - 万年历数据库测试

### 验证脚本 (verify_*.py)
- `verify_bazi_source.py` - 八字数据源验证
- `verify_merged_data.py` - 合并数据验证
- `verify_wannianli.py` - 万年历数据验证

### 检查脚本 (check_*.py)
- `check_calendar.py` - 日历数据检查
- `check_lunar_date.py` - 农历日期检查
- `check_validation.py` - 数据验证检查

### 演示脚本 (demo_*.py)
- `demo_clear_history.py` - 清空历史记录演示

### 快速测试脚本 (quick_*.py)
- `quick_test_lunar.py` - 农历快速测试

### 批量处理示例文件
- `example_input.txt` - TXT格式批量输入示例
- `example_input.csv` - CSV格式批量输入示例
- `example_input.json` - JSON格式批量输入示例
- `example_input_result_*.json` - 批量处理结果示例

### 结果查看工具
- `view_batch_result.py` - 批量处理结果美化查看工具

### 文档
- `万年历集成测试报告.md` - 万年历功能集成测试报告

## 使用说明

### 运行单个测试
```bash
python tests/test_wannianli.py
```

### 批量处理示例
```bash
# 使用 TXT 格式
python bazi.py -b tests/example_input.txt

# 使用 CSV 格式
python bazi.py -b tests/example_input.csv

# 使用 JSON 格式
python bazi.py -b tests/example_input.json
```

### 数据验证
```bash
# 验证万年历数据
python tests/verify_wannianli.py

# 检查农历日期
python tests/check_lunar_date.py

# 验证合并数据
python tests/verify_merged_data.py
```

### 查看批量处理结果
```bash
# 美化显示批量处理结果
python tests/view_batch_result.py tests/example_input_result_20251206_213416.json
```

## 注意事项

- 测试脚本需要在项目根目录运行
- 部分测试需要先加载数据：`python bazi.py --reload-data`
- 批量处理结果会保存在 tests 目录下
