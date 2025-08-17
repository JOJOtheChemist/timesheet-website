#!/bin/bash

# MCP Web界面启动脚本

echo "🚀 启动MCP Web界面服务器..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 启动Flask服务器
echo "🌐 启动Flask服务器..."
echo "📍 访问地址: http://localhost:5000"
echo "🔗 MCP API: http://localhost:5000/api/mcp"
echo "💡 按 Ctrl+C 停止服务器"

python3 app.py 