from flask import Flask, jsonify, render_template, session
import requests
import os
import time

# 配置
FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', "cli_a8341be1df7f901c")
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', "bLbLrrlOJjQCRXcSruTbshbd8fgPOms0")
BASE_ID = os.environ.get('BASE_ID', "Ff4vb1pI5aLIh2s41mgcphRCnJh")
TABLE_ID = os.environ.get('TABLE_ID', "tbl4YNGcNh3Qhepi")
FEISHU_API_BASE_URL = "https://open.feishu.cn/open-apis"

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

class FeishuAPI:
    """飞书API操作类"""
    
    def __init__(self):
        self.app_id = FEISHU_APP_ID
        self.app_secret = FEISHU_APP_SECRET
        self.base_url = FEISHU_API_BASE_URL
        self.access_token = None
        self.token_expires_at = 0
        
    def get_access_token(self):
        """获取访问令牌"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
            
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload)
            data = response.json()
            
            if data.get('code') == 0:
                self.access_token = data['tenant_access_token']
                self.token_expires_at = time.time() + data['expire'] - 300
                return self.access_token
            else:
                print(f"获取token失败: {data}")
                return None
        except Exception as e:
            print(f"获取token异常: {e}")
            return None
    
    def get_records(self, base_id, table_id, page_size=100):
        """获取多维表格记录"""
        token = self.get_access_token()
        if not token:
            return []
            
        url = f"{self.base_url}/bitable/v1/apps/{base_id}/tables/{table_id}/records"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "page_size": page_size
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', {}).get('items', [])
            else:
                print(f"获取记录失败: {data}")
                return []
        except Exception as e:
            print(f"获取记录异常: {e}")
            return []

# 初始化飞书API
feishu_api = FeishuAPI()

# 翻译功能
TRANSLATIONS = {
    'zh': {
        'site_title': 'AO生态文章AI总结',
        'home': '首页',
        'submit_article': '提交文章',
        'data_source': '数据来源：飞书多维表格',
        'welcome_title': 'AO生态文章AI总结',
        'welcome_subtitle': '探索AO生态的最新动态和深度见解',
        'search_placeholder': '搜索文章...',
        'read_more': '阅读全文',
        'back_to_home': '返回首页',
        'loading_error': '加载失败，请稍后重试',
        'check_connection': '检查连接',
        'no_articles': '暂无文章',
        'no_articles_desc': '请稍后再试或检查数据连接',
        'review': '文章点评',
        'language': '语言',
        'chinese': '中文',
        'english': 'English'
    },
    'en': {
        'site_title': 'AO Ecosystem AI Article Summary',
        'home': 'Home',
        'submit_article': 'Submit Article',
        'data_source': 'Data Source: Feishu Bitable',
        'welcome_title': 'AO Ecosystem AI Article Summary',
        'welcome_subtitle': 'Explore the latest trends and insights in the AO ecosystem',
        'search_placeholder': 'Search articles...',
        'read_more': 'Read Full Article',
        'back_to_home': 'Back to Home',
        'loading_error': 'Loading failed, please try again later',
        'check_connection': 'Check Connection',
        'no_articles': 'No Articles',
        'no_articles_desc': 'Please try again later or check data connection',
        'review': 'Article Review',
        'language': 'Language',
        'chinese': '中文',
        'english': 'English'
    }
}

def get_text(key, lang='zh'):
    """获取翻译文本"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['zh']).get(key, key)

