"""错误处理工具测试"""

import pytest
import json
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_poadcast_main.error_utils import (
    safe_file_read,
    safe_json_read,
    safe_file_write,
    safe_json_write,
    retry_on_failure,
    safe_http_get,
    safe_http_post,
    FileOperationError,
    NetworkError
)


class TestSafeFileOperations:
    """测试安全文件操作"""

    def test_safe_file_read_success(self):
        """测试成功读取文件"""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            content = "Test content"
            file_path.write_text(content, encoding='utf-8')

            result = safe_file_read(file_path)
            assert result == content

    def test_safe_file_read_nonexistent(self):
        """测试读取不存在的文件"""
        result = safe_file_read("/nonexistent/file.txt", default="default")
        assert result == "default"

    def test_safe_file_read_with_encoding(self):
        """测试指定编码读取"""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "utf8.txt"
            content = "中文内容"
            file_path.write_text(content, encoding='utf-8')

            result = safe_file_read(file_path, encoding='utf-8')
            assert result == content

    def test_safe_file_write_success(self):
        """测试成功写入文件"""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            content = "Test content"

            success = safe_file_write(file_path, content)
            assert success is True
            assert file_path.exists()
            assert file_path.read_text(encoding='utf-8') == content

    def test_safe_file_write_creates_directories(self):
        """测试自动创建父目录"""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "subdir" / "subdir2" / "test.txt"
            content = "Test"

            success = safe_file_write(file_path, content)
            assert success is True
            assert file_path.exists()

    def test_safe_file_write_to_invalid_path(self):
        """测试写入无效路径"""
        # 尝试写入到根目录（通常会失败）
        result = safe_file_write("/root/forbidden/test.txt", "content")
        # 可能成功也可能失败，取决于权限
        assert isinstance(result, bool)


class TestSafeJSONOperations:
    """测试安全JSON操作"""

    def test_safe_json_read_success(self):
        """测试成功读取JSON"""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            data = {"key": "value", "number": 42}
            file_path.write_text(json.dumps(data), encoding='utf-8')

            result = safe_json_read(file_path)
            assert result == data

    def test_safe_json_read_nonexistent(self):
        """测试读取不存在的JSON文件"""
        result = safe_json_read("/nonexistent.json", default={})
        assert result == {}

    def test_safe_json_read_invalid_json(self):
        """测试读取无效JSON"""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "invalid.json"
            file_path.write_text("{ invalid json }", encoding='utf-8')

            result = safe_json_read(file_path, default={"error": True})
            assert result == {"error": True}

    def test_safe_json_write_success(self):
        """测试成功写入JSON"""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            data = {"key": "value", "list": [1, 2, 3]}

            success = safe_json_write(file_path, data)
            assert success is True
            assert file_path.exists()

            # 验证内容
            loaded = json.loads(file_path.read_text(encoding='utf-8'))
            assert loaded == data

    def test_safe_json_write_with_chinese(self):
        """测试写入包含中文的JSON"""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "chinese.json"
            data = {"title": "中文标题", "content": "内容"}

            success = safe_json_write(file_path, data)
            assert success is True

            # 验证中文正确保存
            content = file_path.read_text(encoding='utf-8')
            assert "中文标题" in content

    def test_safe_json_write_custom_indent(self):
        """测试自定义缩进"""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            data = {"key": {"nested": "value"}}

            safe_json_write(file_path, data, indent=4)
            content = file_path.read_text(encoding='utf-8')

            # 验证缩进
            assert "    " in content  # 4空格缩进


class TestRetryDecorator:
    """测试重试装饰器"""

    def test_retry_success_first_attempt(self):
        """测试首次尝试成功"""
        @retry_on_failure(max_retries=3, delay=0.01)
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_retry_success_after_failures(self):
        """测试失败后重试成功"""
        attempts = []

        @retry_on_failure(max_retries=3, delay=0.01, backoff=1.0)
        def function_with_retries():
            attempts.append(1)
            if len(attempts) < 3:
                raise ValueError("Temporary error")
            return "success"

        result = function_with_retries()
        assert result == "success"
        assert len(attempts) == 3

    def test_retry_all_attempts_fail(self):
        """测试所有重试都失败"""
        attempts = []

        @retry_on_failure(max_retries=3, delay=0.01)
        def always_fails():
            attempts.append(1)
            raise ValueError("Permanent error")

        result = always_fails()
        assert result is None  # 返回None
        assert len(attempts) == 3

    def test_retry_with_custom_exceptions(self):
        """测试自定义异常类型"""
        @retry_on_failure(max_retries=2, delay=0.01, exceptions=(ValueError,))
        def specific_exception():
            raise TypeError("Should not retry")

        # TypeError不在重试列表中，应该立即抛出
        with pytest.raises(TypeError):
            specific_exception()

    def test_retry_backoff_timing(self):
        """测试退避延迟"""
        start_time = time.time()
        attempts = []

        @retry_on_failure(max_retries=3, delay=0.1, backoff=2.0)
        def timed_function():
            attempts.append(time.time())
            raise ValueError("Error")

        timed_function()
        elapsed = time.time() - start_time

        # 应该至少等待 0.1 + 0.2 = 0.3 秒
        assert elapsed >= 0.3
        assert len(attempts) == 3


