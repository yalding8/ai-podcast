# gdelt_monitor.py
import logging
from typing import Dict, List, Sequence, Union

import requests

logger = logging.getLogger(__name__)


def _prepare_query(keywords: Union[str, Sequence[str]]) -> str:
    """标准化查询语句，确保包含布尔逻辑时带上括号。"""
    if isinstance(keywords, str):
        raw = keywords.strip()
        if not raw:
            return ""
        logical_tokens = (" OR ", " AND ", " NOT ", " NEAR ")
        needs_parentheses = any(token in raw.upper() for token in logical_tokens)
        # 保持已有括号，避免重复包装
        if needs_parentheses and not raw.startswith("(") and not raw.endswith(")"):
            return f"({raw})"
        return raw

    cleaned: List[str] = [item.strip() for item in keywords if item and item.strip()]
    if not cleaned:
        return ""

    def _maybe_quote(term: str) -> str:
        # 多词短语加引号，单词直接返回
        return f"\"{term}\"" if " " in term and not term.startswith('"') else term

    quoted = [_maybe_quote(term) for term in cleaned]
    if len(quoted) == 1:
        return quoted[0]
    return f"({' OR '.join(quoted)})"


def search_gdelt(
    keywords: Union[str, Sequence[str]],
    hours: int = 24,
) -> List[Dict[str, str]]:
    """
    搜索 GDELT 最近 hours 小时的新闻。

    Args:
        keywords: 字符串或字符串序列。若包含 OR/AND 等布尔逻辑，会自动补上括号；
                  传入列表时默认用 OR 连接，并对多词短语加引号。
        hours: 查询时间范围（小时）。

    Returns:
        List[Dict[str, str]]: 标准化后的新闻列表，失败时返回空列表。
    """
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    query = _prepare_query(keywords)
    if not query:
        logger.warning("GDELT 查询关键词为空，直接返回空列表。")
        return []

    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": 20,
        "format": "json",
        "timespan": f"{hours}h",
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("GDELT 请求失败：%s", exc)
        return []

    content_type = response.headers.get("Content-Type", "")
    if "json" not in content_type:
        logger.warning(
            "GDELT 返回的 Content-Type 非 JSON：%s，响应前200字符：%s",
            content_type,
            response.text[:200],
        )
        return []

    try:
        payload = response.json()
    except ValueError as exc:
        logger.warning(
            "GDELT 返回的内容不是合法 JSON：%s，响应前200字符：%s",
            exc,
            response.text[:200],
        )
        return []

    articles = payload.get("articles") or []
    normalized = []
    for article in articles:
        title = article.get("title")
        url_value = article.get("url")
        if not title or not url_value:
            continue
        normalized.append(
            {
                "title": title,
                "url": url_value,
                "source": article.get("domain", "GDELT"),
                "published": article.get("seendate", ""),
                "priority": 6,
            }
        )

    return normalized


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    breaking_news = search_gdelt(
        ["student visa ban", "university shutdown"],
        hours=24,
    )
    for item in breaking_news:
        logger.info("%s | %s", item["title"], item["url"])
