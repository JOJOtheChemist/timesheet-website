#!/usr/bin/env python3
"""
Flask后端服务器
作为MCP服务器和前端页面的桥梁
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import json
import logging
from datetime import datetime
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MCP服务器配置
MCP_SERVER_URL = "http://localhost:8001/api/mcp"  # MCP服务器地址

class MCPProxy:
    """MCP服务器代理类"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def send_request(self, method, params=None):
        """发送MCP请求"""
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": f"web_{datetime.now().timestamp()}",
                "method": method,
                "params": params or {}
            }
            
            logger.info(f"发送MCP请求: {method}")
            logger.info(f"MCP服务器URL: {self.base_url}")
            response = self.session.post(
                self.base_url,
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"MCP请求成功: {method}")
                return result
            else:
                logger.error(f"MCP请求失败: {method}, 状态码: {response.status_code}")
                return {
                    "error": {
                        "code": response.status_code,
                        "message": f"HTTP错误: {response.status_code}",
                        "details": response.text
                    }
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP请求异常: {method}, 错误: {e}")
            return {
                "error": {
                    "code": -1,
                    "message": f"网络错误: {str(e)}"
                }
            }
        except Exception as e:
            logger.error(f"MCP请求未知错误: {method}, 错误: {e}")
            return {
                "error": {
                    "code": -1,
                    "message": f"未知错误: {str(e)}"
                }
            }

# 创建MCP代理实例
mcp_proxy = MCPProxy(MCP_SERVER_URL)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')



@app.route('/api/mcp', methods=['POST'])
def mcp_proxy_endpoint():
    """MCP代理端点"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的JSON数据"}), 400
        
        method = data.get('method')
        params = data.get('params', {})
        
        if not method:
            return jsonify({"error": "缺少method参数"}), 400
        
        # 转发请求到MCP服务器
        result = mcp_proxy.send_request(method, params)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"处理MCP请求时发生错误: {e}")
        return jsonify({
            "error": {
                "code": -1,
                "message": f"服务器内部错误: {str(e)}"
            }
        }), 500

@app.route('/api/health')
def health_check():
    """健康检查端点"""
    try:
        # 测试MCP服务器连接
        result = mcp_proxy.send_request('initialize')
        
        if 'error' in result:
            return jsonify({
                "status": "error",
                "mcp_server": "disconnected",
                "error": result['error'],
                "timestamp": datetime.now().isoformat()
            }), 503
        else:
            return jsonify({
                "status": "healthy",
                "mcp_server": "connected",
                "server_info": result.get('result', {}).get('serverInfo', {}),
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "mcp_server": "unknown",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/tools')
def list_tools():
    """获取可用工具列表"""
    result = mcp_proxy.send_request('tools/list')
    return jsonify(result)

@app.route('/api/resources')
def list_resources():
    """获取可用资源列表"""
    result = mcp_proxy.send_request('resources/list')
    return jsonify(result)

@app.route('/api/schedule/<date>')
def get_schedule(date):
    """获取指定日期的日程"""
    result = mcp_proxy.send_request('tools/call', {
        "name": "get_schedule",
        "arguments": {"date": date}
    })
    return jsonify(result)

@app.route('/api/projects')
def get_projects():
    """获取项目列表"""
    result = mcp_proxy.send_request('tools/call', {
        "name": "get_projects",
        "arguments": {}
    })
    return jsonify(result)

@app.route('/api/ai-analyze', methods=['POST'])
def ai_analyze():
    """AI分析用户请求"""
    try:
        data = request.get_json()
        user_request = data.get('user_request', '')
        
        if not user_request:
            return jsonify({"error": "缺少user_request参数"}), 400
        
        result = mcp_proxy.send_request('tools/call', {
            "name": "ai_analyze",
            "arguments": {"user_request": user_request}
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI分析请求失败: {e}")
        return jsonify({
            "error": {
                "code": -1,
                "message": f"AI分析失败: {str(e)}"
            }
        }), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory('static', filename)

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({"error": "页面未找到"}), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({"error": "服务器内部错误"}), 500

if __name__ == '__main__':
    # 检查MCP服务器是否可用
    logger.info("启动Flask后端服务器...")
    logger.info(f"MCP服务器地址: {MCP_SERVER_URL}")
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    ) 