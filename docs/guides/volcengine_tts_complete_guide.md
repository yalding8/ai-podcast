# Volcengine MaaS TTS V3 完整流程指南

本指南覆盖从获取火山引擎 MaaS（模型服务）语音端点到通过仓库中的 `tts_volcengine.py` 批量生成播客音频的全部步骤，适用于需要 **双向流式、复刻、混音** 等高级能力的生产环境。

> ⚠️ **尚未开通 MaaS？**  
> 如果当前账号为个人认证，控制台里看不到 “创建 Endpoint” 按钮，说明你尚未获准使用 MaaS 语音服务。此时仍然可以使用 openspeech 公共接口：  
> - 参考官方 demo `vendor/volcengine_ws_demo/examples/volcengine/binary.py`  
> - 命令示例：  
>   ```bash
>   PYTHONPATH="vendor/volcengine_ws_demo" \
>   .venv/bin/python vendor/volcengine_ws_demo/examples/volcengine/binary.py \
>     --appid "你的openspeech AppID" \
>     --access_token "你的token" \
>     --voice_type "zh_female_cancan_mars_bigtts" \
>     --text "$(tr '\n' ' ' < script.txt)"
>   ```  
> - openspeech 接口不支持复刻 / 混音，高级功能需要申请企业版 MaaS。
>
> 以下章节聚焦 MaaS V3 的完整流程；当你升级到企业权限后，可按本文档重新配置。

---

## 1. 准备工作

| 项目 | 说明 |
|------|------|
| 火山引擎账号 | https://console.volcengine.com，需完成实名认证 |
| MaaS 服务开通 | 控制台 → 产品与服务 → MaaS（模型服务）→ 语音合成<br>选择按量计费或资源包 |
| 语音端点 | 在 MaaS 语音合成控制台创建 Endpoint，记下 Endpoint ID、可用音色、所属集群<br>（若无创建权限，请先参考“附录：openspeech 个人账号方案”或联系商务开通企业 MaaS） |
| 凭证 | 支持两种鉴权：<br>- **API Key**（推荐）<br>- **AK/SK**（AccessKey/SecretKey） |

> ⚠️ openspeech 公共接口与 MaaS 协议不同。如果你使用的是 openspeech，请继续使用官方 demo (`vendor/volcengine_ws_demo/examples/...`)；本指南只针对 MaaS V3。

---

## 2. 收集关键信息

在 Endpoint 详情页或凭证中心找到并抄录以下内容：

| 名称 | 在控制台的位置 | 备注 |
|------|----------------|------|
| `VOLC_APP_ID` | MaaS 应用管理 → 应用详情 → AppID | 区分大小写 |
| `VOLC_AUTH_TOKEN` | 如果启用 API Key 鉴权：安全配置 → API Key | 如果使用 AK/SK，可跳过，改设 `VOLC_ACCESSKEY`/`VOLC_SECRETKEY` |
| `VOLC_ACCESSKEY` / `VOLC_SECRETKEY` | IAM 管理 → 访问控制 → 子账号密钥 | 与 API Key 二选一 |
| `VOLC_MAAS_ENDPOINT` | Endpoint 详情 → WebSocket 接入地址 | 形如 `wss://maas-api.ml-platform-cn-xxx.volces.com/api/v2/endpoint/<endpoint_id>/audio/speech/ws` |
| `VOLC_CLUSTER` | Endpoint 配置中展示的集群名称 | 常见：`volcano_tts`、`volcano_icl` 等；若 Endpoint 限定集群需显式设置 |
| `VOLC_VOICE_TYPE` | 支持的音色 ID | 默认脚本使用 `S_zh_general` |
| `VOLC_VOICE_CLONE_ID`（可选） | 复刻音色 ID | 前提是已开通复刻 |
| `VOLC_MIX_CONFIG`（可选） | 混音 JSON 配置 | 例如 `[{"voice_type":"S_zh_A","gain":0.7},{"voice_type":"bgm_pop","gain":0.3}]` |

---

## 3. 本地环境配置

1. **克隆或进入仓库**  
   确保当前目录为 `/Users/ningding/Desktop/AI POADCAST`。

2. **激活虚拟环境**  
   ```bash
   source .venv/bin/activate
   ```

