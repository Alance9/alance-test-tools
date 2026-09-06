from faker import Faker
import random

class TextGenerator:
    def __init__(self):
        self.fake = Faker('zh_CN')
    
    def generate(self, count=1):
        texts = []
        for _ in range(count):
            texts.append({
                '标题': self.fake.sentence(nb_words=5),
                '段落': self.fake.text(max_nb_chars=200),
                '短句': self.fake.sentence(),
                '词语': self.fake.word(),
                '数字': random.randint(1, 999999),
                '小数': round(random.uniform(0, 1000), 2),
                '日期': self.fake.date(),
                '时间': self.fake.time(),
                '邮箱': self.fake.email(),
                'URL': self.fake.url(),
                'IP地址': self.fake.ipv4(),
                'MAC地址': self.fake.mac_address(),
            })
        return texts
    
    def get_fields(self):
        return ['标题', '段落', '短句', '词语', '数字', '小数', '日期', '时间', '邮箱', 'URL', 'IP地址', 'MAC地址']
