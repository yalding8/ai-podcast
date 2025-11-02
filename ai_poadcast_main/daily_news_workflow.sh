#!/bin/bash
set -e

echo "🌅 $(date) - 调用 daily_workflow.py 处理 Stage0-3"
python ai_poadcast_main/daily_workflow.py --collect --extract --review --stage3 "$@"
