/**
 * API客户端
 * 负责与后端API的通信
 */

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * 发送HTTP请求
     * @param {string} endpoint - API端点
     * @param {Object} options - 请求选项
     * @returns {Promise} 响应数据
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`API请求失败: ${endpoint}`, error);
            throw error;
        }
    }

    /**
     * GET请求
     * @param {string} endpoint - API端点
     * @param {Object} params - 查询参数
     * @returns {Promise} 响应数据
     */
    async get(endpoint, params = {}) {
        const searchParams = new URLSearchParams(params);
        const url = searchParams.toString() ? `${endpoint}?${searchParams}` : endpoint;
        
        return this.request(url, {
            method: 'GET'
        });
    }

    /**
     * POST请求
     * @param {string} endpoint - API端点
     * @param {Object} data - 请求数据
     * @returns {Promise} 响应数据
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // K线数据相关API

    /**
     * 生成K线数据
     * @param {Object} params - 生成参数
     * @returns {Promise} K线数据
     */
    async generateKlineData(params) {
        return this.post('/kline/generate', params);
    }

    /**
     * 生成特定模式的K线数据
     * @param {string} patternType - 模式类型
     * @param {Object} params - 参数
     * @returns {Promise} 模式K线数据
     */
    async generatePatternData(patternType, params = {}) {
        return this.get(`/kline/patterns/${patternType}`, params);
    }

    /**
     * 生成特定趋势的K线数据
     * @param {string} direction - 趋势方向
     * @param {Object} params - 参数
     * @returns {Promise} 趋势K线数据
     */
    async generateTrendingData(direction, params = {}) {
        return this.get(`/kline/trending/${direction}`, params);
    }

    // 缠论分析相关API

    /**
     * 完整缠论分析
     * @param {Object} params - 分析参数
     * @returns {Promise} 完整分析结果
     */
    async completeAnalysis(params) {
        return this.post('/analysis/complete', params);
    }

    /**
     * 分型分析
     * @param {Object} data - 分析数据
     * @returns {Promise} 分型分析结果
     */
    async analyzeFenxing(data) {
        return this.post('/analysis/fenxing', data);
    }

    /**
     * 笔分析
     * @param {Object} data - 分析数据
     * @returns {Promise} 笔分析结果
     */
    async analyzeStroke(data) {
        return this.post('/analysis/stroke', data);
    }

    /**
     * 中枢分析
     * @param {Object} data - 分析数据
     * @returns {Promise} 中枢分析结果
     */
    async analyzeCenter(data) {
        return this.post('/analysis/center', data);
    }

    /**
     * 背驰分析
     * @param {Object} data - 分析数据
     * @returns {Promise} 背驰分析结果
     */
    async analyzeDivergence(data) {
        return this.post('/analysis/divergence', data);
    }

    /**
     * 获取分析功能信息
     * @returns {Promise} 功能信息
     */
    async getAnalysisInfo() {
        return this.get('/analysis/summary');
    }
}

// 创建全局API客户端实例
const apiClient = new APIClient();

/**
 * 错误处理工具
 */
class ErrorHandler {
    static show(error, context = '') {
        const message = error.message || '未知错误';
        console.error(`${context}错误:`, error);
        
        // 显示用户友好的错误信息
        this.showNotification(`${context}失败: ${message}`, 'error');
    }

    static showNotification(message, type = 'info', duration = 3000) {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        // 添加样式
        this.addNotificationStyles();

        // 添加到页面
        document.body.appendChild(notification);

        // 关闭按钮事件
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.removeNotification(notification);
        });

        // 自动关闭
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification);
            }, duration);
        }

        // 显示动画
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
    }

    static getIcon(type) {
        const icons = {
            info: 'ℹ️',
            success: '✅',
            warning: '⚠️',
            error: '❌'
        };
        return icons[type] || icons.info;
    }

    static removeNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    static addNotificationStyles() {
        // 避免重复添加样式
        if (document.getElementById('notification-styles')) {
            return;
        }

        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                min-width: 300px;
                max-width: 500px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                transform: translateX(100%);
                transition: transform 0.3s ease;
            }

            .notification.show {
                transform: translateX(0);
            }

            .notification-content {
                padding: 16px;
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .notification-icon {
                font-size: 18px;
                flex-shrink: 0;
            }

            .notification-message {
                flex: 1;
                font-size: 14px;
                line-height: 1.4;
            }

            .notification-close {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                color: #666;
            }

            .notification-close:hover {
                background: #f0f0f0;
                color: #333;
            }

            .notification-error {
                border-left: 4px solid #dc2626;
            }

            .notification-success {
                border-left: 4px solid #059669;
            }

            .notification-warning {
                border-left: 4px solid #d97706;
            }

            .notification-info {
                border-left: 4px solid #2563eb;
            }

            @media (max-width: 768px) {
                .notification {
                    top: 10px;
                    right: 10px;
                    left: 10px;
                    min-width: auto;
                    max-width: none;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * 加载状态管理
 */
class LoadingManager {
    static show(message = '正在加载...') {
        const loading = document.getElementById('loading');
        const loadingText = loading.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
        loading.classList.add('show');
    }

    static hide() {
        const loading = document.getElementById('loading');
        loading.classList.remove('show');
    }
}

/**
 * 状态更新工具
 */
class StatusManager {
    static update(text, type = 'info') {
        const statusText = document.getElementById('status-text');
        const lastUpdate = document.getElementById('last-update');
        
        if (statusText) {
            statusText.textContent = text;
            statusText.className = `status-${type}`;
        }
        
        if (lastUpdate) {
            lastUpdate.textContent = new Date().toLocaleTimeString();
        }
    }

    static ready() {
        this.update('就绪', 'success');
    }

    static loading(message) {
        this.update(message, 'loading');
    }

    static error(message) {
        this.update(message, 'error');
    }
}