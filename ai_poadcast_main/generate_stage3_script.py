#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate podcast script via LLM using a Stage 3 prompt file."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Optional

try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover
    OpenAI = None

try:
    import anthropic  # type: ignore
except ImportError:  # pragma: no cover
    anthropic = None

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

DEFAULT_PROVIDER = os.getenv("STAGE3_PROVIDER") or os.getenv("KEYPOINT_PROVIDER") or "deepseek"
DEFAULT_MODEL = os.getenv("STAGE3_MODEL") or os.getenv("KEYPOINT_MODEL") or "deepseek-chat"
DEFAULT_SUMMARY_PATH = Path("ai_poadcast_main/news_queue_with_summaries.json")
STAGE3_INPUT_DIR = Path("ai_poadcast_main/stage3_inputs")
STAGE3_OUTPUT_DIR = Path("脚本输出")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Stage 3 podcast script from prompt file.")
    parser.add_argument("--prompt", help="Path to Stage 3 prompt file (Markdown).")
    parser.add_argument("--date", help="Episode date (YYYY-MM-DD); derives prompt/output paths when --prompt 未指定。")
    parser.add_argument("--provider", default=DEFAULT_PROVIDER, help="LLM provider (openai/anthropic/deepseek)。")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="LLM model name。")
    parser.add_argument("--max-tokens", type=int, default=int(os.getenv("STAGE3_MAX_TOKENS", "1800")), help="Maximum tokens for response.")
    parser.add_argument("--temperature", type=float, default=float(os.getenv("STAGE3_TEMPERATURE", "0.4")), help="Sampling temperature。")
    parser.add_argument("--output", help="自定义输出文件路径；默认写入 脚本输出/<date>/episode_<date>_v1.md。")
    parser.add_argument("--overwrite", action="store_true", help="已存在目标文件时覆盖。")
    parser.add_argument("--print-only", action="store_true", help="仅打印生成结果，不写入文件。")
    return parser.parse_args()


def resolve_prompt_path(args: argparse.Namespace) -> tuple[Path, str]:
    from path_utils import safe_path
    if args.prompt:
        path = safe_path(args.prompt, Path.cwd())
        if not path.exists():
            sys.stderr.write(f"❌ Prompt 文件不存在：{path}\n")
            sys.exit(1)
        episode_date = args.date or path.stem.replace("episode_", "")[:10]
        return path, episode_date
    if not args.date:
        episode_date = date.today().isoformat()
    else:
        episode_date = args.date
    prompt_path = STAGE3_INPUT_DIR / episode_date / f"episode_{episode_date}_prompt.md"
    if not prompt_path.exists():
        sys.stderr.write(f"❌ 未找到默认 Prompt：{prompt_path}\n")
        sys.exit(1)
    return prompt_path, episode_date


def read_prompt(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        sys.stderr.write("⚠️ Prompt 内容为空。\n")
    return content


def call_openai(model: str, prompt: str, temperature: float, max_tokens: int) -> str:
    if OpenAI is None:
        raise RuntimeError("未安装 openai 库。")
    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional podcast script writer."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def call_anthropic(model: str, prompt: str, temperature: float, max_tokens: int) -> str:
    if anthropic is None:
        raise RuntimeError("未安装 anthropic 库。")
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        system="You are a professional podcast script writer.",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    parts = []
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text.strip())
    return "\n".join(parts).strip()


def call_deepseek(model: str, prompt: str, temperature: float, max_tokens: int) -> str:
    if requests is None:
        raise RuntimeError("未安装 requests 库。")
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_KEY")
    if not api_key:
        raise RuntimeError("缺少 DEEPSEEK_API_KEY。")
    base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com").rstrip("/")
    endpoint = f"{base_url}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional podcast script writer."},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    if resp.status_code >= 400:
        try:
            detail = resp.json()
        except json.JSONDecodeError:
            detail = resp.text[:200]
        raise RuntimeError(f"DeepSeek API 错误：HTTP {resp.status_code} {detail}")
    data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("DeepSeek 返回缺少 choices。")
    message = choices[0].get("message") or {}
    content = message.get("content", "").strip()
    if not content:
        raise RuntimeError("DeepSeek 返回内容为空。")
    return content


