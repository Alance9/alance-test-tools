# Alance 测试工具平台 —— PythonAnywhere 部署文档

> 适用：免费账户（Beginner），无需信用卡，服务 7×24 在线不休眠。
> 平台架构：`platform/app.py` 用 `DispatcherMiddleware` 将 10 个工具的 Flask app 聚合在一个 WSGI 应用 `application` 上；PythonAnywhere 直接托管该 WSGI 入口。

---

## 一、部署前准备

| 项 | 说明 |
|---|---|
| 账号 | https://www.pythonanywhere.com 注册免费账户（仅需邮箱） |
| 代码 | 本地仓库 `e:\Code\AITest\testTools`，入口 `platform/app.py` |
| 部署配置 | 仓库已内置 `deploy/pythonanywhere_wsgi.py`（WSGI 模板）、`requirements.txt`（依赖清单） |

---

## 二、部署步骤

### 第 1 步：上传代码（二选一）

**方式 A：从 GitHub 克隆**（GitHub 在免费版外网白名单内）

先把代码推到 GitHub 公开仓库，然后在 PythonAnywhere 顶部 **Consoles** → 开 **Bash**：

```bash
cd ~
git clone https://github.com/<你的用户名>/<仓库名>.git alance-test-tools
```

**方式 B：上传 zip**（GitCode 等其他平台不在白名单时用）

1. 本地把 `testTools` 目录打包为 zip
2. PythonAnywhere 顶部 **Files** 页上传 zip
3. Bash 中解压：

```bash
cd ~
unzip ~/上传的文件名.zip
mv 解压出来的目录名 alance-test-tools   # 若目录名不同则重命名
ls ~/alance-test-tools/platform/app.py   # 能列出文件即正确
```

### 第 2 步：确认 Python 版本并安装依赖（关键坑位）

1. 先到 **Web** 标签页（下一步会建 App）或在 Bash 执行 `python3.10 --version` / `python3.11 --version`，确认 Web App 使用的版本号
2. **务必用与 Web App 相同版本的 pip 安装**（Bash 默认的 `pip` 可能对应 3.8，装错版本 Web 应用会 `ModuleNotFoundError`）：

```bash
# 3.10 示例；若 Web App 是 3.11，把所有 3.10 换成 3.11
pip3.10 install --user --upgrade flask pillow pycryptodome qrcode python-barcode openpyxl python-docx py7zr pymupdf faker
```

3. 验证依赖装到了正确的解释器：

```bash
python3.10 -c "import flask, PIL, Crypto, qrcode, barcode, openpyxl, docx, py7zr, fitz, faker; print('deps OK')"
```

输出 `deps OK` 即通过；哪个模块报错就 `pip3.10 install --user <模块名>` 补装。

> 依赖与模块名对照：Pillow→`PIL`、pycryptodome→`Crypto`、python-barcode→`barcode`、python-docx→`docx`、PyMuPDF→`fitz`、Faker→`faker`。

### 第 3 步：创建 Web App

1. 顶部 **Web** 标签 → **Add a new web app** → Next
2. 选 **Manual configuration**（不要选 Flask 模板）→ 选与第 2 步一致的 **Python 3.10**（或 3.11）→ Next

### 第 4 步：配置 WSGI 文件

1. Web 标签页点 **Code** 区的 **WSGI configuration file** 链接（`/var/www/<用户名>_pythonanywhere_com_wsgi.py`）
2. **全选删除**原内容，粘贴如下配置（`<用户名>` 替换为你的 PythonAnywhere 用户名，注意大小写，如 `Alance9`）：

```python
import sys

PROJECT_ROOT = '/home/<用户名>/alance-test-tools'
# platform 目录放最前，使 from app import application 命中 platform/app.py
sys.path.insert(0, PROJECT_ROOT + '/platform')
sys.path.insert(0, PROJECT_ROOT)

# platform/app.py 模块级执行 application = build_app()，
# 即聚合 10 个工具的 DispatcherMiddleware WSGI 应用
from app import application
```

3. 保存。

### 第 5 步：自检并 Reload

**Bash 中模拟 WSGI 导入**（有问题立刻暴露，不用等网页报错）：

```bash
cd ~/alance-test-tools/platform && python3.10 -c "import app; print('import OK')"
```

- 输出 10 行 `[挂载] /t/xxx -> ...` + `import OK` → 代码与依赖正常
- 报错 → 按报错缺啥补啥（多半是依赖未装/版本不对）

然后 **Web 标签页 → 绿色 Reload 按钮**，访问：

```
https://<用户名>.pythonanywhere.com
```

打开后输入邀请码 **alan** 即可使用。

---

## 三、日常运维

| 操作 | 方法 |
|---|---|
| **更新代码** | Bash 中 `cd ~/alance-test-tools && git pull`（zip 方式则重新上传解压覆盖）→ Web 页 **Reload** |
| **改了代码网页没生效** | 必须点 Reload；平台为子应用开启了模板自动重载，但 WSGI 进程级改动仍需 Reload |
| **查看错误日志** | Web 标签页 → **error log** / **server log**，重点看 error log 最后 20 行 |
| **3 个月到期提醒** | 免费 Web App 每 3 个月需登录控制台点一次续期（页面会提示），否则暂停 |
| **Bash 会话过期** | Consoles 页重新开一个 Bash 即可，文件不会丢 |

---

## 四、常见问题排查

| 现象 | 根因 | 解决 |
|---|---|---|
| `ModuleNotFoundError: No module named 'faker'`（或任意模块） | 依赖没装，或 pip 用的 Python 版本与 Web App 不一致 | Web 页确认版本 → `pip3.x install --user <包名>` → `python3.x -c "import ..."` 验证 → Reload |
| 装了依赖仍报 No module named | `pip` 默认指向 3.8 而 Web App 是 3.10/3.11 | 用 `pip3.10` / `pip3.11` 显式安装，勿用裸 `pip` |
| Reload 后 500 / Unhandled Exception | WSGI 路径或配置错误 | 检查 `PROJECT_ROOT` 大小写与实际目录一致；WSGI 文件无残留默认模板内容 |
| Bash 自检 import 报错但网页不报/反之 | 两个 Python 环境不同 | 自检命令也带版本号 `python3.10`，与 Web App 对齐 |
| 生成大文件（100MB）慢或失败 | 免费版单请求时长/内存受限 | 属正常限制，常规小文件与图片处理不受影响 |
| `git clone` 报网络错误 | 目标站点不在免费版白名单 | 改用 Files 页上传 zip 方式 |

**万能排查顺序**：看 error.log 最后一行 → 缺模块就按版本装依赖 → Bash 里 `python3.x -c "import app"` 自检 → Reload。

---

## 五、附：完整依赖清单（requirements.txt）

```
Flask>=3.0
Pillow>=10.0            # 图片处理/图片生成
Faker>=24.0             # 测试数据生成（模块级导入，必装）
pycryptodome>=3.20      # AES/RSA 加解密（Crypto）
qrcode>=7.4             # 二维码
python-barcode>=0.15    # 条形码（barcode）
openpyxl>=3.1           # xlsx 文件生成
python-docx>=1.1        # docx 文件生成（docx）
py7zr>=0.20             # 7z 文件生成
PyMuPDF>=1.24           # PDF 转图片（fitz）
gunicorn>=21.2          # 仅 Render/Koyeb 等平台用，PythonAnywhere 不需要
```