def format_blog_data(records):
    """格式化博客数据"""
    blogs = []
    for record in records:
        fields = record.get('fields', {})
        
        title = (fields.get('标题', '') or 
                fields.get('title', '') or 
                fields.get('Title', ''))
        
        quote = (fields.get('金句输出', '') or 
                fields.get('金句提炼.输出结果', '') or
                fields.get('金句提炼', '') or
                fields.get('quote', ''))
        
        content = (fields.get('概要内容输出', '') or 
                  fields.get('概要内容提炼.输出结果', '') or
                  fields.get('概要内容提炼', '') or
                  fields.get('全文内容提取', '') or
                  fields.get('content', ''))
        
        # 获取链接字段
        link_field = fields.get('链接', {})
        external_link = ''
        if isinstance(link_field, dict):
            external_link = link_field.get('link', '') or link_field.get('url', '')
        elif isinstance(link_field, str):
            external_link = link_field
        
        # 测试数据处理
        if title == "1":
            title = f"测试文章 {record.get('record_id', '')[:8]}"
        if quote == "1":
            quote = "这是一句测试金句，用于展示博客的金句功能。"
        if content == "1":
            content = "这是测试文章内容，用于展示博客的完整文章功能。"
        
        if title:
            blog = {
                'id': record.get('record_id', ''),
                'title': title,
                'quote': quote,
                'content': content,
                'preview': content[:100] + '...' if len(content) > 100 else content,
                'external_link': external_link
            }
            blogs.append(blog)
    
    return blogs

def get_current_language():
    """获取当前语言设置"""
    return session.get('language', 'zh')

@app.route('/set_language/<lang>')
def set_language(lang):
    """设置语言"""
    if lang in ['zh', 'en']:
        session['language'] = lang
    return jsonify({'status': 'success', 'language': lang})

def generate_html_page(blogs, lang='zh'):
    """生成HTML页面"""
    t = TRANSLATIONS[lang]
    
    blog_cards = ""
    if blogs:
        for blog in blogs:
            external_link = blog.get('external_link', '')
            read_more_link = f'<a href="{external_link}" class="btn btn-primary" target="_blank">{t["read_more"]}</a>' if external_link else f'<a href="/detail/{blog["id"]}" class="btn btn-primary">{t["read_more"]}</a>'
            
            blog_cards += f"""
            <article class="blog-card">
                <div class="blog-header">
                    <h2 class="blog-title">{blog['title']}</h2>
                </div>
                {f'<div class="blog-quote"><blockquote>{blog["quote"]}</blockquote></div>' if blog.get('quote') else ''}
                <div class="blog-preview">
                    <p>{blog['preview']}</p>
                </div>
                <div class="blog-footer">
                    {read_more_link}
                </div>
            </article>
            """
    else:
        blog_cards = f"""
        <div class="empty-state">
            <h2>{t['no_articles']}</h2>
            <p>{t['no_articles_desc']}</p>
            <a href="/api/test" class="btn btn-secondary">{t['check_connection']}</a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="{'zh-CN' if lang == 'zh' else 'en'}">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{t['site_title']}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; line-height: 1.6; color: #333; background: #f8fafc; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
            .header {{ background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 40px; }}
            .nav {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 0; }}
            .logo-text {{ font-size: 24px; font-weight: 700; color: #2563eb; text-decoration: none; }}
            .nav-links {{ display: flex; align-items: center; gap: 30px; }}
            .nav-link {{ text-decoration: none; color: #64748b; font-weight: 500; transition: color 0.3s; }}
            .nav-link:hover {{ color: #2563eb; }}
            .language-switcher {{ display: flex; gap: 10px; }}
            .lang-btn {{ padding: 8px 16px; border: 1px solid #e2e8f0; background: white; border-radius: 6px; cursor: pointer; transition: all 0.3s; }}
            .lang-btn.active {{ background: #2563eb; color: white; border-color: #2563eb; }}
            .hero-section {{ text-align: center; margin-bottom: 60px; }}
            .hero-title {{ font-size: 48px; font-weight: 700; color: #1e293b; margin-bottom: 20px; }}
            .hero-subtitle {{ font-size: 20px; color: #64748b; }}
            .blog-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; margin-bottom: 60px; }}
            .blog-card {{ background: white; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: transform 0.3s, box-shadow 0.3s; }}
            .blog-card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 30px rgba(0,0,0,0.12); }}
            .blog-title {{ font-size: 24px; font-weight: 600; color: #1e293b; margin-bottom: 20px; }}
            .blog-quote {{ margin-bottom: 20px; }}
            .blog-quote blockquote {{ font-style: italic; color: #2563eb; border-left: 4px solid #2563eb; padding-left: 20px; }}
            .blog-preview {{ color: #64748b; margin-bottom: 25px; }}
            .btn {{ display: inline-block; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 500; transition: all 0.3s; }}
            .btn-primary {{ background: #2563eb; color: white; }}
            .btn-primary:hover {{ background: #1d4ed8; }}
            .btn-secondary {{ background: #f1f5f9; color: #64748b; }}
            .btn-secondary:hover {{ background: #e2e8f0; }}
            .empty-state {{ text-align: center; padding: 60px 20px; }}
            .footer {{ text-align: center; padding: 40px 0; color: #64748b; border-top: 1px solid #e2e8f0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header class="header">
                <nav class="nav">
                    <a href="/" class="logo-text">{t['site_title']}</a>
                    <div class="nav-links">
                        <a href="/" class="nav-link">{t['home']}</a>
                        <a href="https://uia84zzwgf.feishu.cn/share/base/form/shrcnpVCPowqvVVwosqDqMyBBOd" class="nav-link" target="_blank">{t['submit_article']}</a>
                        <div class="language-switcher">
                            <button onclick="switchLanguage('zh')" class="lang-btn {'active' if lang == 'zh' else ''}">中文</button>
                            <button onclick="switchLanguage('en')" class="lang-btn {'active' if lang == 'en' else ''}">EN</button>
                        </div>
                    </div>
                </nav>
            </header>
            
            <main>
                <div class="hero-section">
                    <h1 class="hero-title">{t['welcome_title']}</h1>
                    <p class="hero-subtitle">{t['welcome_subtitle']}</p>
                </div>
                
                <div class="blog-grid">
                    {blog_cards}
                </div>
            </main>
            
            <footer class="footer">
                <p>&copy; 2025 AO INSIGHT. {t['data_source']}</p>
            </footer>
        </div>
        
        <script>
        function switchLanguage(lang) {{
            fetch('/set_language/' + lang)
                .then(response => response.json())
                .then(data => {{
                    if (data.status === 'success') {{
                        location.reload();
                    }}
                }})
                .catch(error => console.error('Error:', error));
        }}
        </script>
    </body>
    </html>
    """

