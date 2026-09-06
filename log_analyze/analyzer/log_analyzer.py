from collections import Counter, defaultdict
from datetime import datetime

class LogAnalyzer:
    def __init__(self, parsed_lines):
        self.parsed_lines = parsed_lines
    
    def get_level_distribution(self):
        counter = Counter(line.get('level', 'UNKNOWN') for line in self.parsed_lines)
        return dict(counter.most_common())
    
    def get_status_distribution(self):
        counter = Counter(line.get('status') for line in self.parsed_lines if 'status' in line)
        return dict(counter.most_common())
    
    def get_ip_distribution(self, top_n=10):
        counter = Counter(line.get('ip') for line in self.parsed_lines if 'ip' in line)
        return dict(counter.most_common(top_n))
    
    def get_url_distribution(self, top_n=10):
        counter = Counter(line.get('url') for line in self.parsed_lines if 'url' in line)
        return dict(counter.most_common(top_n))
    
    def get_method_distribution(self):
        counter = Counter(line.get('method') for line in self.parsed_lines if 'method' in line)
        return dict(counter.most_common())
    
    def get_time_distribution(self, interval='hour'):
        time_counts = defaultdict(int)
        
        for line in self.parsed_lines:
            if line.get('time'):
                dt = line['time']
                if interval == 'hour':
                    key = dt.strftime('%Y-%m-%d %H:00')
                elif interval == 'minute':
                    key = dt.strftime('%Y-%m-%d %H:%M')
                elif interval == 'day':
                    key = dt.strftime('%Y-%m-%d')
                else:
                    key = dt.strftime('%Y-%m-%d %H:00')
                time_counts[key] += 1
        
        return dict(sorted(time_counts.items()))
    
    def get_error_lines(self):
        return [line for line in self.parsed_lines if line.get('level') in ['ERROR', 'CRITICAL', 'FATAL']]
    
    def get_warning_lines(self):
        return [line for line in self.parsed_lines if line.get('level') in ['WARNING', 'WARN']]
    
    def search(self, keyword, case_sensitive=False):
        results = []
        for line in self.parsed_lines:
            text = line.get('message', '') + line.get('raw', '')
            if case_sensitive:
                if keyword in text:
                    results.append(line)
            else:
                if keyword.lower() in text.lower():
                    results.append(line)
        return results
    
    def get_summary(self):
        total = len(self.parsed_lines)
        levels = self.get_level_distribution()
        errors = levels.get('ERROR', 0) + levels.get('CRITICAL', 0) + levels.get('FATAL', 0)
        warnings = levels.get('WARNING', 0) + levels.get('WARN', 0)
        
        return {
            'total_lines': total,
            'error_count': errors,
            'warning_count': warnings,
            'info_count': levels.get('INFO', 0),
            'debug_count': levels.get('DEBUG', 0),
            'level_distribution': levels,
            'status_distribution': self.get_status_distribution(),
            'ip_distribution': self.get_ip_distribution(),
            'url_distribution': self.get_url_distribution(),
            'method_distribution': self.get_method_distribution(),
            'time_distribution': self.get_time_distribution(),
        }
