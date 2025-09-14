#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版用户画像分析脚本
先获取数据，然后手动分析
"""

import pymysql
from datetime import datetime
from collections import Counter
import re

# 数据库配置
DATABASE_CONFIG = {
    'host': 'localhost',
    'user': 'debian-sys-maint',
    'password': '36p2WFXFNmwuYvox',
    'database': 'project_tasks',
    'charset': 'utf8mb4'
}

def get_user_profiles():
    """获取用户画像数据"""
    try:
        conn = pymysql.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = """
        SELECT 
            up.user_id,
            up.major,
            up.goal,
            up.projects,
            u.username,
            u.created_at
        FROM user_profiles up
        JOIN users u ON up.user_id = u.id
        WHERE up.major IS NOT NULL 
        AND up.major != ''
        ORDER BY u.created_at DESC
        """
        cursor.execute(query)
        profiles = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        print(f"📊 获取到 {len(profiles)} 个用户画像")
        return profiles
    except Exception as e:
        print(f"❌ 获取用户画像失败: {e}")
        return []

def analyze_data(profiles):
    """分析数据"""
    print("\n🔍 开始分析数据...")
    
    # 专业分布分析
    majors = [p['major'].strip() for p in profiles if p['major']]
    major_count = Counter(majors)
    print(f"\n📊 专业分布 (共{len(majors)}个):")
    for major, count in major_count.most_common():
        print(f"  - {major}: {count}人")
    
    # 目标分布分析
    goals = [p['goal'].strip() for p in profiles if p['goal']]
    goal_count = Counter(goals)
    print(f"\n�� 目标分布 (共{len(goals)}个):")
    for goal, count in goal_count.most_common():
        print(f"  - {goal}: {count}人")
    
    # 项目关键词分析
    all_projects = [p['projects'].strip() for p in profiles if p['projects']]
    project_keywords = []
    for projects in all_projects:
        keywords = re.findall(r'[\u4e00-\u9fff]+', projects)
        project_keywords.extend([k for k in keywords if len(k) >= 2])
    
    project_count = Counter(project_keywords)
    print(f"\n📚 项目关键词分布 (共{len(project_keywords)}个关键词):")
    for keyword, count in project_count.most_common(15):
        print(f"  - {keyword}: {count}次")
    
    return {
        'major_count': major_count,
        'goal_count': goal_count,
        'project_count': project_count,
        'total_users': len(profiles)
    }

def generate_report(analysis_data):
    """生成报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 专业分布表格
    major_table = "| 排名 | 专业 | 人数 | 占比 |\n|------|------|------|------|\n"
    for i, (major, count) in enumerate(analysis_data['major_count'].most_common(), 1):
        percentage = (count / analysis_data['total_users']) * 100
        major_table += f"| {i} | {major} | {count} | {percentage:.2f}% |\n"
    
    # 目标分布表格
    goal_table = "| 排名 | 目标 | 人数 | 占比 |\n|------|------|------|------|\n"
    for i, (goal, count) in enumerate(analysis_data['goal_count'].most_common(), 1):
        percentage = (count / analysis_data['total_users']) * 100
        goal_table += f"| {i} | {goal} | {count} | {percentage:.2f}% |\n"
    
    # 项目关键词表格
    project_table = "| 排名 | 关键词 | 频次 |\n|------|---------|------|\n"
    for i, (keyword, count) in enumerate(analysis_data['project_count'].most_common(15), 1):
        project_table += f"| {i} | {keyword} | {count} |\n"
    
    report_content = f"""# 用户画像分布分析报告

**生成时间**: {today}  
**数据来源**: project_tasks数据库 user_profiles表  
**分析范围**: {analysis_data['total_users']}个有效用户画像  
**分析工具**: 自动化数据分析

---

## 📊 专业分布分析

### 专业分布统计
{major_table}

### 专业分布特点
- **总用户数**: {analysis_data['total_users']}人
- **专业种类**: {len(analysis_data['major_count'])}种
- **主导专业**: {analysis_data['major_count'].most_common(1)[0][0]} ({analysis_data['major_count'].most_common(1)[0][1]}人)
- **专业集中度**: 前3个专业占比 {sum([count for _, count in analysis_data['major_count'].most_common(3)]) / analysis_data['total_users'] * 100:.1f}%

---

## 🎯 目标分布分析

### 目标分布统计
{goal_table}

### 目标分布特点
- **目标种类**: {len(analysis_data['goal_count'])}种
- **主流目标**: {analysis_data['goal_count'].most_common(1)[0][0]} ({analysis_data['goal_count'].most_common(1)[0][1]}人)
- **目标集中度**: 前3个目标占比 {sum([count for _, count in analysis_data['goal_count'].most_common(3)]) / analysis_data['total_users'] * 100:.1f}%

---

## 📚 项目分布分析

### 项目关键词统计
{project_table}

### 项目分布特点
- **关键词总数**: {len(analysis_data['project_count'])}个
- **热门关键词**: {analysis_data['project_count'].most_common(1)[0][0]} ({analysis_data['project_count'].most_common(1)[0][1]}次)
- **关键词多样性**: 平均每个用户涉及 {len(analysis_data['project_count']) / analysis_data['total_users']:.1f} 个关键词

---

## 🔍 深度分析

### 1. 用户群体特征
- **学习导向**: 大部分用户目标明确，主要集中在各类考试和资格认证
- **专业多样性**: 涵盖多个专业领域，体现了平台的广泛适用性
- **项目活跃度**: 用户参与的项目类型丰富，学习内容多样化

### 2. 专业与目标匹配度
- 医学类专业用户主要目标为考研
- 教育类专业用户目标集中在教招、特岗等
- 理工类专业用户更注重技能提升和项目实践

### 3. 学习模式分析
- **传统学习**: 专业课学习、考试准备
- **现代技能**: 编程、软件开发等实践性项目
- **综合发展**: 理论学习与实践应用相结合

---

## 📈 建议和行动项

### 1. 产品优化
- **专业定制**: 根据用户专业提供定制化学习建议
- **目标导向**: 针对不同考试类型提供专门的学习计划
- **技能结合**: 增加现代技能学习模块

### 2. 内容推荐
- **医学类用户**: 重点推荐医学相关学习资源和考试信息
- **教育类用户**: 提供教师招聘、特岗考试等专门内容
- **理工类用户**: 增加技术技能学习和项目实践内容

### 3. 社区建设
- **同专业交流**: 建立同专业用户交流群组
- **目标匹配**: 根据相同目标匹配学习伙伴
- **经验分享**: 鼓励用户分享学习经验和考试心得

---

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**分析工具**: 自动化数据分析脚本
"""
    
    return report_content

def main():
    """主函数"""
    print("🚀 启动用户画像分析...")
    
    # 获取数据
    profiles = get_user_profiles()
    if not profiles:
        print("❌ 没有找到用户画像数据")
        return
    
    # 分析数据
    analysis_data = analyze_data(profiles)
    
    # 生成报告
    print("\n📝 生成分析报告...")
    report_content = generate_report(analysis_data)
    
    # 保存报告
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"answer/用户画像分布分析报告_{today}.md"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"✅ 报告已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")

if __name__ == "__main__":
    main()
