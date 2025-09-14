#!/usr/bin/env python3
"""
用户删除脚本 - 彻底删除用户及其所有相关数据
包括：用户画像、项目、子任务、日程安排、邀请码使用记录等
"""

import mysql.connector
import sys
import argparse
from typing import List, Dict, Any

# 数据库配置
DATABASE_CONFIG = {
    "host": "localhost",
    "user": "debian-sys-maint",
    "password": "36p2WFXFNmwuYvox",
    "database": "project_tasks",
    "ssl_disabled": True
}

def get_db_connection():
    """获取数据库连接"""
    return mysql.connector.connect(**DATABASE_CONFIG)

def get_user_info(user_identifier: str) -> Dict[str, Any]:
    """根据用户名或ID获取用户信息"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 尝试按ID查找
        if user_identifier.isdigit():
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = %s", (int(user_identifier),))
        else:
            # 按用户名查找
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE username = %s", (user_identifier,))
        
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        conn.close()

def get_user_related_data(user_id: int) -> Dict[str, List]:
    """获取用户的所有相关数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        data = {
            'user_profiles': [],
            'projects': [],
            'subtasks': [],
            'daily_schedule': [],
            'invite_codes': []
        }
        
        # 用户画像
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = %s", (user_id,))
        data['user_profiles'] = cursor.fetchall()
        
        # 项目
        cursor.execute("SELECT * FROM projects WHERE user_id = %s", (user_id,))
        data['projects'] = cursor.fetchall()
        
        # 子任务
        cursor.execute("SELECT * FROM subtasks WHERE user_id = %s", (user_id,))
        data['subtasks'] = cursor.fetchall()
        
        # 日程安排
        cursor.execute("SELECT * FROM daily_schedule WHERE user_id = %s", (user_id,))
        data['daily_schedule'] = cursor.fetchall()
        
        # 邀请码使用记录
        cursor.execute("SELECT * FROM invite_codes WHERE used_by = %s", (user_id,))
        data['invite_codes'] = cursor.fetchall()
        
        return data
    finally:
        cursor.close()
        conn.close()

def delete_user_data(user_id: int, dry_run: bool = False) -> Dict[str, int]:
    """删除用户的所有相关数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        deleted_counts = {
            'subtasks': 0,
            'projects': 0,
            'daily_schedule': 0,
            'user_profiles': 0,
            'invite_codes_reset': 0,
            'users': 0
        }
        
        if dry_run:
            print("🔍 模拟删除模式 - 不会实际删除数据")
            return deleted_counts
        
        # 开始事务
        conn.start_transaction()
        
        # 1. 删除子任务（有外键约束，需要先删除）
        cursor.execute("DELETE FROM subtasks WHERE user_id = %s", (user_id,))
        deleted_counts['subtasks'] = cursor.rowcount
        
        # 2. 删除项目
        cursor.execute("DELETE FROM projects WHERE user_id = %s", (user_id,))
        deleted_counts['projects'] = cursor.rowcount
        
        # 3. 删除日程安排
        cursor.execute("DELETE FROM daily_schedule WHERE user_id = %s", (user_id,))
        deleted_counts['daily_schedule'] = cursor.rowcount
        
        # 4. 删除用户画像
        cursor.execute("DELETE FROM user_profiles WHERE user_id = %s", (user_id,))
        deleted_counts['user_profiles'] = cursor.rowcount
        
        # 5. 重置邀请码使用记录（将邀请码标记为未使用）
        cursor.execute("UPDATE invite_codes SET used_by = NULL, used_at = NULL WHERE used_by = %s", (user_id,))
        deleted_counts['invite_codes_reset'] = cursor.rowcount
        
        # 6. 最后删除用户
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        deleted_counts['users'] = cursor.rowcount
        
        # 提交事务
        conn.commit()
        print("✅ 用户数据删除成功")
        
        return deleted_counts
        
    except Exception as e:
        # 回滚事务
        conn.rollback()
        print(f"❌ 删除失败: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='彻底删除用户及其所有相关数据')
    parser.add_argument('user_identifier', help='用户名或用户ID')
    parser.add_argument('--dry-run', action='store_true', help='模拟删除，不实际删除数据')
    parser.add_argument('--force', action='store_true', help='强制删除，不显示确认提示')
    
    args = parser.parse_args()
    
    print(f"🔍 查找用户: {args.user_identifier}")
    
    # 获取用户信息
    user = get_user_info(args.user_identifier)
    if not user:
        print(f"❌ 用户 '{args.user_identifier}' 不存在")
        sys.exit(1)
    
    print(f"✅ 找到用户: {user['username']} (ID: {user['id']})")
    print(f"   邮箱: {user['email'] or '无'}")
    print(f"   创建时间: {user['created_at']}")
    
    # 获取相关数据
    print("\n🔍 检查相关数据...")
    related_data = get_user_related_data(user['id'])
    
    # 显示数据统计
    print("\n📊 相关数据统计:")
    print(f"   用户画像: {len(related_data['user_profiles'])} 条")
    print(f"   项目: {len(related_data['projects'])} 个")
    print(f"   子任务: {len(related_data['subtasks'])} 个")
    print(f"   日程安排: {len(related_data['daily_schedule'])} 条")
    print(f"   使用的邀请码: {len(related_data['invite_codes'])} 个")
    
    # 显示详细信息
    if related_data['projects']:
        print("\n📁 项目列表:")
        for project in related_data['projects']:
            print(f"   - {project['name']} (ID: {project['id']})")
    
    if related_data['subtasks']:
        print("\n📋 子任务列表:")
        for subtask in related_data['subtasks']:
            print(f"   - {subtask['name']} (ID: {subtask['id']})")
    
    if related_data['invite_codes']:
        print("\n🎫 使用的邀请码:")
        for invite in related_data['invite_codes']:
            print(f"   - {invite['code']} (使用时间: {invite['used_at']})")
    
    # 确认删除
    if not args.force and not args.dry_run:
        print(f"\n⚠️  警告: 这将永久删除用户 '{user['username']}' 及其所有相关数据!")
        confirm = input("确认删除? (输入 'DELETE' 确认): ")
        if confirm != 'DELETE':
            print("❌ 删除已取消")
            sys.exit(0)
    
    # 执行删除
    print(f"\n🗑️  开始删除用户 '{user['username']}' 的数据...")
    deleted_counts = delete_user_data(user['id'], args.dry_run)
    
    # 显示删除结果
    print("\n📊 删除结果:")
    print(f"   子任务: {deleted_counts['subtasks']} 个")
    print(f"   项目: {deleted_counts['projects']} 个")
    print(f"   日程安排: {deleted_counts['daily_schedule']} 条")
    print(f"   用户画像: {deleted_counts['user_profiles']} 条")
    print(f"   邀请码重置: {deleted_counts['invite_codes_reset']} 个")
    print(f"   用户: {deleted_counts['users']} 个")
    
    if args.dry_run:
        print("\n🔍 这是模拟删除，实际数据未被删除")
    else:
        print(f"\n✅ 用户 '{user['username']}' 及其所有相关数据已彻底删除")

if __name__ == "__main__":
    main()
