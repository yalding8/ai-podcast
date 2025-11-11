"""DeepSeek客户端"""

import os
import requests


class DeepSeekClient:
    """DeepSeek LLM客户端"""
    
    def __init__(self, api_key: str = None, model: str = "deepseek-chat", base_url: str = None):
        if not api_key:
            raise ValueError(
                "DeepSeek API key is required but not provided. "
                "Please set DEEPSEEK_API_KEY in your .env file or environment variables. "
                "You can get an API key from https://platform.deepseek.com/"
            )

        self.api_key = api_key
        self.model = model
        self.base_url = (base_url or os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")).rstrip("/")
    
    def generate(self, prompt: str, temperature: float = 0.4, max_tokens: int = 1800) -> str:
        """生成文本"""
        endpoint = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a professional podcast script writer."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
