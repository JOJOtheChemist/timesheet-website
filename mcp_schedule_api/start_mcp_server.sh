#!/bin/bash

echo "🚀 启动 MCP Schedule API Server..."

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "🐍 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "📚 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 设置执行权限
chmod +x mcp_schedule_server.py

# 启动MCP服务器
echo "🌐 启动MCP服务器..."
python3 mcp_schedule_server.py

echo "✅ MCP服务器已启动！"
echo "📖 查看日志了解运行状态" 