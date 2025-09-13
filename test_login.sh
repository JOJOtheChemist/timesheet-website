#!/bin/bash

echo "=== 测试登录功能 ==="
echo "1. 测试本地API登录..."
LOCAL_RESPONSE=$(curl -s -X POST http://localhost:5001/api/auth/login -H "Content-Type: application/json" -d '{"username":"nuo","password":"nuo"}')
echo "本地API响应: $LOCAL_RESPONSE"

echo ""
echo "2. 测试外网API登录..."
REMOTE_RESPONSE=$(curl -s -X POST http://140.143.194.215/api/auth/login -H "Content-Type: application/json" -d '{"username":"nuo","password":"nuo"}')
echo "外网API响应: $REMOTE_RESPONSE"

echo ""
echo "3. 测试外网健康检查..."
HEALTH_RESPONSE=$(curl -s http://140.143.194.215/health)
echo "健康检查响应: $HEALTH_RESPONSE"

echo ""
echo "4. 测试外网项目API..."
PROJECTS_RESPONSE=$(curl -s http://140.143.194.215/api/projects)
echo "项目API响应: $PROJECTS_RESPONSE"

echo ""
echo "=== 测试完成 ==="
