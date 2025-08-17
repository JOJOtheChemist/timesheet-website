#!/usr/bin/env python3
"""
测试智谱AI API调用
"""

import requests
import json

# 智谱AI配置
API_KEY = "ce85d782d3834f3982b87494dbd2a447.y8l8wxwEFafurRY2"
MODEL = "glm-4.5-air"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def test_zhipuai_api():
    """测试智谱AI API调用"""
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "你好，请简单介绍一下你自己"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 1024
    }
    
    try:
        print(f"正在测试智谱AI API...")
        print(f"模型: {MODEL}")
        print(f"API地址: {API_URL}")
        print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ API调用成功!")
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 提取AI回复
            if 'choices' in result and len(result['choices']) > 0:
                ai_message = result['choices'][0]['message']['content']
                print(f"\n🤖 AI回复: {ai_message}")
            
            return True
        else:
            print(f"\n❌ API调用失败!")
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        return False

if __name__ == "__main__":
    success = test_zhipuai_api()
    if success:
        print("\n🎉 智谱AI API测试成功!")
    else:
        print("\n💥 智谱AI API测试失败!") 