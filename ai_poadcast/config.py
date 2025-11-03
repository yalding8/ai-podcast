"""配置管理"""

from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        BaseSettings = None


if BaseSettings:
    class Settings(BaseSettings):
        """应用配置（使用Pydantic）"""
        
        # LLM配置
        llm_provider: str = "deepseek"
        openai_api_key: Optional[str] = None
        openai_model: str = "gpt-4"
        anthropic_api_key: Optional[str] = None
        anthropic_model: str = "claude-3-5-sonnet-20241022"
        deepseek_api_key: Optional[str] = None
        deepseek_model: str = "deepseek-chat"
        deepseek_api_base: str = "https://api.deepseek.com"
        
        # 生成参数
        max_tokens: int = 1800
        temperature: float = 0.4
        max_retries: int = 3
        
        # TTS配置
        xunfei_app_id: Optional[str] = None
        xunfei_api_key: Optional[str] = None
        xunfei_api_secret: Optional[str] = None
        volcengine_app_id: Optional[str] = None
        volcengine_token: Optional[str] = None
        
        # 路径配置
        source_archive_dir: Path = Path("source_archive")
        stage3_output_dir: Path = Path("脚本输出")
        audio_exports_dir: Path = Path("audio_exports")
        
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = False
            extra = "ignore"
    
    settings = Settings()

else:
    # 降级方案：不使用Pydantic
    import os
    
    class SimpleSettings:
        """简单配置（无Pydantic）"""
        
        def __init__(self):
            self.llm_provider = os.getenv("LLM_PROVIDER", "deepseek")
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
            self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            self.deepseek_api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
            
            self.max_tokens = int(os.getenv("MAX_TOKENS", "1800"))
            self.temperature = float(os.getenv("TEMPERATURE", "0.4"))
            self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
            
            self.xunfei_app_id = os.getenv("XUNFEI_APP_ID")
            self.xunfei_api_key = os.getenv("XUNFEI_API_KEY")
            self.xunfei_api_secret = os.getenv("XUNFEI_API_SECRET")
            self.volcengine_app_id = os.getenv("VOLCENGINE_APP_ID")
            self.volcengine_token = os.getenv("VOLCENGINE_TOKEN")
            
            self.source_archive_dir = Path("source_archive")
            self.stage3_output_dir = Path("脚本输出")
            self.audio_exports_dir = Path("audio_exports")
    
    settings = SimpleSettings()
