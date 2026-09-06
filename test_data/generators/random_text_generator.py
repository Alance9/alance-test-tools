"""随机文本生成器"""
import random
import string


class RandomTextGenerator:
    """随机文本生成器：支持数字、英文字母、简体中文、繁体中文、英文符号、中文符号、生僻字、乱码等多选混合"""

    # 字符集定义
    CHARSET = {
        '数字': string.digits,
        '英文字母': string.ascii_letters,
        '简体中文': '的一是不了人我在有他这为之大来以个中上们到说时地也子就道要于下得可你生自之会发年着动后过天去能对小多然于心学么之都好看起发当没成只如事把还用第样道想作种开美总从无情己面最女但现前些所同日手又行意动方期它头经儿长回位分爱因给法在此活新而进度知世什两次使身者被高亲其进此话常与活正感见明问力理尔点文本电水义加林相由机工物气每并真打太比向忘命旧此仍怎目才二公已当吃变三找让级张今解义我衣些因外天政四日那社义事平形相全表间样与关各重新线内数正心你看原又么利比或质气第向道命此变条只没结解问意建月公无系军很情者最光外将信件计管期被华找但量音刻交父价加东石脑依请国觉应也像办包友等把层目上解让教间也话并因素热都体政法公高住流将复支物里断近内小感文争冷识请证育红速史才受计拉何山消义谓守金界清办强湖发农命神难况尽儿打门风通公全业愿才妈直其平数相专经层飞进善基党新量构划联价电内数劳使教育文动延些质识满服优保药食均七山专负九固威乡电意快法商六代及利协取故医终古继工杂哥世打说乱个利外产态改',
        '繁体中文': '愛樂東車長門問風飛過進見時開學國圖圓與舉齊龍龜鳳無為變聽買賣書畫讀說話語誰謝請這那樣麼個來時後臺灣華僑會計記試詩醫藥體裡衛東西南北中辦公處廠廳廚廁關係發變單帶廣開闊強無舊親觀難點鹽黨獨獻鐘讀觀點變黨變舊親觀難點鹽黨獨獻鐘獨',
        '英文符号': '!@#$%^&*()_+-=[]{}|;:,.<>?/~`',
        '中文符号': '，。！？、；：""''（）《》【】〈〉〔〕『』「」—…·～￥',
        '生僻字': '龘驫羴犇猋麤爩靐齉齾龗龞龡龢龣龥齆齇齈齋齌齍齎齏齔齕齖齗齘齙齚齛齜齝齞齟齠齡齢齣齤齥齦齧齨齩齪齫齬齭齮齯齰齱齲齳齴齵齶齷齹齺齻齼齽齾龀龁龂龃',
        '乱码': '锟斤拷烫烫烫屯屯屯閿欒浠ｇ爜鍒濆鍐呴厤缃凯涓嶅悎娉曟煡璇嗛敭鍥炲瓧绗︿覆鍙戠幇娴嬭懌绗﹀瀵熷疄璺佃寖鍥村お澶у彈绗旂ず鑼冮敭鍥炴煍娲荤姳鍗',
    }

    # 完整选项列表（顺序固定）
    OPTIONS = ['数字', '英文字母', '简体中文', '繁体中文', '英文符号', '中文符号', '生僻字', '乱码']

    def __init__(self):
        pass

    def generate(self, count=1):
        """
        生成指定数量的随机文本
        count: 生成条数
        """
        data = []
        for _ in range(count):
            data.append({
                '随机文本': self._generate_text(),
            })
        return data

    def generate_with_options(self, options, length=20, line_wrap=0):
        """
        根据指定选项生成随机文本
        options: list of str, 选中的字符集选项
        length: 总长度
        line_wrap: 每行个数（0表示不换行）
        """
        chars = self._get_chars(options)
        if not chars:
            return ''
        text = ''.join(random.choices(chars, k=length))
        if line_wrap > 0:
            lines = [text[i:i + line_wrap] for i in range(0, length, line_wrap)]
            text = '\n'.join(lines)
        return text

    def _get_chars(self, options):
        """根据选项获取所有可用字符"""
        chars = ''
        for opt in options:
            if opt in self.CHARSET:
                chars += self.CHARSET[opt]
        return chars

    def _generate_text(self):
        """默认生成：简体中文+数字混合"""
        return self.generate_with_options(['简体中文', '数字'], length=20)

    def get_fields(self):
        """返回字段列表"""
        return ['随机文本']

    def get_options(self):
        """返回可选项列表"""
        return self.OPTIONS
