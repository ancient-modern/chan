/**
 * UI交互管理器
 * 负责用户界面的交互逻辑
 */

class UIManager {
    constructor() {
        this.currentPanel = 'analysis';
        this.currentPattern = null;
        this.currentTrend = null;
        this.isAnalyzing = false;
        
        this.initEventListeners();
        this.initRangeSliders();
        this.initPresets();
    }

    /**
     * 初始化事件监听器
     */
    initEventListeners() {
        // 导航切换
        this.initNavigation();
        
        // 分析控制
        this.initAnalysisControls();
        
        // 模式选择
        this.initPatternControls();
        
        // 图表控制
        this.initChartControls();
        
        // 设置面板
        this.initSettingsControls();
        
        // 状态栏控制
        this.initStatusControls();
    }

    /**
     * 初始化导航
     */
    initNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = link.getAttribute('data-tab');
                if (tab) {
                    this.switchPanel(tab);
                }
            });
        });
    }

    /**
     * 初始化分析控制
     */
    initAnalysisControls() {
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                this.startAnalysis();
            });
        }

        // 快速设置按钮
        const quickButtons = document.querySelectorAll('[data-preset]');
        quickButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const preset = btn.getAttribute('data-preset');
                this.applyPreset(preset);
            });
        });
    }

    /**
     * 初始化模式控制
     */
    initPatternControls() {
        // 模式卡片选择
        const patternCards = document.querySelectorAll('.pattern-card');
        patternCards.forEach(card => {
            card.addEventListener('click', () => {
                this.selectPattern(card);
            });
        });

        // 趋势按钮选择
        const trendBtns = document.querySelectorAll('.trend-btn');
        trendBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectTrend(btn);
            });
        });

        // 生成模式按钮
        const generatePatternBtn = document.getElementById('generate-pattern-btn');
        if (generatePatternBtn) {
            generatePatternBtn.addEventListener('click', () => {
                this.generatePattern();
            });
        }
    }

    /**
     * 初始化图表控制
     */
    initChartControls() {
        // 缩放控制
        const zoomInBtn = document.getElementById('zoom-in');
        const zoomOutBtn = document.getElementById('zoom-out');
        const resetZoomBtn = document.getElementById('reset-zoom');
        const exportChartBtn = document.getElementById('export-chart');

        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => {
                this.zoomChart('in');
            });
        }

        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => {
                this.zoomChart('out');
            });
        }

        if (resetZoomBtn) {
            resetZoomBtn.addEventListener('click', () => {
                chartManager.resetZoom();
            });
        }

        if (exportChartBtn) {
            exportChartBtn.addEventListener('click', () => {
                chartManager.exportChart('main');
            });
        }
    }

    /**
     * 初始化设置控制
     */
    initSettingsControls() {
        // 显示设置开关
        const toggles = [
            'show-fenxing',
            'show-strokes', 
            'show-centers',
            'show-divergence'
        ];

        toggles.forEach(toggleId => {
            const toggle = document.getElementById(toggleId);
            if (toggle) {
                toggle.addEventListener('change', () => {
                    const type = toggleId.replace('show-', '');
                    chartManager.toggleDisplay(type, toggle.checked);
                });
            }
        });

        // 主题切换
        const themeBtns = document.querySelectorAll('.theme-btn');
        themeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTheme(btn);
            });
        });

        // 动画速度设置
        const animationSpeed = document.getElementById('animation-speed');
        if (animationSpeed) {
            animationSpeed.addEventListener('change', () => {
                this.setAnimationSpeed(animationSpeed.value);
            });
        }
    }

    /**
     * 初始化状态栏控制
     */
    initStatusControls() {
        const clearDataBtn = document.getElementById('clear-data');
        const exportDataBtn = document.getElementById('export-data');

        if (clearDataBtn) {
            clearDataBtn.addEventListener('click', () => {
                this.clearData();
            });
        }

        if (exportDataBtn) {
            exportDataBtn.addEventListener('click', () => {
                this.exportData();
            });
        }
    }

    /**
     * 初始化范围滑块
     */
    initRangeSliders() {
        const rangeInputs = document.querySelectorAll('input[type="range"]');
        rangeInputs.forEach(input => {
            const updateValue = () => {
                const valueSpan = input.parentNode.querySelector('.range-value');
                if (valueSpan) {
                    let displayValue = input.value;
                    
                    // 根据输入类型格式化显示值
                    if (input.id === 'volatility' || input.id === 'trend-bias') {
                        displayValue = (parseFloat(input.value) * 100).toFixed(1) + '%';
                    } else if (input.id === 'fenxing-strength') {
                        displayValue = parseFloat(input.value).toFixed(1);
                    }
                    
                    valueSpan.textContent = displayValue;
                }
            };

            // 初始化显示值
            updateValue();

            // 监听值变化
            input.addEventListener('input', updateValue);
        });
    }

    /**
     * 初始化预设值
     */
    initPresets() {
        this.presets = {
            uptrend: {
                'trend-bias': 0.01,
                'volatility': 0.015,
                'fenxing-strength': 0.6
            },
            downtrend: {
                'trend-bias': -0.01,
                'volatility': 0.015,
                'fenxing-strength': 0.6
            },
            sideways: {
                'trend-bias': 0,
                'volatility': 0.01,
                'fenxing-strength': 0.4
            },
            volatile: {
                'trend-bias': 0,
                'volatility': 0.05,
                'fenxing-strength': 0.7
            }
        };
    }

    /**
     * 切换面板
     */
    switchPanel(panelName) {
        // 更新导航状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-tab="${panelName}"]`).classList.add('active');

        // 切换面板显示
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`${panelName}-panel`).classList.add('active');

        this.currentPanel = panelName;
    }

    /**
     * 应用预设值
     */
    applyPreset(presetName) {
        const preset = this.presets[presetName];
        if (!preset) return;

        // 更新预设按钮状态
        document.querySelectorAll('[data-preset]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-preset="${presetName}"]`).classList.add('active');

        // 应用预设值
        Object.keys(preset).forEach(inputId => {
            const input = document.getElementById(inputId);
            if (input) {
                input.value = preset[inputId];
                // 触发change事件以更新显示
                input.dispatchEvent(new Event('input'));
            }
        });

        ErrorHandler.showNotification(`已应用${this.getPresetName(presetName)}预设`, 'success');
    }

    /**
     * 获取预设名称
     */
    getPresetName(presetName) {
        const names = {
            uptrend: '上升趋势',
            downtrend: '下降趋势',
            sideways: '横盘整理',
            volatile: '高波动'
        };
        return names[presetName] || presetName;
    }

    /**
     * 开始分析
     */
    async startAnalysis() {
        if (this.isAnalyzing) return;

        this.isAnalyzing = true;
        this.updateAnalyzeButton(true);

        try {
            LoadingManager.show('正在生成K线数据并进行缠论分析...');
            StatusManager.loading('分析中');

            // 获取分析参数
            const params = this.getAnalysisParams();

            // 调用完整分析API
            const response = await apiClient.completeAnalysis(params);

            if (response.success) {
                const { analysis_result, summary, quality } = response.data;

                // 更新图表
                chartManager.updateMainChart(analysis_result);
                chartManager.updateMacdChart(analysis_result.macd_data);

                // 更新分析摘要
                this.updateAnalysisSummary(summary);

                // 更新质量评估
                this.updateQualityMetrics(quality);

                ErrorHandler.showNotification('缠论分析完成', 'success');
                StatusManager.update('分析完成', 'success');
            } else {
                throw new Error(response.message || '分析失败');
            }

        } catch (error) {
            ErrorHandler.show(error, '缠论分析');
            StatusManager.error('分析失败');
        } finally {
            LoadingManager.hide();
            this.isAnalyzing = false;
            this.updateAnalyzeButton(false);
        }
    }

    /**
     * 获取分析参数
     */
    getAnalysisParams() {
        return {
            count: parseInt(document.getElementById('kline-count').value) || 100,
            start_price: parseFloat(document.getElementById('start-price').value) || 100,
            time_interval: document.getElementById('time-interval').value || '1m',
            volatility: parseFloat(document.getElementById('volatility').value) || 0.02,
            trend_bias: parseFloat(document.getElementById('trend-bias').value) || 0,
            analysis_type: 'complete'
        };
    }

    /**
     * 更新分析按钮状态
     */
    updateAnalyzeButton(analyzing) {
        const btn = document.getElementById('analyze-btn');
        if (!btn) return;

        if (analyzing) {
            btn.disabled = true;
            btn.innerHTML = '<span class="btn-icon">⏳</span>分析中...';
        } else {
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🔍</span>开始分析';
        }
    }

    /**
     * 更新分析摘要
     */
    updateAnalysisSummary(summary) {
        if (!summary) return;

        // 更新基本信息
        this.updateSummaryValue('kline-count-display', summary.basic_info?.kline_count || 0);
        this.updateSummaryValue('fenxing-count-display', summary.fenxing_stats?.total_count || 0);
        this.updateSummaryValue('stroke-count-display', summary.stroke_stats?.total_strokes || 0);
        this.updateSummaryValue('center-count-display', summary.center_stats?.total_centers || 0);
        this.updateSummaryValue('divergence-count-display', summary.divergence_stats?.total_signals || 0);
    }

    /**
     * 更新摘要值
     */
    updateSummaryValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    /**
     * 更新质量评估
     */
    updateQualityMetrics(quality) {
        if (!quality) return;

        // 更新进度条
        this.updateProgressBar('overall-score', quality.overall_score || 0);
        this.updateProgressBar('data-quality', quality.data_quality || 0);
        this.updateProgressBar('fenxing-quality', quality.fenxing_quality || 0);

        // 更新建议
        this.updateRecommendations(quality.recommendations || []);
    }

    /**
     * 更新进度条
     */
    updateProgressBar(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            const percentage = Math.round(value * 100);
            element.style.width = `${percentage}%`;
            element.title = `${percentage}%`;
        }
    }

    /**
     * 更新建议列表
     */
    updateRecommendations(recommendations) {
        const container = document.getElementById('recommendations-list');
        if (!container) return;

        if (recommendations.length === 0) {
            container.innerHTML = '<p class="no-data">分析质量良好，暂无建议</p>';
            return;
        }

        const list = document.createElement('ul');
        recommendations.forEach(rec => {
            const item = document.createElement('li');
            item.textContent = rec;
            list.appendChild(item);
        });

        container.innerHTML = '';
        container.appendChild(list);
    }

    /**
     * 选择模式
     */
    selectPattern(card) {
        // 更新卡片状态
        document.querySelectorAll('.pattern-card').forEach(c => {
            c.classList.remove('active');
        });
        card.classList.add('active');

        this.currentPattern = card.getAttribute('data-pattern');
    }

    /**
     * 选择趋势
     */
    selectTrend(btn) {
        // 更新按钮状态
        document.querySelectorAll('.trend-btn').forEach(b => {
            b.classList.remove('active');
        });
        btn.classList.add('active');

        this.currentTrend = btn.getAttribute('data-trend');
    }

    /**
     * 生成模式
     */
    async generatePattern() {
        try {
            LoadingManager.show('正在生成技术分析模式...');

            let response;
            const params = {
                count: 100,
                start_price: 100,
                volatility: 0.02
            };

            if (this.currentPattern) {
                // 生成特定模式
                response = await apiClient.generatePatternData(this.currentPattern, params);
            } else if (this.currentTrend) {
                // 生成特定趋势
                response = await apiClient.generateTrendingData(this.currentTrend, params);
            } else {
                throw new Error('请选择一个模式或趋势');
            }

            if (response.success) {
                chartManager.updatePatternChart(response.data.kline_data);
                ErrorHandler.showNotification('模式生成完成', 'success');
            } else {
                throw new Error(response.message || '生成失败');
            }

        } catch (error) {
            ErrorHandler.show(error, '模式生成');
        } finally {
            LoadingManager.hide();
        }
    }

    /**
     * 图表缩放
     */
    zoomChart(direction) {
        // ECharts缩放功能需要通过dispatchAction实现
        if (chartManager.mainChart) {
            const zoomDelta = direction === 'in' ? 0.1 : -0.1;
            // 这里可以实现具体的缩放逻辑
            ErrorHandler.showNotification(`图表${direction === 'in' ? '放大' : '缩小'}`, 'info', 1000);
        }
    }

    /**
     * 切换主题
     */
    switchTheme(btn) {
        // 更新主题按钮状态
        document.querySelectorAll('.theme-btn').forEach(b => {
            b.classList.remove('active');
        });
        btn.classList.add('active');

        const theme = btn.getAttribute('data-theme');
        chartManager.switchTheme(theme);

        // 应用页面主题
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }

        ErrorHandler.showNotification(`已切换到${theme === 'dark' ? '暗色' : '亮色'}主题`, 'success');
    }

    /**
     * 设置动画速度
     */
    setAnimationSpeed(speed) {
        // 这里可以设置图表动画速度
        const speeds = {
            fast: 300,
            normal: 500,
            slow: 1000,
            none: 0
        };

        const duration = speeds[speed] || 500;
        // 应用到ECharts配置中
        ErrorHandler.showNotification(`动画速度已设置为${speed}`, 'info', 1000);
    }

    /**
     * 清除数据
     */
    clearData() {
        if (confirm('确定要清除所有数据吗？')) {
            // 清除图表数据
            if (chartManager.mainChart) {
                chartManager.mainChart.clear();
            }
            if (chartManager.macdChart) {
                chartManager.macdChart.clear();
            }
            if (chartManager.patternChart) {
                chartManager.patternChart.clear();
            }

            // 重置摘要信息
            this.resetSummary();

            ErrorHandler.showNotification('数据已清除', 'success');
            StatusManager.ready();
        }
    }

    /**
     * 重置摘要
     */
    resetSummary() {
        const summaryElements = [
            'kline-count-display',
            'fenxing-count-display', 
            'stroke-count-display',
            'center-count-display',
            'divergence-count-display'
        ];

        summaryElements.forEach(id => {
            this.updateSummaryValue(id, '-');
        });

        // 重置进度条
        ['overall-score', 'data-quality', 'fenxing-quality'].forEach(id => {
            this.updateProgressBar(id, 0);
        });

        // 重置建议
        this.updateRecommendations([]);
    }

    /**
     * 导出数据
     */
    exportData() {
        if (!chartManager.analysisResult) {
            ErrorHandler.showNotification('没有可导出的数据', 'warning');
            return;
        }

        try {
            const data = {
                timestamp: new Date().toISOString(),
                analysis_result: chartManager.analysisResult,
                parameters: this.getAnalysisParams()
            };

            const blob = new Blob([JSON.stringify(data, null, 2)], {
                type: 'application/json'
            });

            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `缠论分析数据_${new Date().toISOString().slice(0, 10)}.json`;
            link.click();

            URL.revokeObjectURL(url);
            ErrorHandler.showNotification('数据导出完成', 'success');

        } catch (error) {
            ErrorHandler.show(error, '数据导出');
        }
    }

    /**
     * 显示加载状态
     */
    showLoading(message) {
        LoadingManager.show(message);
    }

    /**
     * 隐藏加载状态
     */
    hideLoading() {
        LoadingManager.hide();
    }
}

// 创建全局UI管理器实例
const uiManager = new UIManager();