from typing import List, Optional, Tuple
from models.analysis import (
    KlineData, Segment, Center, CenterType, StrokeDirection
)


class CenterDetector:
    """中枢检测器"""
    
    def __init__(self):
        """初始化检测器"""
        pass
    
    def find_centers(
        self,
        segments: List[Segment],
        kline_data: List[KlineData]
    ) -> List[Center]:
        """
        识别中枢
        
        中枢定义：
        1. 至少由3个连续的次级走势类型重叠部分构成
        2. 中枢的高点和低点确定
        3. 区分上涨中枢和下跌中枢
        
        Args:
            segments: 线段列表
            kline_data: K线数据
            
        Returns:
            中枢列表
        """
        if len(segments) < 3:
            return []
        
        centers = []
        
        # 滑动窗口寻找中枢
        for i in range(len(segments) - 2):
            for j in range(i + 3, len(segments) + 1):
                candidate_segments = segments[i:j]
                center = self._analyze_potential_center(candidate_segments)
                
                if center:
                    # 验证中枢有效性
                    if self._validate_center(center, kline_data):
                        centers.append(center)
        
        # 去重和优化中枢
        optimized_centers = self._optimize_centers(centers)
        
        return optimized_centers
    
    def _analyze_potential_center(self, segments: List[Segment]) -> Optional[Center]:
        """
        分析潜在中枢
        
        Args:
            segments: 候选线段列表
            
        Returns:
            中枢对象或None
        """
        if len(segments) < 3:
            return None
        
        # 计算重叠区间
        overlap_range = self._calculate_overlap_range(segments)
        if not overlap_range:
            return None
        
        high_price, low_price = overlap_range
        
        # 检查重叠区间是否有效
        if high_price <= low_price:
            return None
        
        # 判断中枢类型
        center_type = self._determine_center_type(segments)
        
        # 计算中枢强度
        strength = self._calculate_center_strength(segments, overlap_range)
        
        center = Center(
            segments=segments,
            center_type=center_type,
            high_price=high_price,
            low_price=low_price,
            center_range=high_price - low_price,
            start_time=segments[0].start_time,
            end_time=segments[-1].end_time,
            strength=strength
        )
        
        return center
    
    def _calculate_overlap_range(self, segments: List[Segment]) -> Optional[Tuple[float, float]]:
        """
        计算线段重叠区间
        
        Args:
            segments: 线段列表
            
        Returns:
            (high_price, low_price) 或 None
        """
        if len(segments) < 3:
            return None
        
        # 获取每个线段的价格区间
        segment_ranges = []
        for segment in segments:
            segment_high = max(segment.start_price, segment.end_price)
            segment_low = min(segment.start_price, segment.end_price)
            
            # 扩展区间以包含线段内的所有笔
            for stroke in segment.strokes:
                stroke_high = max(stroke.start_fenxing.price, stroke.end_fenxing.price)
                stroke_low = min(stroke.start_fenxing.price, stroke.end_fenxing.price)
                segment_high = max(segment_high, stroke_high)
                segment_low = min(segment_low, stroke_low)
            
            segment_ranges.append((segment_high, segment_low))
        
        # 计算所有线段的重叠区间
        overlap_high = min(range_high for range_high, _ in segment_ranges)
        overlap_low = max(range_low for _, range_low in segment_ranges)
        
        # 检查是否有有效重叠
        if overlap_high > overlap_low:
            return (overlap_high, overlap_low)
        
        # 如果没有完全重叠，尝试放宽条件
        return self._calculate_relaxed_overlap(segment_ranges)
    
    def _calculate_relaxed_overlap(self, segment_ranges: List[Tuple[float, float]]) -> Optional[Tuple[float, float]]:
        """
        计算放宽条件的重叠区间
        
        Args:
            segment_ranges: 线段价格区间列表
            
        Returns:
            重叠区间或None
        """
        if len(segment_ranges) < 3:
            return None
        
        # 寻找至少3个线段有重叠的区间
        best_overlap = None
        max_overlap_count = 0
        
        all_prices = []
        for high, low in segment_ranges:
            all_prices.extend([high, low])
        
        all_prices.sort()
        
        # 尝试不同的价格区间
        for i in range(len(all_prices)):
            for j in range(i + 1, len(all_prices)):
                test_high = all_prices[j]
                test_low = all_prices[i]
                
                # 计算有多少线段与此区间重叠
                overlap_count = 0
                for seg_high, seg_low in segment_ranges:
                    if self._ranges_overlap((test_high, test_low), (seg_high, seg_low)):
                        overlap_count += 1
                
                if overlap_count >= 3 and overlap_count > max_overlap_count:
                    max_overlap_count = overlap_count
                    best_overlap = (test_high, test_low)
        
        return best_overlap
    
    def _ranges_overlap(self, range1: Tuple[float, float], range2: Tuple[float, float]) -> bool:
        """
        检查两个价格区间是否重叠
        
        Args:
            range1: 第一个区间 (high, low)
            range2: 第二个区间 (high, low)
            
        Returns:
            是否重叠
        """
        high1, low1 = range1
        high2, low2 = range2
        
        return not (high1 <= low2 or high2 <= low1)
    
    def _determine_center_type(self, segments: List[Segment]) -> CenterType:
        """
        判断中枢类型
        
        Args:
            segments: 构成中枢的线段
            
        Returns:
            中枢类型
        """
        if not segments:
            return CenterType.CONSOLIDATION
        
        # 统计上升和下降线段
        up_segments = [s for s in segments if s.direction == StrokeDirection.UP]
        down_segments = [s for s in segments if s.direction == StrokeDirection.DOWN]
        
        # 计算整体趋势
        start_price = segments[0].start_price
        end_price = segments[-1].end_price
        
        price_change_ratio = (end_price - start_price) / start_price
        
        # 判断中枢类型
        if price_change_ratio > 0.02:  # 上涨超过2%
            return CenterType.UP
        elif price_change_ratio < -0.02:  # 下跌超过2%
            return CenterType.DOWN
        else:
            return CenterType.CONSOLIDATION
    
    def _calculate_center_strength(
        self,
        segments: List[Segment],
        overlap_range: Tuple[float, float]
    ) -> float:
        """
        计算中枢强度
        
        强度计算因素：
        1. 参与线段数量
        2. 重叠区间大小
        3. 时间持续长度
        4. 价格振荡幅度
        
        Args:
            segments: 构成中枢的线段
            overlap_range: 重叠区间
            
        Returns:
            强度值 (0-1)
        """
        high_price, low_price = overlap_range
        
        # 1. 线段数量因子 (25%)
        segment_count_factor = min(1.0, (len(segments) - 3) / 5.0 + 0.5)
        
        # 2. 重叠区间因子 (25%)
        center_range = high_price - low_price
        avg_price = (high_price + low_price) / 2
        range_ratio = center_range / avg_price
        range_factor = min(1.0, range_ratio / 0.1)  # 区间占价格10%为满分
        
        # 3. 时间持续因子 (25%)
        if len(segments) > 1:
            duration = (segments[-1].end_time - segments[0].start_time).total_seconds()
            duration_hours = duration / 3600
            duration_factor = min(1.0, duration_hours / 24.0)  # 24小时为满分
        else:
            duration_factor = 0.5
        
        # 4. 价格振荡因子 (25%)
        oscillation_factor = self._calculate_oscillation_factor(segments, overlap_range)
        
        # 加权计算总强度
        total_strength = (
            segment_count_factor * 0.25 +
            range_factor * 0.25 +
            duration_factor * 0.25 +
            oscillation_factor * 0.25
        )
        
        return min(1.0, max(0.0, total_strength))
    
    def _calculate_oscillation_factor(
        self,
        segments: List[Segment],
        overlap_range: Tuple[float, float]
    ) -> float:
        """
        计算价格振荡因子
        
        Args:
            segments: 线段列表
            overlap_range: 重叠区间
            
        Returns:
            振荡因子 (0-1)
        """
        high_price, low_price = overlap_range
        center_range = high_price - low_price
        
        if center_range == 0:
            return 0.0
        
        # 计算价格在中枢内的振荡次数和幅度
        oscillations = 0
        total_oscillation_range = 0
        
        for segment in segments:
            segment_high = max(segment.start_price, segment.end_price)
            segment_low = min(segment.start_price, segment.end_price)
            
            # 检查线段是否在中枢内振荡
            if low_price <= segment_low <= high_price and low_price <= segment_high <= high_price:
                oscillations += 1
                total_oscillation_range += abs(segment.end_price - segment.start_price)
        
        # 振荡因子计算
        oscillation_ratio = total_oscillation_range / center_range if center_range > 0 else 0
        oscillation_factor = min(1.0, oscillation_ratio / 2.0)  # 振荡幅度达到中枢2倍为满分
        
        return oscillation_factor
    
    def _validate_center(self, center: Center, kline_data: List[KlineData]) -> bool:
        """
        验证中枢有效性
        
        验证条件：
        1. 中枢区间合理
        2. 价格在区间内有足够振荡
        3. 时间持续足够
        4. 结构完整性
        
        Args:
            center: 中枢对象
            kline_data: K线数据
            
        Returns:
            是否有效
        """
        # 1. 基本条件检查
        if center.center_range <= 0:
            return False
        
        if len(center.segments) < 3:
            return False
        
        # 2. 价格区间合理性
        avg_price = (center.high_price + center.low_price) / 2
        if center.center_range / avg_price > 0.5:  # 区间过大
            return False
        
        if center.center_range / avg_price < 0.001:  # 区间过小
            return False
        
        # 3. 时间持续检查
        duration = (center.end_time - center.start_time).total_seconds()
        if duration < 3600:  # 少于1小时
            return False
        
        # 4. 强度阈值
        if center.strength < 0.3:
            return False
        
        return True
    
    def _optimize_centers(self, centers: List[Center]) -> List[Center]:
        """
        优化中枢列表，去除重叠和低质量中枢
        
        Args:
            centers: 原始中枢列表
            
        Returns:
            优化后的中枢列表
        """
        if not centers:
            return []
        
        # 按强度排序
        centers.sort(key=lambda x: x.strength, reverse=True)
        
        optimized = []
        
        for center in centers:
            # 检查是否与已有中枢重叠
            overlapped = False
            for existing in optimized:
                if self._centers_overlap(center, existing):
                    overlapped = True
                    break
            
            if not overlapped:
                optimized.append(center)
        
        # 按时间排序
        optimized.sort(key=lambda x: x.start_time)
        
        return optimized
    
    def _centers_overlap(self, center1: Center, center2: Center) -> bool:
        """
        检查两个中枢是否重叠
        
        Args:
            center1: 第一个中枢
            center2: 第二个中枢
            
        Returns:
            是否重叠
        """
        # 时间重叠检查
        time_overlap = not (
            center1.end_time <= center2.start_time or
            center2.end_time <= center1.start_time
        )
        
        # 价格重叠检查
        price_overlap = self._ranges_overlap(
            (center1.high_price, center1.low_price),
            (center2.high_price, center2.low_price)
        )
        
        return time_overlap and price_overlap
    
    def analyze_center_features(self, centers: List[Center]) -> dict:
        """
        分析中枢特征
        
        Args:
            centers: 中枢列表
            
        Returns:
            特征分析结果
        """
        if not centers:
            return {}
        
        features = {
            "total_centers": len(centers),
            "up_centers": 0,
            "down_centers": 0,
            "consolidation_centers": 0,
            "avg_strength": 0,
            "avg_duration_hours": 0,
            "avg_price_range": 0,
            "max_strength": 0,
            "min_strength": 1.0
        }
        
        total_strength = 0
        total_duration = 0
        total_range = 0
        
        for center in centers:
            # 统计类型
            if center.center_type == CenterType.UP:
                features["up_centers"] += 1
            elif center.center_type == CenterType.DOWN:
                features["down_centers"] += 1
            else:
                features["consolidation_centers"] += 1
            
            # 累计统计
            total_strength += center.strength
            total_range += center.center_range
            
            duration = (center.end_time - center.start_time).total_seconds() / 3600
            total_duration += duration
            
            features["max_strength"] = max(features["max_strength"], center.strength)
            features["min_strength"] = min(features["min_strength"], center.strength)
        
        # 计算平均值
        if len(centers) > 0:
            features["avg_strength"] = total_strength / len(centers)
            features["avg_duration_hours"] = total_duration / len(centers)
            features["avg_price_range"] = total_range / len(centers)
        
        return features
    
    def find_center_extensions(self, centers: List[Center]) -> List[dict]:
        """
        寻找中枢延伸
        
        Args:
            centers: 中枢列表
            
        Returns:
            中枢延伸信息列表
        """
        extensions = []
        
        for i, center in enumerate(centers):
            extension_info = {
                "center_index": i,
                "center": center,
                "extension_type": None,
                "extension_strength": 0,
                "break_direction": None
            }
            
            # 分析中枢后的走势
            if i < len(centers) - 1:
                next_center = centers[i + 1]
                extension_info.update(
                    self._analyze_center_extension(center, next_center)
                )
            
            extensions.append(extension_info)
        
        return extensions
    
    def _analyze_center_extension(self, current_center: Center, next_center: Center) -> dict:
        """
        分析中枢之间的延伸关系
        
        Args:
            current_center: 当前中枢
            next_center: 下一个中枢
            
        Returns:
            延伸分析结果
        """
        # 价格位置比较
        current_mid = (current_center.high_price + current_center.low_price) / 2
        next_mid = (next_center.high_price + next_center.low_price) / 2
        
        price_change = (next_mid - current_mid) / current_mid
        
        # 判断延伸类型
        if abs(price_change) < 0.01:  # 横向延伸
            extension_type = "horizontal"
        elif price_change > 0.05:  # 向上延伸
            extension_type = "upward"
        elif price_change < -0.05:  # 向下延伸
            extension_type = "downward"
        else:
            extension_type = "slight_trend"
        
        # 计算延伸强度
        time_gap = (next_center.start_time - current_center.end_time).total_seconds() / 3600
        strength = min(1.0, abs(price_change) * 10 + (1.0 / (time_gap + 1)))
        
        return {
            "extension_type": extension_type,
            "extension_strength": strength,
            "price_change": price_change,
            "time_gap_hours": time_gap
        }


# 全局中枢检测器实例
center_detector = CenterDetector()