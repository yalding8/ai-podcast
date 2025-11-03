# 自动化功能使用指南

本文档介绍新增的4个自动化功能模块的使用方法。

---

## 1. 考试官网自动爬虫

### 功能说明
自动监控IELTS、TOEFL、GRE、GMAT等考试官网的最新动态，发现新内容时自动保存。

### 使用方法

**基础用法：**
```bash
python ai_poadcast_main/exam_sites_crawler.py
```

**集成到每日工作流：**
```bash
# 在daily_workflow.py中已自动集成
python ai_poadcast_main/daily_workflow.py --collect
```

### 输出文件
- `ai_poadcast_main/exam_updates/exam_updates_YYYYMMDD_HHMMSS.json` - 新发现的考试动态
- `ai_poadcast_main/exam_updates/content_cache.json` - 内容哈希缓存（去重）

### 支持的考试网站
- IELTS官网
- TOEFL/ETS官网
- GRE官网
- 可扩展其他考试网站

---

## 2. 音频后期处理

### 功能说明
对TTS生成的音频进行专业后期处理，包括音量标准化、降噪、添加片头片尾、背景音乐等。

### 使用方法

**仅标准化音量：**
```bash
python audio_postprocess.py \
    --input audio_exports/2025/episode_2025-11-03_xiaoyan.mp3 \
    --output audio_exports/2025/episode_2025-11-03_final.mp3 \
    --normalize-only
```

**完整后期处理：**
```bash
python audio_postprocess.py \
    --input audio_exports/2025/episode_2025-11-03_xiaoyan.mp3 \
    --output audio_exports/2025/episode_2025-11-03_final.mp3 \
    --intro assets/intro.mp3 \
    --outro assets/outro.mp3 \
    --music assets/background_music.mp3 \
    --music-volume 0.1
```

### 功能模块
- **音量标准化** - 响度标准化到-16 LUFS
- **降噪处理** - 高通/低通滤波
- **片头片尾** - 自动拼接片头片尾音频
- **背景音乐** - 混音背景音乐（可调音量）
- **格式转换** - 支持多种音频格式

### 依赖
需要安装ffmpeg：
```bash
brew install ffmpeg  # macOS
```

---

## 3. 自动发布功能

### 功能说明
一键发布播客到多个平台，支持小宇宙、喜马拉雅、RSS Feed等。

### 使用方法

**发布到RSS Feed（推荐）：**
```bash
python auto_publish.py \
    --audio audio_exports/2025/episode_2025-11-03_final.mp3 \
    --title "异乡早咖啡 2025-11-03" \
    --description "今日国际教育资讯" \
    --platforms rss
```

**发布到多个平台：**
```bash
python auto_publish.py \
    --audio audio_exports/2025/episode_2025-11-03_final.mp3 \
    --title "异乡早咖啡 2025-11-03" \
    --description "今日国际教育资讯" \
    --platforms xiaoyuzhou ximalaya rss \
    --cover assets/cover.jpg
```

### 配置API密钥

在`.env`文件中添加：
```bash
# 小宇宙
XIAOYUZHOU_API_KEY=your_api_key_here

# 喜马拉雅
XIMALAYA_API_KEY=your_api_key_here

# 音频CDN地址
AUDIO_BASE_URL=https://your-cdn.com/audio
```

### 输出文件
- `audio_exports/podcast_feed.xml` - RSS Feed文件
- `ai_poadcast_main/publish_log.json` - 发布历史记录

### RSS Feed托管
生成的RSS Feed需要托管到公网服务器，推荐方案：
- GitHub Pages
- Netlify
- 阿里云OSS
- 腾讯云COS

---

## 4. CI/CD流程

### 功能说明
使用GitHub Actions实现全自动播客生产流水线，每天定时运行或手动触发。

### 配置步骤

**1. 配置GitHub Secrets**

