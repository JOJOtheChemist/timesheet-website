#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/ubuntu/langchain-agent')
os.environ['ZHIPUAI_API_KEY'] = 'ce85d782d3834f3982b87494dbd2a447.y8l8wxwEFafurRY2'

try:
    from agent_subtask_llm_simple import run_llm_agent
    print("LLM agent导入成功")
    
    result = run_llm_agent("我考研内容好多啊，就金融数学这个类别，我就需要刷题100道，背诵资料", user_id=1)
    print("LLM agent运行结果:")
    print(f"ok: {result.get('ok', False)}")
    print(f"reply: {result.get('reply', '')[:100]}...")
    print(f"task_created: {result.get('task_created', False)}")
    
except Exception as e:
    print(f"LLM agent测试失败: {e}")
    import traceback
    traceback.print_exc()
