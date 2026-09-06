---
title: Alance Test Tools
emoji: 🛠️
colorFrom: gray
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Alance 测试工具平台

单端口聚合 10 个测试工具的 Flask 平台：文本处理、日志分析、测试数据生成、测试文件生成、数据格式转换、图片处理、加解密处理、存过造数、Python 造数、API 造数。

## 本地运行

```bash
pip install -r requirements.txt
python platform/app.py
# 访问 http://127.0.0.1:5000
```

## 生产部署

- WSGI 入口：`platform/app.py` 中的 `application`（werkzeug DispatcherMiddleware）
- 启动：`gunicorn --chdir platform --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 180 app:application`
- 健康检查：`/health`
