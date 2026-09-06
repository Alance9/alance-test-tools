"""地址类生成器（省市区/详细地址/邮编/座机号关联匹配）"""
import random
from generators.address_utils import generate_detail_address


class AddressExGenerator:
    """地址类生成器：省市区（合并）、详细地址、邮编、座机号（全部关联匹配）"""

    # 完整的省市区 + 邮编 + 区号 + 座机号前缀 关联数据
    # 格式: { 省份: { 城市: [ {district, postcode, area_code, tel_prefix}, ... ] } }
    REGION_DATA = {
        '北京市': {
            '市辖区': [
                {'district': '东城区', 'postcode': '100010', 'tel_prefix': '010'},
                {'district': '西城区', 'postcode': '100032', 'tel_prefix': '010'},
                {'district': '朝阳区', 'postcode': '100020', 'tel_prefix': '010'},
                {'district': '海淀区', 'postcode': '100080', 'tel_prefix': '010'},
                {'district': '丰台区', 'postcode': '100071', 'tel_prefix': '010'},
                {'district': '石景山区', 'postcode': '100043', 'tel_prefix': '010'},
                {'district': '通州区', 'postcode': '101100', 'tel_prefix': '010'},
            ],
        },
        '上海市': {
            '市辖区': [
                {'district': '黄浦区', 'postcode': '200001', 'tel_prefix': '021'},
                {'district': '徐汇区', 'postcode': '200030', 'tel_prefix': '021'},
                {'district': '长宁区', 'postcode': '200050', 'tel_prefix': '021'},
                {'district': '静安区', 'postcode': '200040', 'tel_prefix': '021'},
                {'district': '普陀区', 'postcode': '200333', 'tel_prefix': '021'},
                {'district': '浦东新区', 'postcode': '200120', 'tel_prefix': '021'},
                {'district': '闵行区', 'postcode': '201100', 'tel_prefix': '021'},
            ],
        },
        '广东省': {
            '广州市': [
                {'district': '越秀区', 'postcode': '510030', 'tel_prefix': '020'},
                {'district': '海珠区', 'postcode': '510220', 'tel_prefix': '020'},
                {'district': '荔湾区', 'postcode': '510140', 'tel_prefix': '020'},
                {'district': '天河区', 'postcode': '510630', 'tel_prefix': '020'},
                {'district': '白云区', 'postcode': '510400', 'tel_prefix': '020'},
                {'district': '番禺区', 'postcode': '511400', 'tel_prefix': '020'},
            ],
            '深圳市': [
                {'district': '福田区', 'postcode': '518033', 'tel_prefix': '0755'},
                {'district': '罗湖区', 'postcode': '518001', 'tel_prefix': '0755'},
                {'district': '南山区', 'postcode': '518000', 'tel_prefix': '0755'},
                {'district': '宝安区', 'postcode': '518100', 'tel_prefix': '0755'},
                {'district': '龙岗区', 'postcode': '518172', 'tel_prefix': '0755'},
                {'district': '龙华区', 'postcode': '518109', 'tel_prefix': '0755'},
            ],
            '东莞市': [
                {'district': '莞城区', 'postcode': '523001', 'tel_prefix': '0769'},
                {'district': '南城区', 'postcode': '523071', 'tel_prefix': '0769'},
                {'district': '东城区', 'postcode': '523110', 'tel_prefix': '0769'},
                {'district': '万江区', 'postcode': '523050', 'tel_prefix': '0769'},
            ],
        },
        '江苏省': {
            '南京市': [
                {'district': '玄武区', 'postcode': '210016', 'tel_prefix': '025'},
                {'district': '秦淮区', 'postcode': '210002', 'tel_prefix': '025'},
                {'district': '建邺区', 'postcode': '210019', 'tel_prefix': '025'},
                {'district': '鼓楼区', 'postcode': '210009', 'tel_prefix': '025'},
                {'district': '浦口区', 'postcode': '211800', 'tel_prefix': '025'},
                {'district': '江宁区', 'postcode': '211100', 'tel_prefix': '025'},
            ],
            '苏州市': [
                {'district': '姑苏区', 'postcode': '215001', 'tel_prefix': '0512'},
                {'district': '虎丘区', 'postcode': '215011', 'tel_prefix': '0512'},
                {'district': '吴中区', 'postcode': '215128', 'tel_prefix': '0512'},
                {'district': '相城区', 'postcode': '215131', 'tel_prefix': '0512'},
                {'district': '工业园区', 'postcode': '215123', 'tel_prefix': '0512'},
            ],
        },
        '浙江省': {
            '杭州市': [
                {'district': '上城区', 'postcode': '310002', 'tel_prefix': '0571'},
                {'district': '拱墅区', 'postcode': '310015', 'tel_prefix': '0571'},
                {'district': '西湖区', 'postcode': '310012', 'tel_prefix': '0571'},
                {'district': '滨江区', 'postcode': '310051', 'tel_prefix': '0571'},
                {'district': '萧山区', 'postcode': '311200', 'tel_prefix': '0571'},
                {'district': '余杭区', 'postcode': '311100', 'tel_prefix': '0571'},
            ],
            '宁波市': [
                {'district': '海曙区', 'postcode': '315000', 'tel_prefix': '0574'},
                {'district': '江北区', 'postcode': '315020', 'tel_prefix': '0574'},
                {'district': '北仑区', 'postcode': '315800', 'tel_prefix': '0574'},
                {'district': '镇海区', 'postcode': '315200', 'tel_prefix': '0574'},
                {'district': '鄞州区', 'postcode': '315100', 'tel_prefix': '0574'},
            ],
        },
        '四川省': {
            '成都市': [
                {'district': '锦江区', 'postcode': '610020', 'tel_prefix': '028'},
                {'district': '青羊区', 'postcode': '610031', 'tel_prefix': '028'},
                {'district': '金牛区', 'postcode': '610036', 'tel_prefix': '028'},
                {'district': '武侯区', 'postcode': '610041', 'tel_prefix': '028'},
                {'district': '成华区', 'postcode': '610066', 'tel_prefix': '028'},
                {'district': '高新区', 'postcode': '610041', 'tel_prefix': '028'},
            ],
        },
        '湖北省': {
            '武汉市': [
                {'district': '江岸区', 'postcode': '430014', 'tel_prefix': '027'},
                {'district': '江汉区', 'postcode': '430022', 'tel_prefix': '027'},
                {'district': '硚口区', 'postcode': '430033', 'tel_prefix': '027'},
                {'district': '汉阳区', 'postcode': '430050', 'tel_prefix': '027'},
                {'district': '武昌区', 'postcode': '430061', 'tel_prefix': '027'},
                {'district': '洪山区', 'postcode': '430070', 'tel_prefix': '027'},
            ],
        },
        '陕西省': {
            '西安市': [
                {'district': '新城区', 'postcode': '710004', 'tel_prefix': '029'},
                {'district': '碑林区', 'postcode': '710001', 'tel_prefix': '029'},
                {'district': '莲湖区', 'postcode': '710003', 'tel_prefix': '029'},
                {'district': '雁塔区', 'postcode': '710065', 'tel_prefix': '029'},
                {'district': '未央区', 'postcode': '710016', 'tel_prefix': '029'},
                {'district': '高新区', 'postcode': '710075', 'tel_prefix': '029'},
            ],
        },
        '山东省': {
            '济南市': [
                {'district': '历下区', 'postcode': '250014', 'tel_prefix': '0531'},
                {'district': '市中区', 'postcode': '250002', 'tel_prefix': '0531'},
                {'district': '槐荫区', 'postcode': '250021', 'tel_prefix': '0531'},
                {'district': '天桥区', 'postcode': '250031', 'tel_prefix': '0531'},
                {'district': '历城区', 'postcode': '250100', 'tel_prefix': '0531'},
            ],
            '青岛市': [
                {'district': '市南区', 'postcode': '266071', 'tel_prefix': '0532'},
                {'district': '市北区', 'postcode': '266033', 'tel_prefix': '0532'},
                {'district': '黄岛区', 'postcode': '266500', 'tel_prefix': '0532'},
                {'district': '崂山区', 'postcode': '266100', 'tel_prefix': '0532'},
                {'district': '李沧区', 'postcode': '266100', 'tel_prefix': '0532'},
            ],
        },
        '福建省': {
            '福州市': [
                {'district': '鼓楼区', 'postcode': '350001', 'tel_prefix': '0591'},
                {'district': '台江区', 'postcode': '350004', 'tel_prefix': '0591'},
                {'district': '仓山区', 'postcode': '350007', 'tel_prefix': '0591'},
                {'district': '马尾区', 'postcode': '350015', 'tel_prefix': '0591'},
                {'district': '晋安区', 'postcode': '350011', 'tel_prefix': '0591'},
            ],
            '厦门市': [
                {'district': '思明区', 'postcode': '361001', 'tel_prefix': '0592'},
                {'district': '海沧区', 'postcode': '361026', 'tel_prefix': '0592'},
                {'district': '湖里区', 'postcode': '361006', 'tel_prefix': '0592'},
                {'district': '集美区', 'postcode': '361021', 'tel_prefix': '0592'},
                {'district': '同安区', 'postcode': '361100', 'tel_prefix': '0592'},
            ],
        },
    }

    def generate(self, count=1):
        """生成指定数量的地址类数据（省市区/邮编/座机号全部关联匹配）"""
        data = []
        for _ in range(count):
            province = random.choice(list(self.REGION_DATA.keys()))
            city = random.choice(list(self.REGION_DATA[province].keys()))
            district_info = random.choice(self.REGION_DATA[province][city])

            region = f'{province}{city}{district_info["district"]}'
            postcode = district_info['postcode']
            tel_prefix = district_info['tel_prefix']
            # 生成座机号：区号 + 8位号码
            landline = f'{tel_prefix}-{random.randint(10000000, 99999999)}'
            # 详细地址（真实格式）
            detail = generate_detail_address()

            data.append({
                '省市区': region,
                '详细地址': detail,
                '邮编': postcode,
                '座机号': landline,
            })
        return data

    def get_fields(self):
        """返回字段列表"""
        return ['省市区', '详细地址', '邮编', '座机号']
