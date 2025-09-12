#!/usr/bin/env python3
import requests
import json

# 测试LLM agent集成
def test_agent_chat():
    # 首先登录获取token
    login_data = {
        "username": "yeya",
        "password": "yeya"
    }
    
    login_response = requests.post("http://127.0.0.1:5001/api/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"登录失败: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试LLM agent
    test_messages = [
        "我考研内容好多啊，就金融数学这个类别，我就需要刷题100道，背诵资料",
        "我最近对手工感兴趣，作为休闲时间的时间打发"
    ]
    
    for message in test_messages:
        print(f"\n测试消息: {message}")
        chat_data = {"message": message}
        
        response = requests.post("http://127.0.0.1:5001/api/agent/chat", json=chat_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"回复: {result['reply']}")
            print(f"解析字段: {result['parsed']}")
            if result.get('subtask_id'):
                print(f"创建了子任务ID: {result['subtask_id']}")
        else:
            print(f"请求失败: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_agent_chat()
