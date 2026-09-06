"""网络类生成器"""
from faker import Faker
import random
import string
import time


class NetworkGenerator:
    """网络类生成器：traceId、requestId、IPv6、MAC、IP、端口、URL、User-Agent"""

    # 常见 User-Agent 列表
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'PostmanRuntime/7.36.0',
        'curl/8.4.0',
        'okhttp/4.12.0',
        'Apache-HttpClient/4.5.14 (Java/17.0.9)',
    ]

    def __init__(self):
        self.fake = Faker('zh_CN')

    def generate(self, count=1):
        """生成指定数量的网络类数据"""
        data = []
        for _ in range(count):
            data.append({
                'traceId': self._generate_trace_id(),
                'requestId': self._generate_request_id(),
                'IPv6': self.fake.ipv6(),
                'IPv4': self.fake.ipv4_private(),
                'MAC': self.fake.mac_address(),
                '端口': random.randint(1024, 65535),
                'URL': self.fake.url(),
                'User-Agent': random.choice(self.USER_AGENTS),
            })
        return data

    def _generate_trace_id(self):
        """生成 traceId（32位 hex）"""
        return ''.join(random.choices(string.hexdigits[:16].lower(), k=32))

    def _generate_request_id(self):
        """生成 requestId，格式：req_时间戳_随机字符串（参考 req_1788683365555_r68hk70i）"""
        ts = int(time.time() * 1000)  # 毫秒时间戳
        rand_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f'req_{ts}_{rand_part}'

    def get_fields(self):
        """返回字段列表"""
        return ['traceId', 'requestId', 'IPv6', 'IPv4', 'MAC', '端口', 'URL', 'User-Agent']
