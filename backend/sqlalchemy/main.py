from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date
import models
import schemas
from database import engine, get_db

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Timesheet SQLAlchemy API", version="1.0.0")

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def filter_valid_fields(item_data: dict) -> dict:
    """过滤掉DailySchedule模型中不存在的字段"""
    valid_fields = {
        'id', 'user_id', 'schedule_date', 'time_slot',
        'planned_subtask_id', 'planned_subtask_name', 'planned_notes', 'planned_project_color',
        'actual_subtask_id', 'actual_subtask_name', 'actual_notes', 'actual_project_color',
        'mood', 'created_at', 'updated_at'
    }
    return {k: v for k, v in item_data.items() if k in valid_fields}

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# 日程相关API
@app.post("/api/schedule", response_model=schemas.ScheduleResponse)
def create_schedule(
    schedule_data: List[schemas.ScheduleItem],
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """创建或更新日程数据"""
    try:
        results = []
        for item in schedule_data:
            if not item.schedule_date or not item.time_slot:
                continue
                
            # 过滤有效字段，避免Schema和Model字段不匹配的问题
            item_data = filter_valid_fields(item.dict(exclude_unset=True))
            
            # 查找现有记录
            existing = db.query(models.DailySchedule).filter(
                and_(
                    models.DailySchedule.user_id == user_id,
                    models.DailySchedule.schedule_date == datetime.strptime(item.schedule_date, "%Y-%m-%d").date(),
                    models.DailySchedule.time_slot == item.time_slot
                )
            ).first()
            
            if existing:
                # 更新现有记录
                for field, value in item_data.items():
                    if hasattr(existing, field) and value is not None:
                        setattr(existing, field, value)
                existing.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                results.append(existing)
            else:
                # 创建新记录 - 避免重复参数
                db_schedule = models.DailySchedule(
                    user_id=user_id,
                    **item_data
                )
                db.add(db_schedule)
                db.commit()
                db.refresh(db_schedule)
                results.append(db_schedule)
        
        return schemas.ScheduleResponse(schedule_data=results)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建日程失败: {str(e)}")

@app.get("/api/schedule/{schedule_date}", response_model=schemas.ScheduleResponse)
def get_schedule(
    schedule_date: str,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取指定日期的日程数据"""
    try:
        target_date = datetime.strptime(schedule_date, "%Y-%m-%d").date()
        schedules = db.query(models.DailySchedule).filter(
            and_(
                models.DailySchedule.user_id == user_id,
                models.DailySchedule.schedule_date == target_date
            )
        ).all()
        
        schedule_items = []
        for schedule in schedules:
            item = schemas.ScheduleItem(
                id=schedule.id,
                schedule_date=schedule.schedule_date.strftime("%Y-%m-%d"),
                time_slot=schedule.time_slot,
                planned_subtask_id=schedule.planned_subtask_id,
                planned_subtask_name=schedule.planned_subtask_name,
                planned_notes=schedule.planned_notes,
                planned_project_color=schedule.planned_project_color,
                actual_subtask_id=schedule.actual_subtask_id,
                actual_subtask_name=schedule.actual_subtask_name,
                actual_notes=schedule.actual_notes,
                actual_project_color=schedule.actual_project_color,
                mood=schedule.mood
            )
            schedule_items.append(item)
        
        return schemas.ScheduleResponse(schedule_data=schedule_items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日程失败: {str(e)}")

# 项目相关API
@app.get("/api/projects", response_model=List[schemas.ProjectResponse])
def get_projects(
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取用户的项目列表"""
    try:
        projects = db.query(models.Project).filter(
            models.Project.user_id == user_id
        ).all()
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目失败: {str(e)}")

@app.post("/api/projects", response_model=schemas.ProjectResponse)
def create_project(
    project: schemas.ProjectCreate,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """创建新项目"""
    try:
        # 查找或创建分类
        category_id = None
        if project.category_name:
            category = db.query(models.Category).filter(
                and_(
                    models.Category.user_id == user_id,
                    models.Category.name == project.category_name
                )
            ).first()
            if not category:
                category = models.Category(
                    user_id=user_id,
                    name=project.category_name,
                    color=project.color or "#4f9cff"
                )
                db.add(category)
                db.commit()
                db.refresh(category)
            category_id = category.id
        
        # 创建项目
        db_project = models.Project(
            user_id=user_id,
            category_id=category_id,
            name=project.name,
            description=project.description,
            color=project.color or "#4f9cff"
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")

# 子任务相关API
@app.get("/api/subtasks", response_model=List[schemas.SubtaskResponse])
def get_subtasks(
    user_id: int = Query(..., description="用户ID"),
    project_id: Optional[int] = Query(None, description="项目ID"),
    db: Session = Depends(get_db)
):
    """获取子任务列表"""
    try:
        query = db.query(models.Subtask).filter(models.Subtask.user_id == user_id)
        if project_id:
            query = query.filter(models.Subtask.project_id == project_id)
        subtasks = query.all()
        return subtasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取子任务失败: {str(e)}")

@app.post("/api/subtasks", response_model=schemas.SubtaskResponse)
def create_subtask(
    subtask: schemas.SubtaskCreate,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """创建新子任务"""
    try:
        db_subtask = models.Subtask(
            user_id=user_id,
            project_id=subtask.project_id,
            name=subtask.name,
            urgency_importance=subtask.urgency_importance,
            difficulty=subtask.difficulty,
            color=subtask.color or "#9cc7ff"
        )
        db.add(db_subtask)
        db.commit()
        db.refresh(db_subtask)
        return db_subtask
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建子任务失败: {str(e)}")

# 分类相关API
@app.get("/api/categories", response_model=List[schemas.CategoryResponse])
def get_categories(
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    try:
        categories = db.query(models.Category).filter(
            models.Category.user_id == user_id
        ).all()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类失败: {str(e)}")

@app.post("/api/categories", response_model=schemas.CategoryResponse)
def create_category(
    category: schemas.CategoryCreate,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """创建新分类"""
    try:
        db_category = models.Category(
            user_id=user_id,
            name=category.name,
            color=category.color or "#4f9cff"
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建分类失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5004)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5004)

