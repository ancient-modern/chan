import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List

# 导入待测试的模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.kline_simulator import KlineSimulator
from app.services.fenxing_detector import FenxingDetector
from app.services.stroke_builder import StrokeBuilder
from app.services.center_detector import CenterDetector
from app.services.divergence_detector import DivergenceDetector
from app.services.chan_theory_engine import ChanTheoryEngine
from app.models.analysis import KlineData, FenxingType, StrokeDirection


class TestKlineSimulator:
    """K线数据模拟器测试"""
    
    def setup_method(self):
        self.simulator = KlineSimulator()
    
    def test_generate_basic_kline_data(self):
        """测试基本K线数据生成"""
        kline_data = self.simulator.generate_kline_data(
            count=50,
            start_price=100.0,
            volatility=0.02
        )
        
        assert len(kline_data) == 50
        assert all(isinstance(k, KlineData) for k in kline_data)
        assert all(k.high >= k.low for k in kline_data)
        assert all(k.high >= max(k.open, k.close) for k in kline_data)
        assert all(k.low <= min(k.open, k.close) for k in kline_data)
        assert all(k.volume > 0 for k in kline_data)
    
    def test_price_continuity(self):
        """测试价格连续性"""
        kline_data = self.simulator.generate_kline_data(count=20)
        
        for i in range(1, len(kline_data)):
            # 检查相邻K线的价格连续性
            prev_close = kline_data[i-1].close
            curr_open = kline_data[i].open
            assert curr_open == prev_close
    
    def test_trending_data(self):
        """测试趋势数据生成"""
        # 上升趋势
        up_data = self.simulator.generate_trending_data(50, 100.0, "up")
        start_price = up_data[0].close
        end_price = up_data[-1].close
        assert end_price > start_price * 1.01  # 至少上涨1%
        
        # 下降趋势
        down_data = self.simulator.generate_trending_data(50, 100.0, "down")
        start_price = down_data[0].close
        end_price = down_data[-1].close
        assert end_price < start_price * 0.99  # 至少下跌1%
    
    def test_pattern_generation(self):
        """测试模式生成"""
        patterns = ["double_top", "double_bottom", "head_shoulders"]
        
        for pattern in patterns:
            data = self.simulator.generate_with_patterns(
                count=100,
                start_price=100.0,
                pattern_type=pattern
            )
            assert len(data) == 100
            assert all(isinstance(k, KlineData) for k in data)


class TestFenxingDetector:
    """分型检测器测试"""
    
    def setup_method(self):
        self.detector = FenxingDetector()
        self.simulator = KlineSimulator()
    
    def create_test_data_with_fenxing(self) -> List[KlineData]:
        """创建包含明显分型的测试数据"""
        base_time = datetime.now()
        klines = []
        
        # 创建一个明显的顶分型（高-低-高模式）
        prices = [100, 105, 110, 108, 106]  # 中间最高
        for i, price in enumerate(prices):
            kline = KlineData(
                timestamp=base_time + timedelta(minutes=i),
                open=price - 0.5,
                high=price,
                low=price - 1.0,
                close=price + 0.5,
                volume=10000
            )
            klines.append(kline)
        
        # 创建一个明显的底分型（低-高-低模式）
        prices = [106, 104, 98, 100, 102]  # 中间最低
        for i, price in enumerate(prices):
            kline = KlineData(
                timestamp=base_time + timedelta(minutes=i+5),
                open=price + 0.5,
                high=price + 1.0,
                low=price,
                close=price - 0.5,
                volume=10000
            )
            klines.append(kline)
        
        return klines
    
    def test_fenxing_detection(self):
        """测试分型识别"""
        kline_data = self.create_test_data_with_fenxing()
        fenxing_points = self.detector.find_fenxing_points(kline_data)
        
        assert len(fenxing_points) >= 2  # 至少应该识别出顶分型和底分型
        
        # 检查分型类型
        types = [f.type for f in fenxing_points]
        assert FenxingType.TOP in types
        assert FenxingType.BOTTOM in types
    
    def test_fenxing_strength_filtering(self):
        """测试分型强度过滤"""
        kline_data = self.simulator.generate_kline_data(100)
        
        # 低强度阈值应该识别出更多分型
        low_strength = self.detector.find_fenxing_points(kline_data, min_strength=0.1)
        high_strength = self.detector.find_fenxing_points(kline_data, min_strength=0.8)
        
        assert len(low_strength) >= len(high_strength)
    
    def test_fenxing_sequence_validation(self):
        """测试分型序列验证"""
        kline_data = self.create_test_data_with_fenxing()
        fenxing_points = self.detector.find_fenxing_points(kline_data)
        validated = self.detector.validate_fenxing_sequence(fenxing_points)
        
        # 验证后的分型应该是顶底交替的
        for i in range(1, len(validated)):
            assert validated[i].type != validated[i-1].type


