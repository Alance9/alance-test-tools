"""地址工具模块：生成真实的详细地址（幢、号、座、室）"""
import random

# 常见街道名后缀
STREET_SUFFIXES = ['路', '街', '巷', '道', '大道', '巷', '弄', '胡同', '大街']

# 常见建筑标识
BUILDING_PREFIXES = ['号楼', '栋', '幢', '座']

# 常见区域标识
AREA_PREFIXES = ['A区', 'B区', 'C区', 'D区', '东区', '西区', '南区', '北区']


def generate_detail_address():
    """
    生成真实感较强的详细地址
    格式示例：中山南路88号3号楼2单元501室
    """
    street_names = [
        '中山', '人民', '解放', '建设', '和平', '友谊', '团结', '胜利', '光明', '幸福',
        '新华', '文化', '教育', '科技', '工业', '商业', '金融', '科技', '创新', '发展',
        '长江', '黄河', '珠江', '海河', '淮河', '湘江', '锦江', '西湖', '东湖', '南湖',
        '望京', '朝阳', '海淀', '西城', '东城', '黄浦', '徐汇', '静安', '浦东', '长宁',
        '天河', '越秀', '海珠', '福田', '南山', '龙岗', '罗湖', '宝安', '龙华', '东莞',
        '玄武', '秦淮', '建邺', '鼓楼', '姑苏', '虎丘', '吴中', '相城', '园区', '滨江',
        '高新', '天府', '锦城', '锦江', '青羊', '金牛', '武侯', '成华', '洪山', '江岸',
        '江汉', '硚口', '汉阳', '武昌', '东湖', '新城区', '碑林', '莲湖', '雁塔', '未央',
        '历下', '市中', '槐荫', '天桥', '历城', '市南', '市北', '黄岛', '崂山', '李沧',
        '鼓楼', '台江', '仓山', '马尾', '晋安', '思明', '海沧', '湖里', '集美', '同安',
    ]

    # 随机组合街道名
    street = random.choice(street_names) + random.choice(STREET_SUFFIXES)
    # 门牌号
    building_num = random.randint(1, 999)

    # 随机决定详细程度
    detail_level = random.random()

    if detail_level < 0.25:
        # 最简单：XX路88号
        return f'{street}{building_num}号'
    elif detail_level < 0.5:
        # 中等：XX路88号3号楼
        return f'{street}{building_num}号{random.randint(1, 30)}{random.choice(BUILDING_PREFIXES)}'
    elif detail_level < 0.75:
        # 较详细：XX路88号3号楼2单元
        unit = random.choice(['单元', '栋', '座'])
        return f'{street}{building_num}号{random.randint(1, 30)}{random.choice(BUILDING_PREFIXES)}{random.randint(1, 12)}{unit}'
    else:
        # 最详细：XX路88号3号楼2单元501室
        floor = random.randint(1, 30)
        room = random.randint(1, 24)
        return f'{street}{building_num}号{random.randint(1, 30)}{random.choice(BUILDING_PREFIXES)}{random.randint(1, 12)}单元{floor}{room:02d}室'


def generate_company_address(province='', city=''):
    """
    生成企业详细地址（比普通地址更商务）
    格式示例：XX路88号XX大厦12层1208室
    """
    street_names = [
        '人民', '建设', '解放', '中山', '商务', '金融', '科技', '创新', '发展', 'CBD',
        '中心', '国际', '环球', '时代', '财富', '世贸', '中环', '广场', '花园', '银座',
    ]
    building_names = [
        '大厦', '广场', '中心', '花园', '公寓', '写字楼', '综合楼', '办公楼', '基地', '科技园',
        '创新中心', '商务楼', '写字楼', '产业园', '孵化器', '创业园', '科技园',
    ]

    street = random.choice(street_names) + random.choice(STREET_SUFFIXES)
    building_num = random.randint(1, 999)
    building = random.choice(building_names)
    floor = random.randint(1, 30)
    room = random.randint(1, 24)

    return f'{street}{building_num}号{building}{floor}层{floor}{room:02d}室'
