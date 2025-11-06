"""LLM客户端测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_poadcast.llm.factory import create_llm_client
from ai_poadcast.llm.openai_client import OpenAIClient
from ai_poadcast.llm.deepseek_client import DeepSeekClient


class TestLLMFactory:
    """测试LLM工厂函数"""

    def test_create_openai_client(self):
        """测试创建OpenAI客户端"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            client = create_llm_client(provider='openai', api_key='test-key')
            assert isinstance(client, OpenAIClient)
            assert client.model == 'gpt-4'

    def test_create_deepseek_client(self):
        """测试创建DeepSeek客户端"""
        client = create_llm_client(provider='deepseek', api_key='test-key')
        assert isinstance(client, DeepSeekClient)
        assert client.model == 'deepseek-chat'

    def test_invalid_provider_raises_error(self):
        """测试无效provider抛出异常"""
        with pytest.raises(ValueError, match="不支持的provider"):
            create_llm_client(provider='invalid-provider')

    def test_custom_model_parameter(self):
        """测试自定义模型参数"""
        client = create_llm_client(
            provider='deepseek',
            api_key='test-key',
            model='custom-model'
        )
        assert client.model == 'custom-model'


class TestOpenAIClient:
    """测试OpenAI客户端"""

    @patch('ai_poadcast.llm.openai_client.OpenAI')
    def test_client_initialization(self, mock_openai):
        """测试客户端初始化"""
        client = OpenAIClient(api_key='test-key', model='gpt-4')
        assert client.model == 'gpt-4'
        mock_openai.assert_called_once_with(api_key='test-key')

    @patch('ai_poadcast.llm.openai_client.OpenAI')
    def test_generate_success(self, mock_openai):
        """测试成功生成文本"""
        # Mock响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated text"
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = OpenAIClient(api_key='test-key')
        result = client.generate("Test prompt", temperature=0.5, max_tokens=100)

        assert result == "Generated text"
        mock_openai.return_value.chat.completions.create.assert_called_once()

    @patch('ai_poadcast.llm.openai_client.OpenAI')
    def test_generate_with_custom_parameters(self, mock_openai):
        """测试使用自定义参数生成"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Response"
        mock_openai.return_value.chat.completions.create.return_value = mock_response

        client = OpenAIClient(api_key='test-key')
        client.generate("Prompt", temperature=0.8, max_tokens=2000)

        call_args = mock_openai.return_value.chat.completions.create.call_args
        assert call_args[1]['temperature'] == 0.8
        assert call_args[1]['max_tokens'] == 2000


class TestDeepSeekClient:
    """测试DeepSeek客户端"""

    def test_initialization_with_api_key(self):
        """测试使用API key初始化"""
        client = DeepSeekClient(api_key='test-key')
        assert client.api_key == 'test-key'
        assert client.model == 'deepseek-chat'

    def test_initialization_without_api_key_raises_error(self):
        """测试缺少API key抛出异常"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="需要DEEPSEEK_API_KEY"):
                DeepSeekClient()

    @patch('ai_poadcast.llm.deepseek_client.requests.post')
    def test_generate_success(self, mock_post):
        """测试成功生成文本"""
        # Mock HTTP响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'DeepSeek response'}}]
        }
        mock_post.return_value = mock_response

        client = DeepSeekClient(api_key='test-key')
        result = client.generate("Test prompt")

        assert result == "DeepSeek response"
        mock_post.assert_called_once()

    @patch('ai_poadcast.llm.deepseek_client.requests.post')
    def test_generate_with_custom_base_url(self, mock_post):
        """测试使用自定义base URL"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Response'}}]
        }
        mock_post.return_value = mock_response

        client = DeepSeekClient(
            api_key='test-key',
            base_url='https://custom.api.com'
        )
        client.generate("Prompt")

        call_url = mock_post.call_args[0][0]
        assert call_url.startswith('https://custom.api.com')

    @patch('ai_poadcast.llm.deepseek_client.requests.post')
    def test_generate_handles_http_error(self, mock_post):
        """测试处理HTTP错误"""
        mock_post.return_value.raise_for_status.side_effect = Exception("HTTP Error")

        client = DeepSeekClient(api_key='test-key')
        with pytest.raises(Exception, match="HTTP Error"):
            client.generate("Prompt")


class TestLLMIntegration:
    """集成测试：测试不同LLM客户端的一致性"""

    @patch('ai_poadcast.llm.openai_client.OpenAI')
    @patch('ai_poadcast.llm.deepseek_client.requests.post')
    def test_all_clients_implement_generate_interface(
        self, mock_post, mock_openai
    ):
        """测试所有客户端实现相同的generate接口"""
        # Mock responses
        mock_openai_resp = MagicMock()
        mock_openai_resp.choices[0].message.content = "OpenAI"
        mock_openai.return_value.chat.completions.create.return_value = mock_openai_resp

        mock_deepseek_resp = Mock()
        mock_deepseek_resp.json.return_value = {
            'choices': [{'message': {'content': 'DeepSeek'}}]
        }
        mock_post.return_value = mock_deepseek_resp

        # 测试所有客户端
        clients = [
            OpenAIClient(api_key='test'),
            DeepSeekClient(api_key='test'),
        ]

        for client in clients:
            result = client.generate("Test", temperature=0.4, max_tokens=100)
            assert isinstance(result, str)
            assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
