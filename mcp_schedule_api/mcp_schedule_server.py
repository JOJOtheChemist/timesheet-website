#!/usr/bin/env python3
"""
MCP Schedule API Server with ZhipuAI GLM-4.5-Air Integration
将FastAPI应用转换为Model Context Protocol (MCP)格式，集成智谱AI模型
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, date
import mysql.connector
from mysql.connector import pooling
from contextlib import asynccontextmanager
import zhipuai

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 智谱AI配置
ZHIPUAI_API_KEY = "ce85d782d3834f3982b87494dbd2a447.y8l8wxwEFafurRY2"
ZHIPUAI_MODEL = "glm-4.5-air"
ZHIPUAI_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# MySQL数据库连接池配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12356790zZ_',
    'database': 'project_tasks',
    'charset': 'utf8mb4',
    'autocommit': True
}

# 创建连接池
connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="mcp_pool",
    pool_size=5,
    **db_config
)

# 数据模型
class ScheduleItem:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.schedule_date = kwargs.get('schedule_date')
        self.time_slot = kwargs.get('time_slot')
        # 计划字段
        self.planned_subtask_id = kwargs.get('planned_subtask_id')
        self.planned_subtask_name = kwargs.get('planned_subtask_name')
        self.planned_subtask_color = kwargs.get('planned_subtask_color')
        self.planned_project_name = kwargs.get('planned_project_name')
        self.planned_project_color = kwargs.get('planned_project_color')
        self.planned_notes = kwargs.get('planned_notes')
        # 实际字段
        self.actual_subtask_id = kwargs.get('actual_subtask_id')
        self.actual_subtask_name = kwargs.get('actual_subtask_name')
        self.actual_subtask_color = kwargs.get('actual_subtask_color')
        self.actual_project_name = kwargs.get('actual_project_name')
        self.actual_project_color = kwargs.get('actual_project_color')
        self.actual_notes = kwargs.get('actual_notes')
        self.mood = kwargs.get('mood')
    
    def to_dict(self):
        def safe_serialize(value):
            if isinstance(value, date):
                return value.isoformat()
            elif isinstance(value, datetime):
                return value.isoformat()
            return value
        
        return {
            "id": self.id,
            "schedule_date": safe_serialize(self.schedule_date),
            "time_slot": self.time_slot,
            "planned_subtask_id": self.planned_subtask_id,
            "planned_subtask_name": self.planned_subtask_name,
            "planned_subtask_color": self.planned_subtask_color,
            "planned_project_name": self.planned_project_name,
            "planned_project_color": self.planned_project_color,
            "planned_notes": self.planned_notes,
            "actual_subtask_id": self.actual_subtask_id,
            "actual_subtask_name": self.actual_subtask_name,
            "actual_subtask_color": self.actual_subtask_color,
            "actual_project_name": self.actual_project_name,
            "actual_project_color": self.actual_project_color,
            "actual_notes": self.actual_notes,
            "mood": self.mood
        }

class MCPScheduleServer:
    def __init__(self):
        self.server_info = {
            "name": "mcp-schedule-api-zhipuai",
            "version": "1.0.0",
            "description": "MCP Schedule API Server with ZhipuAI GLM-4.5-Air integration"
        }
        self.resources = {}
        self.tools = {}
        self.initialize_resources()
        self.initialize_tools()
    
    def initialize_resources(self):
        """初始化MCP资源"""
        self.resources = {
            "schedule": {
                "name": "schedule",
                "description": "日程表数据资源",
                "mimeType": "application/json",
                "uri": "mcp://schedule/data"
            },
            "projects": {
                "name": "projects",
                "description": "项目数据资源",
                "mimeType": "application/json",
                "uri": "mcp://projects/data"
            }
        }
    
    def initialize_tools(self):
        """初始化MCP工具"""
        self.tools = {
            "get_schedule": {
                "name": "get_schedule",
                "description": "获取指定日期的日程数据",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "日期 (YYYY-MM-DD)"}
                    },
                    "required": ["date"]
                }
            },
            "create_schedule": {
                "name": "create_schedule",
                "description": "创建新的日程记录",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schedule_date": {"type": "string"},
                        "time_slot": {"type": "string"},
                        "planned_subtask_id": {"type": "integer"},
                        "planned_notes": {"type": "string"},
                        "actual_subtask_id": {"type": "integer"},
                        "actual_notes": {"type": "string"},
                        "mood": {"type": "string"}
                    },
                    "required": ["schedule_date", "time_slot"]
                }
            },
            "update_schedule": {
                "name": "update_schedule",
                "description": "更新现有日程记录",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {"type": "integer"},
                        "data": {"type": "object"}
                    },
                    "required": ["schedule_id", "data"]
                }
            },
            "delete_schedule": {
                "name": "delete_schedule",
                "description": "删除日程记录",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {"type": "integer"}
                    },
                    "required": ["schedule_id"]
                }
            },
            "get_projects": {
                "name": "get_projects",
                "description": "获取项目列表",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "ai_analyze": {
                "name": "ai_analyze",
                "description": "使用智谱AI分析用户请求并执行相应操作",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_request": {"type": "string", "description": "用户的自然语言请求"}
                    },
                    "required": ["user_request"]
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "tools/list":
                return self.list_tools(request_id)
            elif method == "tools/call":
                return await self.call_tool(params, request_id)
            elif method == "resources/list":
                return self.list_resources(request_id)
            elif method == "resources/read":
                return await self.read_resource(params, request_id)
            elif method == "initialize":
                return self.initialize(request_id)
            else:
                return self.error_response(request_id, f"Unknown method: {method}")
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return self.error_response(request_id, str(e))
    
    def initialize(self, request_id: str) -> Dict[str, Any]:
        """初始化MCP服务器"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "logging": {}
                },
                "serverInfo": self.server_info
            }
        }
    
    def list_tools(self, request_id: str) -> Dict[str, Any]:
        """列出可用工具"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": list(self.tools.values())
            }
        }
    
    def list_resources(self, request_id: str) -> Dict[str, Any]:
        """列出可用资源"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": list(self.resources.values())
            }
        }
    
    async def call_tool(self, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """调用工具"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "get_schedule":
            result = await self.get_schedule(arguments.get("date"))
        elif tool_name == "create_schedule":
            result = await self.create_schedule(arguments)
        elif tool_name == "update_schedule":
            result = await self.update_schedule(arguments.get("schedule_id"), arguments.get("data"))
        elif tool_name == "delete_schedule":
            result = await self.delete_schedule(arguments.get("schedule_id"))
        elif tool_name == "get_projects":
            result = await self.get_projects()
        elif tool_name == "ai_analyze":
            result = await self.ai_analyze_request(arguments.get("user_request"))
        else:
            return self.error_response(request_id, f"Unknown tool: {tool_name}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }
                ]
            }
        }
    
    async def read_resource(self, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """读取资源"""
        uri = params.get("uri")
        
        if uri == "mcp://schedule/data":
            content = await self.get_schedule(datetime.now().strftime('%Y-%m-%d'))
        elif uri == "mcp://projects/data":
            content = await self.get_projects()
        else:
            return self.error_response(request_id, f"Unknown resource: {uri}")
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(content, ensure_ascii=False, indent=2)
                    }
                ]
            }
        }
    
    def error_response(self, request_id: str, message: str) -> Dict[str, Any]:
        """错误响应"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -1,
                "message": message
            }
        }
    
    async def ai_analyze_request(self, user_request: str) -> Dict[str, Any]:
        """使用智谱AI分析用户请求"""
        try:
            # 构建提示词
            prompt = f"""
            你是一个智能日程助手，请分析用户的请求并返回相应的操作类型和参数。

            用户请求：{user_request}

            可选操作类型：
            - query_schedule: 查询日程（需要date参数）
            - create_schedule: 创建日程（需要schedule_date, time_slot, planned_notes等参数）
            - update_schedule: 更新日程（需要schedule_id和data参数）
            - delete_schedule: 删除日程（需要schedule_id参数）
            - query_projects: 查询项目信息

            请以JSON格式返回，包含：
            1. action: 操作类型
            2. parameters: 操作参数
            3. explanation: 操作说明

            示例：
            {{
                "action": "query_schedule",
                "parameters": {{"date": "2024-01-01"}},
                "explanation": "查询2024年1月1日的日程安排"
            }}
            """

            # 调用智谱AI
            import requests
            
            headers = {
                "Authorization": f"Bearer {ZHIPUAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": ZHIPUAI_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 1024
            }
            
            response = requests.post(ZHIPUAI_API_URL, headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    ai_response = result['choices'][0]['message']['content']
                
                # 尝试解析AI返回的JSON
                try:
                    parsed_response = json.loads(ai_response)
                    return {
                        "success": True,
                        "ai_analysis": parsed_response,
                        "raw_response": ai_response
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "ai_analysis": {"action": "unknown", "parameters": {}, "explanation": ai_response},
                        "raw_response": ai_response
                    }
            else:
                return {
                    "success": False,
                    "error": "智谱AI调用失败: 没有返回有效内容",
                    "code": -1
                }

        except Exception as e:
            logger.error(f"AI分析请求失败: {e}")
            return {
                "success": False,
                "error": f"AI分析异常: {str(e)}"
            }
    
    # 数据库操作方法
    def get_db(self):
        """获取数据库连接"""
        return connection_pool.get_connection()
    
    async def get_schedule(self, schedule_date: str) -> List[Dict[str, Any]]:
        """获取指定日期的日程数据"""
        conn = self.get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                SELECT 
                    ds.id,
                    ds.schedule_date,
                    ds.time_slot,
                    ds.planned_subtask_id,
                    ds.planned_notes,
                    ds.actual_subtask_id,
                    ds.actual_notes,
                    ds.mood,
                    ps.name as planned_subtask_name,
                    ps.color as planned_subtask_color,
                    pp.name as planned_project_name,
                    pp.color as planned_project_color,
                    asub.name as actual_subtask_name,
                    asub.color as actual_subtask_color,
                    ap.name as actual_project_name,
                    ap.color as actual_project_color
                FROM daily_schedule ds
                LEFT JOIN subtasks ps ON ds.planned_subtask_id = ps.id
                LEFT JOIN projects pp ON ps.project_id = pp.id
                LEFT JOIN subtasks asub ON ds.actual_subtask_id = asub.id
                LEFT JOIN projects ap ON asub.project_id = ap.id
                WHERE ds.schedule_date = %s
                ORDER BY ds.time_slot
            ''', (schedule_date,))
            
            rows = cursor.fetchall()
            def safe_serialize_row(row):
                result = {}
                for key, value in row.items():
                    if isinstance(value, date):
                        result[key] = value.isoformat()
                    elif isinstance(value, datetime):
                        result[key] = value.isoformat()
                    else:
                        result[key] = value
                return result
            
            return [safe_serialize_row(row) for row in rows]
            
        finally:
            cursor.close()
            conn.close()
    
    async def create_schedule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的日程记录"""
        conn = self.get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('''
                INSERT INTO daily_schedule (
                    schedule_date, time_slot, 
                    planned_subtask_id, planned_notes,
                    actual_subtask_id, actual_notes, mood
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                data.get('schedule_date'), data.get('time_slot'),
                data.get('planned_subtask_id'), data.get('planned_notes'),
                data.get('actual_subtask_id'), data.get('actual_notes'), 
                data.get('mood')
            ))
            
            conn.commit()
            schedule_id = cursor.lastrowid
            
            return {"id": schedule_id, "message": "Schedule created successfully"}
            
        finally:
            cursor.close()
            conn.close()
    
    async def update_schedule(self, schedule_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新现有日程记录"""
        conn = self.get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            update_fields = []
            update_values = []
            
            for key, value in data.items():
                if value is not None:
                    update_fields.append(f"{key} = %s")
                    update_values.append(value)
            
            if not update_fields:
                raise ValueError("No fields to update")
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(schedule_id)
            
            cursor.execute(f'''
                UPDATE daily_schedule 
                SET {', '.join(update_fields)}
                WHERE id = %s
            ''', update_values)
            
            if cursor.rowcount == 0:
                raise ValueError("Schedule not found")
            
            conn.commit()
            return {"message": "Schedule updated successfully"}
            
        finally:
            cursor.close()
            conn.close()
    
    async def delete_schedule(self, schedule_id: int) -> Dict[str, Any]:
        """删除日程记录"""
        conn = self.get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('DELETE FROM daily_schedule WHERE id = %s', (schedule_id,))
            
            if cursor.rowcount == 0:
                raise ValueError("Schedule not found")
            
            conn.commit()
            return {"message": "Schedule deleted successfully"}
            
        finally:
            cursor.close()
            conn.close()
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """获取项目列表"""
        conn = self.get_db()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute('SELECT id, name, color FROM categories ORDER BY id')
            categories = cursor.fetchall()
            
            result = []
            for category in categories:
                cursor.execute('''
                    SELECT id, name, description, color 
                    FROM projects 
                    WHERE category_id = %s 
                    ORDER BY id
                ''', (category['id'],))
                
                projects = cursor.fetchall()
                project_list = []
                
                for project in projects:
                    cursor.execute('''
                        SELECT id, name, priority, urgency_importance, difficulty, color
                        FROM subtasks 
                        WHERE project_id = %s 
                        ORDER BY id
                    ''', (project['id'],))
                    
                    subtasks = cursor.fetchall()
                    subtask_list = [
                        {
                            'id': st['id'],
                            'name': st['name'],
                            'urgency_importance': st['urgency_importance'],
                            'difficulty': st['difficulty'],
                            'difficulty_class': st['difficulty'].lower().replace("级", ""),
                            'color': st['color']
                        } for st in subtasks
                    ]
                    
                    project_obj = {
                        'id': project['id'],
                        'name': project['name'],
                        'color': project['color'],
                        'subtasks': subtask_list
                    }
                    
                    project_list.append(project_obj)
                
                category_obj = {
                    'id': category['id'],
                    'name': category['name'],
                    'color': category['color'],
                    'projects': project_list
                }
                
                result.append(category_obj)
            
            return result
            
        finally:
            cursor.close()
            conn.close()

async def main():
    """主函数"""
    server = MCPScheduleServer()
    
    # 初始化数据库
    try:
        conn = server.get_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_schedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                schedule_date DATE NOT NULL,
                time_slot VARCHAR(10) NOT NULL,
                planned_subtask_id INT,
                planned_subtask_name VARCHAR(255),
                planned_notes TEXT,
                planned_project_color VARCHAR(20),
                actual_subtask_id INT,
                actual_subtask_name VARCHAR(255),
                actual_notes TEXT,
                actual_project_color VARCHAR(20),
                mood VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_schedule_date (schedule_date),
                INDEX idx_time_slot (time_slot),
                INDEX idx_planned_subtask_id (planned_subtask_id),
                INDEX idx_actual_subtask_id (actual_subtask_id)
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        cursor.close()
        conn.close()
    
    logger.info("MCP Schedule API Server with ZhipuAI integration is ready!")
    logger.info(f"Server Info: {server.server_info}")
    logger.info(f"ZhipuAI Model: {ZHIPUAI_MODEL}")
    
    # 这里可以添加MCP服务器的网络监听逻辑
    # 目前只是展示MCP协议的结构

if __name__ == "__main__":
    asyncio.run(main()) 