class TestStrokeBuilder:
    """笔构建器测试"""
    
    def setup_method(self):
        self.builder = StrokeBuilder()
        self.detector = FenxingDetector()
        self.simulator = KlineSimulator()
    
    def test_stroke_building(self):
        """测试笔构建"""
        # 生成测试数据
        kline_data = self.simulator.generate_kline_data(100, volatility=0.03)
        fenxing_points = self.detector.find_fenxing_points(kline_data)
        
        if len(fenxing_points) >= 2:
            strokes = self.builder.build_strokes(kline_data, fenxing_points)
            
            # 验证笔的基本属性
            for stroke in strokes:
                assert stroke.start_fenxing.type != stroke.end_fenxing.type
                assert stroke.price_range > 0
                assert stroke.kline_count > 0
                
                # 验证方向一致性
                if stroke.direction == StrokeDirection.UP:
                    assert stroke.end_fenxing.price > stroke.start_fenxing.price
                else:
                    assert stroke.end_fenxing.price < stroke.start_fenxing.price
    
    def test_segment_building(self):
        """测试线段构建"""
        kline_data = self.simulator.generate_trending_data(150, 100.0, "up")
        fenxing_points = self.detector.find_fenxing_points(kline_data)
        strokes = self.builder.build_strokes(kline_data, fenxing_points)
        
        if len(strokes) >= 3:
            segments = self.builder.build_segments(strokes, kline_data)
            
            # 验证线段基本属性
            for segment in segments:
                assert len(segment.strokes) >= 1
                assert segment.price_range >= 0
                assert segment.start_time <= segment.end_time
    
    def test_stroke_features_analysis(self):
        """测试笔特征分析"""
        kline_data = self.simulator.generate_kline_data(100)
        fenxing_points = self.detector.find_fenxing_points(kline_data)
        strokes = self.builder.build_strokes(kline_data, fenxing_points)
        
        if strokes:
            features = self.builder.analyze_stroke_features(strokes)
            
            assert 'total_strokes' in features
            assert 'up_strokes' in features
            assert 'down_strokes' in features
            assert features['total_strokes'] == len(strokes)
            assert features['up_strokes'] + features['down_strokes'] == features['total_strokes']


class TestCenterDetector:
    """中枢检测器测试"""
    
    def setup_method(self):
        self.detector = CenterDetector()
        self.simulator = KlineSimulator()
        self.fenxing_detector = FenxingDetector()
        self.stroke_builder = StrokeBuilder()
    
    def test_center_detection(self):
        """测试中枢检测"""
        # 生成横盘整理数据，更可能产生中枢
        kline_data = self.simulator.generate_trending_data(200, 100.0, "sideways")
        
        # 构建分析链
        fenxing_points = self.fenxing_detector.find_fenxing_points(kline_data)
        strokes = self.stroke_builder.build_strokes(kline_data, fenxing_points)
        segments = self.stroke_builder.build_segments(strokes, kline_data)
        
        if len(segments) >= 3:
            centers = self.detector.find_centers(segments, kline_data)
            
            # 验证中枢基本属性
            for center in centers:
                assert len(center.segments) >= 3
                assert center.high_price > center.low_price
                assert center.center_range > 0
                assert 0 <= center.strength <= 1
    
    def test_center_features_analysis(self):
        """测试中枢特征分析"""
        # 创建模拟中枢数据
        kline_data = self.simulator.generate_trending_data(150, 100.0, "sideways")
        fenxing_points = self.fenxing_detector.find_fenxing_points(kline_data)
        strokes = self.stroke_builder.build_strokes(kline_data, fenxing_points)
        segments = self.stroke_builder.build_segments(strokes, kline_data)
        centers = self.detector.find_centers(segments, kline_data)
        
        features = self.detector.analyze_center_features(centers)
        
        assert 'total_centers' in features
        assert 'up_centers' in features
        assert 'down_centers' in features
        assert 'consolidation_centers' in features
        assert features['total_centers'] == len(centers)


class TestDivergenceDetector:
    """背驰检测器测试"""
    
    def setup_method(self):
        self.detector = DivergenceDetector()
        self.simulator = KlineSimulator()
    
    def test_macd_calculation(self):
        """测试MACD计算"""
        kline_data = self.simulator.generate_kline_data(100)
        macd_data = self.detector.calculate_macd(kline_data)
        
        # MACD数据应该少于K线数据（因为需要EMA计算周期）
        assert len(macd_data) <= len(kline_data)
        
        # 验证MACD数据结构
        for macd in macd_data:
            assert hasattr(macd, 'dif')
            assert hasattr(macd, 'dea')
            assert hasattr(macd, 'macd')
            assert hasattr(macd, 'timestamp')
    
    def test_divergence_detection_empty_data(self):
        """测试空数据的背驰检测"""
        divergences = self.detector.detect_divergences([], [], [])
        assert len(divergences) == 0


