# -*- coding: utf-8 -*-
"""
Playwright Auto 文档查看工具（独立 Flask 子应用）
- 分组菜单「Playwright Auto」下挂两个子项，共用本工具目录：
  · pw_pom  -> POM 分层设计
  · pw_life -> 框架生命周期
- 通过 request.script_root 区分加载不同 Markdown 文档并渲染
"""
import os

from flask import Flask, render_template, request, abort

app = Flask(__name__)

# 工具根目录（本 app.py 所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 本地文档目录候选（按顺序查找，找到即用）
LOCAL_DOCS_DIRS = [
    os.path.join(BASE_DIR, 'doc'),
    os.path.join(BASE_DIR, 'docs'),
]
# 回退文档目录（用户原始 MD 存放位置）
FALLBACK_DOCS_DIR = r'C:\Users\Z\Downloads'

# 挂载 key -> (MD 文件名, 页面标题)
DOC_MAP = {
    'pw_pom':  ('框架生命周期.md', '框架生命周期'),
    'pw_life': ('POM分层设计.md', 'POM 分层设计'),
}


def _find_local(filename):
    """在候选本地文档目录中查找文件，找到返回绝对路径，否则 None。"""
    for d in LOCAL_DOCS_DIRS:
        p = os.path.join(d, filename)
        if os.path.isfile(p):
            return p
    return None


def read_doc(key):
    """根据挂载 key 读取对应 MD 内容；本地 doc/ 优先，找不到则回退 Downloads。"""
    info = DOC_MAP.get(key)
    if not info:
        abort(404)
    filename, title = info
    # 本地优先
    local_path = _find_local(filename)
    if local_path:
        with open(local_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return title, content
    # 回退到用户原始 Downloads 目录
    fb_path = os.path.join(FALLBACK_DOCS_DIR, filename)
    if os.path.isfile(fb_path):
        with open(fb_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return title, content
    return title, '（未找到文档：%s）' % filename


@app.route('/')
def index():
    """根据当前挂载路径的 key 渲染对应 MD 文档。"""
    # 平台挂载时 script_root 为 /t/pw_pom 或 /t/pw_life
    script_root = (request.script_root or '').rstrip('/')
    key = script_root.rsplit('/', 1)[-1] if script_root else ''
    # 独立运行时无法区分子项，默认展示 POM
    if key not in DOC_MAP:
        key = 'pw_pom'
    title, md_content = read_doc(key)
    return render_template('index.html', title=title, md_content=md_content)


@app.route('/health')
def health():
    """健康检查"""
    return 'ok'


if __name__ == '__main__':
    print('Playwright Auto 文档工具启动: http://127.0.0.1:5002')
    app.run(host='0.0.0.0', port=5002, debug=True)
