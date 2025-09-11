(function(){
	class AuthModal extends HTMLElement {
		constructor(){
			super();
			this.attachShadow({ mode: 'open' });
			this.tokenKey = 'ts_auth_token';
			this.apiBase = '/api/auth';
		}
		connectedCallback(){
			this.render();
			this.bindEvents();
			// 不再自动打开，由外部按钮触发
			// 暴露全局工具
			window.tsAuth = {
				getToken: () => localStorage.getItem(this.tokenKey),
				logout: () => { localStorage.removeItem(this.tokenKey); location.reload(); },
				fetch: (url, options={}) => {
					const token = localStorage.getItem(this.tokenKey);
					const headers = Object.assign({}, options.headers || {});
					if (token) headers['Authorization'] = 'Bearer ' + token;
					return fetch(url, Object.assign({}, options, { headers }));
				},
				openLogin: () => this.open()
			};
		}
		open(){ this.shadowRoot.querySelector('#overlay').style.display = 'flex'; }
		close(){ this.shadowRoot.querySelector('#overlay').style.display = 'none'; }
		setLoading(loading){
			this.shadowRoot.querySelectorAll('#submitBtn').forEach(btn=>{ btn.disabled = !!loading; btn.textContent = loading ? '处理中...' : '提交'; });
		}
		showTab(tab){
			this.shadowRoot.querySelectorAll('[data-tab]').forEach(el => el.classList.add('hidden'));
			this.shadowRoot.querySelector(`[data-tab="${tab}"]`).classList.remove('hidden');
			this.shadowRoot.querySelectorAll('[data-tab-button]').forEach(el => el.classList.remove('active'));
			this.shadowRoot.querySelector(`[data-tab-button="${tab}"]`).classList.add('active');
		}
		bindEvents(){
			const sr = this.shadowRoot;
			sr.querySelector('#closeBtn').addEventListener('click', () => this.close());
			sr.querySelector('[data-tab-button="login"]').addEventListener('click', () => this.showTab('login'));
			sr.querySelector('[data-tab-button="register"]').addEventListener('click', () => this.showTab('register'));
			sr.querySelector('[data-tab-button="reset"]').addEventListener('click', () => this.showTab('reset'));
			sr.querySelector('#loginForm').addEventListener('submit', (e)=> this.onLogin(e));
			sr.querySelector('#registerForm').addEventListener('submit', (e)=> this.onRegister(e));
			sr.querySelector('#resetForm').addEventListener('submit', (e)=> this.onReset(e));
			sr.querySelector('#confirmForm').addEventListener('submit', (e)=> this.onConfirmReset(e));
		}
		async onLogin(e){
			e.preventDefault(); this.setLoading(true);
			try{
				const form = new FormData(e.target);
				const body = { username: form.get('username'), password: form.get('password') };
				const res = await fetch(this.apiBase + '/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
				if(!res.ok) throw new Error((await res.json()).detail || '登录失败');
				const data = await res.json();
				localStorage.setItem(this.tokenKey, data.access_token);
				this.close();
				this.dispatchEvent(new CustomEvent('ts-auth:login', { bubbles: true, composed: true }));
			}catch(err){ this.showError(err.message); }
			finally{ this.setLoading(false); }
		}
		async onRegister(e){
			e.preventDefault(); this.setLoading(true);
			try{
				const form = new FormData(e.target);
				const body = { username: form.get('username'), password: form.get('password'), email: form.get('email') };
				const res = await fetch(this.apiBase + '/register', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
				const data = await res.json();
				if(!res.ok) throw new Error(data.detail || data.message || '注册失败');
				this.showInfo('注册成功，请登录');
				this.showTab('login');
			}catch(err){ this.showError(err.message); }
			finally{ this.setLoading(false); }
		}
		async onReset(e){
			e.preventDefault(); this.setLoading(true);
			try{
				const form = new FormData(e.target);
				const body = { username: form.get('username') };
				const res = await fetch(this.apiBase + '/request-reset', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
				const data = await res.json();
				if(!res.ok) throw new Error(data.detail || '请求失败');
				let message = '重置令牌已生成，有效期30分钟。';
				if (data.reset_token) message += '\n开发模式: 令牌为\n' + data.reset_token;
				this.showInfo(message);
				this.showTab('confirm');
			}catch(err){ this.showError(err.message); }
			finally{ this.setLoading(false); }
		}
		async onConfirmReset(e){
			e.preventDefault(); this.setLoading(true);
			try{
				const form = new FormData(e.target);
				const body = { token: form.get('token'), new_password: form.get('new_password') };
				const res = await fetch(this.apiBase + '/reset-password', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
				const data = await res.json();
				if(!res.ok) throw new Error(data.detail || '重置失败');
				this.showInfo('密码已重置，请使用新密码登录');
				this.showTab('login');
			}catch(err){ this.showError(err.message); }
			finally{ this.setLoading(false); }
		}
		showError(msg){
			const box = this.shadowRoot.querySelector('#msg');
			box.textContent = msg; box.className = 'msg error';
		}
		showInfo(msg){
			const box = this.shadowRoot.querySelector('#msg');
			box.textContent = msg; box.className = 'msg info';
		}
		render(){
			this.shadowRoot.innerHTML = `
				<style>
					:host{all:initial}
					#overlay{position:fixed;inset:0;display:none;align-items:center;justify-content:center;background:rgba(0,0,0,.55);z-index:99999}
					.panel{width:360px;background:#0b1220;border:1px solid rgba(79,156,255,.35);border-radius:12px;box-shadow:0 6px 30px rgba(0,0,0,.4);color:#e5e7eb;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,\"Helvetica Neue\",Arial}
					.header{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;border-bottom:1px solid rgba(79,156,255,.25)}
					.header h3{font-size:16px;color:#4f9cff;margin:0}
					.close{cursor:pointer;color:#9ca3af}
					.tabs{display:flex;gap:6px;padding:10px 12px;border-bottom:1px solid rgba(79,156,255,.15)}
					.tab-btn{flex:1;padding:8px 10px;background:#0b152b;border:1px solid rgba(79,156,255,.2);color:#9cc7ff;border-radius:8px;cursor:pointer;font-size:12px}
					.tab-btn.active{background:#152745;color:#fff;border-color:#4f9cff}
					.body{padding:12px}
					.label{font-size:12px;color:#9ca3af;margin:8px 0 4px}
					.input{width:100%;padding:8px 10px;border-radius:8px;border:1px solid rgba(79,156,255,.25);background:#0b152b;color:#e5e7eb}
					#submitBtn{width:100%;margin-top:10px;padding:10px;background:#4f9cff;border:none;border-radius:8px;color:#fff;cursor:pointer}
					.msg{margin-top:8px;font-size:12px}
					.msg.error{color:#fca5a5}
					.msg.info{color:#93c5fd}
					.small{font-size:12px;color:#9ca3af;margin-top:8px}
				</style>
				<div id="overlay">
					<div class="panel">
						<div class="header"><h3>账户登录</h3><span id="closeBtn" class="close">✕</span></div>
						<div class="tabs">
							<button class="tab-btn active" data-tab-button="login">登录</button>
							<button class="tab-btn" data-tab-button="register">注册</button>
							<button class="tab-btn" data-tab-button="reset">找回密码</button>
						</div>
						<div class="body">
							<div id="msg" class="msg"></div>
							<form id="loginForm" data-tab="login">
								<label class="label">用户名</label>
								<input class="input" name="username" required>
								<label class="label">密码</label>
								<input class="input" name="password" type="password" required>
								<button id="submitBtn" type="submit">提交</button>
								<div class="small">忘记密码？切换到“找回密码”</div>
							</form>
							<form id="registerForm" class="hidden" data-tab="register">
								<label class="label">用户名</label>
								<input class="input" name="username" required>
								<label class="label">邮箱（可选）</label>
								<input class="input" name="email" type="email" placeholder="you@example.com">
								<label class="label">密码</label>
								<input class="input" name="password" type="password" required>
								<button id="submitBtn" type="submit">提交</button>
							</form>
							<form id="resetForm" class="hidden" data-tab="reset">
								<label class="label">用户名</label>
								<input class="input" name="username" required>
								<button id="submitBtn" type="submit">提交</button>
								<div class="small">提交后会生成一次性令牌（开发模式直接显示）</div>
							</form>
							<form id="confirmForm" class="hidden" data-tab="confirm">
								<label class="label">重置令牌</label>
								<input class="input" name="token" required>
								<label class="label">新密码</label>
								<input class="input" name="new_password" type="password" required>
								<button id="submitBtn" type="submit">提交</button>
							</form>
						</div>
					</div>
				</div>
			`;
		}
	}
	if (!customElements.get('auth-modal')) customElements.define('auth-modal', AuthModal);
	// Auto mount element
	if (!document.querySelector('auth-modal')) {
		const el = document.createElement('auth-modal');
		document.body.appendChild(el);
	}
})(); 