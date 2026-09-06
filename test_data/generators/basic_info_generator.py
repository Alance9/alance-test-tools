"""基础信息生成器"""
from faker import Faker
import random
import uuid
import time
from generators.address_utils import generate_detail_address


# 省市区关联数据（简化版，用于居住地址）
REGION_DATA = {
    '北京市': {'市辖区': ['东城区', '西城区', '朝阳区', '海淀区', '丰台区']},
    '上海市': {'市辖区': ['黄浦区', '徐汇区', '长宁区', '静安区', '浦东新区']},
    '广东省': {
        '广州市': ['越秀区', '海珠区', '天河区', '白云区'],
        '深圳市': ['福田区', '罗湖区', '南山区', '宝安区'],
    },
    '江苏省': {
        '南京市': ['玄武区', '秦淮区', '鼓楼区', '建邺区'],
        '苏州市': ['姑苏区', '虎丘区', '吴中区'],
    },
    '浙江省': {
        '杭州市': ['上城区', '拱墅区', '西湖区', '滨江区'],
        '宁波市': ['海曙区', '江北区', '北仑区'],
    },
    '四川省': {'成都市': ['锦江区', '青羊区', '金牛区', '武侯区']},
    '湖北省': {'武汉市': ['江岸区', '江汉区', '硚口区', '武昌区']},
    '陕西省': {'西安市': ['新城区', '碑林区', '莲湖区', '雁塔区']},
    '山东省': {
        '济南市': ['历下区', '市中区', '槐荫区'],
        '青岛市': ['市南区', '市北区', '黄岛区'],
    },
    '福建省': {
        '福州市': ['鼓楼区', '台江区', '仓山区'],
        '厦门市': ['思明区', '海沧区', '湖里区'],
    },
}


class BasicInfoGenerator:
    """基础信息生成器：姓名、手机号、邮箱、身份证号、企业名称、银行卡号、UUID、时间戳、出生日期、居住地址"""

    def __init__(self):
        self.fake = Faker('zh_CN')

    def _generate_full_address(self):
        """生成包含省市区的完整居住地址"""
        province = random.choice(list(REGION_DATA.keys()))
        city = random.choice(list(REGION_DATA[province].keys()))
        district = random.choice(REGION_DATA[province][city])
        detail = generate_detail_address()
        return f'{province}{city}{district}{detail}'

    def generate(self, count=1):
        """生成指定数量的基础信息"""
        data = []
        for _ in range(count):
            data.append({
                '中文姓名': self.fake.name(),
                '手机号': self.fake.phone_number(),
                '邮箱': self.fake.email(),
                '身份证号': self.fake.ssn(),
                '企业名称': self.fake.company(),
                '银行卡号': self.fake.credit_card_number(),
                'UUID': str(uuid.uuid4()),
                '时间戳': int(time.time()),
                '出生日期': self.fake.date_of_birth(minimum_age=18, maximum_age=70).strftime('%Y-%m-%d'),
                '居住地址': self._generate_full_address(),
            })
        return data

    def get_fields(self):
        """返回字段列表"""
        return ['中文姓名', '手机号', '邮箱', '身份证号', '企业名称', '银行卡号', 'UUID', '时间戳', '出生日期', '居住地址']
