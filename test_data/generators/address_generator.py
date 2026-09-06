from faker import Faker
import random

class AddressGenerator:
    def __init__(self):
        self.fake = Faker('zh_CN')
    
    def generate(self, count=1):
        addresses = []
        for _ in range(count):
            addresses.append({
                '省': self.fake.province(),
                '市': self.fake.city(),
                '区': self.fake.district(),
                '详细地址': self.fake.street_address(),
                '邮政编码': self.fake.postcode(),
                '完整地址': self.fake.address().replace('\n', ' '),
                '纬度': self.fake.latitude(),
                '经度': self.fake.longitude(),
            })
        return addresses
    
    def get_fields(self):
        return ['省', '市', '区', '详细地址', '邮政编码', '完整地址', '纬度', '经度']
