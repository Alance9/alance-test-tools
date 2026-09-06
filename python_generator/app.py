"""Python造数工具后端"""
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)


PYTHON_MYSQL = r'''# =============================================
# Python + PyMySQL 连接 MySQL 造数示例
# 依赖：pip install pymysql faker
# =============================================
import pymysql
from faker import Faker
import random
import uuid

fake = Faker('zh_CN')

def gen_mysql_data(count=10000):
    # 连接数据库
    conn = pymysql.connect(
        host='localhost', port=3306,
        user='root', password='123456',
        database='test_db', charset='utf8mb4'
    )
    cursor = conn.cursor()

    # 创建表
    cursor.execute("""CREATE TABLE IF NOT EXISTS t_user (
        id BIGINT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50), password VARCHAR(100),
        phone VARCHAR(20), email VARCHAR(100),
        age INT, gender TINYINT, address VARCHAR(200),
        status TINYINT DEFAULT 1, create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_phone (phone)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")

    # 批量造数 executemany
    rows = []
    for i in range(count):
        rows.append((
            f'user_{i+1:06d}',
            f'pwd_{uuid.uuid4().hex[:16]}',
            f'1{random.choice(["3","5","7","8","9"])}{random.randint(100000000, 999999999)}',
            fake.email(),
            random.randint(18, 68),
            random.randint(0, 1),
            fake.address(),
            random.choice([0, 1]),
        ))

    # 批量插入（每5000条提交一次）
    batch_size = 5000
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        cursor.executemany(
            "INSERT INTO t_user (username, password, phone, email, age, gender, address, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            batch
        )
        conn.commit()
        print(f'已插入 {min(i+batch_size, len(rows))}/{len(rows)} 条')

    cursor.close()
    conn.close()

if __name__ == '__main__':
    gen_mysql_data(10000)
'''


PYTHON_ORACLE = r'''# =============================================
# Python + cx_Oracle 连接 Oracle 造数示例
# 依赖：pip install cx_Oracle faker
# =============================================
import cx_Oracle
from faker import Faker
import random
import uuid

fake = Faker('zh_CN')

def gen_oracle_data(count=10000):
    # 初始化 Oracle Client（需安装 Oracle Instant Client）
    cx_Oracle.init_oracle_client(lib_dir=r'D:\oracle\instantclient_19_26')

    # 连接数据库
    dsn = cx_Oracle.makedsn('localhost', 1521, service_name='ORCL')
    conn = cx_Oracle.connect(user='test', password='123456', dsn=dsn)
    cursor = conn.cursor()

    # 创建序列（如果不存在）
    try:
        cursor.execute('CREATE SEQUENCE seq_user START WITH 1 INCREMENT BY 1')
    except:
        pass

    # 批量造数
    batch = []
    for i in range(count):
        batch.append((
            f'user_{i+1:06d}',
            f'pwd_{uuid.uuid4().hex[:16]}',
            f'1{random.choice(["3","5","7","8","9"])}{random.randint(100000000, 999999999)}',
            fake.email(),
            random.randint(18, 68),
            random.randint(0, 1),
            fake.address(),
            random.choice([0, 1]),
        ))

    # 使用 cursor.executemany 批量插入
    cursor.executemany("""
        INSERT INTO t_user (username, password, phone, email, age, gender, address, status)
        VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
    """, batch)

    conn.commit()
    cursor.close()
    conn.close()
    print(f'成功造数 {count} 条')

if __name__ == '__main__':
    gen_oracle_data(10000)
'''


PYTHON_GAUSS = r'''# =============================================
# Python + psycopg2 连接 GaussDB/openGauss 造数示例
# 依赖：pip install psycopg2-binary faker
# =============================================
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
import random
import uuid

fake = Faker('zh_CN')

def gen_gauss_data(count=10000):
    # 连接 GaussDB（兼容 PostgreSQL 协议）
    conn = psycopg2.connect(
        host='localhost', port=5432,
        user='gaussdb', password='123456',
        dbname='test_db'
    )
    cursor = conn.cursor()

    # 创建表
    cursor.execute("""CREATE TABLE IF NOT EXISTS t_user (
        id BIGSERIAL PRIMARY KEY,
        username VARCHAR(50), password VARCHAR(100),
        phone VARCHAR(20), email VARCHAR(100),
        age INTEGER, gender SMALLINT, address VARCHAR(200),
        status SMALLINT DEFAULT 1, create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()

    # 批量造数（使用 execute_values 高效批量插入）
    rows = []
    for i in range(count):
        rows.append((
            f'user_{i+1:06d}',
            f'pwd_{uuid.uuid4().hex[:16]}',
            f'1{random.choice(["3","5","7","8","9"])}{random.randint(100000000, 999999999)}',
            fake.email(),
            random.randint(18, 68),
            random.randint(0, 1),
            fake.address(),
            random.choice([0, 1]),
        ))

    batch_size = 5000
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        execute_values(cursor,
            "INSERT INTO t_user (username, password, phone, email, age, gender, address, status) VALUES %s",
            batch
        )
        conn.commit()
        print(f'已插入 {min(i+batch_size, len(rows))}/{len(rows)} 条')

    cursor.close()
    conn.close()

if __name__ == '__main__':
    gen_gauss_data(10000)
'''


PYTHON_REGEX = r'''# =============================================
# Python 正则表达式常用示例集
# =============================================
import re

# 1. 手机号验证
phone_pattern = re.compile(r'^1[3-9]\d{9}$')
print(phone_pattern.match('13812345678'))  # 匹配
print(phone_pattern.match('12345678901'))  # 不匹配

# 2. 邮箱验证
email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# 3. URL 提取
text = '访问 https://www.example.com/path?x=1 或 http://test.cn 了解更多'
urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
# ['https://www.example.com/path?x=1', 'http://test.cn']

# 4. IP 地址验证
ip_pattern = re.compile(r'^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$')

# 5. 身份证号验证（18位）
id_pattern = re.compile(r'^\d{17}[\dXx]$')

# 6. 日期格式提取
log = '2025-01-15 10:30:45 [INFO] 2025/02/20 错误'
dates = re.findall(r'\d{4}[-/]\d{2}[-/]\d{2}', log)
# ['2025-01-15', '2025/02/20']

# 7. 多行日志解析
log_pattern = re.compile(
    r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\s\[(\w+)\]\s(.+)',
    re.MULTILINE
)

# 8. 数字提取
s = '订单金额: 1234.56元，折扣: 0.8，共3件'
nums = re.findall(r'-?\d+\.?\d*', s)
# ['1234.56', '0.8', '3']

# 9. HTML 标签移除
html = '<p>Hello <b>World</b></p>'
clean = re.sub(r'<[^>]+>', '', html)  # 'Hello World'

# 10. 驼峰转下划线
def camel_to_snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
print(camel_to_snake('userNameList'))  # 'user_name_list'

# 11. 下划线转驼峰
def snake_to_camel(name):
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
print(snake_to_camel('user_name_list'))  # 'userNameList'

# 12. 敏感词替换
sensitive = ['赌博', '色情', '暴力']
text = '禁止赌博和色情内容'
for word in sensitive:
    text = re.sub(word, '*' * len(word), text)
# '禁止**和**内容'
'''


EXAMPLES = {
    'mysql': PYTHON_MYSQL,
    'oracle': PYTHON_ORACLE,
    'gauss': PYTHON_GAUSS,
    'regex': PYTHON_REGEX,
}


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/example', methods=['GET'])
def get_example():
    """获取造数示例"""
    db_type = request.args.get('type', 'mysql')
    return jsonify({'success': True, 'code': EXAMPLES.get(db_type, '')})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
