import re

# 读取文件
with open('daily_schedule.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改容器布局为上下结构
container_pattern = r'(\s+\.container\s*\{[^}]*\})'
container_replacement = '''        .container {
            display: flex;
            flex-direction: column;
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
            background: transparent;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }'''

content = re.sub(container_pattern, container_replacement, content, flags=re.DOTALL)

# 2. 添加项目筛选区域CSS
project_filter_css = '''        .project-filter-section {
            background: rgba(17, 24, 39, 0.5);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.08);
            height: 300px;
            overflow-y: auto;
            color: #E5E7EB;
        }

        .project-filter-section h2 {
            color: #4f9cff;
            margin-bottom: 15px;
            font-size: 2rem;
            border-bottom: 2px solid rgba(79, 156, 255, 0.5);
            padding-bottom: 8px;
            text-shadow: none;
        }'''

# 在main-content之前插入项目筛选CSS
content = content.replace('        .main-content {', project_filter_css + '\n\n        .main-content {')

# 3. 删除sidebar相关CSS
content = re.sub(r'        \.sidebar[^}]*\{[^}]*\}', '', content, flags=re.DOTALL)
content = re.sub(r'        \.sidebar h2[^}]*\{[^}]*\}', '', content, flags=re.DOTALL)

# 4. 修改HTML结构 - 将项目组件包装在project-filter-section中
# 找到项目组件的开始和结束位置
project_start = content.find('<div class="project-component">')
mood_start = content.find('<div class="mood-quick-input-section"')

if project_start != -1 and mood_start != -1:
    # 提取项目组件内容
    project_content = content[project_start:mood_start]
    
    # 包装在project-filter-section中
    new_project_section = '''        <!-- 项目筛选组件 - 固定高度在上方 -->
        <div class="project-filter-section">''' + project_content + '''        </div>

        <!-- 心情快捷输入独立区域 -->'''
    
    # 替换原内容
    content = content[:project_start] + new_project_section + content[mood_start:]

# 写回文件
with open('daily_schedule.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('布局修改完成')
