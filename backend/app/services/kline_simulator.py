import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
from models.analysis import KlineData


class KlineSimulator:
    """K线数据模拟器"""
    
    def __init__(self):
        """初始化模拟器"""
        self.random_state = np.random.RandomState(42)
    
    def generate_kline_data(
        self,
        count: int = 100,
        start_price: float = 100.0,
        start_time: Optional[datetime] = None,
        time_interval: str = "1m",
        volatility: float = 0.02,
        trend_bias: float = 0.0
    ) -> List[KlineData]:
        """
        生成模拟K线数据
        
        Args:
            count: 生成数量
            start_price: 起始价格
            start_time: 开始时间
            time_interval: 时间间隔
            volatility: 波动率
            trend_bias: 趋势偏向
            
        Returns:
            K线数据列表
        """
        if start_time is None:
            start_time = datetime.now()
        
        # 解析时间间隔
        interval_minutes = self._parse_time_interval(time_interval)
        
        # 生成价格序列
        prices = self._generate_price_series(count, start_price, volatility, trend_bias)
        
        # 生成OHLC数据
        kline_list = []
        current_time = start_time
        
        for i in range(count):
            # 生成当前K线的OHLC
            if i == 0:
                open_price = start_price
            else:
                open_price = kline_list[-1].close
            
            close_price = prices[i]
            
            # 生成高低价，确保high >= max(open, close), low <= min(open, close)
            price_range = abs(close_price - open_price) * self.random_state.uniform(0.5, 2.0)
            high_price = max(open_price, close_price) + price_range * self.random_state.uniform(0, 0.8)
            low_price = min(open_price, close_price) - price_range * self.random_state.uniform(0, 0.8)
            
            # 确保价格合理性
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # 生成成交量（基于价格波动调整）
            base_volume = 10000
            volatility_factor = abs(close_price - open_price) / open_price * 100
            volume = int(base_volume * (1 + volatility_factor) * self.random_state.uniform(0.5, 2.0))
            
            kline = KlineData(
                timestamp=current_time,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=volume
            )
            
            kline_list.append(kline)
            current_time += timedelta(minutes=interval_minutes)
        
        return kline_list
    
    def _parse_time_interval(self, interval: str) -> int:
        """解析时间间隔为分钟数"""
        interval_map = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "30m": 30,
            "1h": 60,
            "4h": 240,
            "1d": 1440
        }
        return interval_map.get(interval, 1)
    
    def _generate_price_series(
        self,
        count: int,
        start_price: float,
        volatility: float,
        trend_bias: float
    ) -> np.ndarray:
        """
        生成价格序列（几何布朗运动）
        
        Args:
            count: 数据点数量
            start_price: 起始价格
            volatility: 波动率
            trend_bias: 趋势偏向
            
        Returns:
            价格序列
        """
        # 时间步长
        dt = 1.0
        
        # 生成随机增量
        random_increments = self.random_state.normal(
            loc=trend_bias * dt,
            scale=volatility * np.sqrt(dt),
            size=count
        )
        
        # 累积增量生成价格路径
        log_returns = np.cumsum(random_increments)
        prices = start_price * np.exp(log_returns)
        
        # 添加一些技术分析模式
        prices = self._add_technical_patterns(prices)
        
        return prices
    
    def _add_technical_patterns(self, prices: np.ndarray) -> np.ndarray:
        """添加技术分析模式"""
        # 添加支撑阻力位效应
        prices = self._add_support_resistance(prices)
        
        # 添加趋势延续效应
        prices = self._add_trend_momentum(prices)
        
        return prices
    
    def _add_support_resistance(self, prices: np.ndarray) -> np.ndarray:
        """添加支撑阻力位效应"""
        modified_prices = prices.copy()
        
        # 寻找重要价位
        price_levels = np.percentile(prices, [20, 50, 80])
        
        for i in range(1, len(modified_prices)):
            current_price = modified_prices[i]
            
            # 检查是否接近支撑阻力位
            for level in price_levels:
                distance = abs(current_price - level) / level
                if distance < 0.02:  # 距离重要价位2%以内
                    # 增加在该价位停留的概率
                    if self.random_state.random() < 0.3:
                        bounce_factor = self.random_state.uniform(0.8, 1.2)
                        if current_price > level:
                            modified_prices[i] = level + (current_price - level) * bounce_factor
                        else:
                            modified_prices[i] = level - (level - current_price) * bounce_factor
        
        return modified_prices
    
    def _add_trend_momentum(self, prices: np.ndarray) -> np.ndarray:
        """添加趋势延续效应"""
        if len(prices) < 5:
            return prices
        
        modified_prices = prices.copy()
        
        # 计算移动平均来识别趋势
        window = min(10, len(prices) // 3)
        ma = pd.Series(prices).rolling(window=window).mean().fillna(method='bfill')
        
        for i in range(window, len(modified_prices)):
            # 判断趋势方向
            trend_slope = (ma.iloc[i] - ma.iloc[i-window//2]) / ma.iloc[i-window//2]
            
            # 在趋势方向上增加小幅推动
            if abs(trend_slope) > 0.01:  # 有明显趋势
                momentum_factor = self.random_state.uniform(0.001, 0.005)
                if trend_slope > 0:  # 上升趋势
                    modified_prices[i] *= (1 + momentum_factor)
                else:  # 下降趋势
                    modified_prices[i] *= (1 - momentum_factor)
        
        return modified_prices
    
    def generate_trending_data(
        self,
        count: int = 100,
        start_price: float = 100.0,
        trend_direction: str = "up",
        **kwargs
    ) -> List[KlineData]:
        """
        生成特定趋势的K线数据
        
        Args:
            count: 生成数量
            start_price: 起始价格
            trend_direction: 趋势方向 ("up", "down", "sideways")
            **kwargs: 其他参数
            
        Returns:
            K线数据列表
        """
        trend_bias_map = {
            "up": 0.01,      # 上升趋势
            "down": -0.01,   # 下降趋势
            "sideways": 0.0  # 横盘整理
        }
        
        trend_bias = trend_bias_map.get(trend_direction, 0.0)
        
        return self.generate_kline_data(
            count=count,
            start_price=start_price,
            trend_bias=trend_bias,
            **kwargs
        )
    
    def generate_with_patterns(
        self,
        count: int = 100,
        start_price: float = 100.0,
        pattern_type: str = "double_top",
        **kwargs
    ) -> List[KlineData]:
        """
        生成包含特定技术分析模式的K线数据
        
        Args:
            count: 生成数量
            start_price: 起始价格
            pattern_type: 模式类型
            **kwargs: 其他参数
            
        Returns:
            K线数据列表
        """
        if pattern_type == "double_top":
            return self._generate_double_top_pattern(count, start_price, **kwargs)
        elif pattern_type == "double_bottom":
            return self._generate_double_bottom_pattern(count, start_price, **kwargs)
        elif pattern_type == "head_shoulders":
            return self._generate_head_shoulders_pattern(count, start_price, **kwargs)
        else:
            return self.generate_kline_data(count, start_price, **kwargs)
    
    def _generate_double_top_pattern(self, count: int, start_price: float, **kwargs) -> List[KlineData]:
        """生成双顶模式"""
        # 分阶段生成：上升-回调-再次上升-下跌
        stage_counts = [count//4, count//4, count//4, count//4]
        
        # 第一阶段：上升到第一个顶部
        data1 = self.generate_trending_data(
            stage_counts[0], start_price, "up", 
            volatility=0.015, **kwargs
        )
        
        # 第二阶段：回调
        data2 = self.generate_trending_data(
            stage_counts[1], data1[-1].close, "down",
            volatility=0.02, trend_bias=-0.005, **kwargs
        )
        
        # 第三阶段：再次上升（形成双顶）
        target_price = data1[-1].close * 0.98  # 略低于第一个顶部
        data3 = self.generate_trending_data(
            stage_counts[2], data2[-1].close, "up",
            volatility=0.015, **kwargs
        )
        
        # 第四阶段：下跌确认
        data4 = self.generate_trending_data(
            stage_counts[3], data3[-1].close, "down",
            volatility=0.025, trend_bias=-0.008, **kwargs
        )
        
        return data1 + data2[1:] + data3[1:] + data4[1:]
    
    def _generate_double_bottom_pattern(self, count: int, start_price: float, **kwargs) -> List[KlineData]:
        """生成双底模式"""
        # 分阶段生成：下跌-反弹-再次下跌-上涨
        stage_counts = [count//4, count//4, count//4, count//4]
        
        # 第一阶段：下跌到第一个底部
        data1 = self.generate_trending_data(
            stage_counts[0], start_price, "down",
            volatility=0.02, **kwargs
        )
        
        # 第二阶段：反弹
        data2 = self.generate_trending_data(
            stage_counts[1], data1[-1].close, "up",
            volatility=0.015, trend_bias=0.005, **kwargs
        )
        
        # 第三阶段：再次下跌（形成双底）
        data3 = self.generate_trending_data(
            stage_counts[2], data2[-1].close, "down",
            volatility=0.02, **kwargs
        )
        
        # 第四阶段：上涨确认
        data4 = self.generate_trending_data(
            stage_counts[3], data3[-1].close, "up",
            volatility=0.025, trend_bias=0.008, **kwargs
        )
        
        return data1 + data2[1:] + data3[1:] + data4[1:]
    
    def _generate_head_shoulders_pattern(self, count: int, start_price: float, **kwargs) -> List[KlineData]:
        """生成头肩顶模式"""
        # 分阶段生成：左肩-头部-右肩-颈线突破
        stage_counts = [count//5, count//5, count//5, count//5, count//5]
        
        # 左肩
        data1 = self.generate_trending_data(
            stage_counts[0], start_price, "up",
            volatility=0.015, **kwargs
        )
        
        # 回调到颈线
        data2 = self.generate_trending_data(
            stage_counts[1], data1[-1].close, "down",
            volatility=0.02, trend_bias=-0.003, **kwargs
        )
        
        # 头部（最高点）
        data3 = self.generate_trending_data(
            stage_counts[2], data2[-1].close, "up",
            volatility=0.015, trend_bias=0.008, **kwargs
        )
        
        # 再次回调到颈线
        data4 = self.generate_trending_data(
            stage_counts[3], data3[-1].close, "down",
            volatility=0.02, trend_bias=-0.005, **kwargs
        )
        
        # 右肩（较低的高点）
        data5 = self.generate_trending_data(
            stage_counts[4], data4[-1].close, "up",
            volatility=0.015, trend_bias=0.003, **kwargs
        )
        
        return data1 + data2[1:] + data3[1:] + data4[1:] + data5[1:]


# 全局模拟器实例
kline_simulator = KlineSimulator()