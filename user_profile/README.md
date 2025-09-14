# 智谱AI用户画像分析系统

## 功能概述

这是一个基于智谱AI API的自动化用户画像分析系统，能够：
- 自动从数据库获取用户画像数据
- 使用多个AI Agent分析专业分布、目标分布、项目分布
- 生成专业的分析报告
- 支持每日自动化分析

## 文件说明

- `ai_user_analysis.py` - 主分析脚本
- `daily_analysis.sh` - 每日分析脚本
- `config.py` - 配置文件
- `README.md` - 说明文档

## 使用前配置

### 1. 安装依赖
```bash
pip install requests mysql-connector-python
```

### 2. 配置API密钥
编辑 `config.py` 文件，设置您的智谱AI API密钥：
```python
ZHIPU_API_KEY = "your_actual_api_key_here"
```

### 3. 配置数据库
编辑 `config.py` 文件，设置数据库连接信息：
```python
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_actual_password',
    'database': 'project_tasks',
    'charset': 'utf8mb4'
}
```

## 使用方法

### 手动运行分析
```bash
python3 ai_user_analysis.py
```

### 每日自动分析
```bash
./daily_analysis.sh
```

### 设置定时任务
在crontab中添加以下行，实现每日自动分析：
```bash
# 每天上午9点运行分析
0 9 * * * /home/ubuntu/timesheet/user_profile/daily_analysis.sh
```

## 输出文件

分析完成后会生成以下文件：
- `用户画像分布分析报告_YYYY-MM-DD.md` - 每日分析报告

## AI分析功能

### 专业分布分析Agent
- 分析用户专业分布情况
- 识别主导专业和集中度
- 提供专业类别分析

### 目标分布分析Agent
- 分析用户备考目标分布
- 识别主流目标和趋势
- 提供目标类别分析

### 项目分布分析Agent
- 分析用户学习项目分布
- 提取热门项目关键词
- 提供学习模式分析

### 综合分析Agent
- 整合所有分析结果
- 生成趋势预测
- 提供建议和行动项

## 注意事项

1. 确保数据库连接正常
2. 确保智谱AI API密钥有效
3. 定期检查生成的报告质量
4. 可根据需要调整分析参数

## 故障排除

### 常见问题
1. **数据库连接失败** - 检查数据库配置和网络连接
2. **API调用失败** - 检查API密钥和网络连接
3. **报告生成失败** - 检查文件权限和磁盘空间

### 日志查看
运行脚本时会输出详细的执行日志，包括：
- 数据库连接状态
- 数据获取情况
- AI分析进度
- 文件保存状态
