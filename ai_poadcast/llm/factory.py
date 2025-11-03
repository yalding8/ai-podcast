"""LLM客户端工厂"""

from typing import Optional

from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .deepseek_client import DeepSeekClient
from ..config import settings


def create_llm_client(provider: Optional[str] = None, model: Optional[str] = None, **kwargs):
    """创建LLM客户端（工厂模式）"""
    provider = (provider or settings.llm_provider).lower()
    
    if provider == "openai":
        model = model or settings.openai_model
        api_key = kwargs.pop("api_key", settings.openai_api_key)
        return OpenAIClient(api_key=api_key, model=model, **kwargs)
    
    elif provider == "anthropic":
        model = model or settings.anthropic_model
        api_key = kwargs.pop("api_key", settings.anthropic_api_key)
        return AnthropicClient(api_key=api_key, model=model, **kwargs)
    
    elif provider == "deepseek":
        model = model or settings.deepseek_model
        api_key = kwargs.pop("api_key", settings.deepseek_api_key)
        base_url = kwargs.pop("base_url", settings.deepseek_api_base)
        return DeepSeekClient(api_key=api_key, model=model, base_url=base_url, **kwargs)
    
    else:
        raise ValueError(f"不支持的provider: {provider}")
