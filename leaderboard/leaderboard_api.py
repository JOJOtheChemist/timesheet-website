from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import mysql.connector
import json

app = FastAPI(title="Leaderboard API", version="1.0.0")

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12356790zZ_',
    'database': 'project_tasks',
    'charset': 'utf8mb4',
    'ssl_disabled': True
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

class LeaderboardResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: Optional[str] = None

def get_date_range(period: str) -> tuple:
    """获取指定周期的时间范围"""
    now = datetime.now()
    
    if period == 'daily':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    elif period == 'weekly':
        # 获取本周一
        days_since_monday = now.weekday()
        start_date = now - timedelta(days=days_since_monday)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    elif period == 'monthly':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end_date = now.replace(year=now.year + 1, month=1, day=1) - timedelta(microseconds=1)
        else:
            end_date = now.replace(month=now.month + 1, day=1) - timedelta(microseconds=1)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    elif period == 'yearly':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    
    else:
        raise ValueError(f"Invalid period: {period}")

def get_leaderboard_data(period: str, custom_start_date: str = None, custom_end_date: str = None) -> Dict[str, Any]:
    """获取排行榜数据"""
    try:
        if custom_start_date and custom_end_date:
            start_date, end_date = custom_start_date, custom_end_date
        else:
            start_date, end_date = get_date_range(period)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 查询用户时间统计数据 - 修复时间计算逻辑
        # 每个time_slot记录代表30分钟时间段
        query = """
        SELECT 
            ds.user_id,
            u.username as user_name,
            COUNT(DISTINCT ds.schedule_date) as active_days,
            COUNT(ds.id) as total_records,
            COUNT(ds.id) * 0.5 as total_hours,
            COUNT(DISTINCT COALESCE(ds.actual_subtask_name, ds.planned_subtask_name)) as unique_tasks
        FROM daily_schedule ds
        LEFT JOIN users u ON ds.user_id = u.id
        WHERE ds.schedule_date BETWEEN %s AND %s
        AND (ds.planned_subtask_name IS NOT NULL AND ds.planned_subtask_name != '' 
             OR ds.actual_subtask_name IS NOT NULL AND ds.actual_subtask_name != '')
        GROUP BY ds.user_id, u.username
        HAVING total_hours > 0
        ORDER BY total_hours DESC
        LIMIT 50
        """
        
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()
        
        # 处理数据
        rankings = []
        total_hours = 0
        total_users = len(results)
        
        for i, row in enumerate(results):
            user_hours = float(row['total_hours']) if row['total_hours'] else 0
            total_hours += user_hours
            
            # 计算效率评级
            efficiency = "High" if user_hours >= 8 else ("Medium" if user_hours >= 4 else "Low")
            
            rankings.append({
                'rank': i + 1,
                'user_id': row['user_id'],
                'name': row['user_name'] or f"User_{row['user_id']}",
                'total_hours': round(user_hours, 1),
                'active_days': row['active_days'],
                'tasks_completed': row['total_records'],
                'unique_tasks': row['unique_tasks'],
                'efficiency': efficiency
            })
        
        # 计算统计摘要
        avg_hours = round(total_hours / total_users, 1) if total_users > 0 else 0
        top_hours = round(rankings[0]['total_hours'], 1) if rankings else 0
        
        # 生成周期信息
        period_info = get_period_info(period, start_date, end_date)
        
        cursor.close()
        conn.close()
        
        return {
            'rankings': rankings,
            'summary': {
                'total_users': total_users,
                'total_hours': round(total_hours, 1),
                'avg_hours': avg_hours,
                'top_hours': top_hours
            },
            'period_info': period_info,
            'period': period,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
    except Exception as e:
        print(f"Error getting leaderboard data: {str(e)}")
        return {
            'rankings': [],
            'summary': {
                'total_users': 0,
                'total_hours': 0,
                'avg_hours': 0,
                'top_hours': 0
            },
            'period_info': f"Error: {str(e)}",
            'period': period,
            'date_range': {
                'start_date': '',
                'end_date': ''
            }
        }

def get_period_info(period: str, start_date: str, end_date: str) -> str:
    """生成周期信息描述"""
    now = datetime.now()
    
    if period == 'daily':
        return f"Today ({now.strftime('%Y-%m-%d')})"
    elif period == 'weekly':
        return f"This Week ({start_date} to {end_date})"
    elif period == 'monthly':
        return f"This Month ({now.strftime('%B %Y')})"
    elif period == 'yearly':
        return f"This Year ({now.year})"
    else:
        return f"{start_date} to {end_date}"

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "leaderboard"}

@app.get("/api/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    period: str = Query(..., description="Time period: daily, weekly, monthly, yearly"),
    start_date: str = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Custom end date (YYYY-MM-DD)")
):
    """获取排行榜数据"""
    try:
        if period not in ['daily', 'weekly', 'monthly', 'yearly']:
            raise HTTPException(
                status_code=400, 
                detail="Invalid period. Must be one of: daily, weekly, monthly, yearly"
            )
        
        data = get_leaderboard_data(period, start_date, end_date)
        
        return LeaderboardResponse(
            success=True,
            data=data,
            message=f"Successfully retrieved {period} leaderboard"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get leaderboard data: {str(e)}"
        )

@app.get("/api/leaderboard/demo")
def get_demo_leaderboard():
    """获取演示数据 - 使用历史数据"""
    try:
        # 使用8月8日到8月16日的数据作为演示
        data = get_leaderboard_data('demo', '2025-08-08', '2025-08-16')
        
        return {
            "success": True,
            "data": data,
            "message": "Demo leaderboard with historical data"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get demo leaderboard: {str(e)}"
        )

@app.get("/api/leaderboard/stats")
def get_leaderboard_stats():
    """获取排行榜统计信息"""
    try:
        stats = {}
        
        for period in ['daily', 'weekly', 'monthly', 'yearly']:
            data = get_leaderboard_data(period)
            stats[period] = {
                'total_users': data['summary']['total_users'],
                'total_hours': data['summary']['total_hours'],
                'top_user': data['rankings'][0]['name'] if data['rankings'] else None,
                'top_hours': data['rankings'][0]['total_hours'] if data['rankings'] else 0
            }
        
        return {
            "success": True,
            "data": stats,
            "message": "Successfully retrieved leaderboard statistics"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get leaderboard statistics: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5007)
