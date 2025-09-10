# 多语言翻译配置
TRANSLATIONS = {
    'zh': {
        'site_title': 'AO 生态文章 - AI 总结',
        'home': '首页',
        'submit_article': '提交文章',
        'welcome_title': '欢迎来到 AO 生态文章总结',
        'welcome_subtitle': '探索 AO 生态系统的最新文章和深度分析',
        'featured_quote': '精选金句',
        'review': '点评',
        'read_more': '阅读全文',
        'no_articles': '暂无文章',
        'no_articles_desc': '还没有发布任何文章，请稍后再来查看。',
        'check_connection': '检查数据连接',
        'data_source': '数据来源于飞书多维表格',
        'back': '返回',
        'close_window': '关闭窗口',
        'article_content': '文章内容',
        'data_source_label': '来源：飞书多维表格',
        'loading_error': '数据加载失败'
    },
    'en': {
        'site_title': 'AO Ecosystem Articles - AI Summary',
        'home': 'Home',
        'submit_article': 'Submit Article',
        'welcome_title': 'Welcome to AO Ecosystem Article Summary',
        'welcome_subtitle': 'Explore the latest articles and in-depth analysis of the AO ecosystem',
        'featured_quote': 'Featured Quote',
        'review': 'Review',
        'read_more': 'Read More',
        'no_articles': 'No Articles',
        'no_articles_desc': 'No articles have been published yet, please check back later.',
        'check_connection': 'Check Data Connection',
        'data_source': 'Data sourced from Feishu Bitable',
        'back': 'Back',
        'close_window': 'Close Window',
        'article_content': 'Article Content',
        'data_source_label': 'Source: Feishu Bitable',
        'loading_error': 'Data loading failed'
    }
}

def get_text(key, lang='zh'):
    """获取指定语言的文本"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['zh']).get(key, key)
