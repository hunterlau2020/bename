# 批量处理输入文件示例

## 格式说明

支持三种文件格式：TXT、CSV、JSON

### 必填字段
- name: 姓名
- gender: 性别（男/女）
- birth_date: 出生日期（格式：YYYY-MM-DD）

### 可选字段
- birth_time: 出生时间（格式：HH:MM，默认 12:00）
- longitude: 出生地经度（东经为正，西经为负）
- latitude: 出生地纬度（北纬为正，南纬为负）

---

## 格式 1: TXT 表格格式（空格或制表符分隔）

```txt
# 姓名 性别 出生日期 出生时间 经度 纬度
张三 男 1990-01-01 10:30 116.4074 39.9042
李四 女 1992-05-20 14:00 121.4737 31.2304
王五 男 1985-03-15 08:00
赵六 女 1988-11-30
```

保存为 `names.txt`，使用：
```bash
python bazi.py -b names.txt
# 或使用 tests 目录下的示例
python bazi.py -b tests/example_input.txt
```

---

## 格式 2: TXT 键值对格式（每条记录用空行分隔）

```txt
name: 张三
gender: 男
birth_date: 1990-01-01
birth_time: 10:30
longitude: 116.4074
latitude: 39.9042

name: 李四
gender: 女
birth_date: 1992-05-20
birth_time: 14:00
longitude: 121.4737
latitude: 31.2304

name: 王五
gender: 男
birth_date: 1985-03-15
birth_time: 08:00
```

保存为 `names_kv.txt`，使用：
```bash
python bazi.py -b names_kv.txt
```

---

## 格式 3: CSV 格式

```csv
name,gender,birth_date,birth_time,longitude,latitude
张三,男,1990-01-01,10:30,116.4074,39.9042
李四,女,1992-05-20,14:00,121.4737,31.2304
王五,男,1985-03-15,08:00,,
赵六,女,1988-11-30,,,
```

保存为 `names.csv`，使用：
```bash
python bazi.py -b names.csv
# 或使用 tests 目录下的示例
python bazi.py -b tests/example_input.csv
```

---

## 格式 4: JSON 格式

```json
[
  {
    "name": "张三",
    "gender": "男",
    "birth_date": "1990-01-01",
    "birth_time": "10:30",
    "longitude": 116.4074,
    "latitude": 39.9042
  },
  {
    "name": "李四",
    "gender": "女",
    "birth_date": "1992-05-20",
    "birth_time": "14:00",
    "longitude": 121.4737,
    "latitude": 31.2304
  },
  {
    "name": "王五",
    "gender": "男",
    "birth_date": "1985-03-15",
    "birth_time": "08:00"
  },
  {
    "name": "赵六",
    "gender": "女",
    "birth_date": "1988-11-30"
  }
]
```

保存为 `names.json`，使用：
```bash
python bazi.py -b names.json
# 或使用 tests 目录下的示例
python bazi.py -b tests/example_input.json
```

---

## 输出文件

处理完成后，会在输入文件同目录下生成结果文件：

```
names_result_20251206_143020.json
```

### 输出文件结构

```json
{
  "input_file": "tests/example_input.json",
  "process_time": "20251206_143020",
  "total": 5,
  "success": 5,
  "failed": 0,
  "results": [
    {
      "name": "张伟",
      "success": true,
      "basic_info": {
        "surname": "张",
        "given_name": "伟",
        "gender": "男",
        "birth_time": "1990-01-15 10:30",
        "longitude": 116.4074,
        "latitude": 39.9042
      },
      "comprehensive_score": 70,
      "wuge": {
        "tiange": {"num": 12, "element": "木", "fortune": "凶"},
        "renge": {"num": 22, "element": "木", "fortune": "凶"},
        "dige": {"num": 12, "element": "木", "fortune": "凶"},
        "waige": {"num": 2, "element": "木", "fortune": "凶"},
        "zongge": {"num": 22, "element": "木", "fortune": "凶"},
        "sancai": "木木木 - 大吉",
        "score": 50
      },
      "bazi": {
        "bazi_str": "己巳 丁丑 庚辰 辛巳",
        "wuxing": "土火 火土 金土 金火",
        "nayin": "城墙土 涧下水 城墙土 沙中土",
        "geshu": {"金": 2, "木": 0, "水": 0, "火": 3, "土": 3},
        "rizhu": "庚",
        "siji": "日主天干金生于冬季",
        "xiyong_shen": ["木", "水"],
        "ji_shen": ["火", "土"],
        "color": "绿色、青色、翠色、黑色、蓝色、灰色",
        "score": 80,
        "lunar_date": "1989年12月19日巳时"
      },
      "ziyi": {
        "analysis": "姓名'张伟'字义音形分析结果",
        "score": 75
      },
      "shengxiao": {
        "shengxiao": "马",
        "xi_zigen": ["艹", "木", "禾"],
        "ji_zigen": ["火", "日"],
        "score": 80
      },
      "chenggu": {
        "weight": 3.9,
        "fortune_text": "为利为名终日劳...",
        "comment": "命运中等偏上"
      }
    }
  ]
}
```

### 输出字段说明

**顶层字段：**
- `input_file` - 输入文件路径
- `process_time` - 处理时间戳
- `total` - 总记录数
- `success` - 成功处理数量
- `failed` - 失败处理数量
- `results` - 详细结果数组

**每条记录包含：**
- `basic_info` - 基本信息（姓名、性别、出生时间、经纬度）
- `comprehensive_score` - 综合评分（0-100）
- `wuge` - 三才五格分析（天格、人格、地格、外格、总格、三才配置）
- `bazi` - 生辰八字（八字、五行、纳音、喜用神、忌神、幸运颜色、农历日期）
- `ziyi` - 字义音形分析
- `shengxiao` - 生肖喜忌分析
- `chenggu` - 称骨算命结果

---

## 常见城市经纬度参考

| 城市 | 经度 | 纬度 |
|------|------|------|
| 北京 | 116.4074 | 39.9042 |
| 上海 | 121.4737 | 31.2304 |
| 广州 | 113.2644 | 23.1291 |
| 深圳 | 114.0579 | 22.5431 |
| 成都 | 104.0668 | 30.5728 |
| 杭州 | 120.1551 | 30.2741 |
| 西安 | 108.9398 | 34.3416 |
| 武汉 | 114.3055 | 30.5931 |
| 南京 | 118.7969 | 32.0603 |
| 重庆 | 106.5516 | 29.5630 |

更多城市经纬度可使用：
```bash
python bazi.py --geo-help
```
