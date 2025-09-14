#!/usr/bin/env python3
"""
邀请码API测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:5001"
ADMIN_CODE = "ADMIN-RESET-123"

def test_generate_codes():
    """测试生成邀请码API"""
    print("=== 测试生成邀请码API ===")
    
    url = f"{BASE_URL}/api/invite-codes/generate"
    data = {
        "count": 5,
        "admin_code": ADMIN_CODE
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_get_status():
    """测试获取邀请码状态API"""
    print("\n=== 测试获取邀请码状态API ===")
    
    url = f"{BASE_URL}/api/invite-codes/status"
    params = {"admin_code": ADMIN_CODE}
    
    try:
        response = requests.get(url, params=params)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_validate_code():
    """测试验证邀请码API"""
    print("\n=== 测试验证邀请码API ===")
    
    url = f"{BASE_URL}/api/invite-codes/validate"
    data = {"code": "INV4I9XKMU2"}
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_list_codes():
    """测试列出邀请码API"""
    print("\n=== 测试列出邀请码API ===")
    
    url = f"{BASE_URL}/api/invite-codes/list"
    params = {
        "admin_code": ADMIN_CODE,
        "limit": 10,
        "offset": 0
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"请求失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试邀请码API...")
    
    # 测试各个API
    results = []
    results.append(test_generate_codes())
    results.append(test_get_status())
    results.append(test_validate_code())
    results.append(test_list_codes())
    
    print(f"\n=== 测试结果 ===")
    print(f"成功: {sum(results)}/{len(results)}")
    print(f"失败: {len(results) - sum(results)}/{len(results)}")
