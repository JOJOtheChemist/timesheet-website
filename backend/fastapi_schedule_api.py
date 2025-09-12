from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import mysql.connector
from mysql.connector import pooling
import json
from datetime import datetime, date, timedelta
import uvicorn
from contextlib import asynccontextmanager
import jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sys
import os
import random
import string

# 为 agent 解析器添加路径
if '/home/ubuntu/langchain-agent' not in sys.path:
    sys.path.append('/home/ubuntu/langchain-agent')

# LLM Agent 集成
try:
    from agent_task_planner import run_task_planner
    AGENT_AVAILABLE = True
    print("LLM Agent loaded successfully")
except ImportError as e:
    print(f"Warning: LLM Agent not available: {e}")
    AGENT_AVAILABLE = False

# 回退解析器
try:
    from parser import parse_task_fields  # type: ignore
except Exception:
    def parse_task_fields(message: str) -> Dict[str, Optional[str]]:
        return {"project_name": None, "subtask_name": None, "category_name": None, "urgency_importance": None, "difficulty": None}

def run_agent_with_user_context(message: str, user_id: int) -> Dict[str, Any]:
    """运行LLM agent并返回结果"""
    if not AGENT_AVAILABLE:
        # 回退到简单解析
        return {
            "ok": False,
            "reply": "LLM Agent暂时不可用，请使用简单格式：项目: 工作；子任务: 写日报",
            "parsed_fields": {"project_name": None, "subtask_name": None, "category_name": None, "urgency_importance": None, "difficulty": None},
            "task_created": False,
            "task_info": {"reason": "LLM Agent不可用"}
        }
    
    try:
        result = run_task_planner(message, user_id=user_id)
        return result
    except Exception as e:
        return {
            "ok": False,
            "reply": f"Agent处理出错: {str(e)}",
            "parsed_fields": {"project_name": None, "subtask_name": None, "category_name": None, "urgency_importance": None, "difficulty": None},
            "task_created": False,
            "task_info": {"error": str(e)}
        }

# 认证与安全配置
JWT_SECRET = "change_this_secret_in_env"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer(auto_error=False)
DEV_RETURN_RESET_TOKEN = True
DEV_RETURN_NEW_PASSWORD = True
ADMIN_RESET_CODE = os.getenv("ADMIN_RESET_CODE", "ADMIN-RESET-123")

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    init_db()
    print("Schedule API Database initialized successfully!")
    yield
    # 关闭时执行
    print("Schedule API shutting down...")

app = FastAPI(title="Schedule API", version="1.1.0", lifespan=lifespan)

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件挂载将在所有API路由定义后添加

# 数据模型
class ScheduleItem(BaseModel):
    id: Optional[int] = None
    schedule_date: Optional[str] = None  # 更新时可选
    time_slot: Optional[str] = None      # 更新时可选
    # 计划字段
    planned_subtask_id: Optional[int] = None
    planned_subtask_name: Optional[str] = None
    planned_subtask_color: Optional[str] = None
    planned_project_name: Optional[str] = None
    planned_project_color: Optional[str] = None
    planned_notes: Optional[str] = None
    # 实际字段
    actual_subtask_id: Optional[int] = None
    actual_subtask_name: Optional[str] = None
    actual_subtask_color: Optional[str] = None
    actual_project_name: Optional[str] = None
    actual_project_color: Optional[str] = None
    actual_notes: Optional[str] = None
    mood: Optional[str] = None

class ScheduleResponse(BaseModel):
    schedule_data: List[ScheduleItem]

# 编辑器行模型
class EditorRow(BaseModel):
    project_name: Optional[str] = None
    subtask_name: Optional[str] = None
    category_name: Optional[str] = None
    urgency_importance: Optional[str] = None
    difficulty: Optional[str] = None
    # 可选：通过ID精确更新已有记录（编辑重命名/移动时避免新增）
    category_id: Optional[int] = None
    project_id: Optional[int] = None
    subtask_id: Optional[int] = None

# 认证模型
class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    invite_code: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ResetRequest(BaseModel):
    username: str

