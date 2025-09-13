#!/usr/bin/env python3
"""
SQLAlchemy模块集成示例
展示如何在现有FastAPI应用中集成SQLAlchemy模块
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# 添加sqlalchemy模块路径
sys.path.append('/home/ubuntu/timesheet/backend/sqlalchemy')

# 导入SQLAlchemy模块
from models import DailySchedule, Project, Subtask, Category
from schemas import ScheduleItem, ScheduleResponse, ProjectCreate, ProjectResponse
from database import get_db
from services import ScheduleService, ProjectService

app = FastAPI(title="Timesheet Integration Example")

# 示例：集成日程服务
@app.post("/api/schedule", response_model=ScheduleResponse)
def create_schedule_integrated(
    schedule_data: List[ScheduleItem],
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """使用SQLAlchemy服务创建日程"""
    try:
        results = ScheduleService.create_or_update_schedule(db, user_id, schedule_data)
        
        # 转换为响应格式
        schedule_items = []
        for schedule in results:
            item = ScheduleItem(
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
        
        return ScheduleResponse(schedule_data=schedule_items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建日程失败: {str(e)}")

@app.get("/api/schedule/{schedule_date}", response_model=ScheduleResponse)
def get_schedule_integrated(
    schedule_date: str,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """使用SQLAlchemy服务获取日程"""
    try:
        schedules = ScheduleService.get_schedule_by_date(db, user_id, schedule_date)
        
        schedule_items = []
        for schedule in schedules:
            item = ScheduleItem(
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
        
        return ScheduleResponse(schedule_data=schedule_items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日程失败: {str(e)}")

@app.get("/api/projects", response_model=List[ProjectResponse])
def get_projects_integrated(
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """使用SQLAlchemy服务获取项目"""
    try:
        projects = ProjectService.get_projects_by_user(db, user_id)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目失败: {str(e)}")

@app.post("/api/projects", response_model=ProjectResponse)
def create_project_integrated(
    project: ProjectCreate,
    user_id: int = Query(..., description="用户ID"),
    db: Session = Depends(get_db)
):
    """使用SQLAlchemy服务创建项目"""
    try:
        return ProjectService.create_project(db, user_id, project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("启动SQLAlchemy集成示例服务...")
    print("访问 http://localhost:5005/docs 查看API文档")
    uvicorn.run(app, host="0.0.0.0", port=5005)
