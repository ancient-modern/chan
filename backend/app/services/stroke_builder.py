from typing import List, Optional
from models.analysis import (
    KlineData, FenxingPoint, FenxingType, 
    Stroke, Segment, StrokeDirection
)


class StrokeBuilder:
    """笔线段构建器"""
    
    def __init__(self):
        """初始化构建器"""
        pass
    
    def build_strokes(
        self,
        kline_data: List[KlineData],
        fenxing_points: List[FenxingPoint]
    ) -> List[Stroke]:
        """
        根据分型点构建笔
        
        笔的定义：
        1. 连接相邻的不同类型分型点
        2. 顶分型和底分型之间形成一笔
        3. 笔必须有明确的方向（上升或下降）
        
        Args:
            kline_data: K线数据
            fenxing_points: 分型点列表
            
        Returns:
            笔列表
        """
        if len(fenxing_points) < 2:
            return []
        
        strokes = []
        
        for i in range(len(fenxing_points) - 1):
            start_fenxing = fenxing_points[i]
            end_fenxing = fenxing_points[i + 1]
            
            # 确保相邻分型类型不同
            if start_fenxing.type != end_fenxing.type:
                stroke = self._create_stroke(
                    start_fenxing, end_fenxing, kline_data
                )
                if stroke:
                    strokes.append(stroke)
        
        # 验证和优化笔序列
        optimized_strokes = self._optimize_strokes(strokes, kline_data)
        
        return optimized_strokes
    
    def _create_stroke(
        self,
        start_fenxing: FenxingPoint,
        end_fenxing: FenxingPoint,
        kline_data: List[KlineData]
    ) -> Optional[Stroke]:
        """
        创建单个笔
        
        Args:
            start_fenxing: 起始分型
            end_fenxing: 结束分型
            kline_data: K线数据
            
        Returns:
            笔对象
        """
        # 确定笔的方向
        if start_fenxing.type == FenxingType.BOTTOM and end_fenxing.type == FenxingType.TOP:
            direction = StrokeDirection.UP
            price_range = end_fenxing.price - start_fenxing.price
        elif start_fenxing.type == FenxingType.TOP and end_fenxing.type == FenxingType.BOTTOM:
            direction = StrokeDirection.DOWN
            price_range = start_fenxing.price - end_fenxing.price
        else:
            return None
        
        # 计算K线数量
        kline_count = abs(end_fenxing.index - start_fenxing.index) + 1
        
        # 验证笔的有效性
        if not self._validate_stroke(start_fenxing, end_fenxing, kline_data, direction):
            return None
        
        stroke = Stroke(
            start_fenxing=start_fenxing,
            end_fenxing=end_fenxing,
            direction=direction,
            price_range=abs(price_range),
            kline_count=kline_count,
            start_time=start_fenxing.timestamp,
            end_time=end_fenxing.timestamp
        )
        
        return stroke
    
    def _validate_stroke(
        self,
        start_fenxing: FenxingPoint,
        end_fenxing: FenxingPoint,
        kline_data: List[KlineData],
        direction: StrokeDirection
    ) -> bool:
        """
        验证笔的有效性
        
        验证规则：
        1. 笔的方向必须一致
        2. 中间不能有反向突破
        3. 价格变化必须有意义
        
        Args:
            start_fenxing: 起始分型
            end_fenxing: 结束分型
            kline_data: K线数据
            direction: 笔方向
            
        Returns:
            是否有效
        """
        start_idx = start_fenxing.index
        end_idx = end_fenxing.index
        
        # 确保索引有效
        if start_idx >= len(kline_data) or end_idx >= len(kline_data):
            return False
        
        # 价格变化阈值检查
        price_change_ratio = abs(end_fenxing.price - start_fenxing.price) / start_fenxing.price
        if price_change_ratio < 0.001:  # 价格变化太小
            return False
        
        # 检查中间K线是否有明显反向突破
        min_idx = min(start_idx, end_idx)
        max_idx = max(start_idx, end_idx)
        
        if direction == StrokeDirection.UP:
            # 上升笔：检查是否有明显下破起点
            start_low = start_fenxing.low
            for i in range(min_idx + 1, max_idx):
                if kline_data[i].low < start_low * 0.995:  # 下破超过0.5%
                    return False
        else:
            # 下降笔：检查是否有明显上破起点
            start_high = start_fenxing.high
            for i in range(min_idx + 1, max_idx):
                if kline_data[i].high > start_high * 1.005:  # 上破超过0.5%
                    return False
        
        return True
    
    def _optimize_strokes(
        self,
        strokes: List[Stroke],
        kline_data: List[KlineData]
    ) -> List[Stroke]:
        """
        优化笔序列
        
        优化规则：
        1. 合并过短的笔
        2. 处理包含关系
        3. 确保笔序列的连续性
        
        Args:
            strokes: 原始笔列表
            kline_data: K线数据
            
        Returns:
            优化后的笔列表
        """
        if len(strokes) <= 1:
            return strokes
        
        optimized = []
        i = 0
        
        while i < len(strokes):
            current_stroke = strokes[i]
            
            # 检查是否需要与下一笔合并
            if i < len(strokes) - 1:
                next_stroke = strokes[i + 1]
                merged_stroke = self._try_merge_strokes(
                    current_stroke, next_stroke, kline_data
                )
                if merged_stroke:
                    optimized.append(merged_stroke)
                    i += 2  # 跳过下一笔
                    continue
            
            optimized.append(current_stroke)
            i += 1
        
        return optimized
    
    def _try_merge_strokes(
        self,
        stroke1: Stroke,
        stroke2: Stroke,
        kline_data: List[KlineData]
    ) -> Optional[Stroke]:
        """
        尝试合并两个相邻的笔
        
        合并条件：
        1. 笔太短（时间或价格幅度）
        2. 方向一致
        3. 中间分型不够强
        
        Args:
            stroke1: 第一笔
            stroke2: 第二笔
            kline_data: K线数据
            
        Returns:
            合并后的笔或None
        """
        # 检查笔是否相邻
        if stroke1.end_fenxing.index != stroke2.start_fenxing.index:
            return None
        
        # 检查是否需要合并（笔太短）
        min_kline_count = 5
        min_price_ratio = 0.01
        
        stroke1_weak = (
            stroke1.kline_count < min_kline_count or
            stroke1.price_range / stroke1.start_fenxing.price < min_price_ratio
        )
        
        stroke2_weak = (
            stroke2.kline_count < min_kline_count or
            stroke2.price_range / stroke2.start_fenxing.price < min_price_ratio
        )
        
        # 如果都不弱，不合并
        if not stroke1_weak and not stroke2_weak:
            return None
        
        # 检查方向是否一致（允许合并同向的弱笔）
        if stroke1.direction == stroke2.direction:
            # 创建合并后的笔
            merged_stroke = Stroke(
                start_fenxing=stroke1.start_fenxing,
                end_fenxing=stroke2.end_fenxing,
                direction=stroke1.direction,
                price_range=abs(stroke2.end_fenxing.price - stroke1.start_fenxing.price),
                kline_count=stroke1.kline_count + stroke2.kline_count - 1,
                start_time=stroke1.start_time,
                end_time=stroke2.end_time
            )
            return merged_stroke
        
        return None
    
    def build_segments(
        self,
        strokes: List[Stroke],
        kline_data: List[KlineData]
    ) -> List[Segment]:
        """
        根据笔构建线段
        
        线段定义：
        1. 由多个笔组成的较长趋势
        2. 线段突破确认机制
        3. 线段之间的特征序列分析
        
        Args:
            strokes: 笔列表
            kline_data: K线数据
            
        Returns:
            线段列表
        """
        if len(strokes) < 3:
            return []
        
        segments = []
        current_segment_strokes = []
        current_direction = None
        
        for i, stroke in enumerate(strokes):
            if current_direction is None:
                # 第一笔，设定方向
                current_direction = stroke.direction
                current_segment_strokes = [stroke]
            elif stroke.direction == current_direction:
                # 同向笔，加入当前线段
                current_segment_strokes.append(stroke)
            else:
                # 反向笔，检查是否线段突破
                if self._check_segment_break(
                    current_segment_strokes, stroke, kline_data
                ):
                    # 确认线段突破，结束当前线段
                    if len(current_segment_strokes) >= 1:
                        segment = self._create_segment(current_segment_strokes)
                        if segment:
                            segments.append(segment)
                    
                    # 开始新线段
                    current_direction = stroke.direction
                    current_segment_strokes = [stroke]
                else:
                    # 未突破，可能是回调，等待进一步确认
                    current_segment_strokes.append(stroke)
        
        # 处理最后一个线段
        if len(current_segment_strokes) >= 1:
            segment = self._create_segment(current_segment_strokes)
            if segment:
                segments.append(segment)
        
        return segments
    
    def _check_segment_break(
        self,
        segment_strokes: List[Stroke],
        new_stroke: Stroke,
        kline_data: List[KlineData]
    ) -> bool:
        """
        检查是否发生线段突破
        
        突破判断标准：
        1. 价格突破前一线段的关键位置
        2. 突破幅度足够大
        3. 时间持续确认
        
        Args:
            segment_strokes: 当前线段的笔列表
            new_stroke: 新的反向笔
            kline_data: K线数据
            
        Returns:
            是否突破
        """
        if not segment_strokes:
            return True
        
        # 获取线段的关键价位
        if segment_strokes[0].direction == StrokeDirection.UP:
            # 上升线段，检查是否下破关键支撑
            segment_high = max(stroke.end_fenxing.price for stroke in segment_strokes)
            segment_low = min(stroke.start_fenxing.price for stroke in segment_strokes)
            
            # 下破幅度检查
            break_ratio = (segment_low - new_stroke.end_fenxing.price) / segment_low
            return break_ratio > 0.02  # 下破超过2%
        else:
            # 下降线段，检查是否上破关键阻力
            segment_high = max(stroke.start_fenxing.price for stroke in segment_strokes)
            segment_low = min(stroke.end_fenxing.price for stroke in segment_strokes)
            
            # 上破幅度检查
            break_ratio = (new_stroke.end_fenxing.price - segment_high) / segment_high
            return break_ratio > 0.02  # 上破超过2%
    
    def _create_segment(self, strokes: List[Stroke]) -> Optional[Segment]:
        """
        创建线段
        
        Args:
            strokes: 构成线段的笔列表
            
        Returns:
            线段对象
        """
        if not strokes:
            return None
        
        # 确定线段方向（以主要方向为准）
        up_count = sum(1 for s in strokes if s.direction == StrokeDirection.UP)
        down_count = len(strokes) - up_count
        
        if up_count > down_count:
            direction = StrokeDirection.UP
            start_price = strokes[0].start_fenxing.price
            end_price = max(s.end_fenxing.price for s in strokes if s.direction == StrokeDirection.UP)
        else:
            direction = StrokeDirection.DOWN
            start_price = strokes[0].start_fenxing.price
            end_price = min(s.end_fenxing.price for s in strokes if s.direction == StrokeDirection.DOWN)
        
        price_range = abs(end_price - start_price)
        
        segment = Segment(
            strokes=strokes,
            direction=direction,
            start_price=start_price,
            end_price=end_price,
            price_range=price_range,
            start_time=strokes[0].start_time,
            end_time=strokes[-1].end_time
        )
        
        return segment
    
    def analyze_stroke_features(self, strokes: List[Stroke]) -> dict:
        """
        分析笔的特征
        
        Args:
            strokes: 笔列表
            
        Returns:
            特征分析结果
        """
        if not strokes:
            return {}
        
        features = {
            "total_strokes": len(strokes),
            "up_strokes": 0,
            "down_strokes": 0,
            "avg_price_range": 0,
            "avg_duration": 0,
            "max_price_range": 0,
            "min_price_range": float('inf'),
            "stroke_efficiency": 0  # 笔的效率（价格变化/时间）
        }
        
        total_price_range = 0
        total_duration = 0
        
        for stroke in strokes:
            if stroke.direction == StrokeDirection.UP:
                features["up_strokes"] += 1
            else:
                features["down_strokes"] += 1
            
            total_price_range += stroke.price_range
            total_duration += stroke.kline_count
            
            features["max_price_range"] = max(features["max_price_range"], stroke.price_range)
            features["min_price_range"] = min(features["min_price_range"], stroke.price_range)
        
        if len(strokes) > 0:
            features["avg_price_range"] = total_price_range / len(strokes)
            features["avg_duration"] = total_duration / len(strokes)
            
            if total_duration > 0:
                features["stroke_efficiency"] = total_price_range / total_duration
        
        return features


# 全局笔线段构建器实例
stroke_builder = StrokeBuilder()