import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime

# 导入FastAPI应用
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.main import app


class TestAPIEndpoints:
    """API端点测试"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """测试健康检查接口"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_generate_kline_data(self, client):
        """测试K线数据生成接口"""
        request_data = {
            "count": 50,
            "start_price": 100.0,
            "time_interval": "1m",
            "volatility": 0.02,
            "trend_bias": 0.0
        }
        
        response = await client.post("/api/kline/generate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "kline_data" in data["data"]
        assert len(data["data"]["kline_data"]) == 50
        
        # 验证K线数据结构
        kline = data["data"]["kline_data"][0]
        required_fields = ["timestamp", "open", "high", "low", "close", "volume"]
        for field in required_fields:
            assert field in kline
    
    @pytest.mark.asyncio
    async def test_generate_pattern_data(self, client):
        """测试模式数据生成接口"""
        patterns = ["double_top", "double_bottom", "head_shoulders"]
        
        for pattern in patterns:
            response = await client.get(
                f"/api/kline/patterns/{pattern}",
                params={"count": 100, "start_price": 100.0}
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["data"]["pattern_type"] == pattern
            assert len(data["data"]["kline_data"]) == 100
    
    @pytest.mark.asyncio
    async def test_generate_trending_data(self, client):
        """测试趋势数据生成接口"""
        trends = ["up", "down", "sideways"]
        
        for trend in trends:
            response = await client.get(
                f"/api/kline/trending/{trend}",
                params={"count": 80, "start_price": 100.0}
            )
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["data"]["trend_direction"] == trend
            assert len(data["data"]["kline_data"]) == 80
    
    @pytest.mark.asyncio
    async def test_complete_analysis(self, client):
        """测试完整缠论分析接口"""
        request_data = {
            "count": 100,
            "start_price": 100.0,
            "time_interval": "1m",
            "volatility": 0.02,
            "trend_bias": 0.0,
            "analysis_type": "complete"
        }
        
        response = await client.post("/api/analysis/complete", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        # 验证分析结果结构
        analysis_result = data["data"]["analysis_result"]
        required_sections = [
            "kline_data", "fenxing_points", "strokes", 
            "segments", "centers", "macd_data", "divergence_signals"
        ]
        for section in required_sections:
            assert section in analysis_result
        
        # 验证摘要和质量评估
        assert "summary" in data["data"]
        assert "quality" in data["data"]
    
    @pytest.mark.asyncio
    async def test_fenxing_analysis(self, client):
        """测试分型分析接口"""
        # 首先生成K线数据
        kline_response = await client.post("/api/kline/generate", json={
            "count": 50,
            "start_price": 100.0,
            "volatility": 0.03
        })
        kline_data = kline_response.json()["data"]["kline_data"]
        
        # 进行分型分析
        request_data = {
            "kline_data": kline_data,
            "min_strength": 0.5,
            "analysis_type": "fenxing"
        }
        
        response = await client.post("/api/analysis/fenxing", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "fenxing_points" in data["data"]
    
    @pytest.mark.asyncio
    async def test_analysis_info(self, client):
        """测试分析功能信息接口"""
        response = await client.get("/api/analysis/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "features" in data["data"]
        assert "algorithms" in data["data"]
        assert "supported_patterns" in data["data"]
        assert "supported_trends" in data["data"]
    
    @pytest.mark.asyncio
    async def test_invalid_pattern_type(self, client):
        """测试无效模式类型"""
        response = await client.get("/api/kline/patterns/invalid_pattern")
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_invalid_trend_direction(self, client):
        """测试无效趋势方向"""
        response = await client.get("/api/kline/trending/invalid_trend")
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self, client):
        """测试参数验证"""
        # 测试负数数量
        response = await client.post("/api/kline/generate", json={
            "count": -10,
            "start_price": 100.0
        })
        assert response.status_code == 422  # Validation error
        
        # 测试零价格
        response = await client.post("/api/kline/generate", json={
            "count": 50,
            "start_price": 0
        })
        assert response.status_code == 422  # Validation error
        
        # 测试过大的数量
        response = await client.post("/api/kline/generate", json={
            "count": 2000,
            "start_price": 100.0
        })
        assert response.status_code == 422  # Validation error


class TestAPIIntegration:
    """API集成测试"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_analysis_workflow(self, client):
        """测试完整的分析工作流"""
        # 1. 生成K线数据
        kline_response = await client.post("/api/kline/generate", json={
            "count": 100,
            "start_price": 100.0,
            "volatility": 0.025,
            "trend_bias": 0.005
        })
        assert kline_response.status_code == 200
        kline_data = kline_response.json()["data"]["kline_data"]
        
        # 2. 进行分型分析
        fenxing_response = await client.post("/api/analysis/fenxing", json={
            "kline_data": kline_data,
            "min_strength": 0.4,
            "analysis_type": "fenxing"
        })
        assert fenxing_response.status_code == 200
        
        # 3. 完整分析
        complete_response = await client.post("/api/analysis/complete", json={
            "count": 100,
            "start_price": 100.0,
            "volatility": 0.025,
            "analysis_type": "complete"
        })
        assert complete_response.status_code == 200
        
        complete_data = complete_response.json()["data"]
        
        # 验证分析质量
        quality = complete_data["quality"]
        assert 0 <= quality["overall_score"] <= 1
        assert 0 <= quality["data_quality"] <= 1
    
    @pytest.mark.asyncio
    async def test_different_market_scenarios(self, client):
        """测试不同市场场景的API响应"""
        scenarios = [
            {"name": "bull_market", "trend_bias": 0.01, "volatility": 0.02},
            {"name": "bear_market", "trend_bias": -0.01, "volatility": 0.025},
            {"name": "volatile_market", "trend_bias": 0.0, "volatility": 0.05},
            {"name": "stable_market", "trend_bias": 0.0, "volatility": 0.01}
        ]
        
        for scenario in scenarios:
            response = await client.post("/api/analysis/complete", json={
                "count": 150,
                "start_price": 100.0,
                "trend_bias": scenario["trend_bias"],
                "volatility": scenario["volatility"],
                "analysis_type": "complete"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # 验证每种场景都能生成有效的分析结果
            analysis_result = data["data"]["analysis_result"]
            assert len(analysis_result["kline_data"]) == 150
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, client):
        """测试负载下的性能"""
        import time
        
        # 并发发送多个分析请求
        async def single_analysis():
            response = await client.post("/api/analysis/complete", json={
                "count": 200,
                "start_price": 100.0,
                "analysis_type": "complete"
            })
            return response.status_code == 200
        
        # 并发执行5个分析任务
        start_time = time.time()
        tasks = [single_analysis() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 所有任务都应该成功
        assert all(results)
        
        # 总时间应该在合理范围内
        total_time = end_time - start_time
        assert total_time < 30.0  # 30秒内完成5个并发分析
        
        print(f"5个并发分析任务总耗时: {total_time:.2f}秒")
    
    @pytest.mark.asyncio
    async def test_data_consistency(self, client):
        """测试数据一致性"""
        # 使用相同参数多次调用，检查结果一致性
        params = {
            "count": 100,
            "start_price": 100.0,
            "time_interval": "1m",
            "volatility": 0.02,
            "trend_bias": 0.0
        }
        
        responses = []
        for _ in range(3):
            response = await client.post("/api/analysis/complete", json=params)
            assert response.status_code == 200
            responses.append(response.json())
        
        # 验证基本结构一致性
        for response in responses:
            assert response["success"] is True
            analysis = response["data"]["analysis_result"]
            assert len(analysis["kline_data"]) == 100
            
            # 基本统计应该相似（由于随机性，不要求完全相同）
            summary = response["data"]["summary"]
            assert summary["basic_info"]["kline_count"] == 100


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_malformed_json(self, client):
        """测试格式错误的JSON"""
        response = await client.post(
            "/api/kline/generate",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client):
        """测试缺少必要字段"""
        response = await client.post("/api/analysis/fenxing", json={
            "min_strength": 0.5
            # 缺少 kline_data 字段
        })
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_invalid_data_types(self, client):
        """测试无效数据类型"""
        response = await client.post("/api/kline/generate", json={
            "count": "invalid",  # 应该是数字
            "start_price": 100.0
        })
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_boundary_values(self, client):
        """测试边界值"""
        # 最小有效值
        response = await client.post("/api/kline/generate", json={
            "count": 10,  # 最小值
            "start_price": 0.01,  # 很小的价格
            "volatility": 0.001,  # 最小波动率
            "trend_bias": -0.05  # 最小趋势偏向
        })
        assert response.status_code == 200
        
        # 最大有效值
        response = await client.post("/api/kline/generate", json={
            "count": 1000,  # 最大值
            "start_price": 10000,  # 很大的价格
            "volatility": 0.1,  # 最大波动率
            "trend_bias": 0.05  # 最大趋势偏向
        })
        assert response.status_code == 200


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])