class ResetConfirm(BaseModel):
    token: str
    new_password: str

class AdminRecover(BaseModel):
    username: str
    admin_code: str
    new_password: str

class AgentChatRequest(BaseModel):
    message: str

class AgentChatResponse(BaseModel):
    reply: str
    parsed: Dict[str, Optional[str]]
    category_id: Optional[int] = None
    project_id: Optional[int] = None
    subtask_id: Optional[int] = None
    thought: Optional[str] = None

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
    pool_name="mypool",
    pool_size=20,
    pool_reset_session=True,
    **db_config
)

# 数据库连接
def get_db():
    return connection_pool.get_connection()

# 密码与JWT工具
def hash_password(plain_password: str) -> str:
    return password_context.hash(plain_password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    return password_context.verify(plain_password, password_hash)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer)) -> Optional[Dict[str, Any]]:
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        return None

def require_user(payload: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    if not payload:
        raise HTTPException(status_code=401, detail="未认证")
    return payload

# 初始化数据库（含按用户隔离的迁移）
def init_db():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                reset_token VARCHAR(255),
                reset_expires DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username)
            )
        ''')

        # 业务表按需创建（简化版）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                color VARCHAR(20)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_id INT,
                name VARCHAR(255),
                description TEXT,
                color VARCHAR(20)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subtasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id INT,
                name VARCHAR(255),
                priority VARCHAR(50),
                urgency_importance VARCHAR(50),
                difficulty VARCHAR(50),
                color VARCHAR(20)
            )
        ''')
        # 新增：邀请码表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invite_codes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code VARCHAR(64) NOT NULL UNIQUE,
                used_by INT NULL,
                used_at DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # daily_schedule 表（包含 user_id）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_schedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
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

        # 通用：为 categories/projects/subtasks/daily_schedule 添加 user_id 列（若不存在），并将历史数据标记为 yeya 用户（id=1）
        for table in ["categories", "projects", "subtasks", "daily_schedule"]:
            try:
                cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'user_id'")
                if not cursor.fetchone():
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INT NOT NULL DEFAULT 1 AFTER id")
                    print(f"{table} 添加 user_id 列")
            except Exception as e:
                print(f"为 {table} 添加 user_id 列时出错: {e}")
        
        # 更新 daily_schedule 的唯一键为按用户唯一
        try:
            cursor.execute("SHOW INDEX FROM daily_schedule WHERE Key_name='uniq_date_slot'")
            if cursor.fetchall():
                cursor.execute("ALTER TABLE daily_schedule DROP INDEX uniq_date_slot")
        except Exception:
            pass
        try:
            cursor.execute("SHOW INDEX FROM daily_schedule WHERE Key_name='uniq_user_date_slot'")
            if not cursor.fetchall():
                cursor.execute("ALTER TABLE daily_schedule ADD UNIQUE KEY uniq_user_date_slot (user_id, schedule_date, time_slot)")
        except Exception as e:
            print(f"设置按用户唯一索引失败: {e}")
        
        conn.commit()
        print("Database tables initialized and migrated for user scoping!")
        
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# API 路由

@app.get("/")
async def root():
    return {"message": "Schedule API is running on port 5001!"}

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """处理CORS预检请求"""
    return {"message": "CORS preflight request handled"}

