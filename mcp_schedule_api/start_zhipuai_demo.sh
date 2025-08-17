#!/bin/bash

echo "🚀 启动智谱AI GLM-4.5-Air 集成演示..."

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
pip install --upgrade pip
pip install -r requirements.txt

# 检查智谱AI依赖
if ! python3 -c "import zhipuai" 2>/dev/null; then
    echo "❌ 智谱AI依赖未安装，正在安装..."
    pip install zhipuai
fi

echo "✅ 依赖安装完成！"

# 设置执行权限
chmod +x zhipuai_demo.py

# 启动智谱AI演示
echo "🤖 启动智谱AI演示..."
echo "💡 提示："
echo "   - 演示将自动测试多个用例"
echo "   - 然后进入交互式对话模式"
echo "   - 输入 'quit' 或 'exit' 退出"
echo ""

python3 zhipuai_demo.py

echo "✅ 智谱AI演示结束！" 