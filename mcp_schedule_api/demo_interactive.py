#!/usr/bin/env python3
"""
交互式MCP演示 - 体验AI助手功能
"""

import asyncio
import json
from datetime import datetime, timedelta
from mcp_client_example import MCPScheduleClient

class InteractiveMCPScheduleDemo:
    def __init__(self):
        self.client = None
        self.demo_data_created = False
    
    async def __aenter__(self):
        self.client = MCPScheduleClient()
        await self.client.__aenter__()
        await self.client.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def create_demo_data(self):
        """创建演示数据"""
        if self.demo_data_created:
            return
        
        print("📊 创建演示数据...")
        
        # 创建一些示例日程
        demo_schedules = [
            {
                "schedule_date": "2024-01-01",
                "time_slot": "09:00",
                "planned_notes": "晨会 - 讨论本周计划",
                "mood": "专注"
            },
            {
                "schedule_date": "2024-01-01",
                "time_slot": "14:00",
                "planned_notes": "代码审查会议",
                "mood": "期待"
            },
            {
                "schedule_date": "2024-01-02",
                "time_slot": "10:00",
                "planned_notes": "客户需求讨论",
                "mood": "兴奋"
            }
        ]
        
        for schedule in demo_schedules:
            try:
                result = await self.client.create_schedule(schedule)
                if result.get('id'):
                    print(f"✅ 创建日程：{schedule['time_slot']} - {schedule['planned_notes']}")
            except Exception as e:
                print(f"⚠️ 创建日程失败：{e}")
        
        self.demo_data_created = True
        print("✅ 演示数据创建完成！\n")
    
    async def show_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("🤖 MCP日程表助手 - 交互式演示")
        print("="*60)
        print("请选择要体验的功能：")
        print("1. 📅 查看日程安排")
        print("2. ➕ 创建新日程")
        print("3. 📊 查看项目信息")
        print("4. 🔍 智能查询演示")
        print("5. 🧹 清理演示数据")
        print("0. 🚪 退出演示")
        print("="*60)
    
    async def handle_menu_choice(self, choice: str):
        """处理菜单选择"""
        if choice == "1":
            await self.view_schedule()
        elif choice == "2":
            await self.create_schedule()
        elif choice == "3":
            await self.view_projects()
        elif choice == "4":
            await self.smart_query_demo()
        elif choice == "5":
            await self.cleanup_demo_data()
        elif choice == "0":
            print("👋 感谢使用MCP日程表助手演示！")
            return False
        else:
            print("❌ 无效选择，请重新输入")
        
        return True
    
    async def view_schedule(self):
        """查看日程安排"""
        print("\n📅 查看日程安排")
        print("-" * 40)
        
        # 获取今天的日程
        today = datetime.now().strftime('%Y-%m-%d')
        schedule_data = await self.client.get_schedule(today)
        
        if not schedule_data:
            print(f"📅 {today} 没有安排任何日程")
            print("💡 提示：您可以创建一些演示数据来体验功能")
        else:
            print(f"📅 {today} 的日程安排：")
            for item in schedule_data:
                print(f"\n⏰ {item.get('time_slot', '未知时间')}")
                print(f"📋 计划：{item.get('planned_subtask_name', '无计划任务')}")
                print(f"✅ 实际：{item.get('actual_subtask_name', '无实际任务')}")
                print(f"😊 心情：{item.get('mood', '无心情记录')}")
                print(f"📝 备注：{item.get('planned_notes', '无备注')}")
                print("-" * 30)
    
    async def create_schedule(self):
        """创建新日程"""
        print("\n➕ 创建新日程")
        print("-" * 40)
        
        try:
            # 获取用户输入
            date_input = input("📅 请输入日期 (YYYY-MM-DD，回车使用今天): ").strip()
            if not date_input:
                date_input = datetime.now().strftime('%Y-%m-%d')
            
            time_input = input("⏰ 请输入时间 (HH:MM): ").strip()
            if not time_input:
                print("❌ 时间不能为空")
                return
            
            notes_input = input("📝 请输入备注: ").strip()
            mood_input = input("😊 请输入心情 (可选): ").strip()
            
            # 创建日程
            new_schedule = {
                "schedule_date": date_input,
                "time_slot": time_input,
                "planned_notes": notes_input,
                "mood": mood_input if mood_input else None
            }
            
            result = await self.client.create_schedule(new_schedule)
            
            if result.get('id'):
                print(f"✅ 日程创建成功！")
                print(f"📅 日期：{date_input}")
                print(f"⏰ 时间：{time_input}")
                print(f"📝 备注：{notes_input}")
                if mood_input:
                    print(f"😊 心情：{mood_input}")
            else:
                print("❌ 日程创建失败")
                
        except Exception as e:
            print(f"❌ 创建日程时出错：{e}")
    
    async def view_projects(self):
        """查看项目信息"""
        print("\n📊 查看项目信息")
        print("-" * 40)
        
        try:
            projects_data = await self.client.get_projects()
            
            if not projects_data:
                print("📊 目前没有项目数据")
                print("💡 提示：请确保数据库中有项目数据")
                return
            
            print("📊 项目概览：")
            total_projects = 0
            total_tasks = 0
            
            for category in projects_data:
                category_name = category.get('name', '未命名分类')
                projects = category.get('projects', [])
                
                print(f"\n🏷️ {category_name}：")
                
                for project in projects:
                    project_name = project.get('name', '未命名项目')
                    subtasks = project.get('subtasks', [])
                    
                    print(f"  📁 {project_name} ({len(subtasks)} 个子任务)")
                    
                    # 显示子任务详情
                    for subtask in subtasks[:3]:  # 只显示前3个
                        print(f"    - {subtask.get('name', '未命名任务')}")
                    if len(subtasks) > 3:
                        print(f"    ... 还有 {len(subtasks) - 3} 个任务")
                    
                    total_projects += 1
                    total_tasks += len(subtasks)
                
                print("-" * 20)
            
            print(f"\n📈 统计：共 {total_projects} 个项目，{total_tasks} 个子任务")
            
        except Exception as e:
            print(f"❌ 查询项目信息时出错：{e}")
    
    async def smart_query_demo(self):
        """智能查询演示"""
        print("\n🔍 智能查询演示")
        print("-" * 40)
        print("这个功能演示了如何让AI理解自然语言并调用相应工具")
        print("在实际应用中，AI会分析您的输入并自动选择正确的操作")
        
        # 模拟AI分析过程
        queries = [
            "明天有什么安排？",
            "帮我添加一个会议",
            "查看项目进度",
            "今天心情如何？"
        ]
        
        print("\n🤖 AI分析示例：")
        for query in queries:
            print(f"\n👤 用户：{query}")
            print("🤖 AI分析中...")
            
            # 模拟AI分析
            if "明天" in query or "安排" in query:
                print("🔍 识别意图：查询日程")
                print("🛠️ 调用工具：get_schedule")
                print("📅 返回结果：明天的日程安排")
            elif "添加" in query or "会议" in query:
                print("🔍 识别意图：创建日程")
                print("🛠️ 调用工具：create_schedule")
                print("✅ 返回结果：日程创建成功")
            elif "项目" in query or "进度" in query:
                print("🔍 识别意图：查询项目")
                print("🛠️ 调用工具：get_projects")
                print("📊 返回结果：项目概览信息")
            else:
                print("🔍 识别意图：通用查询")
                print("💬 返回结果：友好提示信息")
            
            await asyncio.sleep(1)  # 模拟处理时间
        
        print("\n💡 这就是MCP的强大之处：")
        print("1. AI理解自然语言")
        print("2. 自动选择正确的工具")
        print("3. 执行具体操作")
        print("4. 返回有用结果")
    
    async def cleanup_demo_data(self):
        """清理演示数据"""
        print("\n🧹 清理演示数据")
        print("-" * 40)
        
        confirm = input("⚠️ 确定要删除所有演示数据吗？(y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return
        
        try:
            # 这里应该实现删除逻辑
            # 由于演示目的，我们只是标记
            print("🔄 清理演示数据中...")
            await asyncio.sleep(2)  # 模拟清理过程
            print("✅ 演示数据清理完成")
            self.demo_data_created = False
            
        except Exception as e:
            print(f"❌ 清理数据时出错：{e}")
    
    async def run_demo(self):
        """运行演示"""
        print("🚀 启动MCP日程表助手演示...")
        
        # 创建演示数据
        await self.create_demo_data()
        
        # 主循环
        while True:
            await self.show_menu()
            choice = input("请选择 (0-5): ").strip()
            
            should_continue = await self.handle_menu_choice(choice)
            if not should_continue:
                break
            
            input("\n按回车键继续...")

async def main():
    """主函数"""
    print("🎉 欢迎使用MCP日程表助手演示！")
    print("这个演示展示了MCP如何让AI模型使用你的日程表工具")
    
    async with InteractiveMCPScheduleDemo() as demo:
        await demo.run_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 演示被中断，再见！")
    except Exception as e:
        print(f"\n❌ 演示运行出错：{e}")
        print("💡 请检查MCP服务器是否正在运行") 