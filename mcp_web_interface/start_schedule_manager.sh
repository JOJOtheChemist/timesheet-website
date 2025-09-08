#!/bin/bash

# Schedule Manager 启动脚本
# 集成MCP Web Interface和Schedule Manager Agent

echo "🚀 启动 Schedule Manager Agent with MCP..."
echo "==============================================="

# 检查必要的组件
echo "📋 检查系统组件..."

# 检查FastAPI Schedule API
if pgrep -f "fastapi_schedule_api.py" > /dev/null; then
    echo "✅ FastAPI Schedule API 正在运行"
else
    echo "❌ FastAPI Schedule API 未运行，正在启动..."
    cd /home/ubuntu/timesheet
    nohup python3 backend/fastapi_schedule_api.py > /tmp/schedule_api.log 2>&1 &
    sleep 3
    if pgrep -f "fastapi_schedule_api.py" > /dev/null; then
        echo "✅ FastAPI Schedule API 启动成功"
    else
        echo "❌ FastAPI Schedule API 启动失败"
        exit 1
    fi
fi

# 检查MCP Schedule Server
if pgrep -f "mcp_schedule_server.py" > /dev/null; then
    echo "✅ MCP Schedule Server 正在运行"
else
    echo "⚠️  MCP Schedule Server 未运行，尝试启动..."
    cd /home/ubuntu/timesheet/mcp_schedule_api
    if [ -f "mcp_schedule_server.py" ]; then
        nohup python3 mcp_schedule_server.py > /tmp/mcp_server.log 2>&1 &
        sleep 3
        if pgrep -f "mcp_schedule_server.py" > /dev/null; then
            echo "✅ MCP Schedule Server 启动成功"
        else
            echo "⚠️  MCP Schedule Server 启动失败，可能需要依赖安装"
        fi
    else
        echo "⚠️  MCP Schedule Server 文件不存在"
    fi
fi

# 启动MCP Web Interface
echo "🌐 启动MCP Web Interface..."
cd /home/ubuntu/timesheet/mcp_web_interface

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 启动Flask应用
echo "🎯 启动Schedule Manager Web Interface..."
export FLASK_APP=app.py
export FLASK_ENV=production

# 后台启动Flask应用
nohup python3 app.py > /tmp/mcp_web_interface.log 2>&1 &
FLASK_PID=$!

sleep 5

# 检查Flask是否启动成功
if ps -p $FLASK_PID > /dev/null; then
    echo "✅ Schedule Manager Web Interface 启动成功 (PID: $FLASK_PID)"
    echo "🌐 Web界面地址: http://localhost:5000"
    echo "📊 状态检查: http://localhost:5000/api/schedule-manager/status"
else
    echo "❌ Schedule Manager Web Interface 启动失败"
    echo "📋 检查日志: tail -f /tmp/mcp_web_interface.log"
    exit 1
fi

# 等待服务完全启动
echo "⏳ 等待服务完全启动..."
sleep 3

# 测试连接
echo "🔍 测试服务连接..."
STATUS_RESPONSE=$(curl -s http://localhost:5000/api/schedule-manager/status 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Schedule Manager Agent 已成功启动并运行"
    echo ""
    echo "📋 服务状态摘要:"
    echo "$STATUS_RESPONSE" | python3 -m json.tool
    echo ""
    echo "🌐 访问地址:"
    echo "  - Web界面: http://localhost:5000"
    echo "  - API文档: http://localhost:5000/api/schedule-manager/status"
    echo "  - FastAPI API: http://localhost:5001/docs"
    echo ""
    echo "🔧 可用工具:"
    echo "  - 日程查询: get_schedule"
    echo "  - 日程创建: create_schedule"
    echo "  - 日程更新: update_schedule"
    echo "  - 日程删除: delete_schedule"
    echo "  - 项目查询: get_projects"
    echo "  - AI分析: ai_analyze"
    echo ""
    echo "🎉 Schedule Manager Agent with MCP 已就绪！"
else
    echo "❌ 服务连接测试失败"
    echo "📋 检查日志文件:"
    echo "  - MCP Web Interface: tail -f /tmp/mcp_web_interface.log"
    echo "  - Schedule API: tail -f /tmp/schedule_api.log"
    echo "  - MCP Server: tail -f /tmp/mcp_server.log"
fi

echo $FLASK_PID > /tmp/schedule_manager.pid
echo "📝 Schedule Manager PID: $FLASK_PID"