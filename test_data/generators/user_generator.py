from faker import Faker
import random

class UserGenerator:
    def __init__(self):
        self.fake = Faker('zh_CN')
    
    def generate(self, count=1):
        users = []
        for _ in range(count):
            gender = random.choice(['男', '女'])
            users.append({
                '姓名': self.fake.name(),
                '性别': gender,
                '年龄': random.randint(18, 65),
                '手机号': self.fake.phone_number(),
                '邮箱': self.fake.email(),
                '身份证号': self.fake.ssn(),
                '用户名': self.fake.user_name(),
                '密码': self.fake.password(length=8),
                '职位': self.fake.job(),
                '部门': self.fake.company(),
            })
        return users
    
    def get_fields(self):
        return ['姓名', '性别', '年龄', '手机号', '邮箱', '身份证号', '用户名', '密码', '职位', '部门']
