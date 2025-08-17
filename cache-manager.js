/**
 * 缓存管理器 - 实现定时批量保存功能
 * 用于减少API请求频率，提高性能
 */

class CacheManager {
    constructor() {
        // 本地缓存数据
        this.cache = new Map();
        
        // 保存定时器
        this.saveTimer = null;
        
        // 保存间隔（毫秒）
        this.saveInterval = 5000; // 5秒
        
        // 最大缓存大小
        this.maxCacheSize = 1000;
        
        // 保存状态
        this.isSaving = false;
        
        // 初始化
        this.init();
    }
    
    /**
     * 初始化缓存管理器
     */
    init() {
        console.log('缓存管理器初始化完成');
        this.startAutoSave();
    }
    
    /**
     * 设置缓存数据
     * @param {string} key - 缓存键
     * @param {object} data - 缓存数据
     */
    set(key, data) {
        this.cache.set(key, {
            ...data,
            timestamp: Date.now(),
            dirty: true // 标记为需要保存
        });
        
        console.log(`缓存数据已更新: ${key}`, data);
        
        // 检查缓存大小
        if (this.cache.size > this.maxCacheSize) {
            this.cleanup();
        }
    }
    
    /**
     * 获取缓存数据
     * @param {string} key - 缓存键
     * @returns {object|null} 缓存数据
     */
    get(key) {
        return this.cache.get(key) || null;
    }
    
    /**
     * 删除缓存数据
     * @param {string} key - 缓存键
     */
    delete(key) {
        this.cache.delete(key);
        console.log(`缓存数据已删除: ${key}`);
    }
    
    /**
     * 清空所有缓存
     */
    clear() {
        this.cache.clear();
        console.log('所有缓存数据已清空');
    }
    
    /**
     * 获取所有需要保存的数据
     * @returns {Array} 需要保存的数据列表
     */
    getDirtyData() {
        const dirtyData = [];
        for (const [key, value] of this.cache.entries()) {
            if (value.dirty) {
                dirtyData.push({
                    key,
                    data: value
                });
            }
        }
        return dirtyData;
    }
    
    /**
     * 标记数据为已保存
     * @param {string} key - 缓存键
     */
    markAsSaved(key) {
        const item = this.cache.get(key);
        if (item) {
            item.dirty = false;
            item.lastSaved = Date.now();
        }
    }
    
    /**
     * 开始自动保存
     */
    startAutoSave() {
        if (this.saveTimer) {
            clearInterval(this.saveTimer);
        }
        
        this.saveTimer = setInterval(() => {
            this.saveDirtyData();
        }, this.saveInterval);
        
        console.log(`自动保存已启动，间隔: ${this.saveInterval}ms`);
    }
    
    /**
     * 停止自动保存
     */
    stopAutoSave() {
        if (this.saveTimer) {
            clearInterval(this.saveTimer);
            this.saveTimer = null;
            console.log('自动保存已停止');
        }
    }
    
    /**
     * 保存所有脏数据
     */
    async saveDirtyData() {
        if (this.isSaving) {
            console.log('正在保存中，跳过本次保存');
            return;
        }
        
        const dirtyData = this.getDirtyData();
        if (dirtyData.length === 0) {
            return;
        }
        
        console.log(`开始批量保存 ${dirtyData.length} 条数据`);
        this.isSaving = true;
        
        try {
            // 按数据类型分组
            const taskUpdates = [];
            const notesUpdates = [];
            const moodUpdates = [];
            
            for (const {key, data} of dirtyData) {
                const {schedule_date, time_slot, schedule_id} = data;
                
                // 任务更新
                if (data.planned_subtask_id || data.actual_subtask_id) {
                    taskUpdates.push({
                        schedule_id,
                        schedule_date,
                        time_slot,
                        planned_subtask_id: data.planned_subtask_id,
                        planned_subtask_name: data.planned_subtask_name,
                        planned_subtask_color: data.planned_subtask_color,
                        actual_subtask_id: data.actual_subtask_id,
                        actual_subtask_name: data.actual_subtask_name,
                        actual_subtask_color: data.actual_subtask_color
                    });
                }
                
                // 备注更新
                if (data.planned_notes || data.actual_notes) {
                    notesUpdates.push({
                        schedule_id,
                        schedule_date,
                        time_slot,
                        planned_notes: data.planned_notes,
                        actual_notes: data.actual_notes
                    });
                }
                
                // 心情更新
                if (data.mood) {
                    moodUpdates.push({
                        schedule_id,
                        schedule_date,
                        time_slot,
                        mood: data.mood
                    });
                }
            }
            
            // 批量保存任务数据
            if (taskUpdates.length > 0) {
                await this.batchSaveTasks(taskUpdates);
            }
            
            // 批量保存备注数据
            if (notesUpdates.length > 0) {
                await this.batchSaveNotes(notesUpdates);
            }
            
            // 批量保存心情数据
            if (moodUpdates.length > 0) {
                await this.batchSaveMoods(moodUpdates);
            }
            
            // 标记所有数据为已保存
            for (const {key} of dirtyData) {
                this.markAsSaved(key);
            }
            
            console.log(`批量保存完成: 任务${taskUpdates.length}条, 备注${notesUpdates.length}条, 心情${moodUpdates.length}条`);
            
            // 显示保存成功提示
            this.showSaveSuccessMessage(taskUpdates.length, notesUpdates.length, moodUpdates.length);
            
        } catch (error) {
            console.error('批量保存失败:', error);
            this.showSaveErrorMessage(error.message);
        } finally {
            this.isSaving = false;
        }
    }
    
