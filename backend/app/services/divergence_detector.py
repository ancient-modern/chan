import numpy as np
import pandas as pd
from typing import List, Optional, Tuple
from models.analysis import (
    KlineData, Center, MACDData, DivergenceSignal,
    CenterType
)


class DivergenceDetector:
    """背驰检测器"""
    
    def __init__(self):
        """初始化检测器"""
        pass
    
    def calculate_macd(
        self,
        kline_data: List[KlineData],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> List[MACDData]:
        """
        计算MACD指标
        
        MACD = EMA(12) - EMA(26)
        Signal = EMA(MACD, 9)
        Histogram = MACD - Signal
        
        Args:
            kline_data: K线数据
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            MACD数据列表
        """
        if len(kline_data) < slow_period:
            return []
        
        # 提取收盘价
        close_prices = [k.close for k in kline_data]
        df = pd.DataFrame({'close': close_prices})
        
        # 计算EMA
        ema_fast = df['close'].ewm(span=fast_period).mean()
        ema_slow = df['close'].ewm(span=slow_period).mean()
        
        # 计算MACD线 (DIF)
        macd_line = ema_fast - ema_slow
        
        # 计算信号线 (DEA)
        signal_line = macd_line.ewm(span=signal_period).mean()
        
        # 计算MACD柱状图
        histogram = macd_line - signal_line
        
        # 构建MACD数据
        macd_data = []
        for i in range(len(kline_data)):
            if i >= slow_period - 1:  # 确保有足够数据计算
                macd = MACDData(
                    timestamp=kline_data[i].timestamp,
                    dif=float(macd_line.iloc[i]),
                    dea=float(signal_line.iloc[i]),
                    macd=float(histogram.iloc[i])
                )
                macd_data.append(macd)
        
        return macd_data
    
    def detect_divergences(
        self,
        kline_data: List[KlineData],
        centers: List[Center],
        macd_data: List[MACDData]
    ) -> List[DivergenceSignal]:
        """
        检测背驰信号
        
        背驰定义：
        1. 价格创新高/新低，但MACD未创新高/新低
        2. 基于中枢的背驰分析
        3. 趋势力度对比
        
        Args:
            kline_data: K线数据
            centers: 中枢列表
            macd_data: MACD数据
            
        Returns:
            背驰信号列表
        """
        if not centers or not macd_data:
            return []
        
        divergence_signals = []
        
        for center in centers:
            # 分析中枢前后的背驰
            signals = self._analyze_center_divergence(
                center, kline_data, macd_data
            )
            divergence_signals.extend(signals)
        
        # 分析整体趋势背驰
        trend_signals = self._analyze_trend_divergence(
            kline_data, macd_data
        )
        divergence_signals.extend(trend_signals)
        
        # 去重和排序
        divergence_signals = self._optimize_divergence_signals(divergence_signals)
        
        return divergence_signals
    
    def _analyze_center_divergence(
        self,
        center: Center,
        kline_data: List[KlineData],
        macd_data: List[MACDData]
    ) -> List[DivergenceSignal]:
        """
        分析中枢相关的背驰
        
        Args:
            center: 中枢
            kline_data: K线数据
            macd_data: MACD数据
            
        Returns:
            背驰信号列表
        """
        signals = []
        
        # 获取中枢时间范围内的数据
        center_klines = self._get_klines_in_timerange(
            kline_data, center.start_time, center.end_time
        )
        center_macd = self._get_macd_in_timerange(
            macd_data, center.start_time, center.end_time
        )
        
        if not center_klines or not center_macd:
            return signals
        
        # 分析中枢突破后的背驰
        post_center_signals = self._analyze_post_center_divergence(
            center, kline_data, macd_data
        )
        signals.extend(post_center_signals)
        
        # 分析中枢内部的力度背驰
        internal_signals = self._analyze_internal_divergence(
            center, center_klines, center_macd
        )
        signals.extend(internal_signals)
        
        return signals
    
    def _analyze_post_center_divergence(
        self,
        center: Center,
        kline_data: List[KlineData],
        macd_data: List[MACDData]
    ) -> List[DivergenceSignal]:
        """
        分析中枢突破后的背驰
        
        Args:
            center: 中枢
            kline_data: K线数据
            macd_data: MACD数据
            
        Returns:
            背驰信号列表
        """
        signals = []
        
        # 获取中枢后的数据
        post_klines = [k for k in kline_data if k.timestamp > center.end_time]
        post_macd = [m for m in macd_data if m.timestamp > center.end_time]
        
        if len(post_klines) < 10:  # 数据不够
            return signals
        
        # 寻找突破确认点
        break_point = self._find_center_break_point(center, post_klines)
        if not break_point:
            return signals
        
        # 分析突破后的背驰
        if center.center_type == CenterType.UP or center.center_type == CenterType.CONSOLIDATION:
            # 寻找上破后的顶背驰
            signal = self._detect_top_divergence_after_break(
                center, break_point, post_klines, post_macd
            )
            if signal:
                signals.append(signal)
        
        if center.center_type == CenterType.DOWN or center.center_type == CenterType.CONSOLIDATION:
            # 寻找下破后的底背驰
            signal = self._detect_bottom_divergence_after_break(
                center, break_point, post_klines, post_macd
            )
            if signal:
                signals.append(signal)
        
        return signals
    
    def _analyze_internal_divergence(
        self,
        center: Center,
        center_klines: List[KlineData],
        center_macd: List[MACDData]
    ) -> List[DivergenceSignal]:
        """
        分析中枢内部的力度背驰
        
        Args:
            center: 中枢
            center_klines: 中枢内K线数据
            center_macd: 中枢内MACD数据
            
        Returns:
            背驰信号列表
        """
        signals = []
        
        if len(center_klines) < 10 or len(center_macd) < 10:
            return signals
        
        # 分析中枢内的高低点对比
        highs, lows = self._find_internal_extremes(center_klines)
        
        # 检测内部顶背驰
        for i in range(1, len(highs)):
            prev_high = highs[i-1]
            curr_high = highs[i]
            
            signal = self._check_internal_top_divergence(
                prev_high, curr_high, center, center_macd
            )
            if signal:
                signals.append(signal)
        
        # 检测内部底背驰
        for i in range(1, len(lows)):
            prev_low = lows[i-1]
            curr_low = lows[i]
            
            signal = self._check_internal_bottom_divergence(
                prev_low, curr_low, center, center_macd
            )
            if signal:
                signals.append(signal)
        
        return signals
    
    def _analyze_trend_divergence(
        self,
        kline_data: List[KlineData],
        macd_data: List[MACDData]
    ) -> List[DivergenceSignal]:
        """
        分析整体趋势背驰
        
        Args:
            kline_data: K线数据
            macd_data: MACD数据
            
        Returns:
            背驰信号列表
        """
        signals = []
        
        if len(kline_data) < 50 or len(macd_data) < 50:
            return signals
        
        # 寻找价格极值点
        price_highs = self._find_price_highs(kline_data)
        price_lows = self._find_price_lows(kline_data)
        
        # 检测顶背驰
        top_signals = self._detect_trend_top_divergence(
            price_highs, kline_data, macd_data
        )
        signals.extend(top_signals)
        
        # 检测底背驰
        bottom_signals = self._detect_trend_bottom_divergence(
            price_lows, kline_data, macd_data
        )
        signals.extend(bottom_signals)
        
        return signals
    
    def _detect_trend_top_divergence(
        self,
        price_highs: List[Tuple[int, float]],
        kline_data: List[KlineData],
        macd_data: List[MACDData]
    ) -> List[DivergenceSignal]:
        """
        检测趋势顶背驰
        
        Args:
            price_highs: 价格高点列表 [(index, price)]
            kline_data: K线数据
            macd_data: MACD数据
            
        Returns:
            背驰信号列表
        """
        signals = []
        
        if len(price_highs) < 2:
            return signals
        
        for i in range(1, len(price_highs)):
            prev_high_idx, prev_high_price = price_highs[i-1]
            curr_high_idx, curr_high_price = price_highs[i]
            
            # 价格创新高
            if curr_high_price > prev_high_price * 1.001:  # 至少高0.1%
                
                # 获取对应的MACD值
                prev_macd = self._get_macd_at_index(macd_data, prev_high_idx, kline_data)
                curr_macd = self._get_macd_at_index(macd_data, curr_high_idx, kline_data)
                
                if prev_macd and curr_macd:
                    # 检查MACD是否背驰
                    macd_divergence = self._check_macd_top_divergence(prev_macd, curr_macd)
                    
                    if macd_divergence > 0.5:  # 背驰强度阈值
                        signal = DivergenceSignal(
                            center=None,  # 趋势背驰不关联特定中枢
                            signal_time=kline_data[curr_high_idx].timestamp,
                            signal_type="trend_top_divergence",
                            strength=macd_divergence,
                            description=f"价格创新高{curr_high_price:.2f}，但MACD未创新高，形成顶背驰"
                        )
                        signals.append(signal)
        
        return signals
    
    def _detect_trend_bottom_divergence(
        self,
        price_lows: List[Tuple[int, float]],
        kline_data: List[KlineData],
        macd_data: List[MACDData]
    ) -> List[DivergenceSignal]:
        """
        检测趋势底背驰
        
        Args:
            price_lows: 价格低点列表 [(index, price)]
            kline_data: K线数据
            macd_data: MACD数据
            
        Returns:
            背驰信号列表
        """
        signals = []
        
        if len(price_lows) < 2:
            return signals
        
        for i in range(1, len(price_lows)):
            prev_low_idx, prev_low_price = price_lows[i-1]
            curr_low_idx, curr_low_price = price_lows[i]
            
            # 价格创新低
            if curr_low_price < prev_low_price * 0.999:  # 至少低0.1%
                
                # 获取对应的MACD值
                prev_macd = self._get_macd_at_index(macd_data, prev_low_idx, kline_data)
                curr_macd = self._get_macd_at_index(macd_data, curr_low_idx, kline_data)
                
                if prev_macd and curr_macd:
                    # 检查MACD是否背驰
                    macd_divergence = self._check_macd_bottom_divergence(prev_macd, curr_macd)
                    
                    if macd_divergence > 0.5:  # 背驰强度阈值
                        signal = DivergenceSignal(
                            center=None,  # 趋势背驰不关联特定中枢
                            signal_time=kline_data[curr_low_idx].timestamp,
                            signal_type="trend_bottom_divergence",
                            strength=macd_divergence,
                            description=f"价格创新低{curr_low_price:.2f}，但MACD未创新低，形成底背驰"
                        )
                        signals.append(signal)
        
        return signals
    
    def _check_macd_top_divergence(self, prev_macd: MACDData, curr_macd: MACDData) -> float:
        """
        检查MACD顶背驰强度
        
        Args:
            prev_macd: 前一个MACD数据
            curr_macd: 当前MACD数据
            
        Returns:
            背驰强度 (0-1)
        """
        # DIF线背驰检查
        dif_divergence = 0
        if prev_macd.dif > curr_macd.dif:
            dif_divergence = (prev_macd.dif - curr_macd.dif) / abs(prev_macd.dif) if prev_macd.dif != 0 else 0
        
        # MACD柱状图背驰检查
        macd_divergence = 0
        if prev_macd.macd > curr_macd.macd:
            macd_divergence = (prev_macd.macd - curr_macd.macd) / abs(prev_macd.macd) if prev_macd.macd != 0 else 0
        
        # 综合背驰强度
        total_divergence = (dif_divergence * 0.6 + macd_divergence * 0.4)
        return min(1.0, max(0.0, total_divergence * 5))  # 放大并限制在0-1
    
    def _check_macd_bottom_divergence(self, prev_macd: MACDData, curr_macd: MACDData) -> float:
        """
        检查MACD底背驰强度
        
        Args:
            prev_macd: 前一个MACD数据
            curr_macd: 当前MACD数据
            
        Returns:
            背驰强度 (0-1)
        """
        # DIF线背驰检查
        dif_divergence = 0
        if prev_macd.dif < curr_macd.dif:
            dif_divergence = (curr_macd.dif - prev_macd.dif) / abs(prev_macd.dif) if prev_macd.dif != 0 else 0
        
        # MACD柱状图背驰检查
        macd_divergence = 0
        if prev_macd.macd < curr_macd.macd:
            macd_divergence = (curr_macd.macd - prev_macd.macd) / abs(prev_macd.macd) if prev_macd.macd != 0 else 0
        
        # 综合背驰强度
        total_divergence = (dif_divergence * 0.6 + macd_divergence * 0.4)
        return min(1.0, max(0.0, total_divergence * 5))  # 放大并限制在0-1
    
    def _get_klines_in_timerange(
        self,
        kline_data: List[KlineData],
        start_time,
        end_time
    ) -> List[KlineData]:
        """获取时间范围内的K线数据"""
        return [k for k in kline_data if start_time <= k.timestamp <= end_time]
    
    def _get_macd_in_timerange(
        self,
        macd_data: List[MACDData],
        start_time,
        end_time
    ) -> List[MACDData]:
        """获取时间范围内的MACD数据"""
        return [m for m in macd_data if start_time <= m.timestamp <= end_time]
    
    def _find_center_break_point(
        self,
        center: Center,
        post_klines: List[KlineData]
    ) -> Optional[KlineData]:
        """寻找中枢突破确认点"""
        if not post_klines:
            return None
        
        # 寻找突破中枢区间的K线
        for kline in post_klines:
            if kline.high > center.high_price or kline.low < center.low_price:
                return kline
        
        return None
    
    def _detect_top_divergence_after_break(
        self,
        center: Center,
        break_point: KlineData,
        post_klines: List[KlineData],
        post_macd: List[MACDData]
    ) -> Optional[DivergenceSignal]:
        """检测突破后的顶背驰"""
        # 寻找突破后的最高点
        max_high = break_point.high
        max_high_time = break_point.timestamp
        
        for kline in post_klines[:20]:  # 检查突破后20根K线
            if kline.high > max_high:
                max_high = kline.high
                max_high_time = kline.timestamp
        
        # 检查是否形成背驰
        # 这里简化处理，实际应该更复杂的逻辑
        if max_high > center.high_price * 1.02:  # 显著突破
            return DivergenceSignal(
                center=center,
                signal_time=max_high_time,
                signal_type="post_break_top_divergence",
                strength=0.7,
                description=f"突破中枢后形成顶背驰，最高价{max_high:.2f}"
            )
        
        return None
    
    def _detect_bottom_divergence_after_break(
        self,
        center: Center,
        break_point: KlineData,
        post_klines: List[KlineData],
        post_macd: List[MACDData]
    ) -> Optional[DivergenceSignal]:
        """检测突破后的底背驰"""
        # 寻找突破后的最低点
        min_low = break_point.low
        min_low_time = break_point.timestamp
        
        for kline in post_klines[:20]:  # 检查突破后20根K线
            if kline.low < min_low:
                min_low = kline.low
                min_low_time = kline.timestamp
        
        # 检查是否形成背驰
        if min_low < center.low_price * 0.98:  # 显著突破
            return DivergenceSignal(
                center=center,
                signal_time=min_low_time,
                signal_type="post_break_bottom_divergence",
                strength=0.7,
                description=f"跌破中枢后形成底背驰，最低价{min_low:.2f}"
            )
        
        return None
    
    def _find_internal_extremes(self, klines: List[KlineData]) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        """寻找内部极值点"""
        highs = []
        lows = []
        
        for i in range(1, len(klines) - 1):
            # 寻找高点
            if klines[i].high > klines[i-1].high and klines[i].high > klines[i+1].high:
                highs.append((i, klines[i].high))
            
            # 寻找低点
            if klines[i].low < klines[i-1].low and klines[i].low < klines[i+1].low:
                lows.append((i, klines[i].low))
        
        return highs, lows
    
    def _check_internal_top_divergence(
        self,
        prev_high: Tuple[int, float],
        curr_high: Tuple[int, float],
        center: Center,
        center_macd: List[MACDData]
    ) -> Optional[DivergenceSignal]:
        """检查内部顶背驰"""
        prev_idx, prev_price = prev_high
        curr_idx, curr_price = curr_high
        
        if curr_price > prev_price * 1.001:  # 价格创新高
            # 简化的背驰检查
            return DivergenceSignal(
                center=center,
                signal_time=center.start_time,
                signal_type="internal_top_divergence",
                strength=0.6,
                description=f"中枢内部顶背驰"
            )
        
        return None
    
    def _check_internal_bottom_divergence(
        self,
        prev_low: Tuple[int, float],
        curr_low: Tuple[int, float],
        center: Center,
        center_macd: List[MACDData]
    ) -> Optional[DivergenceSignal]:
        """检查内部底背驰"""
        prev_idx, prev_price = prev_low
        curr_idx, curr_price = curr_low
        
        if curr_price < prev_price * 0.999:  # 价格创新低
            # 简化的背驰检查
            return DivergenceSignal(
                center=center,
                signal_time=center.start_time,
                signal_type="internal_bottom_divergence",
                strength=0.6,
                description=f"中枢内部底背驰"
            )
        
        return None
    
    def _find_price_highs(self, kline_data: List[KlineData], window: int = 5) -> List[Tuple[int, float]]:
        """寻找价格高点"""
        highs = []
        
        for i in range(window, len(kline_data) - window):
            is_high = True
            current_high = kline_data[i].high
            
            # 检查周围窗口内是否是最高点
            for j in range(i - window, i + window + 1):
                if j != i and kline_data[j].high >= current_high:
                    is_high = False
                    break
            
            if is_high:
                highs.append((i, current_high))
        
        return highs
    
    def _find_price_lows(self, kline_data: List[KlineData], window: int = 5) -> List[Tuple[int, float]]:
        """寻找价格低点"""
        lows = []
        
        for i in range(window, len(kline_data) - window):
            is_low = True
            current_low = kline_data[i].low
            
            # 检查周围窗口内是否是最低点
            for j in range(i - window, i + window + 1):
                if j != i and kline_data[j].low <= current_low:
                    is_low = False
                    break
            
            if is_low:
                lows.append((i, current_low))
        
        return lows
    
    def _get_macd_at_index(
        self,
        macd_data: List[MACDData],
        kline_index: int,
        kline_data: List[KlineData]
    ) -> Optional[MACDData]:
        """根据K线索引获取对应的MACD数据"""
        if kline_index >= len(kline_data):
            return None
        
        target_time = kline_data[kline_index].timestamp
        
        # 寻找最接近的MACD数据
        for macd in macd_data:
            if macd.timestamp == target_time:
                return macd
        
        # 如果没有完全匹配，寻找最接近的
        closest_macd = None
        min_diff = float('inf')
        
        for macd in macd_data:
            diff = abs((macd.timestamp - target_time).total_seconds())
            if diff < min_diff:
                min_diff = diff
                closest_macd = macd
        
        return closest_macd
    
    def _optimize_divergence_signals(self, signals: List[DivergenceSignal]) -> List[DivergenceSignal]:
        """优化背驰信号，去重和排序"""
        if not signals:
            return []
        
        # 按时间排序
        signals.sort(key=lambda x: x.signal_time)
        
        # 去除时间太接近的重复信号
        optimized = []
        for signal in signals:
            is_duplicate = False
            for existing in optimized:
                time_diff = abs((signal.signal_time - existing.signal_time).total_seconds())
                if time_diff < 3600 and signal.signal_type == existing.signal_type:  # 1小时内的同类型信号
                    if signal.strength > existing.strength:
                        # 替换为更强的信号
                        optimized.remove(existing)
                        optimized.append(signal)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                optimized.append(signal)
        
        return optimized


# 全局背驰检测器实例
divergence_detector = DivergenceDetector()