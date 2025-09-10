from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'AO生态文章AI总结网站 - API正常运行',
        'version': '1.0.0'
    })

@app.route('/api/test')
def test_api():
    return jsonify({
        'status': 'success',
        'message': 'API测试成功',
        'env_vars': {
            'FEISHU_APP_ID': bool(os.environ.get('FEISHU_APP_ID')),
            'FEISHU_APP_SECRET': bool(os.environ.get('FEISHU_APP_SECRET')),
            'BASE_ID': bool(os.environ.get('BASE_ID')),
            'TABLE_ID': bool(os.environ.get('TABLE_ID'))
        }
    })

# Vercel导出
if __name__ == '__main__':
    app.run(debug=True)