    /**
     * 批量保存任务数据
     * @param {Array} taskUpdates - 任务更新数据
     */
    async batchSaveTasks(taskUpdates) {
        console.log('批量保存任务数据:', taskUpdates);
        
        for (const taskData of taskUpdates) {
            try {
                if (!taskData.schedule_id) {
                    // 创建新记录
                    const response = await fetch('/api/schedule', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(taskData)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`创建任务失败: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    console.log('任务创建成功:', result);
                    
                } else {
                    // 更新现有记录
                    const response = await fetch(`/api/schedule/${taskData.schedule_id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(taskData)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`更新任务失败: ${response.status}`);
                    }
                    
                    console.log('任务更新成功');
                }
            } catch (error) {
                console.error(`保存任务数据失败:`, error);
                throw error;
            }
        }
    }
    
    /**
     * 批量保存备注数据
     * @param {Array} notesUpdates - 备注更新数据
     */
    async batchSaveNotes(notesUpdates) {
        console.log('批量保存备注数据:', notesUpdates);
        
        for (const notesData of notesUpdates) {
            try {
                if (!notesData.schedule_id) {
                    // 创建新记录
                    const response = await fetch('/api/schedule', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(notesData)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`创建备注失败: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    console.log('备注创建成功:', result);
                    
                } else {
                    // 更新现有记录
                    const response = await fetch(`/api/schedule/${notesData.schedule_id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(notesData)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`更新备注失败: ${response.status}`);
                    }
                    
                    console.log('备注更新成功');
                }
            } catch (error) {
                console.error(`保存备注数据失败:`, error);
                throw error;
            }
        }
    }
    
    /**
     * 批量保存心情数据
     * @param {Array} moodUpdates - 心情更新数据
     */
    async batchSaveMoods(moodUpdates) {
        console.log('批量保存心情数据:', moodUpdates);
        
        for (const moodData of moodUpdates) {
            try {
                if (!moodData.schedule_id) {
                    // 创建新记录
                    const response = await fetch('/api/schedule', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(moodData)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`创建心情失败: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    console.log('心情创建成功:', result);
                    
                } else {
                    // 更新现有记录
                    const response = await fetch(`/api/schedule/${moodData.schedule_id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(moodData)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`更新心情失败: ${response.status}`);
                    }
                    
                    console.log('心情更新成功');
                }
            } catch (error) {
                console.error(`保存心情数据失败:`, error);
                throw error;
            }
        }
    }
    
    /**
     * 强制立即保存
     */
    async forceSave() {
        console.log('强制立即保存');
        await this.saveDirtyData();
    }
    
    /**
     * 清理过期缓存
     */
    cleanup() {
        const now = Date.now();
        const maxAge = 24 * 60 * 60 * 1000; // 24小时
        
        for (const [key, value] of this.cache.entries()) {
            if (now - value.timestamp > maxAge && !value.dirty) {
                this.cache.delete(key);
            }
        }
        
        console.log(`缓存清理完成，当前缓存大小: ${this.cache.size}`);
    }
    
    /**
     * 显示保存成功提示
     */
    showSaveSuccessMessage(taskCount, notesCount, moodCount) {
        let message = '保存成功！';
        const parts = [];
        
        if (taskCount > 0) parts.push(`任务: ${taskCount}个`);
        if (notesCount > 0) parts.push(`备注: ${notesCount}个`);
        if (moodCount > 0) parts.push(`心情: ${moodCount}个`);
        
        if (parts.length > 0) {
            message += ' ' + parts.join(' ');
        }
        
        this.showNotification(message, 'success');
    }
    
    /**
     * 显示保存失败提示
     */
    showSaveErrorMessage(errorMessage) {
        this.showNotification(`保存失败: ${errorMessage}`, 'error');
    }
    
    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `cache-notification ${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            font-size: 14px;
            font-weight: 500;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, type === 'error' ? 5000 : 3000);
    }
    
    /**
     * 获取缓存统计信息
     */
    getStats() {
        const dirtyCount = this.getDirtyData().length;
        return {
            totalSize: this.cache.size,
            dirtyCount,
            isSaving: this.isSaving,
            saveInterval: this.saveInterval
        };
    }
    
    /**
     * 设置保存间隔
     * @param {number} interval - 保存间隔（毫秒）
     */
    setSaveInterval(interval) {
        this.saveInterval = interval;
        this.startAutoSave(); // 重新启动自动保存
        console.log(`保存间隔已更新为: ${interval}ms`);
    }
}

// 创建全局缓存管理器实例
window.cacheManager = new CacheManager();

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CacheManager;
} 