from flask import Flask, render_template, request, jsonify
from analyzer import LogParser, LogAnalyzer

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_log():
    log_text = request.json.get('log_text', '')
    log_format = request.json.get('log_format', 'auto')
    
    if not log_text.strip():
        return jsonify({'error': '日志内容不能为空'}), 400
    
    parser = LogParser(log_format=log_format)
    parsed_lines = parser.parse(log_text)
    
    if not parsed_lines:
        return jsonify({'error': '未能解析任何日志行'}), 400
    
    analyzer = LogAnalyzer(parsed_lines)
    summary = analyzer.get_summary()
    
    lines_for_table = []
    for line in parsed_lines:
        line_data = {
            'raw': line.get('raw', ''),
            'level': line.get('level', 'INFO'),
            'time': line['time'].strftime('%Y-%m-%d %H:%M:%S') if line.get('time') else '',
            'message': line.get('message', '')[:200],
            'ip': line.get('ip', ''),
            'status': line.get('status', ''),
            'url': line.get('url', ''),
            'method': line.get('method', ''),
        }
        lines_for_table.append(line_data)
    
    return jsonify({
        'success': True,
        'summary': summary,
        'lines': lines_for_table[:1000],
        'total_lines': len(parsed_lines),
        'displayed_lines': min(len(parsed_lines), 1000),
    })

@app.route('/api/search', methods=['POST'])
def search_log():
    log_text = request.json.get('log_text', '')
    keyword = request.json.get('keyword', '')
    case_sensitive = request.json.get('case_sensitive', False)
    
    if not log_text.strip():
        return jsonify({'error': '日志内容不能为空'}), 400
    
    if not keyword.strip():
        return jsonify({'error': '搜索关键词不能为空'}), 400
    
    parser = LogParser(log_format='auto')
    parsed_lines = parser.parse(log_text)
    
    analyzer = LogAnalyzer(parsed_lines)
    results = analyzer.search(keyword, case_sensitive)
    
    lines_for_table = []
    for line in results:
        line_data = {
            'raw': line.get('raw', ''),
            'level': line.get('level', 'INFO'),
            'time': line['time'].strftime('%Y-%m-%d %H:%M:%S') if line.get('time') else '',
            'message': line.get('message', '')[:200],
            'ip': line.get('ip', ''),
            'status': line.get('status', ''),
            'url': line.get('url', ''),
            'method': line.get('method', ''),
        }
        lines_for_table.append(line_data)
    
    return jsonify({
        'success': True,
        'keyword': keyword,
        'results': lines_for_table[:1000],
        'total_results': len(results),
        'displayed_results': min(len(results), 1000),
    })

@app.route('/api/sample', methods=['GET'])
def get_sample_log():
    sample = """2024-01-15 10:00:01 INFO User login successful: user123
2024-01-15 10:00:02 DEBUG Database query executed in 15ms
2024-01-15 10:00:05 WARNING Rate limit exceeded for IP: 192.168.1.100
2024-01-15 10:00:10 ERROR Connection timeout while connecting to database
2024-01-15 10:00:15 INFO Request processed: /api/users, status: 200, duration: 50ms
2024-01-15 10:00:20 INFO User login successful: admin
2024-01-15 10:00:25 ERROR Failed to process request: /api/orders, error: Internal Server Error
2024-01-15 10:00:30 WARNING Memory usage exceeded 80% threshold
2024-01-15 10:00:35 DEBUG Cache hit for key: user_session_abc123
2024-01-15 10:00:40 INFO User logout: user123
2024-01-15 10:00:45 CRITICAL Server health check failed
2024-01-15 10:00:50 INFO Request processed: /api/products, status: 200, duration: 30ms
2024-01-15 10:00:55 WARNING Slow query detected: SELECT * FROM large_table
2024-01-15 10:01:00 INFO User login successful: guest
2024-01-15 10:01:05 ERROR Authentication failed for user: invalid_user
"""
    return jsonify({'success': True, 'sample': sample})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5009)
