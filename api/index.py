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

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
root_dir = os.path.dirname(current_dir)

app = Flask(__name__, 
           template_folder=os.path.join(root_dir, 'templates'),
           static_folder=os.path.join(root_dir, 'static'))
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


@app.route('/debug')
def debug():
    """调试信息"""
    import os
    return f"""
    <h1>调试信息</h1>
    <p>当前工作目录: {os.getcwd()}</p>
    <p>模板文件夹: {app.template_folder}</p>
    <p>静态文件夹: {app.static_folder}</p>
    <p>模板文件夹是否存在: {os.path.exists(app.template_folder)}</p>
    <p>静态文件夹是否存在: {os.path.exists(app.static_folder)}</p>
    <p>index.html是否存在: {os.path.exists(os.path.join(app.template_folder, 'index.html'))}</p>
    <p>style.css是否存在: {os.path.exists(os.path.join(app.static_folder, 'css', 'style.css'))}</p>
    """

@app.route('/')
def index():
    """首页"""
    # 暂时强制使用内置HTML以确保中国红UI显示
    lang = get_current_language()
    records = feishu_api.get_records(BASE_ID, TABLE_ID)
    blogs = format_blog_data(records)
    
    # 直接返回带中国红样式的HTML
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>AO生态文章AI总结</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --primary-color: #DC143C;
                    --primary-light: #FF6B6B;
                    --primary-dark: #B22222;
                    --secondary-color: #F5F5F7;
                    --text-primary: #1D1D1F;
                    --text-secondary: #86868B;
                    --background: #FFFFFF;
                    --surface: #FBFBFD;
                    --border: #E5E5E7;
                    --shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                    --shadow-hover: 0 8px 30px rgba(0, 0, 0, 0.12);
                    --border-radius: 12px;
                    --transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                }}
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: var(--text-primary); background: var(--background); }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; min-height: 100vh; display: flex; flex-direction: column; }}
                .header {{ padding: 20px 0; border-bottom: 1px solid var(--border); background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(20px); }}
                .nav {{ display: flex; justify-content: space-between; align-items: center; }}
                .logo-text {{ font-size: 24px; font-weight: 700; letter-spacing: -0.5px; color: var(--primary-color); text-decoration: none; }}
                .nav-links {{ display: flex; gap: 30px; align-items: center; }}
                .nav-link {{ text-decoration: none; color: var(--text-primary); font-weight: 500; transition: var(--transition); padding: 8px 16px; border-radius: 8px; }}
                .nav-link:hover {{ color: var(--primary-color); background: var(--secondary-color); }}
                .language-switcher {{ display: flex; gap: 4px; margin-left: 20px; }}
                .lang-btn {{ padding: 6px 12px; border: 1px solid var(--border); background: var(--background); color: var(--text-secondary); border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 500; transition: var(--transition); }}
                .lang-btn.active {{ background: var(--primary-color); color: white; border-color: var(--primary-color); }}
                .main {{ flex: 1; padding: 40px 0; }}
                .hero-section {{ text-align: center; padding: 60px 0; background: linear-gradient(135deg, var(--surface) 0%, var(--background) 100%); border-radius: var(--border-radius); margin-bottom: 60px; }}
                .hero-title {{ font-size: 48px; font-weight: 700; color: var(--text-primary); margin-bottom: 16px; letter-spacing: -1px; }}
                .hero-subtitle {{ font-size: 20px; color: var(--text-secondary); font-weight: 400; }}
                .blog-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px; margin-bottom: 60px; }}
                .blog-card {{ background: var(--background); border-radius: var(--border-radius); padding: 30px; box-shadow: var(--shadow); transition: var(--transition); border: 1px solid var(--border); }}
                .blog-card:hover {{ box-shadow: var(--shadow-hover); transform: translateY(-2px); }}
                .blog-title {{ font-size: 24px; font-weight: 600; color: var(--text-primary); line-height: 1.3; margin-bottom: 20px; }}
                .blog-quote {{ background: linear-gradient(135deg, var(--primary-color), var(--primary-light)); border-radius: var(--border-radius); padding: 20px; margin-bottom: 20px; }}
                .blog-quote blockquote {{ color: white; font-size: 18px; font-weight: 600; font-style: italic; text-align: center; line-height: 1.4; }}
                .blog-preview {{ margin-bottom: 24px; color: var(--text-secondary); line-height: 1.6; }}
                .blog-footer {{ display: flex; justify-content: flex-end; }}
                .btn {{ display: inline-flex; align-items: center; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 500; font-size: 14px; transition: var(--transition); border: none; cursor: pointer; }}
                .btn-primary {{ background: var(--primary-color); color: white; }}
                .btn-primary:hover {{ background: var(--primary-dark); transform: translateY(-1px); }}
                .footer {{ text-align: center; padding: 40px 0; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 14px; }}
                @media (max-width: 768px) {{ .blog-grid {{ grid-template-columns: 1fr; }} .hero-title {{ font-size: 32px; }} }}
            </style>
        </head>
        <body>
            <div class="container">
                <header class="header">
                    <nav class="nav">
                        <a href="/" class="logo-text">AO生态文章AI总结</a>
                        <div class="nav-links">
                            <a href="/" class="nav-link">首页</a>
                            <a href="https://uia84zzwgf.feishu.cn/share/base/form/shrcnpVCPowqvVVwosqDqMyBBOd" class="nav-link" target="_blank">提交文章</a>
                            <div class="language-switcher">
                                <button onclick="switchLanguage('zh')" class="lang-btn active">中文</button>
                                <button onclick="switchLanguage('en')" class="lang-btn">EN</button>
                            </div>
                        </div>
                    </nav>
                </header>
                
                <main class="main">
                    <div class="hero-section">
                        <h1 class="hero-title">AO生态文章AI总结</h1>
                        <p class="hero-subtitle">探索AO生态的最新动态和深度见解</p>
                    </div>
                    
                    <div class="blog-grid">
                        {''.join([f'''
                        <article class="blog-card">
                            <div class="blog-header">
                                <h2 class="blog-title">{blog["title"]}</h2>
                            </div>
                            {f'<div class="blog-quote"><blockquote>{blog["quote"]}</blockquote></div>' if blog.get("quote") else ''}
                            <div class="blog-preview">
                                <p>{blog["preview"]}</p>
                            </div>
                            <div class="blog-footer">
                                <a href="{blog.get("external_link", "#")}" class="btn btn-primary" target="_blank">阅读全文</a>
                            </div>
                        </article>
                        ''' for blog in blogs])}
                    </div>
                </main>
                
                <footer class="footer">
                    <p>&copy; 2025 AO INSIGHT. 数据来源：飞书多维表格</p>
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
