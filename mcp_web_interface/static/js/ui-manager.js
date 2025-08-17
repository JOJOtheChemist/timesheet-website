/**
 * UI管理器组件
 * 负责管理页面UI状态和交互
 */
class UIManager {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentTab = 'schedule';
    }

    /**
     * 初始化DOM元素引用
     */
    initializeElements() {
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearChatBtn = document.getElementById('clearChat');
        this.chatHistory = document.getElementById('chatHistory');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        // 标签页相关
        this.tabBtns = document.querySelectorAll('.tab-btn');
        this.tabPanes = document.querySelectorAll('.tab-pane');
        
        // 内容区域
        this.scheduleContent = document.getElementById('scheduleContent');
        this.projectsContent = document.getElementById('projectsContent');
        this.aiAnalysisContent = document.getElementById('aiAnalysisContent');
        
        // 调试信息
        console.log('🔍 DOM元素初始化:', {
            userInput: !!this.userInput,
            sendBtn: !!this.sendBtn,
            clearChatBtn: !!this.clearChatBtn,
            chatHistory: !!this.chatHistory,
            loadingOverlay: !!this.loadingOverlay,
            tabBtns: this.tabBtns.length,
            tabPanes: this.tabPanes.length
        });
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 确保DOM元素存在后再绑定事件
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.handleSend());
        }
        
        if (this.userInput) {
            // 回车键发送
            this.userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSend();
                }
            });
        }

        if (this.clearChatBtn) {
            // 清空聊天记录
            this.clearChatBtn.addEventListener('click', () => this.clearChat());
        }

        // 标签页切换
        this.tabBtns.forEach(btn => {
            btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
        });
        
        console.log('✅ UI事件绑定完成');
    }

    /**
     * 处理发送消息
     */
    async handleSend() {
        const userInput = this.userInput.value.trim();
        if (!userInput) return;

        // 显示用户消息
        this.addChatMessage('user', userInput);
        
        // 清空输入框
        this.userInput.value = '';
        
        // 显示加载状态
        this.showLoading();

        try {
            // 使用全局的MCP客户端实例
            if (window.app && window.app.mcpClient) {
                const result = await window.app.mcpClient.processNaturalLanguageRequest(userInput);
                
                // 显示AI回复
                this.addChatMessage('assistant', this.formatAIResponse(result));
                
                // 更新结果展示
                this.updateResults(result);
            } else {
                throw new Error('MCP客户端未初始化');
            }
            
        } catch (error) {
            console.error('处理请求失败:', error);
            this.addChatMessage('assistant', `抱歉，处理您的请求时出现了错误：${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 添加聊天消息
     */
    addChatMessage(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        
        const timestamp = new Date().toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span>${type === 'user' ? '你' : 'AI助手'}</span>
                <span>${timestamp}</span>
            </div>
            <div class="message-content">${content}</div>
        `;
        
        this.chatHistory.appendChild(messageDiv);
        
        // 滚动到底部
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
        
        // 移除欢迎消息
        const welcomeMessage = this.chatHistory.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
    }

    /**
     * 格式化AI响应
     */
    formatAIResponse(result) {
        let response = `<strong>操作类型：</strong>${result.action}<br>`;
        response += `<strong>操作说明：</strong>${result.explanation}<br>`;
        
        if (result.parameters && Object.keys(result.parameters).length > 0) {
            response += `<strong>参数：</strong>${JSON.stringify(result.parameters, null, 2)}<br>`;
        }
        
        if (result.data) {
            response += `<strong>结果：</strong>操作成功完成`;
        }
        
        return response;
    }

    /**
     * 更新结果展示
     */
    updateResults(result) {
        switch (result.action) {
            case 'query_schedule':
                this.updateScheduleTab(result.data);
                this.switchTab('schedule');
                break;
                
            case 'query_projects':
                this.updateProjectsTab(result.data);
                this.switchTab('projects');
                break;
                
            default:
                this.updateAIAnalysisTab(result);
                this.switchTab('ai-analysis');
        }
    }

    /**
     * 更新日程标签页
     */
    updateScheduleTab(scheduleData) {
        if (!Array.isArray(scheduleData) || scheduleData.length === 0) {
            this.scheduleContent.innerHTML = '<p class="placeholder-text">暂无日程数据</p>';
            return;
        }

        let html = '<h4>今日日程安排</h4>';
        scheduleData.forEach(item => {
            html += `
                <div class="data-item">
                    <h4>${item.time_slot} - ${item.planned_subtask_name || '未安排'}</h4>
                    <p><strong>计划项目：</strong>${item.planned_project_name || '无'}</p>
                    <p><strong>实际项目：</strong>${item.actual_project_name || '无'}</p>
                    <p><strong>备注：</strong>${item.planned_notes || '无'}</p>
                    <p><strong>心情：</strong>${item.mood || '无'}</p>
                    <div class="tags">
                        <span class="tag">${item.schedule_date}</span>
                        <span class="tag">${item.time_slot}</span>
                    </div>
                </div>
            `;
        });
        
        this.scheduleContent.innerHTML = html;
    }

    /**
     * 更新项目标签页
     */
    updateProjectsTab(projectsData) {
        if (!Array.isArray(projectsData) || projectsData.length === 0) {
            this.projectsContent.innerHTML = '<p class="placeholder-text">暂无项目数据</p>';
            return;
        }

        let html = '<h4>项目结构</h4>';
        projectsData.forEach(category => {
            html += `
                <div class="data-item">
                    <h4>${category.name}</h4>
                    <p><strong>分类ID：</strong>${category.id}</p>
                    <p><strong>项目数量：</strong>${category.projects.length}</p>
                    <div class="tags">
                        <span class="tag" style="background-color: ${category.color}; color: white;">${category.name}</span>
                    </div>
                </div>
            `;
            
            category.projects.forEach(project => {
                html += `
                    <div class="data-item" style="margin-left: 20px;">
                        <h4>└─ ${project.name}</h4>
                        <p><strong>项目ID：</strong>${project.id}</p>
                        <p><strong>子任务数量：</strong>${project.subtasks.length}</p>
                        <div class="tags">
                            <span class="tag" style="background-color: ${project.color}; color: white;">${project.name}</span>
                        </div>
                    </div>
                `;
            });
        });
        
        this.projectsContent.innerHTML = html;
    }

    /**
     * 更新AI分析标签页
     */
    updateAIAnalysisTab(result) {
        let html = `
            <h4>AI分析结果</h4>
            <div class="data-item">
                <h4>操作分析</h4>
                <p><strong>操作类型：</strong>${result.action}</p>
                <p><strong>操作说明：</strong>${result.explanation}</p>
                <p><strong>参数：</strong>${JSON.stringify(result.parameters, null, 2)}</p>
                <p><strong>执行状态：</strong>${result.data ? '成功' : '失败'}</p>
            </div>
        `;
        
        if (result.data) {
            html += `
                <div class="data-item">
                    <h4>执行结果</h4>
                    <pre>${JSON.stringify(result.data, null, 2)}</pre>
                </div>
            `;
        }
        
        this.aiAnalysisContent.innerHTML = html;
    }

    /**
     * 切换标签页
     */
    switchTab(tabName) {
        // 更新标签页按钮状态
        this.tabBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        // 更新标签页内容显示
        this.tabPanes.forEach(pane => {
            pane.classList.toggle('active', pane.id === `${tabName}-tab`);
        });
        
        this.currentTab = tabName;
    }

    /**
     * 显示加载状态
     */
    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
        this.sendBtn.disabled = true;
        this.sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
    }

    /**
     * 隐藏加载状态
     */
    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
        this.sendBtn.disabled = false;
        this.sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 发送';
    }

    /**
     * 清空聊天记录
     */
    clearChat() {
        this.chatHistory.innerHTML = `
            <div class="welcome-message">
                <i class="fas fa-hand-wave"></i>
                <p>聊天记录已清空，请告诉我你需要什么帮助？</p>
            </div>
        `;
    }
}

// 导出UI管理器类
window.UIManager = UIManager; 