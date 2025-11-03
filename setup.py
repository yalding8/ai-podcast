"""安装配置"""

from setuptools import setup, find_packages

setup(
    name="ai-poadcast",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4>=4.12.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "aipod=ai_poadcast.cli:main",
        ],
    },
    python_requires=">=3.9",
    extras_require={
        "llm": ["openai>=1.0.0", "anthropic>=0.18.0", "requests>=2.31.0"],
        "tts": ["websocket-client>=1.6.0"],
    },
)
