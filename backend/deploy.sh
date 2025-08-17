#!/bin/bash

echo "🚀 开始部署 Schedule API..."

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

# 安装系统依赖
echo "📦 安装系统依赖..."
sudo apt update
sudo apt install -y python3.12-venv python3-pip

# 创建虚拟环境
if [ ! -d "../venv" ]; then
    echo "🐍 创建虚拟环境..."
    python3 -m venv ../venv
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境并安装依赖
echo "📚 安装Python依赖..."
source ../venv/bin/activate
pip install -r requirements.txt

# 设置启动脚本权限
echo "🔧 设置脚本权限..."
chmod +x start_api.sh

# 安装systemd服务
echo "🔧 安装systemd服务..."
sudo cp schedule-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable schedule-api.service

echo "✅ 部署完成！"
echo ""
echo "📋 使用说明："
echo "  启动服务: sudo systemctl start schedule-api.service"
echo "  停止服务: sudo systemctl stop schedule-api.service"
echo "  查看状态: sudo systemctl status schedule-api.service"
echo "  查看日志: sudo journalctl -u schedule-api.service -f"
echo ""
echo "🌐 API将在 http://localhost:5001 启动"
echo "📖 API文档: http://localhost:5001/docs"
echo ""
echo "🚀 现在可以启动服务了！" 