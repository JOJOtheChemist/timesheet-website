#!/usr/bin/env python3
"""
智谱AI GLM-4.5-Air 集成演示
展示如何使用智谱AI模型与MCP服务器交互
"""

import asyncio
import json
from mcp_schedule_server import MCPScheduleServer

class ZhipuAIDemo:
    def __init__(self):
        self.server = MCPScheduleServer()
    
    async def demo_ai_analysis(self):
        """演示AI分析功能"""
        print("🤖 智谱AI GLM-4.5-Air 集成演示")
        print("=" * 60)
        
        # 测试用例
        test_requests = [
            "帮我查看明天的日程安排",
            "我想在下午2点添加一个会议",
            "删除ID为123的日程记录",
            "查看所有项目信息",
            "今天心情不错，记录一下"
        ]
        
        for i, request in enumerate(test_requests, 1):
            print(f"\n📝 测试用例 {i}: {request}")
            print("-" * 40)
            
            try:
                # 调用AI分析
                result = await self.server.ai_analyze_request(request)
                
                if result.get('success'):
                    ai_analysis = result.get('ai_analysis', {})
                    action = ai_analysis.get('action', 'unknown')
                    parameters = ai_analysis.get('parameters', {})
                    explanation = ai_analysis.get('explanation', '无说明')
                    
                    print(f"✅ AI分析成功")
                    print(f"🔍 识别操作: {action}")
                    print(f"📋 操作参数: {json.dumps(parameters, ensure_ascii=False, indent=2)}")
                    print(f"💡 操作说明: {explanation}")
                    
                    # 根据AI分析结果执行相应操作
                    await self.execute_ai_action(action, parameters, request)
                    
                else:
                    print(f"❌ AI分析失败: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ 处理请求时出错: {e}")
            
            print("-" * 40)
            await asyncio.sleep(1)  # 避免API调用过快
    
    async def execute_ai_action(self, action: str, parameters: dict, original_request: str):
        """根据AI分析结果执行相应操作"""
        print(f"🔄 执行AI建议的操作: {action}")
        
        try:
            if action == "query_schedule":
                date = parameters.get('date', '2024-01-01')
                schedule_data = await self.server.get_schedule(date)
                print(f"📅 查询结果: 找到 {len(schedule_data)} 条日程记录")
                
            elif action == "create_schedule":
                # 这里可以添加创建日程的逻辑
                print(f"➕ 准备创建日程: {parameters}")
                
            elif action == "delete_schedule":
                schedule_id = parameters.get('schedule_id')
                if schedule_id:
                    print(f"🗑️ 准备删除日程ID: {schedule_id}")
                else:
                    print("⚠️ 缺少schedule_id参数")
                    
            elif action == "query_projects":
                projects_data = await self.server.get_projects()
                print(f"📊 查询结果: 找到 {len(projects_data)} 个项目分类")
                
            else:
                print(f"❓ 未知操作类型: {action}")
                
        except Exception as e:
            print(f"❌ 执行操作失败: {e}")
    
    async def demo_natural_language(self):
        """演示自然语言交互"""
        print("\n🗣️ 自然语言交互演示")
        print("=" * 60)
        print("现在你可以用自然语言与AI助手对话！")
        print("输入 'quit' 或 'exit' 退出")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见！")
                    break
                
                if not user_input:
                    continue
                
                print("🤖 AI正在分析您的请求...")
                
                # 调用AI分析
                result = await self.server.ai_analyze_request(user_input)
                
                if result.get('success'):
                    ai_analysis = result.get('ai_analysis', {})
                    action = ai_analysis.get('action', 'unknown')
                    explanation = ai_analysis.get('explanation', '无说明')
                    
                    print(f"🤖 AI助手: {explanation}")
                    
                    # 执行操作
                    parameters = ai_analysis.get('parameters', {})
                    await self.execute_ai_action(action, parameters, user_input)
                    
                else:
                    print(f"🤖 AI助手: 抱歉，我无法理解您的请求。错误: {result.get('error')}")
                    
            except KeyboardInterrupt:
                print("\n\n👋 演示被中断，再见！")
                break
            except Exception as e:
                print(f"❌ 处理请求时出错: {e}")
    
    async def run_demo(self):
        """运行完整演示"""
        print("🚀 启动智谱AI集成演示...")
        
        # 1. 自动测试用例演示
        await self.demo_ai_analysis()
        
        # 2. 交互式自然语言演示
        await self.demo_natural_language()

async def main():
    """主函数"""
    demo = ZhipuAIDemo()
    await demo.run_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 演示被中断，再见！")
    except Exception as e:
        print(f"\n❌ 演示运行出错: {e}")
        print("💡 请检查智谱AI API密钥是否正确配置") 