# -*- coding: utf-8 -*-
"""
Alance 测试工具平台
将 10 个独立 Flask 工具合并到单端口运行：
- 根路径 / 渲染平台主页面（顶部 header + 左侧菜单 + 右侧 iframe）
- 每个工具通过 DispatcherMiddleware 挂载到 /t/<key>/ 前缀下
- 模板内 API 请求使用相对路径（'api/...'），独立运行与平台挂载均兼容
"""
import os
import sys
import importlib.util

from flask import Flask, render_template, send_from_directory
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# 工作区根目录（platform 的上一级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 菜单项：(挂载key, 工具目录名, 菜单显示名)，顺序即左侧菜单顺序
TOOLS = [
    ('text',    'font_beauty',        '文本处理'),
    ('log',     'log_analyze',        '日志分析'),
    ('data',    'test_data',          '测试数据生成'),
    ('file',    'file_generator_tool','测试文件生成'),
    ('convert', 'data_converter',     '数据格式转换'),
    ('image',   'image_processor',    '图片处理'),
    ('crypto',  'crypto_tools',       '加解密处理'),
    ('sql',     'sql_generator',      '存过造数'),
    ('pygen',   'python_generator',   'Python 造数'),
    ('apigen',  'api_generator',      'API 造数'),
]

# 分组主菜单：主菜单可展开/收起，子项仍是挂载在 /t/<key>/ 的内部工具。
# children: (挂载key, 工具目录名, 子菜单显示名)
TOOL_GROUPS = [
    {
        'name': 'AI 工具',
        'children': [
            ('ai', 'ai_tools', '测试智能体'),
        ],
    },
]


def load_tool_app(key, dirname):
    """以唯一模块名动态加载单个工具的 app.py，返回其 Flask 实例。

    注册到 sys.modules 后再 exec，保证 Flask(__name__) 能通过
    模块 __file__ 定位到工具目录（templates 根路径正确）。
    """
    tool_dir = os.path.join(BASE_DIR, dirname)
    app_path = os.path.join(tool_dir, 'app.py')
    mod_name = 'alance_tool_' + key
    spec = importlib.util.spec_from_file_location(mod_name, app_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module          # 先注册，Flask 才能找到模块
    if tool_dir not in sys.path:
        sys.path.insert(0, tool_dir)        # 工具目录加入模块搜索路径
    spec.loader.exec_module(module)
    # 子应用以模块方式加载时 debug=False，Jinja 默认缓存模板；
    # 显式开启自动重载，保证修改工具模板后无需重启即可生效
    module.app.config['TEMPLATES_AUTO_RELOAD'] = True
    module.app.jinja_env.auto_reload = True
    return module.app


# 平台根应用（主页面）
root_app = Flask(__name__)
root_app.config['TEMPLATES_AUTO_RELOAD'] = True
root_app.jinja_env.auto_reload = True


@root_app.route('/')
def index():
    """渲染平台主页面：header + 左侧菜单 + 右侧 iframe 功能区

    菜单 = 普通工具（{key,name}）+ 分组主菜单（{name,children:[{key,name}]}）
    """
    menu = [{'key': k, 'name': n} for k, _, n in TOOLS]
    for group in TOOL_GROUPS:
        menu.append({
            'name': group['name'],
            'children': [{'key': k, 'name': n} for k, _, n in group['children']],
        })
    return render_template('index.html', menu=menu)


@root_app.route('/health')
def health():
    """健康检查"""
    return 'ok'


# 平台静态资源目录（存放 favicon 等）
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


@root_app.route('/favicon.ico')
def favicon_ico():
    """返回浏览器标签页图标（.ico，多尺寸）"""
    return send_from_directory(STATIC_DIR, 'favicon.ico', mimetype='image/x-icon')


@root_app.route('/favicon.png')
def favicon_png():
    """返回浏览器标签页图标（.png，高清）"""
    return send_from_directory(STATIC_DIR, 'favicon.png', mimetype='image/png')


def build_app():
    """加载全部工具（普通工具 + 分组菜单的子工具）并构建合并应用"""
    mounts = {}

    def mount(key, dirname, name):
        """加载并挂载单个工具到 /t/<key>/"""
        sub_app = load_tool_app(key, dirname)
        mounts['/t/' + key] = sub_app
        print(f'[挂载] /t/{key:<8} -> {dirname:<20} {name}')

    for key, dirname, name in TOOLS:
        mount(key, dirname, name)
    for group in TOOL_GROUPS:
        for key, dirname, name in group['children']:
            mount(key, dirname, name)
    return DispatcherMiddleware(root_app, mounts)


application = build_app()


if __name__ == '__main__':
    print('Alance 测试工具平台启动: http://127.0.0.1:5000')
    run_simple('0.0.0.0', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)
