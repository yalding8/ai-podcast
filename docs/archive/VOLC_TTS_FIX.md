# 火山TTS配置问题修复

## 🔍 问题诊断

**错误：** `HTTP 400` - server rejected WebSocket connection

**根本原因：** 
- 当前使用的是 `VOLC_ACCESSKEY`（AK/SK方式）
- 但代码中使用的是 `auth_token` 字段，需要的是 **API Key** 或 **Token**

## ✅ 解决方案

### 方案1：获取API Key（推荐）

1. 访问火山控制台：https://console.volcengine.com/speech/service/8
2. 进入"应用管理" → 找到AppID `1474910664`
3. 点击"凭证管理" → "生成Token"或"API Key"
4. 复制Token值

### 方案2：修改代码使用AK/SK

如果只有AK/SK，需要修改认证方式（较复杂，不推荐）

## 📝 更新.env配置

将`.env`中的火山配置改为：

```bash
# 火山引擎TTS凭证
VOLC_APPID="1474910664"
VOLC_AUTH_TOKEN="你的API_Key或Token"  # 从控制台获取
# VOLC_ACCESSKEY 和 VOLC_SECRETKEY 可以删除或注释
```

## 🧪 测试步骤

1. 更新.env后测试：
```bash
set -a; source .env; set +a
export TTS_TEXT_FILE="脚本输出/2025-11-03/episode_2025-11-03_v1.md"
export TTS_OUTPUT_FILE="audio_exports/2025/test_volc.wav"
python tts_volcengine.py
```

2. 如果成功，更新Makefile使用火山TTS

## 🔗 参考文档

- 火山控制台：https://console.volcengine.com/speech/service/8
- 完整指南：volcengine_tts_complete_guide.md

---

**当前状态：** 等待从火山控制台获取正确的API Key/Token
