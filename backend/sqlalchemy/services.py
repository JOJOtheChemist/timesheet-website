from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date
import models
import schemas

class ScheduleService:
    """日程服务类 - 封装日程相关的数据库操作"""
    
    @staticmethod
    def create_or_update_schedule(
        db: Session, 
        user_id: int, 
        schedule_items: List[schemas.ScheduleItem]
    ) -> List[models.DailySchedule]:
        """创建或更新日程数据"""
        results = []
        for item in schedule_items:
            if not item.schedule_date or not item.time_slot:
                continue
                
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
                for field, value in item.dict(exclude_unset=True).items():
                    if hasattr(existing, field) and value is not None:
                        setattr(existing, field, value)
                existing.updated_at = datetime.utcnow()
                results.append(existing)
            else:
                # 创建新记录
                db_schedule = models.DailySchedule(
                    user_id=user_id,
                    schedule_date=datetime.strptime(item.schedule_date, "%Y-%m-%d").date(),
                    time_slot=item.time_slot,
                    **item.dict(exclude_unset=True)
                )
                db.add(db_schedule)
                results.append(db_schedule)
        
        db.commit()
        for result in results:
            db.refresh(result)
        return results
    
    @staticmethod
    def get_schedule_by_date(
        db: Session, 
        user_id: int, 
        schedule_date: str
    ) -> List[models.DailySchedule]:
        """获取指定日期的日程数据"""
        target_date = datetime.strptime(schedule_date, "%Y-%m-%d").date()
        return db.query(models.DailySchedule).filter(
            and_(
                models.DailySchedule.user_id == user_id,
                models.DailySchedule.schedule_date == target_date
            )
        ).all()

class ProjectService:
    """项目服务类 - 封装项目相关的数据库操作"""
    
    @staticmethod
    def get_projects_by_user(db: Session, user_id: int) -> List[models.Project]:
        """获取用户的所有项目"""
        return db.query(models.Project).filter(
            models.Project.user_id == user_id
        ).all()
    
    @staticmethod
    def create_project(
        db: Session, 
        user_id: int, 
        project_data: schemas.ProjectCreate
    ) -> models.Project:
        """创建新项目"""
        # 查找或创建分类
        category_id = None
        if project_data.category_name:
            category = db.query(models.Category).filter(
                and_(
                    models.Category.user_id == user_id,
                    models.Category.name == project_data.category_name
                )
            ).first()
            if not category:
                category = models.Category(
                    user_id=user_id,
                    name=project_data.category_name,
                    color=project_data.color or "#4f9cff"
                )
                db.add(category)
                db.commit()
                db.refresh(category)
            category_id = category.id
        
        # 创建项目
        db_project = models.Project(
            user_id=user_id,
            category_id=category_id,
            name=project_data.name,
            description=project_data.description,
            color=project_data.color or "#4f9cff"
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

class SubtaskService:
    """子任务服务类 - 封装子任务相关的数据库操作"""
    
    @staticmethod
    def get_subtasks_by_user(
        db: Session, 
        user_id: int, 
        project_id: Optional[int] = None
    ) -> List[models.Subtask]:
        """获取用户的子任务列表"""
        query = db.query(models.Subtask).filter(models.Subtask.user_id == user_id)
        if project_id:
            query = query.filter(models.Subtask.project_id == project_id)
        return query.all()
    
    @staticmethod
    def create_subtask(
        db: Session, 
        user_id: int, 
        subtask_data: schemas.SubtaskCreate
    ) -> models.Subtask:
        """创建新子任务"""
        db_subtask = models.Subtask(
            user_id=user_id,
            project_id=subtask_data.project_id,
            name=subtask_data.name,
            urgency_importance=subtask_data.urgency_importance,
            difficulty=subtask_data.difficulty,
            color=subtask_data.color or "#9cc7ff"
        )
        db.add(db_subtask)
        db.commit()
        db.refresh(db_subtask)
        return db_subtask

class CategoryService:
    """分类服务类 - 封装分类相关的数据库操作"""
    
    @staticmethod
    def get_categories_by_user(db: Session, user_id: int) -> List[models.Category]:
        """获取用户的所有分类"""
        return db.query(models.Category).filter(
            models.Category.user_id == user_id
        ).all()
    
    @staticmethod
    def create_category(
        db: Session, 
        user_id: int, 
        category_data: schemas.CategoryCreate
    ) -> models.Category:
        """创建新分类"""
        db_category = models.Category(
            user_id=user_id,
            name=category_data.name,
            color=category_data.color or "#4f9cff"
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
