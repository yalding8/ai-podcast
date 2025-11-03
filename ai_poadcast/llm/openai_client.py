"""OpenAI客户端"""


class OpenAIClient:
    """OpenAI LLM客户端"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, temperature: float = 0.4, max_tokens: int = 1800) -> str:
        """生成文本"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional podcast script writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
