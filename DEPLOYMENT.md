# Vercel 部署指南

## 部署步骤

### 1. 准备工作
确保您的项目已经推送到 GitHub 仓库。

### 2. 在 Vercel 中创建项目
1. 访问 [Vercel](https://vercel.com)
2. 点击 "New Project"
3. 导入您的 GitHub 仓库
4. 选择 Framework Preset: "Other"

### 3. 配置环境变量
在 Vercel 项目设置中添加以下环境变量：

```
FEISHU_APP_ID=cli_a8341be1df7f901c
FEISHU_APP_SECRET=bLbLrrlOJjQCRXcSruTbshbd8fgPOms0
BASE_ID=Ff4vb1pI5aLIh2s41mgcphRCnJh
TABLE_ID=tbl4YNGcNh3Qhepi
SECRET_KEY=your-production-secret-key
```

### 4. 部署
点击 "Deploy" 按钮，Vercel 会自动构建和部署您的应用。

## 项目结构说明

```
ai-windlearn/
├── api/
│   └── index.py          # Vercel 入口文件
├── static/
│   └── css/
│       └── style.css     # 样式文件
├── templates/
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页模板
│   └── detail.html       # 详情页模板
├── config.py             # 配置文件
├── translations.py       # 多语言配置
├── requirements.txt      # Python 依赖
├── vercel.json          # Vercel 配置
└── README.md            # 项目说明
```

## 注意事项

1. **环境变量安全**: 不要在代码中硬编码敏感信息，使用 Vercel 的环境变量功能
2. **静态文件**: CSS 和 JS 文件通过 `/static/` 路径访问
3. **会话管理**: Vercel 的 serverless 特性可能影响 Flask session，建议使用外部存储
4. **冷启动**: 首次访问可能较慢，这是 serverless 的正常现象

## 故障排除

### 常见问题
1. **500 错误**: 检查环境变量是否正确配置
2. **静态文件 404**: 确认 `vercel.json` 中的路由配置
3. **飞书 API 错误**: 验证 App ID 和 Secret 是否有效

### 调试方法
1. 查看 Vercel 部署日志
2. 使用 `/api/test` 端点测试 API 连接
3. 检查浏览器开发者工具的网络请求

## 更新部署
推送代码到 GitHub 主分支，Vercel 会自动重新部署。
