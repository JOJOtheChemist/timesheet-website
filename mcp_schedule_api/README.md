# MCP Schedule API Server

## 项目简介

这是一个将FastAPI应用转换为Model Context Protocol (MCP)格式的日程表API服务器。MCP是一个标准化的协议，用于AI模型与外部工具和资源的交互。

## 主要特性

- ✅ **MCP协议支持** - 完全兼容MCP 2024-11-05版本
- ✅ **MySQL数据库** - 使用连接池管理数据库连接
- ✅ **异步处理** - 基于asyncio的高性能异步架构
- ✅ **工具和资源** - 支持工具调用和资源读取
- ✅ **标准化接口** - 遵循MCP协议规范

## 文件结构

```
mcp_schedule_api/
├── mcp_schedule_server.py    # MCP服务器主程序
├── mcp_client_example.py     # MCP客户端示例
├── mcp_config.json          # MCP配置文件
├── requirements.txt          # Python依赖
├── start_mcp_server.sh      # 启动脚本
└── README.md                # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置数据库

确保MySQL数据库已启动，并更新 `mcp_config.json` 中的数据库配置：

```json
{
  "database": {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "project_tasks"
  }
}
```

### 3. 启动服务器

```bash
# 使用启动脚本
./start_mcp_server.sh

# 或直接运行
python3 mcp_schedule_server.py
```

## MCP协议特性

### 支持的工具 (Tools)

- **get_schedule** - 获取指定日期的日程数据
- **create_schedule** - 创建新的日程记录
- **update_schedule** - 更新现有日程记录
- **delete_schedule** - 删除日程记录
- **get_projects** - 获取项目列表

### 支持的资源 (Resources)

- **schedule** - 日程表数据资源
- **projects** - 项目数据资源

### 协议方法

- **initialize** - 初始化MCP连接
- **tools/list** - 列出可用工具
- **tools/call** - 调用工具
- **resources/list** - 列出可用资源
- **resources/read** - 读取资源

## 使用示例

### 客户端示例

```python
import asyncio
from mcp_client_example import MCPScheduleClient

async def main():
    async with MCPScheduleClient() as client:
        # 初始化连接
        await client.initialize()
        
        # 获取日程数据
        schedule = await client.get_schedule("2024-01-01")
        print(f"获取到 {len(schedule)} 条日程记录")
        
        # 创建新日程
        result = await client.create_schedule({
            "schedule_date": "2024-01-01",
            "time_slot": "09:00",
            "planned_notes": "测试日程"
        })
        print(f"创建结果: {result}")

asyncio.run(main())
```

## 配置说明

### 服务器配置

- **host**: 服务器监听地址 (默认: 0.0.0.0)
- **port**: 服务器端口 (默认: 8000)
- **debug**: 调试模式 (默认: false)

### 数据库配置

- **pool_size**: 连接池大小 (默认: 5)
- **autocommit**: 自动提交 (默认: true)
- **charset**: 字符集 (默认: utf8mb4)

## 开发说明

### 添加新工具

1. 在 `initialize_tools()` 方法中添加工具定义
2. 在 `call_tool()` 方法中添加工具实现
3. 更新工具的描述和输入模式

### 添加新资源

1. 在 `initialize_resources()` 方法中添加资源定义
2. 在 `read_resource()` 方法中添加资源读取逻辑
3. 更新资源的MIME类型和描述

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库配置信息
   - 确认网络连接正常

2. **依赖安装失败**
   - 使用Python 3.8+
   - 检查pip版本
   - 尝试升级pip: `pip install --upgrade pip`

3. **权限问题**
   - 确保脚本有执行权限: `chmod +x start_mcp_server.sh`
   - 检查文件所有者权限

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！ 