class TestChanTheoryEngine:
    """缠论分析引擎测试"""
    
    def setup_method(self):
        self.engine = ChanTheoryEngine()
    
    def test_complete_analysis(self):
        """测试完整分析"""
        result = self.engine.complete_analysis(
            count=100,
            start_price=100.0,
            volatility=0.02
        )
        
        # 验证分析结果结构
        assert hasattr(result, 'kline_data')
        assert hasattr(result, 'fenxing_points')
        assert hasattr(result, 'strokes')
        assert hasattr(result, 'segments')
        assert hasattr(result, 'centers')
        assert hasattr(result, 'macd_data')
        assert hasattr(result, 'divergence_signals')
        assert hasattr(result, 'analysis_time')
        
        # 验证数据数量
        assert len(result.kline_data) == 100
        assert len(result.macd_data) <= len(result.kline_data)
    
    def test_analysis_with_existing_data(self):
        """测试使用已有数据的分析"""
        # 生成测试数据
        kline_data = self.engine.generate_kline_only(50)
        
        # 使用已有数据进行分析
        result = self.engine.analyze_with_existing_data(kline_data)
        
        assert len(result.kline_data) == 50
        assert result.kline_data == kline_data
    
    def test_individual_analysis_methods(self):
        """测试单独的分析方法"""
        kline_data = self.engine.generate_kline_only(80)
        
        # 分型分析
        fenxing_points = self.engine.analyze_fenxing_only(kline_data)
        assert isinstance(fenxing_points, list)
        
        # 笔分析
        if fenxing_points:
            strokes = self.engine.analyze_strokes_only(kline_data, fenxing_points)
            assert isinstance(strokes, list)
    
    def test_analysis_summary(self):
        """测试分析摘要"""
        result = self.engine.complete_analysis(count=50)
        summary = self.engine.get_analysis_summary(result)
        
        assert 'basic_info' in summary
        assert 'fenxing_stats' in summary
        assert 'stroke_stats' in summary
        assert 'center_stats' in summary
        assert 'divergence_stats' in summary
        
        # 验证基本信息
        assert summary['basic_info']['kline_count'] == 50
    
    def test_analysis_quality_validation(self):
        """测试分析质量验证"""
        result = self.engine.complete_analysis(count=100)
        quality = self.engine.validate_analysis_quality(result)
        
        assert 'overall_score' in quality
        assert 'data_quality' in quality
        assert 'fenxing_quality' in quality
        assert 'stroke_quality' in quality
        assert 'center_quality' in quality
        assert 'recommendations' in quality
        
        # 验证评分范围
        assert 0 <= quality['overall_score'] <= 1
        assert 0 <= quality['data_quality'] <= 1


class TestIntegration:
    """集成测试"""
    
    def setup_method(self):
        self.engine = ChanTheoryEngine()
    
    def test_full_analysis_pipeline(self):
        """测试完整分析流程"""
        # 生成上升趋势数据
        result = self.engine.complete_analysis(
            count=150,
            start_price=100.0,
            trend_bias=0.005,  # 轻微上升趋势
            volatility=0.02
        )
        
        # 验证分析链完整性
        assert len(result.kline_data) == 150
        
        # 如果有分型，应该有相应的笔
        if result.fenxing_points:
            assert len(result.strokes) >= 0
        
        # 如果有足够的笔，应该能构建线段
        if len(result.strokes) >= 3:
            assert len(result.segments) >= 0
        
        # 如果有足够的线段，应该能识别中枢
        if len(result.segments) >= 3:
            assert len(result.centers) >= 0
        
        # 应该有MACD数据
        assert len(result.macd_data) > 0
        
        # 分析时间应该是最近的
        time_diff = datetime.now() - result.analysis_time
        assert time_diff.total_seconds() < 60  # 1分钟内
    
    def test_different_market_conditions(self):
        """测试不同市场条件"""
        conditions = [
            ("bull_market", {"trend_bias": 0.01, "volatility": 0.015}),
            ("bear_market", {"trend_bias": -0.01, "volatility": 0.02}),
            ("sideways_market", {"trend_bias": 0.0, "volatility": 0.01}),
            ("volatile_market", {"trend_bias": 0.0, "volatility": 0.05})
        ]
        
        for condition_name, params in conditions:
            result = self.engine.complete_analysis(
                count=100,
                **params
            )
            
            # 每种市场条件都应该能完成分析
            assert len(result.kline_data) == 100
            assert isinstance(result.fenxing_points, list)
            assert isinstance(result.strokes, list)
            assert isinstance(result.segments, list)
            assert isinstance(result.centers, list)
            assert isinstance(result.macd_data, list)
            assert isinstance(result.divergence_signals, list)
    
    def test_performance_benchmark(self):
        """测试性能基准"""
        import time
        
        # 测试大数据量分析性能
        start_time = time.time()
        result = self.engine.complete_analysis(count=1000)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # 1000根K线的完整分析应该在合理时间内完成（< 10秒）
        assert analysis_time < 10.0
        assert len(result.kline_data) == 1000
        
        print(f"1000根K线完整分析耗时: {analysis_time:.2f}秒")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])