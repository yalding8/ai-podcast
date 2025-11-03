"""依赖注入示例"""

from ai_poadcast.llm import create_llm_client
from ai_poadcast.generators.script import ScriptGenerator


# 示例1：使用工厂函数
def example_with_factory():
    """使用工厂函数创建客户端"""
    llm = create_llm_client(provider="deepseek", model="deepseek-chat")
    generator = ScriptGenerator(llm)
    
    prompt = "生成一段播客开场白..."
    script = generator.generate(prompt, temperature=0.5, max_tokens=500)
    print(script)


# 示例2：直接注入
def example_with_direct_injection():
    """直接注入特定客户端"""
    from ai_poadcast.llm import OpenAIClient
    
    llm = OpenAIClient(model="gpt-4")
    generator = ScriptGenerator(llm)
    
    script = generator.generate("生成播客脚本...")
    print(script)


# 示例3：测试时注入Mock
def example_with_mock():
    """测试时使用Mock客户端"""
    class MockLLM:
        def generate(self, prompt, temperature, max_tokens):
            return "这是测试脚本内容"
    
    generator = ScriptGenerator(MockLLM())
    script = generator.generate("任意prompt")
    assert script == "这是测试脚本内容"
    print("✅ Mock测试通过")


if __name__ == "__main__":
    print("依赖注入示例")
    print("=" * 50)
    example_with_mock()
