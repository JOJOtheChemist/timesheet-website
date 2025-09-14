#!/bin/bash

# 排行榜服务启动脚本
echo "启动排行榜服务..."

# 切换到timesheet目录
cd /home/ubuntu/timesheet

# 激活虚拟环境
source venv/bin/activate

# 切换到leaderboard目录
cd leaderboard

# 启动服务
echo "启动排行榜API服务 (端口: 5007)..."
python3 leaderboard_api.py