@app.route('/')
def index():
    """首页"""
    try:
        lang = get_current_language()
        records = feishu_api.get_records(BASE_ID, TABLE_ID)
        blogs = format_blog_data(records)
        
        # 尝试使用模板，如果失败则使用内置HTML
        try:
            translations = {key: get_text(key, lang) for key in TRANSLATIONS[lang].keys()}
            return render_template('index.html', blogs=blogs, lang=lang, t=translations)
        except:
            return generate_html_page(blogs, lang)
    except Exception as e:
        print(f"首页加载异常: {e}")
        return generate_html_page([], get_current_language())

@app.route('/detail/<record_id>')
def detail(record_id):
    """文章详情页"""
    try:
        lang = get_current_language()
        records = feishu_api.get_records(BASE_ID, TABLE_ID)
        blogs = format_blog_data(records)
        
        # 查找指定文章
        blog = None
        for b in blogs:
            if b['id'] == record_id:
                blog = b
                break
        
        if not blog:
            return "文章未找到" if lang == 'zh' else "Article not found", 404
        
        # 传递翻译文本到模板
        translations = {key: get_text(key, lang) for key in TRANSLATIONS[lang].keys()}
            
        return render_template('detail.html', blog=blog, lang=lang, t=translations)
    except Exception as e:
        print(f"详情页加载异常: {e}")
        lang = get_current_language()
        error_msg = "加载失败" if lang == 'zh' else "Loading failed"
        return error_msg, 500

@app.route('/api/test')
def test_api():
    """测试API连接"""
    try:
        token = feishu_api.get_access_token()
        if token:
            records = feishu_api.get_records(BASE_ID, TABLE_ID)
            return jsonify({
                'status': 'success',
                'token_available': True,
                'records_count': len(records),
                'sample_record': records[0] if records else None
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '无法获取访问令牌'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

# Vercel导出
if __name__ == '__main__':
    app.run(debug=True)
