# 用户删除工具

这个工具包提供了完整的用户删除功能，确保删除用户时所有相关数据都被彻底清理。

## 功能特点

- ✅ 彻底删除用户及其所有相关数据
- ✅ 支持事务处理，确保数据一致性
- ✅ 支持模拟删除模式，安全预览
- ✅ 支持单个用户删除和批量删除
- ✅ 提供API端点集成到FastAPI
- ✅ 详细的删除统计和日志

## 删除的数据类型

1. **用户账户** (users表)
2. **用户画像** (user_profiles表)
3. **项目** (projects表)
4. **子任务** (subtasks表)
5. **日程安排** (daily_schedule表)
6. **邀请码使用记录** (invite_codes表，重置为未使用状态)

## 使用方法

### 1. 单个用户删除

```bash
# 按用户名删除
python3 user_delete/delete_user.py username

# 按用户ID删除
python3 user_delete/delete_user.py 123

# 模拟删除（不实际删除数据）
python3 user_delete/delete_user.py username --dry-run

# 强制删除（不显示确认提示）
python3 user_delete/delete_user.py username --force
```

### 2. 批量用户删除

```bash
# 删除所有测试用户
python3 user_delete/batch_delete_users.py --criteria test_users

# 删除用户名包含特定字符的用户
python3 user_delete/batch_delete_users.py --criteria username_pattern --value test

# 删除没有用户画像的用户
python3 user_delete/batch_delete_users.py --criteria no_profile

# 删除指定日期后创建的用户
python3 user_delete/batch_delete_users.py --criteria created_after --value "2025-09-14 20:00:00"

# 限制删除数量
python3 user_delete/batch_delete_users.py --criteria test_users --limit 5

# 模拟删除
python3 user_delete/batch_delete_users.py --criteria test_users --dry-run
```

### 3. API端点使用

```python
# 获取用户信息
GET /api/admin/user-info/{user_identifier}

# 删除用户
DELETE /api/admin/delete-user
{
    "user_identifier": "username",
    "force": false
}
```

## 安全特性

1. **事务处理**: 所有删除操作都在事务中进行，确保数据一致性
2. **外键约束处理**: 按正确顺序删除数据，避免外键约束错误
3. **模拟模式**: 支持dry-run模式，安全预览删除操作
4. **确认机制**: 默认需要用户确认，防止误删
5. **详细日志**: 提供详细的删除统计和错误信息

## 删除顺序

为确保外键约束正确，删除顺序如下：

1. 子任务 (subtasks) - 依赖项目
2. 项目 (projects) - 依赖用户
3. 日程安排 (daily_schedule) - 依赖用户
4. 用户画像 (user_profiles) - 依赖用户
5. 邀请码使用记录 (invite_codes) - 重置为未使用
6. 用户 (users) - 最后删除

## 注意事项

⚠️ **警告**: 删除操作不可逆，请谨慎使用！

- 删除前请确保已备份重要数据
- 建议先使用 `--dry-run` 模式预览删除操作
- 批量删除时建议先测试少量用户
- 生产环境使用前请充分测试

## 示例

### 删除测试用户
```bash
# 查看所有测试用户
python3 user_delete/batch_delete_users.py --criteria test_users --dry-run

# 删除所有测试用户
python3 user_delete/batch_delete_users.py --criteria test_users --force
```

### 清理无画像用户
```bash
# 查看没有用户画像的用户
python3 user_delete/batch_delete_users.py --criteria no_profile --dry-run

# 删除没有用户画像的用户
python3 user_delete/batch_delete_users.py --criteria no_profile --force
```

## 错误处理

- 如果删除过程中出现错误，所有操作会自动回滚
- 详细的错误信息会显示在控制台
- API端点会返回适当的HTTP状态码和错误信息
