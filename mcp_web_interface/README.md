# 🌐 MCP Web界面

一个基于Flask的Web界面，提供与MCP服务器的自然语言交互功能。

## ✨ 功能特性

- 🤖 **智能对话**: 使用自然语言与AI助手交互
- 📅 **日程管理**: 查询、创建、更新日程安排
- 📁 **项目管理**: 查看项目结构和任务信息
- 🔧 **MCP集成**: 完全兼容MCP协议
- 🎨 **现代化UI**: 响应式设计，支持移动端
- 📊 **实时反馈**: 实时显示操作结果和AI分析

## 🏗️ 项目结构

```
mcp_web_interface/
├── templates/              # HTML模板
│   └── index.html         # 主页面
├── static/                 # 静态资源
│   ├── css/               # 样式文件
│   │   └── style.css      # 主样式
│   └── js/                # JavaScript文件
│       ├── mcp-client.js  # MCP客户端
│       ├── ui-manager.js  # UI管理器
│       └── main.js        # 主程序
├── app.py                 # Flask后端服务器
├── requirements.txt       # Python依赖
├── start_web_server.sh   # 启动脚本
├── nginx.conf            # Nginx配置
└── README.md             # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /home/ubuntu/timesheet/mcp_web_interface
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 启动Web服务器

```bash
# 方法1: 使用启动脚本
chmod +x start_web_server.sh
./start_web_server.sh

# 方法2: 直接启动
source venv/bin/activate
python3 app.py
```

### 3. 配置Nginx

将 `nginx.conf` 中的配置添加到你的Nginx配置文件中，然后重启Nginx：

```bash
sudo nginx -t          # 测试配置
sudo systemctl reload nginx  # 重新加载配置
```

### 4. 访问应用

- **本地访问**: http://localhost:5000
- **公网访问**: http://140.143.194.215/

## 🔧 配置说明

### MCP服务器地址

在 `app.py` 中修改MCP服务器地址：

```python
MCP_SERVER_URL = "http://localhost:8000"  # 改为你的MCP服务器地址
```

### 端口配置

默认Flask运行在5000端口，可在 `app.py` 中修改：

```python
app.run(
    host='0.0.0.0',
    port=5000,  # 修改端口号
    debug=True,
    threaded=True
)
```

## 📱 使用方法

### 1. 自然语言交互

在输入框中输入自然语言指令，例如：

- "查询今天的日程安排"
- "显示所有项目"
- "创建明天上午9点的会议"
- "更新日程ID为123的备注"

### 2. 查看结果

- **日程标签页**: 显示日程查询结果
- **项目标签页**: 显示项目结构信息
- **AI分析标签页**: 显示AI分析结果

### 3. 对话历史

所有交互都会保存在对话历史中，可以查看完整的对话记录。

## 🔌 API接口

### MCP代理接口

- `POST /api/mcp` - MCP请求代理
- `GET /api/health` - 健康检查
- `GET /api/tools` - 获取工具列表
- `GET /api/resources` - 获取资源列表
- `GET /api/schedule/<date>` - 获取日程
- `GET /api/projects` - 获取项目
- `POST /api/ai-analyze` - AI分析

### 使用示例

```javascript
// 发送MCP请求
const response = await fetch('/api/mcp', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        jsonrpc: "2.0",
        id: "test",
        method: "tools/list",
        params: {}
    })
});

const result = await response.json();
```

## 🛠️ 开发说明

### 组件架构

- **MCPClient**: 负责与MCP服务器通信
- **UIManager**: 管理页面UI状态和交互
- **MCPApp**: 应用主类，负责初始化和协调

### 扩展功能

要添加新功能，可以：

1. 在 `MCPClient` 中添加新的MCP方法
2. 在 `UIManager` 中添加对应的UI处理逻辑
3. 在 `app.py` 中添加新的API端点

## 🔍 故障排除

### 常见问题

1. **MCP服务器连接失败**
   - 检查MCP服务器是否运行
   - 确认 `MCP_SERVER_URL` 配置正确

2. **页面无法访问**
   - 检查Flask服务器是否启动
   - 确认Nginx配置正确
   - 检查防火墙设置

3. **静态文件加载失败**
   - 确认 `static` 目录存在
   - 检查文件权限

### 日志查看

```bash
# Flask日志
tail -f /var/log/flask_app.log

# Nginx日志
tail -f /var/log/nginx/mcp_web_access.log
tail -f /var/log/nginx/mcp_web_error.log
```

## 📄 许可证

本项目基于MIT许可证开源。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 支持

如有问题，请查看：
1. 项目文档
2. 故障排除部分
3. 提交Issue

---

**享受你的MCP智能日程助手！** 🎉 