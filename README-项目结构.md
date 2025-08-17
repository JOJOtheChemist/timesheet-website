# 项目结构说明

## 📁 目录结构

```
timesheet/
├── 📁 backend/                    # 后端服务目录
│   ├── fastapi_schedule_api.py    # FastAPI主应用（MySQL）
│   ├── requirements.txt           # Python依赖
│   ├── start_api.sh              # 启动脚本
│   ├── deploy.sh                 # 部署脚本
│   ├── schedule-api.service      # systemd服务配置
│   ├── timesheet.service         # 前端服务配置
│   ├── api.log                   # API日志
│   └── README.md                 # 后端说明文档
│
├── 📁 components/                 # 前端组件目录
│   └── 📁 background-switcher/   # 背景切换器组件
│       ├── background-switcher.css
│       ├── background-switcher.js
│       ├── README-背景切换器.md
│       └── README.md
│
├── 📁 mcp_schedule_api/          # MCP协议实现目录
│   ├── mcp_schedule_server.py    # MCP服务器主程序
│   ├── mcp_client_example.py     # MCP客户端示例
│   ├── ai_integration_example.py # AI集成示例
│   ├── demo_interactive.py       # 交互式演示
│   ├── mcp_config.json          # MCP配置文件
│   ├── requirements.txt          # Python依赖
│   ├── start_mcp_server.sh      # 启动脚本
│   ├── install.sh               # 安装脚本
│   ├── mcp-schedule.service     # systemd服务配置
│   ├── README.md                # 项目说明
│   ├── AI_INTEGRATION_GUIDE.md  # AI集成指南
│   └── MCP_CONVERSION_SUMMARY.md # 转换总结
│
├── 📁 static/                    # 静态资源目录
│   ├── css/                      # 样式文件
│   ├── js/                       # JavaScript文件
│   └── images/                   # 图片资源
│
├── 📁 venv/                      # Python虚拟环境
├── daily_schedule.html           # 主页面（日程表）
├── nginx.conf                    # Nginx主配置
├── timesheet.conf                # 站点配置
├── cache-manager.js              # 缓存管理
├── timesheet.db                  # SQLite数据库（已弃用，使用MySQL）
├── README.md                     # 项目主说明
└── README-项目结构.md            # 本文件
```

## 🔄 架构说明

### **前端架构**
- **主页面**: `daily_schedule.html` - 包含完整的日程表功能
- **组件化**: `components/` - 可复用的前端组件
- **静态资源**: `static/` - CSS、JS、图片等资源

### **后端架构**
- **主服务**: `backend/fastapi_schedule_api.py` - FastAPI应用，使用MySQL
- **服务管理**: systemd服务配置，支持自动启动和重启
- **部署脚本**: 自动化部署和配置

### **MCP架构** (新增)
- **协议实现**: `mcp_schedule_api/` - Model Context Protocol实现
- **AI集成**: 支持AI模型调用日程表工具
- **标准化接口**: 遵循MCP协议规范

## 🚀 服务说明

### **运行中的服务**
1. **FastAPI后端**: 端口5001，提供REST API
2. **Nginx前端**: 端口80，提供静态文件和反向代理
3. **MySQL数据库**: 存储项目、任务、日程数据

### **MCP服务** (可选)
- **MCP服务器**: 端口8000，提供AI模型接口
- **支持工具**: 日程查询、创建、更新、删除
- **支持资源**: 日程数据、项目信息

## 📊 数据流

```
用户操作 → 前端界面 → FastAPI后端 → MySQL数据库
    ↓
AI模型 → MCP协议 → MCP服务器 → 相同数据库
```

## 🛠️ 开发说明

### **添加新功能**
1. **前端**: 在 `daily_schedule.html` 中添加功能
2. **后端**: 在 `backend/fastapi_schedule_api.py` 中添加API
3. **MCP**: 在 `mcp_schedule_api/` 中添加工具和资源

### **部署更新**
1. 修改代码后重启FastAPI服务
2. 更新前端文件后刷新浏览器
3. MCP服务需要重启以加载新工具

## 🔧 维护说明

### **日志查看**
- **API日志**: `backend/api.log`
- **系统日志**: `sudo journalctl -u schedule-api.service`
- **Nginx日志**: `/var/log/nginx/`

### **服务管理**
- **启动**: `sudo systemctl start schedule-api.service`
- **停止**: `sudo systemctl stop schedule-api.service`
- **状态**: `sudo systemctl status schedule-api.service`

### **MCP服务管理**
- **启动**: `cd mcp_schedule_api && ./start_mcp_server.sh`
- **安装**: `cd mcp_schedule_api && ./install.sh`
- **演示**: `cd mcp_schedule_api && python3 demo_interactive.py`

## 📈 扩展方向

### **短期目标**
- ✅ 完善MCP工具集
- ✅ 优化AI集成体验
- ✅ 添加更多智能功能

### **长期目标**
- 🔄 多模态交互（语音、图像）
- 🔄 预测性分析
- 🔄 个性化AI助手
- 🔄 移动端应用

## 🎯 总结

项目采用模块化架构，支持多种访问方式：
1. **传统Web界面** - 通过浏览器访问
2. **REST API** - 通过HTTP请求访问
3. **MCP协议** - 通过AI模型访问

这种设计让项目既保持了传统的易用性，又具备了AI时代的智能化能力。 