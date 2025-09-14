#!/bin/bash
# 每日用户画像分析脚本

# 设置工作目录
cd /home/ubuntu/timesheet/user_profile

# 激活Python环境（如果需要）
# source /path/to/your/venv/bin/activate

# 运行分析脚本
echo "🚀 开始每日用户画像分析..."
python3 ai_user_analysis.py

# 检查是否成功生成报告
if [ $? -eq 0 ]; then
    echo "✅ 每日分析完成"
    
    # 可选：发送通知或上传到服务器
    # curl -X POST "your_webhook_url" -d "每日用户画像分析完成"
    
    # 可选：清理旧报告（保留最近30天）
    # find . -name "用户画像分布分析报告_*.md" -mtime +30 -delete
else
    echo "❌ 分析失败"
    exit 1
fi
