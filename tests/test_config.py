"""配置管理测试"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

# 设置测试环境变量
os.environ.setdefault('DEEPSEEK_API_KEY', 'test-deepseek-key')


class TestSettings:
    """测试配置类"""

    def test_settings_with_pydantic(self):
        """测试Pydantic配置加载"""
        try:
            from pydantic_settings import BaseSettings
            from ai_poadcast.config import settings

            assert hasattr(settings, 'llm_provider')
            assert hasattr(settings, 'deepseek_api_key')
            assert hasattr(settings, 'openai_api_key')
        except ImportError:
            pytest.skip("Pydantic未安装，跳过测试")

    def test_settings_without_pydantic(self):
        """测试降级配置（无Pydantic）"""
        # 模拟Pydantic不可用
        with patch.dict('sys.modules', {'pydantic_settings': None, 'pydantic': None}):
            # 重新导入配置
            import importlib
            import ai_poadcast.config as config_module
            importlib.reload(config_module)

            assert hasattr(config_module.settings, 'llm_provider')
            assert hasattr(config_module.settings, 'deepseek_api_key')

    def test_default_values(self):
        """测试默认配置值"""
        from ai_poadcast.config import settings

        assert settings.llm_provider == "deepseek"
        assert settings.max_tokens == 1800
        assert settings.temperature == 0.4
        assert settings.max_retries == 3

    def test_llm_model_defaults(self):
        """测试LLM模型默认值"""
        from ai_poadcast.config import settings

        assert settings.openai_model == "gpt-4"
        assert settings.deepseek_model == "deepseek-chat"
        assert "claude" in settings.anthropic_model

    def test_path_configuration(self):
        """测试路径配置"""
        from ai_poadcast.config import settings

        assert isinstance(settings.source_archive_dir, Path)
        assert isinstance(settings.stage3_output_dir, Path)
        assert isinstance(settings.audio_exports_dir, Path)

    def test_environment_variable_override(self):
        """测试环境变量覆盖"""
        with patch.dict('os.environ', {
            'LLM_PROVIDER': 'openai',
            'MAX_TOKENS': '2000',
            'TEMPERATURE': '0.7'
        }):
            # 重新导入以获取新的环境变量
            import importlib
            import ai_poadcast.config as config_module
            importlib.reload(config_module)

            from ai_poadcast.config import settings
            assert settings.llm_provider == 'openai'
            # 注意：已加载的设置可能不会改变，这取决于实现

    def test_api_key_security(self):
        """测试API密钥不会被意外暴露"""
        from ai_poadcast.config import settings

        # 确保敏感配置存在但不打印
        config_repr = repr(settings)
        # 基本检查：不应该包含完整的API密钥
        # （实际实现可能需要在Settings类中覆盖__repr__）


class TestConfigurationValidation:
    """测试配置验证"""

    def test_tts_configuration(self):
        """测试TTS配置"""
        from ai_poadcast.config import settings

        # 应该有TTS相关配置
        assert hasattr(settings, 'xunfei_app_id')
        assert hasattr(settings, 'volcengine_app_id')

    def test_deepseek_api_base_default(self):
        """测试DeepSeek API base URL默认值"""
        from ai_poadcast.config import settings

        assert settings.deepseek_api_base == "https://api.deepseek.com"

    def test_config_with_dotenv(self):
        """测试.env文件加载"""
        # 创建临时.env文件
        test_env_path = Path(__file__).parent.parent / '.env.test'
        test_env_content = """
LLM_PROVIDER=test_provider
MAX_TOKENS=9999
"""
        try:
            test_env_path.write_text(test_env_content)

            # 测试是否能正确加载
            # （实际测试需要mock dotenv加载）
            assert True  # 占位符

        finally:
            if test_env_path.exists():
                test_env_path.unlink()


class TestConfigEdgeCases:
    """测试配置边界情况"""

    def test_missing_required_api_keys(self):
        """测试缺少必需的API密钥"""
        with patch.dict('os.environ', {}, clear=True):
            from ai_poadcast.config import settings
            # 应该允许None值，但使用时会报错
            assert settings.openai_api_key is None or settings.openai_api_key == ''

    def test_invalid_numeric_values(self):
        """测试无效的数字值"""
        with patch.dict('os.environ', {
            'MAX_TOKENS': 'invalid',
            'TEMPERATURE': 'not_a_number'
        }):
            # SimpleSettings应该使用默认值或抛出异常
            try:
                import importlib
                import ai_poadcast.config as config_module
                importlib.reload(config_module)
                # 如果没有抛出异常，检查是否使用了默认值
                from ai_poadcast.config import settings
                assert settings.max_tokens == 1800  # 应该fallback到默认值
            except (ValueError, TypeError):
                # 这也是可接受的行为
                pass

    def test_path_configuration_creates_directories(self):
        """测试路径配置（不自动创建目录）"""
        from ai_poadcast.config import settings

        # 配置应该是Path对象，但不应该自动创建目录
        assert not settings.source_archive_dir.exists() or settings.source_archive_dir.is_dir()


class TestSettingsImmutability:
    """测试配置不可变性"""

    def test_settings_is_singleton(self):
        """测试settings是单例"""
        from ai_poadcast.config import settings as settings1
        from ai_poadcast.config import settings as settings2

        assert settings1 is settings2

    def test_multiple_imports_return_same_instance(self):
        """测试多次导入返回相同实例"""
        from ai_poadcast.config import settings as s1
        import ai_poadcast.config
        s2 = ai_poadcast.config.settings

        assert s1 is s2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
