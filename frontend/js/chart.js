/**
 * ECharts图表管理器
 * 负责K线图表和缠论可视化
 */

class ChartManager {
    constructor() {
        this.mainChart = null;
        this.macdChart = null;
        this.patternChart = null;
        this.currentData = null;
        this.analysisResult = null;
        
        // 图表配置
        this.chartTheme = 'light';
        this.showFenxing = true;
        this.showStrokes = true;
        this.showCenters = true;
        this.showDivergence = true;
    }

    /**
     * 初始化所有图表
     */
    initCharts() {
        this.initMainChart();
        this.initMacdChart();
        this.initPatternChart();
    }

    /**
     * 初始化主K线图表
     */
    initMainChart() {
        const chartDom = document.getElementById('main-chart');
        this.mainChart = echarts.init(chartDom);
        
        const option = this.getMainChartOption();
        this.mainChart.setOption(option);

        // 响应式处理
        window.addEventListener('resize', () => {
            this.mainChart.resize();
        });
    }

    /**
     * 初始化MACD图表
     */
    initMacdChart() {
        const chartDom = document.getElementById('macd-chart');
        this.macdChart = echarts.init(chartDom);
        
        const option = this.getMacdChartOption();
        this.macdChart.setOption(option);

        // 响应式处理
        window.addEventListener('resize', () => {
            this.macdChart.resize();
        });
    }

    /**
     * 初始化模式图表
     */
    initPatternChart() {
        const chartDom = document.getElementById('pattern-chart');
        this.patternChart = echarts.init(chartDom);
        
        const option = this.getPatternChartOption();
        this.patternChart.setOption(option);

        // 响应式处理
        window.addEventListener('resize', () => {
            this.patternChart.resize();
        });
    }

