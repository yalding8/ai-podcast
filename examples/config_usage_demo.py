"""配置使用示例"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_poadcast.config import settings
from ai_poadcast.llm import create_llm_client
from ai_poadcast.generators.script import ScriptGenerator


def example_use_settings():
    """使用配置对象"""
    print("当前配置：")
    print(f"  LLM Provider: {settings.llm_provider}")
    print(f"  Max Tokens: {settings.max_tokens}")
    print(f"  Temperature: {settings.temperature}")
    print(f"  Max Retries: {settings.max_retries}")


def example_create_client_from_config():
    """从配置创建客户端"""
    # 自动使用settings中的配置
    llm = create_llm_client()
    generator = ScriptGenerator(llm)
    print(f"\n✅ 已创建生成器，使用 {settings.llm_provider}")


def example_override_config():
    """运行时覆盖配置"""
    # 覆盖provider
    llm = create_llm_client(provider="openai", model="gpt-3.5-turbo")
    print("\n✅ 已覆盖配置，使用 openai/gpt-3.5-turbo")


if __name__ == "__main__":
    print("配置管理示例")
    print("=" * 50)
    
    example_use_settings()
    
    # 取消注释测试（需要API key）
    # example_create_client_from_config()
    # example_override_config()
