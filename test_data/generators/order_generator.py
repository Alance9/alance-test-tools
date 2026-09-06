from faker import Faker
import random
import uuid
from datetime import datetime, timedelta

class OrderGenerator:
    def __init__(self):
        self.fake = Faker('zh_CN')
    
    def generate(self, count=1):
        orders = []
        status_list = ['待支付', '已支付', '已发货', '已签收', '已取消']
        payment_list = ['支付宝', '微信支付', '银行卡', '现金']
        for _ in range(count):
            create_time = self.fake.date_time_between(start_date='-30d', end_date='now')
            orders.append({
                '订单号': 'ORD' + datetime.now().strftime('%Y%m%d') + str(random.randint(100000, 999999)),
                'UUID': str(uuid.uuid4()),
                '用户ID': random.randint(10000, 99999),
                '商品名称': self.fake.word(),
                '商品数量': random.randint(1, 10),
                '商品单价': round(random.uniform(10, 1000), 2),
                '订单金额': round(random.uniform(10, 5000), 2),
                '支付方式': random.choice(payment_list),
                '订单状态': random.choice(status_list),
                '创建时间': create_time.strftime('%Y-%m-%d %H:%M:%S'),
                '支付时间': (create_time + timedelta(minutes=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S') 
                           if random.random() > 0.3 else '',
                '发货时间': (create_time + timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S') 
                           if random.random() > 0.5 else '',
                '收货地址': self.fake.address().replace('\n', ' '),
            })
        return orders
    
    def get_fields(self):
        return ['订单号', 'UUID', '用户ID', '商品名称', '商品数量', '商品单价', '订单金额', '支付方式', '订单状态', '创建时间', '支付时间', '发货时间', '收货地址']
