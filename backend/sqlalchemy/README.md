# Timesheet SQLAlchemy 模块

这是一个基于SQLAlchemy的模块化数据库操作层，用于支持Timesheet项目的schedule页面功能。

## 📁 文件结构

```
sqlalchemy/
├── main.py          # FastAPI应用主文件
├── models.py        # SQLAlchemy数据模型
├── schemas.py       # Pydantic数据验证模型
├── database.py      # 数据库连接配置
├── services.py      # 业务逻辑服务层
├── start_sqlalchemy_api.sh  # 启动脚本
├── test_api.py      # API测试脚本
└── README.md        # 说明文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn sqlalchemy pydantic
```

### 2. 启动服务

```bash
# 使用启动脚本
./start_sqlalchemy_api.sh

# 或直接运行
python main.py
```

服务将在端口5004启动。

### 3. 测试API

```bash
python test_api.py
```

## 📊 数据模型

### 核心表结构

1. **users** - 用户表
2. **categories** - 分类表
3. **projects** - 项目表
4. **subtasks** - 子任务表
5. **daily_schedule** - 日程表（核心业务表）
6. **invite_codes** - 邀请码表

### 日程表字段说明

- **计划字段**: planned_subtask_id, planned_subtask_name, planned_notes, planned_project_color
- **实际字段**: actual_subtask_id, actual_subtask_name, actual_notes, actual_project_color
- **心情字段**: mood
- **时间字段**: schedule_date, time_slot

## 🔧 API接口

### 日程相关

- `POST /api/schedule` - 创建或更新日程
- `GET /api/schedule/{date}` - 获取指定日期的日程

### 项目相关

- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建新项目

### 子任务相关

- `GET /api/subtasks` - 获取子任务列表
- `POST /api/subtasks` - 创建新子任务

### 分类相关

- `GET /api/categories` - 获取分类列表
- `POST /api/categories` - 创建新分类

## 💡 使用示例

### 创建日程数据

```python
import requests

# 日程数据
schedule_data = {
    "schedule_data": [
        {
            "schedule_date": "2025-09-13",
            "time_slot": "09:00",
            "planned_subtask_name": "写代码",
            "planned_notes": "完成用户登录功能",
            "mood": "专注"
        }
    ]
}

# 发送请求
response = requests.post(
    "http://localhost:5004/api/schedule?user_id=1",
    json=schedule_data
)
```

### 获取日程数据

```python
# 获取指定日期的日程
response = requests.get(
    "http://localhost:5004/api/schedule/2025-09-13?user_id=1"
)
```

## 🔄 与现有系统集成

### 1. 替换现有API

可以将现有的MySQL连接替换为SQLAlchemy模块：

```python
# 原来的方式
import mysql.connector

# 新的方式
from sqlalchemy.orm import Session
from database import get_db
```

### 2. 数据迁移

可以使用SQLAlchemy的迁移功能将现有数据迁移到新结构。

### 3. 服务层集成

通过services.py中的服务类，可以在现有FastAPI应用中集成：

```python
from services import ScheduleService, ProjectService

# 在路由中使用
@app.post("/api/schedule")
def create_schedule(schedule_data: List[ScheduleItem], db: Session = Depends(get_db)):
    return ScheduleService.create_or_update_schedule(db, user_id, schedule_data)
```

## ⚙️ 配置选项

### 数据库配置

在`database.py`中修改数据库连接：

```python
# SQLite (默认)
DATABASE_URL = "sqlite:///./timesheet.db"

# MySQL
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/timesheet"

# PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost:5432/timesheet"
```

### 环境变量

```bash
export DATABASE_URL="sqlite:///./timesheet.db"
```

## 🧪 测试

运行测试脚本验证所有功能：

```bash
python test_api.py
```

测试包括：
- 健康检查
- 日程CRUD操作
- 项目CRUD操作
- 子任务CRUD操作
- 分类CRUD操作

## 📝 注意事项

1. **数据一致性**: 使用事务确保数据一致性
2. **错误处理**: 所有操作都有适当的错误处理
3. **性能优化**: 使用连接池和索引优化查询性能
4. **安全性**: 所有操作都需要用户ID验证

## 🔧 开发建议

1. **模块化设计**: 每个服务类负责特定的业务逻辑
2. **数据验证**: 使用Pydantic进行数据验证
3. **错误处理**: 统一的错误处理机制
4. **日志记录**: 添加适当的日志记录
5. **单元测试**: 为每个服务类编写单元测试
