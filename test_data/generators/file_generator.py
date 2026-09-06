"""文件类生成器"""
import random
import string


class FileGenerator:
    """文件类生成器：文件名、扩展名、文件路径、MIME、文件大小"""

    # 常见扩展名 + 对应 MIME 映射
    EXT_MIME_MAP = {
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.mp3': 'audio/mpeg',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.zip': 'application/zip',
        '.rar': 'application/x-rar-compressed',
        '.7z': 'application/x-7z-compressed',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.py': 'text/x-python',
        '.java': 'text/x-java-source',
        '.c': 'text/x-csrc',
        '.cpp': 'text/x-c++src',
        '.md': 'text/markdown',
        '.csv': 'text/csv',
        '.sql': 'application/sql',
        '.exe': 'application/x-msdownload',
        '.apk': 'application/vnd.android.package-archive',
        '.ipa': 'application/octet-stream',
    }

    # 常见文件名词汇
    FILENAME_WORDS = [
        'report', 'data', 'image', 'doc', 'test', 'config', 'log', 'backup',
        'note', 'summary', 'plan', 'draft', 'final', 'temp', 'sample', 'demo',
        'export', 'import', 'record', 'cache', 'avatar', 'cover', 'screenshot',
        'evidence', 'invoice', 'contract', 'agreement', 'manual', 'guide',
    ]

    def __init__(self):
        pass

    def generate(self, count=1):
        """生成指定数量的文件类数据"""
        data = []
        for _ in range(count):
            ext = random.choice(list(self.EXT_MIME_MAP.keys()))
            filename = random.choice(self.FILENAME_WORDS) + '_' + ''.join(random.choices(string.digits, k=4)) + ext
            data.append({
                '文件名': filename,
                '扩展名': ext,
                '文件路径': self._generate_path(filename),
                'MIME': self.EXT_MIME_MAP[ext],
                '文件大小': self._generate_file_size(),
            })
        return data

    def _generate_path(self, filename):
        """生成文件路径"""
        depth = random.randint(1, 4)
        dirs = ['home', 'data', 'logs', 'tmp', 'var', 'opt', 'app', 'static', 'uploads', 'files']
        path = '/'.join(random.choices(dirs, k=depth))
        return '/' + path + '/' + filename

    def _generate_file_size(self):
        """生成文件大小（人类可读）"""
        size = random.randint(1, 1073741824)  # 1B - 1GB
        if size < 1024:
            return str(size) + ' B'
        elif size < 1024 * 1024:
            return str(round(size / 1024, 2)) + ' KB'
        elif size < 1024 * 1024 * 1024:
            return str(round(size / (1024 * 1024), 2)) + ' MB'
        else:
            return str(round(size / (1024 * 1024 * 1024), 2)) + ' GB'

    def get_fields(self):
        """返回字段列表"""
        return ['文件名', '扩展名', '文件路径', 'MIME', '文件大小']
