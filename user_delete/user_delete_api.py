"""
用户删除API端点 - 集成到FastAPI中
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import mysql.connector
from backend.fastapi_schedule_api import get_db, get_current_user

router = APIRouter()

class UserDeleteRequest(BaseModel):
    user_identifier: str  # 用户名或用户ID
    force: bool = False   # 是否强制删除

class UserDeleteResponse(BaseModel):
    message: str
    deleted_counts: Dict[str, int]
    user_info: Dict[str, Any]

def get_user_info(user_identifier: str, db: mysql.connector.MySQLConnection) -> Optional[Dict[str, Any]]:
    """根据用户名或ID获取用户信息"""
    cursor = db.cursor(dictionary=True)
    try:
        if user_identifier.isdigit():
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = %s", (int(user_identifier),))
        else:
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE username = %s", (user_identifier,))
        return cursor.fetchone()
    finally:
        cursor.close()

def get_user_related_data_count(user_id: int, db: mysql.connector.MySQLConnection) -> Dict[str, int]:
    """获取用户相关数据统计"""
    cursor = db.cursor()
    try:
        counts = {}
        
        # 用户画像
        cursor.execute("SELECT COUNT(*) FROM user_profiles WHERE user_id = %s", (user_id,))
        counts['user_profiles'] = cursor.fetchone()[0]
        
        # 项目
        cursor.execute("SELECT COUNT(*) FROM projects WHERE user_id = %s", (user_id,))
        counts['projects'] = cursor.fetchone()[0]
        
        # 子任务
        cursor.execute("SELECT COUNT(*) FROM subtasks WHERE user_id = %s", (user_id,))
        counts['subtasks'] = cursor.fetchone()[0]
        
        # 日程安排
        cursor.execute("SELECT COUNT(*) FROM daily_schedule WHERE user_id = %s", (user_id,))
        counts['daily_schedule'] = cursor.fetchone()[0]
        
        # 邀请码使用记录
        cursor.execute("SELECT COUNT(*) FROM invite_codes WHERE used_by = %s", (user_id,))
        counts['invite_codes'] = cursor.fetchone()[0]
        
        return counts
    finally:
        cursor.close()

def delete_user_data(user_id: int, db: mysql.connector.MySQLConnection) -> Dict[str, int]:
    """删除用户的所有相关数据"""
    cursor = db.cursor()
    
    try:
        deleted_counts = {
            'subtasks': 0,
            'projects': 0,
            'daily_schedule': 0,
            'user_profiles': 0,
            'invite_codes_reset': 0,
            'users': 0
        }
        
        # 开始事务
        db.start_transaction()
        
        # 1. 删除子任务（有外键约束，需要先删除）
        cursor.execute("DELETE FROM subtasks WHERE user_id = %s", (user_id,))
        deleted_counts['subtasks'] = cursor.rowcount
        
        # 2. 删除项目
        cursor.execute("DELETE FROM projects WHERE user_id = %s", (user_id,))
        deleted_counts['projects'] = cursor.rowcount
        
        # 3. 删除日程安排
        cursor.execute("DELETE FROM daily_schedule WHERE user_id = %s", (user_id,))
        deleted_counts['daily_schedule'] = cursor.rowcount
        
        # 4. 删除用户画像
        cursor.execute("DELETE FROM user_profiles WHERE user_id = %s", (user_id,))
        deleted_counts['user_profiles'] = cursor.rowcount
        
        # 5. 重置邀请码使用记录
        cursor.execute("UPDATE invite_codes SET used_by = NULL, used_at = NULL WHERE used_by = %s", (user_id,))
        deleted_counts['invite_codes_reset'] = cursor.rowcount
        
        # 6. 最后删除用户
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        deleted_counts['users'] = cursor.rowcount
        
        # 提交事务
        db.commit()
        
        return deleted_counts
        
    except Exception as e:
        # 回滚事务
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除用户数据失败: {str(e)}")
    finally:
        cursor.close()

@router.delete("/api/admin/delete-user", response_model=UserDeleteResponse)
async def delete_user(
    request: UserDeleteRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    db: mysql.connector.MySQLConnection = Depends(get_db)
):
    """删除用户及其所有相关数据"""
    
    # 检查权限（这里可以添加管理员权限检查）
    if not current_user:
        raise HTTPException(status_code=401, detail="未认证")
    
    # 获取用户信息
    user = get_user_info(request.user_identifier, db)
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 '{request.user_identifier}' 不存在")
    
    # 获取相关数据统计
    related_counts = get_user_related_data_count(user['id'], db)
    
    # 检查是否有数据需要删除
    total_related_data = sum(related_counts.values())
    if total_related_data == 0:
        raise HTTPException(status_code=400, detail="用户没有相关数据需要删除")
    
    # 执行删除
    try:
        deleted_counts = delete_user_data(user['id'], db)
        
        return UserDeleteResponse(
            message=f"用户 '{user['username']}' 及其所有相关数据已删除",
            deleted_counts=deleted_counts,
            user_info=user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

@router.get("/api/admin/user-info/{user_identifier}")
async def get_user_info_endpoint(
    user_identifier: str,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user),
    db: mysql.connector.MySQLConnection = Depends(get_db)
):
    """获取用户信息及其相关数据统计"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="未认证")
    
    # 获取用户信息
    user = get_user_info(user_identifier, db)
    if not user:
        raise HTTPException(status_code=404, detail=f"用户 '{user_identifier}' 不存在")
    
    # 获取相关数据统计
    related_counts = get_user_related_data_count(user['id'], db)
    
    return {
        "user_info": user,
        "related_data_counts": related_counts,
        "total_related_data": sum(related_counts.values())
    }
