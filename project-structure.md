# Timesheet 项目结构总结

## 📁 当前项目结构

```
timesheet/
├── 📁 backend/                          # 后端API服务
│   ├── fastapi_schedule_api.py         # 主API服务 (端口5001)
│   ├── batch_api.py                    # 批量操作API
│   ├── batch_manager.py                # 批量管理器
│   ├── start_api.sh                    # API启动脚本
│   ├── deploy.sh                       # 部署脚本
│   ├── login.html                      # 后端登录页面
│   ├── simple_login_test.html          # 简单登录测试
│   ├── test_login.html                 # 登录测试页面
│   └── README.md                       # 后端文档
│
├── 📁 components/                       # 前端组件库
│   ├── 📁 auth-modal/                  # 认证模态框组件
│   │   └── auth-modal.js               # 认证模态框逻辑
│   └── 📁 background-switcher/         # 背景切换器组件
│       ├── background-switcher.css     # 背景切换器样式
│       ├── background-switcher.js      # 背景切换器逻辑
│       ├── README.md                   # 组件文档
│       └── README-背景切换器.md        # 中文文档
│
├── 📁 mcp_schedule_api/                # MCP智能日程API
│   ├── mcp_schedule_server.py         # MCP服务器主程序
│   ├── mcp_http_server.py             # HTTP服务器
│   ├── mcp_client_example.py          # MCP客户端示例
│   ├── ai_integration_example.py      # AI集成示例
│   ├── demo_interactive.py            # 交互式演示
│   ├── zhipuai_demo.py                # 智谱AI演示
│   ├── test_mcp_client.py             # MCP客户端测试
│   ├── test_zhipuai.py                # 智谱AI测试
│   ├── mcp_config.json                # MCP配置
│   ├── zhipuai_config.json            # 智谱AI配置
│   ├── start_mcp_server.sh            # MCP服务器启动脚本
│   ├── start_zhipuai_demo.sh          # 智谱AI演示启动脚本
│   ├── install.sh                     # 安装脚本
│   ├── README.md                       # MCP API文档
│   ├── AI_INTEGRATION_GUIDE.md        # AI集成指南
│   ├── MCP_CONVERSION_SUMMARY.md      # MCP转换总结
│   ├── MCP_TEST_REPORT.md             # MCP测试报告
│   └── ZHIPUAI_README.md              # 智谱AI文档
│
├── 📁 mcp_web_interface/               # MCP Web界面 (端口5002)
│   ├── app.py                         # Flask应用主程序
│   ├── nginx.conf                     # Nginx配置
│   ├── nginx_mcp_addition.conf        # Nginx MCP附加配置
│   ├── start_web_server.sh            # Web服务器启动脚本
│   ├── start_schedule_manager.sh      # 日程管理器启动脚本
│   ├── README.md                      # Web界面文档
│   ├── 📁 static/                     # 静态资源
│   │   ├── 📁 css/
│   │   │   └── style.css              # 样式文件
│   │   ├── 📁 js/
│   │   │   ├── main.js                # 主JavaScript文件
│   │   │   ├── mcp-client.js          # MCP客户端
│   │   │   └── ui-manager.js          # UI管理器
│   │   └── 📁 images/                 # 图片资源
│   └── 📁 templates/                  # HTML模板
│       ├── index.html                 # 主页模板
│       └── schedule_assistant.html    # 日程助手模板
│
├── 📁 schedule_assistant/              # 日程助手
│   ├── assistant.py                   # 助手主程序
│   └── README.md                      # 助手文档
│
├── 📁 static/                         # 静态资源目录
│   └── 📁 images/                     # 图片资源
│       ├── 📁 easyhard/               # 难易度图片
│       ├── 📁 style1/                 # 风格1图片
│       ├── 📁 svg/                    # SVG图标
│       ├── 📁 学习表情包/              # 学习表情包
│       ├── 📁 背景图2/                # 背景图片2
│       └── 📁 蕨类/                   # 蕨类图片
│
├── 📁 .claude/                        # Claude配置
│   └── 📁 agents/
│       └── schedule-manager.md        # 日程管理器配置
│
├── 📄 核心页面文件
│   ├── daily_schedule.html            # 日程表主页面
│   ├── edit_subtasks.html             # 编辑子任务页面
│   ├── login.html                     # 登录页面
│   └── onboarding.html                # 引导页面
│
├── 📄 配置文件
│   ├── nginx.conf                     # Nginx配置
│   ├── timesheet.conf                 # 项目配置
│   └── .gitignore                     # Git忽略文件
│
├── 📄 数据库文件
│   └── timesheet.db                   # SQLite数据库
│
├── 📄 脚本文件
│   ├── start_api_with_agent.sh        # 带Agent的API启动脚本
│   └── cache-manager.js               # 缓存管理器
│
├── 📄 文档文件
│   ├── README.md                      # 项目说明
│   ├── README-项目结构.md              # 项目结构说明
│   ├── project-structure.md           # 项目结构文档
│   └── MCP_QUICK_START.md            # MCP快速开始指南
│
└── 📄 日志文件
    ├── api.log                        # API日志
    └── nohup.out                      # 后台运行日志
```

## 🎯 端口分配

| 端口 | 服务 | 说明 |
|------|------|------|
| 5001 | FastAPI Schedule API | 主API服务，处理用户认证、日程管理、任务管理等 |
| 5002 | MCP Web Interface | MCP智能日程助手Web界面 |
| 5003 | 未使用 | 预留的中间件端口 |

## 🔧 核心功能模块

### 1. 后端API (端口5001)
- **主服务**: `backend/fastapi_schedule_api.py`
- **功能**: 用户认证、日程管理、任务管理、项目管理
- **数据库**: SQLite (`timesheet.db`)

### 2. MCP智能助手 (端口5002)
- **Web界面**: `mcp_web_interface/`
- **API服务**: `mcp_schedule_api/`
- **功能**: 智能日程规划、AI对话、任务建议

### 3. 前端页面
- **日程表**: `daily_schedule.html` - 主要工作界面
- **任务编辑**: `edit_subtasks.html` - 子任务管理
- **用户认证**: `login.html` - 登录页面
- **用户引导**: `onboarding.html` - 新用户引导

### 4. 组件系统
- **认证组件**: `components/auth-modal/`
- **背景切换**: `components/background-switcher/`
- **缓存管理**: `cache-manager.js`

## 🚀 快速启动

### 启动主API服务
```bash
cd /home/ubuntu/timesheet
./start_api_with_agent.sh
```

### 启动MCP Web界面
```bash
cd /home/ubuntu/timesheet/mcp_web_interface
./start_web_server.sh
```

### 启动MCP API服务
```bash
cd /home/ubuntu/timesheet/mcp_schedule_api
./start_mcp_server.sh
```

## 📋 项目特点

1. **模块化设计**: 前后端分离，组件化开发
2. **多端口架构**: 不同服务运行在不同端口
3. **AI集成**: 集成MCP和智谱AI服务
4. **响应式设计**: 支持移动端和桌面端
5. **实时更新**: 支持实时数据同步和缓存管理

## 🔄 数据流

```
用户界面 → Nginx (80) → FastAPI (5001) → SQLite数据库
         ↓
    MCP Web界面 (5002) → MCP API (5003) → AI服务
```

## 📝 开发说明

- **前端**: 原生HTML/CSS/JavaScript，无框架依赖
- **后端**: FastAPI + SQLite
- **AI服务**: MCP协议 + 智谱AI
- **部署**: Nginx反向代理 + 多端口服务
