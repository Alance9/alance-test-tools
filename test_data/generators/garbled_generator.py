"""乱码生成器"""
import random
import string


class GarbledGenerator:
    """乱码生成器：用于测试乱码场景"""

    def __init__(self):
        pass

    def generate(self, count=1):
        """生成指定数量的乱码数据"""
        data = []
        for _ in range(count):
            data.append({
                '乱码': self._generate_garbled(),
            })
        return data

    def _generate_garbled(self):
        """生成乱码字符串"""
        # 模拟各种乱码场景
        mode = random.randint(0, 3)
        length = random.randint(8, 30)
        if mode == 0:
            # 随机可见 ASCII
            return ''.join(random.choices(string.printable.strip(), k=length))
        elif mode == 1:
            # 模拟 UTF-8 被当作 GBK 解析的乱码
            return ''.join(chr(random.randint(0x80, 0xff)) for _ in range(length))
        elif mode == 2:
            # 模拟 Base64 误读
            chars = string.ascii_letters + string.digits + '+/='
            return ''.join(random.choices(chars, k=length))
        else:
            # 混合控制字符和符号
            return ''.join(chr(random.randint(0x20, 0x7e)) for _ in range(length))

    def get_fields(self):
        """返回字段列表"""
        return ['乱码']
