/**
 * 主应用程序
 * 应用程序的入口点和全局协调器
 */

class App {
    constructor() {
        this.version = '1.0.0';
        this.initialized = false;
        this.currentData = null;
        
        // 绑定事件处理器
        this.handleError = this.handleError.bind(this);
        this.handleResize = this.handleResize.bind(this);
    }

    /**
     * 应用程序初始化
     */
    async init() {
        try {
            console.log('🚀 启动缠论K线分析系统...');
            
            // 检查浏览器兼容性
            this.checkBrowserCompatibility();
            
            // 初始化错误处理
            this.initErrorHandling();
            
            // 初始化图表
            chartManager.initCharts();
            
            // 设置初始状态
            this.setInitialState();
            
            // 绑定全局事件
            this.bindGlobalEvents();
            
            // 检查API连接
            await this.checkAPIConnection();
            
            this.initialized = true;
            StatusManager.ready();
            
            console.log('✅ 系统初始化完成');
            ErrorHandler.showNotification('缠论K线分析系统已就绪', 'success');
            
        } catch (error) {
            console.error('❌ 系统初始化失败:', error);
            this.handleInitError(error);
        }
    }

    /**
     * 检查浏览器兼容性
     */
    checkBrowserCompatibility() {
        const requiredFeatures = [
            'fetch',
            'Promise',
            'localStorage',
            'addEventListener'
        ];

        const missingFeatures = requiredFeatures.filter(feature => {
            return typeof window[feature] === 'undefined';
        });

        if (missingFeatures.length > 0) {
            throw new Error(`浏览器不支持以下功能: ${missingFeatures.join(', ')}`);
        }

        // 检查ECharts
        if (typeof echarts === 'undefined') {
            throw new Error('ECharts图表库未加载');
        }
    }

    /**
     * 初始化错误处理
     */
    initErrorHandling() {
        // 全局错误处理
        window.addEventListener('error', this.handleError);
        window.addEventListener('unhandledrejection', this.handleError);
        
        // 监听API错误
        window.addEventListener('apierror', this.handleError);
    }

    /**
     * 设置初始状态
     */
    setInitialState() {
        // 从localStorage恢复设置
        this.restoreSettings();
        
        // 设置默认参数
        this.setDefaultParameters();
        
        // 更新UI状态
        this.updateUIState();
    }

    /**
     * 恢复设置
     */
    restoreSettings() {
        try {
            const settings = localStorage.getItem('chanTheorySettings');
            if (settings) {
                const parsed = JSON.parse(settings);
                
                // 恢复显示设置
                Object.keys(parsed.display || {}).forEach(key => {
                    const checkbox = document.getElementById(`show-${key}`);
                    if (checkbox) {
                        checkbox.checked = parsed.display[key];
                    }
                });
                
                // 恢复主题设置
                if (parsed.theme) {
                    const themeBtn = document.querySelector(`[data-theme="${parsed.theme}"]`);
                    if (themeBtn) {
                        themeBtn.click();
                    }
                }
                
                // 恢复参数设置
                Object.keys(parsed.parameters || {}).forEach(key => {
                    const input = document.getElementById(key);
                    if (input) {
                        input.value = parsed.parameters[key];
                        input.dispatchEvent(new Event('input'));
                    }
                });
            }
        } catch (error) {
            console.warn('恢复设置失败:', error);
        }
    }

    /**
     * 设置默认参数
     */
    setDefaultParameters() {
        const defaults = {
            'kline-count': 100,
            'start-price': 100,
            'volatility': 0.02,
            'trend-bias': 0,
            'fenxing-strength': 0.5,
            'time-interval': '1m'
        };

        Object.keys(defaults).forEach(id => {
            const input = document.getElementById(id);
            if (input && !input.value) {
                input.value = defaults[id];
                input.dispatchEvent(new Event('input'));
            }
        });
    }

    /**
     * 更新UI状态
     */
    updateUIState() {
        // 触发范围滑块更新
        document.querySelectorAll('input[type="range"]').forEach(input => {
            input.dispatchEvent(new Event('input'));
        });
    }

