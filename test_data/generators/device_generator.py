"""设备类生成器"""
from faker import Faker
import random
import string


class DeviceGenerator:
    """设备类生成器：设备id、IMEI、Android id、序列号"""

    def __init__(self):
        self.fake = Faker('zh_CN')

    def generate(self, count=1):
        """生成指定数量的设备类数据"""
        data = []
        for _ in range(count):
            data.append({
                '设备ID': self._generate_device_id(),
                'IMEI': self._generate_imei(),
                'AndroidID': self._generate_android_id(),
                '序列号': self._generate_serial_number(),
            })
        return data

    def _generate_device_id(self):
        """生成设备ID（32位 hex）"""
        return ''.join(random.choices('0123456789abcdef', k=32))

    def _generate_imei(self):
        """生成IMEI（15位数字）"""
        # 常见 TAC 前缀
        tac = random.choice(['35362706', '35693803', '49015420', '35824005'])
        serial = ''.join(random.choices(string.digits, k=6))
        body = tac + serial
        # 简化：末位随机
        check = str(random.randint(0, 9))
        return body + check

    def _generate_android_id(self):
        """生成Android ID（16位 hex）"""
        return ''.join(random.choices('0123456789abcdef', k=16))

    def _generate_serial_number(self):
        """生成序列号（16位字母数字，每4位带-分隔）"""
        raw = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        return '-'.join(raw[i:i+4] for i in range(0, 16, 4))

    def get_fields(self):
        """返回字段列表"""
        return ['设备ID', 'IMEI', 'AndroidID', '序列号']
