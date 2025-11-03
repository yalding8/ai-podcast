# 依赖注入架构

## 问题：硬编码依赖

**旧代码：**
```python
from openai import OpenAI

def generate_script(prompt):
    client = OpenAI()  # 硬编码
    response = client.chat.completions.create(...)
    return response.choices[0].message.content
```

**缺点：**
- 无法切换LLM提供商
- 难以编写单元测试
- 配置不灵活

## 解决方案：依赖注入

### 1. 定义接口（Protocol）

```python
from typing import Protocol

class LLMClient(Protocol):
    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        ...
```

### 2. 实现具体客户端

```python
# ai_poadcast/llm/openai_client.py
class OpenAIClient:
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        response = self.client.chat.completions.create(...)
        return response.choices[0].message.content.strip()
```

### 3. 注入依赖

```python
# ai_poadcast/generators/script.py
class ScriptGenerator:
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client  # 依赖注入
    
    def generate(self, prompt: str, temperature: float = 0.4, max_tokens: int = 1800) -> str:
        return self.client.generate(prompt, temperature, max_tokens)
```

## 使用方式

### 方式1：工厂函数（推荐）

```python
from ai_poadcast.llm import create_llm_client
from ai_poadcast.generators.script import ScriptGenerator

# 自动根据环境变量选择provider
llm = create_llm_client()
generator = ScriptGenerator(llm)
script = generator.generate("生成播客脚本...")
```

### 方式2：直接注入

```python
from ai_poadcast.llm import DeepSeekClient
from ai_poadcast.generators.script import ScriptGenerator

llm = DeepSeekClient(model="deepseek-chat")
generator = ScriptGenerator(llm)
script = generator.generate("...")
```

### 方式3：测试时Mock

```python
class MockLLM:
    def generate(self, prompt, temperature, max_tokens):
        return "测试脚本"

generator = ScriptGenerator(MockLLM())
assert generator.generate("test") == "测试脚本"
```

## 环境变量配置

```bash
# .env
LLM_PROVIDER=deepseek          # openai/anthropic/deepseek
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

## 支持的LLM提供商

| Provider | 客户端类 | 默认模型 |
|----------|---------|---------|
| OpenAI | `OpenAIClient` | gpt-4 |
| Anthropic | `AnthropicClient` | claude-3-5-sonnet-20241022 |
| DeepSeek | `DeepSeekClient` | deepseek-chat |

## 优势

1. **可测试性**：轻松注入Mock对象
2. **灵活性**：运行时切换LLM提供商
3. **解耦**：业务逻辑与具体实现分离
4. **可扩展**：新增LLM只需实现接口

## 示例代码

查看 `examples/dependency_injection_demo.py`

运行测试：
```bash
export PYTHONPATH="$PWD"
python examples/dependency_injection_demo.py
```
