"""
邀请码管理API
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import mysql.connector
from .generator import InviteCodeGenerator

# 管理员验证码
ADMIN_CODE = "ADMIN-RESET-123"

router = APIRouter(prefix="/api/invite-codes", tags=["邀请码管理"])

class GenerateCodesRequest(BaseModel):
    count: int = 11
    admin_code: str

class ValidateCodeRequest(BaseModel):
    code: str

class InviteCodeResponse(BaseModel):
    success: bool
    message: str
    codes: Optional[List[str]] = None
    total: Optional[int] = None
    used: Optional[int] = None
    unused: Optional[int] = None

def verify_admin(admin_code: str):
    """验证管理员权限"""
    if admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="管理员验证码错误")

@router.post("/generate", response_model=InviteCodeResponse)
async def generate_invite_codes(request: GenerateCodesRequest):
    """生成邀请码"""
    verify_admin(request.admin_code)
    
    if request.count <= 0 or request.count > 100:
        raise HTTPException(status_code=400, detail="生成数量必须在1-100之间")
    
    generator = InviteCodeGenerator()
    codes = generator.generate_codes(request.count)
    result = generator.save_codes_to_db(codes)
    
    return InviteCodeResponse(
        success=result["success"],
        message=result["message"],
        codes=result.get("codes", [])
    )

@router.get("/status", response_model=InviteCodeResponse)
async def get_invite_codes_status(admin_code: str = Query(..., description="管理员验证码")):
    """获取邀请码状态"""
    verify_admin(admin_code)
    
    generator = InviteCodeGenerator()
    result = generator.get_codes_status()
    
    return InviteCodeResponse(
        success=result["success"],
        message=result.get("message", "查询成功"),
        total=result.get("total", 0),
        used=result.get("used", 0),
        unused=result.get("unused", 0)
    )

@router.post("/validate", response_model=Dict[str, Any])
async def validate_invite_code(request: ValidateCodeRequest):
    """验证邀请码"""
    generator = InviteCodeGenerator()
    result = generator.validate_code(request.code)
    
    return result

@router.get("/list", response_model=Dict[str, Any])
async def list_invite_codes(
    admin_code: str = Query(..., description="管理员验证码"),
    limit: int = Query(50, description="返回数量限制"),
    offset: int = Query(0, description="偏移量")
):
    """列出邀请码详情"""
    verify_admin(admin_code)
    
    generator = InviteCodeGenerator()
    result = generator.get_codes_status()
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    
    codes = result.get("codes", [])
    paginated_codes = codes[offset:offset + limit]
    
    return {
        "success": True,
        "total": result["total"],
        "used": result["used"],
        "unused": result["unused"],
        "codes": paginated_codes,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < result["total"]
        }
    }
