"""图片处理工具后端服务"""
from flask import Flask, render_template, request, jsonify, Response
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


def pil_to_base64(img, fmt='PNG'):
    """PIL Image 转 base64"""
    buf = io.BytesIO()
    if fmt.upper() == 'JPG' or fmt.upper() == 'JPEG':
        fmt = 'JPEG'
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
    img.save(buf, format=fmt)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def base64_to_pil(b64_str):
    """base64 转 PIL Image"""
    data = base64.b64decode(b64_str)
    return Image.open(io.BytesIO(data))


@app.route('/api/image/crop', methods=['POST'])
def image_crop():
    """图片裁剪"""
    try:
        data = request.json
        img = base64_to_pil(data['image'])
        x = int(data.get('x', 0))
        y = int(data.get('y', 0))
        w = int(data.get('width', img.width))
        h = int(data.get('height', img.height))
        cropped = img.crop((x, y, x + w, y + h))
        fmt = data.get('format', 'PNG')
        return jsonify({'success': True, 'image': pil_to_base64(cropped, fmt), 'format': fmt.lower()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/image/watermark', methods=['POST'])
def image_watermark():
    """图片水印"""
    try:
        data = request.json
        img = base64_to_pil(data['image'])
        text = data.get('text', '')
        position = data.get('position', 'bottom-right')
        opacity = float(data.get('opacity', 0.3))
        fmt = data.get('format', 'PNG')

        layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        try:
            font = ImageFont.truetype('arial.ttf', 30)
        except:
            font = ImageFont.load_default()

        # 计算位置
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        margin = 20
        positions = {
            'top-left': (margin, margin),
            'top-right': (img.width - tw - margin, margin),
            'bottom-left': (margin, img.height - th - margin),
            'bottom-right': (img.width - tw - margin, img.height - th - margin),
            'center': ((img.width - tw) // 2, (img.height - th) // 2),
        }
        pos = positions.get(position, positions['bottom-right'])
        fill = (255, 255, 255, int(255 * opacity)) if data.get('color', 'white') == 'white' else (0, 0, 0, int(255 * opacity))
        draw.text(pos, text, fill=fill, font=font)

        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        result = Image.alpha_composite(img, layer)
        return jsonify({'success': True, 'image': pil_to_base64(result, fmt), 'format': fmt.lower()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/image/compress', methods=['POST'])
def image_compress():
    """图片压缩"""
    try:
        data = request.json
        img = base64_to_pil(data['image'])
        quality = int(data.get('quality', 70))
        max_width = int(data.get('max_width', 0))

        if max_width > 0 and img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

        fmt = data.get('format', 'JPEG')
        buf = io.BytesIO()
        if fmt.upper() in ('JPG', 'JPEG'):
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            img.save(buf, format='JPEG', quality=quality, optimize=True)
        else:
            img.save(buf, format=fmt.upper())
        buf.seek(0)
        return jsonify({'success': True, 'image': base64.b64encode(buf.read()).decode(), 'format': fmt.lower()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/image/convert', methods=['POST'])
def image_convert():
    """格式转换"""
    try:
        data = request.json
        img = base64_to_pil(data['image'])
        target_fmt = data.get('target_format', 'JPG').upper()

        if target_fmt == 'JPG':
            target_fmt = 'JPEG'
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

        buf = io.BytesIO()
        img.save(buf, format=target_fmt)
        buf.seek(0)
        return jsonify({'success': True, 'image': base64.b64encode(buf.read()).decode(), 'format': target_fmt.lower()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/image/batch_convert', methods=['POST'])
def batch_convert():
    """批量格式转换（单张失败不影响其他，返回新文件名与正确扩展名）"""
    try:
        data = request.json
        images = data.get('images', [])
        target_fmt = data.get('target_format', 'JPG').upper()
        # 保存格式与下载扩展名
        save_fmt = 'JPEG' if target_fmt == 'JPG' else target_fmt
        ext = 'jpg' if target_fmt == 'JPG' else target_fmt.lower()

        results = []
        for item in images:
            orig_name = item.get('name', 'image.png')
            base = orig_name.rsplit('.', 1)[0] if '.' in orig_name else orig_name
            try:
                img = base64_to_pil(item['image'])
                # JPEG 不支持透明通道，需铺白底
                if save_fmt == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGBA')
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif save_fmt in ('JPEG', 'BMP') and img.mode != 'RGB':
                    img = img.convert('RGB')
                buf = io.BytesIO()
                img.save(buf, format=save_fmt)
                buf.seek(0)
                results.append({
                    'success': True,
                    'name': f'{base}_converted.{ext}',
                    'image': base64.b64encode(buf.read()).decode(),
                    'format': ext
                })
            except Exception as e:
                results.append({'success': False, 'name': orig_name, 'error': f'转换失败：{str(e)}'})
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/pdf/to_images', methods=['POST'])
def pdf_to_images():
    """PDF 转图片"""
    try:
        import fitz  # PyMuPDF
        data = request.json
        pdf_bytes = base64.b64decode(data['pdf'])
        doc = fitz.open(stream=pdf_bytes, filetype='pdf')
        images = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            images.append({'page': i + 1, 'image': pil_to_base64(img, 'JPEG')})
        doc.close()
        return jsonify({'success': True, 'images': images})
    except ImportError:
        return jsonify({'success': False, 'error': '请先安装 PyMuPDF: pip install pymupdf'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/images/to_pdf', methods=['POST'])
def images_to_pdf():
    """图片转 PDF"""
    try:
        data = request.json
        images_data = data.get('images', [])
        pil_images = []
        for item in images_data:
            img = base64_to_pil(item['image'])
            if img.mode != 'RGB':
                img = img.convert('RGB')
            pil_images.append(img)

        buf = io.BytesIO()
        pil_images[0].save(buf, format='PDF', save_all=True, append_images=pil_images[1:])
        buf.seek(0)
        return jsonify({'success': True, 'pdf': base64.b64encode(buf.read()).decode()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
