"""API造数工具后端"""
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)


POSTMAN_EXAMPLE = r'''# =============================================
# Postman Collection 造数示例
# 导入 Postman 使用，批量调用 API 造数
# =============================================
# 1. 新建 Collection: TestDataGenerator
# 2. 添加 Authorization -> Bearer Token
# 3. 添加请求变量 {{baseUrl}} = http://localhost:8080
# =============================================

# ====== 用户注册接口 ======
POST {{baseUrl}}/api/user/register
Content-Type: application/json

{
    "username": "user{{randomInt}}",
    "password": "Pwd@{{randomInt}}",
    "phone": "1{{randomInt(1000000000, 9999999999)}}",
    "email": "user{{randomInt}}@test.com"
}

# ====== 批量造数（Runner 模式）======
# Collection Runner 设置：
# - Iterations: 10000
# - Delay: 10ms
# - 每次迭代生成一个随机用户名

# Pre-request Script:
pm.environment.set("username", "user_" + Math.floor(Math.random() * 1000000));
pm.environment.set("phone", "1" + (3 + Math.floor(Math.random() * 7)) + Math.floor(Math.random() * 1000000000));
pm.environment.set("email", "user_" + Math.floor(Math.random() * 1000000) + "@test.com");

# ====== 断言脚本 ======
# Tests 标签:
pm.test("状态码为 200", function() {
    pm.response.to.have.status(200);
});
pm.test("返回成功标志", function() {
    var jsonData = pm.response.json();
    pm.expect(jsonData.code).to.eql(0);
});

# ====== 订单接口造数 ======
POST {{baseUrl}}/api/order/create
Content-Type: application/json
Authorization: Bearer {{token}}

{
    "userId": {{userId}},
    "productId": {{randomInt(1, 100)}},
    "quantity": {{randomInt(1, 10)}},
    "address": "北京市朝阳区XX路{{randomInt(1, 999)}}号"
}

# ====== CSV 数据驱动造数 ======
# 在 Collection 中引用 CSV 文件：users.csv
# CSV 格式：
# username,password,phone,email
# user1,Pwd123!,13800000001,user1@test.com
# user2,Pwd123!,13800000002,user2@test.com
# ...
#
# 请求体中使用变量：
{
    "username": "{{username}}",
    "password": "{{password}}",
    "phone": "{{phone}}",
    "email": "{{email}}"
}
'''


JMETER_EXAMPLE = r'''# =============================================
# JMeter 造数脚本示例（.jmx 关键配置）
# 使用 CSV Data Set Config + 线程组批量造数
# =============================================

# ====== 1. 线程组配置 ======
# Thread Group:
#   - Number of Threads: 100
#   - Ramp-Up Period: 10
#   - Loop Count: 100
#   - 总请求数 = 100 * 100 = 10000

# ====== 2. CSV 数据文件 ======
# CSV Data Set Config:
#   - Filename: users.csv
#   - Variable Names: username,password,phone,email
#   - Delimiter: ,
#   - Allow quoted data: true
#   - Sharing mode: All threads

# ====== 3. HTTP 请求 ======
# HTTP Request Defaults:
#   - Protocol: http
#   - Server Name: localhost
#   - Port: 8080

# HTTP Request (用户注册):
#   - Method: POST
#   - Path: /api/user/register
#   - Body Data:
{"username":"${username}","password":"${password}","phone":"${phone}","email":"${email}"}

# ====== 4. 随机变量生成 ======
# User Defined Variables:
#   - baseUrl = http://localhost:8080

# JSR223 PreProcessor (Groovy):
import java.util.Random;
def random = new Random();
def prefix = "user_" + System.currentTimeMillis();
vars.put("username", prefix + "_" + random.nextInt(10000));
vars.put("phone", "1" + (3 + random.nextInt(7)) + String.format("%010d", random.nextInt(1000000000)));
vars.put("email", prefix + "@test.com");

# ====== 5. 响应断言 ======
# Response Assertion:
#   - Pattern Matching Rules: Contains
#   - Patterns to Test: "success"
#   - OR: 使用 JSON Extractor 提取 token

# JSON Extractor:
#   - Names of created variables: token
#   - JSON Path Expressions: $.data.token

# ====== 6. 监听器（输出结果）======
# View Results Tree / View Results in Table
# Simple Data Writer 输出 CSV 结果

# ====== 7. 参数化造数（不用 CSV）======
# 使用 __counter 函数生成唯一序号:
{"username":"user_${__counter(TRUE,)}","phone":"1${__Random(3000000000,9999999999,)}"}
'''


PYTHON_THREADPOOL = r'''import requests, random
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8080"
THREADS  = 50
TOTAL    = 10000

def send(_):
    try:
        requests.post(f"{BASE_URL}/api/user/register", json={
            "username": f"user_{random.randint(1,999999)}",
            "password": f"Pwd{random.randint(1,999999)}",
            "phone":    f"1{random.randint(3000000000, 9999999999)}",
        }, timeout=5)
    except: pass

with ThreadPoolExecutor(max_workers=THREADS) as pool:
    list(pool.map(send, range(TOTAL)))
print("done")
'''


EXAMPLES = {
    'postman': POSTMAN_EXAMPLE,
    'jmeter': JMETER_EXAMPLE,
    'python': PYTHON_THREADPOOL,
}


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/example', methods=['GET'])
def get_example():
    """获取造数示例"""
    t = request.args.get('type', 'postman')
    return jsonify({'success': True, 'code': EXAMPLES.get(t, '')})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006)
