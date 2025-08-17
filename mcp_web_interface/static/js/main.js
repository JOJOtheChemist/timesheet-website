/**
 * 主程序入口
 * 负责初始化应用和全局配置
 */

// 全局配置
const CONFIG = {
    // MCP服务器配置
    MCP_SERVER: {
        HOST: window.location.hostname,
        PORT: window.location.port || (window.location.protocol === 'https:' ? '443' : '80'),
        PROTOCOL: window.location.protocol
    },
    
    // 应用配置
    APP: {
        NAME: 'MCP智能日程助手',
        VERSION: '1.0.0',
        DEBUG: true
    }
};

/**
 * 应用主类
 */
class MCPApp {
    constructor() {
        this.uiManager = null;
        this.mcpClient = null;
        this.isInitialized = false;
    }

    /**
     * 初始化应用
     */
    async initialize() {
        try {
            console.log('🚀 初始化MCP智能日程助手...');
            
            // 检查浏览器兼容性
            this.checkBrowserCompatibility();
            
            // 初始化UI管理器
            this.uiManager = new UIManager();
            
            // 初始化MCP客户端
            this.mcpClient = new MCPClient();
            
            // 测试MCP服务器连接
            await this.testMCPServer();
            
            // 绑定UI管理器到全局应用实例
            this.uiManager.app = this;
            
            // 标记初始化完成
            this.isInitialized = true;
            
            console.log('✅ MCP智能日程助手初始化完成');
            
            // 显示欢迎消息
            this.showWelcomeMessage();
            
        } catch (error) {
            console.error('❌ 应用初始化失败:', error);
            this.showErrorMessage('应用初始化失败，请刷新页面重试');
        }
    }

    /**
     * 检查浏览器兼容性
     */
    checkBrowserCompatibility() {
        const requiredFeatures = [
            'fetch',
            'Promise',
            'async',
            'await'
        ];

        const missingFeatures = requiredFeatures.filter(feature => {
            switch (feature) {
                case 'fetch':
                    return typeof fetch === 'undefined';
                case 'Promise':
                    return typeof Promise === 'undefined';
                case 'async':
                case 'await':
                    return !(function() { try { eval('async () => {}'); return true; } catch(e) { return false; } })();
                default:
                    return false;
            }
        });

        if (missingFeatures.length > 0) {
            throw new Error(`浏览器不支持以下功能: ${missingFeatures.join(', ')}`);
        }
    }

    /**
     * 测试MCP服务器连接
     */
    async testMCPServer() {
        try {
            console.log('🔍 测试MCP服务器连接...');
            
            // 尝试初始化MCP服务器
            const initResult = await this.mcpClient.initialize();
            console.log('MCP服务器初始化结果:', initResult);
            
            // 获取工具列表
            const toolsResult = await this.mcpClient.listTools();
            console.log('可用工具数量:', toolsResult.tools?.length || 0);
            
            // 获取资源列表
            const resourcesResult = await this.mcpClient.listResources();
            console.log('可用资源数量:', resourcesResult.resources?.length || 0);
            
            console.log('✅ MCP服务器连接测试成功');
            
        } catch (error) {
            console.error('❌ MCP服务器连接测试失败:', error);
            throw new Error(`无法连接到MCP服务器: ${error.message}`);
        }
    }

    /**
     * 显示欢迎消息
     */
    showWelcomeMessage() {
        // 在聊天历史中添加欢迎消息
        if (this.uiManager) {
            this.uiManager.addChatMessage('assistant', `
                <strong>🎉 欢迎使用MCP智能日程助手！</strong><br><br>
                我可以帮助你：<br>
                • 📅 查询日程安排<br>
                • 📁 管理项目结构<br>
                • 🤖 智能分析需求<br>
                • ✨ 自然语言交互<br><br>
                试试说："查询今天的日程安排" 或 "显示所有项目"
            `);
        }
    }

    /**
     * 显示错误消息
     */
    showErrorMessage(message) {
        // 创建错误提示元素
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <div style="background: #ffebee; color: #c62828; padding: 20px; border-radius: 10px; text-align: center; margin: 20px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 10px;"></i>
                <h3>错误</h3>
                <p>${message}</p>
                <button onclick="location.reload()" style="background: #c62828; color: white; border: none; padding: 10px 20px; border-radius: 5px; margin-top: 10px; cursor: pointer;">
                    刷新页面
                </button>
            </div>
        `;
        
        // 插入到页面顶部
        const container = document.querySelector('.container');
        container.insertBefore(errorDiv, container.firstChild);
    }

    /**
     * 获取应用状态
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            mcpClient: !!this.mcpClient,
            uiManager: !!this.uiManager,
            config: CONFIG
        };
    }

    /**
     * 调试信息
     */
    debug() {
        if (CONFIG.APP.DEBUG) {
            console.log('🔍 应用状态:', this.getStatus());
            console.log('🌐 当前配置:', CONFIG);
        }
    }
}

// 全局应用实例
let app = null;

/**
 * 页面加载完成后初始化应用
 */
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // 创建应用实例
        app = new MCPApp();
        
        // 初始化应用
        await app.initialize();
        
        // 输出调试信息
        app.debug();
        
    } catch (error) {
        console.error('应用启动失败:', error);
    }
});

/**
 * 页面卸载前清理资源
 */
window.addEventListener('beforeunload', () => {
    if (app) {
        console.log('🧹 清理应用资源...');
        // 这里可以添加资源清理逻辑
    }
});

/**
 * 全局错误处理
 */
window.addEventListener('error', (event) => {
    console.error('全局错误:', event.error);
    if (app && app.uiManager) {
        app.uiManager.addChatMessage('assistant', `系统遇到错误：${event.error.message}`);
    }
});

/**
 * 未处理的Promise拒绝
 */
window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的Promise拒绝:', event.reason);
    if (app && app.uiManager) {
        app.uiManager.addChatMessage('assistant', `操作失败：${event.reason.message || '未知错误'}`);
    }
});

// 导出到全局作用域（用于调试）
window.MCPApp = MCPApp;
window.app = app; 