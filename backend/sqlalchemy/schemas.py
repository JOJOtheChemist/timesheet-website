from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List

# 用户相关Schema
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

# 日程相关Schema
class ScheduleItem(BaseModel):
    id: Optional[int] = None
    schedule_date: Optional[str] = None
    time_slot: Optional[str] = None
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

# 编辑器相关Schema
class EditorRow(BaseModel):
    project_name: Optional[str] = None
    subtask_name: Optional[str] = None
    category_name: Optional[str] = None
    urgency_importance: Optional[str] = None
    difficulty: Optional[str] = None
    category_id: Optional[int] = None
    project_id: Optional[int] = None
    subtask_id: Optional[int] = None

# 项目相关Schema
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_name: Optional[str] = None
    color: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    color: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 子任务相关Schema
class SubtaskCreate(BaseModel):
    name: str
    project_id: int
    urgency_importance: Optional[str] = "重要不紧急"
    difficulty: Optional[str] = "中级"
    color: Optional[str] = None

class SubtaskResponse(BaseModel):
    id: int
    name: str
    project_id: int
    urgency_importance: str
    difficulty: str
    color: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 分类相关Schema
class CategoryCreate(BaseModel):
    name: str
    color: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 批量操作Schema
class BulkScheduleItem(BaseModel):
    schedule_date: str
    time_slot: str
    planned_subtask_id: Optional[int] = None
    planned_subtask_name: Optional[str] = None
    planned_notes: Optional[str] = None
    planned_project_color: Optional[str] = None
    actual_subtask_id: Optional[int] = None
    actual_subtask_name: Optional[str] = None
    actual_notes: Optional[str] = None
    actual_project_color: Optional[str] = None
    mood: Optional[str] = None

class BulkSchedulePayload(BaseModel):
    items: List[BulkScheduleItem]

# Agent相关Schema
class AgentChatRequest(BaseModel):
    message: str

class AgentChatResponse(BaseModel):
    reply: str
    parsed: dict
    category_id: Optional[int] = None
    project_id: Optional[int] = None
    subtask_id: Optional[int] = None
    thought: Optional[str] = None
    tasks: Optional[List[dict]] = None
