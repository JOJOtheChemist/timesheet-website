/**
 * MCP客户端组件
 * 负责与MCP服务器通信
 */
class MCPClient {
    constructor() {
        this.baseUrl = '/api/mcp'; // 通过nginx代理到MCP服务器
        this.requestId = 1;
    }

    /**
     * 生成唯一的请求ID
     */
    generateRequestId() {
        return `web_${Date.now()}_${this.requestId++}`;
    }

    /**
     * 发送MCP请求
     */
    async sendRequest(method, params = {}) {
        const request = {
            jsonrpc: "2.0",
            id: this.generateRequestId(),
            method: method,
            params: params
        };

        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(request)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.error) {
                throw new Error(`MCP Error: ${result.error.message}`);
            }

            return result.result;
        } catch (error) {
            console.error('MCP请求失败:', error);
            throw error;
        }
    }

    /**
     * 初始化MCP服务器
     */
    async initialize() {
        return await this.sendRequest('initialize');
    }

    /**
     * 获取工具列表
     */
    async listTools() {
        return await this.sendRequest('tools/list');
    }

    /**
     * 获取资源列表
     */
    async listResources() {
        return await this.sendRequest('resources/list');
    }

    /**
     * 调用工具
     */
    async callTool(name, arguments_ = {}) {
        return await this.sendRequest('tools/call', {
            name: name,
            arguments: arguments_
        });
    }

    /**
     * 读取资源
     */
    async readResource(uri) {
        return await this.sendRequest('resources/read', {
            uri: uri
        });
    }

    /**
     * 使用AI分析用户请求
     */
    async analyzeUserRequest(userRequest) {
        try {
            const result = await this.callTool('ai_analyze', {
                user_request: userRequest
            });
            
            if (result && result.content && result.content.length > 0) {
                const content = result.content[0];
                if (content.type === 'text') {
                    try {
                        return JSON.parse(content.text);
                    } catch (e) {
                        return {
                            action: 'unknown',
                            parameters: {},
                            explanation: content.text
                        };
                    }
                }
            }
            
            throw new Error('AI分析返回格式错误');
        } catch (error) {
            console.error('AI分析失败:', error);
            throw error;
        }
    }

    /**
     * 获取日程数据
     */
    async getSchedule(date) {
        try {
            const result = await this.callTool('get_schedule', { date: date });
            if (result && result.content && result.content.length > 0) {
                const content = result.content[0];
                if (content.type === 'text') {
                    try {
                        return JSON.parse(content.text);
                    } catch (e) {
                        return [];
                    }
                }
            }
            return [];
        } catch (error) {
            console.error('获取日程失败:', error);
            return [];
        }
    }

    /**
     * 获取项目数据
     */
    async getProjects() {
        try {
            const result = await this.callTool('get_projects');
            if (result && result.content && result.content.length > 0) {
                const content = result.content[0];
                if (content.type === 'text') {
                    try {
                        return JSON.parse(content.text);
                    } catch (e) {
                        return [];
                    }
                }
            }
            return [];
        } catch (error) {
            console.error('获取项目失败:', error);
            return [];
        }
    }

    /**
     * 创建日程
     */
    async createSchedule(scheduleData) {
        try {
            const result = await this.callTool('create_schedule', scheduleData);
            return result;
        } catch (error) {
            console.error('创建日程失败:', error);
            throw error;
        }
    }

    /**
     * 更新日程
     */
    async updateSchedule(scheduleId, data) {
        try {
            const result = await this.callTool('update_schedule', {
                schedule_id: scheduleId,
                data: data
            });
            return result;
        } catch (error) {
            console.error('更新日程失败:', error);
            throw error;
        }
    }

    /**
     * 删除日程
     */
    async deleteSchedule(scheduleId) {
        try {
            const result = await this.callTool('delete_schedule', {
                schedule_id: scheduleId
            });
            return result;
        } catch (error) {
            console.error('删除日程失败:', error);
            throw error;
        }
    }

    /**
     * 处理用户自然语言请求
     */
    async processNaturalLanguageRequest(userRequest) {
        try {
            // 1. 使用AI分析用户请求
            const aiAnalysis = await this.analyzeUserRequest(userRequest);
            
            // 2. 根据AI分析结果执行相应操作
            let result = {
                action: aiAnalysis.action,
                parameters: aiAnalysis.parameters,
                explanation: aiAnalysis.explanation,
                data: null
            };

            switch (aiAnalysis.action) {
                case 'query_schedule':
                    const date = aiAnalysis.parameters.date === 'today' 
                        ? new Date().toISOString().split('T')[0] 
                        : aiAnalysis.parameters.date;
                    result.data = await this.getSchedule(date);
                    break;
                    
                case 'query_projects':
                    result.data = await this.getProjects();
                    break;
                    
                case 'create_schedule':
                    result.data = await this.createSchedule(aiAnalysis.parameters);
                    break;
                    
                case 'update_schedule':
                    result.data = await this.updateSchedule(
                        aiAnalysis.parameters.schedule_id, 
                        aiAnalysis.parameters.data
                    );
                    break;
                    
                case 'delete_schedule':
                    result.data = await this.deleteSchedule(aiAnalysis.parameters.schedule_id);
                    break;
                    
                default:
                    result.data = { message: '未知操作类型' };
            }

            return result;
        } catch (error) {
            console.error('处理自然语言请求失败:', error);
            return {
                action: 'error',
                parameters: {},
                explanation: `处理请求时发生错误: ${error.message}`,
                data: null
            };
        }
    }
}

// 导出MCP客户端实例
window.MCPClient = MCPClient; 