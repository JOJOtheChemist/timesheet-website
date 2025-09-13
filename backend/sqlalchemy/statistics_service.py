"""
统计服务模块
处理时间统计和分析逻辑
"""
import sqlite3
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
import json

class StatisticsService:
    def __init__(self, db_path: str = "/home/ubuntu/timesheet/timesheet.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def get_schedule_data(self, start_date: str, end_date: str) -> List[Dict]:
        """获取指定日期范围的日程数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT s.*, 
               p.name as project_name, p.color as project_color,
               st.name as subtask_name, st.urgency_importance, st.difficulty
        FROM schedules s
        LEFT JOIN subtasks st ON s.planned_subtask_id = st.id OR s.actual_subtask_id = st.id
        LEFT JOIN projects p ON st.project_id = p.id
        WHERE s.schedule_date BETWEEN ? AND ?
        ORDER BY s.schedule_date, s.time_slot
        """
        
        cursor.execute(query, (start_date, end_date))
        columns = [description[0] for description in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            record = dict(zip(columns, row))
            results.append(record)
        
        conn.close()
        return results
    
    def calculate_time_slot_hours(self, time_slot: str) -> float:
        """计算时间段的小时数"""
        if not time_slot:
            return 0
        
        # 处理不同的时间格式
        if '-' in time_slot:
            # 格式: "14:00-17:00" 或 "22:00-01:30"
            parts = time_slot.split('-')
            if len(parts) != 2:
                return 0
            
            start_time = self.parse_time(parts[0])
            end_time = self.parse_time(parts[1])
            
            if start_time is None or end_time is None:
                return 0
            
            # 处理跨天情况
            if end_time < start_time:
                end_time += 24
            
            return end_time - start_time
        else:
            # 格式: "14:00" (单点时间，假设1小时)
            return 1.0
    
    def parse_time(self, time_str: str) -> Optional[float]:
        """解析时间字符串为小数小时"""
        try:
            parts = time_str.strip().split(':')
            if len(parts) != 2:
                return None
            
            hours = int(parts[0])
            minutes = int(parts[1])
            
            return hours + minutes / 60.0
        except (ValueError, IndexError):
            return None
    
    def extract_start_hour(self, time_slot: str) -> Optional[int]:
        """提取时间段的开始小时"""
        if not time_slot:
            return None
        
        if '-' in time_slot:
            start_time_str = time_slot.split('-')[0]
        else:
            start_time_str = time_slot
        
        start_time = self.parse_time(start_time_str)
        return int(start_time) if start_time is not None else None
    
    def calculate_statistics(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """计算统计数据"""
        schedule_data = self.get_schedule_data(start_date, end_date)
        
        # 基础统计
        total_hours = 0
        completed_tasks = 0
        hourly_activity = {i: 0 for i in range(24)}
        project_stats = {}
        daily_hours = {}
        planned_tasks = 0
        actual_tasks = 0
        
        for record in schedule_data:
            # 计算工作时长
            hours = self.calculate_time_slot_hours(record['time_slot'])
            total_hours += hours
            
            # 统计任务
            if record['planned_subtask_id']:
                planned_tasks += 1
            if record['actual_subtask_id']:
                actual_tasks += 1
                completed_tasks += 1
            
            # 小时活动统计
            start_hour = self.extract_start_hour(record['time_slot'])
            if start_hour is not None:
                hourly_activity[start_hour] += 1
            
            # 项目统计
            project_name = record['project_name'] or '其他'
            if project_name not in project_stats:
                project_stats[project_name] = 0
            project_stats[project_name] += hours
            
            # 每日统计
            schedule_date = record['schedule_date']
            if schedule_date not in daily_hours:
                daily_hours[schedule_date] = 0
            daily_hours[schedule_date] += hours
        
        # 计算效率
        efficiency = (actual_tasks / planned_tasks * 100) if planned_tasks > 0 else 0
        
        # 找到最活跃时段
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1])[0] if any(hourly_activity.values()) else 0
        peak_hours = f"{peak_hour:02d}:00-{(peak_hour + 2) % 24:02d}:00"
        
        # 准备每日活动数据
        daily_activity = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        while current_date <= end_date_obj:
            date_str = current_date.strftime("%Y-%m-%d")
            hours = daily_hours.get(date_str, 0)
            daily_activity.append({
                "date": date_str,
                "hours": hours
            })
            current_date += timedelta(days=1)
        
        return {
            "total_hours": round(total_hours, 1),
            "completed_tasks": completed_tasks,
            "avg_efficiency": round(efficiency, 1),
            "peak_hours": peak_hours,
            "time_distribution": project_stats,
            "daily_activity": daily_activity,
            "hourly_activity": hourly_activity,
            "project_analysis": project_stats,
            "raw_data": schedule_data
        }
    
    def get_project_analysis(self) -> Dict[str, Any]:
        """获取项目分析数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT p.name, p.color, COUNT(s.id) as task_count,
               SUM(CASE WHEN s.planned_subtask_id IS NOT NULL THEN 1 ELSE 0 END) as planned_count,
               SUM(CASE WHEN s.actual_subtask_id IS NOT NULL THEN 1 ELSE 0 END) as actual_count
        FROM projects p
        LEFT JOIN subtasks st ON p.id = st.project_id
        LEFT JOIN schedules s ON st.id = s.planned_subtask_id OR st.id = s.actual_subtask_id
        GROUP BY p.id, p.name, p.color
        ORDER BY task_count DESC
        """
        
        cursor.execute(query)
        results = []
        
        for row in cursor.fetchall():
            results.append({
                "name": row[0],
                "color": row[1],
                "task_count": row[2],
                "planned_count": row[3],
                "actual_count": row[4]
            })
        
        conn.close()
        return {"projects": results}
    
    def get_category_analysis(self) -> Dict[str, Any]:
        """获取分类分析数据"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT c.name, c.color, COUNT(s.id) as task_count
        FROM categories c
        LEFT JOIN projects p ON c.id = p.category_id
        LEFT JOIN subtasks st ON p.id = st.project_id
        LEFT JOIN schedules s ON st.id = s.planned_subtask_id OR st.id = s.actual_subtask_id
        GROUP BY c.id, c.name, c.color
        ORDER BY task_count DESC
        """
        
        cursor.execute(query)
        results = []
        
        for row in cursor.fetchall():
            results.append({
                "name": row[0],
                "color": row[1],
                "task_count": row[2]
            })
        
        conn.close()
        return {"categories": results}

# 创建全局实例
stats_service = StatisticsService()
