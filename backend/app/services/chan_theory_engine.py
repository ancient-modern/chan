from datetime import datetime
from typing import List, Optional
from models.analysis import (
    KlineData, AnalysisResult, FenxingPoint, Stroke, 
    Segment, Center, MACDData, DivergenceSignal
)
from services.kline_simulator import kline_simulator
from services.fenxing_detector import fenxing_detector
from services.stroke_builder import stroke_builder
from services.center_detector import center_detector
from services.divergence_detector import divergence_detector


class ChanTheoryEngine:
    """缠论分析引擎"""
    
    def __init__(self):
        """初始化分析引擎"""
        self.kline_simulator = kline_simulator
        self.fenxing_detector = fenxing_detector
        self.stroke_builder = stroke_builder
        self.center_detector = center_detector
        self.divergence_detector = divergence_detector
    
    def complete_analysis(
        self,
        count: int = 100,
        start_price: float = 100.0,
        time_interval: str = "1m",
        volatility: float = 0.02,
        trend_bias: float = 0.0,
        min_fenxing_strength: float = 0.5
    ) -> AnalysisResult:
        """
        完整的缠论分析
        
        Args:
            count: K线数量
            start_price: 起始价格
            time_interval: 时间间隔
            volatility: 波动率
            trend_bias: 趋势偏向
            min_fenxing_strength: 最小分型强度
            
        Returns:
            完整分析结果
        """
        # 1. 生成K线数据
        kline_data = self.kline_simulator.generate_kline_data(
            count=count,
            start_price=start_price,
            time_interval=time_interval,
            volatility=volatility,
            trend_bias=trend_bias
        )
        
        # 2. 分型识别
        fenxing_points = self.fenxing_detector.find_fenxing_points(
            kline_data, min_fenxing_strength
        )
        
        # 3. 构建笔
        strokes = self.stroke_builder.build_strokes(kline_data, fenxing_points)
        
        # 4. 构建线段
        segments = self.stroke_builder.build_segments(strokes, kline_data)
        
        # 5. 识别中枢
        centers = self.center_detector.find_centers(segments, kline_data)
        
        # 6. 计算MACD
        macd_data = self.divergence_detector.calculate_macd(kline_data)
        
        # 7. 检测背驰
        divergence_signals = self.divergence_detector.detect_divergences(
            kline_data, centers, macd_data
        )
        
        # 8. 构建完整结果
        result = AnalysisResult(
            kline_data=kline_data,
            fenxing_points=fenxing_points,
            strokes=strokes,
            segments=segments,
            centers=centers,
            macd_data=macd_data,
            divergence_signals=divergence_signals,
            analysis_time=datetime.now()
        )
        
        return result
    
    def analyze_with_existing_data(
        self,
        kline_data: List[KlineData],
        min_fenxing_strength: float = 0.5
    ) -> AnalysisResult:
        """
        使用已有K线数据进行分析
        
        Args:
            kline_data: K线数据
            min_fenxing_strength: 最小分型强度
            
        Returns:
            分析结果
        """
        # 分型识别
        fenxing_points = self.fenxing_detector.find_fenxing_points(
            kline_data, min_fenxing_strength
        )
        
        # 构建笔
        strokes = self.stroke_builder.build_strokes(kline_data, fenxing_points)
        
        # 构建线段
        segments = self.stroke_builder.build_segments(strokes, kline_data)
        
        # 识别中枢
        centers = self.center_detector.find_centers(segments, kline_data)
        
        # 计算MACD
        macd_data = self.divergence_detector.calculate_macd(kline_data)
        
        # 检测背驰
        divergence_signals = self.divergence_detector.detect_divergences(
            kline_data, centers, macd_data
        )
        
        result = AnalysisResult(
            kline_data=kline_data,
            fenxing_points=fenxing_points,
            strokes=strokes,
            segments=segments,
            centers=centers,
            macd_data=macd_data,
            divergence_signals=divergence_signals,
            analysis_time=datetime.now()
        )
        
        return result
    
    def generate_kline_only(
        self,
        count: int = 100,
        start_price: float = 100.0,
        time_interval: str = "1m",
        volatility: float = 0.02,
        trend_bias: float = 0.0
    ) -> List[KlineData]:
        """
        仅生成K线数据
        
        Args:
            count: K线数量
            start_price: 起始价格
            time_interval: 时间间隔
            volatility: 波动率
            trend_bias: 趋势偏向
            
        Returns:
            K线数据列表
        """
        return self.kline_simulator.generate_kline_data(
            count=count,
            start_price=start_price,
            time_interval=time_interval,
            volatility=volatility,
            trend_bias=trend_bias
        )
    
    def analyze_fenxing_only(
        self,
        kline_data: List[KlineData],
        min_strength: float = 0.5
    ) -> List[FenxingPoint]:
        """
        仅进行分型分析
        
        Args:
            kline_data: K线数据
            min_strength: 最小强度
            
        Returns:
            分型点列表
        """
        return self.fenxing_detector.find_fenxing_points(kline_data, min_strength)
    
    def analyze_strokes_only(
        self,
        kline_data: List[KlineData],
        fenxing_points: List[FenxingPoint]
    ) -> List[Stroke]:
        """
        仅进行笔分析
        
        Args:
            kline_data: K线数据
            fenxing_points: 分型点列表
            
        Returns:
            笔列表
        """
        return self.stroke_builder.build_strokes(kline_data, fenxing_points)
    
    def analyze_centers_only(
        self,
        segments: List[Segment],
        kline_data: List[KlineData]
    ) -> List[Center]:
        """
        仅进行中枢分析
        
        Args:
            segments: 线段列表
            kline_data: K线数据
            
        Returns:
            中枢列表
        """
        return self.center_detector.find_centers(segments, kline_data)
    
    def analyze_divergence_only(
        self,
        kline_data: List[KlineData],
        centers: List[Center]
    ) -> List[DivergenceSignal]:
        """
        仅进行背驰分析
        
        Args:
            kline_data: K线数据
            centers: 中枢列表
            
        Returns:
            背驰信号列表
        """
        macd_data = self.divergence_detector.calculate_macd(kline_data)
        return self.divergence_detector.detect_divergences(
            kline_data, centers, macd_data
        )
    
    def get_analysis_summary(self, result: AnalysisResult) -> dict:
        """
        获取分析摘要
        
        Args:
            result: 分析结果
            
        Returns:
            分析摘要
        """
        summary = {
            "basic_info": {
                "kline_count": len(result.kline_data),
                "time_range": {
                    "start": result.kline_data[0].timestamp if result.kline_data else None,
                    "end": result.kline_data[-1].timestamp if result.kline_data else None
                },
                "price_range": {
                    "start": result.kline_data[0].close if result.kline_data else None,
                    "end": result.kline_data[-1].close if result.kline_data else None,
                    "highest": max(k.high for k in result.kline_data) if result.kline_data else None,
                    "lowest": min(k.low for k in result.kline_data) if result.kline_data else None
                }
            },
            "fenxing_stats": {
                "total_count": len(result.fenxing_points),
                "top_fenxing": len([f for f in result.fenxing_points if f.type.value == "top"]),
                "bottom_fenxing": len([f for f in result.fenxing_points if f.type.value == "bottom"]),
                "avg_confidence": sum(f.confidence for f in result.fenxing_points) / len(result.fenxing_points) if result.fenxing_points else 0
            },
            "stroke_stats": self.stroke_builder.analyze_stroke_features(result.strokes),
            "center_stats": self.center_detector.analyze_center_features(result.centers),
            "divergence_stats": {
                "total_signals": len(result.divergence_signals),
                "signal_types": {},
                "avg_strength": sum(s.strength for s in result.divergence_signals) / len(result.divergence_signals) if result.divergence_signals else 0
            }
        }
        
        # 统计背驰信号类型
        for signal in result.divergence_signals:
            signal_type = signal.signal_type
            if signal_type not in summary["divergence_stats"]["signal_types"]:
                summary["divergence_stats"]["signal_types"][signal_type] = 0
            summary["divergence_stats"]["signal_types"][signal_type] += 1
        
        return summary
    
    def validate_analysis_quality(self, result: AnalysisResult) -> dict:
        """
        验证分析质量
        
        Args:
            result: 分析结果
            
        Returns:
            质量评估结果
        """
        quality = {
            "overall_score": 0.0,
            "data_quality": 0.0,
            "fenxing_quality": 0.0,
            "stroke_quality": 0.0,
            "center_quality": 0.0,
            "recommendations": []
        }
        
        # 1. 数据质量评估
        if len(result.kline_data) >= 50:
            quality["data_quality"] = min(1.0, len(result.kline_data) / 100.0)
        else:
            quality["data_quality"] = 0.5
            quality["recommendations"].append("建议增加K线数据量以获得更准确的分析")
        
        # 2. 分型质量评估
        if result.fenxing_points:
            avg_confidence = sum(f.confidence for f in result.fenxing_points) / len(result.fenxing_points)
            quality["fenxing_quality"] = avg_confidence
            
            if avg_confidence < 0.6:
                quality["recommendations"].append("分型置信度较低，建议调整分型强度阈值")
        else:
            quality["fenxing_quality"] = 0.0
            quality["recommendations"].append("未识别到有效分型，建议降低分型强度阈值")
        
        # 3. 笔质量评估
        if result.strokes:
            stroke_features = self.stroke_builder.analyze_stroke_features(result.strokes)
            if stroke_features.get("stroke_efficiency", 0) > 0.5:
                quality["stroke_quality"] = 0.8
            else:
                quality["stroke_quality"] = 0.6
                quality["recommendations"].append("笔的效率较低，可能存在过度分割")
        else:
            quality["stroke_quality"] = 0.0
            quality["recommendations"].append("未构建有效的笔，检查分型识别结果")
        
        # 4. 中枢质量评估
        if result.centers:
            avg_strength = sum(c.strength for c in result.centers) / len(result.centers)
            quality["center_quality"] = avg_strength
            
            if avg_strength < 0.5:
                quality["recommendations"].append("中枢强度较低，建议检查线段构建逻辑")
        else:
            quality["center_quality"] = 0.0
            quality["recommendations"].append("未识别到有效中枢，可能数据量不足或市场趋势性较强")
        
        # 计算总体质量
        quality["overall_score"] = (
            quality["data_quality"] * 0.2 +
            quality["fenxing_quality"] * 0.3 +
            quality["stroke_quality"] * 0.3 +
            quality["center_quality"] * 0.2
        )
        
        return quality


# 全局缠论分析引擎实例
chan_theory_engine = ChanTheoryEngine()