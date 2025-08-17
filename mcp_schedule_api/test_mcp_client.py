#!/usr/bin/env python3
"""
MCP客户端测试脚本
测试MCP服务器的各种功能
"""

import json
import asyncio
from mcp_schedule_server import MCPScheduleServer

async def test_mcp_server():
    """测试MCP服务器功能"""
    
    print("🚀 启动MCP服务器测试...")
    
    # 创建MCP服务器实例
    server = MCPScheduleServer()
    
    # 测试1: 初始化
    print("\n📋 测试1: 初始化")
    init_response = server.initialize("test_init")
    print(f"初始化响应: {json.dumps(init_response, ensure_ascii=False, indent=2)}")
    
    # 测试2: 列出工具
    print("\n🔧 测试2: 列出工具")
    tools_response = server.list_tools("test_tools")
    print(f"工具列表: {json.dumps(tools_response, ensure_ascii=False, indent=2)}")
    
    # 测试3: 列出资源
    print("\n📚 测试3: 列出资源")
    resources_response = server.list_resources("test_resources")
    print(f"资源列表: {json.dumps(resources_response, ensure_ascii=False, indent=2)}")
    
    # 测试4: AI分析请求
    print("\n🤖 测试4: AI分析请求")
    ai_response = await server.ai_analyze_request("查询今天的日程安排")
    print(f"AI分析结果: {json.dumps(ai_response, ensure_ascii=False, indent=2)}")
    
    # 测试5: 获取项目列表
    print("\n📁 测试5: 获取项目列表")
    try:
        projects_response = await server.get_projects()
        print(f"项目列表: {json.dumps(projects_response, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"获取项目列表失败: {e}")
    
    # 测试6: 获取今日日程
    print("\n📅 测试6: 获取今日日程")
    try:
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        schedule_response = await server.get_schedule(today)
        print(f"今日日程: {json.dumps(schedule_response, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"获取日程失败: {e}")
    
    print("\n✅ MCP服务器测试完成!")

def test_mcp_request_handling():
    """测试MCP请求处理"""
    
    print("\n🔄 测试MCP请求处理...")
    
    server = MCPScheduleServer()
    
    # 测试请求
    test_requests = [
        {
            "jsonrpc": "2.0",
            "id": "test1",
            "method": "initialize",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": "test2",
            "method": "tools/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": "test3",
            "method": "resources/list",
            "params": {}
        }
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📤 测试请求 {i}: {request['method']}")
        try:
            response = asyncio.run(server.handle_request(request))
            print(f"✅ 响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n✅ MCP请求处理测试完成!")

if __name__ == "__main__":
    print("🎯 开始MCP服务器全面测试...")
    
    # 运行异步测试
    asyncio.run(test_mcp_server())
    
    # 运行同步测试
    test_mcp_request_handling()
    
    print("\n🎉 所有测试完成!") 