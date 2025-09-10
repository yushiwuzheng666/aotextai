from flask import Flask, render_template, request, jsonify, session
import requests
import json
import time
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from translations import get_text, TRANSLATIONS

app = Flask(__name__, 
           template_folder='../templates',
           static_folder='../static')
app.config.from_object(Config)

class FeishuAPI:
    """飞书API操作类"""
    
    def __init__(self):
        self.app_id = app.config['FEISHU_APP_ID']
        self.app_secret = app.config['FEISHU_APP_SECRET']
        self.base_url = app.config['FEISHU_API_BASE_URL']
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
                # 提前5分钟刷新token
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

def format_blog_data(records):
    """格式化博客数据"""
    blogs = []
    for record in records:
        fields = record.get('fields', {})
        
        # 提取字段数据，处理飞书表格的实际字段名称
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
        
        # 如果数据为"1"，说明是测试数据，使用默认内容
        if title == "1":
            title = f"测试文章 {record.get('record_id', '')[:8]}"
        if quote == "1":
            quote = "这是一句测试金句，用于展示博客的金句功能。"
        if content == "1":
            content = "这是测试文章内容，用于展示博客的完整文章功能。当您在飞书多维表格中添加真实内容后，这里会显示实际的文章内容。"
        
        if title:  # 只有标题不为空才添加
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

@app.route('/')
def index():
    """首页"""
    try:
        lang = get_current_language()
        records = feishu_api.get_records(
            app.config['BASE_ID'], 
            app.config['TABLE_ID']
        )
        blogs = format_blog_data(records)
        
        # 传递翻译文本到模板
        translations = {key: get_text(key, lang) for key in TRANSLATIONS[lang].keys()}
        
        return render_template('index.html', blogs=blogs, lang=lang, t=translations)
    except Exception as e:
        print(f"首页加载异常: {e}")
        lang = get_current_language()
        translations = {key: get_text(key, lang) for key in TRANSLATIONS[lang].keys()}
        error_msg = get_text('loading_error', lang)
        return render_template('index.html', blogs=[], error=error_msg, lang=lang, t=translations)

@app.route('/detail/<record_id>')
def detail(record_id):
    """文章详情页"""
    try:
        lang = get_current_language()
        records = feishu_api.get_records(
            app.config['BASE_ID'], 
            app.config['TABLE_ID']
        )
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
            records = feishu_api.get_records(
                app.config['BASE_ID'], 
                app.config['TABLE_ID']
            )
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

# Vercel需要的handler函数
def handler(request):
    return app(request.environ, lambda status, headers: None)
