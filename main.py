from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import json
from datetime import datetime, date
import uvicorn
import os

app = FastAPI(title="Timesheet Management System", version="1.0.0")

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 数据模型
class ScheduleItem(BaseModel):
    id: Optional[int] = None
    schedule_date: str
    time_slot: str
    planned_subtask_id: Optional[int] = None
    planned_notes: Optional[str] = None
    actual_subtask_id: Optional[int] = None
    actual_notes: Optional[str] = None
    mood: Optional[str] = None
    project_color: Optional[str] = None

class Project(BaseModel):
    id: int
    name: str
    color: str
    category_id: int

class Category(BaseModel):
    id: int
    name: str
    color: str
    projects: List[Project]

class ScheduleResponse(BaseModel):
    schedule_data: List[ScheduleItem]

# 数据库连接
def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'timesheet.db')
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 创建日程表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            planned_subtask_id INTEGER,
            planned_notes TEXT,
            actual_subtask_id INTEGER,
            actual_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 检查是否需要迁移数据（从旧结构迁移到新结构）
    cursor.execute("PRAGMA table_info(schedules)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # 如果只有旧字段，需要添加新字段
    if 'subtask_id' in columns and 'actual_subtask_id' not in columns:
        print("正在迁移数据库结构...")
        
        # 添加新字段
        cursor.execute("ALTER TABLE schedules ADD COLUMN planned_subtask_id INTEGER")
        cursor.execute("ALTER TABLE schedules ADD COLUMN planned_notes TEXT")
        cursor.execute("ALTER TABLE schedules ADD COLUMN actual_subtask_id INTEGER")
        cursor.execute("ALTER TABLE schedules ADD COLUMN actual_notes TEXT")
        
        # 将现有数据迁移到actual字段
        cursor.execute("UPDATE schedules SET actual_subtask_id = subtask_id, actual_notes = notes")
        
        # 删除旧字段（SQLite不支持直接删除字段，所以我们重命名表）
        cursor.execute("ALTER TABLE schedules RENAME TO schedules_old")
        
        # 创建新表
        cursor.execute('''
            CREATE TABLE schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                planned_subtask_id INTEGER,
                planned_notes TEXT,
                actual_subtask_id INTEGER,
                actual_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 迁移数据
        cursor.execute('''
            INSERT INTO schedules (id, schedule_date, time_slot, planned_subtask_id, planned_notes, actual_subtask_id, actual_notes, created_at)
            SELECT id, schedule_date, time_slot, NULL, NULL, actual_subtask_id, actual_notes, created_at
            FROM schedules_old
        ''')
        
        # 删除旧表
        cursor.execute("DROP TABLE schedules_old")
        
        print("数据库结构迁移完成")
    
    # 创建项目分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT NOT NULL
        )
    ''')
    
    # 创建项目表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # 创建子任务表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            project_id INTEGER,
            urgency_importance TEXT DEFAULT '不重要不紧急',
            difficulty TEXT DEFAULT '中级',
            difficulty_class TEXT DEFAULT 'bg-gray-100 text-gray-800 border-gray-200',
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    # 插入示例数据
    cursor.execute('''
        INSERT OR IGNORE INTO categories (id, name, color) VALUES 
        (1, '工作', '#007bff'),
        (2, '学习', '#28a745'),
        (3, '生活', '#ffc107')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO projects (id, name, color, category_id) VALUES 
        (1, '项目A', '#007bff', 1),
        (2, '项目B', '#28a745', 1),
        (3, '学习Python', '#ffc107', 2),
        (4, '健身', '#dc3545', 3)
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO subtasks (id, name, project_id, urgency_importance, difficulty, difficulty_class) VALUES 
        (1, '开发功能A', 1, '紧急重要', '困难', 'bg-red-100 text-red-800 border-red-200'),
        (2, '测试功能B', 2, '重要不紧急', '简单', 'bg-green-100 text-green-800 border-green-200'),
        (3, '学习FastAPI', 3, '重要不紧急', '中级', 'bg-blue-100 text-blue-800 border-blue-200'),
        (4, '跑步30分钟', 4, '不重要不紧急', '简单', 'bg-gray-100 text-gray-800 border-gray-200')
    ''')
    
    conn.commit()
    conn.close()

# API 路由

@app.get("/")
async def root():
    """根路径，返回HTML页面"""
    return FileResponse('daily_schedule.html')

@app.get("/api/schedule/{schedule_date}")
async def get_schedule(schedule_date: str, db: sqlite3.Connection = Depends(get_db)):
    """获取指定日期的日程数据"""
    try:
        cursor = db.cursor()
        
        # 确保存在 mood 列（轻量校验）
        cursor.execute("PRAGMA table_info(schedules)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'mood' not in columns:
            cursor.execute("ALTER TABLE schedules ADD COLUMN mood TEXT")
            db.commit()
        
        # 获取日程数据，包括计划和实际的子任务和项目信息
        cursor.execute('''
            SELECT 
                s.id,
                s.schedule_date,
                s.time_slot,
                s.planned_subtask_id,
                s.planned_notes,
                s.actual_subtask_id,
                s.actual_notes,
                s.mood,
                pp.color as planned_project_color,
                pst.name as planned_subtask_name,
                ap.color as actual_project_color,
                ast.name as actual_subtask_name
            FROM schedules s
            LEFT JOIN subtasks pst ON s.planned_subtask_id = pst.id
            LEFT JOIN projects pp ON pst.project_id = pp.id
            LEFT JOIN subtasks ast ON s.actual_subtask_id = ast.id
            LEFT JOIN projects ap ON ast.project_id = ap.id
            WHERE s.schedule_date = ?
            ORDER BY s.time_slot
        ''', (schedule_date,))
        
        rows = cursor.fetchall()
        schedule_data = []
        
        for row in rows:
            schedule_data.append({
                "id": row['id'],
                "schedule_date": row['schedule_date'],
                "time_slot": row['time_slot'],
                "planned_subtask_id": row['planned_subtask_id'],
                "planned_subtask_name": row['planned_subtask_name'],
                "planned_notes": row['planned_notes'],
                "actual_subtask_id": row['actual_subtask_id'],
                "actual_subtask_name": row['actual_subtask_name'],
                "actual_notes": row['actual_notes'],
                "mood": row['mood'],
                "planned_project_color": row['planned_project_color'],
                "actual_project_color": row['actual_project_color']
            })
        
        return ScheduleResponse(schedule_data=schedule_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/schedule")
async def create_schedule(schedule: ScheduleItem, db: sqlite3.Connection = Depends(get_db)):
    """创建新的日程记录"""
    try:
        cursor = db.cursor()
        
        # 确保存在 mood 列
        cursor.execute("PRAGMA table_info(schedules)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'mood' not in columns:
            cursor.execute("ALTER TABLE schedules ADD COLUMN mood TEXT")
            db.commit()
        
        cursor.execute('''
            INSERT INTO schedules (schedule_date, time_slot, planned_subtask_id, planned_notes, actual_subtask_id, actual_notes, mood)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            schedule.schedule_date, schedule.time_slot, 
              schedule.planned_subtask_id, schedule.planned_notes,
            schedule.actual_subtask_id, schedule.actual_notes,
            schedule.mood
        ))
        
        db.commit()
        
        # 返回创建的记录
        schedule.id = cursor.lastrowid
        return schedule
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")

@app.put("/api/schedule/{schedule_id}")
async def update_schedule(schedule_id: int, schedule: ScheduleItem, db: sqlite3.Connection = Depends(get_db)):
    """更新现有日程记录"""
    try:
        cursor = db.cursor()
        
        # 先获取现有记录（包含 mood）
        cursor.execute('SELECT planned_subtask_id, planned_notes, actual_subtask_id, actual_notes, mood FROM schedules WHERE id = ?', (schedule_id,))
        existing_record = cursor.fetchone()
        
        if not existing_record:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        # 只更新提供的字段，保留现有值
        update_planned_subtask_id = schedule.planned_subtask_id if schedule.planned_subtask_id is not None else existing_record['planned_subtask_id']
        update_planned_notes = schedule.planned_notes if schedule.planned_notes is not None else existing_record['planned_notes']
        update_actual_subtask_id = schedule.actual_subtask_id if schedule.actual_subtask_id is not None else existing_record['actual_subtask_id']
        update_actual_notes = schedule.actual_notes if schedule.actual_notes is not None else existing_record['actual_notes']
        update_mood = schedule.mood if schedule.mood is not None else existing_record['mood']
        
        cursor.execute('''
            UPDATE schedules 
            SET planned_subtask_id = ?, planned_notes = ?, actual_subtask_id = ?, actual_notes = ?, mood = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (update_planned_subtask_id, update_planned_notes, update_actual_subtask_id, update_actual_notes, update_mood, schedule_id))
        
        db.commit()
        
        # 返回更新后的记录
        schedule.id = schedule_id
        schedule.planned_subtask_id = update_planned_subtask_id
        schedule.planned_notes = update_planned_notes
        schedule.actual_subtask_id = update_actual_subtask_id
        schedule.actual_notes = update_actual_notes
        schedule.mood = update_mood
        return schedule
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update schedule: {str(e)}")

@app.get("/api/projects")
async def get_projects(db: sqlite3.Connection = Depends(get_db)):
    """获取项目列表，按分类组织"""
    try:
        cursor = db.cursor()
        
        # 获取所有分类
        cursor.execute('SELECT id, name, color FROM categories ORDER BY id')
        categories = cursor.fetchall()
        
        result = []
        
        for category in categories:
            # 获取该分类下的项目
            cursor.execute('''
                SELECT id, name, color, category_id 
                FROM projects 
                WHERE category_id = ? 
                ORDER BY id
            ''', (category['id'],))
            
            projects = cursor.fetchall()
            
            # 获取每个项目的子任务
            project_list = []
            for project in projects:
                cursor.execute('''
                    SELECT id, name, urgency_importance, difficulty, difficulty_class
                    FROM subtasks 
                    WHERE project_id = ? 
                    ORDER BY id
                ''', (project['id'],))
                
                subtasks = cursor.fetchall()
                
                # 转换为字典格式
                subtask_list = [
                    {
                        'id': st['id'],
                        'name': st['name'],
                        'urgency_importance': st['urgency_importance'],
                        'difficulty': st['difficulty'],
                        'difficulty_class': st['difficulty_class']
                    } for st in subtasks
                ]
                
                project_obj = {
                    'id': project['id'],
                    'name': project['name'],
                    'color': project['color'],
                    'category_id': project['category_id'],
                    'subtasks': subtask_list
                }
                
                project_list.append(project_obj)
            
            # 创建分类对象
            category_obj = Category(
                id=category['id'],
                name=category['name'],
                color=category['color'],
                projects=project_list
            )
            
            result.append(category_obj)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized successfully!")

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("API documentation available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False) 