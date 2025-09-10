import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 飞书应用配置
    FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID') or "cli_a8341be1df7f901c"
    FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET') or "bLbLrrlOJjQCRXcSruTbshbd8fgPOms0"
    
    # 多维表格配置
    BASE_ID = os.environ.get('BASE_ID') or "Ff4vb1pI5aLIh2s41mgcphRCnJh"
    TABLE_ID = os.environ.get('TABLE_ID') or "tbl4YNGcNh3Qhepi"
    
    # 飞书API相关配置
    FEISHU_API_BASE_URL = "https://open.feishu.cn/open-apis"
    
    # 缓存配置
    CACHE_TIMEOUT = 300  # 5分钟缓存
    
    # 分页配置
    POSTS_PER_PAGE = 10
