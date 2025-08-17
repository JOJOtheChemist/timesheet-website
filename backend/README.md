# 后端服务

## 功能描述
这是日程表应用的后端服务，基于FastAPI构建，提供RESTful API接口。

## 文件结构
- `fastapi_schedule_api.py` - 主要的FastAPI应用 (MySQL数据库)
- `requirements.txt` - Python依赖包
- `start_api.sh` - 启动脚本
- `deploy.sh` - 部署脚本
- `schedule-api.service` - systemd服务配置
- `timesheet.service` - 服务配置
- `api.log` - API访问日志

## 快速开始

### 1. 安装依赖
```bash
cd backend
source ../venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动服务
```bash
./start_api.sh
```

### 3. 访问API
- API地址: http://localhost:5001
- API文档: http://localhost:5001/docs
- OpenAPI规范: http://localhost:5001/openapi.json

## 部署

### 使用部署脚本
```bash
./deploy.sh
```

### 手动部署
1. 安装systemd服务
2. 配置nginx反向代理
3. 启动服务

## 服务管理

### systemd服务
```bash
# 启动服务
sudo systemctl start schedule-api.service

# 停止服务
sudo systemctl stop schedule-api.service

# 查看状态
sudo systemctl status schedule-api.service

# 查看日志
sudo journalctl -u schedule-api.service -f
```

## 配置说明
- 服务端口: 5001
- 数据库: SQLite (timesheet.db)
- 日志: api.log
- 虚拟环境: ../venv/ 