#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Stage 3 prompt files from news summaries."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKDIR = Path(__file__).resolve().parent
DEFAULT_SUMMARY_PATH = WORKDIR / "news_queue_with_summaries.json"
STAGE3_DIR = WORKDIR / "stage3_inputs"

LLM_TEMPLATE = """你是《异乡早咖啡》播客的脚本作者大刘。现在需要将以下新闻要点编写成一期8分钟的播客脚本。

---

## 📰 本期新闻要点

{NEWS_BLOCKS}

---

## ✍️ 脚本要求

### 【基本原则】
1. **事实准确**：每个具体信息必须来自要点卡片，不得臆造
2. **来源标注**：关键信息后必须加"据XX官网/机构报道"
3. **口语化**：使用对话式语言，避免书面语
4. **听众视角**：多用"如果你正在准备申请..."、"这对你意味着..."
5. **时间感**：明确时间节点，如"从3月1日起"、"在2月底前"
6. **时长控制**：全文1500-1800字，口播时长≤8分钟，整期不超过5条新闻/数据点

### 【语言风格】
- ✅ 使用："这周最大的新闻是..."、"值得注意的是..."、"简单来说..."
- ❌ 避免："根据相关报道"、"有关部门表示"、"据悉"等模糊表述
- ✅ 数字重复：重要数字说2遍，如"延长1年，也就是从2年变成3年"
- ❌ 避免：连续3句以上都是数据，需要穿插解读

### 【结构要求】
每条新闻包含：
1. 引入（1句话吸引注意）
2. 核心事实（5W1H）
3. 背景解读（为什么重要）
4. 实用建议（听众怎么办）
5. 过渡语（连接下一条新闻）

---

## 📝 脚本模板（直接填充）

### 【开场白】(20秒 / 70-80字)

> 大家好，欢迎收听《异乡早咖啡》，我是[大刘]。今天是{EPISODE_DATE}，我们将在8分钟内快速带你盘点国际教育领域的重磅动态。
>
> 本期我们聚焦三个关键词：[话题1]、[话题2]、[话题3]。如果你正在关注国际教育行业全球动态，记得点击订阅。
>
> 那我们马上开始第一条新闻。

---

### 【主体内容-新闻1】(2分30秒 / 480-520字)

**[分节标题]** 🔴 重磅：[新闻标题]

> 本周最值得关注的，是据[来源]在[日期]发布的[一句话核心事件]。
>
> 换句话说，[用口语解释核心变化]。对[受众群体]来说，有三个重点要记住：
>
> **重点一**  
> [关键事实或数据]，意味着[影响解读]。
>
> **重点二**  
> [关键事实或数据]，意味着[影响解读]。
>
> **重点三**  
> [关键事实或数据]，意味着[影响解读]。
>
> 说完第一条，我们来看第二条。

---

### 【主体内容-新闻2】(2分30秒 / 480-520字)

[同上结构]

---

### 【主体内容-新闻3】(2分30秒 / 480-520字)

[同上结构]

---

### 【附加新闻/彩蛋】(可选，1分 / 200字)

[如无可删除]

---

### 【结尾】(40秒 / 120字)

> 今天的节目就到这里。如果你觉得有收获，欢迎分享给同样关注国际教育的朋友。也记得订阅《异乡早咖啡》，我们每天早上都会精选行业重磅资讯。  
> 我是大刘，我们明天见！
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Stage 3 prompt file from summaries.")
    parser.add_argument("--date", dest="episode_date", help="Episode date (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--count", type=int, default=3, help="Number of news items to include.")
    parser.add_argument("--min-priority", type=int, default=8, help="Minimum priority to consider.")
    parser.add_argument("--select", nargs="*", type=int, help="Explicitly select news indexes (1-based after sorting).")
    parser.add_argument("--summaries-file", default=str(DEFAULT_SUMMARY_PATH), help="Path to news_queue_with_summaries.json.")
    parser.add_argument("--output", help="Custom output path (defaults to stage3_inputs/<date>/episode_<date>_prompt.md).")
    parser.add_argument("--print-only", action="store_true", help="Print generated prompt without writing file.")
    return parser.parse_args()


def load_items(path: Path) -> List[dict]:
    if not path.exists():
        sys.stderr.write(f"❌ 找不到 summaries 文件：{path}\n")
        sys.exit(1)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"❌ 无法解析 JSON：{exc}\n")
        sys.exit(1)
    items = payload.get("items") or []
    if not items:
        sys.stderr.write("⚠️ summaries 文件为空，无法生成 Stage 3 Prompt。\n")
        sys.exit(1)
    return items


def normalize_date(raw: str) -> str:
    if not raw:
        return ""
    try:
        return datetime.strptime(raw[:10], "%Y-%m-%d").date().isoformat()
    except Exception:
        return raw


def pick_items(items: Sequence[dict], count: int, min_priority: int, select: List[int] | None) -> List[dict]:
    filtered = [item for item in items if item.get("priority", 0) >= min_priority]
    if not filtered:
        filtered = list(items)
    sorted_items = sorted(
        filtered,
        key=lambda x: (
            -(x.get("priority", 0) or 0),
            x.get("collected_at", ""),
            x.get("title", ""),
        ),
    )
    if select:
        chosen = []
        for idx in select:
            if 1 <= idx <= len(sorted_items):
                chosen.append(sorted_items[idx - 1])
            else:
                sys.stderr.write(f"⚠️ 忽略无效索引 {idx}\n")
        return chosen
    return sorted_items[:count]


def build_news_blocks(items: Sequence[dict]) -> str:
    blocks = []
    for idx, item in enumerate(items, start=1):
        keywords = ", ".join(item.get("tags") or [])
        priority = item.get("priority", "-")
        published = normalize_date(item.get("published", ""))
        summary = (item.get("chinese_summary") or "⚠️ 暂无中文摘要，请补充。").strip()
        block = "\n".join([
            f"### 新闻{idx}：{item.get('title', '未命名新闻')}",
            f"- 来源：{item.get('source', '未知来源')} | 优先级：{priority} | 发布：{published}",
            f"- 标签：{keywords or '未填写'}",
            "",
            summary,
        ])
        blocks.append(block)
    return "\n\n".join(blocks)


def build_prompt(items: Sequence[dict], episode_date: str, generated_date: str) -> str:
    news_cards = []
    for idx, item in enumerate(items, start=1):
        summary = (item.get("chinese_summary") or "⚠️ 暂无中文摘要，请补充。").strip()
        card = "\n".join([
            f"### 新闻{idx}：{item.get('title', '未命名新闻')}",
            f"- 来源：{item.get('source', '未知来源')} | 优先级：{item.get('priority', '-')}",
            f"- 链接：{item.get('url', '无')}",
            "",
            summary,
        ])
        news_cards.append(card)
    cards_section = "\n\n".join(news_cards)

    news_blocks = build_news_blocks(items)
    llm_prompt = LLM_TEMPLATE.replace("{NEWS_BLOCKS}", news_blocks.strip()).replace("{EPISODE_DATE}", episode_date)

    body = [
        f"# Episode {episode_date} Prompt",
        "",
        f"- 生成日期：{generated_date}",
        f"- 自动汇总条数：{len(items)}",
        "",
        "## 📰 本期新闻概览",
        "",
        cards_section,
        "",
        "## Prompt 模板",
        "```markdown",
        llm_prompt.strip(),
        "```",
        "",
        "---",
        "",
        "> 本文件由 prepare_stage3_prompt.py 自动生成，可根据需要调整标题、关键词等信息。",
    ]
    return "\n".join(body) + "\n"


def write_output(content: str, episode_date: str, output: str | None, print_only: bool) -> None:
    if print_only:
        print(content)
        return
    if output:
        path = Path(output)
    else:
        target_dir = STAGE3_DIR / episode_date
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"episode_{episode_date}_prompt.md"
    path.write_text(content, encoding="utf-8")
    print(f"✅ 已生成 Stage 3 Prompt：{path}")


def main() -> None:
    args = parse_args()
    summaries_path = Path(args.summaries_file)
    items = load_items(summaries_path)
    selected = pick_items(items, args.count, args.min_priority, args.select)
    if not selected:
        sys.stderr.write("⚠️ 未选中任何新闻，已退出。\n")
        sys.exit(1)

    episode_date = args.episode_date or date.today().isoformat()
    generated_date = date.today().isoformat()
    content = build_prompt(selected, episode_date, generated_date)
    write_output(content, episode_date, args.output, args.print_only)


if __name__ == "__main__":
    main()
