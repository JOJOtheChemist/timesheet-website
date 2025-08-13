# Timesheet Management System

一个基于FastAPI的日程管理系统，支持项目分类、子任务管理和日程安排。

## 功能特性

- 📅 日程管理：按时间段安排任务
- 📋 项目管理：分类管理项目
- 🎯 子任务管理：详细的任务分解
- 🔍 智能筛选：按紧急性、困难程度等筛选
- 📝 备注系统：为每个时间段添加备注
- 🎨 颜色编码：项目颜色区分

## 系统架构

- **前端**: HTML + JavaScript + Tailwind CSS
- **后端**: FastAPI (Python)
- **数据库**: SQLite
- **Web服务器**: Nginx
- **进程管理**: Systemd

## 快速开始

### 1. 环境要求

- Ubuntu 18.04+ / CentOS 7+
- Python 3.8+
- Nginx
- Systemd

### 2. 安装部署

```bash
# 克隆或下载项目到服务器
cd /home/ubuntu/timesheet

# 运行部署脚本
chmod +x deploy.sh
./deploy.sh
```

### 3. 访问系统

- 主页面: http://localhost
- API文档: http://localhost/docs
- 健康检查: http://localhost/health

## 项目结构

```
timesheet/
├── main.py                 # FastAPI主程序
├── daily_schedule.html     # 前端页面
├── requirements.txt        # Python依赖
├── nginx.conf             # Nginx配置
├── timesheet.service      # Systemd服务配置
├── deploy.sh              # 部署脚本
├── static/                # 静态文件目录
└── timesheet.db           # SQLite数据库（自动创建）
```

## API接口

### 日程管理
- `GET /api/schedule/{date}` - 获取指定日期的日程
- `POST /api/schedule` - 创建新日程
- `PUT /api/schedule/{id}` - 更新日程

### 项目管理
- `GET /api/projects` - 获取项目列表（按分类组织）

## 服务管理

```bash
# 启动服务
sudo systemctl start timesheet.service

# 停止服务
sudo systemctl stop timesheet.service

# 重启服务
sudo systemctl restart timesheet.service

# 查看状态
sudo systemctl status timesheet.service

# 查看日志
sudo journalctl -u timesheet.service -f

# 开机自启
sudo systemctl enable timesheet.service
```

## 数据库结构

### schedules 表
- id: 主键
- schedule_date: 日期
- time_slot: 时间段
- subtask_id: 子任务ID
- notes: 备注
- created_at: 创建时间
- updated_at: 更新时间

### categories 表
- id: 主键
- name: 分类名称
- color: 分类颜色

### projects 表
- id: 主键
- name: 项目名称
- color: 项目颜色
- category_id: 分类ID

### subtasks 表
- id: 主键
- name: 子任务名称
- project_id: 项目ID
- urgency_importance: 紧急性重要性
- difficulty: 困难程度
- difficulty_class: CSS样式类

## 故障排除

### 1. 服务无法启动
```bash
# 检查日志
sudo journalctl -u timesheet.service -f

# 检查端口占用
sudo netstat -tlnp | grep :8000
```

### 2. Nginx配置错误
```bash
# 测试配置
sudo nginx -t

# 检查错误日志
sudo tail -f /var/log/nginx/error.log
```

### 3. 数据库问题
```bash
# 检查数据库文件权限
ls -la timesheet.db

# 重新初始化数据库（会丢失数据）
rm timesheet.db
sudo systemctl restart timesheet.service
```

## 开发说明

### 本地开发
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行开发服务器
python main.py
```

### 添加新功能
1. 在 `main.py` 中添加新的API路由
2. 在前端HTML中添加相应的JavaScript代码
3. 更新数据库结构（如需要）
4. 测试功能并部署

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！ 