#!/usr/bin/env python3
"""
批量用户删除脚本 - 根据条件批量删除用户
"""

import mysql.connector
import sys
import argparse
from typing import List, Dict, Any
from delete_user import get_db_connection, get_user_info, delete_user_data

def get_users_by_criteria(criteria: str, value: str) -> List[Dict[str, Any]]:
    """根据条件获取用户列表"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if criteria == "username_pattern":
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE username LIKE %s", (f"%{value}%",))
        elif criteria == "created_after":
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE created_at > %s", (value,))
        elif criteria == "created_before":
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE created_at < %s", (value,))
        elif criteria == "no_profile":
            cursor.execute("""
                SELECT u.id, u.username, u.email, u.created_at 
                FROM users u 
                LEFT JOIN user_profiles up ON u.id = up.user_id 
                WHERE up.user_id IS NULL
            """)
        elif criteria == "test_users":
            cursor.execute("SELECT id, username, email, created_at FROM users WHERE username LIKE 'test%' OR username LIKE '%test%'")
        else:
            raise ValueError(f"不支持的条件: {criteria}")
        
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def main():
    parser = argparse.ArgumentParser(description='批量删除用户')
    parser.add_argument('--criteria', required=True, 
                       choices=['username_pattern', 'created_after', 'created_before', 'no_profile', 'test_users'],
                       help='删除条件')
    parser.add_argument('--value', help='条件值（某些条件不需要）')
    parser.add_argument('--dry-run', action='store_true', help='模拟删除，不实际删除数据')
    parser.add_argument('--force', action='store_true', help='强制删除，不显示确认提示')
    parser.add_argument('--limit', type=int, help='限制删除数量')
    
    args = parser.parse_args()
    
    print(f"🔍 根据条件 '{args.criteria}' 查找用户...")
    
    # 获取用户列表
    users = get_users_by_criteria(args.criteria, args.value or "")
    
    if not users:
        print("❌ 没有找到符合条件的用户")
        sys.exit(0)
    
    # 限制数量
    if args.limit and len(users) > args.limit:
        users = users[:args.limit]
        print(f"⚠️  限制删除数量为 {args.limit} 个用户")
    
    print(f"✅ 找到 {len(users)} 个符合条件的用户:")
    for user in users:
        print(f"   - {user['username']} (ID: {user['id']}, 创建时间: {user['created_at']})")
    
    # 确认删除
    if not args.force and not args.dry_run:
        print(f"\n⚠️  警告: 这将永久删除 {len(users)} 个用户及其所有相关数据!")
        confirm = input("确认删除? (输入 'DELETE' 确认): ")
        if confirm != 'DELETE':
            print("❌ 删除已取消")
            sys.exit(0)
    
    # 执行批量删除
    print(f"\n🗑️  开始批量删除 {len(users)} 个用户...")
    
    total_deleted = {
        'users': 0,
        'subtasks': 0,
        'projects': 0,
        'daily_schedule': 0,
        'user_profiles': 0,
        'invite_codes_reset': 0
    }
    
    for i, user in enumerate(users, 1):
        print(f"\n[{i}/{len(users)}] 删除用户: {user['username']}")
        try:
            deleted_counts = delete_user_data(user['id'], args.dry_run)
            for key in total_deleted:
                total_deleted[key] += deleted_counts[key]
            print(f"✅ 用户 {user['username']} 删除成功")
        except Exception as e:
            print(f"❌ 用户 {user['username']} 删除失败: {str(e)}")
    
    # 显示总结果
    print(f"\n📊 批量删除结果:")
    print(f"   用户: {total_deleted['users']} 个")
    print(f"   子任务: {total_deleted['subtasks']} 个")
    print(f"   项目: {total_deleted['projects']} 个")
    print(f"   日程安排: {total_deleted['daily_schedule']} 条")
    print(f"   用户画像: {total_deleted['user_profiles']} 条")
    print(f"   邀请码重置: {total_deleted['invite_codes_reset']} 个")
    
    if args.dry_run:
        print("\n🔍 这是模拟删除，实际数据未被删除")
    else:
        print(f"\n✅ 批量删除完成，共删除 {total_deleted['users']} 个用户")

if __name__ == "__main__":
    main()
