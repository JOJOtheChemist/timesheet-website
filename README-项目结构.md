# 项目目录结构

## 整体架构
这是一个前后端分离的日程表应用，采用组件化设计。

## 目录结构
```
timesheet/
├── backend/                    # 后端服务
│   ├── fastapi_schedule_api.py # FastAPI主应用 (MySQL)
│   ├── requirements.txt       # Python依赖
│   ├── start_api.sh          # 启动脚本
│   ├── deploy.sh             # 部署脚本
│   ├── schedule-api.service   # systemd服务配置
│   ├── timesheet.service      # 服务配置
│   ├── api.log               # API日志
│   └── README.md             # 后端说明文档
│
├── components/                 # 前端组件
│   └── background-switcher/   # 背景切换器组件
│       ├── background-switcher.css
│       ├── background-switcher.js
│       ├── README.md
│       └── README-背景切换器.md
│
├── static/                     # 静态资源
│   └── images/                # 图片资源
│
├── daily_schedule.html         # 主页面
├── nginx.conf                  # Nginx配置
├── timesheet.conf              # 配置文件
├── timesheet.db                # 数据库文件 (已移至backend/)
├── venv/                       # Python虚拟环境
└── README.md                   # 项目主说明
```

## 技术栈

### 后端
- **FastAPI** - 现代Python Web框架
- **MySQL** - 关系型数据库
- **systemd** - 系统服务管理

### 前端
- **HTML5 + CSS3** - 页面结构和样式
- **JavaScript** - 交互逻辑
- **组件化设计** - 模块化前端架构

### 部署
- **Nginx** - 反向代理和静态文件服务
- **systemd** - 服务管理
- **Shell脚本** - 自动化部署

## 快速开始

### 1. 启动后端
```bash
cd backend
./start_api.sh
```

### 2. 访问应用
- 主页面: http://localhost
- API文档: http://localhost:5001/docs

### 3. 部署
```bash
cd backend
./deploy.sh
```

## 开发说明
- 前端组件放在 `components/` 目录
- 后端服务放在 `backend/` 目录
- 静态资源放在 `static/` 目录
- 配置文件放在项目根目录 