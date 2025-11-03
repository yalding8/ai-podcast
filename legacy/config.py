#!/usr/bin/env python3
"""
统一配置管理 - 所有配置集中在此文件
"""
import os
from pathlib import Path

# ==================== 项目路径 ====================
PROJECT_ROOT = Path(__file__).parent
AI_POADCAST_MAIN = PROJECT_ROOT / "ai_poadcast_main"
SOURCE_ARCHIVE = PROJECT_ROOT / "source_archive"
AUDIO_EXPORTS = PROJECT_ROOT / "audio_exports"
SCRIPT_OUTPUT = PROJECT_ROOT / "脚本输出"
CARD_OUTPUT = PROJECT_ROOT / "要点卡片"

# ==================== API密钥 ====================
# LLM提供商
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# TTS服务
XUNFEI_APP_ID = os.getenv("XUNFEI_APP_ID", "")
XUNFEI_API_SECRET = os.getenv("XUNFEI_API_SECRET", "")
XUNFEI_API_KEY = os.getenv("XUNFEI_API_KEY", "")
VOLCENGINE_APP_ID = os.getenv("VOLCENGINE_APP_ID", "")
VOLCENGINE_TOKEN = os.getenv("VOLCENGINE_TOKEN", "")

# 新闻API
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# ==================== RSS源配置 ====================
RSS_SOURCES = {
    # Tier 1 - 最高优先级
    "ICEF Monitor": {
        "rss": "https://monitor.icef.com/feed/",
        "priority": 10,
        "max_items": 5,
        "tags": ["policy", "market", "data"]
    },
    "The PIE News": {
        "rss": "https://thepienews.com/feed/",
        "priority": 10,
        "max_items": 5,
        "tags": ["policy", "institution", "market"]
    },
    "Study International": {
        "rss": "https://www.studyinternational.com/feed/",
        "priority": 10,
        "max_items": 4,
        "tags": ["policy", "institution", "student"]
    },
    "University World News": {
        "rss": "https://www.universityworldnews.com/rss/pf_rss.php",
        "priority": 10,
        "max_items": 4,
        "tags": ["policy", "global", "institution"]
    },
    "USCIS Newsroom": {
        "rss": "https://www.uscis.gov/rss.xml",
        "priority": 10,
        "max_items": 6,
        "tags": ["us", "visa", "policy"]
    },
    "UK Visas and Immigration": {
        "rss": "https://www.gov.uk/government/organisations/uk-visas-and-immigration.atom",
        "priority": 10,
        "max_items": 6,
        "tags": ["uk", "visa", "policy"]
    },
    
    # Tier 2 - 高优先级
    "QS Top Universities": {
        "rss": "https://www.topuniversities.com/rss.xml",
        "priority": 9,
        "max_items": 3,
        "tags": ["ranking", "admission", "student"]
    },
    "College Board": {
        "rss": "https://newsroom.collegeboard.org/rss",
        "priority": 8,
        "max_items": 3,
        "tags": ["us", "exam", "admission"]
    },
    "WENR (WES)": {
        "rss": "https://wenr.wes.org/feed",
        "priority": 8,
        "max_items": 3,
        "tags": ["global", "research", "policy"]
    },
    
    # Tier 3 - 中优先级（严格过滤）
    "UK GOV Education": {
        "rss": "https://www.gov.uk/government/organisations/department-for-education.atom",
        "priority": 7,
        "max_items": 3,
        "tags": ["uk", "policy"],
        "strict_filter": True  # 需要严格关键词过滤
    },
    "Google News - International Education": {
        "rss": "https://news.google.com/rss/search?q=international+students+study+abroad+visa&hl=en-US&gl=US&ceid=US:en",
        "priority": 6,
        "max_items": 10,
        "tags": ["general"]
    }
}

# ==================== 过滤规则 ====================
PRIORITY_KEYWORDS = [
    "visa", "immigration", "policy", "international student",
    "study abroad", "admission", "application", "scholarship",
    "university ranking", "tuition", "ielts", "toefl", "gre", "gmat"
]

EXCLUDE_KEYWORDS = [
    "sport", "football", "basketball", "celebrity", "entertainment",
    "weather", "traffic", "crime", "real estate", "cryptocurrency"
]

# UK GOV Education 严格过滤
UK_GOV_KEYWORDS = [
    "international student", "overseas student", "international education",
    "visa", "immigration", "foreign student", "study abroad"
]

# ==================== 工作流配置 ====================
# 优先级阈值
DEFAULT_MIN_PRIORITY = 8
AUTO_IMPORT_MIN_PRIORITY = 9
AUTO_IMPORT_COUNT = 3

# RSS采集
RSS_TIME_FILTER_HOURS = 48
RSS_REQUEST_TIMEOUT = 20
RSS_MAX_RETRIES = 3

# Stage 2 - 要点提取
KEYPOINT_PROVIDER = os.getenv("KEYPOINT_PROVIDER", "openai")
KEYPOINT_MODEL = os.getenv("KEYPOINT_MODEL", "gpt-4o-mini")
KEYPOINT_MAX_SOURCE_CHARS = 6000
KEYPOINT_MAX_TOKENS = 512

# Stage 3 - 脚本生成
SCRIPT_PROVIDER = os.getenv("SCRIPT_PROVIDER", "openai")
SCRIPT_MODEL = os.getenv("SCRIPT_MODEL", "gpt-4o-mini")

# TTS配置
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "xunfei")  # xunfei/volcengine
XUNFEI_DEFAULT_VOICE = "xiaoyan"
XUNFEI_DEFAULT_SPEED = 50
XUNFEI_SEGMENT_SIZE = 4000
XUNFEI_MAX_RETRIES = 3

# ==================== 文件命名规范 ====================
SOURCE_ARCHIVE_PATTERN = "{date}/{slug}.md"
CARD_OUTPUT_PATTERN = "{date}/{slug}_card_final.md"
SCRIPT_OUTPUT_PATTERN = "{date}/episode_{date}_v{version}.md"
AUDIO_OUTPUT_PATTERN = "{year}/episode_{date}_{voice}.{ext}"

# ==================== 功能开关 ====================
ENABLE_DEMO_NEWS = False  # Demo新闻（虚假URL）
ENABLE_AUTO_IMPORT = True  # 自动导入高优先级新闻
ENABLE_NEWSAPI = bool(NEWSAPI_KEY)  # NewsAPI采集
ENABLE_STRICT_FILTER = True  # 严格关键词过滤
