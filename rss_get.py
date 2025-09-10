import feedparser
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import re


def get_rss_content(rss_url: str) -> Dict[str, Any]:
    """
    读取RSS内容的简易函数
    
    Args:
        rss_url (str): RSS订阅链接
        
    Returns:
        Dict[str, Any]: 包含RSS内容的字典
    """
    try:
        # 解析RSS feed
        feed = feedparser.parse(rss_url)
        
        # 检查是否解析成功
        if feed.bozo:
            print(f"警告: RSS解析可能有问题 - {feed.bozo_exception}")
        
        # 提取feed基本信息
        feed_info = {
            'title': feed.feed.get('title', '未知标题'),
            'description': feed.feed.get('description', ''),
            'link': feed.feed.get('link', ''),
            'language': feed.feed.get('language', ''),
            'updated': feed.feed.get('updated', ''),
            'total_entries': len(feed.entries)
        }
        
        # 提取文章条目
        articles = []
        def _get_day_from_struct(e):
            try:
                if hasattr(e, 'published_parsed') and e.published_parsed:
                    return e.published_parsed.tm_mday
                if hasattr(e, 'updated_parsed') and e.updated_parsed:
                    return e.updated_parsed.tm_mday
            except Exception:
                pass
            return None

        for entry in feed.entries:
            article = {
                'title': entry.get('title', '无标题'),
                'link': entry.get('link', ''),
                'description': entry.get('description', ''),
                'summary': entry.get('summary', ''),
                'published': entry.get('published', ''),
                'updated': entry.get('updated', ''),
                'author': entry.get('author', ''),
                'tags': [tag.term for tag in entry.get('tags', [])],
                'published_day': _get_day_from_struct(entry),
            }
            articles.append(article)
        
        return {
            'status': 'success',
            'feed_info': feed_info,
            'articles': articles
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'feed_info': None,
            'articles': []
        }


def print_rss_summary(rss_data: Dict[str, Any], target_day: Optional[int] = None, max_items: Optional[int] = 5) -> None:
    """
    打印RSS摘要信息
    
    Args:
        rss_data (Dict[str, Any]): get_rss_content函数返回的数据
        target_day (Optional[int]): 目标日期（日号1-31）。为空则不按日期过滤。
        max_items (Optional[int]): 每个源打印的最大条目数。为空则默认5。
    """
    if rss_data['status'] == 'error':
        print(f"错误: {rss_data['error']}")
        return
    
    feed_info = rss_data['feed_info']
    articles = rss_data['articles']
    
    print(f"\n=== RSS Feed 信息 ===")
    print(f"标题: {feed_info['title']}")
    print(f"描述: {feed_info['description']}")
    print(f"链接: {feed_info['link']}")
    print(f"语言: {feed_info['language']}")
    print(f"更新时间: {feed_info['updated']}")
    print(f"文章总数: {feed_info['total_entries']}")
    
    def _get_day_from_str(date_str: str) -> Any:
        if not date_str:
            return None
        fmts = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%d %H:%M:%S %z",
            "%Y-%m-%d %H:%M:%S",
        ]
        for f in fmts:
            try:
                return datetime.strptime(date_str, f).day
            except Exception:
                continue
        m = re.search(r"[\-,\s](\d{1,2})[\s,]", date_str)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                return None
        return None

    # 过滤逻辑：按 target_day（如提供）过滤，否则不过滤
    if target_day is not None:
        filtered: List[Dict[str, Any]] = []
        for a in articles:
            day = a.get('published_day')
            if day is None:
                day = _get_day_from_str(a.get('published', '')) or _get_day_from_str(a.get('updated', ''))
            if day == target_day:
                filtered.append(a)
    else:
        filtered = articles

    count = max_items if max_items is not None else 5
    print(f"\n=== 最新文章（前{count}条{'' if target_day is None else f'｜仅日期为 {target_day} 号'}）===")
    for i, article in enumerate(filtered[:count], 1):
        print(f"\n{i}. {article['title']}")
        print(f"   链接: {article['link']}")
        print(f"   发布时间: {article['published']}")
        #print(f"   摘要: {article['summary'][:100]}..." if len(article['summary']) > 100 else f"   摘要: {article['summary']}")


