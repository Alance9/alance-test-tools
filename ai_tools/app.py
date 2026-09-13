# -*- coding: utf-8 -*-
"""
AI 工具（独立 Flask 子应用）
- 页面内嵌 Coze 发布版测试智能体（分享短链，支持 iframe 嵌入）
- 提供"新标签页登录"与"刷新"按钮，解决未登录时 SSO 登录页
  （signin.volcengine.com，CSP frame-ancestors）无法在 iframe 内打开的问题
"""
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    """渲染 AI 工具主页：顶部工具条 + Coze 智能体内嵌 iframe"""
    return render_template('index.html')


@app.route('/health')
def health():
    """健康检查"""
    return 'ok'


if __name__ == '__main__':
    print('AI 工具启动: http://127.0.0.1:5001')
    app.run(host='0.0.0.0', port=5001, debug=True)
