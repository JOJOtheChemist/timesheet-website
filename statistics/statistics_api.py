#!/usr/bin/env python3
"""
统计API服务器
提供统计数据接口
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os

# 添加backend/sqlalchemy到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'sqlalchemy'))

from statistics_service import stats_service

app = FastAPI(title="Statistics API", version="1.0.0")

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "statistics"}

@app.get("/api/statistics")
def get_statistics(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)")
):
    """获取统计数据"""
    try:
        # 验证日期格式
        from datetime import datetime
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
        
        # 获取统计数据
        statistics = stats_service.calculate_statistics(start_date, end_date)
        
        return {
            "status": "success",
            "data": statistics,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@app.get("/api/statistics/projects")
def get_project_statistics():
    """获取项目统计"""
    try:
        project_stats = stats_service.get_project_analysis()
        return {
            "status": "success",
            "data": project_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目统计失败: {str(e)}")

@app.get("/api/statistics/categories")
def get_category_statistics():
    """获取分类统计"""
    try:
        category_stats = stats_service.get_category_analysis()
        return {
            "status": "success",
            "data": category_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类统计失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)
