"""
邀请码生成器模块
"""
import random
import string
import mysql.connector
from typing import List, Dict, Any
from datetime import datetime

# 数据库配置
DATABASE_CONFIG = {
    "host": "localhost",
    "user": "debian-sys-maint",
    "password": "36p2WFXFNmwuYvox",
    "database": "project_tasks",
    "ssl_disabled": True
}

class InviteCodeGenerator:
    """邀请码生成器"""
    
    def __init__(self):
        self.db_config = DATABASE_CONFIG
    
    def generate_single_code(self) -> str:
        """生成单个邀请码"""
        return 'INV' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def generate_codes(self, count: int) -> List[str]:
        """批量生成邀请码"""
        codes = []
        for _ in range(count):
            codes.append(self.generate_single_code())
        return codes
    
    def save_codes_to_db(self, codes: List[str]) -> Dict[str, Any]:
        """将邀请码保存到数据库"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 批量插入邀请码
            insert_data = [(code,) for code in codes]
            cursor.executemany("INSERT INTO invite_codes (code) VALUES (%s)", insert_data)
            
            conn.commit()
            return {
                "success": True,
                "message": f"成功生成并保存 {len(codes)} 个邀请码",
                "codes": codes
            }
        except mysql.connector.IntegrityError as e:
            return {
                "success": False,
                "message": f"部分邀请码已存在: {str(e)}",
                "codes": codes
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存失败: {str(e)}",
                "codes": codes
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def get_codes_status(self) -> Dict[str, Any]:
        """获取所有邀请码状态"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT code, used_by, used_at, created_at 
                FROM invite_codes 
                ORDER BY created_at DESC
            """)
            
            codes = cursor.fetchall()
            
            # 统计信息
            total = len(codes)
            used = len([c for c in codes if c['used_by'] is not None])
            unused = total - used
            
            return {
                "success": True,
                "total": total,
                "used": used,
                "unused": unused,
                "codes": codes
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"查询失败: {str(e)}"
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """验证邀请码是否有效"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT id, used_by, used_at FROM invite_codes WHERE code=%s", (code,))
            result = cursor.fetchone()
            
            if not result:
                return {
                    "valid": False,
                    "message": "邀请码不存在"
                }
            
            if result['used_by'] is not None:
                return {
                    "valid": False,
                    "message": "邀请码已被使用",
                    "used_by": result['used_by'],
                    "used_at": result['used_at']
                }
            
            return {
                "valid": True,
                "message": "邀请码有效",
                "code_id": result['id']
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"验证失败: {str(e)}"
            }
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

def generate_and_save_codes(count: int = 11) -> Dict[str, Any]:
    """生成并保存邀请码的便捷函数"""
    generator = InviteCodeGenerator()
    codes = generator.generate_codes(count)
    return generator.save_codes_to_db(codes)

if __name__ == "__main__":
    # 测试代码
    generator = InviteCodeGenerator()
    
    # 生成11个邀请码
    print("生成11个邀请码...")
    result = generate_and_save_codes(11)
    print(f"结果: {result}")
    
    # 查看状态
    print("\n查看邀请码状态...")
    status = generator.get_codes_status()
    print(f"状态: {status}")
