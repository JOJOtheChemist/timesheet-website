# Timesheet 项目复制清单

## 📋 复制前准备

### 1. 环境要求
- Ubuntu 20.04+ 或类似Linux系统
- Python 3.8+
- Node.js (可选，用于前端开发)
- Nginx
- Git

### 2. 依赖安装
```bash
# 安装Python依赖
pip install fastapi uvicorn mysql-connector-python passlib python-jose[cryptography] python-multipart

# 安装Nginx
sudo apt update
sudo apt install nginx

# 安装其他工具
sudo apt install curl wget
```

## 📁 需要复制的核心文件

### 1. 后端API服务
```
timesheet/backend/
├── fastapi_schedule_api.py    # 主API服务
├── batch_api.py              # 批量操作API
├── batch_manager.py          # 批量管理器
├── start_api.sh              # 启动脚本
└── README.md                 # 文档
```

### 2. 前端页面
```
timesheet/
├── daily_schedule.html       # 日程表主页面
├── edit_subtasks.html        # 编辑子任务页面
├── login.html                # 登录页面
├── onboarding.html           # 引导页面
└── cache-manager.js          # 缓存管理器
```

### 3. 组件库
```
timesheet/components/
├── auth-modal/
│   └── auth-modal.js
└── background-switcher/
    ├── background-switcher.css
    ├── background-switcher.js
    └── README.md
```

### 4. 静态资源
```
timesheet/static/
└── images/                   # 所有图片资源
    ├── easyhard/
    ├── style1/
    ├── svg/
    ├── 学习表情包/
    ├── 背景图2/
    └── 蕨类/
```

### 5. 配置文件
```
timesheet/
├── nginx.conf                # Nginx配置
├── timesheet.conf            # 项目配置
├── .gitignore                # Git忽略文件
└── start_api_with_agent.sh   # 启动脚本
```

### 6. 数据库
```
timesheet/timesheet.db        # SQLite数据库文件
```

## 🔧 复制后配置

### 1. 修改端口配置
- 检查 `backend/fastapi_schedule_api.py` 中的端口设置
- 检查 `nginx.conf` 中的代理配置
- 确保端口5001、5002可用

### 2. 修改API地址
- 检查 `login.html` 中的 `API_BASE` 配置
- 检查 `daily_schedule.html` 中的API调用地址
- 确保所有API调用指向正确的端口

### 3. 数据库配置
- 确保 `timesheet.db` 文件权限正确
- 检查数据库连接配置

### 4. 启动服务
```bash
# 启动主API服务
cd /path/to/timesheet
./start_api_with_agent.sh

# 配置Nginx
sudo cp nginx.conf /etc/nginx/sites-available/timesheet
sudo ln -s /etc/nginx/sites-available/timesheet /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## ⚠️ 注意事项

1. **端口冲突**: 确保5001、5002端口未被占用
2. **文件权限**: 确保脚本文件有执行权限
3. **依赖版本**: 检查Python包版本兼容性
4. **数据库路径**: 确保数据库文件路径正确
5. **API地址**: 确保前端API调用地址正确

## 🚀 验证复制

### 1. 检查服务状态
```bash
# 检查端口监听
netstat -tlnp | grep -E ":(5001|5002|80)"

# 检查API健康状态
curl http://localhost:5001/health
curl http://localhost:5002/
```

### 2. 测试功能
- 访问登录页面
- 测试用户登录
- 检查日程表显示
- 测试任务编辑功能

## 📞 故障排除

### 常见问题
1. **502 Bad Gateway**: 检查后端服务是否启动
2. **API调用失败**: 检查API地址配置
3. **数据库错误**: 检查数据库文件权限
4. **静态资源404**: 检查Nginx配置

### 日志查看
```bash
# 查看API日志
tail -f timesheet/api.log

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log
```
