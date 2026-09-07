# -*- coding: utf-8 -*-
"""
一次性生成平台 favicon 脚本。
样式参考顶部 logo：深灰底(#2b2b2b) + 白色边框 + 圆角 + 白色粗体 "A"。
输出：platform/static/favicon.ico（多尺寸）与 platform/static/favicon.png（64x64）
"""
import os
from PIL import Image, ImageDraw, ImageFont

# 输出目录
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
os.makedirs(OUT_DIR, exist_ok=True)


def make_icon(size):
    """生成单张指定尺寸的 logo 图标（深灰底 + 白边圆角框 + 白 A）。"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg = (43, 43, 43, 255)        # #2b2b2b
    border = (255, 255, 255, 255) # #fff
    border_w = max(2, size // 16)
    radius = max(2, size // 5)

    # 底层：深色圆角矩形（含边框区域）
    draw.rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=radius, fill=bg, outline=border, width=border_w
    )

    # 白色粗体 "A" 居中（放大 A 字，占满内框更多空间）
    font_size = int(size * 0.82)
    try:
        font = ImageFont.truetype('arialbd.ttf', font_size)
    except Exception:
        font = ImageFont.load_default()

    # 兼容新版 Pillow 文本测量
    try:
        bbox = draw.textbbox((0, 0), 'A', font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        ox, oy = bbox[0], bbox[1]
    except AttributeError:
        tw, th = draw.textsize('A', font=font)
        ox, oy = 0, 0

    x = (size - tw) / 2 - ox
    y = (size - th) / 2 - oy
    draw.text((x, y), 'A', font=font, fill=border)
    return img


def main():
    # 生成 PNG（64x64）
    png = make_icon(64)
    png.save(os.path.join(OUT_DIR, 'favicon.png'))
    print('favicon.png saved ->', os.path.join(OUT_DIR, 'favicon.png'))

    # 生成 ICO（多尺寸 16/32/48/64）
    sizes = [16, 32, 48, 64]
    icons = [make_icon(s) for s in sizes]
    ico_path = os.path.join(OUT_DIR, 'favicon.ico')
    icons[0].save(ico_path, format='ICO', sizes=[(s, s) for s in sizes])
    print('favicon.ico saved ->', ico_path)


if __name__ == '__main__':
    main()
