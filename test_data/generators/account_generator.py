"""账号类生成器"""
from faker import Faker
import random
import string
import uuid
import secrets


class AccountGenerator:
    """账号类生成器：用户名、随机密码、用户ID、token、盐值、幂等键、邀请码"""

    def __init__(self):
        self.fake = Faker('zh_CN')

    def generate(self, count=1):
        """生成指定数量的账号类数据"""
        data = []
        for _ in range(count):
            data.append({
                '用户名': self.fake.user_name(),
                '随机密码': self._generate_password(),
                '用户ID': random.randint(10000, 99999999),
                'token': secrets.token_hex(32),
                '盐值': secrets.token_hex(8),
                '幂等键': uuid.uuid4().hex,
                '邀请码': ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
            })
        return data

    def _generate_password(self):
        """生成随机密码"""
        length = random.randint(8, 16)
        chars = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(random.choices(chars, k=length))

    def get_fields(self):
        """返回字段列表"""
        return ['用户名', '随机密码', '用户ID', 'token', '盐值', '幂等键', '邀请码']
