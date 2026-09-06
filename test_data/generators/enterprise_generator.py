"""企业类生成器"""
from faker import Faker
import random
import string
from generators.address_utils import generate_company_address


# 复用地址类的省市区数据以确保关联一致
PROVINCE_CITY_DISTRICT = {
    '北京市': {'市辖区': ['东城区', '西城区', '朝阳区', '海淀区', '丰台区', '石景山区']},
    '上海市': {'市辖区': ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '浦东新区']},
    '广东省': {
        '广州市': ['越秀区', '海珠区', '荔湾区', '天河区', '白云区'],
        '深圳市': ['福田区', '罗湖区', '南山区', '宝安区', '龙岗区'],
        '东莞市': ['莞城区', '南城区', '东城区', '万江区'],
    },
    '江苏省': {
        '南京市': ['玄武区', '秦淮区', '建邺区', '鼓楼区', '浦口区'],
        '苏州市': ['姑苏区', '虎丘区', '吴中区', '相城区', '工业园区'],
    },
    '浙江省': {
        '杭州市': ['上城区', '拱墅区', '西湖区', '滨江区', '萧山区'],
        '宁波市': ['海曙区', '江北区', '北仑区', '镇海区', '鄞州区'],
    },
    '四川省': {
        '成都市': ['锦江区', '青羊区', '金牛区', '武侯区', '成华区'],
    },
    '湖北省': {
        '武汉市': ['江岸区', '江汉区', '硚口区', '汉阳区', '武昌区'],
    },
    '陕西省': {
        '西安市': ['新城区', '碑林区', '莲湖区', '雁塔区', '未央区'],
    },
    '山东省': {
        '济南市': ['历下区', '市中区', '槐荫区', '天桥区', '历城区'],
        '青岛市': ['市南区', '市北区', '黄岛区', '崂山区', '李沧区'],
    },
    '福建省': {
        '福州市': ['鼓楼区', '台江区', '仓山区', '马尾区', '晋安区'],
        '厦门市': ['思明区', '海沧区', '湖里区', '集美区', '同安区'],
    },
}


class EnterpriseGenerator:
    """企业类生成器：公司名、公司地址（关联省市区）、统一社会信用代码、组织机构代码、税号（纯数字）、企业邮箱"""

    def __init__(self):
        self.fake = Faker('zh_CN')

    def generate(self, count=1):
        """生成指定数量的企业类数据"""
        data = []
        province_keys = list(PROVINCE_CITY_DISTRICT.keys())

        for _ in range(count):
            # 关联省市区
            province = random.choice(province_keys)
            city = random.choice(list(PROVINCE_CITY_DISTRICT[province].keys()))
            district = random.choice(PROVINCE_CITY_DISTRICT[province][city])
            # 企业详细地址
            detail = generate_company_address(province, city)
            company_address = f'{province}{city}{district}{detail}'

            company_name = self.fake.company()
            data.append({
                '公司名': company_name,
                '公司地址': company_address,
                '统一社会信用代码': self._generate_uscc(),
                '组织机构代码': self._generate_org_code(),
                '税号': self._generate_tax_number(),
                '企业邮箱': self._generate_company_email(company_name),
            })
        return data

    def _generate_uscc(self):
        """生成统一社会信用代码（18位）"""
        return ''.join(random.choices(string.digits + string.ascii_uppercase, k=18))

    def _generate_org_code(self):
        """生成组织机构代码（9位，含分隔符）"""
        code = ''.join(random.choices(string.digits + string.ascii_uppercase, k=8))
        return code + '-' + random.choice('0123456789ABCDEFGHJKLMNPRSTUWXY') + ''.join(random.choices('0123456789ABCDEFGHJKLMNPRSTUWXY', k=0))

    def _generate_tax_number(self):
        """生成税号（纯15位数字）"""
        return ''.join(random.choices(string.digits, k=15))

    def _generate_company_email(self, company_name):
        """生成企业邮箱"""
        domain = 'company' + str(random.randint(1, 999)) + '.com'
        return self.fake.user_name() + '@' + domain

    def get_fields(self):
        """返回字段列表"""
        return ['公司名', '公司地址', '统一社会信用代码', '组织机构代码', '税号', '企业邮箱']
