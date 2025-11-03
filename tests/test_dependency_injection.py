"""依赖注入单元测试"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_poadcast.generators.script import ScriptGenerator


class MockLLM:
    """Mock LLM客户端"""
    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        return f"Generated: {prompt[:20]}..."


def test_script_generator_with_mock():
    """测试ScriptGenerator接受任意LLM客户端"""
    mock_llm = MockLLM()
    generator = ScriptGenerator(mock_llm)
    
    result = generator.generate("测试prompt", temperature=0.5, max_tokens=100)
    assert result.startswith("Generated: 测试prompt")
    print("✅ 依赖注入测试通过")


def test_multiple_llm_clients():
    """测试可以注入不同的LLM客户端"""
    class LLM_A:
        def generate(self, prompt, temperature, max_tokens):
            return "Response from LLM A"
    
    class LLM_B:
        def generate(self, prompt, temperature, max_tokens):
            return "Response from LLM B"
    
    gen_a = ScriptGenerator(LLM_A())
    gen_b = ScriptGenerator(LLM_B())
    
    assert gen_a.generate("test") == "Response from LLM A"
    assert gen_b.generate("test") == "Response from LLM B"
    print("✅ 多客户端切换测试通过")


if __name__ == "__main__":
    test_script_generator_with_mock()
    test_multiple_llm_clients()
    print("\n所有测试通过！")