在GitHub仓库设置中添加以下Secrets：
- `OPENAI_API_KEY` - OpenAI API密钥
- `XUNFEI_APP_ID` - 讯飞应用ID
- `XUNFEI_API_KEY` - 讯飞API Key
- `XUNFEI_API_SECRET` - 讯飞API Secret
- `XIAOYUZHOU_API_KEY` - 小宇宙API密钥（可选）
- `XIMALAYA_API_KEY` - 喜马拉雅API密钥（可选）

**2. 启用GitHub Actions**

推送代码到GitHub后，Actions会自动启用。

**3. 手动触发**

在GitHub仓库页面：
1. 点击 Actions 标签
2. 选择 "Podcast Production Pipeline"
3. 点击 "Run workflow"
4. 选择要运行的阶段（all/collect/extract/script/audio/publish）

### 自动运行
默认每天UTC时间00:00（北京时间08:00）自动运行完整流水线。

### 流程阶段
1. **collect-news** - 采集新闻
2. **extract-summaries** - 提取摘要
3. **generate-script** - 生成脚本
4. **synthesize-audio** - 合成音频
5. **publish-episode** - 发布节目

### 查看运行结果
在Actions页面可以查看每次运行的日志和产出物（Artifacts）。

---

## 5. 快速命令（Makefile）

为简化操作，提供了Makefile快捷命令：

```bash
# 查看所有命令
make help

# 采集新闻
make collect

# 提取摘要
make extract

# 生成脚本
make script

# 合成音频
make audio

# 音频后期处理
make postprocess

# 发布节目
make publish

# 完整流水线
make full-pipeline

# 运行测试
make test

# 清理临时文件
make clean
```

---

## 6. 完整工作流示例

### 本地手动流程
```bash
# 1. 采集新闻
make collect

# 2. 提取摘要并生成脚本
python ai_poadcast_main/daily_workflow.py

# 3. 合成音频
make audio

# 4. 音频后期处理
make postprocess

# 5. 发布
make publish
```

### 一键自动化
```bash
make full-pipeline
```

### GitHub Actions自动化
1. 推送代码到GitHub
2. 配置Secrets
3. 等待每天自动运行，或手动触发

---

## 7. 故障排查

### 考试爬虫失败
- 检查网络连接
- 考试网站可能更新了页面结构，需要更新选择器
- 查看`ai_poadcast_main/exam_updates/`目录下的日志

### 音频处理失败
- 确认已安装ffmpeg：`ffmpeg -version`
- 检查输入文件是否存在
- 查看错误信息中的ffmpeg命令

### 发布失败
- 检查API密钥是否正确配置
- 确认音频文件路径正确
- 查看`ai_poadcast_main/publish_log.json`中的错误信息

### CI/CD失败
- 检查GitHub Secrets是否配置完整
- 查看Actions运行日志
- 确认requirements.txt包含所有依赖

---

## 8. 最佳实践

1. **每日运行** - 使用GitHub Actions定时任务，保持内容更新
2. **质量检查** - 音频合成后人工审听，确保质量
3. **备份数据** - 定期备份`source_archive/`和`audio_exports/`
4. **监控额度** - 定期检查TTS和API调用额度
5. **版本控制** - 重要配置文件纳入Git管理

---

## 9. 扩展开发

### 添加新的考试网站
编辑`ai_poadcast_main/exam_sites_crawler.py`，添加新的爬取方法：

```python
def crawl_new_exam(self) -> List[Dict]:
    results = []
    try:
        url = "https://new-exam-site.com/news"
        # 实现爬取逻辑
    except Exception as e:
        print(f"爬取失败: {e}")
    return results
```

### 添加新的发布平台
编辑`auto_publish.py`，添加新的发布方法：

```python
def publish_to_new_platform(self, audio_file, title, description):
    # 实现发布逻辑
    pass
```

### 自定义音频处理
在`audio_postprocess.py`中添加新的处理方法，使用ffmpeg滤镜。

---

## 10. 相关文档

- [README.md](README.md) - 项目总览
- [START_HERE.md](START_HERE.md) - 快速开始
- [QUICK_START_QUALITY.md](QUICK_START_QUALITY.md) - 提升新闻质量
- [volcengine_tts_complete_guide.md](volcengine_tts_complete_guide.md) - 火山TTS指南
