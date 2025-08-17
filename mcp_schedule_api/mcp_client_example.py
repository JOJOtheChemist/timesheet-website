#!/usr/bin/env python3
"""
MCP Schedule API Client Example
展示如何与MCP服务器交互的客户端示例
"""

import asyncio
import json
import aiohttp
from typing import Dict, Any, List

class MCPScheduleClient:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送MCP请求到服务器"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        async with self.session.post(
            f"{self.server_url}/mcp",
            json=request,
            headers={"Content-Type": "application/json"}
        ) as response:
            return await response.json()
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化MCP连接"""
        return await self.send_request("initialize")
    
    async def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        return await self.send_request("tools/list")
    
    async def list_resources(self) -> Dict[str, Any]:
        """列出可用资源"""
        return await self.send_request("resources/list")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        return await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """读取资源"""
        return await self.send_request("resources/read", {"uri": uri})
    
    # 便捷方法
    async def get_schedule(self, date: str) -> List[Dict[str, Any]]:
        """获取指定日期的日程数据"""
        response = await self.call_tool("get_schedule", {"date": date})
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        return []
    
    async def create_schedule(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的日程记录"""
        response = await self.call_tool("create_schedule", schedule_data)
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        return {}
    
    async def update_schedule(self, schedule_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新现有日程记录"""
        response = await self.call_tool("update_schedule", {
            "schedule_id": schedule_id,
            "data": data
        })
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        return {}
    
    async def delete_schedule(self, schedule_id: int) -> Dict[str, Any]:
        """删除日程记录"""
        response = await self.call_tool("delete_schedule", {"schedule_id": schedule_id})
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        return {}
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """获取项目列表"""
        response = await self.call_tool("get_projects", {})
        if "result" in response and "content" in response["result"]:
            content = response["result"]["content"][0]["text"]
            return json.loads(content)
        return []

async def main():
    """主函数 - 演示MCP客户端的使用"""
    print("🚀 MCP Schedule API Client Example")
    print("=" * 50)
    
    async with MCPScheduleClient() as client:
        try:
            # 1. 初始化连接
            print("1. 初始化MCP连接...")
            init_response = await client.initialize()
            print(f"   服务器信息: {init_response.get('result', {}).get('serverInfo', {})}")
            
            # 2. 列出可用工具
            print("\n2. 列出可用工具...")
            tools_response = await client.list_tools()
            tools = tools_response.get('result', {}).get('tools', [])
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
            
            # 3. 列出可用资源
            print("\n3. 列出可用资源...")
            resources_response = await client.list_resources()
            resources = resources_response.get('result', {}).get('resources', [])
            for resource in resources:
                print(f"   - {resource['name']}: {resource['description']}")
            
            # 4. 获取今天的日程数据
            print("\n4. 获取今天的日程数据...")
            today = "2024-01-01"  # 示例日期
            schedule_data = await client.get_schedule(today)
            print(f"   获取到 {len(schedule_data)} 条日程记录")
            
            # 5. 获取项目列表
            print("\n5. 获取项目列表...")
            projects_data = await client.get_projects()
            print(f"   获取到 {len(projects_data)} 个分类")
            for category in projects_data:
                print(f"   - {category['name']}: {len(category['projects'])} 个项目")
            
            # 6. 创建示例日程记录
            print("\n6. 创建示例日程记录...")
            new_schedule = {
                "schedule_date": today,
                "time_slot": "09:00",
                "planned_notes": "MCP测试日程",
                "mood": "兴奋"
            }
            create_result = await client.create_schedule(new_schedule)
            print(f"   创建结果: {create_result}")
            
            print("\n✅ MCP客户端演示完成！")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            print("   请确保MCP服务器正在运行")

if __name__ == "__main__":
    asyncio.run(main()) 