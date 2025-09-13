"""
批量操作API端点
支持计划任务和实际任务的批量保存
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import asyncio
import json
import logging
from datetime import datetime

# 导入认证依赖（从主文件复制）
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from passlib.context import CryptContext

# JWT配置
JWT_SECRET = "change_this_secret_in_env"
JWT_ALGORITHM = "HS256"
http_bearer = HTTPBearer(auto_error=False)

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

# 导入批量管理器
from batch_manager import save_task_immediately, get_batch_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class BatchTaskItem(BaseModel):
    """批量任务项"""
    schedule_date: str
    time_slot: str
    task_type: str  # 'planned' or 'actual'
    subtask_id: Optional[int] = None
    subtask_name: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None
    notes: Optional[str] = None
    mood: Optional[str] = None

class BatchSaveRequest(BaseModel):
    """批量保存请求"""
    tasks: List[BatchTaskItem]

class RapidTaskRequest(BaseModel):
    """快速任务请求 - 低延迟保存"""
    schedule_date: str
    time_slot: str
    task_type: str
    subtask_id: Optional[int] = None
    subtask_name: Optional[str] = None
    project_name: Optional[str] = None
    project_color: Optional[str] = None
    notes: Optional[str] = None
    mood: Optional[str] = None

@router.post("/api/batch/save")
async def batch_save_tasks(
    request: BatchSaveRequest,
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    批量保存任务
    支持计划任务和实际任务的批量操作
    """
    try:
        user_id = current_user["sub"]
        batch_manager = get_batch_manager()
        
        success_count = 0
        failed_tasks = []
        
        for task in request.tasks:
            try:
                result = save_task_immediately(
                    user_id=user_id,
                    schedule_date=task.schedule_date,
                    time_slot=task.time_slot,
                    task_type=task.task_type,
                    subtask_id=task.subtask_id,
                    subtask_name=task.subtask_name,
                    project_name=task.project_name,
                    project_color=task.project_color,
                    notes=task.notes,
                    mood=task.mood
                )
                
                if result:
                    success_count += 1
                else:
                    failed_tasks.append({
                        "time_slot": task.time_slot,
                        "task_type": task.task_type,
                        "error": "保存失败"
                    })
                    
            except Exception as e:
                failed_tasks.append({
                    "time_slot": task.time_slot,
                    "task_type": task.task_type,
                    "error": str(e)
                })
        
        return {
            "message": "批量保存处理完成",
            "total_tasks": len(request.tasks),
            "success_count": success_count,
            "failed_count": len(failed_tasks),
            "failed_tasks": failed_tasks,
            "batch_info": {
                "buffer_size": len(batch_manager.task_buffer),
                "batch_size": batch_manager.batch_size,
                "flush_interval": batch_manager.flush_interval
            }
        }
        
    except Exception as e:
        logger.error(f"批量保存失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量保存失败: {str(e)}")