3. **安装依赖**  
   `tts_volcengine.py` 仅依赖 `websockets`（其余来自标准库 & vendor 协议）：
   ```bash
   .venv/bin/python -m pip install --upgrade pip
   .venv/bin/python -m pip install websockets
   ```

4. **可选：处理代理**  
   若本机设置了 `ALL_PROXY/HTTPS_PROXY`，但不需要经过代理访问 Volcengine，可在运行命令前清空：
   ```bash
   unset ALL_PROXY HTTPS_PROXY HTTP_PROXY
   ```
   如果必须使用 SOCKS 代理，请额外安装 `python-socks`。

---

## 4. 配置环境变量

可以直接在终端 `export`，或创建 `.env`/`launch.json`。以下示例展示了最常用的变量：

```bash
export VOLC_APP_ID="xxxxxxxx"
export VOLC_AUTH_TOKEN="yyyyyyyyyyyy"      # 或使用 AK/SK：export VOLC_ACCESSKEY=... export VOLC_SECRETKEY=...
export VOLC_MAAS_ENDPOINT="wss://maas-api.ml-platform-cn-xx.volces.com/api/v2/endpoint/maas-xxxxxxxx/audio/speech/ws"

# 可选配置：
export VOLC_CLUSTER="volcano_tts"          # 若 Endpoint 限定集群，务必显式设置
export VOLC_VOICE_TYPE="S_zh_general"
export VOLC_VOICE_CLONE_ID="clone_abc123"  # 复刻音色
export VOLC_MIX_CONFIG='[{"voice_type":"S_zh_A","gain":0.8},{"voice_type":"bgm_pop","gain":0.2}]'
export TTS_OUTPUT_FILE="播客第001期.wav"
export TTS_TEXT_FILE="script.txt"
export TTS_ENCODING="wav"                  # 可改 mp3/ogg
export TTS_SAMPLE_RATE="24000"
export TTS_SPEED="0.95"
export TTS_VOLUME="1.05"
export TTS_PITCH="0.0"
```

建议将这些变量写入 Shell 启动脚本或 `.env`，避免每次手工输入。

---

## 5. 运行脚本生成音频

1. **准备输入脚本**  
   将最新播客文稿保存为 `script.txt`。脚本会自动读取该文件（可通过 `TTS_TEXT_FILE` 指定其它路径）。

2. **执行命令**  
   ```bash
   .venv/bin/python tts_volcengine.py
   ```

3. **监控日志**  
   - 首次连接会输出 `Connecting to ...`，成功后可见 `x-tt-logid`。
   - 文本会被分块发送，日志显示 `已发送文本分段 n/m`。
   - 收到最后一个音频包后打印 `音频已保存：...`。

4. **检查输出**  
   默认音频写入 `output.wav`（或 `TTS_OUTPUT_FILE` 指定的位置）。可以用播放器试听，确认停顿、音质、混音效果符合预期。

---

## 6. 高级配置

### 6.1 语速/音量/音调调节
- `TTS_SPEED`：0.5–2.0，1.0 为原速。
- `TTS_VOLUME`：0.1–3.0，1.0 为默认音量。
- `TTS_PITCH`：单位为半音，相对音调调整；常规播客建议 -2.0 到 +2.0。

### 6.2 复刻音色
1. 在 MaaS 控制台上传样本并等待审核，获得 `voice_clone_id`。
2. 将 ID 设置到 `VOLC_VOICE_CLONE_ID`。脚本会自动加到请求体里。

### 6.3 混音轨道
- 使用 `VOLC_MIX_CONFIG` 指定多个轨道，每个轨道包含 `voice_type` 和 `gain` 等字段。
- MaaS 端点需支持混音功能；否则会返回错误。

### 6.4 自定义额外参数
- 若官方文档提供了额外字段，可通过 `VOLC_AUDIO_EXTRAS`（JSON）和 `VOLC_REQUEST_EXTRAS` 注入。

---

## 7. 与播客生产流程衔接

1. **脚本生成**：按照 `ai_poadcast_main/stage3_script_generation.md` 的模板、`Master action plan` 的节奏，从 `要点卡片` 产出 `script.txt`。
2. **语音合成**：运行 `tts_volcengine.py` 得到音频文件（可重命名为 `国际教育周报_第001期.mp3` 等）。
3. **后期处理**：如需降噪、归一化，可使用 Audition、Auphonic 或 FFmpeg。
4. **上架**：结合 show notes 与音频链接，发布到播客平台。

