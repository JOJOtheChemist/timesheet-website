"""
SQLAlchemy批量操作管理器
用于优化timesheet数据存储性能，减少数据库请求次数
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from contextlib import asynccontextmanager
import threading
import time
from collections import defaultdict
import logging

# SQLAlchemy imports
from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mysql import insert

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = "mysql+pymysql://root:12356790zZ_@localhost/project_tasks?charset=utf8mb4"

Base = declarative_base()

class DailySchedule(Base):
    """日程安排数据模型"""
    __tablename__ = 'daily_schedule'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    schedule_date = Column(Date, nullable=False)
    time_slot = Column(String(10), nullable=False)
    planned_subtask_id = Column(Integer, ForeignKey('subtasks.id'))
    planned_subtask_name = Column(String(255))
    planned_notes = Column(Text)
    planned_project_color = Column(String(20))
    actual_subtask_id = Column(Integer, ForeignKey('subtasks.id'))
    actual_subtask_name = Column(String(255))
    actual_notes = Column(Text)
    actual_project_color = Column(String(20))
    mood = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@dataclass
class TaskBufferItem:
    """任务缓冲项"""
    user_id: int
    schedule_date: str
    time_slot: str
    task_type: str  # 'planned' or 'actual'
    subtask_id: Optional[int] = None
    subtask_name: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None
    notes: Optional[str] = None
    mood: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class BatchSaveManager:
    """批量保存管理器"""
    
    def __init__(self, batch_size: int = 50, flush_interval: float = 0.5):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        # 缓冲区
        self.task_buffer: List[TaskBufferItem] = []
        self.buffer_lock = threading.Lock()
        
        # SQLAlchemy引擎和会话
        self.engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=30)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # 定时刷新任务
        self._flush_timer = None
        self._running = False
        
        # 启动管理器
        self.start()
    
    def start(self):
        """启动批量保存管理器"""
        self._running = True
        self._schedule_flush()
        logger.info("批量保存管理器已启动")
    
    def stop(self):
        """停止批量保存管理器"""
        self._running = False
        if self._flush_timer:
            self._flush_timer.cancel()
        # 强制刷新剩余数据
        self.flush_buffer()
        logger.info("批量保存管理器已停止")
    
    def _schedule_flush(self):
        """安排下一次刷新"""
        if self._running:
            self._flush_timer = threading.Timer(self.flush_interval, self.flush_buffer)
            self._flush_timer.daemon = True
            self._flush_timer.start()
    
    def add_task(self, task_data: TaskBufferItem) -> bool:
        """添加任务到缓冲区"""
        try:
            with self.buffer_lock:
                self.task_buffer.append(task_data)
                
                # 如果达到批量大小，立即刷新
                if len(self.task_buffer) >= self.batch_size:
                    self._flush_immediately()
                    return True
                
                logger.debug(f"任务已添加到缓冲区，当前缓冲区大小: {len(self.task_buffer)}")
                return True
                
        except Exception as e:
            logger.error(f"添加任务到缓冲区失败: {e}")
            return False
    
    def _flush_immediately(self):
        """立即刷新缓冲区"""
        try:
            self.flush_buffer()
        except Exception as e:
            logger.error(f"立即刷新缓冲区失败: {e}")
    
    def flush_buffer(self):
        """刷新缓冲区到数据库"""
        if not self.task_buffer:
            return
        
        try:
            with self.buffer_lock:
                if not self.task_buffer:
                    return
                    
                tasks_to_flush = self.task_buffer.copy()
                self.task_buffer.clear()
            
            # 批量保存到数据库
            self._batch_save_to_db(tasks_to_flush)
            logger.info(f"批量保存 {len(tasks_to_flush)} 个任务完成")
            
        except Exception as e:
            logger.error(f"刷新缓冲区失败: {e}")
            # 重新放入缓冲区
            with self.buffer_lock:
                self.task_buffer.extend(tasks_to_flush)
        finally:
            if self._running:
                self._schedule_flush()
    
    def _batch_save_to_db(self, tasks: List[TaskBufferItem]):
        """批量保存任务到数据库"""
        session = self.SessionLocal()
        try:
            # 按用户和日期分组
            grouped_tasks = defaultdict(list)
            for task in tasks:
                key = (task.user_id, task.schedule_date, task.time_slot)
                grouped_tasks[key].append(task)
            
            # 批量更新或插入
            for (user_id, schedule_date, time_slot), task_list in grouped_tasks.items():
                # 合并同一时间槽的任务
                planned_task = None
                actual_task = None
                
                for task in task_list:
                    if task.task_type == 'planned':
                        planned_task = task
                    elif task.task_type == 'actual':
                        actual_task = task
                
                # 构建更新数据
                update_data = {
                    'user_id': user_id,
                    'schedule_date': datetime.strptime(schedule_date, '%Y-%m-%d').date(),
                    'time_slot': time_slot,
                    'updated_at': datetime.utcnow()
                }
                
                if planned_task:
                    update_data.update({
                        'planned_subtask_id': planned_task.subtask_id,
                        'planned_subtask_name': planned_task.subtask_name,
                        'planned_notes': planned_task.notes,
                        'planned_project_color': planned_task.project_color,
                    })
                
                if actual_task:
                    update_data.update({
                        'actual_subtask_id': actual_task.subtask_id,
                        'actual_subtask_name': actual_task.subtask_name,
                        'actual_notes': actual_task.notes,
                        'actual_project_color': actual_task.project_color,
                        'mood': actual_task.mood,
                    })
                
                # 使用ON DUPLICATE KEY UPDATE进行批量插入或更新
                stmt = insert(DailySchedule).values(update_data)
                update_stmt = stmt.on_duplicate_key_update(
                    planned_subtask_id=stmt.inserted.planned_subtask_id,
                    planned_subtask_name=stmt.inserted.planned_subtask_name,
                    planned_notes=stmt.inserted.planned_notes,
                    planned_project_color=stmt.inserted.planned_project_color,
                    actual_subtask_id=stmt.inserted.actual_subtask_id,
                    actual_subtask_name=stmt.inserted.actual_subtask_name,
                    actual_notes=stmt.inserted.actual_notes,
                    actual_project_color=stmt.inserted.actual_project_color,
                    mood=stmt.inserted.mood,
                    updated_at=stmt.inserted.updated_at
                )
                
                session.execute(update_stmt)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"批量保存到数据库失败: {e}")
            raise
        finally:
            session.close()

# 全局批量保存管理器实例
batch_manager = None

def get_batch_manager() -> BatchSaveManager:
    """获取批量保存管理器实例"""
    global batch_manager
    if batch_manager is None:
        batch_manager = BatchSaveManager(batch_size=50, flush_interval=0.5)
    return batch_manager

def save_task_immediately(
    user_id: int,
    schedule_date: str,
    time_slot: str,
    task_type: str,
    subtask_id: Optional[int] = None,
    subtask_name: Optional[str] = None,
    project_name: Optional[str] = None,
    project_color: Optional[str] = None,
    notes: Optional[str] = None,
    mood: Optional[str] = None
) -> bool:
    """立即保存任务到缓冲区"""
    try:
        batch_manager = get_batch_manager()
        task_data = TaskBufferItem(
            user_id=user_id,
            schedule_date=schedule_date,
            time_slot=time_slot,
            task_type=task_type,
            subtask_id=subtask_id,
            subtask_name=subtask_name,
            project_name=project_name,
            project_color=project_color,
            notes=notes,
            mood=mood
        )
        
        return batch_manager.add_task(task_data)
        
    except Exception as e:
        logger.error(f"保存任务失败: {e}")
        return False

# 上下文管理器用于启动和停止批量管理器
@asynccontextmanager
async def lifespan_manager():
    """批量管理器生命周期管理器"""
    manager = get_batch_manager()
    try:
        yield manager
    finally:
        manager.stop()

# FastAPI集成函数
async def init_batch_manager():
    """初始化批量管理器"""
    get_batch_manager()
    logger.info("批量管理器初始化完成")

async def shutdown_batch_manager():
    """关闭批量管理器"""
    global batch_manager
    if batch_manager:
        batch_manager.stop()
        batch_manager = None
    logger.info("批量管理器已关闭")