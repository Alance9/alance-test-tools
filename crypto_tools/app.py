"""加解密处理工具后端服务"""
from flask import Flask, render_template, request, jsonify
import base64
import hashlib
import hmac
import os
import json


app = Flask(__name__)


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


# ========== Base64 ==========
@app.route('/api/crypto/base64', methods=['POST'])
def crypto_base64():
    """Base64 加解密"""
    try:
        data = request.json
        text = data.get('text', '')
        op = data.get('op', 'encode')  # encode | decode
        if op == 'encode':
            result = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        else:
            result = base64.b64decode(text.encode('utf-8')).decode('utf-8')
        return jsonify({'success': True, 'result': result})
    except Exception as e:
            return jsonify({'success': False, 'error': 'Base64 处理失败，请检查输入内容'}), 400


# ========== MD5 / SHA ==========
@app.route('/api/crypto/hash', methods=['POST'])
def crypto_hash():
    """哈希加密"""
    try:
        data = request.json
        text = data.get('text', '')
        algo = data.get('algo', 'md5')  # md5 | sha1 | sha256 | sha512
        if algo == 'md5':
            h = hashlib.md5()
        elif algo == 'sha1':
            h = hashlib.sha1()
        elif algo == 'sha256':
            h = hashlib.sha256()
        elif algo == 'sha512':
            h = hashlib.sha512()
        else:
            return jsonify({'success': False, 'error': '不支持的加密算法'}), 400
        h.update(text.encode('utf-8'))
        return jsonify({'success': True, 'result': h.hexdigest()})
    except Exception as e:
        return jsonify({'success': False, 'error': '加密失败'}), 400


# ========== AES ==========
@app.route('/api/crypto/aes', methods=['POST'])
def crypto_aes():
    """AES 加解密"""
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad, unpad
        import hashlib as hl

        data = request.json
        text = data.get('text', '')
        key = data.get('key', '')
        op = data.get('op', 'encrypt')  # encrypt | decrypt
        mode = data.get('mode', 'CBC')  # CBC | ECB
        iv = data.get('iv', '')

        # 密钥处理：用 SHA256 生成 32 字节密钥
        key_bytes = hl.sha256(key.encode('utf-8')).digest()

        if mode == 'CBC':
            # IV 处理
            if iv:
                iv_bytes = iv.encode('utf-8')[:16].ljust(16, b'\x00')
            else:
                iv_bytes = os.urandom(16)
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        else:
            cipher = AES.new(key_bytes, AES.MODE_ECB)
            iv_bytes = b''

        if op == 'encrypt':
            ct = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
            result = base64.b64encode((iv_bytes + ct) if mode == 'CBC' else ct).decode()
        else:
            raw = base64.b64decode(text)
            if mode == 'CBC':
                iv_bytes = raw[:16]
                ct = raw[16:]
                cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
            else:
                ct = raw
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            result = pt.decode('utf-8')

        return jsonify({'success': True, 'result': result})
    except ImportError:
        return jsonify({'success': False, 'error': '请先安装 pycryptodome: pip install pycryptodome'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': 'AES 加解密失败，请检查密钥和输入内容'}), 400


# ========== RSA ==========
@app.route('/api/crypto/rsa', methods=['POST'])
def crypto_rsa():
    """RSA 加解密 / 签名验签"""
    try:
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_v1_5
        from Crypto.Signature import pkcs1_15
        from Crypto.Hash import SHA256

        data = request.json
        text = data.get('text', '')
        op = data.get('op', 'encrypt')  # encrypt | decrypt | sign | verify
        key_pem = data.get('key', '')

        if not key_pem:
            return jsonify({'success': False, 'error': '请输入密钥'}), 400

        if op in ('encrypt', 'sign'):
            key = RSA.import_key(key_pem)
        else:
            key = RSA.import_key(key_pem)

        if op == 'encrypt':
            cipher = PKCS1_v1_5.new(key)
            ct = cipher.encrypt(text.encode('utf-8'))
            return jsonify({'success': True, 'result': base64.b64encode(ct).decode()})
        elif op == 'decrypt':
            cipher = PKCS1_v1_5.new(key)
            ct = base64.b64decode(text)
            pt = cipher.decrypt(ct, None)
            if pt is None:
                return jsonify({'success': False, 'error': '解密失败，请检查私钥是否正确'}), 400
            return jsonify({'success': True, 'result': pt.decode('utf-8')})
        elif op == 'sign':
            h = SHA256.new(text.encode('utf-8'))
            signer = pkcs1_15.new(key)
            sig = signer.sign(h)
            return jsonify({'success': True, 'result': base64.b64encode(sig).decode()})
        elif op == 'verify':
            sig = base64.b64decode(data.get('signature', ''))
            h = SHA256.new(text.encode('utf-8'))
            verifier = pkcs1_15.new(key)
            try:
                verifier.verify(h, sig)
                return jsonify({'success': True, 'result': '验签通过'})
            except:
                return jsonify({'success': True, 'result': '验签失败'})
    except ImportError:
        return jsonify({'success': False, 'error': '请先安装 pycryptodome: pip install pycryptodome'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': 'RSA 操作失败，请检查密钥格式'}), 400


# ========== 编码转换 ==========
@app.route('/api/crypto/encoding', methods=['POST'])
def crypto_encoding():
    """编码转换"""
    try:
        data = request.json
        text = data.get('text', '')
        from_enc = data.get('from', 'utf-8').lower().replace('-', '')
        to_enc = data.get('to', 'utf-8').lower().replace('-', '')
        enc_map = {'utf8': 'utf-8', 'gbk': 'gbk', 'gb2312': 'gb2312', 'latin1': 'iso-8859-1', 'iso88591': 'iso-8859-1'}
        from_enc = enc_map.get(from_enc, from_enc)
        to_enc = enc_map.get(to_enc, to_enc)

        raw = text.encode(from_enc)
        result = raw.decode(to_enc)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': '编码转换失败，请检查输入和目标编码'}), 400


# ========== 密钥生成 ==========
@app.route('/api/crypto/generate_key', methods=['POST'])
def generate_key():
    """密钥生成"""
    try:
        data = request.json
        key_type = data.get('type', 'aes')  # aes | rsa
        if key_type == 'aes':
            length = int(data.get('length', 32))  # 16, 24, 32
            key = os.urandom(length)
            return jsonify({
                'success': True,
                'hex': key.hex(),
                'base64': base64.b64encode(key).decode(),
                'bytes': length,
            })
        elif key_type == 'rsa':
            length = int(data.get('length', 2048))  # 1024, 2048, 4096
            from Crypto.PublicKey import RSA
            key = RSA.generate(length)
            private_pem = key.export_key().decode()
            public_pem = key.publickey().export_key().decode()
            return jsonify({
                'success': True,
                'private_key': private_pem,
                'public_key': public_pem,
                'length': length,
            })
        else:
            return jsonify({'success': False, 'error': '不支持的密钥类型'}), 400
    except ImportError:
        return jsonify({'success': False, 'error': '请先安装 pycryptodome: pip install pycryptodome'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': '密钥生成失败'}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