# 示例使用
if __name__ == "__main__":
    # A.1 基础情报设施
    basic_intelligence = {
        # A.1.1 顶级科技与科学媒体
        "Wired": "https://www.wired.com/feed/rss",
        "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
        "MIT Technology Review": "https://www.technologyreview.com/feed",
        "IEEE Spectrum": "https://spectrum.ieee.org/feeds/feed.rss",
        
        # A.1.2 风险投资与创业生态
        "TechCrunch": "https://techcrunch.com/feed/",
        "Crunchbase News": "https://news.crunchbase.com/feed",
        "PrNewswire Telecomm­unications": "https://www.prnewswire.com/rss/telecommunications-latest-news/telecommunications-latest-news-list.rss",
        "PrNewswire Consumer Technology": "https://www.prnewswire.com/rss/consumer-technology-latest-news/consumer-technology-latest-news-list.rss",
        "PrNewswire Business Technology": "https://www.prnewswire.com/rss/business-technology-latest-news/business-technology-latest-news-list.rss",
        # A.1.3 全球金融市场与经济指标
        "Investing.com - All News": "https://www.investing.com/rss/news.rss",
        "Investing.com - Stock Market": "https://www.investing.com/rss/news_25.rss",
        "Bloomberg - Technology": "https://feeds.bloomberg.com/technology/news.rss",
        # "Nasdaq - Technology": "https://www.nasdaq.com/feed/nasdaq-original/technology",
        # "Nasdaq - AI": "https://www.nasdaq.com/feed/nasdaq-original/artificial-intelligence",
    }
    
    # A.2.1 人工智能
    ai_sources = {
        "Google Research Blog": "https://research.google/blog/rss",
        "OpenAI Blog": "https://openai.com/blog/rss.xml",
        "BAIR Blog": "https://bair.berkeley.edu/blog/feed.xml",
        "AWS ML Blog": "https://aws.amazon.com/blogs/machine-learning/feed/",
        "ML Mastery": "https://machinelearningmastery.com/blog/feed/",
        "MarkTechPost": "https://www.marktechpost.com/feed",
        "Unite.AI": "https://unite.ai/feed",
        "VentureBeat - AI": "https://venturebeat.com/category/ai/feed/",
        "Ars Technica - AI": "https://arstechnica.com/ai/feed",
        "MIT Tech Review - AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    }
    
    # A.2.2 具身智能与先进机器人
    robotics_sources = {
        "arXiv - Robotics": "https://rss.arxiv.org/rss/cs.RO",
        # "arXiv - AI": "https://rss.arxiv.org/rss/cs.AI",
        "The Robot Report": "https://www.therobotreport.com/feed",
        "Robohub": "https://robohub.org/feed",
        "Robotics & Automation News": "https://roboticsandautomationnews.com/feed/",
        "IEEE Spectrum - Robotics": "https://spectrum.ieee.org/feeds/topic/robotics.rss",
        "ScienceDaily - Robotics": "https://www.sciencedaily.com/rss/computers_math/robotics.xml",
        "MIT News - AI": "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml",
        "MIT News - Robotics": "https://news.mit.edu/topic/mitrobotics-rss.xml",
    }
    
    # A.2.3 自动驾驶系统
    autonomous_driving = {
        "Guardian - Self-driving": "https://www.theguardian.com/technology/self-driving-cars/rss",
        "Medium - Self Driving": "https://medium.com/feed/self-driving-cars",
        "InsideEVs - Autonomous": "https://insideevs.com/rss/category/autonomous-vehicles/",
        "TAS": "https://tas.ac.uk/feeds/",
        "NVIDIA Newsroom": "https://nvidianews.nvidia.com/feed/",
    }
    
    # 中文科技媒体
    chinese_tech = {
        "36kr": "https://36kr.com/feed",
        "量子位": "https://wechat2rss.xlab.app/feed/7131b577c61365cb47e81000738c10d872685908.xml",
        "新智元": "https://wechat2rss.xlab.app/feed/ede30346413ea70dbef5d485ea5cbb95cca446e7.xml",
        "机器之心": "https://wechat2rss.xlab.app/feed/51e92aad2728acdd1fda7314be32b16639353001.xml",
        "人形机器人发布":"https://raw.githubusercontent.com/osnsyc/Wechat-Scholar/main/channels/gh_3d2d45a5f9f1.xml",
        "深科技":"https://raw.githubusercontent.com/osnsyc/Wechat-Scholar/main/channels/gh_27c43c799b0c.xml",
    }

    selected_news ={
        "36kr": "https://36kr.com/feed",
        "量子位": "https://wechat2rss.xlab.app/feed/7131b577c61365cb47e81000738c10d872685908.xml",
        "新智元": "https://wechat2rss.xlab.app/feed/ede30346413ea70dbef5d485ea5cbb95cca446e7.xml",
        "机器之心": "https://wechat2rss.xlab.app/feed/51e92aad2728acdd1fda7314be32b16639353001.xml",
        "人形机器人发布":"https://raw.githubusercontent.com/osnsyc/Wechat-Scholar/main/channels/gh_3d2d45a5f9f1.xml",
        "深科技":"https://raw.githubusercontent.com/osnsyc/Wechat-Scholar/main/channels/gh_27c43c799b0c.xml",
        "TechCrunch": "https://techcrunch.com/feed/",
        #"Crunchbase News": "https://news.crunchbase.com/feed",
        "MIT Tech Review - AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        "PrNewswire Telecomm­unications": "https://www.prnewswire.com/rss/telecommunications-latest-news/telecommunications-latest-news-list.rss",
        #"PrNewswire Consumer Technology": "https://www.prnewswire.com/rss/consumer-technology-latest-news/consumer-technology-latest-news-list.rss",
        #"PrNewswire Business Technology": "https://www.prnewswire.com/rss/business-technology-latest-news/business-technology-latest-news-list.rss",

    }
    
    # 选择要测试的RSS源分类
    print("RSS情报系统测试")
    print("=" * 70)
    
    # 可以选择测试不同的分类
    test_categories = {
        "基础情报设施": basic_intelligence,
        "人工智能": ai_sources,
        "机器人技术": robotics_sources,
        "自动驾驶": autonomous_driving,
        "中文科技媒体": chinese_tech,
        "新闻": selected_news,
    }
    
    # 选择要测试的分类（可以修改这里来测试不同分类）
    selected_category = "新闻"  # 可以改为其他分类名称
    test_sources = test_categories[selected_category]
    
    print(f"\n正在测试分类: {selected_category}")
    print(f"RSS源数量: {len(test_sources)}")
    print("=" * 70)
    
    for name, url in test_sources.items():
        print(f"\n正在读取 {name}: {url}")
        rss_data = get_rss_content(url)
        print_rss_summary(rss_data)
        print("-" * 70)
