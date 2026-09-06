from faker import Faker
import random
import uuid
from datetime import datetime

class IDGenerator:
    def __init__(self):
        self.fake = Faker('zh_CN')
    
    def generate(self, count=1):
        ids = []
        for _ in range(count):
            ids.append({
                'UUID': str(uuid.uuid4()),
                'UUID1': str(uuid.uuid1()),
                'UUID3': str(uuid.uuid3(uuid.NAMESPACE_DNS, self.fake.word())),
                'UUID4': str(uuid.uuid4()),
                'UUID5': str(uuid.uuid5(uuid.NAMESPACE_DNS, self.fake.word())),
                '雪花ID': self._generate_snowflake_id(),
                '时间戳ID': str(int(datetime.now().timestamp())) + str(random.randint(1000, 9999)),
                '随机整数ID': random.randint(1, 9999999),
                '字母数字ID': self.fake.bothify(text='ABCDEFGHIJKLMNOPQRSTUVWXYZ???###'),
                '身份证号': self.fake.ssn(),
                '手机号': self.fake.phone_number(),
                '银行卡号': self.fake.credit_card_number(),
            })
        return ids
    
    def _generate_snowflake_id(self):
        timestamp = int(datetime.now().timestamp() * 1000)
        worker_id = random.randint(0, 31)
        datacenter_id = random.randint(0, 31)
        sequence = random.randint(0, 4095)
        return (timestamp << 22) | (datacenter_id << 17) | (worker_id << 12) | sequence
    
    def get_fields(self):
        return ['UUID', 'UUID1', 'UUID3', 'UUID4', 'UUID5', '雪花ID', '时间戳ID', '随机整数ID', '字母数字ID', '身份证号', '手机号', '银行卡号']
