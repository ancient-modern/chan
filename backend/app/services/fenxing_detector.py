from typing import List, Optional
from models.analysis import KlineData, FenxingPoint, FenxingType


class FenxingDetector:
    """分型检测器"""
    
    def __init__(self):
        """初始化检测器"""
        pass
    
    def find_fenxing_points(
        self,
        kline_data: List[KlineData],
        min_strength: float = 0.5
    ) -> List[FenxingPoint]:
        """
        识别所有分型点
        
        Args:
            kline_data: K线数据列表
            min_strength: 最小强度阈值
            
        Returns:
            分型点列表
        """
        if len(kline_data) < 3:
            return []
        
        fenxing_points = []
        
        # 寻找顶分型
        top_fenxings = self._find_top_fenxing(kline_data, min_strength)
        fenxing_points.extend(top_fenxings)
        
        # 寻找底分型
        bottom_fenxings = self._find_bottom_fenxing(kline_data, min_strength)
        fenxing_points.extend(bottom_fenxings)
        
        # 按时间排序
        fenxing_points.sort(key=lambda x: x.timestamp)
        
        # 过滤相邻的同类型分型
        filtered_points = self._filter_adjacent_fenxing(fenxing_points)
        
        return filtered_points
    
    def _find_top_fenxing(
        self,
        kline_data: List[KlineData],
        min_strength: float
    ) -> List[FenxingPoint]:
        """
        寻找顶分型
        
        顶分型定义：
        1. 当前K线最高价大于前一根和后一根K线最高价
        2. 连续3根K线形成局部高点
        3. 强度计算基于价格差异和确认程度
        
        Args:
            kline_data: K线数据
            min_strength: 最小强度
            
        Returns:
            顶分型点列表
        """
        top_fenxings = []
        
        for i in range(1, len(kline_data) - 1):
            current = kline_data[i]
            prev = kline_data[i - 1]
            next_kline = kline_data[i + 1]
            
            # 基本条件：当前K线高点大于前后K线高点
            if current.high > prev.high and current.high > next_kline.high:
                
                # 计算强度
                strength = self._calculate_top_fenxing_strength(
                    kline_data, i, min_strength
                )
                
                if strength >= min_strength:
                    fenxing = FenxingPoint(
                        index=i,
                        type=FenxingType.TOP,
                        high=current.high,
                        low=current.low,
                        price=current.high,  # 顶分型关键价格是最高价
                        timestamp=current.timestamp,
                        confidence=strength
                    )
                    top_fenxings.append(fenxing)
        
        return top_fenxings
    
    def _find_bottom_fenxing(
        self,
        kline_data: List[KlineData],
        min_strength: float
    ) -> List[FenxingPoint]:
        """
        寻找底分型
        
        底分型定义：
        1. 当前K线最低价小于前一根和后一根K线最低价
        2. 连续3根K线形成局部低点
        3. 强度计算基于价格差异和确认程度
        
        Args:
            kline_data: K线数据
            min_strength: 最小强度
            
        Returns:
            底分型点列表
        """
        bottom_fenxings = []
        
        for i in range(1, len(kline_data) - 1):
            current = kline_data[i]
            prev = kline_data[i - 1]
            next_kline = kline_data[i + 1]
            
            # 基本条件：当前K线低点小于前后K线低点
            if current.low < prev.low and current.low < next_kline.low:
                
                # 计算强度
                strength = self._calculate_bottom_fenxing_strength(
                    kline_data, i, min_strength
                )
                
                if strength >= min_strength:
                    fenxing = FenxingPoint(
                        index=i,
                        type=FenxingType.BOTTOM,
                        high=current.high,
                        low=current.low,
                        price=current.low,  # 底分型关键价格是最低价
                        timestamp=current.timestamp,
                        confidence=strength
                    )
                    bottom_fenxings.append(fenxing)
        
        return bottom_fenxings
    
    def _calculate_top_fenxing_strength(
        self,
        kline_data: List[KlineData],
        index: int,
        min_strength: float
    ) -> float:
        """
        计算顶分型强度
        
        强度计算因素：
        1. 价格突出程度
        2. 成交量确认
        3. 周围K线确认数量
        4. 相对位置（是否在高位）
        
        Args:
            kline_data: K线数据
            index: 当前K线索引
            min_strength: 最小强度
            
        Returns:
            强度值 (0-1)
        """
        current = kline_data[index]
        
        # 1. 价格突出程度 (30%)
        price_prominence = self._calculate_price_prominence_top(kline_data, index)
        
        # 2. 成交量确认 (20%)
        volume_confirmation = self._calculate_volume_confirmation(kline_data, index)
        
        # 3. 周围确认 (30%)
        surrounding_confirmation = self._calculate_surrounding_confirmation_top(kline_data, index)
        
        # 4. 相对位置 (20%)
        relative_position = self._calculate_relative_position_top(kline_data, index)
        
        # 加权计算总强度
        total_strength = (
            price_prominence * 0.3 +
            volume_confirmation * 0.2 +
            surrounding_confirmation * 0.3 +
            relative_position * 0.2
        )
        
        return min(1.0, max(0.0, total_strength))
    
    def _calculate_bottom_fenxing_strength(
        self,
        kline_data: List[KlineData],
        index: int,
        min_strength: float
    ) -> float:
        """
        计算底分型强度
        
        Args:
            kline_data: K线数据
            index: 当前K线索引
            min_strength: 最小强度
            
        Returns:
            强度值 (0-1)
        """
        current = kline_data[index]
        
        # 1. 价格突出程度 (30%)
        price_prominence = self._calculate_price_prominence_bottom(kline_data, index)
        
        # 2. 成交量确认 (20%)
        volume_confirmation = self._calculate_volume_confirmation(kline_data, index)
        
        # 3. 周围确认 (30%)
        surrounding_confirmation = self._calculate_surrounding_confirmation_bottom(kline_data, index)
        
        # 4. 相对位置 (20%)
        relative_position = self._calculate_relative_position_bottom(kline_data, index)
        
        # 加权计算总强度
        total_strength = (
            price_prominence * 0.3 +
            volume_confirmation * 0.2 +
            surrounding_confirmation * 0.3 +
            relative_position * 0.2
        )
        
        return min(1.0, max(0.0, total_strength))
    
    def _calculate_price_prominence_top(self, kline_data: List[KlineData], index: int) -> float:
        """计算顶分型价格突出程度"""
        current = kline_data[index]
        
        # 计算与周围K线的价格差异
        window = min(5, index, len(kline_data) - index - 1)
        if window < 1:
            return 0.5
        
        nearby_highs = []
        for i in range(max(0, index - window), min(len(kline_data), index + window + 1)):
            if i != index:
                nearby_highs.append(kline_data[i].high)
        
        if not nearby_highs:
            return 0.5
        
        max_nearby = max(nearby_highs)
        avg_nearby = sum(nearby_highs) / len(nearby_highs)
        
        # 计算突出程度
        if max_nearby == 0:
            return 0.5
        
        prominence = (current.high - max_nearby) / max_nearby
        relative_prominence = (current.high - avg_nearby) / avg_nearby
        
        # 归一化到0-1
        score = min(1.0, max(0.0, (prominence + relative_prominence * 0.5) * 10))
        return score
    
    def _calculate_price_prominence_bottom(self, kline_data: List[KlineData], index: int) -> float:
        """计算底分型价格突出程度"""
        current = kline_data[index]
        
        # 计算与周围K线的价格差异
        window = min(5, index, len(kline_data) - index - 1)
        if window < 1:
            return 0.5
        
        nearby_lows = []
        for i in range(max(0, index - window), min(len(kline_data), index + window + 1)):
            if i != index:
                nearby_lows.append(kline_data[i].low)
        
        if not nearby_lows:
            return 0.5
        
        min_nearby = min(nearby_lows)
        avg_nearby = sum(nearby_lows) / len(nearby_lows)
        
        # 计算突出程度
        if avg_nearby == 0:
            return 0.5
        
        prominence = (min_nearby - current.low) / avg_nearby
        relative_prominence = (avg_nearby - current.low) / avg_nearby
        
        # 归一化到0-1
        score = min(1.0, max(0.0, (prominence + relative_prominence * 0.5) * 10))
        return score
    
    def _calculate_volume_confirmation(self, kline_data: List[KlineData], index: int) -> float:
        """计算成交量确认程度"""
        current = kline_data[index]
        
        # 计算与前后几根K线的成交量对比
        window = min(3, index, len(kline_data) - index - 1)
        if window < 1:
            return 0.5
        
        nearby_volumes = []
        for i in range(max(0, index - window), min(len(kline_data), index + window + 1)):
            if i != index:
                nearby_volumes.append(kline_data[i].volume)
        
        if not nearby_volumes:
            return 0.5
        
        avg_volume = sum(nearby_volumes) / len(nearby_volumes)
        
        if avg_volume == 0:
            return 0.5
        
        # 成交量放大程度
        volume_ratio = current.volume / avg_volume
        
        # 归一化：成交量放大1.5倍以上给满分
        score = min(1.0, max(0.0, (volume_ratio - 0.5) / 1.0))
        return score
    
    def _calculate_surrounding_confirmation_top(self, kline_data: List[KlineData], index: int) -> float:
        """计算顶分型周围确认程度"""
        # 检查更大范围内是否确实是高点
        window = min(10, index, len(kline_data) - index - 1)
        if window < 2:
            return 0.5
        
        current_high = kline_data[index].high
        higher_count = 0
        total_count = 0
        
        for i in range(max(0, index - window), min(len(kline_data), index + window + 1)):
            if i != index:
                total_count += 1
                if kline_data[i].high < current_high:
                    higher_count += 1
        
        if total_count == 0:
            return 0.5
        
        # 周围低于当前高点的K线比例
        confirmation_ratio = higher_count / total_count
        return confirmation_ratio
    
    def _calculate_surrounding_confirmation_bottom(self, kline_data: List[KlineData], index: int) -> float:
        """计算底分型周围确认程度"""
        # 检查更大范围内是否确实是低点
        window = min(10, index, len(kline_data) - index - 1)
        if window < 2:
            return 0.5
        
        current_low = kline_data[index].low
        lower_count = 0
        total_count = 0
        
        for i in range(max(0, index - window), min(len(kline_data), index + window + 1)):
            if i != index:
                total_count += 1
                if kline_data[i].low > current_low:
                    lower_count += 1
        
        if total_count == 0:
            return 0.5
        
        # 周围高于当前低点的K线比例
        confirmation_ratio = lower_count / total_count
        return confirmation_ratio
    
    def _calculate_relative_position_top(self, kline_data: List[KlineData], index: int) -> float:
        """计算顶分型相对位置（是否在高位）"""
        # 计算在整个数据序列中的相对高度
        all_highs = [k.high for k in kline_data]
        max_high = max(all_highs)
        min_high = min(all_highs)
        
        if max_high == min_high:
            return 0.5
        
        current_high = kline_data[index].high
        relative_position = (current_high - min_high) / (max_high - min_high)
        
        # 在高位的分型更有意义
        return relative_position
    
    def _calculate_relative_position_bottom(self, kline_data: List[KlineData], index: int) -> float:
        """计算底分型相对位置（是否在低位）"""
        # 计算在整个数据序列中的相对高度
        all_lows = [k.low for k in kline_data]
        max_low = max(all_lows)
        min_low = min(all_lows)
        
        if max_low == min_low:
            return 0.5
        
        current_low = kline_data[index].low
        relative_position = (current_low - min_low) / (max_low - min_low)
        
        # 在低位的分型更有意义（1 - relative_position）
        return 1.0 - relative_position
    
    def _filter_adjacent_fenxing(self, fenxing_points: List[FenxingPoint]) -> List[FenxingPoint]:
        """
        过滤相邻的同类型分型，保留强度更高的
        
        Args:
            fenxing_points: 原始分型点列表
            
        Returns:
            过滤后的分型点列表
        """
        if len(fenxing_points) <= 1:
            return fenxing_points
        
        filtered = []
        i = 0
        
        while i < len(fenxing_points):
            current = fenxing_points[i]
            
            # 寻找相同类型的连续分型
            same_type_group = [current]
            j = i + 1
            
            while j < len(fenxing_points) and fenxing_points[j].type == current.type:
                same_type_group.append(fenxing_points[j])
                j += 1
            
            # 如果有多个相同类型的分型，选择强度最高的
            if len(same_type_group) > 1:
                best_fenxing = max(same_type_group, key=lambda x: x.confidence)
                filtered.append(best_fenxing)
            else:
                filtered.append(current)
            
            i = j
        
        return filtered
    
    def validate_fenxing_sequence(self, fenxing_points: List[FenxingPoint]) -> List[FenxingPoint]:
        """
        验证分型序列的合理性，确保顶底分型交替出现
        
        Args:
            fenxing_points: 分型点列表
            
        Returns:
            验证后的分型点列表
        """
        if len(fenxing_points) <= 1:
            return fenxing_points
        
        validated = [fenxing_points[0]]
        
        for i in range(1, len(fenxing_points)):
            current = fenxing_points[i]
            last = validated[-1]
            
            # 确保顶底分型交替
            if current.type != last.type:
                validated.append(current)
            else:
                # 如果类型相同，选择强度更高的
                if current.confidence > last.confidence:
                    validated[-1] = current
        
        return validated


# 全局分型检测器实例
fenxing_detector = FenxingDetector()