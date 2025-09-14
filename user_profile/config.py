# 配置文件
# 请根据您的实际情况修改以下配置

# 智谱AI API配置
ZHIPU_API_KEY = "ce85d782d3834f3982b87494dbd2a447.y8l8wxwEFafurRY2"
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'debian-sys-maint',
    'password': '36p2WFXFNmwuYvox',
    'database': 'project_tasks',
    'charset': 'utf8mb4'
}

# 分析配置
ANALYSIS_CONFIG = {
    'max_project_keywords': 20,  # 项目关键词最大数量
    'min_keyword_length': 2,     # 关键词最小长度
    'ai_model': 'glm-4.5-air',   # 使用的AI模型
    'temperature': 0.7,          # AI生成温度
    'max_tokens': 2000           # 最大token数
}
