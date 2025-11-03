"""脚本生成器"""

from typing import Protocol


class LLMClient(Protocol):
    """LLM客户端接口"""
    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        ...


class ScriptGenerator:
    """播客脚本生成器（依赖注入）"""
    
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client
    
    def generate(self, prompt: str, temperature: float = 0.4, max_tokens: int = 1800) -> str:
        """生成播客脚本"""
        return self.client.generate(prompt, temperature, max_tokens)
