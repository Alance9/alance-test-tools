import re
from datetime import datetime

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'WARN', 'ERROR', 'CRITICAL', 'FATAL']

class LogParser:
    def __init__(self, log_format='auto'):
        self.log_format = log_format
        self.patterns = {
            'nginx': re.compile(
                r'^(?P<ip>\S+)\s+-\s+(?P<user>\S+)\s+\[(?P<time>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+(?P<protocol>\S+)"\s+(?P<status>\d+)\s+(?P<bytes>\d+)\s+"(?P<referer>[^"]*)"\s+"(?P<agent>[^"]*)"'
            ),
            'apache': re.compile(
                r'^(?P<ip>\S+)\s+-\s+(?P<user>\S+)\s+\[(?P<time>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+(?P<protocol>\S+)"\s+(?P<status>\d+)\s+(?P<bytes>\d+)'
            ),
            'application': re.compile(
                r'^(?P<time>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+(?P<level>[A-Z]+)\s+(?P<message>.*)'
            ),
            'application_bracket': re.compile(
                r'^\[(?P<time>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)\]\s+\[(?P<level>[A-Z]+)\]\s+(?P<message>.*)'
            ),
            'general': re.compile(
                r'^(?P<time>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\s*(?P<level>[A-Z]+)?\s*(?P<message>.*)'
            ),
        }
    
    def detect_format(self, log_text):
        lines = log_text.strip().split('\n')[:50]
        scores = {fmt: 0 for fmt in self.patterns}
        
        for line in lines:
            for fmt, pattern in self.patterns.items():
                if pattern.match(line):
                    scores[fmt] += 1
        
        if all(s == 0 for s in scores.values()):
            return 'general'
        
        return max(scores, key=scores.get)
    
    def parse_line(self, line, pattern):
        match = pattern.match(line)
        if not match:
            return None
        
        groups = match.groupdict()
        result = {
            'raw': line.strip(),
            'message': groups.get('message', line.strip()),
        }
        
        if 'ip' in groups:
            result['ip'] = groups['ip']
        if 'user' in groups:
            result['user'] = groups['user']
        if 'time' in groups:
            result['time'] = self._parse_time(groups['time'])
        if 'method' in groups:
            result['method'] = groups['method']
        if 'url' in groups:
            result['url'] = groups['url']
        if 'protocol' in groups:
            result['protocol'] = groups['protocol']
        if 'status' in groups:
            result['status'] = int(groups['status'])
        if 'bytes' in groups:
            result['bytes'] = int(groups['bytes'])
        if 'referer' in groups:
            result['referer'] = groups['referer']
        if 'agent' in groups:
            result['agent'] = groups['agent']
        
        level = groups.get('level', '').upper()
        if level in LOG_LEVELS:
            result['level'] = level
        else:
            result['level'] = self._infer_level(result['message'])
        
        return result
    
    def _parse_time(self, time_str):
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%d/%b/%Y:%H:%M:%S %z',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _infer_level(self, message):
        msg_upper = message.upper()
        if any(level in msg_upper for level in ['ERROR', 'EXCEPTION', 'FAILED', 'FATAL', 'CRITICAL']):
            return 'ERROR'
        elif any(level in msg_upper for level in ['WARN', 'WARNING']):
            return 'WARNING'
        elif any(level in msg_upper for level in ['INFO', 'SUCCESS']):
            return 'INFO'
        elif any(level in msg_upper for level in ['DEBUG', 'TRACE']):
            return 'DEBUG'
        return 'INFO'
    
    def parse(self, log_text):
        if self.log_format == 'auto':
            detected_format = self.detect_format(log_text)
            pattern = self.patterns[detected_format]
        else:
            pattern = self.patterns.get(self.log_format, self.patterns['general'])
        
        parsed_lines = []
        for line in log_text.strip().split('\n'):
            if line.strip():
                parsed = self.parse_line(line, pattern)
                if parsed:
                    parsed_lines.append(parsed)
        
        return parsed_lines