整个链路最长耗时点在首次配置；脚本稳定后，日常生产仅需替换脚本文本并重新执行即可。

---

## 8. 个人账号（openspeech）快速方案

如果你尚未获得 MaaS 企业权限，可先用 openspeech 接口完成基础播客语音合成。主要区别：不需要 Endpoint、仅支持官方音色、暂不支持复刻/混音。

### 8.1 开通与获取密钥
1. 访问 https://console.volcengine.com/speech/service/8 （智能语音 → 语音合成）。  
2. 点击“应用管理”→“创建应用”，记录 `AppID`。  
3. 在同一页面的“凭证管理”里生成 `Token`（可设置有效期）。  
4. 下载安装 openspeech SDK（仓库已包含官方 WebSocket demo 于 `vendor/volcengine_ws_demo/`）。

### 8.2 体验步骤
```bash
cd "/Users/ningding/Desktop/AI POADCAST"
PYTHONPATH="vendor/volcengine_ws_demo" \
.venv/bin/python vendor/volcengine_ws_demo/examples/volcengine/binary.py \
  --appid "你的AppID" \
  --access_token "你的Token" \
  --voice_type "zh_female_cancan_mars_bigtts" \
  --text "$(tr '\n' ' ' < script.txt)"
```
输出文件默认保存在 `vendor/volcengine_ws_demo/` 目录内（文件名即音色 ID）。

### 8.3 能力与限制
- ✅ 成本低、配置简单，适合快速验证。  
- ✅ 覆盖官方提供的中文/英文播报音色。  
- ❌ 不支持自定义 mix/复刻；高级参数（情感、背景音等）受限。  
- ❌ 如需稳定生产，可在后续申请 MaaS 企业版并迁移到本文档主流程。

---

## 9. 常见问题排查

| 现象 | 可能原因 | 解决方案 |
|------|----------|----------|
| `Missing environment variable` | 未设置必须的变量 | 检查 `VOLC_APP_ID`、`VOLC_AUTH_TOKEN` 等是否 export |
| 连接时报 `ImportError: python-socks` | 环境变量中存在 SOCKS 代理 | `unset ALL_PROXY` 或安装 `python-socks` |
| `HTTP 404` | 端点 URL 与账号不匹配，或仍使用 openspeech 地址；个人账号尚未获得 MaaS 权限 | 重新复制 MaaS Endpoint；若无端点权限，请联系商务开通或改用 openspeech demo |
| `HTTP 502` 或 `ClientSDKRequestError` | Endpoint 状态异常 / 集群、音色配置不对 | 检查 `VOLC_CLUSTER`、`VOLC_VOICE_TYPE`，带上日志的 `req_id` 联系支持 |
| 生成的音频为空 | 脚本文本为空或只有空白 | 确认 `script.txt` 内容，脚本会在日志中提示 |
| `ModuleNotFoundError: protocols` | 未将 vendor demo 加入路径 | 保留 `vendor/volcengine_ws_demo` 目录，脚本会自动 `sys.path.insert` |

如需与官方支持沟通，把日志中的 `x-tt-logid`/`req_id` 一并提供，可加快定位。

---

## 10. 附录：测试命令速查

| 场景 | 命令 |
|------|------|
| 单段文本快速验证 | `TTS_TEXT_FILE=demo.txt .venv/bin/python tts_volcengine.py` |
| 指定输出格式为 MP3 | `export TTS_ENCODING=mp3` 后运行脚本 |
| 使用 API Key 鉴权 | 仅设置 `VOLC_APP_ID`、`VOLC_AUTH_TOKEN`，无需 AK/SK |
| 使用 AK/SK 鉴权 | `export VOLC_ACCESSKEY=...`、`export VOLC_SECRETKEY=...` 并清除 `VOLC_AUTH_TOKEN` |
| 手动调用 openspeech demo（非 MaaS） | 参考 `vendor/volcengine_ws_demo/examples/volcengine/binary.py` |

---

完成上述配置后，即可在 1 分钟内从最新播客脚本批量生成高质量语音，为下游剪辑、分发提供可靠素材。祝制作顺利！***
