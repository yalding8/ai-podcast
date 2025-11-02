#!/usr/bin/env python3
"""RSS源配置文件"""

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
    "Duolingo English Test": {
        "url": "https://englishtest.duolingo.com/applicants",
        "method": "scrape",
        "tags": ["exam", "duolingo"],
        "check_frequency": "monthly",
        "priority": 8
    },
    
    # 主流教育媒体
    "Times Higher Education": {
        "rss": "https://www.timeshighereducation.com/news.rss",
        "tags": ["ranking", "research", "policy"],
        "check_frequency": "daily",
        "priority": 8
    },
    "QS Rankings News": {
        "rss": "https://news.google.com/rss/search?q=QS+university+rankings&hl=en-US&gl=US&ceid=US:en",
        "tags": ["ranking"],
        "check_frequency": "weekly",
        "priority": 7
    },
    
    # 政府移民与奖学金
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
        "priority": 10
    },
    "IRCC Newsroom": {
        "rss": "https://www.canada.ca/en/immigration-refugees-citizenship.atom",
        "tags": ["canada", "visa", "policy"],
        "check_frequency": "daily",
        "priority": 10
    },
    "Australian Department of Home Affairs": {
        "rss": "https://www.homeaffairs.gov.au/news-media/archive/rss.xml",
        "tags": ["australia", "visa", "policy"],
        "check_frequency": "weekly",
        "priority": 9
    },
    "Chevening Scholarships": {
        "rss": "https://www.chevening.org/feed/",
        "tags": ["uk", "scholarship"],
        "check_frequency": "weekly",
        "priority": 9
    }
}

TIER_2_SOURCES = {
    # 英国
    "UK GOV Education": {
        "rss": "https://www.gov.uk/government/organisations/department-for-education.atom",
        "tags": ["uk", "policy", "visa"],
        "priority": 9
    },
    "UCAS": {
        "url": "https://www.ucas.com/corporate/news-and-key-documents/news",
        "method": "scrape",
        "tags": ["uk", "application"],
        "priority": 8
    },
    
    # 美国
    "Inside Higher Ed": {
        "rss": "https://www.insidehighered.com/news.rss",
        "tags": ["us", "policy", "institution"],
        "priority": 7
    },
    "NAFSA News": {
        "rss": "https://news.google.com/rss/search?q=NAFSA+international+students&hl=en-US&gl=US&ceid=US:en",
        "tags": ["us", "immigration", "policy"],
        "priority": 7
    },
    
    # 澳大利亚
    "Study in Australia": {
        "url": "https://www.studyinaustralia.gov.au/english/news",
        "method": "scrape",
        "tags": ["australia", "policy"],
        "priority": 7
    },
    
    # 加拿大
    "Universities Canada": {
        "url": "https://www.univcan.ca/media-room/media-releases/",
        "method": "scrape",
        "tags": ["canada", "policy"],
        "priority": 7
    },
    
    # 中国
    "中国教育部留学服务中心": {
        "url": "http://www.cscse.edu.cn/cscse/hdxw/index.html",
        "method": "scrape",
        "tags": ["china", "policy", "认证"],
        "priority": 8
    },
    
    # 欧洲与其他地区官方渠道
    "Education New Zealand": {
        "rss": "https://www.enz.govt.nz/news-and-research/news-and-events/rss",
        "tags": ["newzealand", "market", "policy"],
        "priority": 8
    },
    "Campus France": {
        "rss": "https://www.campusfrance.org/en/rss",
        "tags": ["france", "policy", "scholarship"],
        "priority": 7
    },
    "DAAD": {
        "rss": "https://www.daad.de/en/the-daad/news/news/rss.xml",
        "tags": ["germany", "scholarship", "policy"],
        "priority": 7
    },
    "Singapore Ministry of Education": {
        "rss": "https://www.moe.gov.sg/rss/press-releases",
        "tags": ["singapore", "policy"],
        "priority": 7
    },
    
    # 重点院校官方
    "University of Cambridge": {
        "rss": "https://www.cam.ac.uk/news/rss",
        "tags": ["uk", "institution"],
        "priority": 7
    },
    "MIT News": {
        "rss": "https://news.mit.edu/rss",
        "tags": ["us", "institution", "research"],
        "priority": 7
    },
    "University of Toronto": {
        "rss": "https://www.utoronto.ca/news/rss.xml",
        "tags": ["canada", "institution"],
        "priority": 7
    }
}

TIER_3_SOURCES = {
    # Google News（简化版，无特殊字符）
    "Google News - International Education": {
        "rss": "https://news.google.com/rss/search?q=international+students+study+abroad+visa&hl=en-US&gl=US&ceid=US:en",
        "tags": ["general"],
        "priority": 6
    },
    "Google News - University Rankings": {
        "rss": "https://news.google.com/rss/search?q=university+rankings+QS+THE&hl=en-US&gl=US&ceid=US:en",
        "tags": ["ranking"],
        "priority": 5
    },
    
    # Reddit
    "r/gradadmissions": {
        "rss": "https://www.reddit.com/r/gradadmissions/top/.rss?t=week",
        "tags": ["application", "trends"],
        "priority": 5
    },
    "r/ApplyingToCollege": {
        "rss": "https://www.reddit.com/r/ApplyingToCollege/top/.rss?t=week",
        "tags": ["application", "trends"],
        "priority": 5
    },
    
    # 行业研究与数据服务
    "World Education Services (WENR)": {
        "rss": "https://wenr.wes.org/feed",
        "tags": ["global", "research", "policy"],
        "priority": 6
    },
    "ApplyBoard Insights": {
        "rss": "https://www.applyboard.com/blog/feed",
        "tags": ["market", "trend"],
        "priority": 6
    },
    "QS Insights Magazine": {
        "rss": "https://www.qs.com/insights-magazine/feed/",
        "tags": ["ranking", "analysis"],
        "priority": 5
    },
    "World Bank Education": {
        "rss": "https://blogs.worldbank.org/education/rss",
        "tags": ["global", "policy", "data"],
        "priority": 6
    }
}
