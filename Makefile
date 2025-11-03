# AI POADCAST Makefile
# 快速执行常用命令

.PHONY: help collect extract script audio publish full-pipeline test clean

help:
	@echo "AI POADCAST 播客制作工具"
	@echo ""
	@echo "可用命令:"
	@echo "  make collect       - 采集新闻（RSS + 考试网站）"
	@echo "  make extract       - 提取要点摘要"
	@echo "  make script        - 生成播客脚本"
	@echo "  make audio         - 合成音频"
	@echo "  make postprocess   - 音频后期处理"
	@echo "  make publish       - 发布到各平台"
	@echo "  make full-pipeline - 完整流水线（采集→脚本→音频→发布）"
	@echo "  make test          - 运行测试"
	@echo "  make clean         - 清理临时文件"

collect:
	@echo "📰 采集新闻..."
	python ai_poadcast_main/collect_rss_feeds.py
	python ai_poadcast_main/exam_sites_crawler.py

extract:
	@echo "📝 提取要点摘要..."
	python ai_poadcast_main/daily_workflow.py --extract

script:
	@echo "✍️  生成播客脚本..."
	python ai_poadcast_main/daily_workflow.py --stage3

audio:
	@echo "🎙️  合成音频（火山TTS）..."
	@set -a; [ -f .env ] && . ./.env; set +a; \
	TODAY=$$(date +%Y-%m-%d); \
	YEAR=$$(date +%Y); \
	SCRIPT_DIR="脚本输出/$$TODAY"; \
	if [ -d "$$SCRIPT_DIR" ]; then \
		SCRIPT=$$(ls -t "$$SCRIPT_DIR"/episode_$${TODAY}_v*.md 2>/dev/null | head -1); \
		if [ -z "$$SCRIPT" ]; then \
			SCRIPT="$$SCRIPT_DIR/episode_$${TODAY}_final.md"; \
		fi; \
	else \
		echo "❌ 脚本目录不存在: $$SCRIPT_DIR"; \
		exit 1; \
	fi; \
	if [ ! -f "$$SCRIPT" ]; then \
		echo "❌ 未找到脚本文件"; \
		exit 1; \
	fi; \
	echo "✅ 使用最新脚本: $$SCRIPT"; \
	python tts_volcengine_rest.py \
		--text-file "$$SCRIPT" \
		--output "audio_exports/$$YEAR/episode_$${TODAY}_volcengine.mp3"

postprocess:
	@echo "🎬 音频后期处理..."
	@TODAY=$$(date +%Y-%m-%d); \
	YEAR=$$(date +%Y); \
	if [ -f "legacy/audio_postprocess.py" ]; then \
		python legacy/audio_postprocess.py \
			--input "audio_exports/$$YEAR/episode_$${TODAY}_volcengine.mp3" \
			--output "audio_exports/$$YEAR/episode_$${TODAY}_final.mp3" \
			--normalize-only; \
	else \
		echo "⚠️  音频后期处理脚本不存在，跳过..."; \
		cp "audio_exports/$$YEAR/episode_$${TODAY}_volcengine.mp3" "audio_exports/$$YEAR/episode_$${TODAY}_final.mp3"; \
	fi

publish:
	@echo "📡 发布节目..."
	@set -a; [ -f .env ] && . ./.env; set +a; \
	TODAY=$$(date +%Y-%m-%d); \
	YEAR=$$(date +%Y); \
	if [ -f "legacy/auto_publish.py" ]; then \
		python legacy/auto_publish.py \
			--audio "audio_exports/$$YEAR/episode_$${TODAY}_final.mp3" \
			--title "异乡早咖啡 $$TODAY" \
			--description "今日国际教育资讯" \
			--platforms rss; \
	else \
		echo "⚠️  发布脚本不存在，跳过..."; \
		echo "✅ 音频已生成: audio_exports/$$YEAR/episode_$${TODAY}_final.mp3"; \
	fi

full-pipeline:
	@echo "🚀 启动完整流水线..."
	python ai_poadcast_main/daily_workflow.py
	@$(MAKE) audio
	@$(MAKE) postprocess || true
	@$(MAKE) publish || true
	@echo "✅ 流水线完成！"

test:
	@echo "🧪 运行测试..."
	pytest tests/ -v

clean:
	@echo "🧹 清理临时文件..."
	rm -rf audio_parts/temp/
	rm -rf script_chunks/temp/
	rm -f ai_poadcast_main/*.pyc
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
