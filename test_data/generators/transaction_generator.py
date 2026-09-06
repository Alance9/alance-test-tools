"""交易类生成器"""
from faker import Faker
import random
import uuid
from datetime import datetime, timedelta
from generators.address_utils import generate_detail_address


class TransactionGenerator:
    """交易类生成器：订单号、UUID、用户ID、商品、金额、支付方式、状态、时间、收货地址"""

    # 中文商品名称库
    PRODUCT_NAMES = [
        '智能手机', '平板电脑', '无线耳机', '蓝牙音箱', '智能手表',
        '机械键盘', '光电鼠标', '移动硬盘', 'U盘', '内存卡',
        '显示器', '主机', '路由器', '摄像头', '打印机',
        '电动牙刷', '吹风机', '电饭煲', '电磁炉', '微波炉',
        '洗衣机', '冰箱', '空调', '电视机', '投影仪',
        '运动鞋', '休闲裤', 'T恤', '羽绒服', '牛仔裤',
        '双肩包', '钱包', '皮带', '帽子', '袜子',
        '牛奶', '面包', '饼干', '巧克力', '咖啡豆',
        '矿泉水', '果汁', '茶叶', '糖果', '坚果',
    ]

    # 收货地址省市区关联数据
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
            '绵阳市': ['涪城区', '游仙区', '安州区'],
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

    def __init__(self):
        self.fake = Faker('zh_CN')

    def generate(self, count=1):
        """生成指定数量的交易类数据"""
        data = []
        status_list = ['待支付', '已支付', '已发货', '已签收', '已取消']
        payment_list = ['支付宝', '微信支付', '银行卡', '现金']
        province_city_district_keys = list(self.PROVINCE_CITY_DISTRICT.keys())

        for _ in range(count):
            create_time = self.fake.date_time_between(start_date='-30d', end_date='now')
            # 关联省市区
            province = random.choice(province_city_district_keys)
            cities = list(self.PROVINCE_CITY_DISTRICT[province].keys())
            city = random.choice(cities)
            districts = self.PROVINCE_CITY_DISTRICT[province][city]
            district = random.choice(districts)
            detail_addr = generate_detail_address()
            full_address = f'{province}{city}{district}{detail_addr}'

            # 商品和金额
            product_name = random.choice(self.PRODUCT_NAMES)
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(10, 1000), 2)
            total_amount = round(quantity * unit_price, 2)

            # 时间
            payment_time = (create_time + timedelta(minutes=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S') if random.random() > 0.3 else ''
            ship_time = (create_time + timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S') if random.random() > 0.5 else ''

            data.append({
                '订单号': str(random.randint(1000000000, 9999999999)),
                'UUID': str(uuid.uuid4()),
                '用户ID': random.randint(10000, 99999),
                '商品名称': product_name,
                '商品数量': quantity,
                '商品单价': unit_price,
                '订单金额': total_amount,
                '支付方式': random.choice(payment_list),
                '订单状态': random.choice(status_list),
                '创建时间': create_time.strftime('%Y-%m-%d %H:%M:%S'),
                '支付时间': payment_time,
                '发货时间': ship_time,
                '收货地址': full_address,
            })
        return data

    def get_fields(self):
        """返回字段列表"""
        return ['订单号', 'UUID', '用户ID', '商品名称', '商品数量', '商品单价', '订单金额',
                '支付方式', '订单状态', '创建时间', '支付时间', '发货时间', '收货地址']
