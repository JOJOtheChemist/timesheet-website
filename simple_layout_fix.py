# 读取文件
with open('daily_schedule.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要修改的行
new_lines = []
for i, line in enumerate(lines):
    if '.container {' in line and 'display: flex;' in lines[i+1]:
        # 替换容器CSS
        new_lines.append('        .container {\n')
        new_lines.append('            display: flex;\n')
        new_lines.append('            flex-direction: column;\n')
        new_lines.append('            gap: 20px;\n')
        new_lines.append('            max-width: 1600px;\n')
        new_lines.append('            margin: 0 auto;\n')
        new_lines.append('            background: transparent;\n')
        new_lines.append('            border-radius: 15px;\n')
        new_lines.append('            box-shadow: 0 20px 40px rgba(0,0,0,0.1);\n')
        new_lines.append('            overflow: hidden;\n')
        new_lines.append('        }\n')
        # 跳过原来的容器CSS行
        j = i + 1
        while j < len(lines) and lines[j].strip() != '}':
            j += 1
        # 添加项目筛选区域CSS
        new_lines.append('\n')
        new_lines.append('        .project-filter-section {\n')
        new_lines.append('            background: rgba(17, 24, 39, 0.5);\n')
        new_lines.append('            padding: 20px;\n')
        new_lines.append('            border-radius: 15px;\n')
        new_lines.append('            border: 1px solid rgba(255,255,255,0.08);\n')
        new_lines.append('            height: 300px;\n')
        new_lines.append('            overflow-y: auto;\n')
        new_lines.append('            color: #E5E7EB;\n')
        new_lines.append('        }\n')
        new_lines.append('\n')
        new_lines.append('        .project-filter-section h2 {\n')
        new_lines.append('            color: #4f9cff;\n')
        new_lines.append('            margin-bottom: 15px;\n')
        new_lines.append('            font-size: 2rem;\n')
        new_lines.append('            border-bottom: 2px solid rgba(79, 156, 255, 0.5);\n')
        new_lines.append('            padding-bottom: 8px;\n')
        new_lines.append('            text-shadow: none;\n')
        new_lines.append('        }\n')
        new_lines.append('\n')
        # 跳过到main-content
        while j < len(lines) and '.main-content' not in lines[j]:
            j += 1
        new_lines.append(lines[j])
        i = j
    elif '.sidebar' in line:
        # 跳过sidebar相关CSS
        while i < len(lines) and lines[i].strip() != '}':
            i += 1
    elif '<div class="project-component">' in line:
        # 在项目组件前添加包装
        new_lines.append('        <!-- 项目筛选组件 - 固定高度在上方 -->\n')
        new_lines.append('        <div class="project-filter-section">\n')
        new_lines.append(line)
    elif '<!-- 心情快捷输入独立区域 -->' in line:
        # 在心情快捷输入前添加闭合标签
        new_lines.append('        </div>\n')
        new_lines.append('\n')
        new_lines.append(line)
    else:
        new_lines.append(line)
    i += 1

# 写回文件
with open('daily_schedule.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('布局修改完成')
