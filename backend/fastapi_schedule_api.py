from fastapi import FastAPI, HTTPException, Depends
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

# 认证与安全配置
JWT_SECRET = "change_this_secret_in_env"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer(auto_error=False)
DEV_RETURN_RESET_TOKEN = True

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    init_db()
    print("Schedule API Database initialized successfully!")
    yield
    # 关闭时执行
    print("Schedule API shutting down...")

app = FastAPI(title="Schedule API", version="1.0.0", lifespan=lifespan)

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# 认证模型
class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

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
    pool_size=5,
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

# 初始化数据库
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

        # 检查daily_schedule表是否存在，如果不存在则创建
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_schedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                schedule_date DATE NOT NULL,
                time_slot VARCHAR(10) NOT NULL,
                # 计划字段
                planned_subtask_id INT,
                planned_subtask_name VARCHAR(255),
                planned_notes TEXT,
                planned_project_color VARCHAR(20),
                # 实际字段
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

        # 确保唯一索引：同一天同一时间槽只允许一条记录（计划/实际共用一行）
        try:
            cursor.execute('''
                ALTER TABLE daily_schedule
                ADD UNIQUE KEY uniq_date_slot (schedule_date, time_slot)
            ''')
        except Exception:
            # 可能已存在则忽略
            pass
        
        # 检查是否需要迁移旧数据
        cursor.execute("SHOW COLUMNS FROM daily_schedule LIKE 'subtask_id'")
        if cursor.fetchone():
            print("检测到旧表结构，开始迁移数据...")
            try:
                # 添加新字段
                cursor.execute('''
                    ALTER TABLE daily_schedule 
                    ADD COLUMN planned_subtask_id INT AFTER time_slot,
                    ADD COLUMN planned_subtask_name VARCHAR(255) AFTER planned_subtask_id,
                    ADD COLUMN planned_notes TEXT AFTER planned_subtask_name,
                    ADD COLUMN planned_project_color VARCHAR(20) AFTER planned_notes,
                    ADD COLUMN actual_subtask_id INT AFTER planned_project_color,
                    ADD COLUMN actual_subtask_name VARCHAR(255) AFTER actual_subtask_id,
                    ADD COLUMN actual_notes TEXT AFTER actual_subtask_name,
                    ADD COLUMN actual_project_color VARCHAR(20) AFTER actual_notes
                ''')
                
                # 迁移旧数据到新字段
                cursor.execute('''
                    UPDATE daily_schedule 
                    SET planned_subtask_id = subtask_id,
                        planned_subtask_name = subtask_name,
                        planned_notes = notes,
                        planned_project_color = project_color
                    WHERE subtask_id IS NOT NULL OR notes IS NOT NULL
                ''')
                
                # 删除旧字段
                cursor.execute('''
                    ALTER TABLE daily_schedule 
                    DROP COLUMN subtask_id,
                    DROP COLUMN subtask_name,
                    DROP COLUMN notes,
                    DROP COLUMN project_color
                ''')
                
                print("数据迁移完成！")
            except Exception as e:
                print(f"数据迁移失败: {str(e)}")
                conn.rollback()
        
        conn.commit()
        print("Database tables initialized successfully!")
        
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

# 认证路由
@app.post("/api/auth/register", response_model=Dict[str, Any])
async def register(user: UserRegister, db: mysql.connector.MySQLConnection = Depends(get_db)):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id FROM users WHERE username=%s", (user.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="用户名已存在")
        cursor.execute(
            "INSERT INTO users (username, password_hash, email) VALUES (%s, %s, %s)",
            (user.username, hash_password(user.password), user.email)
        )
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
            # 即使不存在也返回成功，防止用户枚举
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
        # 验证token
        try:
            payload = jwt.decode(body.token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("reset")
        except Exception:
            raise HTTPException(status_code=400, detail="无效或过期的令牌")
        # 匹配数据库中的令牌并检查过期
        cursor.execute("SELECT id, reset_expires FROM users WHERE id=%s AND reset_token=%s", (user_id, body.token))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=400, detail="无效或过期的令牌")
        if row["reset_expires"] and datetime.utcnow() > row["reset_expires"]:
            raise HTTPException(status_code=400, detail="令牌已过期")
        # 更新密码并清除令牌
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

