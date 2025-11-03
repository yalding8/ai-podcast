# 配置管理

## 问题：分散的配置

**旧代码：**
```python
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4")
max_tokens = int(os.getenv("MAX_TOKENS", "1800"))
```

**缺点：**
- 配置分散在各个文件
- 类型不安全
- 缺少默认值管理
- 难以验证

## 解决方案：统一配置

### 使用Pydantic Settings

```python
# ai_poadcast/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM配置
    llm_provider: str = "deepseek"
    openai_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    
    # 生成参数
    max_tokens: int = 1800
    temperature: float = 0.4
    max_retries: int = 3
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
```

## 使用方式

### 1. 访问配置

```python
from ai_poadcast.config import settings

print(settings.llm_provider)  # deepseek
print(settings.max_tokens)    # 1800
```

### 2. 在工厂函数中使用

```python
from ai_poadcast.config import settings

def create_llm_client(provider=None):
    provider = provider or settings.llm_provider
    model = settings.openai_model if provider == "openai" else settings.deepseek_model
    return Client(model=model)
```

### 3. 运行时覆盖

```python
# 使用默认配置
llm = create_llm_client()

# 覆盖配置
llm = create_llm_client(provider="openai", model="gpt-3.5-turbo")
```

## 环境变量

创建 `.env` 文件：

```bash
# LLM配置
LLM_PROVIDER=deepseek
OPENAI_API_KEY=sk-xxx
DEEPSEEK_API_KEY=sk-xxx

# 生成参数
MAX_TOKENS=1800
TEMPERATURE=0.4
MAX_RETRIES=3

# TTS配置
XUNFEI_APP_ID=xxx
XUNFEI_API_KEY=xxx
```

参考 `.env.example` 查看完整配置。

## 优势

1. **类型安全**：Pydantic自动验证类型
2. **集中管理**：所有配置在一个文件
3. **默认值**：清晰的默认值定义
4. **自动加载**：从.env文件自动读取
5. **IDE支持**：自动补全和类型提示

## 降级方案

如果未安装Pydantic，自动使用简单配置：

```python
class SimpleSettings:
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "deepseek")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "1800"))
```

## 示例

查看 `examples/config_usage_demo.py`

运行：
```bash
python examples/config_usage_demo.py
```
