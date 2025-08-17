# MCP快速启动指南

## 🎯 **MCP是什么？**

MCP (Model Context Protocol) 让你的日程表应用支持AI模型交互：
- **自然语言操作** - 用中文说话就能管理日程
- **AI驱动** - AI自动理解需求并执行操作
- **标准化协议** - 遵循MCP协议规范

## 📁 **目录位置**

MCP功能位于项目根目录下的 `mcp_schedule_api/` 文件夹：
```
/home/ubuntu/timesheet/mcp_schedule_api/
```

## 🚀 **快速开始**

### **步骤1：进入MCP目录**
```bash
cd /home/ubuntu/timesheet/mcp_schedule_api
```

### **步骤2：安装依赖**
```bash
# 创建虚拟环境并安装依赖
./install.sh
```

### **步骤3：启动MCP服务器**
```bash
# 方式1：手动启动
./start_mcp_server.sh

# 方式2：使用systemd服务
sudo systemctl start mcp-schedule.service
```

### **步骤4：体验功能**
```bash
# 运行交互式演示
python3 demo_interactive.py
```

## 🎮 **功能演示**

### **1. 交互式演示**
```bash
cd /home/ubuntu/timesheet/mcp_schedule_api
python3 demo_interactive.py
```

**演示功能：**
- 📅 查看日程安排
- ➕ 创建新日程
- 📊 查看项目信息
- 🔍 智能查询演示

### **2. AI集成示例**
```bash
cd /home/ubuntu/timesheet/mcp_schedule_api
python3 ai_integration_example.py
```

**AI功能：**
- 自然语言理解
- 自动工具选择
- 智能操作执行

### **3. 客户端示例**
```bash
cd /home/ubuntu/timesheet/mcp_schedule_api
python3 mcp_client_example.py
```

**客户端功能：**
- MCP协议通信
- 工具调用示例
- 资源访问演示

## 🔧 **服务管理**

### **查看服务状态**
```bash
sudo systemctl status mcp-schedule.service
```

### **启动服务**
```bash
sudo systemctl start mcp-schedule.service
```

### **停止服务**
```bash
sudo systemctl stop mcp-schedule.service
```

### **查看日志**
```bash
sudo journalctl -u mcp-schedule.service -f
```

## 📊 **MCP工具说明**

### **可用工具**
1. **`get_schedule`** - 获取指定日期的日程数据
2. **`create_schedule`** - 创建新的日程记录
3. **`update_schedule`** - 更新现有日程记录
4. **`delete_schedule`** - 删除日程记录
5. **`get_projects`** - 获取项目列表

### **可用资源**
1. **`schedule`** - 日程表数据资源
2. **`projects`** - 项目数据资源

## 🌐 **网络配置**

### **默认端口**
- **MCP服务器**: 8000
- **FastAPI后端**: 5001
- **Nginx前端**: 80

### **访问地址**
- **Web界面**: http://localhost
- **API文档**: http://localhost:5001/docs
- **MCP服务**: http://localhost:8000

## 🚨 **故障排除**

### **常见问题**

#### **1. 依赖安装失败**
```bash
# 检查Python版本
python3 --version

# 升级pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

#### **2. 服务启动失败**
```bash
# 检查日志
sudo journalctl -u mcp-schedule.service -n 50

# 检查端口占用
sudo netstat -tlnp | grep :8000

# 手动启动测试
cd /home/ubuntu/timesheet/mcp_schedule_api
python3 mcp_schedule_server.py
```

#### **3. 数据库连接失败**
```bash
# 检查MySQL服务
sudo systemctl status mysql

# 检查数据库配置
cat mcp_config.json | grep -A 10 "database"
```

### **调试模式**
```bash
# 设置调试日志
export MCP_LOG_LEVEL=DEBUG

# 启动服务器
python3 mcp_schedule_server.py
```

## 📚 **学习资源**

### **文档文件**
- **`README.md`** - 项目说明
- **`AI_INTEGRATION_GUIDE.md`** - AI集成指南
- **`MCP_CONVERSION_SUMMARY.md`** - 转换总结

### **在线资源**
- **MCP官方文档**: https://modelcontextprotocol.io/
- **Claude API**: https://docs.anthropic.com/
- **OpenAI API**: https://platform.openai.com/docs

## 🎉 **下一步**

### **基础使用**
1. ✅ 运行演示程序
2. ✅ 理解MCP工具
3. ✅ 测试基本功能

### **进阶使用**
1. 🔄 集成真实AI模型
2. 🔄 自定义MCP工具
3. 🔄 优化AI提示词

### **生产部署**
1. 🔄 配置生产环境
2. 🔄 设置监控告警
3. 🔄 性能优化

## 💡 **使用建议**

1. **新手**: 先运行 `demo_interactive.py` 体验功能
2. **开发者**: 查看 `ai_integration_example.py` 学习集成
3. **运维**: 使用systemd服务管理MCP服务器

**现在就开始体验MCP的强大功能吧！** 🚀 