"""要点提取器"""

from typing import Optional, Protocol
import logging

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """LLM客户端接口"""
    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        ...


class SummaryExtractor:
    """新闻要点提取器"""

    DEFAULT_MAX_SOURCE_CHARS = 6000
    DEFAULT_MAX_TOKENS = 512
    DEFAULT_TEMPERATURE = 0.4

    def __init__(
        self,
        llm_client: LLMClient,
        max_source_chars: int = DEFAULT_MAX_SOURCE_CHARS,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE
    ):
        """
        初始化要点提取器

        Args:
            llm_client: LLM客户端实例
            max_source_chars: 原文最大字符数
            max_tokens: 生成最大token数
            temperature: 生成温度
        """
        self.llm_client = llm_client
        self.max_source_chars = max_source_chars
        self.max_tokens = max_tokens
        self.temperature = temperature

    def extract(self, title: str, url: str, article_text: str) -> dict:
        """
        提取新闻要点（Stage 2）

        Args:
            title: 新闻标题
            url: 新闻URL
            article_text: 新闻正文

        Returns:
            包含摘要和元数据的字典
        """
        if not article_text:
            logger.warning(f"文章正文为空: {url}")
            return {
                'summary': '⚠️ 正文抓取失败，无法生成要点。',
                'status': 'failed',
                'error': 'empty_content',
                'article_length': 0
            }

        try:
            # 截断过长的文本
            truncated_text = self._truncate_text(article_text)

            # 构建提示词
            prompt = self._build_prompt(title, url, truncated_text)

            # 调用LLM生成摘要
            summary = self.llm_client.generate(
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            if not summary:
                raise ValueError("LLM返回空摘要")

            return {
                'summary': summary.strip(),
                'status': 'success',
                'article_length': len(article_text),
                'truncated': len(article_text) > self.max_source_chars
            }

        except Exception as e:
            logger.error(f"提取要点失败 {url}: {e}")
            return {
                'summary': f'⚠️ 要点提取失败: {str(e)}',
                'status': 'error',
                'error': str(e),
                'article_length': len(article_text)
            }

    def _truncate_text(self, text: str) -> str:
        """
        截断过长的文本

        Args:
            text: 原文

        Returns:
            截断后的文本
        """
        if len(text) <= self.max_source_chars:
            return text

        truncated = text[:self.max_source_chars]
        truncated += (
            f"\n\n[原文截断：保留前 {self.max_source_chars} 字，"
            f"共 {len(text)} 字]"
        )
        return truncated

    def _build_prompt(self, title: str, url: str, article_text: str) -> str:
        """
        构建提示词

        Args:
            title: 新闻标题
            url: 新闻URL
            article_text: 新闻正文

        Returns:
            提示词
        """
        return f"""You are a bilingual international education analyst. Produce structured Chinese key points.

请阅读以下英文新闻，并用专业的简体中文总结 3-5 条要点，每条 25 字以内。

输出格式示例：
1. ...
2. ...
3. ...

需覆盖事件背景、受影响人群、措施/时间节点，以及给国际学生的建议。

新闻标题：{title}
原文链接：{url}

英文原文：
{article_text}
"""

    def extract_batch(
        self,
        articles: list[dict],
        progress_callback: Optional[callable] = None
    ) -> list[dict]:
        """
        批量提取要点

        Args:
            articles: 文章列表，每个包含 title, url, text
            progress_callback: 进度回调函数(current, total, article)

        Returns:
            包含摘要的文章列表
        """
        results = []
        total = len(articles)

        for i, article in enumerate(articles, 1):
            if progress_callback:
                progress_callback(i, total, article)

            result = self.extract(
                title=article.get('title', ''),
                url=article.get('url', ''),
                article_text=article.get('text', '')
            )

            # 合并原始数据和提取结果
            results.append({
                **article,
                'chinese_summary': result['summary'],
                'extraction_status': result['status'],
                'article_length': result.get('article_length', 0)
            })

        return results