def generate_script(provider: str, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
    provider = provider.lower()
    
    # 定义备用方案
    fallback_providers = []
    if provider == "deepseek":
        fallback_providers = [("openai", "gpt-4o-mini"), ("anthropic", "claude-3-5-sonnet-20241022")]
    elif provider == "openai":
        fallback_providers = [("deepseek", "deepseek-chat"), ("anthropic", "claude-3-5-sonnet-20241022")]
    elif provider == "anthropic":
        fallback_providers = [("openai", "gpt-4o-mini"), ("deepseek", "deepseek-chat")]
    
    # 尝试主要provider
    try:
        if provider == "openai":
            return call_openai(model, prompt, temperature, max_tokens)
        if provider == "anthropic":
            return call_anthropic(model, prompt, temperature, max_tokens)
        if provider == "deepseek":
            return call_deepseek(model, prompt, temperature, max_tokens)
        raise RuntimeError(f"不支持的 provider：{provider}")
    except Exception as e:
        error_msg = str(e)
        # 检查是否是503或服务过载错误
        if "503" in error_msg or "too busy" in error_msg.lower() or "service_unavailable" in error_msg.lower():
            sys.stderr.write(f"⚠️ {provider} 服务繁忙，尝试切换备用LLM...\n")
            
            # 尝试备用providers
            for fallback_provider, fallback_model in fallback_providers:
                try:
                    sys.stderr.write(f"🔄 尝试使用 {fallback_provider} ({fallback_model})...\n")
                    if fallback_provider == "openai":
                        result = call_openai(fallback_model, prompt, temperature, max_tokens)
                    elif fallback_provider == "anthropic":
                        result = call_anthropic(fallback_model, prompt, temperature, max_tokens)
                    elif fallback_provider == "deepseek":
                        result = call_deepseek(fallback_model, prompt, temperature, max_tokens)
                    else:
                        continue
                    sys.stderr.write(f"✅ 成功使用 {fallback_provider}\n")
                    return result
                except Exception as fallback_error:
                    sys.stderr.write(f"❌ {fallback_provider} 也失败: {fallback_error}\n")
                    continue
            
            # 所有备用方案都失败
            raise RuntimeError(f"所有LLM服务都不可用。原始错误: {error_msg}")
        else:
            # 非503错误，直接抛出
            raise


def resolve_output_path(episode_date: str, output: Optional[str], overwrite: bool) -> Path:
    from path_utils import safe_path
    if output:
        return safe_path(output, Path.cwd())
    year = episode_date[:4]
    target_dir = STAGE3_OUTPUT_DIR / episode_date
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 如果不覆盖，自动找下一个可用版本号
    if not overwrite:
        version = 1
        while True:
            path = target_dir / f"episode_{episode_date}_v{version}.md"
            if not path.exists():
                return path
            version += 1
            if version > 99:  # 防止无限循环
                raise RuntimeError(f"版本号超过99，请检查目录：{target_dir}")
    
    return target_dir / f"episode_{episode_date}_v1.md"


def write_output(content: str, path: Path, overwrite: bool, print_only: bool) -> None:
    if print_only:
        print(content)
        return
    if path.exists() and not overwrite:
        raise RuntimeError(f"目标文件已存在：{path}（使用 --overwrite 覆盖）")
    path.write_text(content, encoding="utf-8")
    print(f"✅ 已生成脚本：{path}")


def main() -> None:
    args = parse_args()
    prompt_path, episode_date = resolve_prompt_path(args)
    prompt = read_prompt(prompt_path)
    try:
        script = generate_script(args.provider, args.model, prompt, args.temperature, args.max_tokens)
    except Exception as exc:
        sys.stderr.write(f"❌ 脚本生成失败：{exc}\n")
        sys.exit(1)

    output_path = resolve_output_path(episode_date, args.output, args.overwrite)
    try:
        write_output(script, output_path, args.overwrite, args.print_only)
    except Exception as exc:
        sys.stderr.write(f"❌ 写入失败：{exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
