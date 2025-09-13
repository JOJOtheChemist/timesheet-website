#!/usr/bin/env python3
"""
SQLAlchemy API 测试脚本
测试所有API端点的功能
"""
import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:5004"

def test_health():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    return response.status_code == 200

def test_schedule_operations():
    """测试日程操作"""
    print("\n=== 测试日程操作 ===")
    
    # 测试创建日程
    schedule_data = {
        "schedule_data": [
            {
                "schedule_date": "2025-09-13",
                "time_slot": "09:00",
                "planned_subtask_name": "测试任务",
                "planned_notes": "这是一个测试任务",
                "mood": "开心"
            },
            {
                "schedule_date": "2025-09-13",
                "time_slot": "10:00",
                "actual_subtask_name": "实际任务",
                "actual_notes": "这是实际完成的任务",
                "mood": "满意"
            }
        ]
    }
    
    # 创建日程
    response = requests.post(
        f"{BASE_URL}/api/schedule?user_id=1",
        json=schedule_data
    )
    print(f"创建日程状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"创建日程响应: {response.json()}")
    else:
        print(f"创建日程错误: {response.text}")
    
    # 获取日程
    response = requests.get(f"{BASE_URL}/api/schedule/2025-09-13?user_id=1")
    print(f"获取日程状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"获取日程响应: {response.json()}")
    else:
        print(f"获取日程错误: {response.text}")

def test_project_operations():
    """测试项目操作"""
    print("\n=== 测试项目操作 ===")
    
    # 创建项目
    project_data = {
        "name": "测试项目",
        "description": "这是一个测试项目",
        "category_name": "工作",
        "color": "#ff0000"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/projects?user_id=1",
        json=project_data
    )
    print(f"创建项目状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"创建项目响应: {response.json()}")
    else:
        print(f"创建项目错误: {response.text}")
    
    # 获取项目列表
    response = requests.get(f"{BASE_URL}/api/projects?user_id=1")
    print(f"获取项目状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"获取项目响应: {response.json()}")
    else:
        print(f"获取项目错误: {response.text}")

def test_subtask_operations():
    """测试子任务操作"""
    print("\n=== 测试子任务操作 ===")
    
    # 创建子任务
    subtask_data = {
        "name": "测试子任务",
        "project_id": 1,
        "urgency_importance": "重要紧急",
        "difficulty": "困难",
        "color": "#00ff00"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/subtasks?user_id=1",
        json=subtask_data
    )
    print(f"创建子任务状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"创建子任务响应: {response.json()}")
    else:
        print(f"创建子任务错误: {response.text}")
    
    # 获取子任务列表
    response = requests.get(f"{BASE_URL}/api/subtasks?user_id=1")
    print(f"获取子任务状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"获取子任务响应: {response.json()}")
    else:
        print(f"获取子任务错误: {response.text}")

def test_category_operations():
    """测试分类操作"""
    print("\n=== 测试分类操作 ===")
    
    # 创建分类
    category_data = {
        "name": "学习",
        "color": "#0000ff"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/categories?user_id=1",
        json=category_data
    )
    print(f"创建分类状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"创建分类响应: {response.json()}")
    else:
        print(f"创建分类错误: {response.text}")
    
    # 获取分类列表
    response = requests.get(f"{BASE_URL}/api/categories?user_id=1")
    print(f"获取分类状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"获取分类响应: {response.json()}")
    else:
        print(f"获取分类错误: {response.text}")

def main():
    """主测试函数"""
    print("开始测试 SQLAlchemy API...")
    
    # 测试健康检查
    if not test_health():
        print("健康检查失败，请确保API服务正在运行")
        return
    
    # 测试各个功能模块
    test_schedule_operations()
    test_project_operations()
    test_subtask_operations()
    test_category_operations()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
