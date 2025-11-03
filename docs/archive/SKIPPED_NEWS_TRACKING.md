# 跳过新闻追踪功能

## 功能说明

当你在审核新闻时选择"跳过"，系统会自动记录该新闻的URL，下次运行时不再显示。

## 工作原理

### 记录文件
- **位置**: `ai_poadcast_main/.skipped_urls.json`
- **格式**: JSON，包含所有跳过的URL列表

### 触发时机
在 `process_queue.py` 交互式审核中，当你选择：
- `[n]跳过` - 记录URL
- `[o]打开浏览器` 后选择 `[n]跳过` - 记录URL

### 过滤时机
每次运行 `process_queue.py` 时，自动过滤已跳过的URL。

## 使用示例

### 场景1：首次审核
```bash
python ai_poadcast_main/process_queue.py

# 输出：
[1/66] 优先级: 10
标题: Some news title...
操作: [y]导入 [n]跳过 [s]停止 [o]打开浏览器 [q]退出? n
  ⏭️ 已跳过（已记录，下次不再显示）
```

### 场景2：再次运行
```bash
python ai_poadcast_main/process_queue.py

# 输出：
[DEBUG] 已过滤 42 条之前跳过的新闻
📥 队列中共有 24 条新闻
```

## 管理跳过记录

### 查看已跳过的URL
```bash
cat ai_poadcast_main/.skipped_urls.json | python -m json.tool | head -20
```

### 清空跳过记录
```bash
rm ai_poadcast_main/.skipped_urls.json
```

### 移除特定URL
```bash
python3 << 'EOF'
import json
from pathlib import Path

file = Path("ai_poadcast_main/.skipped_urls.json")
data = json.loads(file.read_text())
urls = data.get('urls', [])

# 移除特定URL
url_to_remove = "https://example.com/news"
if url_to_remove in urls:
    urls.remove(url_to_remove)
    data['urls'] = urls
    file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"✅ 已移除: {url_to_remove}")
else:
    print(f"⚠️ URL不存在")
EOF
```

## 文件格式

```json
{
  "updated_at": "2025-11-03T10:30:00",
  "urls": [
    "https://example.com/news1",
    "https://example.com/news2",
    "https://example.com/news3"
  ]
}
```

## 优点

1. ✅ **避免重复审核** - 跳过的新闻不再出现
2. ✅ **提高效率** - 专注于新内容
3. ✅ **持久化记录** - 重启后仍然有效
4. ✅ **易于管理** - 可随时查看和清理

## 与其他去重机制的关系

### 三层过滤
1. **已存档URL** (`source_archive/_index.json`) - 已导入的新闻
2. **已跳过URL** (`.skipped_urls.json`) - 手动跳过的新闻
3. **标题相似度** - 重复标题的新闻

### 过滤顺序
```
RSS采集 → URL去重(已存档) → 队列保存 → 加载队列 → URL去重(已跳过) → 显示给用户
```

## 注意事项

1. **文件位置**: `.skipped_urls.json` 以点开头，是隐藏文件
2. **不影响采集**: 跳过记录只在审核阶段生效，不影响RSS采集
3. **可恢复**: 删除 `.skipped_urls.json` 即可重新审核所有新闻
4. **URL精确匹配**: 必须完全相同的URL才会被过滤

## 工作流集成

### make full-pipeline
```bash
make full-pipeline
# 自动跳过之前标记的新闻
```

### daily_workflow.py
```bash
python ai_poadcast_main/daily_workflow.py
# 自动应用跳过过滤
```

---

**创建日期**: 2025-11-03  
**状态**: ✅ 已实现并测试
