from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import mysql.connector
from mysql.connector import pooling
import json
from datetime import datetime, date
import uvicorn
from contextlib import asynccontextmanager

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
    schedule_date: str
    time_slot: str
    # 计划字段
    planned_subtask_id: Optional[int] = None
    planned_subtask_name: Optional[str] = None
    planned_notes: Optional[str] = None
    planned_project_color: Optional[str] = None
    # 实际字段
    actual_subtask_id: Optional[int] = None
    actual_subtask_name: Optional[str] = None
    actual_notes: Optional[str] = None
    actual_project_color: Optional[str] = None
    mood: Optional[str] = None

class ScheduleResponse(BaseModel):
    schedule_data: List[ScheduleItem]

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

# 初始化数据库
def init_db():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
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

@app.get("/api/schedule/{schedule_date}")
async def get_schedule(schedule_date: str, db: mysql.connector.MySQLConnection = Depends(get_db)):
    """获取指定日期的日程数据"""
    try:
        cursor = db.cursor(dictionary=True)
        
        # 获取日程数据，包括计划字段和实际字段的子任务和项目信息
        cursor.execute('''
            SELECT 
                ds.id,
                ds.schedule_date,
                ds.time_slot,
                # 计划字段
                ds.planned_subtask_id,
                ds.planned_subtask_name,
                ds.planned_notes,
                ds.planned_project_color,
                # 实际字段
                ds.actual_subtask_id,
                ds.actual_subtask_name,
                ds.actual_notes,
                ds.actual_project_color,
                ds.mood
            FROM daily_schedule ds
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
                # 计划字段
                "planned_subtask_id": row['planned_subtask_id'],
                "planned_subtask_name": row['planned_subtask_name'],
                "planned_notes": row['planned_notes'],
                "planned_project_color": row['planned_project_color'],
                # 实际字段
                "actual_subtask_id": row['actual_subtask_id'],
                "actual_subtask_name": row['actual_subtask_name'],
                "actual_notes": row['actual_notes'],
                "actual_project_color": row['actual_project_color'],
                "mood": row['mood']
            })
        
        return ScheduleResponse(schedule_data=schedule_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.post("/api/schedule")
async def create_schedule(schedule: ScheduleItem, db: mysql.connector.MySQLConnection = Depends(get_db)):
    """创建新的日程记录"""
    try:
        cursor = db.cursor(dictionary=True)
        
        cursor.execute('''
            INSERT INTO daily_schedule (
                schedule_date, time_slot, 
                planned_subtask_id, planned_subtask_name, planned_notes, planned_project_color,
                actual_subtask_id, actual_subtask_name, actual_notes, actual_project_color, mood
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            schedule.schedule_date, schedule.time_slot,
            schedule.planned_subtask_id, schedule.planned_subtask_name, schedule.planned_notes, schedule.planned_project_color,
            schedule.actual_subtask_id, schedule.actual_subtask_name, schedule.actual_notes, schedule.actual_project_color, schedule.mood
        ))
        
        db.commit()
        
        # 返回创建的记录
        schedule.id = cursor.lastrowid
        return schedule
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.put("/api/schedule/{schedule_id}")
async def update_schedule(schedule_id: int, schedule: ScheduleItem, db: mysql.connector.MySQLConnection = Depends(get_db)):
    """更新现有日程记录"""
    try:
        cursor = db.cursor(dictionary=True)
        
        # 构建动态更新语句，只更新有值的字段
        update_fields = []
        update_values = []
        
        if schedule.planned_subtask_id is not None:
            update_fields.append("planned_subtask_id = %s")
            update_values.append(schedule.planned_subtask_id)
        if schedule.planned_subtask_name is not None:
            update_fields.append("planned_subtask_name = %s")
            update_values.append(schedule.planned_subtask_name)
        if schedule.planned_notes is not None:
            update_fields.append("planned_notes = %s")
            update_values.append(schedule.planned_notes)
        if schedule.planned_project_color is not None:
            update_fields.append("planned_project_color = %s")
            update_values.append(schedule.planned_project_color)
        if schedule.actual_subtask_id is not None:
            update_fields.append("actual_subtask_id = %s")
            update_values.append(schedule.actual_subtask_id)
        if schedule.actual_subtask_name is not None:
            update_fields.append("actual_subtask_name = %s")
            update_values.append(schedule.actual_subtask_name)
        if schedule.actual_notes is not None:
            update_fields.append("actual_notes = %s")
            update_values.append(schedule.actual_notes)
        if schedule.actual_project_color is not None:
            update_fields.append("actual_project_color = %s")
            update_values.append(schedule.actual_project_color)
        if schedule.mood is not None:
            update_fields.append("mood = %s")
            update_values.append(schedule.mood)
        
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
async def delete_schedule(schedule_id: int, db: mysql.connector.MySQLConnection = Depends(get_db)):
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
async def get_projects(db: mysql.connector.MySQLConnection = Depends(get_db)):
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