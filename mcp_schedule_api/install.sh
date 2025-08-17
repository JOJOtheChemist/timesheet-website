#!/bin/bash

echo "🚀 安装 MCP Schedule API Server..."

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "❌ 请不要使用root用户运行此脚本"
    exit 1
fi

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi

echo "✅ Python3 已安装: $(python3 --version)"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "🐍 创建虚拟环境..."
    python3 -m venv venv
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境并安装依赖
echo "📚 安装Python依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 设置脚本权限
echo "🔧 设置脚本权限..."
chmod +x start_mcp_server.sh

# 安装systemd服务
echo "🔧 安装systemd服务..."
sudo cp mcp-schedule.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mcp-schedule.service

echo "✅ 安装完成！"
echo ""
echo "📋 使用说明："
echo "  启动服务: sudo systemctl start mcp-schedule.service"
echo "  停止服务: sudo systemctl stop mcp-schedule.service"
echo "  查看状态: sudo systemctl status mcp-schedule.service"
echo "  查看日志: sudo journalctl -u mcp-schedule.service -f"
echo ""
echo "🌐 MCP服务器将在后台运行"
echo "📖 查看README.md了解详细使用方法"
echo ""
echo "🚀 现在可以启动服务了！" 