# Schedule Assistant (ReAct)

一个独立的基于 ReAct 范式的命令行助手，调用现有的 MCP HTTP 服务（/home/ubuntu/timesheet/mcp_schedule_api）来填写日程表。

## 功能
- 解析自然语言中的时间表达（昨天/昨晚/今天/明天 + HH点[半]）
- 识别睡觉/起床/计划类意图
- 多段睡眠自动分段填充（以 30 分钟为粒度）
- 计划类请求根据已存在子任务进行匹配（语义近似），若未匹配则提示需要创建子任务
- 自动在备注中加入例如“抖音听asmr睡着”等关键信息

## 前置条件
- MCP HTTP 服务已在 8001 端口启动：
  - 路径：`/home/ubuntu/timesheet/mcp_schedule_api/mcp_http_server.py`
  - 健康检查：`curl -s http://127.0.0.1:8001/api/health`
- Python 3.12+

## 安装依赖
助手脚本使用 `requests` 包，请确保可用（已有服务端虚拟环境即可复用，也可直接系统 pip 安装）：
```bash
pip3 install requests
```

## 使用
```bash
cd /home/ubuntu/timesheet/schedule_assistant
python3 assistant.py '我昨天2点睡觉、今天12点、起床、昨晚是听抖音asmr睡着的'
python3 assistant.py '计划接下来要研究一下agent' --dry-run
```

- 默认会真实写入日程。带 `--dry-run` 仅打印将要执行的操作而不写库。
- 睡眠：自动从“睡觉”到“起床”之间按 30 分钟粒度写入实际任务。
- 计划：在未来一小时内按 30 分钟粒度创建计划任务，备注含“agent相关研究”等关键词。

## 说明
- 子任务匹配：使用相似度近似查找（带有一些同义词扩展）。若没有匹配到合适子任务，会提示先到项目管理里创建对应子任务。
- 本助手不是 MCP 服务本身，而是调用已有的 `/home/ubuntu/timesheet/mcp_schedule_api` HTTP 接口完成写入。 