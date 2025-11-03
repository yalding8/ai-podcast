#!/usr/bin/env python3
"""RSS源配置文件 - 已修复失效源"""

TIER_1_SOURCES = {
    # 行业核心媒体
    "ICEF Monitor": {
        "rss": "https://monitor.icef.com/feed/",
        "tags": ["policy", "market", "data"],
        "check_frequency": "daily",
        "priority": 10
    },
    "The PIE News": {
        "rss": "https://thepienews.com/feed/",
        "tags": ["policy", "institution", "market"],
        "check_frequency": "daily",
        "priority": 10,
        "max_items": 5
    },
    "Study International": {
        "rss": "https://www.studyinternational.com/feed/",
        "tags": ["policy", "institution", "student"],
        "check_frequency": "daily",
        "priority": 10
    },
    "University World News": {
        "rss": "https://www.universityworldnews.com/rss/pf_rss.php",
        "tags": ["policy", "global", "institution"],
        "check_frequency": "daily",
        "priority": 10
    },
    
    # 考试机构（需手动监控）
    "IELTS Official": {
        "url": "https://www.ielts.org/for-test-takers/ielts-updates",
        "method": "scrape",
        "tags": ["exam", "ielts"],
        "check_frequency": "weekly",
        "priority": 9
    },
    "ETS TOEFL": {
        "url": "https://www.ets.org/toefl/test-takers/ibt/news.html",
        "method": "scrape",
        "tags": ["exam", "toefl"],
        "check_frequency": "weekly",
        "priority": 9
    },
    
    # 主流教育媒体
    "QS Top Universities": {
        "rss": "https://www.topuniversities.com/rss.xml",
        "tags": ["ranking", "admission", "student"],
        "check_frequency": "daily",
        "priority": 9
    },
    
    # 政府移民
    "USCIS Newsroom": {
        "rss": "https://www.uscis.gov/rss.xml",
        "tags": ["us", "visa", "policy"],
        "check_frequency": "daily",
        "priority": 10
    },
    "UK Visas and Immigration": {
        "rss": "https://www.gov.uk/government/organisations/uk-visas-and-immigration.atom",
        "tags": ["uk", "visa", "policy"],
        "check_frequency": "daily",
        "priority": 10,
        "max_items": 6
    }
}

TIER_2_SOURCES = {
    # 英国 - 严格过滤
    "UK GOV Education": {
        "rss": "https://www.gov.uk/government/organisations/department-for-education.atom",
        "tags": ["uk", "policy"],
        "priority": 7,  # 降低优先级
        "max_items": 3  # 限制数量
    },
    
    # 美国
    "College Board": {
        "rss": "https://newsroom.collegeboard.org/rss",
        "tags": ["us", "exam", "admission"],
        "priority": 8
    },
    "NAFSA News": {
        "rss": "https://news.google.com/rss/search?q=NAFSA+international+students&hl=en-US&gl=US&ceid=US:en",
        "tags": ["us", "immigration", "policy"],
        "priority": 7
    }
}

TIER_3_SOURCES = {
    # Google News
    "Google News - International Education": {
        "rss": "https://news.google.com/rss/search?q=international+students+study+abroad+visa&hl=en-US&gl=US&ceid=US:en",
        "tags": ["general"],
        "priority": 6,
        "max_items": 10
    },
    
    # 行业研究
    "World Education Services (WENR)": {
        "rss": "https://wenr.wes.org/feed",
        "tags": ["global", "research", "policy"],
        "priority": 8
    },
    "ApplyBoard Insights": {
        "rss": "https://www.applyboard.com/blog/feed",
        "tags": ["market", "trend"],
        "priority": 6
    }
}
