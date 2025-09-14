# 邀请码管理系统

## 功能概述

这是一个完整的邀请码管理系统，包含生成、验证、状态查询等功能。

## 文件结构

```
invitation_code/
├── __init__.py          # 模块初始化
├── generator.py         # 邀请码生成器核心逻辑
├── api.py              # FastAPI路由定义
├── test_api.py         # API测试脚本
└── README.md           # 使用说明
```

## API接口

### 1. 生成邀请码
**POST** `/api/invite-codes/generate`

**请求体:**
```json
{
    "count": 11,
    "admin_code": "ADMIN-RESET-123"
}
```

**响应:**
```json
{
    "success": true,
    "message": "成功生成并保存 11 个邀请码",
    "codes": ["INV12345678", "INV87654321", ...]
}
```

### 2. 获取邀请码状态
**GET** `/api/invite-codes/status?admin_code=ADMIN-RESET-123`

**响应:**
```json
{
    "success": true,
    "message": "查询成功",
    "total": 76,
    "used": 2,
    "unused": 74
}
```

### 3. 验证邀请码
**POST** `/api/invite-codes/validate`

**请求体:**
```json
{
    "code": "INV12345678"
}
```

**响应:**
```json
{
    "valid": true,
    "message": "邀请码有效",
    "code_id": 123
}
```

### 4. 列出邀请码详情
**GET** `/api/invite-codes/list?admin_code=ADMIN-RESET-123&limit=10&offset=0`

**响应:**
```json
{
    "success": true,
    "total": 76,
    "used": 2,
    "unused": 74,
    "codes": [
        {
            "code": "INV12345678",
            "used_by": null,
            "used_at": null,
            "created_at": "2025-09-14 11:30:00"
        }
    ],
    "pagination": {
        "limit": 10,
        "offset": 0,
        "has_more": true
    }
}
```

## 使用方法

### 1. 直接调用生成器
```python
from invitation_code.generator import generate_and_save_codes

# 生成11个邀请码
result = generate_and_save_codes(11)
print(result)
```

### 2. 使用API接口
```bash
# 生成邀请码
curl -X POST "http://localhost:5001/api/invite-codes/generate" \
  -H "Content-Type: application/json" \
  -d '{"count": 11, "admin_code": "ADMIN-RESET-123"}'

# 查看状态
curl "http://localhost:5001/api/invite-codes/status?admin_code=ADMIN-RESET-123"

# 验证邀请码
curl -X POST "http://localhost:5001/api/invite-codes/validate" \
  -H "Content-Type: application/json" \
  -d '{"code": "INV12345678"}'
```

### 3. 运行测试
```bash
cd /home/ubuntu/timesheet/invitation_code
python3 test_api.py
```

## 邀请码格式

- 前缀: `INV` (固定)
- 后缀: 8位随机字符 (大写字母+数字)
- 总长度: 11位
- 示例: `INV12345678`, `INVABCDEFGH`

## 数据库表结构

```sql
CREATE TABLE invite_codes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(64) NOT NULL UNIQUE,
    used_by INT NULL,
    used_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 注意事项

1. 管理员验证码: `ADMIN-RESET-123`
2. 每个邀请码只能使用一次
3. 生成数量限制: 1-100个
4. 邀请码永久有效（无过期机制）
5. 需要管理员权限才能生成和查看邀请码
