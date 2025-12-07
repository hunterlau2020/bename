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

## 📚 文档

详细文档请查看 [docs/](docs/) 目录：

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
- 结果数据表（6个）：测试记录、五格结果、八字结果、字义结果、生肖结果、称骨结果

## 日志文件

运行日志保存在 `logs/app.log`

## 开发规范

- 遵循 PEP 8 代码规范
- 使用 UTF-8 编码
- 函数添加类型注解
- 模块添加 docstring

## 版本信息

当前版本：v1.0

## 作者

HunterLau@HongKong

## 许可证

MIT License
