"""测试数据生成器后端服务"""
from flask import Flask, render_template, request, jsonify, Response
from generators import (
    BasicInfoGenerator, NetworkGenerator, AccountGenerator,
    EnterpriseGenerator, AddressExGenerator, DeviceGenerator,
    TransactionGenerator, SecurityGenerator, TextExGenerator,
    FileGenerator, RareCharGenerator, GarbledGenerator,
    RandomTextGenerator,
)
import json


app = Flask(__name__)

# 全局随机文本生成器实例
random_text_gen = RandomTextGenerator()


# 分类配置：key -> 名称 + 生成器实例（随机文本放第一列）
CATEGORIES = {
    'random_text': {'name': '随机文本', 'generator': random_text_gen},
    'basic':       {'name': '基础信息', 'generator': BasicInfoGenerator()},
    'network':     {'name': '网络类',   'generator': NetworkGenerator()},
    'account':     {'name': '账号类',   'generator': AccountGenerator()},
    'enterprise':  {'name': '企业类',   'generator': EnterpriseGenerator()},
    'address':     {'name': '地址类',   'generator': AddressExGenerator()},
    'device':      {'name': '设备类',   'generator': DeviceGenerator()},
    'transaction': {'name': '交易类',   'generator': TransactionGenerator()},
    'security':    {'name': '安全类',   'generator': SecurityGenerator()},
    'text':        {'name': '文本类',   'generator': TextExGenerator()},
    'file':        {'name': '文件类',   'generator': FileGenerator()},
    'rare':        {'name': '生僻字',   'generator': RareCharGenerator()},
    'garbled':     {'name': '乱码',     'generator': GarbledGenerator()},
}


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/generate', methods=['POST'])
def generate_data():
    """生成数据接口"""
    data_type = request.json.get('data_type', 'basic')
    count = int(request.json.get('count', 10))

    if data_type not in CATEGORIES:
        return jsonify({'error': '不支持的数据类型'}), 400

    if count < 1 or count > 10000:
        return jsonify({'error': '数量必须在1-10000之间'}), 400

    generator = CATEGORIES[data_type]['generator']
    data = generator.generate(count)

    return jsonify({
        'success': True,
        'data_type': CATEGORIES[data_type]['name'],
        'count': count,
        'data': data,
        'fields': generator.get_fields(),
    })


@app.route('/api/generate/random_text', methods=['POST'])
def generate_random_text():
    """根据选项生成随机文本（专用接口）"""
    options = request.json.get('options', ['简体中文'])
    length = int(request.json.get('length', 20))
    line_wrap = int(request.json.get('line_wrap', 0))

    if length < 1 or length > 5000:
        return jsonify({'error': '长度必须在1-5000之间'}), 400

    if not options:
        return jsonify({'error': '请至少选择一种字符类型'}), 400

    text = random_text_gen.generate_with_options(options, length, line_wrap)

    return jsonify({
        'success': True,
        'text': text,
    })


@app.route('/api/random_text_options', methods=['GET'])
def get_random_text_options():
    """获取随机文本可选项"""
    return jsonify({
        'success': True,
        'options': random_text_gen.get_options(),
    })


@app.route('/api/download/csv', methods=['POST'])
def download_csv():
    """导出CSV接口"""
    data_type = request.json.get('data_type', 'basic')
    count = int(request.json.get('count', 10))

    if data_type not in CATEGORIES:
        return jsonify({'error': '不支持的数据类型'}), 400

    generator = CATEGORIES[data_type]['generator']
    data = generator.generate(count)

    if not data:
        return jsonify({'error': '生成数据失败'}), 500

    fields = generator.get_fields()

    def generate():
        yield ','.join(fields) + '\n'
        for row in data:
            yield ','.join('"' + str(row.get(field, '')).replace('"', '""') + '"' for field in fields) + '\n'

    return Response(generate(), mimetype='text/csv', headers={
        'Content-Disposition': f'attachment; filename={data_type}_data.csv',
    })


@app.route('/api/download/json', methods=['POST'])
def download_json():
    """导出JSON接口"""
    data_type = request.json.get('data_type', 'basic')
    count = int(request.json.get('count', 10))

    if data_type not in CATEGORIES:
        return jsonify({'error': '不支持的数据类型'}), 400

    generator = CATEGORIES[data_type]['generator']
    data = generator.generate(count)

    return Response(json.dumps(data, ensure_ascii=False, indent=2), mimetype='application/json', headers={
        'Content-Disposition': f'attachment; filename={data_type}_data.json',
    })


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取所有分类及字段信息"""
    return jsonify({
        'success': True,
        'categories': [{
            'key': key,
            'name': value['name'],
            'fields': value['generator'].get_fields(),
        } for key, value in CATEGORIES.items()]
    })


@app.route('/api/generate/single', methods=['POST'])
def generate_single():
    """刷新单个字段值：重新生成一条数据并返回指定字段的值"""
    data_type = request.json.get('data_type', 'basic')
    field = request.json.get('field', '')

    if data_type not in CATEGORIES:
        return jsonify({'error': '不支持的数据类型'}), 400

    generator = CATEGORIES[data_type]['generator']
    fields = generator.get_fields()
    if field not in fields:
        return jsonify({'error': f'不支持的字段：{field}'}), 400

    data = generator.generate(1)
    value = data[0].get(field, '')

    return jsonify({
        'success': True,
        'field': field,
        'value': value,
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
