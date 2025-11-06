# 测试指南

## 概述

本项目使用 pytest 作为测试框架，目标测试覆盖率为 **70%**。

## 快速开始

### 运行所有测试

```bash
make test
```

### 运行测试并生成覆盖率报告

```bash
make test-cov
```

覆盖率报告将生成在 `htmlcov/` 目录，打开 `htmlcov/index.html` 查看详细报告。

### 快速测试（不生成覆盖率）

```bash
make test-fast
```

## 测试结构

```
tests/
├── test_core_functions.py      # 核心函数测试
├── test_dependency_injection.py # 依赖注入测试
├── test_llm_clients.py          # LLM客户端测试
├── test_config.py               # 配置管理测试
├── test_archive_manager.py     # 档案管理器测试
└── test_error_utils.py         # 错误处理工具测试
```

## 测试覆盖率目标

| 模块                | 目标覆盖率 | 当前状态 |
|---------------------|-----------|---------|
| ai_poadcast/        | 70%+      | 🟡 开发中 |
| ai_poadcast_main/   | 50%+      | 🔴 待改进 |
| 整体                | 70%+      | 🟡 进行中 |

## 运行特定测试

### 运行单个测试文件

```bash
pytest tests/test_llm_clients.py -v
```

### 运行特定测试类

```bash
pytest tests/test_llm_clients.py::TestLLMFactory -v
```

### 运行特定测试方法

```bash
pytest tests/test_llm_clients.py::TestLLMFactory::test_create_openai_client -v
```

### 运行匹配特定模式的测试

```bash
pytest -k "llm" -v  # 运行所有包含"llm"的测试
```

## 编写测试

### 测试命名规范

- 测试文件: `test_*.py`
- 测试类: `Test*`
- 测试方法: `test_*`

### 示例测试

```python
"""模块测试"""

import pytest
from ai_poadcast.module import function_to_test


class TestModuleName:
    """测试模块功能"""

    def test_basic_functionality(self):
        """测试基本功能"""
        result = function_to_test("input")
        assert result == "expected"

    def test_error_handling(self):
        """测试错误处理"""
        with pytest.raises(ValueError):
            function_to_test(None)
```

### Mock 和 Patch

使用 `unittest.mock` 进行依赖隔离：

```python
from unittest.mock import Mock, patch

@patch('module.external_dependency')
def test_with_mock(mock_dependency):
    """使用mock的测试"""
    mock_dependency.return_value = "mocked"
    # 测试代码
```

## 测试覆盖率配置

配置文件：`.coveragerc`

```ini
[run]
source = ai_poadcast, ai_poadcast_main
omit = */tests/*, */vendor/*

[report]
precision = 2
show_missing = True

[html]
directory = htmlcov
```

## 持续集成

### GitHub Actions（待添加）

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest --cov --cov-fail-under=70
```

## 最佳实践

### 1. 独立性

每个测试应该独立运行，不依赖其他测试的状态。

```python
# ✅ 好的做法
def test_function():
    data = create_test_data()  # 每次创建新数据
    result = process(data)
    assert result == expected

# ❌ 避免
shared_data = []  # 不要在测试间共享状态
```

### 2. 使用临时目录

文件操作测试应使用临时目录：

```python
from tempfile import TemporaryDirectory

def test_file_operation():
    with TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.txt"
        # 测试代码
```

### 3. 清晰的断言消息

```python
# ✅ 好的做法
assert result == expected, f"Expected {expected}, got {result}"

# ❌ 避免
assert result == expected
```

### 4. 测试边界情况

- 空输入
- None 值
- 超大数据
- 无效格式
- 异常情况

### 5. 使用 Fixtures

```python
@pytest.fixture
def sample_config():
    """提供测试配置"""
    return {"key": "value"}

def test_with_fixture(sample_config):
    assert sample_config["key"] == "value"
```

## 测试覆盖率不足的模块

以下模块需要补充测试：

- [ ] ai_poadcast/collectors/
- [ ] ai_poadcast/generators/prompt.py
- [ ] ai_poadcast_main/collect_rss_feeds.py (部分覆盖)
- [ ] ai_poadcast_main/daily_workflow.py
- [ ] ai_poadcast_main/generate_stage3_script.py

## 排除覆盖率的代码

使用注释排除不需要测试的代码：

```python
def debug_function():  # pragma: no cover
    """仅用于调试的函数"""
    print("Debug info")
```

## 故障排查

### 导入错误

如果遇到模块导入错误：

```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-cov

# 设置 PYTHONPATH
export PYTHONPATH=/home/user/ai-podcast:$PYTHONPATH
```

### 测试超时

增加超时时间：

```bash
pytest --timeout=60  # 60秒超时
```

### 查看详细输出

```bash
pytest -vv -s  # 更详细的输出 + 显示 print
```

## 参考资源

- [pytest 文档](https://docs.pytest.org/)
- [unittest.mock 文档](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py 文档](https://coverage.readthedocs.io/)

## 测试目标时间线

| 时间段 | 目标 | 优先级 |
|--------|------|--------|
| Week 1 | 核心模块达到 70% | 🔴 高 |
| Week 2 | 旧模块达到 40% | 🟡 中 |
| Month 1 | 整体达到 70% | 🔴 高 |
| Month 2 | 添加集成测试 | 🟡 中 |
| Month 3 | E2E 测试 | 🟢 低 |

---

**最后更新**: 2025-01-15
**维护者**: AI Podcast Team
