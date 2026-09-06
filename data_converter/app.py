"""数据格式转换工具后端服务"""
from flask import Flask, render_template, request, jsonify, Response
import json
import csv
import io
import xml.etree.ElementTree as ET
from datetime import datetime


app = Flask(__name__)


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/timestamp/convert', methods=['POST'])
def timestamp_convert():
    """时间戳转换"""
    try:
        data = request.json
        value = data.get('value', '').strip()
        convert_type = data.get('type', 'to_date')  # to_date | to_timestamp

        if not value:
            return jsonify({'success': False, 'error': '请输入有效的时间戳或日期'}), 400

        if convert_type == 'to_date':
            # 时间戳 -> 日期
            try:
                ts = int(float(value))
            except ValueError:
                return jsonify({'success': False, 'error': '请输入有效的时间戳（数字）'}), 400

            if ts > 1e12:  # 毫秒
                ts = ts / 1000
            if ts < 0:
                return jsonify({'success': False, 'error': '时间戳不能为负数'}), 400

            dt = datetime.fromtimestamp(ts)
            return jsonify({
                'success': True,
                'result': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'ms': int(ts * 1000),
                's': int(ts),
            })
        else:
            # 日期 -> 时间戳
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d %H:%M',
                '%Y/%m/%d',
            ]
            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue

            if dt is None:
                return jsonify({'success': False, 'error': '日期格式不正确，支持格式如：2025-01-01 12:00:00'}), 400

            ts = int(dt.timestamp())
            return jsonify({
                'success': True,
                's': ts,
                'ms': ts * 1000,
            })
    except Exception as e:
        return jsonify({'success': False, 'error': f'转换失败：{str(e)}'}), 400


@app.route('/api/qrcode/generate', methods=['POST'])
def qrcode_generate():
    """生成二维码（返回PNG base64）"""
    try:
        from io import BytesIO
        import base64
        import qrcode
        data = request.json.get('data', '')
        if not data:
            return jsonify({'success': False, 'error': '请输入内容'}), 400

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode()
        return jsonify({'success': True, 'image': f'data:image/png;base64,{img_b64}'})
    except ImportError:
        return jsonify({'success': False, 'error': '请先安装 qrcode 和 Pillow: pip install "qrcode[pil]"'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'生成失败：{str(e)}'}), 400


@app.route('/api/barcode/generate', methods=['POST'])
def barcode_generate():
    """生成条形码（Code128，返回PNG base64）"""
    try:
        from io import BytesIO
        import base64
        from barcode.codex import Code128
        from barcode.writer import ImageWriter

        data = request.json.get('data', '')
        if not data:
            return jsonify({'success': False, 'error': '请输入条形码内容'}), 400

        # Code128 支持字母和数字，限制长度
        if len(data) > 40:
            return jsonify({'success': False, 'error': '条形码内容过长（最多40字符）'}), 400

        buf = BytesIO()
        Code128(data, writer=ImageWriter()).write(buf, options={'write_text': True, 'module_height': 15.0})
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode()
        return jsonify({'success': True, 'image': f'data:image/png;base64,{img_b64}'})
    except ImportError:
        return jsonify({'success': False, 'error': '请先安装 python-barcode 和 Pillow: pip install python-barcode Pillow'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'生成失败：{str(e)}'}), 400


@app.route('/api/convert/upload', methods=['POST'])
def convert_upload():
    """文件上传后转换（支持 JSON→CSV/Excel/XML, CSV→JSON）"""
    try:
        convert_type = request.form.get('type', '')
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '请选择要上传的文件'}), 400

        file = request.files['file']
        filename = file.filename
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        content = file.read()

        # 根据扩展名和转换类型处理
        if convert_type in ('json_to_csv', 'json_to_excel', 'json_to_xml'):
            # 输入必须是 JSON 文件
            if ext != 'json':
                return jsonify({'success': False, 'error': '请上传 JSON 文件'}), 400

            try:
                text = content.decode('utf-8-sig')
                obj = json.loads(text)
            except UnicodeDecodeError:
                try:
                    text = content.decode('gbk')
                    obj = json.loads(text)
                except Exception:
                    return jsonify({'success': False, 'error': 'JSON 文件编码错误'}), 400
            except json.JSONDecodeError as e:
                return jsonify({'success': False, 'error': f'JSON格式错误：{str(e)}'}), 400

            if convert_type == 'json_to_csv':
                return _json_to_csv(obj)
            elif convert_type == 'json_to_excel':
                return _json_to_excel(obj)
            elif convert_type == 'json_to_xml':
                return _json_to_xml(obj)

        elif convert_type == 'csv_to_json':
            # 输入必须是 CSV 文件
            if ext != 'csv':
                return jsonify({'success': False, 'error': '请上传 CSV 文件'}), 400

            try:
                text = content.decode('utf-8-sig')
            except UnicodeDecodeError:
                text = content.decode('gbk', errors='ignore')

            reader = csv.DictReader(io.StringIO(text))
            rows = list(reader)
            return jsonify({
                'success': True,
                'result': json.dumps(rows, ensure_ascii=False, indent=2),
                'filename': filename.rsplit('.', 1)[0] + '.json',
            })
        else:
            return jsonify({'success': False, 'error': '未知的转换类型'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': f'转换失败：{str(e)}'}), 400


def _json_to_csv(obj):
    """JSON 对象转 CSV"""
    arr = obj if isinstance(obj, list) else [obj]
    if not arr:
        return jsonify({'success': False, 'error': 'JSON 数据为空'}), 400

    fields = list(arr[0].keys())
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(fields)
    for row in arr:
        writer.writerow([str(row.get(f, '')) for f in fields])

    return jsonify({
        'success': True,
        'result': output.getvalue(),
        'filename': 'output.csv',
    })


def _json_to_excel(obj):
    """JSON 对象转 Excel"""
    try:
        from openpyxl import Workbook
    except ImportError:
        return jsonify({'success': False, 'error': '请先安装 openpyxl: pip install openpyxl'}), 500

    arr = obj if isinstance(obj, list) else [obj]
    if not arr:
        return jsonify({'success': False, 'error': 'JSON 数据为空'}), 400

    wb = Workbook()
    ws = wb.active
    ws.title = 'Sheet1'
    fields = list(arr[0].keys())
    ws.append(fields)
    for row in arr:
        ws.append([str(row.get(f, '')) for f in fields])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    import base64
    return jsonify({
        'success': True,
        'file': base64.b64encode(buf.read()).decode(),
        'filename': 'output.xlsx',
    })


def _json_to_xml(obj):
    """JSON 对象转 XML"""
    def dict_to_xml(tag, d):
        elements = []
        if isinstance(d, dict):
            for k, v in d.items():
                elements.append(dict_to_xml(str(k), v))
        elif isinstance(d, list):
            for item in d:
                elements.append(dict_to_xml('item', item))
        else:
            elements.append(str(d))
        return f'<{tag}>' + ''.join(elements) + f'</{tag}>'

    if isinstance(obj, list):
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<root>'
        for item in obj:
            xml_str += dict_to_xml('item', item)
        xml_str += '</root>'
    else:
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + dict_to_xml('root', obj)

    return jsonify({
        'success': True,
        'result': xml_str,
        'filename': 'output.xml',
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