    /**
     * 获取主图表配置
     */
    getMainChartOption() {
        return {
            title: {
                text: '缠论K线分析',
                left: 'center',
                textStyle: {
                    color: '#333',
                    fontSize: 16,
                    fontWeight: 'normal'
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                },
                formatter: this.getKlineTooltipFormatter()
            },
            legend: {
                data: ['K线', '分型', '笔', '中枢', '背驰'],
                top: 30
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: [],
                axisLine: {
                    lineStyle: {
                        color: '#666'
                    }
                }
            },
            yAxis: {
                type: 'value',
                scale: true,
                splitLine: {
                    lineStyle: {
                        color: '#e0e0e0'
                    }
                },
                axisLine: {
                    lineStyle: {
                        color: '#666'
                    }
                }
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 0,
                    end: 100
                },
                {
                    show: true,
                    type: 'slider',
                    top: '90%',
                    start: 0,
                    end: 100
                }
            ],
            series: [
                {
                    name: 'K线',
                    type: 'candlestick',
                    data: [],
                    itemStyle: {
                        color: '#ef4444',
                        color0: '#22c55e',
                        borderColor: '#ef4444',
                        borderColor0: '#22c55e'
                    }
                }
            ]
        };
    }

    /**
     * 获取MACD图表配置
     */
    getMacdChartOption() {
        return {
            title: {
                text: 'MACD指标',
                left: 'center',
                textStyle: {
                    color: '#333',
                    fontSize: 14
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                }
            },
            legend: {
                data: ['DIF', 'DEA', 'MACD'],
                top: 25
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '10%',
                top: '20%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: []
            },
            yAxis: {
                type: 'value',
                splitLine: {
                    lineStyle: {
                        color: '#e0e0e0'
                    }
                }
            },
            series: [
                {
                    name: 'DIF',
                    type: 'line',
                    data: [],
                    lineStyle: {
                        color: '#2563eb'
                    }
                },
                {
                    name: 'DEA',
                    type: 'line',
                    data: [],
                    lineStyle: {
                        color: '#dc2626'
                    }
                },
                {
                    name: 'MACD',
                    type: 'bar',
                    data: [],
                    itemStyle: {
                        color: function(params) {
                            return params.value >= 0 ? '#ef4444' : '#22c55e';
                        }
                    }
                }
            ]
        };
    }

    /**
     * 获取模式图表配置
     */
    getPatternChartOption() {
        return {
            title: {
                text: '技术分析模式',
                left: 'center',
                textStyle: {
                    color: '#333',
                    fontSize: 16
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                top: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: []
            },
            yAxis: {
                type: 'value',
                scale: true
            },
            dataZoom: [
                {
                    type: 'inside',
                    start: 0,
                    end: 100
                }
            ],
            series: [
                {
                    name: 'K线',
                    type: 'candlestick',
                    data: [],
                    itemStyle: {
                        color: '#ef4444',
                        color0: '#22c55e',
                        borderColor: '#ef4444',
                        borderColor0: '#22c55e'
                    }
                }
            ]
        };
    }

    /**
     * K线工具提示格式化器
     */
    getKlineTooltipFormatter() {
        return function(params) {
            if (!params || params.length === 0) return '';
            
            const data = params[0];
            if (data.seriesType === 'candlestick') {
                const values = data.value;
                return `
                    <div>
                        <strong>${data.name}</strong><br/>
                        开盘: ${values[1]}<br/>
                        最高: ${values[3]}<br/>
                        最低: ${values[2]}<br/>
                        收盘: ${values[4]}<br/>
                        涨跌: ${(values[4] - values[1]).toFixed(2)}<br/>
                        涨幅: ${((values[4] - values[1]) / values[1] * 100).toFixed(2)}%
                    </div>
                `;
            }
            return data.name + ': ' + data.value;
        };
    }

    /**
     * 更新主图表数据
     */
    updateMainChart(analysisResult) {
        if (!this.mainChart || !analysisResult) return;

        this.analysisResult = analysisResult;
        const { kline_data, fenxing_points, strokes, centers, divergence_signals } = analysisResult;

        // 准备K线数据
        const times = [];
        const klineData = [];
        
        kline_data.forEach(item => {
            const time = new Date(item.timestamp).toLocaleTimeString();
            times.push(time);
            klineData.push([
                item.open,
                item.close,
                item.low,
                item.high,
                item.volume
            ]);
        });

        // 构建系列数据
        const series = [
            {
                name: 'K线',
                type: 'candlestick',
                data: klineData,
                itemStyle: {
                    color: '#ef4444',
                    color0: '#22c55e',
                    borderColor: '#ef4444',
                    borderColor0: '#22c55e'
                }
            }
        ];

        // 添加分型标记
        if (this.showFenxing && fenxing_points && fenxing_points.length > 0) {
            const fenxingData = this.prepareFenxingData(fenxing_points, times);
            series.push(...fenxingData);
        }

        // 添加笔线段
        if (this.showStrokes && strokes && strokes.length > 0) {
            const strokeData = this.prepareStrokeData(strokes, kline_data);
            series.push(...strokeData);
        }

        // 添加中枢区域
        if (this.showCenters && centers && centers.length > 0) {
            const centerData = this.prepareCenterData(centers, kline_data);
            series.push(...centerData);
        }

        // 添加背驰信号
        if (this.showDivergence && divergence_signals && divergence_signals.length > 0) {
            const divergenceData = this.prepareDivergenceData(divergence_signals, kline_data);
            series.push(...divergenceData);
        }

        // 更新图表
        this.mainChart.setOption({
            xAxis: {
                data: times
            },
            series: series
        });
    }

    /**
     * 准备分型数据
     */
    prepareFenxingData(fenxing_points, times) {
        const topFenxing = [];
        const bottomFenxing = [];

        fenxing_points.forEach(point => {
            const timeIndex = point.index;
            if (timeIndex < times.length) {
                if (point.type === 'top') {
                    topFenxing.push([timeIndex, point.price]);
                } else {
                    bottomFenxing.push([timeIndex, point.price]);
                }
            }
        });

        return [
            {
                name: '顶分型',
                type: 'scatter',
                coordinateSystem: 'cartesian2d',
                data: topFenxing,
                symbol: 'triangle',
                symbolSize: 12,
                symbolRotate: 180,
                itemStyle: {
                    color: '#ef4444'
                },
                label: {
                    show: true,
                    position: 'top',
                    formatter: '▼',
                    color: '#ef4444',
                    fontSize: 12
                }
            },
            {
                name: '底分型',
                type: 'scatter',
                coordinateSystem: 'cartesian2d',
                data: bottomFenxing,
                symbol: 'triangle',
                symbolSize: 12,
                itemStyle: {
                    color: '#22c55e'
                },
                label: {
                    show: true,
                    position: 'bottom',
                    formatter: '▲',
                    color: '#22c55e',
                    fontSize: 12
                }
            }
        ];
    }

    /**
     * 准备笔数据
     */
    prepareStrokeData(strokes, kline_data) {
        const strokeLines = [];

        strokes.forEach((stroke, index) => {
            const startIndex = stroke.start_fenxing.index;
            const endIndex = stroke.end_fenxing.index;
            
            if (startIndex < kline_data.length && endIndex < kline_data.length) {
                strokeLines.push({
                    name: `笔${index + 1}`,
                    type: 'line',
                    data: [
                        [startIndex, stroke.start_fenxing.price],
                        [endIndex, stroke.end_fenxing.price]
                    ],
                    lineStyle: {
                        color: stroke.direction === 'up' ? '#ef4444' : '#22c55e',
                        width: 2,
                        type: 'solid'
                    },
                    symbol: 'none',
                    silent: true
                });
            }
        });

        return strokeLines;
    }

    /**
     * 准备中枢数据
     */
    prepareCenterData(centers, kline_data) {
        const centerAreas = [];

        centers.forEach((center, index) => {
            // 找到中枢在K线数据中的时间范围
            const startTime = new Date(center.start_time);
            const endTime = new Date(center.end_time);
            
            let startIndex = 0;
            let endIndex = kline_data.length - 1;
            
            for (let i = 0; i < kline_data.length; i++) {
                const klineTime = new Date(kline_data[i].timestamp);
                if (klineTime >= startTime && startIndex === 0) {
                    startIndex = i;
                }
                if (klineTime <= endTime) {
                    endIndex = i;
                }
            }

            // 创建中枢矩形区域
            centerAreas.push({
                name: `中枢${index + 1}`,
                type: 'custom',
                renderItem: (params, api) => {
                    const x1 = api.coord([startIndex, center.low_price])[0];
                    const y1 = api.coord([startIndex, center.low_price])[1];
                    const x2 = api.coord([endIndex, center.high_price])[0];
                    const y2 = api.coord([endIndex, center.high_price])[1];
                    
                    return {
                        type: 'rect',
                        shape: {
                            x: x1,
                            y: y2,
                            width: x2 - x1,
                            height: y1 - y2
                        },
                        style: {
                            fill: center.center_type === 'up' ? 'rgba(239, 68, 68, 0.1)' : 
                                  center.center_type === 'down' ? 'rgba(34, 197, 94, 0.1)' : 
                                  'rgba(100, 116, 139, 0.1)',
                            stroke: center.center_type === 'up' ? '#ef4444' : 
                                   center.center_type === 'down' ? '#22c55e' : '#64748b',
                            lineWidth: 1
                        }
                    };
                },
                data: [[startIndex, endIndex]],
                silent: true
            });
        });

        return centerAreas;
    }

    /**
     * 准备背驰数据
     */
    prepareDivergenceData(divergence_signals, kline_data) {
        const divergenceMarks = [];

        divergence_signals.forEach((signal, index) => {
            // 找到背驰信号在K线中的位置
            const signalTime = new Date(signal.signal_time);
            let signalIndex = -1;
            
            for (let i = 0; i < kline_data.length; i++) {
                const klineTime = new Date(kline_data[i].timestamp);
                if (Math.abs(klineTime - signalTime) < 60000) { // 1分钟误差范围
                    signalIndex = i;
                    break;
                }
            }

            if (signalIndex >= 0) {
                const kline = kline_data[signalIndex];
                const isTopDivergence = signal.signal_type.includes('top');
                
                divergenceMarks.push([
                    signalIndex, 
                    isTopDivergence ? kline.high * 1.02 : kline.low * 0.98
                ]);
            }
        });

        if (divergenceMarks.length > 0) {
            return [{
                name: '背驰信号',
                type: 'scatter',
                data: divergenceMarks,
                symbol: 'diamond',
                symbolSize: 15,
                itemStyle: {
                    color: '#f59e0b'
                },
                label: {
                    show: true,
                    formatter: '⚡',
                    position: 'top',
                    color: '#f59e0b',
                    fontSize: 14
                }
            }];
        }

        return [];
    }

    /**
     * 更新MACD图表
     */
    updateMacdChart(macdData) {
        if (!this.macdChart || !macdData || macdData.length === 0) return;

        const times = [];
        const difData = [];
        const deaData = [];
        const macdBarData = [];

        macdData.forEach(item => {
            const time = new Date(item.timestamp).toLocaleTimeString();
            times.push(time);
            difData.push(item.dif.toFixed(4));
            deaData.push(item.dea.toFixed(4));
            macdBarData.push(item.macd.toFixed(4));
        });

        this.macdChart.setOption({
            xAxis: {
                data: times
            },
            series: [
                {
                    name: 'DIF',
                    data: difData
                },
                {
                    name: 'DEA',
                    data: deaData
                },
                {
                    name: 'MACD',
                    data: macdBarData
                }
            ]
        });
    }

    /**
     * 更新模式图表
     */
    updatePatternChart(klineData) {
        if (!this.patternChart || !klineData) return;

        const times = [];
        const candlestickData = [];

        klineData.forEach(item => {
            const time = new Date(item.timestamp).toLocaleTimeString();
            times.push(time);
            candlestickData.push([
                item.open,
                item.close,
                item.low,
                item.high
            ]);
        });

        this.patternChart.setOption({
            xAxis: {
                data: times
            },
            series: [{
                name: 'K线',
                data: candlestickData
            }]
        });
    }

    /**
     * 切换显示设置
     */
    toggleDisplay(type, show) {
        switch (type) {
            case 'fenxing':
                this.showFenxing = show;
                break;
            case 'strokes':
                this.showStrokes = show;
                break;
            case 'centers':
                this.showCenters = show;
                break;
            case 'divergence':
                this.showDivergence = show;
                break;
        }

        // 重新渲染主图表
        if (this.analysisResult) {
            this.updateMainChart(this.analysisResult);
        }
    }

    /**
     * 导出图表
     */
    exportChart(chartType = 'main') {
        let chart;
        let filename;

        switch (chartType) {
            case 'main':
                chart = this.mainChart;
                filename = '缠论K线分析图';
                break;
            case 'macd':
                chart = this.macdChart;
                filename = 'MACD指标图';
                break;
            case 'pattern':
                chart = this.patternChart;
                filename = '技术分析模式图';
                break;
            default:
                return;
        }

        if (chart) {
            const url = chart.getDataURL({
                pixelRatio: 2,
                backgroundColor: '#fff'
            });

            const link = document.createElement('a');
            link.download = `${filename}_${new Date().toISOString().slice(0, 10)}.png`;
            link.href = url;
            link.click();
        }
    }

    /**
     * 重置缩放
     */
    resetZoom() {
        if (this.mainChart) {
            this.mainChart.dispatchAction({
                type: 'dataZoom',
                start: 0,
                end: 100
            });
        }
    }

    /**
     * 切换主题
     */
    switchTheme(theme) {
        this.chartTheme = theme;
        
        // 重新初始化图表以应用新主题
        if (this.mainChart) {
            this.mainChart.dispose();
            this.initMainChart();
            if (this.analysisResult) {
                this.updateMainChart(this.analysisResult);
            }
        }

        if (this.macdChart) {
            this.macdChart.dispose();
            this.initMacdChart();
            if (this.analysisResult && this.analysisResult.macd_data) {
                this.updateMacdChart(this.analysisResult.macd_data);
            }
        }

        if (this.patternChart) {
            this.patternChart.dispose();
            this.initPatternChart();
        }
    }

    /**
     * 销毁图表
     */
    dispose() {
        if (this.mainChart) {
            this.mainChart.dispose();
            this.mainChart = null;
        }
        if (this.macdChart) {
            this.macdChart.dispose();
            this.macdChart = null;
        }
        if (this.patternChart) {
            this.patternChart.dispose();
            this.patternChart = null;
        }
    }
}

// 创建全局图表管理器实例
const chartManager = new ChartManager();