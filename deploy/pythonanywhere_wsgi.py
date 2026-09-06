# -*- coding: utf-8 -*-
"""
PythonAnywhere WSGI 配置模板（免费账户，无需信用卡，服务不休眠）

部署步骤：
1. 注册 https://www.pythonanywhere.com （Beginner 免费账户，不要信用卡）
2. 把代码放到服务器 home 目录（任选一种）：
   a. Bash console 中克隆（GitHub 公开仓库在免费版外网白名单内）：
        cd ~ && git clone https://github.com/<你的用户名>/alance-test-tools.git
   b. 或在 Files 标签页上传项目 zip，Bash 中执行：unzip 上传的文件.zip
3. Bash console 安装依赖：
     pip install --user pillow pycryptodome qrcode python-barcode openpyxl python-docx py7zr pymupdf
4. Web 标签页 -> Add a new web app -> Manual configuration -> Python 3.10/3.11
5. 点开生成的 /var/www/<用户名>_pythonanywhere_com_wsgi.py，
   用下面"实际配置"部分替换全部内容（<用户名> 改为你的 PythonAnywhere 用户名，
   目录名按实际修改）
6. Web 标签页点 Reload，访问 https://<用户名>.pythonanywhere.com

注意：
- 免费 Web App 每 3 个月需登录控制台点一次续期（页面会提示）
- 免费环境内存/请求时长有限，100MB 大文件生成可能较慢或失败，常规功能不受影响
"""

# ==================== 实际配置（复制到 WSGI 文件中） ====================
import sys

# 项目根目录（按实际目录名修改）
PROJECT_ROOT = '/home/<用户名>/alance-test-tools'

# platform 目录放在最前，使 `from app import application` 命中 platform/app.py
sys.path.insert(0, PROJECT_ROOT + '/platform')
sys.path.insert(0, PROJECT_ROOT)

# platform/app.py 在模块级执行 application = build_app()，
# 即 DispatcherMiddleware 聚合的 10 个工具 WSGI 应用，PythonAnywhere 直接托管
from app import application  # noqa: E402,F401
