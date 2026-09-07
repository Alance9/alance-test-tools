"""测试文件生成工具后端"""
from flask import Flask, render_template, request, jsonify, Response
from PIL import Image
import io
import base64
import os
import json


app = Flask(__name__)


# ========== 配置文件示例 ==========
CONFIG_EXAMPLES = {
    'json': r'''{
    "app": {
        "name": "TestApp",
        "version": "1.0.0",
        "description": "测试应用配置",
        "debug": true
    },
    "database": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "123456",
        "database": "test_db",
        "pool_size": 10,
        "timeout": 30
    },
    "redis": {
        "host": "localhost",
        "port": 6379,
        "password": "",
        "db": 0
    },
    "server": {
        "host": "0.0.0.0",
        "port": 8080,
        "workers": 4,
        "max_requests": 10000
    },
    "logging": {
        "level": "INFO",
        "file": "/var/log/app.log",
        "max_size": "100MB",
        "backup_count": 10
    },
    "features": {
        "enable_cache": true,
        "enable_compression": true,
        "enable_ssl": false,
        "cors_origins": ["http://localhost:3000", "http://localhost:8080"]
    }
}''',
    'yaml': r'''# 应用配置文件
app:
  name: TestApp
  version: 1.0.0
  description: 测试应用配置
  debug: true

database:
  host: localhost
  port: 3306
  user: root
  password: "123456"
  database: test_db
  pool_size: 10
  timeout: 30

redis:
  host: localhost
  port: 6379
  password: ""
  db: 0

server:
  host: 0.0.0.0
  port: 8080
  workers: 4
  max_requests: 10000

logging:
  level: INFO
  file: /var/log/app.log
  max_size: 100MB
  backup_count: 10

features:
  enable_cache: true
  enable_compression: true
  enable_ssl: false
  cors_origins:
    - http://localhost:3000
    - http://localhost:8080''',
    'ini': r'''[app]
name = TestApp
version = 1.0.0
description = 测试应用配置
debug = true

[database]
host = localhost
port = 3306
user = root
password = 123456
database = test_db
pool_size = 10
timeout = 30

[redis]
host = localhost
port = 6379
password =
db = 0

[server]
host = 0.0.0.0
port = 8080
workers = 4
max_requests = 10000

[logging]
level = INFO
file = /var/log/app.log
max_size = 100MB
backup_count = 10

[features]
enable_cache = true
enable_compression = true
enable_ssl = false
cors_origins = http://localhost:3000, http://localhost:8080''',
    'xml': r'''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <app name="TestApp" version="1.0.0" debug="true">
        <description>测试应用配置</description>
    </app>
    <database host="localhost" port="3306">
        <user>root</user>
        <password>123456</password>
        <name>test_db</name>
        <pool_size>10</pool_size>
        <timeout>30</timeout>
    </database>
    <redis host="localhost" port="6379">
        <password></password>
        <db>0</db>
    </redis>
    <server host="0.0.0.0" port="8080">
        <workers>4</workers>
        <max_requests>10000</max_requests>
    </server>
    <logging level="INFO">
        <file>/var/log/app.log</file>
        <max_size>100MB</max_size>
        <backup_count>10</backup_count>
    </logging>
    <features>
        <enable_cache>true</enable_cache>
        <enable_compression>true</enable_compression>
        <enable_ssl>false</enable_ssl>
        <cors_origins>
            <origin>http://localhost:3000</origin>
            <origin>http://localhost:8080</origin>
        </cors_origins>
    </features>
</configuration>''',
    'sh': r'''#!/bin/bash
# =============================================
# 应用启动脚本
# =============================================

export APP_NAME="TestApp"
export APP_PORT=8080
export DB_HOST="localhost"
export DB_PORT=3306

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========== 启动 ${APP_NAME} ==========${NC}"

check_dependencies() {
    echo -e "${YELLOW}检查依赖...${NC}"
    command -v python3 >/dev/null 2>&1 || { echo -e "${RED}python3 未安装${NC}"; exit 1; }
    command -v mysql >/dev/null 2>&1 || { echo -e "${YELLOW}mysql 未安装（可选）${NC}"; }
    echo -e "${GREEN}依赖检查通过${NC}"
}

init_database() {
    echo -e "${YELLOW}初始化数据库...${NC}"
    mysql -h ${DB_HOST} -P ${DB_PORT} -u root -p123456 -e "CREATE DATABASE IF NOT EXISTS test_db DEFAULT CHARSET utf8mb4;"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}数据库初始化成功${NC}"
    else
        echo -e "${RED}数据库初始化失败${NC}"
        exit 1
    fi
}

start_app() {
    echo -e "${YELLOW}启动应用...${NC}"
    cd "$(dirname "$0")"
    nohup python3 app.py > /var/log/app.log 2>&1 &
    APP_PID=$!
    echo -e "${GREEN}应用已启动, PID: ${APP_PID}${NC}"
    echo ${APP_PID} > app.pid
}

stop_app() {
    echo -e "${YELLOW}停止应用...${NC}"
    if [ -f app.pid ]; then
        kill $(cat app.pid) && rm app.pid
        echo -e "${GREEN}应用已停止${NC}"
    else
        echo -e "${YELLOW}未找到 app.pid${NC}"
        pkill -f "python3 app.py"
    fi
}

status_app() {
    if [ -f app.pid ] && kill -0 $(cat app.pid) 2>/dev/null; then
        echo -e "${GREEN}应用运行中, PID: $(cat app.pid)${NC}"
    else
        echo -e "${RED}应用未运行${NC}"
    fi
}

case "$1" in
    start) check_dependencies; init_database; start_app ;;
    stop) stop_app ;;
    restart) stop_app; sleep 2; start_app ;;
    status) status_app ;;
    *) echo "Usage: $0 {start|stop|restart|status}"; exit 1 ;;
esac''',
    'groovy': r'''// =============================================
// Jenkins Pipeline：UI 自动化测试（Python + Selenium）
// 流程：拉取代码 → 构建环境 → 运行自动化 → Allure 报告 → 多邮箱通知
// =============================================

pipeline {
    agent any

    environment {
        // 项目与测试配置
        PROJECT_NAME   = 'WebAutoTest'
        PYTHON_VERSION = 'python3.10'
        TEST_DIR       = 'tests'
        ALLURE_DIR     = 'allure-results'
        ALLURE_REPORT  = 'allure-report'
        // 收件人列表（用逗号分隔）
        MAIL_TO        = 'tester1@example.com,tester2@example.com,leader@example.com'
    }

    options {
        timestamps()                          // 控制台输出带时间戳
        timeout(time: 60, unit: 'MINUTES')    // 整体超时 60 分钟
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    stages {

        // 1. 拉取代码
        stage('拉取代码 Checkout') {
            steps {
                echo "====== 拉取代码（分支: ${env.BRANCH_NAME}）======"
                checkout scm
                sh 'git log --oneline -5'
            }
        }

        // 2. 构建环境（Python 虚拟环境 + 依赖）
        stage('构建环境 Setup') {
            steps {
                echo '====== 构建 Python 环境 ======'
                sh """
                    ${PYTHON_VERSION} -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install selenium pytest allure-pytest
                    python -c "import selenium; print('selenium', selenium.__version__)"
                """
            }
        }

        // 3. 运行 Python + Selenium 自动化脚本
        // catchError：测试失败不中断流水线，后续 Allure + 邮件阶段仍执行
        stage('运行自动化 Run Tests') {
            steps {
                echo '====== 运行 Selenium 自动化测试 ======'
                catchError(buildResult: 'FAILURE', stageResult: 'UNSTABLE', message: '自动化测试执行失败') {
                    sh """
                        . venv/bin/activate
                        mkdir -p ${ALLURE_DIR}
                        pytest ${TEST_DIR} -s -q \
                            --alluredir=${ALLURE_DIR} \
                            --clean-alluredir \
                            -v
                    """
                }
            }
            post {
                always {
                    // 收集 pytest 的 junit 结果供 Jenkins 展示
                    junit allowEmptyResults: true, testResults: '**/junit-*.xml'
                }
            }
        }

        // 4. 生成 Allure 报告（成功/失败都生成，便于排查）
        stage('生成 Allure 报告') {
            steps {
                echo '====== 生成 Allure 测试报告 ======'
                catchError(buildResult: 'FAILURE', stageResult: 'UNSTABLE', message: 'Allure 报告生成失败') {
                    sh """
                        # 生成静态报告
                        allure generate ${ALLURE_DIR} -o ${ALLURE_REPORT} --clean
                        # 打包报告便于发送
                        zip -r allure-report.zip ${ALLURE_REPORT}
                        echo "报告目录: ${WORKSPACE}/${ALLURE_REPORT}"
                    """
                    // 在 Jenkins 中发布 Allure 报告（需安装 Allure Jenkins Plugin）
                    allure includeProperties: false,
                           jdk: '',
                           results: [[path: '${ALLURE_DIR}']]
                }
            }
        }

        // 5. 发送报告到多个邮箱（成功/失败都发送）
        stage('邮件通知 Notify') {
            steps {
                echo "====== 发送报告到: ${MAIL_TO} ======"
                script {
                    def status = currentBuild.currentResult  // SUCCESS / FAILURE / UNSTABLE
                    emailext (
                        subject: "[${PROJECT_NAME}][${status}] 自动化测试报告 - 构建 #${BUILD_NUMBER}",
                        body: """
                            <h3>自动化测试执行结果</h3>
                            <p>项目: ${PROJECT_NAME}</p>
                            <p>状态: <b>${status}</b></p>
                            <p>构建编号: #${BUILD_NUMBER}</p>
                            <p>分支: ${env.BRANCH_NAME}</p>
                            <p>触发人: ${env.BUILD_USER_ID}</p>
                            <p>Allure 报告: <a href="${BUILD_URL}allure/">查看在线报告</a></p>
                            <p>详细日志: <a href="${BUILD_URL}console">Console Output</a></p>
                            <hr/>
                            <p>此邮件由 Jenkins 自动发送，请勿回复。</p>
                        """,
                        to: "${MAIL_TO}",
                        attachLog: true,
                        attachmentsPattern: 'allure-report.zip',
                        mimeType: 'text/html'
                    )
                }
            }
        }
    }

    post {
        success { echo '✅ 流水线执行成功' }
        failure { echo '❌ 流水线执行失败（Allure 报告与邮件已发送）' }
        always {
            echo '====== 清理工作空间 ======'
            sh 'rm -rf venv __pycache__ .pytest_cache'
        }
    }
}
''',
    'jmeter': r'''// =============================================
// Groovy 在 JMeter 中的常用语法示例
// 适用场景：JSR223 Sampler / PreProcessor / PostProcessor
// 常用内置变量：prev / vars / props / log / ctx / sampler / data
// =============================================

// ========== 1. 变量读写（vars） ==========
// vars：当前线程局部变量（String 存取），跨组件传参的核心
vars.put('token', 'abc123')                     // 存字符串
vars.put('count', '100')                        // 数字也要转字符串存
def token = vars.get('token')                   // 取字符串
def count = vars.get('count') as int            // 取并转 int
vars.putObject('userList', [1, 2, 3])           // 存对象（List/Map 等）
def list = vars.getObject('userList')           // 取对象

// ========== 2. 全局属性读写（props） ==========
// props：JMeter 全局属性，跨线程组共享
props.put('global_token', 'xyz789')             // 存全局属性
def globalToken = props.get('global_token')     // 取全局属性
def threads = props.get('num_threads', '10')    // 带默认值取值

// ========== 3. 获取响应内容与响应时间（prev） ==========
// prev：上一个取样器的 SampleResult 对象
def responseCode    = prev.getResponseCode()          // 响应码，如 '200'
def responseMsg     = prev.getResponseMessage()       // 响应消息
def responseData    = prev.getResponseDataAsString()  // 响应体（字符串）
def responseTime    = prev.getTime()                  // 接口响应时间（毫秒）
def latency         = prev.getLatency()               // 延迟时间（首字节时间）
def bodySize        = prev.getBodySizeAsLong()        // 响应体大小（字节）
def isSuccess       = prev.isSuccessful()             // 请求是否成功
def responseHeaders = prev.getResponseHeaders()       // 响应头

// 根据响应时间判断是否通过
if (responseTime > 3000) {
    prev.setSuccessful(false)
    prev.setResponseMessage('响应超时：' + responseTime + 'ms')
}

// ========== 4. 提取 JSON 响应字段 ==========
import groovy.json.JsonSlurper
def json = new JsonSlurper().parseText(responseData)
def userId = json.data.userId                    // 取嵌套字段
def items  = json.data.items                     // 取数组
def firstId = items[0].id                        // 取数组首元素字段
vars.put('userId', userId.toString())            // 存入变量供后续请求使用

// ========== 5. 正则提取响应内容 ==========
import java.util.regex.Pattern
def matcher = (responseData =~ /"order_id":"(\d+)"/)
if (matcher.find()) {
    def orderId = matcher.group(1)
    vars.put('orderId', orderId)
    log.info('提取到 orderId: ' + orderId)
}

// ========== 6. 传参：构造下一个请求的参数 ==========
// 方式一：存到 vars，下一个 HTTP 请求用 ${varName} 引用
vars.put('nextUserId', userId.toString())

// 方式二：直接修改当前取样器参数（PreProcessor 中）
sampler.addArgument('userId', userId.toString())   // 表单参数
sampler.addArgument('token', token)

// 方式三：修改 HTTP 请求头
import org.apache.jmeter.protocol.http.control.Header
sampler.getHeaderManager().add(new Header('Authorization', 'Bearer ' + token))

// ========== 7. 日志输出（log） ==========
log.info('普通信息日志')
log.warn('警告日志')
log.error('错误日志')
log.debug('调试日志：responseTime = ' + responseTime + 'ms')

// ========== 8. 上下文 ctx（线程上下文） ==========
def threadNum    = ctx.getThreadNum()                // 当前线程编号（0 开始）
def threadName   = ctx.getThread().getThreadName()   // 线程名
def samplerName  = ctx.getCurrentSampler().getName()
def isFirstThread = (threadNum == 0)                 // 是否第一个线程

// ========== 9. 时间相关 ==========
def now       = System.currentTimeMillis()            // 当前时间戳（毫秒）
def date      = new Date().format('yyyy-MM-dd HH:mm:ss') // 格式化时间
def startTime = prev.getStartTime()                   // 请求开始时间戳
def endTime   = prev.getEndTime()                     // 请求结束时间戳

// ========== 10. 常用工具：生成随机数据 ==========
import org.apache.commons.lang3.RandomUtils
import org.apache.commons.lang3.RandomStringUtils
def randomInt = RandomUtils.nextInt(1, 100)                    // 1~99 随机整数
def randomStr = RandomStringUtils.randomAlphanumeric(8)        // 8 位随机字母数字
vars.put('randomInt', randomInt.toString())
vars.put('randomStr', randomStr)

// ========== 11. 完整示例：登录后提取 token 并传给后续请求 ==========
// 【JSR223 PostProcessor】放在登录请求下
try {
    def resp = prev.getResponseDataAsString()
    def obj  = new JsonSlurper().parseText(resp)

    if (obj.code == 0 && obj.data?.token) {
        vars.put('TOKEN', obj.data.token)
        log.info('登录成功，token 已保存: ' + obj.data.token)
    } else {
        prev.setSuccessful(false)
        prev.setResponseMessage('登录失败: ' + (obj.msg ?: '未知错误'))
        log.error('登录失败，响应: ' + resp)
    }
} catch (Exception e) {
    prev.setSuccessful(false)
    prev.setResponseMessage('解析响应异常: ' + e.getMessage())
    log.error('解析异常', e)
}

// ========== 12. 完整示例：统计接口响应时间并设阈值断言 ==========
// 【JSR223 Assertion】
def threshold = 2000  // 阈值 2 秒
def rt = prev.getTime()
if (rt > threshold) {
    AssertionResult.setFailure(true)
    AssertionResult.setFailureMessage('响应时间 ' + rt + 'ms 超过阈值 ' + threshold + 'ms')
}
''',
}


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/image/generate', methods=['POST'])
def image_generate():
    """生成指定尺寸的测试图片（最大 5000x5000）"""
    try:
        import random
        from PIL import ImageDraw
        data = request.json
        width = min(5000, max(1, int(data.get('width', 800))))
        height = min(5000, max(1, int(data.get('height', 600))))
        fmt = data.get('format', 'JPEG').upper()
        color = data.get('color', 'random')

        if color == 'random':
            img = Image.new('RGB', (width, height), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            draw = ImageDraw.Draw(img)
            for _ in range(50):
                x1, x2 = sorted([random.randint(0, width), random.randint(0, width)])
                y1, y2 = sorted([random.randint(0, height), random.randint(0, height)])
                c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                draw.rectangle([x1, y1, x2, y2], fill=c)
            draw.text((10, 10), f'{width}x{height} {fmt}', fill='white')
        else:
            img = Image.new('RGB', (width, height), tuple(int(c) for c in color.split(',')))

        if fmt == 'JPG':
            fmt = 'JPEG'
        if fmt in ('JPEG', 'GIF') and img.mode != 'RGB':
            img = img.convert('RGB')

        buf = io.BytesIO()
        img.save(buf, format=fmt)
        raw = buf.getvalue()
        actual_kb = round(len(raw) / 1024, 1)
        return jsonify({'success': True, 'image': base64.b64encode(raw).decode(), 'format': fmt.lower(), 'actual_kb': actual_kb})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


def pad_zip_to_size(zip_bytes, target_bytes):
    """向 zip/xlsx/docx 容器追加 STORED 填充条目，使总字节数精确等于 target_bytes（不截断）"""
    import zipfile
    if len(zip_bytes) >= target_bytes:
        return zip_bytes
    name = 'padding.bin'
    # 探针：追加同名小条目，测量该条目带来的固定字节开销（与条目数量、名称长度相关）
    probe = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(probe, 'a', zipfile.ZIP_STORED) as zf:
        zf.writestr(name, b'\0' * 100)
    overhead = len(probe.getvalue()) - len(zip_bytes) - 100
    pad = target_bytes - len(zip_bytes) - overhead

    out = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(out, 'a', zipfile.ZIP_STORED) as zf:
        zf.writestr(name, os.urandom(max(0, pad)))
    result = out.getvalue()

    # 偏差兜底：若仍不足且还能再容纳一个条目，则精确补一次（永远不截断，保证 EOCD 完整）
    diff = target_bytes - len(result)
    if diff > overhead:
        with zipfile.ZipFile(out, 'a', zipfile.ZIP_STORED) as zf:
            zf.writestr(name, os.urandom(diff - overhead))
        result = out.getvalue()
    return result


@app.route('/api/file/generate', methods=['POST'])
def file_generate():
    """生成指定大小的测试文件（大小精确），支持 xlsx/docx/pdf/zip/7z/rar"""
    try:
        import random
        import string
        import tempfile
        import zipfile
        data = request.json
        size_mb = float(data.get('size_mb', 10))
        size_mb = min(100, max(0.01, size_mb))  # 最大 100MB
        fmt = data.get('format', 'zip').lower()
        target = int(size_mb * 1024 * 1024)

        mime_map = {
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'pdf':  'application/pdf',
            'zip':  'application/zip',
            '7z':   'application/x-7z-compressed',
            'rar':  'application/x-rar-compressed',
        }

        if fmt == 'zip':
            # zip：随机数据用 STORED 存储，再用填充条目精确补齐
            out = io.BytesIO()
            with zipfile.ZipFile(out, 'w', zipfile.ZIP_STORED) as zf:
                zf.writestr('data.bin', os.urandom(max(0, target - 4096)))
            raw = pad_zip_to_size(out.getvalue(), target)

        elif fmt == 'rar':
            # rar 写入依赖外部命令，此处生成精确大小的二进制占位文件
            raw = os.urandom(target)

        elif fmt == '7z':
            try:
                import py7zr
                # 迭代调整内部数据大小（随机数据压缩率约等于 1:1）
                inner_size = max(0, target - 4096)
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.bin')
                try:
                    tmp.write(os.urandom(inner_size))
                    tmp.close()
                    raw = b''
                    for _ in range(6):
                        buf = io.BytesIO()
                        with py7zr.SevenZipFile(buf, 'w') as z:
                            z.write(tmp.name, arcname='data.bin')
                        raw = buf.getvalue()
                        diff = target - len(raw)
                        # 偏小且偏差很小时接受，偏大则缩小内部数据后重试
                        if 0 <= diff <= 256:
                            break
                        inner_size = max(0, inner_size + diff)
                        with open(tmp.name, 'wb') as f:
                            f.write(os.urandom(inner_size))
                    # 尾部补随机字节兜底（7z 头在文件首部，尾部填充不影响读取）
                    if len(raw) < target:
                        raw += os.urandom(target - len(raw))
                finally:
                    try: os.unlink(tmp.name)
                    except: pass
            except ImportError:
                return jsonify({'success': False, 'error': '缺少 py7zr 依赖，请 pip install py7zr'}), 400

        elif fmt == 'xlsx':
            try:
                from openpyxl import Workbook
                wb = Workbook()
                ws = wb.active
                ws.append(['id', 'name', 'value', 'remark'])
                for i in range(100):
                    ws.append([i, f'item_{i}', random.randint(1, 99999), 'test data row'])
                buf = io.BytesIO()
                wb.save(buf)
                raw = pad_zip_to_size(buf.getvalue(), target)
            except ImportError:
                return jsonify({'success': False, 'error': '缺少 openpyxl 依赖，请 pip install openpyxl'}), 400

        elif fmt == 'docx':
            try:
                from docx import Document
                doc = Document()
                doc.add_paragraph('测试文档 - Test File')
                doc.add_paragraph(''.join(random.choices(string.ascii_letters + string.digits + ' ', k=500)))
                buf = io.BytesIO()
                doc.save(buf)
                raw = pad_zip_to_size(buf.getvalue(), target)
            except ImportError:
                return jsonify({'success': False, 'error': '缺少 python-docx 依赖，请 pip install python-docx'}), 400

        elif fmt == 'pdf':
            # 先生成基础 PDF，再以 PDF 注释形式在 %%EOF 后精确填充
            pdf = (b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n'
                   b'2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n'
                   b'3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>>endobj\n'
                   b'4 0 obj<</Length 44>>stream\nBT /F1 24 Tf 72 720 Td (Test File) Tj ET\nendstream endobj\n'
                   b'xref\n0 5\ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n0\n%%EOF\n')
            if len(pdf) < target:
                # PDF 注释行（% 开头），追加在 %%EOF 之后，字节精确
                pdf += b'% ' + b'A' * (target - len(pdf) - 2) + b'\n'
            raw = pdf[:target]

        else:
            raw = os.urandom(target)

        return Response(raw, mimetype=mime_map.get(fmt, 'application/octet-stream'),
                        headers={'Content-Disposition': f'attachment; filename=test_file.{fmt}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/config/example', methods=['GET'])
def get_config_example():
    """获取配置文件示例"""
    fmt = request.args.get('format', 'json')
    return jsonify({'success': True, 'content': CONFIG_EXAMPLES.get(fmt, '')})


@app.route('/api/config/download', methods=['POST'])
def config_download():
    """下载配置文件"""
    try:
        data = request.json
        fmt = data.get('format', 'json')
        content = CONFIG_EXAMPLES.get(fmt, '')
        mime_map = {'json': 'application/json', 'yaml': 'text/yaml', 'yml': 'text/yaml', 'ini': 'text/plain', 'xml': 'application/xml', 'sh': 'text/x-shellscript', 'groovy': 'text/x-groovy', 'gradle': 'text/x-groovy', 'jmx': 'application/xml'}
        ext_map = {'sh': 'sh', 'groovy': 'groovy', 'gradle': 'gradle', 'yml': 'yml', 'jmeter': 'jmx'}
        ext = ext_map.get(fmt, fmt)
        return Response(content, mimetype=mime_map.get(ext, 'text/plain'), headers={'Content-Disposition': f'attachment; filename=application.{ext}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5007)
