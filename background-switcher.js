// 背景图切换器
class BackgroundSwitcher {
    constructor() {
        this.currentBackground = 'night';
        this.backgrounds = ['night', 'morning', 'day', 'dusk'];
        this.backgroundNames = {
            'night': '🌙 夜间',
            'morning': '🌅 早晨',
            'day': '☀️ 白天',
            'dusk': '🌆 傍晚'
        };
        
        this.init();
    }
    
    init() {
        this.createUI();
        this.bindEvents();
        this.setBackgroundByTime();
        console.log('🎨 背景图切换器已初始化');
    }
    
    createUI() {
        // 创建背景指示器
        const indicator = document.createElement('div');
        indicator.className = 'background-indicator';
        indicator.innerHTML = this.backgroundNames[this.currentBackground];
        document.body.appendChild(indicator);
        
        // 创建背景控制按钮
        const controls = document.createElement('div');
        controls.className = 'background-controls';
        
        this.backgrounds.forEach(bg => {
            const btn = document.createElement('button');
            btn.className = 'bg-btn';
            btn.innerHTML = this.getBackgroundIcon(bg);
            btn.title = this.backgroundNames[bg];
            btn.onclick = () => this.switchBackground(bg);
            
            if (bg === this.currentBackground) {
                btn.classList.add('active');
            }
            
            controls.appendChild(btn);
        });
        
        document.body.appendChild(controls);
        this.indicator = indicator;
        this.controls = controls;
        
        // 添加拖拽功能
        this.makeDraggable(controls);
    }
    
    getBackgroundIcon(bg) {
        const icons = {
            'night': '🌙',
            'morning': '🌅',
            'day': '☀️',
            'dusk': '🌆'
        };
        return icons[bg] || '🎨';
    }
    
    bindEvents() {
        // 只监听日程表容器的滚动事件
        const scheduleContainer = document.querySelector('body > div.container > div.main-content > div.schedule-table-container');
        if (scheduleContainer) {
            scheduleContainer.addEventListener('scroll', (e) => {
                this.handleScroll(e);
            });
            console.log('🎯 已绑定日程表滚动事件监听器');
        } else {
            console.warn('⚠️ 未找到日程表容器，背景自动切换功能将不可用');
        }
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.switchBackground('night');
                        break;
                    case '2':
                        e.preventDefault();
                        this.switchBackground('morning');
                        break;
                    case '3':
                        e.preventDefault();
                        this.switchBackground('day');
                        break;
                    case '4':
                        e.preventDefault();
                        this.switchBackground('dusk');
                        break;
                }
            }
        });
    }
    
    handleScroll(e) {
        // 根据滚动位置自动切换背景
        const scrollTop = e.target.scrollTop || window.pageYOffset;
        const maxScroll = e.target.scrollHeight - e.target.clientHeight || document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = scrollTop / maxScroll;
        
        // 根据滚动百分比切换背景
        if (scrollPercent < 0.25) {
            this.autoSwitchBackground('night');
        } else if (scrollPercent < 0.5) {
            this.autoSwitchBackground('morning');
        } else if (scrollPercent < 0.75) {
            this.autoSwitchBackground('day');
        } else {
            this.autoSwitchBackground('dusk');
        }
    }
    
    autoSwitchBackground(bg) {
        if (bg !== this.currentBackground) {
            this.switchBackground(bg, true);
        }
    }
    
    switchBackground(bg, isAuto = false) {
        if (bg === this.currentBackground) return;
        
        // 移除所有背景类
        document.body.classList.remove(...this.backgrounds.map(b => `background-${b}`));
        
        // 添加新背景类
        document.body.classList.add(`background-${bg}`);
        
        // 更新当前背景
        this.currentBackground = bg;
        
        // 更新指示器
        this.indicator.innerHTML = this.backgroundNames[bg];
        
        // 更新按钮状态
        this.updateButtonStates(bg);
        
        // 显示切换提示
        if (!isAuto) {
            this.showNotification(`背景已切换到: ${this.backgroundNames[bg]}`);
        }
        
        console.log(`🎨 背景已切换到: ${bg}`);
    }
    
    updateButtonStates(activeBg) {
        const buttons = this.controls.querySelectorAll('.bg-btn');
        buttons.forEach((btn, index) => {
            btn.classList.toggle('active', this.backgrounds[index] === activeBg);
        });
    }
    
    setBackgroundByTime() {
        const hour = new Date().getHours();
        let bg;
        
        if (hour >= 6 && hour < 10) {
            bg = 'morning';
        } else if (hour >= 10 && hour < 18) {
            bg = 'day';
        } else if (hour >= 18 && hour < 20) {
            bg = 'dusk';
        } else {
            bg = 'night';
        }
        
        this.switchBackground(bg, true);
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 15px 25px;
            border-radius: 25px;
            font-size: 14px;
            z-index: 10001;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: fadeInOut 2s ease-in-out;
        `;
        
        notification.innerHTML = message;
        document.body.appendChild(notification);
        
        // 添加动画样式
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes fadeInOut {
                    0%, 100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                    20%, 80% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
                }
            `;
            document.head.appendChild(style);
        }
        
        setTimeout(() => {
            notification.remove();
        }, 2000);
    }
    
    makeDraggable(element) {
        let isDragging = false;
        let dragOffset = { x: 0, y: 0 };
        
        const dragStart = (e) => {
            e.preventDefault();
            isDragging = true;
            
            const rect = element.getBoundingClientRect();
            if (e.type === 'touchstart') {
                dragOffset.x = e.touches[0].clientX - rect.left;
                dragOffset.y = e.touches[0].clientY - rect.top;
            } else {
                dragOffset.x = e.clientX - rect.left;
                dragOffset.y = e.clientY - rect.top;
            }
            
            element.style.cursor = 'grabbing';
        };
        
        const dragMove = (e) => {
            if (!isDragging) return;
            e.preventDefault();
            
            let clientX, clientY;
            if (e.type === 'touchmove') {
                clientX = e.touches[0].clientX;
                clientY = e.touches[0].clientY;
            } else {
                clientX = e.clientX;
                clientY = e.clientY;
            }
            
            const x = clientX - dragOffset.x;
            const y = clientY - dragOffset.y;
            
            // 限制在视窗范围内
            const maxX = window.innerWidth - element.offsetWidth;
            const maxY = window.innerHeight - element.offsetHeight;
            
            // 直接设置CSS属性，不使用transform
            element.style.left = Math.max(0, Math.min(x, maxX)) + 'px';
            element.style.top = Math.max(0, Math.min(y, maxY)) + 'px';
            element.style.right = 'auto';
            element.style.transform = 'none';
        };
        
        const dragEnd = () => {
            isDragging = false;
            element.style.cursor = 'move';
        };
        
        // 鼠标事件
        element.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', dragMove);
        document.addEventListener('mouseup', dragEnd);
        
        // 触摸事件（移动端）
        element.addEventListener('touchstart', dragStart, { passive: false });
        document.addEventListener('touchmove', dragMove, { passive: false });
        document.addEventListener('touchend', dragEnd);
        
        // 防止拖拽时触发按钮点击
        element.addEventListener('click', (e) => {
            if (isDragging) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    new BackgroundSwitcher();
}); 