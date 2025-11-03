#!/usr/bin/env python3
"""
新闻队列处理器 - 调试版本
"""

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import requests
except ImportError:
    requests = None


def init_translator(provider: str, model: str):
    """初始化翻译客户端"""
    if provider == 'openai':
        if OpenAI is None:
            print("⚠️ 未安装 openai 库，无法启用摘要翻译。")
            return None
        try:
            client = OpenAI()
        except Exception as exc:  # pragma: no cover
            print(f"⚠️ 无法初始化 OpenAI 客户端：{exc}")
            return None
    elif provider == 'anthropic':
        if anthropic is None:
            print("⚠️ 未安装 anthropic 库，无法启用摘要翻译。")
            return None
        try:
            client = anthropic.Anthropic()
        except Exception as exc:  # pragma: no cover
            print(f"⚠️ 无法初始化 Anthropic 客户端：{exc}")
            return None
    else:
        print(f"⚠️ 未知翻译提供方: {provider}")
        return None
    
    return {
        'provider': provider,
        'client': client,
        'model': model,
        'cache': {},
        'disabled': False
    }


def translate_summary_to_zh(summary: str, translator: Optional[dict]):
    """调用指定模型将英文摘要翻译成中文"""
    if not translator or translator.get('disabled'):
        return None
    if not summary:
        return ""
    summary = summary.strip()
    if not summary:
        return ""
    cache = translator['cache']
    if summary in cache:
        return cache[summary]
    
    prompt = (
        "请将以下英文新闻摘要翻译成自然、准确的简体中文，保留专有名词，不添加额外说明：\n\n"
        f"{summary}"
    )
    
    provider = translator.get('provider', 'openai')
    
    try:
        if provider == 'openai':
            response = translator['client'].chat.completions.create(
                model=translator['model'],
                messages=[
                    {"role": "system", "content": "You are a professional English-to-Chinese news translator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )
            translation = response.choices[0].message.content.strip()
        elif provider == 'anthropic':
            response = translator['client'].messages.create(
                model=translator['model'],
                system="You are a professional English-to-Chinese news translator.",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.2
            )
            translation_parts = []
            for block in response.content:
                text = getattr(block, "text", None)
                if text:
                    translation_parts.append(text.strip())
            translation = "\n".join(part for part in translation_parts if part)
        else:
            print(f"  ⚠️ 未知翻译提供方: {provider}，已停用翻译。")
            translator['disabled'] = True
            cache[summary] = None
            return None
        
        translation = translation.strip()
        cache[summary] = translation
        return translation
    except Exception as exc:  # pragma: no cover
        error_text = str(exc)
        quota_indicators = (
            'insufficient_quota',
            'exceeded your current quota',
            'rate limit',
            'RateLimit',
            '429'
        )
        auth_indicators = (
            'authentication_error',
            'invalid x-api-key',
            'Invalid API key',
            'invalid_api_key',
            'API key is missing',
            'PermissionDenied',
            'Could not resolve authentication method',
            'Unauthorized',
            'invalid authentication',
        )
        if any(indicator in error_text for indicator in quota_indicators):
            print("  ⚠️ 摘要翻译失败：额度或速率受限，已停用翻译。")
            translator['disabled'] = True
        elif any(indicator in error_text for indicator in auth_indicators):
            print("  ⚠️ 摘要翻译失败：API Key 验证失败，已停用翻译。")
            translator['disabled'] = True
        else:
            print(f"  ⚠️ 摘要翻译失败：{exc}")
        cache[summary] = None
        return None


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/118.0 Safari/537.36"
)
_LLM_CLIENT_CACHE = {}
_LLM_DISABLED = {}
_LLM_DISABLED_NOTIFIED = set()


def _fallback_extract_text(html: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style|noscript).*?>.*?</\1>", "", html)
    cleaned = re.sub(r"(?s)<[^>]+>", "\n", cleaned)
    lines = [line.strip() for line in cleaned.splitlines()]
    return "\n".join(line for line in lines if line)


def _extract_iso_date(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    text = raw.strip()
    if not text:
        return None

    match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if match:
        return match.group(1)

    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        dt = None
    if dt:
        return dt.date().isoformat()

    try:
        dt = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        dt = None
    if dt:
        return dt.date().isoformat()

    date_patterns = [
        "%Y/%m/%d",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%m/%d/%Y",
        "%d-%b-%Y",
    ]
    for pattern in date_patterns:
        try:
            dt = datetime.strptime(text, pattern)
            return dt.date().isoformat()
        except ValueError:
            continue

    return None


def _validate_iso_date(value: str) -> Optional[str]:
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.date().isoformat()
    except ValueError:
        return None


def fetch_article_text(url: str, user_agent: Optional[str] = None, timeout: int = 30) -> Optional[str]:
    """抓取网页正文并做基本清洗"""
    if not url:
        print("  ⚠️ 未提供 URL，无法抓取正文。")
        return None

    ua = user_agent or os.getenv("NEWS_FETCH_USER_AGENT") or DEFAULT_USER_AGENT
    request = urllib.request.Request(url, headers={"User-Agent": ua})

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            raw_bytes = response.read()
    except urllib.error.HTTPError as exc:
        print(f"  ⚠️ 抓取失败（HTTP {exc.code}）：{exc.reason}")
        return None
    except urllib.error.URLError as exc:
        print(f"  ⚠️ 抓取失败：{exc.reason}")
        return None
    except Exception as exc:  # pragma: no cover
        print(f"  ⚠️ 抓取失败：{exc}")
        return None

    raw_html = raw_bytes.decode(charset, errors="replace")

    try:
        from import_raw_story import extract_readable_text
    except ImportError:
        text = _fallback_extract_text(raw_html)
    else:
        try:
            text = extract_readable_text(raw_html)
        except Exception as exc:  # pragma: no cover
            print(f"  ⚠️ 解析正文失败：{exc}")
            text = _fallback_extract_text(raw_html)

    cleaned = (text or "").strip()
    if not cleaned:
        print("  ⚠️ 成功抓取页面，但未能解析正文。")
        return None
    return cleaned


def _get_llm_client(provider: str):
    provider = provider.lower()
    if provider in _LLM_DISABLED:
        return None
    if provider in _LLM_CLIENT_CACHE:
        return _LLM_CLIENT_CACHE[provider]

    client = None
    if provider == 'openai':
        if OpenAI is None:
            print("  ⚠️ 未安装 openai 库，无法生成要点。")
        else:
            try:
                client = OpenAI()
            except Exception as exc:  # pragma: no cover
                print(f"  ⚠️ 无法初始化 OpenAI 客户端：{exc}")
    elif provider == 'anthropic':
        if anthropic is None:
            print("  ⚠️ 未安装 anthropic 库，无法生成要点。")
        else:
            try:
                client = anthropic.Anthropic()
            except Exception as exc:  # pragma: no cover
                print(f"  ⚠️ 无法初始化 Anthropic 客户端：{exc}")
    elif provider == 'deepseek':
        api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_KEY")
        if not api_key:
            print("  ⚠️ 未设置 DEEPSEEK_API_KEY，无法生成要点。")
        elif requests is None:
            print("  ⚠️ 未安装 requests 库，无法调用 DeepSeek 模型。")
        else:
            client = {
                "api_key": api_key,
                "base_url": os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"),
            }
    else:
        print(f"  ⚠️ 未知生成模型提供方: {provider}")

    _LLM_CLIENT_CACHE[provider] = client
    return client


def _invoke_llm(provider: str, model: str, system_prompt: str, user_prompt: str,
                temperature: float = 0.2, max_tokens: int = 512) -> Optional[str]:
    provider = provider.lower()
    if provider in _LLM_DISABLED:
        return None

    client = _get_llm_client(provider)
    if client is None:
        return None

    try:
        if provider == 'openai':
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        elif provider == 'anthropic':
            response = client.messages.create(
                model=model,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            parts = []
            for block in response.content:
                text = getattr(block, "text", None)
                if text:
                    parts.append(text.strip())
            return "\n".join(part for part in parts if part).strip()
        elif provider == 'deepseek':
            if requests is None:
                raise RuntimeError("requests 库未安装。")
            if not isinstance(client, dict):
                raise RuntimeError("DeepSeek 客户端配置缺失。")
            api_key = client.get("api_key")
            base_url = client.get("base_url", "https://api.deepseek.com").rstrip("/")
            if not api_key:
                raise RuntimeError("缺少 DeepSeek API Key。")

            endpoint = f"{base_url}/v1/chat/completions"
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            try:
                resp = requests.post(endpoint, json=payload, headers=headers, timeout=45)
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(f"DeepSeek 请求失败：{exc}") from exc

            if resp.status_code >= 400:
                try:
                    error_body = resp.json()
                except ValueError:
                    error_body = resp.text[:200]
                raise RuntimeError(f"HTTP {resp.status_code}: {error_body}")

            try:
                data = resp.json()
            except ValueError as exc:  # pragma: no cover
                raise RuntimeError(f"DeepSeek 返回非 JSON：{resp.text[:200]}") from exc

            choices = data.get("choices") or []
            if not choices:
                raise RuntimeError("DeepSeek 返回中缺少 choices。")
            message = choices[0].get("message") or {}
            content = message.get("content", "").strip()
            if not content:
                raise RuntimeError("DeepSeek 返回内容为空。")
            return content
    except Exception as exc:  # pragma: no cover
        error_text = str(exc)
        print(f"  ⚠️ 生成要点失败：{error_text}")

        quota_indicators = (
            'insufficient_quota',
            'exceeded your current quota',
            'rate limit',
            'RateLimit',
            '429'
        )
        auth_indicators = (
            'authentication_error',
            'invalid x-api-key',
            'Invalid API key',
            'invalid_api_key',
            'API key is missing',
            'PermissionDenied',
            'Could not resolve authentication method',
            'Unauthorized',
            'invalid authentication',
        )
        disable_reason = None
        if any(indicator in error_text for indicator in quota_indicators):
            disable_reason = "额度或速率受限，请检查账号或切换模型。"
        elif any(indicator in error_text for indicator in auth_indicators):
            disable_reason = "API Key 验证失败，请更新密钥后再试。"

        if disable_reason:
            _LLM_DISABLED[provider] = disable_reason
            _LLM_DISABLED_NOTIFIED.discard(provider)
            _LLM_CLIENT_CACHE.pop(provider, None)
        else:
            if provider not in _LLM_DISABLED_NOTIFIED:
                print(f"  ⚠️ {provider} 模型已停用，请检查配置。")
                _LLM_DISABLED_NOTIFIED.add(provider)

        return None

    return None


def _fallback_summary(article_text: str, reason: Optional[str] = None) -> str:
    preview = re.split(r"(?<=[.!?。！？])\s+", article_text.strip())
    snippet = " ".join(preview[:3]).strip()
    if not snippet:
        snippet = article_text[:240].strip()
    if reason:
        header = f"⚠️ 自动提炼停用：{reason}"
    else:
        header = "⚠️ 自动提炼失败，请手动处理。"
    return (
        f"{header}\n\n"
        "英文原文摘录：\n"
        f"{snippet}"
    )


def extract_key_points(title: str, url: str, article_text: str,
                       provider: Optional[str] = None,
                       model: Optional[str] = None) -> str:
    """使用大模型生成中文要点摘要，失败时返回降级文案"""
    if not article_text:
        return "⚠️ 正文抓取失败，无法生成要点。"

    provider_choice = (provider or os.getenv("KEYPOINT_PROVIDER") or "openai").lower()
    env_model = os.getenv("KEYPOINT_MODEL")
    if model:
        model_choice = model
    elif env_model:
        model_choice = env_model
    else:
        default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-haiku-20240307",
            "deepseek": "deepseek-chat",
        }
        model_choice = default_models.get(provider_choice, "gpt-4o-mini")

    try:
        max_source_chars = int(os.getenv("KEYPOINT_MAX_SOURCE_CHARS", "6000"))
    except ValueError:
        max_source_chars = 6000

    try:
        max_tokens = int(os.getenv("KEYPOINT_MAX_TOKENS", "512"))
    except ValueError:
        max_tokens = 512

    truncated = article_text[:max_source_chars]
    if len(article_text) > max_source_chars:
        truncated += f"\n\n[原文截断：保留前 {max_source_chars} 字，共 {len(article_text)} 字]"

    system_prompt = "You are a bilingual international education analyst. Produce structured Chinese key points."
    user_prompt = (
        "请阅读以下英文新闻，并用专业的简体中文总结 3-5 条要点，每条 25 字以内。"
        "输出格式示例：\n"
        "1. ...\n2. ...\n3. ...\n"
        "需覆盖事件背景、受影响人群、措施/时间节点，以及给国际学生的建议。\n\n"
        f"新闻标题：{title}\n"
        f"原文链接：{url}\n\n"
        "英文原文：\n"
        f"{truncated}"
    )

    summary = _invoke_llm(provider_choice, model_choice, system_prompt, user_prompt, max_tokens=max_tokens)
    if summary:
        return summary.strip()

    reason = _LLM_DISABLED.get(provider_choice)
    return _fallback_summary(article_text, reason)


def load_skipped_urls():
    """加载已跳过的URL列表"""
    from path_utils import safe_path
    from error_utils import safe_json_read
    
    skipped_file = safe_path("ai_poadcast_main/.skipped_urls.json", Path.cwd())
    data = safe_json_read(skipped_file, default={})
    
    if isinstance(data, dict):
        return set(data.get('urls', []))
    return set()

def save_skipped_url(url: str):
    """保存跳过的URL"""
    from path_utils import safe_path
    from error_utils import safe_json_write
    
    skipped_file = safe_path("ai_poadcast_main/.skipped_urls.json", Path.cwd())
    skipped_urls = load_skipped_urls()
    skipped_urls.add(url)
    
    data = {
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'urls': sorted(list(skipped_urls))
    }
    
    safe_json_write(skipped_file, data)

def load_queue(queue_file="ai_poadcast_main/news_queue.json",
               summaries_file: Optional[str] = None):
    """加载队列"""
    from path_utils import safe_path
    from error_utils import safe_json_read
    
    queue_path = safe_path(queue_file, Path.cwd())
    
    print(f"[DEBUG] 尝试加载队列: {queue_file}")
    
    data = safe_json_read(queue_path, default={'items': []})
    if data is None or not isinstance(data, dict):
        print(f"❌ 队列文件加载失败: {queue_file}")
        print("💡 请先运行: python ai_poadcast_main/collect_rss_feeds.py")
        return {'items': []}

    items = data.get('items', [])
    print(f"[DEBUG] 加载成功，共 {len(items)} 条")
    
    # 过滤已跳过的URL
    skipped_urls = load_skipped_urls()
    if skipped_urls:
        before = len(items)
        items = [item for item in items if item.get('url') not in skipped_urls]
        filtered_count = before - len(items)
        if filtered_count > 0:
            print(f"[DEBUG] 已过滤 {filtered_count} 条之前跳过的新闻")
        data['items'] = items

    if summaries_file:
        from error_utils import safe_json_read
        summaries_path = safe_path(summaries_file, Path.cwd())
        print(f"[DEBUG] 尝试合并中文要点: {summaries_file}")
        
        summaries_data = safe_json_read(summaries_path)
        if summaries_data:
            summary_lookup = {}
            for entry in summaries_data.get("items", []):
                key = entry.get("url") or entry.get("title")
                if key:
                    summary_lookup[key] = entry
            merged = 0
            for item in items:
                key = item.get("url") or item.get("title")
                summary_entry = summary_lookup.get(key)
                if summary_entry:
                    if summary_entry.get("chinese_summary"):
                        item["chinese_summary"] = summary_entry["chinese_summary"]
                    if summary_entry.get("article_length") is not None:
                        item["article_length"] = summary_entry["article_length"]
                    merged += 1
            print(f"[DEBUG] 已合并中文要点 {merged} 条")
        else:
            print("[DEBUG] 中文要点文件加载失败或不存在。")
    
    return data

def filter_by_keywords(items, must_include=None, must_exclude=None):
    """按关键词过滤"""
    if must_include is None:
        must_include = [
            # 核心关键词 - 高权重
            'visa', 'immigration', 'policy', 'international student',
            'study abroad', 'admission', 'application', 'scholarship',
            'university ranking', 'college ranking', 'tuition',
            # 考试相关
            'ielts', 'toefl', 'gre', 'gmat', 'sat', 'act',
            # 学位相关
            'master', 'phd', 'graduate', 'undergraduate', 'mba',
            # 地区相关
            'uk visa', 'us visa', 'canada visa', 'australia visa',
            # 机构相关
            'university', 'college', 'education', 'academic'
        ]
    
    if must_exclude is None:
        must_exclude = [
            # 明确排除的内容
            'sport', 'football', 'basketball', 'celebrity', 'entertainment',
            'gossip', 'fashion', 'beauty', 'recipe', 'cooking', 'game', 'gaming',
            # 低质量内容
            'weather', 'traffic', 'local news', 'obituary', 'crime',
            # 非教育相关
            'real estate', 'property', 'investment', 'stock market',
            'cryptocurrency', 'bitcoin', 'trading'
        ]
    
    print(f"[DEBUG] 开始关键词过滤，输入 {len(items)} 条")

    source_exclude = {
        "UK GOV Education",
    }
    source_keyword_rules = {
        "UK GOV Education": [
            "international student",
            "overseas student",
            "international education",
            "visa",
            "immigration",
            "foreign student",
            "study abroad",
            "international recruitment",
        ],
    }
    
    filtered = []
    for item in items:
        title_lower = item['title'].lower()
        summary_lower = item.get('summary', '').lower()
        combined = title_lower + ' ' + summary_lower
        source_name = item.get('source', '')

        if source_name in source_exclude:
            allow_keywords = source_keyword_rules.get(source_name, [])
            allow = any(keyword in combined for keyword in allow_keywords)
            if not allow:
                print(f"[DEBUG] 排除: {item['title'][:50]} (来源过滤: {source_name})")
                continue
        
        # 检查排除词
        excluded = False
        for word in must_exclude:
            if word.lower() in combined:
                excluded = True
                print(f"[DEBUG] 排除: {item['title'][:50]} (匹配排除词: {word})")
                break
        
        if excluded:
            continue
        
        # 检查包含词（或者优先级>=9直接通过）
        if item.get('priority', 0) >= 9:
            print(f"[DEBUG] 保留（高优先级）: {item['title'][:50]}")
            filtered.append(item)
        elif any(word.lower() in combined for word in must_include):
            print(f"[DEBUG] 保留（关键词匹配）: {item['title'][:50]}")
            filtered.append(item)
        else:
            print(f"[DEBUG] 排除（无关键词）: {item['title'][:50]}")
    
    print(f"[DEBUG] 过滤完成，输出 {len(filtered)} 条")
    return filtered

def import_story(item, dry_run=False):
    """调用 import_raw_story.py 导入"""
    cmd = [
        'python', 'ai_poadcast_main/import_raw_story.py',
        '--title', item['title'],
        '--url', item['url'],
    ]

    source = item.get('source')
    if source:
        cmd.extend(['--source', source])

    published_date = item.get('published_date') or _extract_iso_date(item.get('published', ''))
    if published_date:
        cmd.extend(['--published-date', published_date])

    cmd.extend(['--fetch', '--store-html'])

    for tag in item.get('tags', []):
        cmd.extend(['--tags', tag])
    
    if dry_run:
        print("  [DRY RUN] " + ' '.join(cmd))
        return True
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("  ✅ 导入成功")
        return True
    except subprocess.CalledProcessError as e:
        if "URL already exists" in e.stderr or "该 URL 已经存档" in e.stderr:
            print("  ⚠️  已存在，跳过")
            return True  # 返回True避免中断流程
        else:
            print(f"  ❌ 导入失败: {e.stderr[:100]}")
            return False


def ensure_import_metadata(item: dict) -> bool:
    """确保导入前的必要字段齐全，必要时请求用户输入"""
    title = item.get('title', '').strip()
    url = item.get('url', '').strip()
    if not title:
        print("  ❌ 缺少标题，无法导入。")
        return False
    if not url:
        print("  ❌ 缺少 URL，无法导入。")
        return False

    source = (item.get('source') or "").strip()
    if not source:
        user_source = input("来源缺失，输入来源名称（回车使用 Unknown）: ").strip()
        item['source'] = user_source or "Unknown"
    else:
        item['source'] = source

    if not item.get('published_date'):
        inferred = _extract_iso_date(item.get('published', ''))
        if inferred:
            item['published_date'] = inferred
            print(f"  🗓️  使用原始发布日期: {inferred}")
        else:
            default_date = date.today().isoformat()
            while True:
                user_input = input(f"发布日期未知，请输入日期 (YYYY-MM-DD，回车使用 {default_date}): ").strip()
                candidate = user_input or default_date
                normalized = _validate_iso_date(candidate)
                if normalized:
                    item['published_date'] = normalized
                    break
                print("  ⚠️ 日期格式不正确，请重新输入。")

    tags = item.get('tags')
    if not tags:
        tag_input = input("未设置标签，可输入逗号分隔的标签（回车跳过）: ").strip()
        if tag_input:
            item['tags'] = [tag.strip() for tag in tag_input.split(',') if tag.strip()]

    return True

def interactive_review(items, max_import=10, translator=None):
    """交互式审核"""
    print("\n" + "="*70)
    print("📋 待处理新闻列表（按优先级排序）")
    print("="*70)
    
    imported_count = 0
    skipped_count = 0
    
    for i, item in enumerate(items, 1):
        if imported_count >= max_import:
            print(f"\n⚠️  已达到导入上限 ({max_import} 条)")
            break
        
        print("\n" + "="*70)
        print(f"[{i}/{len(items)}] 优先级: {item['priority']}")
        print(f"来源: {item['source']}")
        print(f"标题: {item['title']}")
        print(f"URL: {item['url']}")
        
        published_date = item.get('published_date') or _extract_iso_date(item.get('published', ''))
        if published_date:
            print(f"发布日期: {published_date}")
        else:
            print(f"发布日期: 未知")

        cn_summary = item.get('chinese_summary')
        if cn_summary:
            print("\n【中文要点】")
            print(cn_summary.strip())
        
        if item.get('summary'):
            summary_text = item['summary']
            display_text = summary_text[:150]
            print(f"摘要 (原文): {display_text}...")
            zh_translation = translate_summary_to_zh(summary_text, translator)
            if zh_translation:
                print(f"摘要 (中文): {zh_translation}")
        
        print("="*70)
        
        choice = input("\n操作: [y]导入 [n]跳过 [s]停止 [o]打开浏览器 [q]退出? ").lower()
        
        if choice == 'y':
            if ensure_import_metadata(item):
                if import_story(item):
                    imported_count += 1
                else:
                    skipped_count += 1
            else:
                skipped_count += 1
        elif choice == 'n':
            skipped_count += 1
            save_skipped_url(item['url'])
            print("  ⏭️  已跳过（已记录，下次不再显示）")
        elif choice == 's':
            print("\n🛑 停止审核")
            break
        elif choice == 'o':
            import webbrowser
            webbrowser.open(item['url'])
            choice2 = input("看完了吗？[y]导入 [n]跳过? ").lower()
            if choice2 == 'y':
                if import_story(item):
                    imported_count += 1
                else:
                    skipped_count += 1
            else:
                skipped_count += 1
                save_skipped_url(item['url'])
        elif choice == 'q':
            print("\n👋 退出")
            return
    
    print("\n" + "="*70)
    print("✅ 审核完成")
    print(f"  导入: {imported_count} 条")
    print(f"  跳过: {skipped_count} 条")
    print("="*70)

def auto_import_top(items, count=5):
    """自动导入优先级最高的N条"""
    print(f"\n🤖 自动导入模式：将导入前 {count} 条高优先级新闻\n")
    
    imported = 0
    for i, item in enumerate(items[:count], 1):
        title_short = item['title'][:60]
        print(f"[{i}/{count}] {title_short}...")
        if import_story(item):
            imported += 1
    
    print(f"\n✅ 成功导入 {imported}/{count} 条")

def show_summary(items):
    """显示队列摘要"""
    print("\n" + "="*70)
    print("📊 队列摘要")
    print("="*70)
    
    by_source = {}
    for item in items:
        source = item['source']
        by_source[source] = by_source.get(source, 0) + 1
    
    print("\n按来源分布：")
    for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count} 条")
    
    by_priority = {}
    for item in items:
        priority = item['priority']
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    print("\n按优先级分布：")
    for priority in sorted(by_priority.keys(), reverse=True):
        print(f"  优先级 {priority}: {by_priority[priority]} 条")

def main():
    """主流程"""
    import argparse
    
    parser = argparse.ArgumentParser(description='处理新闻队列')
    parser.add_argument('--auto', type=int, help='自动导入前N条')
    parser.add_argument('--queue-file', default='ai_poadcast_main/news_queue.json',
                        help='队列文件路径')
    parser.add_argument('--summaries-file', default='ai_poadcast_main/news_queue_with_summaries.json',
                        help='包含中文要点的文件，存在时自动合并')
    parser.add_argument('--no-summaries', action='store_true', help='忽略中文要点合并')
    parser.add_argument('--min-priority', type=int, default=7, help='最低优先级')
    parser.add_argument('--max-import', type=int, default=10, help='最多导入数量')
    parser.add_argument('--summary', action='store_true', help='只显示摘要，不处理')
    parser.add_argument('--no-filter', action='store_true', help='不过滤关键词')
    parser.add_argument('--debug', action='store_true', help='显示调试信息')
    parser.add_argument('--translate', action='store_true', help='将新闻摘要翻译成中文（需配置对应 API KEY）')
    parser.add_argument('--translate-provider', choices=['openai', 'anthropic'], default='openai',
                        help='摘要翻译模型提供方（默认：openai）')
    parser.add_argument('--translate-model', default='gpt-4o-mini', help='摘要翻译使用的模型名称')
    args = parser.parse_args()
    
    print("[DEBUG] 开始执行")
    
    translator = None
    if args.translate:
        translator = init_translator(args.translate_provider, args.translate_model)
        if not translator:
            print("⚠️ 未能启用摘要翻译功能，将继续显示英文摘要。")
    
    # 加载队列
    summaries_file = None if args.no_summaries else args.summaries_file
    queue = load_queue(args.queue_file, summaries_file)
    items = queue.get('items', [])
    
    print(f"[DEBUG] items数量: {len(items)}")
    
    if not items:
        print("\n⚠️  队列为空")
        print("💡 请运行: python ai_poadcast_main/collect_rss_feeds.py")
        return
    
    print(f"📥 队列中共有 {len(items)} 条新闻")
    
    # 优先级过滤
    original_count = len(items)
    items = [item for item in items if item.get('priority', 0) >= args.min_priority]
    print(f"🎯 过滤后剩余 {len(items)} 条（优先级 >= {args.min_priority}，过滤掉 {original_count - len(items)} 条）")
    
    # 关键词过滤
    if not args.no_filter:
        before_filter = len(items)
        items = filter_by_keywords(items)
        print(f"🔍 关键词过滤后剩余 {len(items)} 条（过滤掉 {before_filter - len(items)} 条）")
    
    if not items:
        print("\n⚠️  没有符合条件的新闻")
        print("💡 尝试降低优先级: --min-priority 6")
        print("💡 或跳过关键词过滤: --no-filter")
        return
    
    # 按优先级排序
    items.sort(key=lambda x: x.get('priority', 0), reverse=True)
    
    # 显示摘要
    if args.summary:
        show_summary(items)
        return
    
    # 处理
    if args.auto:
        auto_import_top(items, args.auto)
    else:
        interactive_review(items, args.max_import, translator)

if __name__ == "__main__":
    main()
