# 讯飞TTS配置指南

## ⚠️ IP白名单问题

讯飞TTS需要在控制台配置IP白名单才能使用。

### 错误信息
```
Your IP address is not allowed
```

### 解决方案

#### 方案1：配置IP白名单（推荐用于生产环境）

1. 访问讯飞控制台：https://console.xfyun.cn/services/tts
2. 进入"在线语音合成"服务
3. 找到"IP白名单"设置
4. 添加你的公网IP地址

**获取公网IP：**
```bash
curl ifconfig.me
```

#### 方案2：使用macOS say命令（当前默认）

项目已配置macOS自带的say命令作为备选方案：

```bash
# 使用Makefile（推荐）
make audio

# 或直接使用say命令
say -v Ting-Ting -f script.md -o output.aiff
afconvert -f m4af -d aac output.aiff output.m4a
```

**优点：**
- 无需配置，开箱即用
- 离线工作
- 免费无限制

**缺点：**
- 音质不如讯飞
- 发音人选择有限
- 仅支持macOS

#### 方案3：使用火山引擎TTS

```bash
python tts_volcengine.py \
    --text-file script.md \
    --output output.wav
```

需要配置火山引擎凭证（见volcengine_tts_complete_guide.md）

## 🎯 推荐使用场景

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 本地开发测试 | macOS say | 快速、免费 |
| 正式播客制作 | 讯飞TTS | 音质最佳 |
| 语音克隆 | 火山引擎 | 支持克隆 |
| CI/CD自动化 | macOS say 或 火山 | 无IP限制 |

## 📝 当前配置

项目Makefile已配置为默认使用macOS say命令，确保开箱即用。

如需切换到讯飞TTS：
1. 配置IP白名单
2. 修改Makefile中的audio命令
3. 使用tts_xunfei.py

## 🔧 环境变量

已在`.env`中配置：
```bash
XUNFEI_APP_ID=d018e2dc
XUNFEI_API_SECRET=MWExMTNmYmIyYzUzZjRkMmUzMTNlZWNm
XUNFEI_API_KEY=c90405383bccbb7dd5f93e9d940dca91
```

## ✅ 验证配置

```bash
# 测试当前TTS方案
make audio

# 检查生成的音频
ls -lh audio_exports/2025/
```

---

**当前状态：** ✅ 使用macOS say命令，无需额外配置
