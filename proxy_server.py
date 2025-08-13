#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.parse
import json
from urllib.error import HTTPError, URLError

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 如果是API请求，转发到FastAPI
        if self.path.startswith('/api/') or self.path == '/health':
            try:
                # 转发到本地FastAPI
                target_url = f"http://localhost:5001{self.path}"
                print(f"代理请求: {self.path} -> {target_url}")
                
                with urllib.request.urlopen(target_url) as response:
                    content = response.read()
                    self.send_response(response.status)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', '*')
                    self.end_headers()
                    self.wfile.write(content)
                return
            except (HTTPError, URLError) as e:
                print(f"代理错误: {e}")
                self.send_error(502, f"Proxy Error: {e}")
                return
        
        # 其他请求按静态文件处理
        return super().do_GET()
    
    def do_OPTIONS(self):
        # 处理CORS预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
    
    def do_POST(self):
        # 转发POST请求到FastAPI
        if self.path.startswith('/api/'):
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                target_url = f"http://localhost:5001{self.path}"
                print(f"代理POST请求: {self.path} -> {target_url}")
                
                req = urllib.request.Request(target_url, data=post_data)
                req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req) as response:
                    content = response.read()
                    self.send_response(response.status)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(content)
                return
            except Exception as e:
                print(f"代理POST错误: {e}")
                self.send_error(502, f"Proxy Error: {e}")
                return
        
        return super().do_POST()

    def do_PUT(self):
        # 转发PUT请求到FastAPI
        if self.path.startswith('/api/'):
            try:
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                
                target_url = f"http://localhost:5001{self.path}"
                print(f"代理PUT请求: {self.path} -> {target_url}")
                
                req = urllib.request.Request(target_url, data=put_data, method='PUT')
                req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req) as response:
                    content = response.read()
                    self.send_response(response.status)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(content)
                return
            except Exception as e:
                print(f"代理PUT错误: {e}")
                self.send_error(502, f"Proxy Error: {e}")
                return
        
        return super().do_PUT()

    def do_DELETE(self):
        # 转发DELETE请求到FastAPI
        if self.path.startswith('/api/'):
            try:
                target_url = f"http://localhost:5001{self.path}"
                print(f"代理DELETE请求: {self.path} -> {target_url}")
                
                req = urllib.request.Request(target_url, method='DELETE')
                
                with urllib.request.urlopen(req) as response:
                    content = response.read()
                    self.send_response(response.status)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(content)
                return
            except Exception as e:
                print(f"代理DELETE错误: {e}")
                self.send_error(502, f"Proxy Error: {e}")
                return
        
        return super().do_DELETE()

if __name__ == "__main__":
    PORT = 8080
    Handler = ProxyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"代理服务器运行在端口 {PORT}")
        print(f"访问地址: http://140.143.194.215:{PORT}")
        print("API请求将自动转发到localhost:5001")
        httpd.serve_forever() 