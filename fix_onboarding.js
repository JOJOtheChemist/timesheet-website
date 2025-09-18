// 修复后的callAgent函数
async function callAgent(){
	// 先保存用户画像
	try {
		await saveUserProfile();
		console.log('用户画像保存成功');
	} catch (err) {
		console.error('保存用户画像失败:', err);
		// 继续执行，不阻止AI生成
	}
	
	const major = prMajor.value.trim();
	const goal = prGoal.value.trim();
	const projects = prProjects.value.trim();
	const token = await ensureToken();
	if(!token) { 
		throw new Error("无法获取认证令牌，请先注册或登录"); 
	}
	
	const message = [
		'你是智能项目管理助手，只负责子任务的识别、项目归属与增删改查。',
		'现在请"直接给出要创建的项目与子任务清单"，不要询问，不要犹豫。',
		'若用户未明确，也请根据常识与上下文进行合理补全，至少返回1个项目与若干子任务。',
		'请优先将以下资料解析为可创建的任务：',
		`- 专业：${major||'-'}`,
		`- 备考目标：${goal||'-'}`,
		`- 最近在做的项目：${projects||'-'}`,
		'输出格式：用简短条目列出【项目 -> 子任务】（可多项），必要时合并到更大项目（如"英语练习"、"金融考研专业课复习"等）。',
	].join('\n');
	
	const res = await fetchWithTimeout(`${API_BASE}/api/agent/chat`, { 
		method:'POST', 
		headers:{
			'Content-Type':'application/json', 
			...(token?{Authorization:`Bearer ${token}`}:{}) 
		}, 
		body: JSON.stringify({ message }) 
	}, 30000);
	
	const data = await res.json();
	if(!res.ok) throw new Error(data.detail||'生成失败');
	
	const tRaw = (data.thought||'').trim();
	const thought = tRaw && tRaw !== '无思考过程' ? `思考：${tRaw}\n` : '';
	let text = `${thought}${data.reply||'生成完成'}`;
	
	if (Array.isArray(data.tasks) && data.tasks.length){
		const byProj = {};
		for (const t of data.tasks){
			const pj = (t && t.project_name) || '未命名项目';
			if(!byProj[pj]) byProj[pj] = [];
			byProj[pj].push((t && t.subtask_name) || '未命名子任务');
		}
		text += '\n' + Object.keys(byProj).map(p=>`【${p}】\n- `+byProj[p].join('\n- ')).join('\n');
	}
	
	prResult.className='msg info';
	prResult.textContent=text;
	return true;
}
