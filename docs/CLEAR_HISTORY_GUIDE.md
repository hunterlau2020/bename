# 清空历史记录功能使用说明

## 功能概述
新增了清空所有历史计算结果的功能,支持三种使用方式:命令行参数、交互界面命令、程序API调用。

## 使用方式

### 方式一: 命令行参数 (推荐)

最直接的方式,适合一次性清空操作。

```bash
# 清空所有历史记录
python bazi.py --clear-history
```

**执行流程:**
1. 显示当前历史记录数量
2. 要求用户确认 (输入 yes/y/是)
3. 清空所有记录并显示结果

**示例输出:**
```
当前共有 2 条历史记录
确认清空所有历史记录？(yes/no): yes
✓ 历史记录已清空
```

**注意事项:**
- 如果没有历史记录,直接提示 "当前没有历史记录"
- 必须输入 yes/y/是 才会执行清空,其他输入则取消操作
- 清空操作不可撤销,请谨慎使用

---

### 方式二: 交互界面命令

在程序运行过程中清空历史记录,无需退出重启。

```bash
# 启动交互界面
python bazi.py
```

**使用步骤:**
1. 在 "姓名:" 提示符下输入 `clear`
2. 确认清空操作
3. 继续使用程序或退出

**示例对话:**
```
============================================================
姓名测试软件 v1.0
基于传统命理学的姓名分析系统
============================================================

提示: 输入 'clear' 清空历史记录

请输入姓名（2-4个汉字，输入'quit'退出）：
姓名: clear

当前共有 5 条历史记录
确认清空所有历史记录？(yes/no): yes
✓ 历史记录已清空

请输入姓名（2-4个汉字，输入'quit'退出）：
姓名: 
```

**优点:**
- 无需退出程序
- 清空后可以继续使用
- 界面友好,操作直观

---

### 方式三: API 调用

在代码中清空历史记录,适合集成到其他程序。

```python
from modules.storage import Storage

# 创建 Storage 实例
storage = Storage()

# 查询记录数
count = storage.get_records_count()
print(f"当前有 {count} 条历史记录")

# 清空所有记录
if storage.clear_all_records():
    print("清空成功")
else:
    print("清空失败")

# 再次查询确认
count = storage.get_records_count()
print(f"清空后有 {count} 条历史记录")
```

**相关 API:**
- `storage.get_records_count()` - 获取历史记录总数
- `storage.clear_all_records()` - 清空所有历史记录
- `storage.query_history(limit=10)` - 查询最近的历史记录

---

## 技术实现

### 数据库操作
清空操作会删除以下所有表中的数据:

1. `test_records` - 主记录表
2. `wuge_results` - 五格分析结果
3. `bazi_results` - 八字分析结果
4. `ziyi_results` - 字义音形分析结果
5. `shengxiao_results` - 生肖喜忌分析结果
6. `chenggu_results` - 称骨算命结果

**删除顺序:**
按照外键依赖关系,先删除子表,最后删除主表,确保数据一致性。

### 安全机制
1. **二次确认**: 所有清空操作都需要用户明确确认
2. **日志记录**: 清空操作会记录到日志文件
3. **事务处理**: 使用数据库事务,失败时自动回滚
4. **错误处理**: 清空失败时返回 False 并记录错误日志

---

## 常见问题

### Q1: 清空后能恢复吗?
**A:** 不能。清空操作会永久删除所有历史记录,无法恢复。请在清空前确认是否需要备份。

### Q2: 清空会影响资源数据吗?
**A:** 不会。清空只删除用户的计算历史,不影响康熙字典、五格数理等基础资源数据。

### Q3: 清空失败怎么办?
**A:** 
1. 检查 `logs/app.log` 日志文件查看错误信息
2. 确认数据库文件 `local.db` 是否被其他程序占用
3. 检查文件权限是否正常

### Q4: 如何只删除部分记录?
**A:** 目前只支持全部清空。如需删除单条记录,可以使用:
```python
storage.delete_record(record_id)
```

### Q5: 清空会释放磁盘空间吗?
**A:** 会。SQLite 在删除数据后,可以通过 VACUUM 命令回收空间:
```python
import sqlite3
conn = sqlite3.connect('local.db')
conn.execute('VACUUM')
conn.close()
```

---

## 命令行帮助

查看所有命令行选项:
```bash
python bazi.py --help
```

输出:
```
options:
  -h, --help       show this help message and exit
  -t, --test       开始姓名测试
  -v, --version    显示版本信息
  --reload-data    重新加载资源数据
  --clear-history  清空所有历史计算结果
  --geo-help       显示经纬度查询帮助
```

---

## 示例脚本

完整的演示脚本:
```bash
# 运行完整演示
python demo_clear_history.py
```

该脚本会:
1. 创建测试数据
2. 显示历史记录
3. 演示三种清空方式
4. 验证清空结果

---

## 更新日志

### v1.1 (2025-12-05)
- ✨ 新增 `--clear-history` 命令行参数
- ✨ 新增交互界面 `clear` 命令
- ✨ 新增 `Storage.clear_all_records()` API
- ✨ 新增 `Storage.get_records_count()` API
- 📝 完善用户提示和错误处理
- 📝 添加日志记录

---

## 相关文件

- `modules/storage.py` - Storage 类实现
- `bazi.py` - 主程序入口
- `modules/ui.py` - 用户界面
- `demo_clear_history.py` - 功能演示脚本
- `test_ui_clear.py` - 单元测试脚本