# 认证路由（保持不变）
@app.post("/api/auth/register", response_model=Dict[str, Any])
async def register(user: UserRegister, db: mysql.connector.MySQLConnection = Depends(get_db)):
    try:
        cursor = db.cursor(dictionary=True)
        # 校验邀请码
        cursor.execute("SELECT id, used_by FROM invite_codes WHERE code=%s", (user.invite_code,))
        invite = cursor.fetchone()
        if not invite or invite.get("used_by"):
            raise HTTPException(status_code=400, detail="无效或已使用的邀请码")
        # 校验用户名
        cursor.execute("SELECT id FROM users WHERE username=%s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="用户名已存在")
        # 创建用户
        cursor.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
            (user.username, hash_password(user.password), user.email)
        )
        user_id = cursor.lastrowid
        # 标记邀请码已使用
        cursor.execute("UPDATE invite_codes SET used_by=%s, used_at=NOW() WHERE id=%s", (user_id, invite["id"]))
        db.commit()
        return {"message": "注册成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user: UserLogin, db: mysql.connector.MySQLConnection = Depends(get_db)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username=%s", (user.username,))
        row = cursor.fetchone()
        if not row or not verify_password(user.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        token = create_access_token({"sub": row["id"], "username": row["username"]})
        return TokenResponse(access_token=token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.get("/api/auth/me", response_model=Dict[str, Any])
async def me(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="未认证")
    return {"id": current_user.get("sub"), "username": current_user.get("username")}

@app.post("/api/auth/request-reset", response_model=Dict[str, Any])
async def request_reset(body: ResetRequest, db: mysql.connector.MySQLConnection = Depends(get_db)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username=%s", (body.username,))
        row = cursor.fetchone()
        if not row:
            return {"message": "如果账号存在，重置令牌已生成"}
        token = create_access_token({"reset": row["id"], "username": body.username}, expires_delta=timedelta(minutes=30))
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        cursor.execute("UPDATE users SET reset_token=%s, reset_expires=%s WHERE id=%s", (token, expires_at, row["id"]))
        db.commit()
        response: Dict[str, Any] = {"message": "重置令牌已生成，有效期30分钟"}
        if DEV_RETURN_RESET_TOKEN:
            response["reset_token"] = token
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"请求重置失败: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.post("/api/auth/reset-password", response_model=Dict[str, Any])
async def reset_password(body: ResetConfirm, db: mysql.connector.MySQLConnection = Depends(get_db)):
    try:
        cursor = db.cursor(dictionary=True)
        try:
            payload = jwt.decode(body.token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("reset")
        except Exception:
            raise HTTPException(status_code=400, detail="无效或过期的令牌")
        cursor.execute("SELECT id, reset_expires FROM users WHERE id=%s AND reset_token=%s", (user_id, body.token))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="无效或过期的令牌")
        if row["reset_expires"] and datetime.utcnow() > row["reset_expires"]:
            raise HTTPException(status_code=400, detail="令牌已过期")
        cursor.execute("UPDATE users SET password_hash=%s, reset_token=NULL, reset_expires=NULL WHERE id=%s", (hash_password(body.new_password), user_id))
        db.commit()
        return {"message": "密码已重置，请使用新密码登录"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"重置失败: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.post("/api/auth/admin-recover", response_model=Dict[str, Any])
async def admin_recover(body: AdminRecover, db: mysql.connector.MySQLConnection = Depends(get_db)):
    if body.admin_code != ADMIN_RESET_CODE:
        raise HTTPException(status_code=403, detail="管理员校验码错误")
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username=%s", (body.username,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="用户不存在")
        # 使用提供的新密码进行重置
        if not body.new_password or len(body.new_password) < 6:
            raise HTTPException(status_code=400, detail="新密码不符合要求")
        cursor.execute("UPDATE users SET password_hash=%s WHERE id=%s", (hash_password(body.new_password), row["id"]))
        db.commit()
        return {"message": "密码已重置"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"管理员重置失败: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.post("/api/editor/row", response_model=Dict[str, Any])
async def upsert_editor_row(body: EditorRow, db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    """根据传入的行数据（分类/项目/子任务/紧急/困难）为当前用户创建或更新。
    简化规则：
    - 若category_name存在，按名称(user_id, name)查找或创建分类
    - 若project_name存在，按(user_id, name)查找或创建项目，并关联分类（如果分类存在）
    - 若subtask_name存在，按(user_id, project_id, name)查找或创建子任务，并更新紧急/困难
    返回当前行对象的IDs
    """
    try:
        cursor = db.cursor(dictionary=True)
        user_id = current_user["sub"]
        category_id = body.category_id
        project_id = body.project_id
        subtask_id = body.subtask_id

        # 分类
        if body.category_name:
            cursor.execute("SELECT id FROM categories WHERE user_id=%s AND name=%s", (user_id, body.category_name))
            row = cursor.fetchone()
            if row:
                category_id = row["id"]
            else:
                cursor.execute("INSERT INTO categories (user_id, name, color) VALUES (%s, %s, %s)", (user_id, body.category_name, "#4f9cff"))
                category_id = cursor.lastrowid
        
        # 项目
        if body.project_name:
            cursor.execute("SELECT id FROM projects WHERE user_id=%s AND name=%s", (user_id, body.project_name))
            row = cursor.fetchone()
            if row:
                project_id = row["id"]
                # 如有分类则更新项目分类
                if category_id:
                    cursor.execute("UPDATE projects SET category_id=%s WHERE id=%s", (category_id, project_id))
            else:
                cursor.execute(
                    "INSERT INTO projects (user_id, category_id, name, description, color) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, category_id, body.project_name, None, "#4f9cff")
                )
                project_id = cursor.lastrowid
        
        # 子任务：若携带 subtask_id 则精确更新，否则按名称查找或创建
        if project_id and (body.subtask_name is not None):
            if subtask_id:
                # 校验归属并执行更新（允许重命名与移动到新项目）
                cursor.execute("SELECT id FROM subtasks WHERE id=%s AND user_id=%s", (subtask_id, user_id))
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="子任务不存在或无权限")
                cursor.execute(
                    "UPDATE subtasks SET project_id=%s, name=%s, urgency_importance=%s, difficulty=%s WHERE id=%s",
                    (project_id, body.subtask_name or "", body.urgency_importance or "重要不紧急", body.difficulty or "中级", subtask_id)
                )
            else:
                # 旧逻辑：按名称查找或新增
                cursor.execute("SELECT id FROM subtasks WHERE user_id=%s AND project_id=%s AND name=%s", (user_id, project_id, body.subtask_name))
                row = cursor.fetchone()
                if row:
                    subtask_id = row["id"]
                    cursor.execute(
                        "UPDATE subtasks SET urgency_importance=%s, difficulty=%s WHERE id=%s",
                        (body.urgency_importance or "重要不紧急", body.difficulty or "中级", subtask_id)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO subtasks (user_id, project_id, name, urgency_importance, difficulty, color) VALUES (%s,%s,%s,%s,%s,%s)",
                        (user_id, project_id, body.subtask_name, body.urgency_importance or "重要不紧急", body.difficulty or "中级", "#9cc7ff")
                    )
                    subtask_id = cursor.lastrowid
        
        db.commit()
        return {
            "message": "保存成功",
            "category_id": category_id,
            "project_id": project_id,
            "subtask_id": subtask_id
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.post("/api/agent/chat", response_model=AgentChatResponse)
async def agent_chat(body: AgentChatRequest, db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    """LLM智能任务管理Agent：理解用户意图并创建任务"""
    user_id = current_user["sub"]
    
    # 使用LLM agent处理用户消息
    agent_result = run_agent_with_user_context(body.message or "", user_id)
    
    # 提取结果
    reply = agent_result.get("reply", "处理完成")
    parsed_fields = agent_result.get("parsed_fields", {})
    task_created = agent_result.get("task_created", False)
    task_info = agent_result.get("task_info", {})
    
    # 如果agent已经创建了任务，直接返回结果
    if task_created and task_info:
        # task_info是列表，取第一个任务的ids
        if isinstance(task_info, list) and len(task_info) > 0:
            ids = task_info[0].get("ids", {})
        else:
            ids = task_info.get("ids", {}) if isinstance(task_info, dict) else {}
        return AgentChatResponse(
            reply=reply,
            parsed=parsed_fields,
            category_id=ids.get("category_id"),
            project_id=ids.get("project_id"),
            subtask_id=ids.get("subtask_id"),
            thought=agent_result.get("thought", "")
        )
    
    # 如果agent没有创建任务，但解析出了字段，尝试创建
    if parsed_fields.get("project_name") and parsed_fields.get("subtask_name"):
        try:
            cursor = db.cursor(dictionary=True)
            category_id = None
            project_id = None
            subtask_id = None
            
            # 分类
            if parsed_fields.get("category_name"):
                cursor.execute("SELECT id FROM categories WHERE user_id=%s AND name=%s", (user_id, parsed_fields["category_name"]))
                row = cursor.fetchone()
                if row:
                    category_id = row["id"]
                else:
                    cursor.execute("INSERT INTO categories (user_id, name, color) VALUES (%s, %s, %s)", (user_id, parsed_fields["category_name"], "#4f9cff"))
                    category_id = cursor.lastrowid
            
            # 项目
            cursor.execute("SELECT id FROM projects WHERE user_id=%s AND name=%s", (user_id, parsed_fields["project_name"]))
            row = cursor.fetchone()
            if row:
                project_id = row["id"]
                if category_id:
                    cursor.execute("UPDATE projects SET category_id=%s WHERE id=%s", (category_id, project_id))
            else:
                cursor.execute(
                    "INSERT INTO projects (user_id, category_id, name, description, color) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, category_id, parsed_fields["project_name"], None, "#4f9cff")
                )
                project_id = cursor.lastrowid
            
            # 子任务
            if project_id:
                cursor.execute("SELECT id FROM subtasks WHERE user_id=%s AND project_id=%s AND name=%s", (user_id, project_id, parsed_fields["subtask_name"]))
                row = cursor.fetchone()
                if row:
                    subtask_id = row["id"]
                    cursor.execute(
                        "UPDATE subtasks SET urgency_importance=%s, difficulty=%s WHERE id=%s",
                        (parsed_fields.get("urgency_importance") or "重要不紧急", parsed_fields.get("difficulty") or "中级", subtask_id)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO subtasks (user_id, project_id, name, urgency_importance, difficulty, color) VALUES (%s,%s,%s,%s,%s,%s)",
                        (user_id, project_id, parsed_fields["subtask_name"], parsed_fields.get("urgency_importance") or "重要不紧急", parsed_fields.get("difficulty") or "中级", "#9cc7ff")
                    )
                    subtask_id = cursor.lastrowid
            
            db.commit()
            reply += "。任务已保存"
            
            return AgentChatResponse(
                reply=reply,
                parsed=parsed_fields,
                category_id=category_id,
                project_id=project_id,
                subtask_id=subtask_id
            )
            
        except Exception as e:
            db.rollback()
            reply += f"。保存失败: {str(e)}"
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            db.close()
    
    # 返回agent的回复，即使没有创建任务
    return AgentChatResponse(
        reply=reply,
        parsed=parsed_fields,
        category_id=None,
        project_id=None,
        subtask_id=None
    )

# 业务路由（受保护，按用户隔离）
@app.get("/api/schedule/{schedule_date}")
async def get_schedule(schedule_date: str, db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    try:
        cursor = db.cursor(dictionary=True)
        
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
            LEFT JOIN subtasks ps ON ds.planned_subtask_id = ps.id AND ps.user_id = ds.user_id
            LEFT JOIN projects pp ON ps.project_id = pp.id AND pp.user_id = ds.user_id
            LEFT JOIN subtasks asub ON ds.actual_subtask_id = asub.id AND asub.user_id = ds.user_id
            LEFT JOIN projects ap ON asub.project_id = ap.id AND ap.user_id = ds.user_id
            WHERE ds.user_id = %s AND ds.schedule_date = %s
            ORDER BY ds.time_slot
        ''', (current_user["sub"], schedule_date))
        
        rows = cursor.fetchall()
        schedule_data = []
        for row in rows:
            schedule_data.append({
                "id": row['id'],
                "schedule_date": row['schedule_date'].isoformat() if row['schedule_date'] else None,
                "time_slot": row['time_slot'],
                "planned_subtask_id": row['planned_subtask_id'],
                "planned_subtask_name": row['planned_subtask_name'],
                "planned_subtask_color": row['planned_subtask_color'],
                "planned_project_name": row['planned_project_name'],
                "planned_project_color": row['planned_project_color'],
                "planned_notes": row['planned_notes'],
                "actual_subtask_id": row['actual_subtask_id'],
                "actual_subtask_name": row['actual_subtask_name'],
                "actual_subtask_color": row['actual_subtask_color'],
                "actual_project_name": row['actual_project_name'],
                "actual_project_color": row['actual_project_color'],
                "actual_notes": row['actual_notes'],
                "mood": row['mood']
            })
        return ScheduleResponse(schedule_data=schedule_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.post("/api/schedule")
async def create_schedule(schedule: ScheduleItem, db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('''
            INSERT INTO daily_schedule (
                user_id,
                schedule_date, time_slot,
                planned_subtask_id, planned_notes,
                actual_subtask_id, actual_notes, mood
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                planned_subtask_id = VALUES(planned_subtask_id),
                planned_notes = VALUES(planned_notes),
                actual_subtask_id = VALUES(actual_subtask_id),
                actual_notes = VALUES(actual_notes),
                mood = VALUES(mood),
                updated_at = CURRENT_TIMESTAMP
        ''', (
            current_user["sub"],
            schedule.schedule_date, schedule.time_slot,
            schedule.planned_subtask_id, schedule.planned_notes,
            schedule.actual_subtask_id, schedule.actual_notes, schedule.mood
        ))
        db.commit()
        cursor.execute('''
            SELECT id FROM daily_schedule WHERE user_id=%s AND schedule_date=%s AND time_slot=%s
        ''', (current_user["sub"], schedule.schedule_date, schedule.time_slot))
        row = cursor.fetchone()
        if row:
            schedule.id = row['id']
        return schedule
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.put("/api/schedule/{schedule_id}")
async def update_schedule(schedule_id: int, schedule: ScheduleItem, db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    try:
        cursor = db.cursor(dictionary=True)
        update_fields = []
        update_values = []
        if hasattr(schedule, 'planned_subtask_id'):
            if schedule.planned_subtask_id is not None:
                update_fields.append("planned_subtask_id = %s"); update_values.append(schedule.planned_subtask_id)
            else:
                update_fields.append("planned_subtask_id = NULL")
        if hasattr(schedule, 'planned_notes'):
            if schedule.planned_notes is not None:
                update_fields.append("planned_notes = %s"); update_values.append(schedule.planned_notes)
            else:
                update_fields.append("planned_notes = NULL")
        if hasattr(schedule, 'actual_subtask_id'):
            if schedule.actual_subtask_id is not None:
                update_fields.append("actual_subtask_id = %s"); update_values.append(schedule.actual_subtask_id)
            else:
                update_fields.append("actual_subtask_id = NULL")
        if hasattr(schedule, 'actual_notes'):
            if schedule.actual_notes is not None:
                update_fields.append("actual_notes = %s"); update_values.append(schedule.actual_notes)
            else:
                update_fields.append("actual_notes = NULL")
        if hasattr(schedule, 'mood'):
            if schedule.mood is not None:
                update_fields.append("mood = %s"); update_values.append(schedule.mood)
            else:
                update_fields.append("mood = NULL")
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_values.extend([schedule_id, current_user["sub"]])
        cursor.execute(f'''
            UPDATE daily_schedule 
            SET {', '.join(update_fields)}
            WHERE id = %s AND user_id = %s
        ''', update_values)
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Schedule not found")
        db.commit()
        schedule.id = schedule_id
        return schedule
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.delete("/api/schedule/{schedule_id}")
async def delete_schedule(schedule_id: int, db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('DELETE FROM daily_schedule WHERE id = %s AND user_id = %s', (schedule_id, current_user["sub"]))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Schedule not found")
        db.commit()
        return {"message": "Schedule deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete schedule: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.get("/api/projects")
async def get_projects(db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute('SELECT id, name, color FROM categories WHERE user_id=%s ORDER BY id', (current_user["sub"],))
        categories = cursor.fetchall()
        cursor.execute('''
            SELECT id, category_id, name, description, color 
            FROM projects 
            WHERE user_id=%s
            ORDER BY category_id, id
        ''', (current_user["sub"],))
        projects = cursor.fetchall()
        cursor.execute('''
            SELECT id, project_id, name, priority, urgency_importance, difficulty, color
            FROM subtasks 
            WHERE user_id=%s
            ORDER BY project_id, id
        ''', (current_user["sub"],))
        subtasks = cursor.fetchall()
        result = []
        for category in categories:
            category_projects = []
            for project in projects:
                if project["category_id"] == category["id"]:
                    project_subtasks = [
                        {
                            "id": subtask["id"],
                            "name": subtask["name"],
                            "priority": subtask["priority"],
                            "urgency_importance": subtask["urgency_importance"],
                            "difficulty": subtask["difficulty"],
                            "difficulty_class": (subtask.get("difficulty") or "").lower().replace("级", ""),
                            "color": subtask["color"]
                        }
                        for subtask in subtasks
                        if subtask["project_id"] == project["id"]
                    ]
                    category_projects.append({
                        "id": project["id"],
                        "name": project["name"],
                        "description": project["description"],
                        "color": project["color"],
                        "subtasks": project_subtasks
                    })
            result.append({
                "id": category["id"],
                "name": category["name"],
                "color": category["color"],
                "projects": category_projects
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.delete("/api/subtasks", response_model=Dict[str, Any])
async def delete_subtasks(ids: List[int] = Query(...), db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    try:
        if not ids:
            return {"message": "无可删除的任务", "deleted": 0}
        cursor = db.cursor()
        # 仅删除当前用户的这些子任务
        format_strings = ",".join(["%s"] * len(ids))
        params = ids + [current_user["sub"]]
        cursor.execute(f"DELETE FROM subtasks WHERE id IN ({format_strings}) AND user_id = %s", params)
        deleted = cursor.rowcount
        db.commit()
        return {"message": "删除完成", "deleted": deleted}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.post("/api/subtasks/delete", response_model=Dict[str, Any])
async def delete_subtasks_post(payload: Dict[str, Any], db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    try:
        ids = payload.get("ids") or []
        if not isinstance(ids, list):
            raise HTTPException(status_code=400, detail="ids参数必须为数组")
        ids = [int(i) for i in ids if str(i).isdigit()]
        if not ids:
            return {"message": "无可删除的任务", "deleted": 0}
        cursor = db.cursor()
        format_strings = ",".join(["%s"] * len(ids))
        params = ids + [current_user["sub"]]
        cursor.execute(f"DELETE FROM subtasks WHERE id IN ({format_strings}) AND user_id = %s", params)
        deleted = cursor.rowcount
        db.commit()
        return {"message": "删除完成", "deleted": deleted}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 挂载静态文件（必须在所有API路由之后）
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    print("Starting Schedule API on port 5001...")
    print("API documentation available at: http://140.143.194.215:5001/docs")
    print("API will be accessible from external networks")
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=False) 

@app.post("/api/agent/chat/stream")
async def agent_chat_stream(body: AgentChatRequest, db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    """LLM智能任务管理Agent流式返回：理解用户意图并创建任务"""
    user_id = current_user["sub"]
    
    async def generate():
        try:
            # 使用LLM agent处理用户消息
            agent_result = run_agent_with_user_context(body.message or "", user_id)
            
            # 先返回thought
            if agent_result.get("thought"):
                yield f"data: {json.dumps({'type': 'thought', 'content': agent_result['thought']}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.1)  # 小延迟让用户看到thought
            
            # 然后返回回复
            reply = agent_result.get("reply", "处理完成")
            yield f"data: {json.dumps({'type': 'reply', 'content': reply}, ensure_ascii=False)}\n\n"
            
            # 最后返回任务信息
            task_created = agent_result.get("task_created", False)
            task_info = agent_result.get("task_info", {})
            
            if task_created and task_info:
                if isinstance(task_info, list) and len(task_info) > 0:
                    ids = task_info[0].get("ids", {})
                else:
                    ids = task_info.get("ids", {}) if isinstance(task_info, dict) else {}
                
                yield f"data: {json.dumps({'type': 'task_info', 'content': {'category_id': ids.get('category_id'), 'project_id': ids.get('project_id'), 'subtask_id': ids.get('subtask_id')}}, ensure_ascii=False)}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")
