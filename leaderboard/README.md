# Leaderboard - Time Management Rankings

## 功能概述

排行榜系统是一个基于时间管理的排名展示工具，提供：

1. **多维度排名** - 日榜、周榜、月榜、年榜
2. **时间统计** - 统计各用户的学习/工作时间
3. **效率分析** - 评估用户的时间使用效率
4. **实时更新** - 自动刷新排名数据

## 文件结构

```
leaderboard/
├── leaderboard.html      # 排行榜前端页面
├── index.html           # 默认首页
├── leaderboard_api.py   # FastAPI后端服务
├── start_leaderboard.sh # 启动脚本
└── README.md           # 说明文档
```

## 功能特性

### 1. 多时间维度排名
- **Daily Rankings** - 今日排名
- **Weekly Rankings** - 本周排名  
- **Monthly Rankings** - 本月排名
- **Yearly Rankings** - 本年排名

### 2. 排名指标
- 总学习/工作时间
- 活跃天数
- 完成任务数
- 效率评级 (High/Medium/Low)

### 3. 统计摘要
- 总用户数
- 总时间
- 平均时间
- 最高时间

## API接口

### 健康检查
```
GET /health
```

### 获取排行榜
```
GET /api/leaderboard?period={daily|weekly|monthly|yearly}
```

### 获取统计信息
```
GET /api/leaderboard/stats
```

## 使用方法

### 1. 启动服务
```bash
# 使用启动脚本
./start_leaderboard.sh

# 或手动启动
cd /home/ubuntu/timesheet
source venv/bin/activate
cd leaderboard
python3 leaderboard_api.py
```

### 2. 访问排行榜页面
打开浏览器访问：`http://140.143.194.215/leaderboard/`

### 3. 查看不同时间维度的排名
- 点击 "Daily" 查看今日排名
- 点击 "Weekly" 查看本周排名
- 点击 "Monthly" 查看本月排名
- 点击 "Yearly" 查看本年排名

## 技术架构

- **前端**: HTML + CSS + JavaScript
- **后端**: FastAPI + Python
- **数据库**: MySQL (project_tasks数据库)
- **服务器**: Nginx (反向代理)

## 数据库依赖

排行榜系统依赖以下数据库表：
- `daily_schedule` - 日程记录表
- `users` - 用户表

## 配置说明

### 数据库配置
在 `leaderboard_api.py` 中配置MySQL连接：
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '12356790zZ_',
    'database': 'project_tasks',
    'charset': 'utf8mb4',
    'ssl_disabled': True
}
```

### Nginx配置
已自动配置以下路由：
- `/leaderboard/` - 排行榜页面
- `/api/leaderboard` - 排行榜API

## 排名算法

### 时间计算
- 基于 `daily_schedule` 表中的 `time_slot` 字段
- 自动解析时间段格式 (如 "09:00-10:30")
- 计算实际学习/工作时间

### 排名规则
1. 按总时间降序排列
2. 时间相同时按活跃天数排序
3. 活跃天数相同时按任务完成数排序

### 效率评级
- **High**: 8小时以上
- **Medium**: 4-8小时
- **Low**: 4小时以下

## 故障排除

### 1. 服务无法启动
- 检查虚拟环境是否正确激活
- 确认依赖包已安装：`pip install fastapi uvicorn`
- 检查端口5007是否被占用

### 2. 页面无法访问
- 检查nginx配置是否正确
- 确认排行榜API路由已配置
- 检查防火墙设置

### 3. 数据为空
- 检查数据库连接是否正常
- 确认 `daily_schedule` 表中有数据
- 检查时间范围设置

### 4. API调用失败
- 检查服务是否正在运行：`curl http://localhost:5007/health`
- 查看控制台错误信息
- 确认数据库表结构正确

## 扩展功能

### 添加新的排名维度
在 `get_leaderboard_data()` 函数中添加新的统计指标。

### 自定义排名算法
修改SQL查询逻辑，实现自定义的排名规则。

### 集成其他数据源
扩展数据库查询，支持从其他表获取排名数据。

## 性能优化

- 排行榜数据每5分钟自动刷新
- 限制显示前50名用户
- 使用数据库索引优化查询性能
- 前端缓存减少API调用