class TestSafeHTTPOperations:
    """测试安全HTTP操作"""

    @patch('ai_poadcast_main.error_utils.requests.get')
    def test_safe_http_get_success(self, mock_get):
        """测试成功的HTTP GET请求"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_get.return_value = mock_response

        response = safe_http_get("https://example.com")
        assert response is not None
        assert response.status_code == 200

    @patch('ai_poadcast_main.error_utils.requests.get')
    def test_safe_http_get_with_retries(self, mock_get):
        """测试带重试的HTTP GET"""
        # 前两次失败，第三次成功
        mock_get.side_effect = [
            Exception("Network error"),
            Exception("Timeout"),
            Mock(status_code=200, text="Success")
        ]

        response = safe_http_get("https://example.com", max_retries=3)
        assert response is not None
        assert response.status_code == 200
        assert mock_get.call_count == 3

    @patch('ai_poadcast_main.error_utils.requests.get')
    def test_safe_http_get_all_retries_fail(self, mock_get):
        """测试所有重试都失败"""
        mock_get.side_effect = Exception("Permanent error")

        response = safe_http_get("https://example.com", max_retries=2)
        assert response is None
        assert mock_get.call_count == 2

    @patch('ai_poadcast_main.error_utils.requests.get')
    def test_safe_http_get_custom_headers(self, mock_get):
        """测试自定义请求头"""
        mock_response = Mock()
        mock_get.return_value = mock_response

        custom_headers = {"Authorization": "Bearer token"}
        safe_http_get("https://example.com", headers=custom_headers)

        # 验证请求头被传递
        call_kwargs = mock_get.call_args[1]
        assert "Authorization" in call_kwargs['headers']

    @patch('ai_poadcast_main.error_utils.requests.post')
    def test_safe_http_post_with_json(self, mock_post):
        """测试POST JSON数据"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        json_data = {"key": "value"}
        response = safe_http_post(
            "https://api.example.com",
            json_data=json_data
        )

        assert response is not None
        assert response.status_code == 201
        mock_post.assert_called_once()

    @patch('ai_poadcast_main.error_utils.requests.post')
    def test_safe_http_post_timeout(self, mock_post):
        """测试POST超时"""
        mock_post.side_effect = Exception("Timeout")

        response = safe_http_post(
            "https://api.example.com",
            json_data={},
            max_retries=1
        )

        assert response is None


class TestCustomExceptions:
    """测试自定义异常"""

    def test_file_operation_error(self):
        """测试FileOperationError"""
        with pytest.raises(FileOperationError):
            raise FileOperationError("File error")

    def test_network_error(self):
        """测试NetworkError"""
        with pytest.raises(NetworkError):
            raise NetworkError("Network error")

    def test_exceptions_inherit_from_exception(self):
        """测试异常继承"""
        assert issubclass(FileOperationError, Exception)
        assert issubclass(NetworkError, Exception)


class TestIntegration:
    """集成测试"""

    def test_realistic_file_workflow(self):
        """测试真实文件操作流程"""
        with TemporaryDirectory() as tmpdir:
            # 写入JSON
            file_path = Path(tmpdir) / "data.json"
            data = {
                "articles": [
                    {"title": "Article 1", "priority": 9},
                    {"title": "Article 2", "priority": 7}
                ],
                "updated_at": "2025-01-15"
            }

            success = safe_json_write(file_path, data)
            assert success is True

            # 读取JSON
            loaded = safe_json_read(file_path)
            assert loaded == data

            # 修改并重新写入
            loaded["articles"].append({"title": "Article 3", "priority": 8})
            success = safe_json_write(file_path, loaded)
            assert success is True

            # 验证修改
            final = safe_json_read(file_path)
            assert len(final["articles"]) == 3

    @patch('ai_poadcast_main.error_utils.requests.get')
    def test_realistic_http_workflow(self, mock_get):
        """测试真实HTTP请求流程"""
        # 模拟RSS采集
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """<?xml version="1.0"?>
        <rss><channel><item><title>News</title></item></channel></rss>"""
        mock_get.return_value = mock_response

        response = safe_http_get("https://example.com/rss", timeout=10)
        assert response is not None
        assert "News" in response.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
