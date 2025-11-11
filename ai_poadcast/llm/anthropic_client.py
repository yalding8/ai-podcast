"""Anthropic客户端"""


class AnthropicClient:
    """Anthropic Claude客户端"""

    def __init__(self, api_key: str = None, model: str = "claude-3-5-sonnet-20241022"):
        if not api_key:
            raise ValueError(
                "Anthropic API key is required but not provided. "
                "Please set ANTHROPIC_API_KEY in your .env file or environment variables. "
                "You can get an API key from https://console.anthropic.com/"
            )

        import anthropic
        # Explicitly pass api_key to prevent SDK from auto-discovering credentials
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, temperature: float = 0.4, max_tokens: int = 1800) -> str:
        """生成文本"""
        response = self.client.messages.create(
            model=self.model,
            system="You are a professional podcast script writer.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return "\n".join(block.text for block in response.content if hasattr(block, "text")).strip()