@router.post("/api/rapid/save")
async def rapid_save_task(
    request: RapidTaskRequest,
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    快速保存任务 - 低延迟响应
    用户输入后立即响应，实际保存由批量管理器异步处理
    """
    try:
        user_id = current_user["sub"]
        
        # 立即添加到缓冲区（低延迟）
        result = save_task_immediately(
            user_id=user_id,
            schedule_date=request.schedule_date,
            time_slot=request.time_slot,
            task_type=request.task_type,
            subtask_id=request.subtask_id,
            subtask_name=request.subtask_name,
            project_name=request.project_name,
            project_color=request.project_color,
            notes=request.notes,
            mood=request.mood
        )
        
        if result:
            return {
                "message": "任务已加入保存队列",
                "status": "queued",
                "task_type": request.task_type,
                "time_slot": request.time_slot,
                "queued_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="任务保存失败")
            
    except Exception as e:
        logger.error(f"快速保存失败: {e}")
        raise HTTPException(status_code=500, detail=f"快速保存失败: {str(e)}")

@router.post("/api/planned-task/rapid")
async def save_planned_task_rapid(
    schedule_date: str,
    time_slot: str,
    subtask_id: Optional[int] = None,
    subtask_name: Optional[str] = None,
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    project_color: Optional[str] = None,
    notes: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    快速保存计划任务
    专门为计划任务优化的端点
    """
    try:
        user_id = current_user["sub"]
        
        result = save_task_immediately(
            user_id=user_id,
            schedule_date=schedule_date,
            time_slot=time_slot,
            task_type="planned",
            subtask_id=subtask_id,
            subtask_name=subtask_name,
            project_name=project_name,
            project_color=project_color,
            notes=notes
        )
        
        if result:
            return {
                "message": "计划任务已保存",
                "status": "queued",
                "time_slot": time_slot,
                "queued_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="计划任务保存失败")
            
    except Exception as e:
        logger.error(f"计划任务快速保存失败: {e}")
        raise HTTPException(status_code=500, detail=f"计划任务保存失败: {str(e)}")

@router.post("/api/actual-task/rapid")
async def save_actual_task_rapid(
    schedule_date: str,
    time_slot: str,
    subtask_id: Optional[int] = None,
    subtask_name: Optional[str] = None,
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    project_color: Optional[str] = None,
    notes: Optional[str] = None,
    mood: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    快速保存实际任务
    专门为实际任务优化的端点
    """
    try:
        user_id = current_user["sub"]
        
        result = save_task_immediately(
            user_id=user_id,
            schedule_date=schedule_date,
            time_slot=time_slot,
            task_type="actual",
            subtask_id=subtask_id,
            subtask_name=subtask_name,
            project_name=project_name,
            project_color=project_color,
            notes=notes,
            mood=mood
        )
        
        if result:
            return {
                "message": "实际任务已保存",
                "status": "queued",
                "time_slot": time_slot,
                "queued_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="实际任务保存失败")
            
    except Exception as e:
        logger.error(f"实际任务快速保存失败: {e}")
        raise HTTPException(status_code=500, detail=f"实际任务保存失败: {str(e)}")

@router.get("/api/batch/status")
async def get_batch_status(
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    获取批量管理器状态
    """
    try:
        batch_manager = get_batch_manager()
        
        return {
            "status": "active",
            "buffer_size": len(batch_manager.task_buffer),
            "batch_size": batch_manager.batch_size,
            "flush_interval": batch_manager.flush_interval,
            "is_running": batch_manager._running,
            "next_flush_in": "定时器运行中"
        }
        
    except Exception as e:
        logger.error(f"获取批量状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@router.post("/api/batch/flush")
async def manual_flush_batch(
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    手动刷新批量缓冲区
    """
    try:
        batch_manager = get_batch_manager()
        buffer_size_before = len(batch_manager.task_buffer)
        
        batch_manager.flush_buffer()
        
        return {
            "message": "批量缓冲区已手动刷新",
            "flushed_tasks": buffer_size_before,
            "current_buffer_size": len(batch_manager.task_buffer)
        }
        
    except Exception as e:
        logger.error(f"手动刷新失败: {e}")
        raise HTTPException(status_code=500, detail=f"手动刷新失败: {str(e)}")

# 模拟快速随机输入的测试端点
@router.post("/api/test/rapid-input")
async def test_rapid_input(
    task_count: int = 20,
    delay_seconds: float = 0.1,
    current_user: Dict[str, Any] = Depends(require_user)
) -> Dict[str, Any]:
    """
    测试快速随机输入功能
    模拟用户快速输入随机分布的计划和实际任务
    """
    try:
        user_id = current_user["sub"]
        from datetime import datetime, timedelta
        import random
        
        # 生成测试数据
        time_slots = [f"{i:02d}:00" for i in range(8, 20)]  # 8:00 到 19:00
        test_date = datetime.now().strftime('%Y-%m-%d')
        
        success_count = 0
        failed_count = 0
        
        async def save_single_task():
            nonlocal success_count, failed_count
            
            try:
                # 随机选择任务类型
                task_type = random.choice(['planned', 'actual'])
                # 随机选择时间槽
                time_slot = random.choice(time_slots)
                
                # 模拟任务数据
                result = save_task_immediately(
                    user_id=user_id,
                    schedule_date=test_date,
                    time_slot=time_slot,
                    task_type=task_type,
                    subtask_id=random.randint(1, 100),
                    subtask_name=f"测试任务_{random.randint(1, 1000)}",
                    project_name=f"测试项目_{random.randint(1, 50)}",
                    project_color=f"#{random.randint(0, 0xFFFFFF):06x}",
                    notes=f"测试备注_{random.randint(1, 100)}"
                )
                
                if result:
                    success_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"测试任务保存失败: {e}")
        
        # 批量并发保存
        tasks = []
        for i in range(task_count):
            task = asyncio.create_task(save_single_task())
            tasks.append(task)
            
            # 添加延迟模拟真实输入
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
        
        # 等待所有任务完成
        await asyncio.gather(*tasks)
        
        return {
            "message": "快速输入测试完成",
            "total_tasks": task_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": f"{(success_count/task_count)*100:.1f}%",
            "test_date": test_date,
            "delay_per_task": delay_seconds
        }
        
    except Exception as e:
        logger.error(f"快速输入测试失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")