# 下面保留原有业务路由（受保护）
@app.get("/api/schedule/{schedule_date}")
async def get_schedule(schedule_date: str, db: mysql.connector.MySQLConnection = Depends(get_db), current_user: Dict[str, Any] = Depends(require_user)):
    """获取指定日期的日程数据"""
    try:
        cursor = db.cursor(dictionary=True)
        
        # 通过JOIN获取完整的日程数据，包括子任务和项目信息
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
                -- 计划子任务信息
                ps.name as planned_subtask_name,
                ps.color as planned_subtask_color,
                pp.name as planned_project_name,
                pp.color as planned_project_color,
                -- 实际子任务信息
                asub.name as actual_subtask_name,
                asub.color as actual_subtask_color,
                ap.name as actual_project_name,
                ap.color as actual_project_color
            FROM daily_schedule ds
            -- 左连接计划子任务和项目
            LEFT JOIN subtasks ps ON ds.planned_subtask_id = ps.id
            LEFT JOIN projects pp ON ps.project_id = pp.id
            -- 左连接实际子任务和项目
            LEFT JOIN subtasks asub ON ds.actual_subtask_id = asub.id
            LEFT JOIN projects ap ON asub.project_id = ap.id
            WHERE ds.schedule_date = %s
            ORDER BY ds.time_slot
        ''', (schedule_date,))
        
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
    """创建新的日程记录（同一时间槽幂等：存在则更新）"""
    try:
        cursor = db.cursor(dictionary=True)
        
        # 使用 upsert，若该时间槽已存在则更新对应字段
        cursor.execute('''
            INSERT INTO daily_schedule (
                schedule_date, time_slot,
                planned_subtask_id, planned_notes,
                actual_subtask_id, actual_notes, mood
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                planned_subtask_id = VALUES(planned_subtask_id),
                planned_notes = VALUES(planned_notes),
                actual_subtask_id = VALUES(actual_subtask_id),
                actual_notes = VALUES(actual_notes),
                mood = VALUES(mood),
                updated_at = CURRENT_TIMESTAMP
        ''', (
            schedule.schedule_date, schedule.time_slot,
            schedule.planned_subtask_id, schedule.planned_notes,
            schedule.actual_subtask_id, schedule.actual_notes, schedule.mood
        ))
        
        db.commit()
        
        # 返回创建/更新的记录：重新查询该时间槽行
        cursor.execute('''
            SELECT id FROM daily_schedule WHERE schedule_date=%s AND time_slot=%s
        ''', (schedule.schedule_date, schedule.time_slot))
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
    """更新现有日程记录"""
    try:
        cursor = db.cursor(dictionary=True)
        
        # 构建动态更新语句，只更新有值的字段
        update_fields = []
        update_values = []
        
        # 对于subtask_id字段，允许null值（用于删除）
        if hasattr(schedule, 'planned_subtask_id') and schedule.planned_subtask_id is not None:
            update_fields.append("planned_subtask_id = %s")
            update_values.append(schedule.planned_subtask_id)
        elif hasattr(schedule, 'planned_subtask_id') and schedule.planned_subtask_id is None:
            update_fields.append("planned_subtask_id = NULL")
            
        if hasattr(schedule, 'planned_notes') and schedule.planned_notes is not None:
            update_fields.append("planned_notes = %s")
            update_values.append(schedule.planned_notes)
        elif hasattr(schedule, 'planned_notes') and schedule.planned_notes is None:
            update_fields.append("planned_notes = NULL")
            
        if hasattr(schedule, 'actual_subtask_id') and schedule.actual_subtask_id is not None:
            update_fields.append("actual_subtask_id = %s")
            update_values.append(schedule.actual_subtask_id)
        elif hasattr(schedule, 'actual_subtask_id') and schedule.actual_subtask_id is None:
            update_fields.append("actual_subtask_id = NULL")
            
        if hasattr(schedule, 'actual_notes') and schedule.actual_notes is not None:
            update_fields.append("actual_notes = %s")
            update_values.append(schedule.actual_notes)
        elif hasattr(schedule, 'actual_notes') and schedule.actual_notes is None:
            update_fields.append("actual_notes = NULL")
            
        if hasattr(schedule, 'mood') and schedule.mood is not None:
            update_fields.append("mood = %s")
            update_values.append(schedule.mood)
        elif hasattr(schedule, 'mood') and schedule.mood is None:
            update_fields.append("mood = NULL")
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        update_values.append(schedule_id)
        
        cursor.execute(f'''
            UPDATE daily_schedule 
            SET {', '.join(update_fields)}
            WHERE id = %s
        ''', update_values)
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        db.commit()
        
        # 返回更新后的记录
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
    """删除日程记录"""
    try:
        cursor = db.cursor(dictionary=True)
        
        cursor.execute('DELETE FROM daily_schedule WHERE id = %s', (schedule_id,))
        
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
    """获取项目列表，按分类组织"""
    try:
        cursor = db.cursor(dictionary=True)
        
        # 获取所有分类
        cursor.execute('SELECT id, name, color FROM categories ORDER BY id')
        categories = cursor.fetchall()
        
        # 获取所有项目
        cursor.execute('''
            SELECT id, category_id, name, description, color 
            FROM projects 
            ORDER BY category_id, id
        ''')
        projects = cursor.fetchall()
        
        # 获取所有子任务
        cursor.execute('''
            SELECT id, project_id, name, priority, urgency_importance, difficulty, color
            FROM subtasks 
            ORDER BY project_id, id
        ''')
        subtasks = cursor.fetchall()
        
        # 按分类组织项目数据
        result = []
        for category in categories:
            category_projects = []
            for project in projects:
                if project["category_id"] == category["id"]:
                    # 获取该项目的子任务
                    project_subtasks = [
                        {
                            "id": subtask["id"],
                            "name": subtask["name"],
                            "priority": subtask["priority"],
                            "urgency_importance": subtask["urgency_importance"],
                            "difficulty": subtask["difficulty"],
                            "difficulty_class": subtask["difficulty"].lower().replace("级", "").replace("级", ""),
                            "color": subtask["color"]  # 使用子任务自己的颜色
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

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 启动时初始化数据库
# @app.on_event("startup")
# async def startup_event():
#     init_db()
#     print("Schedule API Database initialized successfully!")

if __name__ == "__main__":
    print("Starting Schedule API on port 5001...")
    print("API documentation available at: http://140.143.194.215:5001/docs")
    print("API will be accessible from external networks")
    uvicorn.run(app, host="0.0.0.0", port=5001, reload=False) 