    /**
     * 绑定全局事件
     */
    bindGlobalEvents() {
        // 窗口大小变化
        window.addEventListener('resize', this.handleResize);
        
        // 页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.handlePageVisible();
            } else {
                this.handlePageHidden();
            }
        });
        
        // 页面卸载前保存设置
        window.addEventListener('beforeunload', () => {
            this.saveSettings();
        });
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    /**
     * 检查API连接
     */
    async checkAPIConnection() {
        try {
            StatusManager.loading('检查API连接');
            const response = await apiClient.getAnalysisInfo();
            
            if (response.success) {
                console.log('✅ API连接正常');
            } else {
                throw new Error('API响应异常');
            }
        } catch (error) {
            console.warn('⚠️ API连接检查失败:', error);
            ErrorHandler.showNotification('API连接异常，某些功能可能不可用', 'warning');
        }
    }

    /**
     * 处理窗口大小变化
     */
    handleResize() {
        // 防抖处理
        clearTimeout(this.resizeTimer);
        this.resizeTimer = setTimeout(() => {
            if (chartManager.mainChart) {
                chartManager.mainChart.resize();
            }
            if (chartManager.macdChart) {
                chartManager.macdChart.resize();
            }
            if (chartManager.patternChart) {
                chartManager.patternChart.resize();
            }
        }, 300);
    }

    /**
     * 处理页面可见
     */
    handlePageVisible() {
        console.log('页面变为可见');
        // 重新检查API连接
        if (this.initialized) {
            this.checkAPIConnection();
        }
    }

    /**
     * 处理页面隐藏
     */
    handlePageHidden() {
        console.log('页面被隐藏');
        // 保存当前设置
        this.saveSettings();
    }

    /**
     * 处理键盘快捷键
     */
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + 快捷键
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'Enter':
                    e.preventDefault();
                    if (!uiManager.isAnalyzing) {
                        uiManager.startAnalysis();
                    }
                    break;
                case 's':
                    e.preventDefault();
                    uiManager.exportData();
                    break;
                case 'r':
                    e.preventDefault();
                    chartManager.resetZoom();
                    break;
                case '1':
                    e.preventDefault();
                    uiManager.switchPanel('analysis');
                    break;
                case '2':
                    e.preventDefault();
                    uiManager.switchPanel('patterns');
                    break;
                case '3':
                    e.preventDefault();
                    uiManager.switchPanel('settings');
                    break;
            }
        }
        
        // ESC键
        if (e.key === 'Escape') {
            LoadingManager.hide();
        }
    }

    /**
     * 保存设置
     */
    saveSettings() {
        try {
            const settings = {
                display: {
                    fenxing: document.getElementById('show-fenxing')?.checked,
                    strokes: document.getElementById('show-strokes')?.checked,
                    centers: document.getElementById('show-centers')?.checked,
                    divergence: document.getElementById('show-divergence')?.checked
                },
                theme: document.querySelector('.theme-btn.active')?.getAttribute('data-theme'),
                parameters: {
                    'kline-count': document.getElementById('kline-count')?.value,
                    'start-price': document.getElementById('start-price')?.value,
                    'volatility': document.getElementById('volatility')?.value,
                    'trend-bias': document.getElementById('trend-bias')?.value,
                    'fenxing-strength': document.getElementById('fenxing-strength')?.value,
                    'time-interval': document.getElementById('time-interval')?.value
                }
            };

            localStorage.setItem('chanTheorySettings', JSON.stringify(settings));
        } catch (error) {
            console.warn('保存设置失败:', error);
        }
    }

    /**
     * 处理错误
     */
    handleError(event) {
        let error;
        
        if (event.type === 'unhandledrejection') {
            error = event.reason;
        } else if (event.type === 'error') {
            error = event.error || new Error(event.message);
        } else {
            error = event.detail || event;
        }

        console.error('全局错误处理:', error);
        
        // 记录错误到本地存储
        this.logError(error);
        
        // 显示用户友好的错误信息
        if (error && error.message) {
            ErrorHandler.showNotification(`系统错误: ${error.message}`, 'error');
        }
        
        StatusManager.error('系统错误');
    }

    /**
     * 记录错误
     */
    logError(error) {
        try {
            const errorLog = {
                timestamp: new Date().toISOString(),
                message: error.message || '未知错误',
                stack: error.stack,
                userAgent: navigator.userAgent,
                url: window.location.href
            };

            const logs = JSON.parse(localStorage.getItem('errorLogs') || '[]');
            logs.push(errorLog);
            
            // 保留最近50条错误日志
            if (logs.length > 50) {
                logs.splice(0, logs.length - 50);
            }
            
            localStorage.setItem('errorLogs', JSON.stringify(logs));
        } catch (e) {
            console.warn('记录错误日志失败:', e);
        }
    }

    /**
     * 处理初始化错误
     */
    handleInitError(error) {
        document.body.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; padding: 20px; text-align: center; background: #f8fafc;">
                <div style="max-width: 500px; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                    <h1 style="color: #dc2626; margin-bottom: 20px;">❌ 系统初始化失败</h1>
                    <p style="color: #64748b; margin-bottom: 20px; line-height: 1.6;">
                        ${error.message || '未知错误'}
                    </p>
                    <button onclick="location.reload()" style="background: #2563eb; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 14px;">
                        重新加载
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * 获取系统信息
     */
    getSystemInfo() {
        return {
            version: this.version,
            userAgent: navigator.userAgent,
            screen: {
                width: screen.width,
                height: screen.height
            },
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            timestamp: new Date().toISOString()
        };
    }

    /**
     * 清理资源
     */
    cleanup() {
        // 移除事件监听器
        window.removeEventListener('error', this.handleError);
        window.removeEventListener('unhandledrejection', this.handleError);
        window.removeEventListener('resize', this.handleResize);
        
        // 清理图表
        chartManager.dispose();
        
        // 保存设置
        this.saveSettings();
        
        console.log('✅ 应用程序清理完成');
    }
}

// 创建全局应用实例
const app = new App();

/**
 * DOM内容加载完成后初始化应用
 */
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

/**
 * 页面卸载前清理资源
 */
window.addEventListener('beforeunload', () => {
    app.cleanup();
});

/**
 * 导出全局变量供调试使用
 */
window.ChanTheoryApp = {
    app,
    chartManager,
    uiManager,
    apiClient,
    ErrorHandler,
    LoadingManager,
    StatusManager
};