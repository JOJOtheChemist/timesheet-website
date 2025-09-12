#!/bin/bash
cd /home/ubuntu/timesheet
export ZHIPUAI_API_KEY=ce85d782d3834f3982b87494dbd2a447.y8l8wxwEFafurRY2
export PYTHONPATH=/home/ubuntu/langchain-agent:$PYTHONPATH
nohup venv/bin/python backend/fastapi_schedule_api.py > api.log 2>&1 &
echo "API服务器已启动，PID: $!"
