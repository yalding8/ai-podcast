#!/usr/bin/env python3
"""
高质量新闻源配置 - 专注于权威性和时效性
仅包含经过验证的高质量源，用于重要新闻采集
"""

# 政府官方源 - 最高优先级
OFFICIAL_GOVERNMENT_SOURCES = {
    "USCIS News": {
        "rss": "https://www.uscis.gov/rss.xml",
        "tags": ["us", "visa", "policy", "immigration"],
        "priority": 10,
        "max_items": 8
    },
    "UK Home Office": {
        "rss": "https://www.gov.uk/government/organisations/home-office.atom",
        "tags": ["uk", "visa", "policy", "immigration"],
        "priority": 10,
        "max_items": 8
    },
    "IRCC Canada": {
        "rss": "https://www.canada.ca/en/immigration-refugees-citizenship.atom",
        "tags": ["canada", "visa", "policy", "immigration"],
        "priority": 10,
        "max_items": 6
    },
    "Australian Home Affairs": {
        "rss": "https://www.homeaffairs.gov.au/rss/news-media.xml",
        "tags": ["australia", "visa", "policy", "immigration"],
        "priority": 10,
        "max_items": 6
    }
}

# 权威教育媒体 - 高优先级
AUTHORITATIVE_MEDIA_SOURCES = {
    "ICEF Monitor": {
        "rss": "https://monitor.icef.com/feed/",
        "tags": ["policy", "market", "data", "global"],
        "priority": 10,
        "max_items": 5
    },
    "The PIE News": {
        "rss": "https://thepienews.com/feed/",
        "tags": ["policy", "institution", "market", "global"],
        "priority": 10,
        "max_items": 5
    },
    "Study International": {
        "rss": "https://www.studyinternational.com/feed/",
        "tags": ["student", "institution", "policy", "global"],
        "priority": 9,
        "max_items": 4
    },
    "University World News": {
        "rss": "https://www.universityworldnews.com/rss/pf_rss.php",
        "tags": ["policy", "global", "institution", "research"],
        "priority": 9,
        "max_items": 4
    },
    "Times Higher Education": {
        "rss": "https://www.timeshighereducation.com/rss",
        "tags": ["ranking", "research", "policy", "global"],
        "priority": 9,
        "max_items": 4
    }
}

# 考试机构官方 - 中高优先级
EXAM_OFFICIAL_SOURCES = {
    "ETS TOEFL Updates": {
        "url": "https://www.ets.org/toefl/test-takers/ibt/news.html",
        "method": "scrape",
        "tags": ["exam", "toefl", "us"],
        "priority": 9,
        "check_frequency": "weekly"
    },
    "IELTS Official Updates": {
        "url": "https://www.ielts.org/for-test-takers/ielts-updates",
        "method": "scrape", 
        "tags": ["exam", "ielts", "uk"],
        "priority": 9,
        "check_frequency": "weekly"
    },
    "College Board News": {
        "rss": "https://newsroom.collegeboard.org/rss",
        "tags": ["us", "exam", "admission", "sat"],
        "priority": 8,
        "max_items": 3
    }
}

# 数据与研究机构 - 中优先级
RESEARCH_DATA_SOURCES = {
    "IIE Open Doors": {
        "rss": "https://www.iie.org/rss/news",
        "tags": ["us", "data", "mobility", "statistics"],
        "priority": 9,
        "max_items": 3
    },
    "WENR (WES)": {
        "rss": "https://wenr.wes.org/feed",
        "tags": ["global", "research", "policy", "data"],
        "priority": 8,
        "max_items": 3
    },
    "OECD Education": {
        "rss": "https://www.oecd.org/education/rss.xml",
        "tags": ["global", "policy", "data", "statistics"],
        "priority": 8,
        "max_items": 2
    },
    "QS Intelligence Unit": {
        "rss": "https://www.topuniversities.com/rss.xml",
        "tags": ["ranking", "data", "global", "analysis"],
        "priority": 8,
        "max_items": 3
    }
}

# 奖学金与资助 - 中优先级
SCHOLARSHIP_SOURCES = {
    "Fulbright Commission": {
        "rss": "https://www.fulbright.org.uk/news/rss",
        "tags": ["us", "uk", "scholarship", "exchange"],
        "priority": 8,
        "max_items": 2
    },
    "Chevening Scholarships": {
        "rss": "https://www.chevening.org/feed/",
        "tags": ["uk", "scholarship", "global"],
        "priority": 8,
        "max_items": 2
    },
    "DAAD Germany": {
        "rss": "https://www.daad.de/en/rss.xml",
        "tags": ["germany", "scholarship", "policy"],
        "priority": 7,
        "max_items": 2
    }
}

# 合并所有高质量源
PREMIUM_SOURCES = {
    **OFFICIAL_GOVERNMENT_SOURCES,
    **AUTHORITATIVE_MEDIA_SOURCES,
    **EXAM_OFFICIAL_SOURCES,
    **RESEARCH_DATA_SOURCES,
    **SCHOLARSHIP_SOURCES
}

# 质量过滤规则
QUALITY_FILTERS = {
    "min_word_count": 100,  # 最少字数
    "exclude_keywords": [
        "sport", "football", "basketball", "celebrity", "entertainment",
        "gossip", "fashion", "beauty", "recipe", "cooking", "game", "gaming",
        "weather", "traffic", "local news", "obituary"
    ],
    "priority_keywords": [
        "visa", "immigration", "policy", "university", "college", "student",
        "international", "admission", "ranking", "scholarship", "tuition",
        "application", "deadline", "exam", "test", "ielts", "toefl",
        "study abroad", "education", "graduate", "undergraduate"
    ],
    "source_reliability": {
        "government": 10,
        "official_institution": 9,
        "authoritative_media": 8,
        "research_organization": 8,
        "general_media": 6
    }
}