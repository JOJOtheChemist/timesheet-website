#!/usr/bin/env python3
"""
Flask后端服务器
作为MCP服务器和前端页面的桥梁
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import json
import logging
from datetime import datetime
import os
import sys
from flask import Response, stream_with_context
from zhipuai import ZhipuAI
import copy

# 添加agent-react路径到sys.path
sys.path.insert(0, '/home/ubuntu/agent-react')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MCP服务器配置
MCP_SERVER_URL = "http://localhost:8001/api/mcp"  # MCP服务器地址
SCHEDULE_API_URL = "http://localhost:5001"  # FastAPI Schedule API地址

class MCPProxy:
    """MCP服务器代理类"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def send_request(self, method, params=None):
        """发送MCP请求"""
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": f"web_{datetime.now().timestamp()}",
                "method": method,
                "params": params or {}
            }
            
            logger.info(f"发送MCP请求: {method}")
            logger.info(f"MCP服务器URL: {self.base_url}")
            response = self.session.post(
                self.base_url,
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"MCP请求成功: {method}")
                return result
            else:
                logger.error(f"MCP请求失败: {method}, 状态码: {response.status_code}")
                return {
                    "error": {
                        "code": response.status_code,
                        "message": f"HTTP错误: {response.status_code}",
                        "details": response.text
                    }
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP请求异常: {method}, 错误: {e}")
            return {
                "error": {
                    "code": -1,
                    "message": f"网络错误: {str(e)}"
                }
            }
        except Exception as e:
            logger.error(f"MCP请求未知错误: {method}, 错误: {e}")
            return {
                "error": {
                    "code": -1,
                    "message": f"未知错误: {str(e)}"
                }
            }

# 创建MCP代理实例
mcp_proxy = MCPProxy(MCP_SERVER_URL)

# 简单的内存会话存储：按 session_id 保存消息历史与临时缓存
SESSION_STORE: dict[str, dict] = {}

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/schedule-assistant')
def schedule_assistant():
    """日程ReAct助手页面"""
    return render_template('schedule_assistant.html')

@app.route('/api/schedule-assistant/chat', methods=['POST'])
def schedule_assistant_chat():
    """日程ReAct助手聊天端点"""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        if not user_input:
            return jsonify({"error": "缺少user_input参数"}), 400
        
        # 导入并运行日程ReAct助手
        try:
            from schedule_react.agent import ReActAgent
            from schedule_react.prompt import schedule_system_prompt_template
            
            # 设置MCP服务器URL环境变量
            os.environ['MCP_SERVER_URL'] = 'http://127.0.0.1:8001/api'
            
            # 导入工具函数
            from schedule_react.agent import (
                mcp_initialize, mcp_list_tools, mcp_get_schedule, 
                mcp_create_schedule, mcp_update_schedule, mcp_get_projects, 
                find_best_subtask, get_current_date
            )
            
            # 创建助手实例
            tools = [mcp_initialize, mcp_list_tools, mcp_get_schedule, 
                    mcp_create_schedule, mcp_update_schedule, mcp_get_projects, 
                    find_best_subtask, get_current_date]
            agent = ReActAgent(
                tools=tools,  # 传入正确的工具列表
                model="glm-4o-mini",  # 使用默认模型
                project_directory="/home/ubuntu"
            )
            
            # 运行助手
            result = agent.run(user_input)
            
            return jsonify({
                "success": True,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
        except ImportError as e:
            logger.error(f"导入日程ReAct助手失败: {e}")
            return jsonify({
                "error": {
                    "code": -1,
                    "message": f"导入日程ReAct助手失败: {str(e)}"
                }
            }), 500
        except Exception as e:
            logger.error(f"日程ReAct助手运行失败: {e}")
            # 记录完整的错误信息
            import traceback
            logger.error(f"完整错误信息: {traceback.format_exc()}")
            return jsonify({
                "error": {
                    "code": -1,
                    "message": f"日程ReAct助手运行失败: {str(e)}"
                }
            }), 500
        
    except Exception as e:
        logger.error(f"处理日程助手请求时发生错误: {e}")
        return jsonify({
            "error": {
                "code": -1,
                "message": f"服务器内部错误: {str(e)}"
            }
        }), 500

@app.route('/api/schedule-assistant/chat-stream', methods=['POST'])
def schedule_assistant_chat_stream():
    """日程ReAct助手流式聊天端点（ReadableStream，text/plain分块）"""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        session_id = data.get('session_id') or ''
        if not user_input:
            return jsonify({"error": "缺少user_input参数"}), 400
        try:
            from schedule_react.agent import ReActAgent
            from schedule_react.prompt import schedule_system_prompt_template
            os.environ['MCP_SERVER_URL'] = 'http://127.0.0.1:8001/api'
            from schedule_react.agent import (
                mcp_initialize, mcp_list_tools, mcp_get_schedule,
                mcp_create_schedule, mcp_update_schedule, mcp_get_projects,
                find_best_subtask, get_current_date
            )
            tools = [mcp_initialize, mcp_list_tools, mcp_get_schedule,
                    mcp_create_schedule, mcp_update_schedule, mcp_get_projects,
                    find_best_subtask, get_current_date]
            agent = ReActAgent(
                tools=tools,
                model="glm-4.5-air",
                project_directory="/home/ubuntu"
            )
            # 读取并传入历史
            session = SESSION_STORE.setdefault(session_id, {"messages": [], "cache": {}}) if session_id else {"messages": [], "cache": {}}
            history = session.get("messages") or []
            def generate():
                try:
                    for chunk in agent.run_stream(user_input, history=history):
                        if chunk:
                            yield chunk
                except Exception as e:
                    yield f"\n[stream-error] {str(e)}\n"
                finally:
                    # 回写历史与临时缓存
                    if session_id:
                        last_msgs = getattr(agent, 'last_messages', None)
                        if last_msgs:
                            SESSION_STORE[session_id]["messages"] = last_msgs
                        if hasattr(agent, "last_projects"):
                            SESSION_STORE[session_id]["cache"]["projects"] = getattr(agent, "last_projects")
                        if hasattr(agent, "last_pending"):
                            SESSION_STORE[session_id]["cache"]["last_pending"] = getattr(agent, "last_pending")
            return Response(stream_with_context(generate()), mimetype='text/plain')
        except Exception as e:
            logger.error(f"日程ReAct助手流式运行失败: {e}")
            import traceback
            logger.error(f"完整错误信息: {traceback.format_exc()}")
            return jsonify({
                "error": {"code": -1, "message": f"日程ReAct助手流式运行失败: {str(e)}"}
            }), 500
    except Exception as e:
        logger.error(f"处理流式请求时发生错误: {e}")
        return jsonify({
            "error": {"code": -1, "message": f"服务器内部错误: {str(e)}"}
        }), 500


@app.route('/api/mcp', methods=['POST'])
def mcp_proxy_endpoint():
    """MCP代理端点"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的JSON数据"}), 400
        
        method = data.get('method')
        params = data.get('params', {})
        
        if not method:
            return jsonify({"error": "缺少method参数"}), 400
        
        # 转发请求到MCP服务器
        result = mcp_proxy.send_request(method, params)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"处理MCP请求时发生错误: {e}")
        return jsonify({
            "error": {
                "code": -1,
                "message": f"服务器内部错误: {str(e)}"
            }
        }), 500

@app.route('/api/health')
def health_check():
    """健康检查端点"""
    try:
        # 测试MCP服务器连接
        result = mcp_proxy.send_request('initialize')
        
        if 'error' in result:
            return jsonify({
                "status": "error",
                "mcp_server": "disconnected",
                "error": result['error'],
                "timestamp": datetime.now().isoformat()
            }), 503
        else:
            return jsonify({
                "status": "healthy",
                "mcp_server": "connected",
                "server_info": result.get('result', {}).get('serverInfo', {}),
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "mcp_server": "unknown",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/tools')
def list_tools():
    """获取可用工具列表"""
    result = mcp_proxy.send_request('tools/list')
    return jsonify(result)

@app.route('/api/resources')
def list_resources():
    """获取可用资源列表"""
    result = mcp_proxy.send_request('resources/list')
    return jsonify(result)

@app.route('/api/schedule/<date>')
def get_schedule(date):
    """获取指定日期的日程"""
    result = mcp_proxy.send_request('tools/call', {
        "name": "get_schedule",
        "arguments": {"date": date}
    })
    return jsonify(result)

@app.route('/api/projects')
def get_projects():
    """获取项目列表"""
    result = mcp_proxy.send_request('tools/call', {
        "name": "get_projects",
        "arguments": {}
    })
    return jsonify(result)

@app.route('/api/ai-analyze', methods=['POST'])
def ai_analyze():
    """AI分析用户请求"""
    try:
        data = request.get_json()
        user_request = data.get('user_request', '')
        
        if not user_request:
            return jsonify({"error": "缺少user_request参数"}), 400
        
        result = mcp_proxy.send_request('tools/call', {
            "name": "ai_analyze",
            "arguments": {"user_request": user_request}
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI分析请求失败: {e}")
        return jsonify({
            "error": {
                "code": -1,
                "message": f"AI分析失败: {str(e)}"
            }
        }), 500

@app.route('/api/schedule-manager/request', methods=['POST'])
def schedule_manager_request():
    """Schedule Manager专用请求端点"""
    try:
        data = request.get_json()
        request_type = data.get('type', 'schedule_query')
        request_data = data.get('data', {})
        
        if request_type == 'schedule_query':
            # 查询日程
            date = request_data.get('date', datetime.now().strftime('%Y-%m-%d'))
            response = requests.get(f"{SCHEDULE_API_URL}/api/schedule/{date}", timeout=10)
            return jsonify(response.json())
            
        elif request_type == 'schedule_create':
            # 创建日程
            response = requests.post(f"{SCHEDULE_API_URL}/api/schedule", json=request_data, timeout=10)
            return jsonify(response.json())
            
        elif request_type == 'schedule_update':
            # 更新日程
            schedule_id = request_data.get('id')
            update_data = request_data.get('data', {})
            response = requests.put(f"{SCHEDULE_API_URL}/api/schedule/{schedule_id}", json=update_data, timeout=10)
            return jsonify(response.json())
            
        elif request_type == 'schedule_delete':
            # 删除日程
            schedule_id = request_data.get('id')
            response = requests.delete(f"{SCHEDULE_API_URL}/api/schedule/{schedule_id}", timeout=10)
            return jsonify(response.json())
            
        elif request_type == 'projects_query':
            # 查询项目
            response = requests.get(f"{SCHEDULE_API_URL}/api/projects", timeout=10)
            return jsonify(response.json())
            
        elif request_type == 'ai_analyze':
            # AI分析请求
            user_request = request_data.get('user_request', '')
            result = mcp_proxy.send_request('tools/call', {
                "name": "ai_analyze",
                "arguments": {"user_request": user_request}
            })
            return jsonify(result)
            
        else:
            return jsonify({"error": f"不支持的请求类型: {request_type}"}), 400
            
    except Exception as e:
        logger.error(f"Schedule Manager请求失败: {e}")
        return jsonify({
            "error": {
                "code": -1,
                "message": f"Schedule Manager请求失败: {str(e)}"
            }
        }), 500

@app.route('/api/schedule-manager/status')
def schedule_manager_status():
    """Schedule Manager状态检查"""
    try:
        # 检查MCP服务器
        mcp_status = mcp_proxy.send_request('initialize')
        
        # 检查FastAPI Schedule API
        schedule_response = requests.get(f"{SCHEDULE_API_URL}/health", timeout=5)
        
        return jsonify({
            "status": "healthy",
            "mcp_server": "connected" if 'error' not in mcp_status else "disconnected",
            "schedule_api": "connected" if schedule_response.status_code == 200 else "disconnected",
            "web_interface": "running",
            "timestamp": datetime.now().isoformat(),
            "agent_config": {
                "name": "schedule-manager",
                "mcp_enabled": True,
                "tools_available": ["get_schedule", "create_schedule", "update_schedule", "delete_schedule", "get_projects", "ai_analyze"]
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """提供静态文件"""
    return send_from_directory('static', filename)

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({"error": "页面未找到"}), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({"error": "服务器内部错误"}), 500

def get_zhipu_client():
    api_key = os.getenv('ZHIPUAI_API_KEY') or os.getenv('BIGMODEL_API_KEY') or ''
    return ZhipuAI(api_key=api_key)

# 规划：仅分析用户输入，输出严格JSON计划，不落库
@app.route('/api/schedule-assistant/plan', methods=['POST'])
def schedule_assistant_plan():
    try:
        data = request.get_json() or {}
        user_input = data.get('user_input', '').strip()
        if not user_input:
            return jsonify({"error": "缺少user_input参数"}), 400
        client = get_zhipu_client()
        system_prompt = (
            "你是一个日程规划助手。仅返回JSON，不要任何解释。\n"
            "请将用户输入解析为 plan 对象：{\n"
            "  \"actual\": [ {\"date\":\"YYYY-MM-DD\", \"time_slots\":[\"HH:MM\"...], \"notes\":\"...\"} ],\n"
            "  \"planned\": [ {\"date\":\"YYYY-MM-DD\", \"time_slots\":[\"HH:MM\"...], \"notes\":\"...\", \"query\":\"用于匹配子任务的关键词，可空\"} ]\n"
            "}\n时间粒度30分钟；若文本无具体日期，使用今天日期；notes中保留关键信息（如‘清洁’、‘研究 agent’）。"
        )
        resp = client.chat.completions.create(
            model="glm-4.5-air",
            messages=[
                {"role":"system","content":system_prompt},
                {"role":"user","content":user_input}
            ],
        )
        content = resp.choices[0].message.content or "{}"
        import json, re, copy
        try:
            plan = json.loads(content)
        except Exception:
            m = re.search(r"\{[\s\S]*\}$", content)
            if not m:
                return jsonify({"error":"LLM未返回JSON"}), 500
            plan = json.loads(m.group(0))

        matched = []
        applied_plan = copy.deepcopy(plan)
        needs_confirmation = False
        try:
            # 取项目结构
            mcp_projects = mcp_proxy.send_request('tools/call', {"name":"get_projects","arguments":{}})
            projects = mcp_projects.get('result', {})
            projects_json = json.dumps(projects, ensure_ascii=False)
            # 动态导入 find_best_subtask
            from schedule_react.agent import find_best_subtask
            for idx, item in enumerate(plan.get('planned') or []):
                q = (item or {}).get('query') or (item or {}).get('notes') or ''
                if not q:
                    matched.append({"index": idx, "query": q, "suggested": None})
                    continue
                try:
                    res = find_best_subtask(projects_json, q)
                    resj = json.loads(res)
                    matched.append({
                        "index": idx,
                        "query": q,
                        "suggested": resj
                    })
                    # 置信度>=0.7则直接应用到副本，否则需要确认
                    if (resj or {}).get('subtask_id') and float((resj or {}).get('score', 0.0)) >= 0.7:
                        applied_plan.setdefault('planned', [])[idx]["planned_subtask_id"] = resj['subtask_id']
                    else:
                        needs_confirmation = True
                except Exception:
                    matched.append({"index": idx, "query": q, "suggested": None})
                    needs_confirmation = True
        except Exception:
            # 获取项目失败则需要确认
            needs_confirmation = True
        return jsonify({
            "success": True,
            "plan": plan,
            "matched": matched,
            "applied_plan": applied_plan,
            "needs_confirmation": needs_confirmation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 提交：根据plan逐条创建记录
@app.route('/api/schedule-assistant/commit-plan', methods=['POST'])
def schedule_assistant_commit_plan():
    try:
        payload = request.get_json() or {}
        plan = payload.get('plan') or {}
        import datetime
        results = []
        def create_records(items, is_planned: bool):
            for rec in items or []:
                date = rec.get('date') or datetime.date.today().strftime('%Y-%m-%d')
                notes = rec.get('notes') or ''
                subtask_id = rec.get('planned_subtask_id') if is_planned else rec.get('actual_subtask_id')
                for ts in rec.get('time_slots') or []:
                    args = {"schedule_date": date, "time_slot": ts}
                    if is_planned:
                        if subtask_id:
                            args["planned_subtask_id"] = subtask_id
                        if notes:
                            args["planned_notes"] = notes
                    else:
                        if subtask_id:
                            args["actual_subtask_id"] = subtask_id
                        if notes:
                            args["actual_notes"] = notes
                    r = mcp_proxy.send_request('tools/call', {"name":"create_schedule","arguments": args})
                    results.append({"args": args, "result": r})
        create_records(plan.get('actual'), is_planned=False)
        create_records(plan.get('planned'), is_planned=True)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 提交：将ReAct流式会话中的 pending 写入（或直接用传入参数写入）
@app.route('/api/schedule-assistant/commit-pending', methods=['POST'])
def schedule_assistant_commit_pending():
    try:
        payload = request.get_json() or {}
        session_id = payload.get('session_id') or ''
        overrides = payload.get('overrides') or {}
        direct_args = payload.get('args') or None
        pending = None
        if session_id:
            session = SESSION_STORE.get(session_id) or {}
            pending = ((session.get('cache') or {}).get('last_pending'))
        args = None
        if pending and isinstance(pending, dict):
            if pending.get('type') == 'create_schedule':
                args = dict(pending.get('args') or {})
        if args is None and direct_args:
            args = dict(direct_args)
        if not args:
            return jsonify({"error": "没有可提交的pending，也未提供args"}), 400
        # 合并覆盖
        for k, v in (overrides.items() if isinstance(overrides, dict) else []):
            args[k] = v
        # 调用 MCP 创建
        result = mcp_proxy.send_request('tools/call', {"name": "create_schedule", "arguments": args})
        # 清理 pending
        if session_id and pending:
            try:
                SESSION_STORE[session_id]["cache"].pop("last_pending", None)
            except Exception:
                pass
        return jsonify({"success": True, "args": args, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 检查MCP服务器是否可用
    logger.info("启动Flask后端服务器...")
    logger.info(f"MCP服务器地址: {MCP_SERVER_URL}")
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=5002,  # 改为5002端口，避免与nginx代理的5000端口冲突
        debug=True,
        threaded=True
    ) 