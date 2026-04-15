#!/usr/bin/env python3
"""
抠图大师 - AI 背景移除服务器
"""

import os
import sys
import io
import json
import traceback
import cgi
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    from PIL import Image
    import numpy as np
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_POST(self):
        parsed = self.path
        if parsed == '/api/remove-bg':
            self.handle_remove_bg()
        else:
            self.send_error(404)

    def do_GET(self):
        parsed = self.path
        if parsed == '/api/status':
            self.handle_status()
        else:
            super().do_GET()

    def handle_status(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        status = {
            'status': 'ready',
            'pil': HAS_PIL,
            'rembg': HAS_REMBG,
            'message': '服务正常'
        }

        if not HAS_PIL:
            status['status'] = 'error'
            status['message'] = '请安装 Pillow: pip install pillow'
        elif not HAS_REMBG:
            status['status'] = 'warning'
            status['message'] = '将使用简单背景移除'

        self.wfile.write(json.dumps(status).encode())

    def handle_remove_bg(self):
        if not HAS_PIL:
            self.send_error_response('缺少 Pillow 库')
            return

        try:
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self.send_error_response('需要上传图片文件')
                return

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers.get('Content-Type'),
                }
            )

            if 'image' not in form:
                self.send_error_response('没有找到图片')
                return

            field = form['image']
            if not field.filename:
                self.send_error_response('没有选择文件')
                return

            input_data = field.file.read()
            input_img = Image.open(io.BytesIO(input_data)).convert('RGBA')

            if HAS_REMBG:
                output_img = remove(input_img)
            else:
                output_img = self.simple_remove_bg(input_img)

            output_buffer = io.BytesIO()
            output_img.save(output_buffer, format='PNG')
            output_data = output_buffer.getvalue()

            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', len(output_data))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(output_data)

        except Exception as e:
            traceback.print_exc()
            self.send_error_response(str(e))

    def simple_remove_bg(self, img):
        arr = np.array(img)
        bg_color = arr[0, 0]
        diff = np.abs(arr[:, :, :3].astype(int) - bg_color[:3].astype(int))
        distance = np.sqrt(np.sum(diff ** 2, axis=2))
        threshold = 50
        mask = distance < threshold
        arr[:, :, 3] = np.where(mask, 0, 255)
        return Image.fromarray(arr)

    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())


def main():
    port = int(os.environ.get('PORT', 8080))

    print(f"""
╔═══════════════════════════════════════════════╗
║           抠图大师 - AI 背景移除工具            ║
╠═══════════════════════════════════════════════╣
║  打开浏览器访问: http://localhost:{port}        ║
║  按 Ctrl+C 停止服务器                          ║
╚═══════════════════════════════════════════════╝
    """)

    if not HAS_PIL:
        print("⚠️  缺少 Pillow 库")
        print("   运行: pip install pillow")

    if not HAS_REMBG:
        print("⚠️  缺少 rembg 库 (AI 抠图)")
        print("   运行: pip install 'rembg[u2net]'")
        print("   将使用简单背景移除（效果较差）")

    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f"\n服务器已启动: http://localhost:{port}")
    print("=" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
