# Hugging Face Spaces (Docker SDK) 部署文件
# 也可用于任何支持 Dockerfile 的平台（Koyeb/Railway/Fly 等）
FROM python:3.11-slim

WORKDIR /app

# 先装依赖（利用 Docker 层缓存，代码变动不重装依赖）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝全部项目代码（10 个工具 + platform 聚合入口）
COPY . .

# HF Spaces 要求容器监听 7860 端口
EXPOSE 7860

# gunicorn 启动 WSGI 入口 application（DispatcherMiddleware 聚合应用）
# --chdir platform：以 platform 为工作目录，加载 app:application
CMD ["gunicorn", "--chdir", "platform", "--bind", "0.0.0.0:7860", \
     "--workers", "1", "--threads", "4", "--timeout", "180", "app:application"]
