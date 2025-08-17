#!/usr/bin/env python3
"""
AI集成示例 - 展示如何让AI模型使用MCP工具
"""

import asyncio
import json
from typing import Dict, Any, List
from mcp_client_example import MCPScheduleClient

class AIScheduleAssistant:
    def __init__(self):
        self.client = None
        self.conversation_history = []
    
    async def __aenter__(self):
        self.client = MCPScheduleClient()
        await self.client.__aenter__()
        await self.client.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def process_user_request(self, user_input: str) -> str:
        """处理用户自然语言请求"""
        # 记录对话历史
        self.conversation_history.append({"user": user_input, "timestamp": "now"})
        
        # 分析用户意图并调用相应工具
        response = await self._analyze_and_execute(user_input)
        
        # 记录AI响应
        self.conversation_history.append({"ai": response, "timestamp": "now"})
        
        return response
    
    async def _analyze_and_execute(self, user_input: str) -> str:
        """分析用户意图并执行相应操作"""
        user_input_lower = user_input.lower()
        
        try:
            # 1. 查询日程相关
            if any(word in user_input_lower for word in ["日程", "安排", "计划", "今天", "明天", "查看"]):
                return await self._handle_schedule_query(user_input)
            
            # 2. 创建日程相关
            elif any(word in user_input_lower for word in ["添加", "创建", "安排", "设置"]):
                return await self._handle_schedule_creation(user_input)
            
            # 3. 项目管理相关
            elif any(word in user_input_lower for word in ["项目", "任务", "工作"]):
                return await self._handle_project_query(user_input)
            
            # 4. 通用查询
            else:
                return await self._handle_general_query(user_input)
                
        except Exception as e:
            return f"抱歉，处理您的请求时出现错误：{str(e)}"
    
    async def _handle_schedule_query(self, user_input: str) -> str:
        """处理日程查询请求"""
        # 简单的日期提取逻辑（实际应用中可以使用更复杂的NLP）
        if "今天" in user_input:
            date = "2024-01-01"  # 示例日期
        elif "明天" in user_input:
            date = "2024-01-02"  # 示例日期
        else:
            date = "2024-01-01"  # 默认今天
        
        schedule_data = await self.client.get_schedule(date)
        
        if not schedule_data:
            return f"{date} 没有安排任何日程。"
        
        response = f"{date} 的日程安排：\n"
        for item in schedule_data:
            time_slot = item.get('time_slot', '未知时间')
            planned_task = item.get('planned_subtask_name', '无计划任务')
            actual_task = item.get('actual_subtask_name', '无实际任务')
            mood = item.get('mood', '无心情记录')
            
            response += f"\n⏰ {time_slot}\n"
            response += f"📋 计划：{planned_task}\n"
            response += f"✅ 实际：{actual_task}\n"
            response += f"😊 心情：{mood}\n"
            response += "─" * 30
        
        return response
    
    async def _handle_schedule_creation(self, user_input: str) -> str:
        """处理日程创建请求"""
        # 这里可以集成更复杂的NLP来解析用户意图
        # 目前使用简单的示例数据
        
        try:
            new_schedule = {
                "schedule_date": "2024-01-01",
                "time_slot": "14:00",
                "planned_notes": f"用户请求：{user_input}",
                "mood": "期待"
            }
            
            result = await self.client.create_schedule(new_schedule)
            
            if result.get('id'):
                return f"✅ 日程创建成功！\n📅 时间：{new_schedule['time_slot']}\n📝 备注：{new_schedule['planned_notes']}"
            else:
                return "❌ 日程创建失败，请重试。"
                
        except Exception as e:
            return f"创建日程时出错：{str(e)}"
    
    async def _handle_project_query(self, user_input: str) -> str:
        """处理项目查询请求"""
        try:
            projects_data = await self.client.get_projects()
            
            if not projects_data:
                return "目前没有项目数据。"
            
            response = "📊 项目概览：\n"
            total_projects = 0
            total_tasks = 0
            
            for category in projects_data:
                category_name = category.get('name', '未命名分类')
                projects = category.get('projects', [])
                
                response += f"\n🏷️ {category_name}：\n"
                
                for project in projects:
                    project_name = project.get('name', '未命名项目')
                    subtasks = project.get('subtasks', [])
                    
                    response += f"  📁 {project_name} ({len(subtasks)} 个子任务)\n"
                    
                    total_projects += 1
                    total_tasks += len(subtasks)
                
                response += "─" * 20
            
            response += f"\n📈 统计：共 {total_projects} 个项目，{total_tasks} 个子任务"
            return response
            
        except Exception as e:
            return f"查询项目信息时出错：{str(e)}"
    
    async def _handle_general_query(self, user_input: str) -> str:
        """处理通用查询"""
        return f"我理解您想了解：{user_input}\n\n我可以帮您：\n" \
               f"📅 查看日程安排\n" \
               f"➕ 创建新的日程\n" \
               f"📊 查看项目信息\n" \
               f"🔍 查询特定信息\n\n" \
               f"请告诉我您具体需要什么帮助？"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history

async def main():
    """主函数 - 演示AI助手的使用"""
    print("🤖 AI日程助手演示")
    print("=" * 50)
    print("这个示例展示如何让AI模型使用MCP工具来管理日程")
    print("=" * 50)
    
    async with AIScheduleAssistant() as assistant:
        # 模拟用户与AI的对话
        test_queries = [
            "帮我查看今天的日程安排",
            "我想添加一个新的会议安排",
            "告诉我项目的整体情况",
            "明天有什么安排？"
        ]
        
        for query in test_queries:
            print(f"\n👤 用户：{query}")
            print("🤖 AI助手正在处理...")
            
            response = await assistant.process_user_request(query)
            print(f"🤖 AI助手：{response}")
            
            print("-" * 50)
            await asyncio.sleep(1)  # 模拟处理时间
        
        # 显示对话历史
        print("\n📚 对话历史：")
        history = assistant.get_conversation_history()
        for i, entry in enumerate(history, 1):
            if "user" in entry:
                print(f"{i}. 👤 用户：{entry['user']}")
            elif "ai" in entry:
                print(f"{i}. 🤖 AI：{entry['ai'][:100]}...")
        
        print("\n✅ AI助手演示完成！")
        print("\n💡 实际使用中，您可以：")
        print("1. 集成真实的AI模型API（如Claude、GPT）")
        print("2. 使用更复杂的NLP来理解用户意图")
        print("3. 添加更多智能功能（如日程建议、冲突检测）")
        print("4. 支持语音输入和输出")

if __name__ == "__main__":
    asyncio.run(main()) 