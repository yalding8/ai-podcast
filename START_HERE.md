#!/usr/bin/env markdown
# Start Here · Daily Workflow

欢迎来到 AI POADCAST 项目！如果你只想快速跑一遍每日流程，按照下面三个动作即可：

1. **准备环境**
   ```bash
   source .venv/bin/activate
   source .env                             # 载入 KEYPOINT_PROVIDER/KEYPOINT_MODEL 等默认配置
   export DEEPSEEK_API_KEY="你的密钥"    # 或 OPENAI_API_KEY / ANTHROPIC_API_KEY
   ```

2. **一键运行 Stage 0-3**
   ```bash
   python ai_poadcast_main/daily_workflow.py
   ```
   默认动作：
   - Stage 0：抓取 RSS（自动导入前 3 条优先级 ≥9 的新闻，合并 Demo 新闻源，并写入 `daily_review.txt`）；
   - Stage 2：批量生成中文要点 (`news_queue_with_summaries.json`、`daily_review_cn.md`)；
   - Stage 2：交互式审核并写入 `source_archive/`；
   - Stage 3：自动生成 Prompt + 脚本初稿 (`stage3_inputs/`、`脚本输出/.._v1.md`)。

   途中会提示你在终端确认要导入的新闻。如果只想执行部分阶段，可使用以下参数：
   - `--collect/--scrape/--auto-import`：仅采集或调整自动导入策略；
   - `--extract`、`--review`、`--stage3`：单独控制 Stage 2/3；
   - `--stage3-select 1 3 5`：指定脚本使用的新闻序号。
   - `--no-demo`：跳过 demo 新闻源的合并。

完成后，请在 QA Checklist 中记录修改，必要时继续 Stage 4-6（详见 `README.md` 第 4 节）。
