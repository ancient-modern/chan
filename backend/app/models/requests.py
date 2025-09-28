from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KlineGenerateRequest(BaseModel):
    """K线生成请求模型"""
    count: int = Field(100, description="生成K线数量", ge=10, le=1000)
    start_price: float = Field(100.0, description="起始价格", gt=0)
    time_interval: str = Field("1m", description="时间间隔")
    volatility: float = Field(0.02, description="波动率", ge=0.001, le=0.1)
    trend_bias: float = Field(0.0, description="趋势偏向", ge=-0.05, le=0.05)


class AnalysisRequest(BaseModel):
    """分析请求基础模型"""
    symbol: Optional[str] = Field(None, description="交易对符号")
    analysis_type: str = Field(..., description="分析类型")


class FenxingAnalysisRequest(AnalysisRequest):
    """分型分析请求模型"""
    kline_data: list = Field(..., description="K线数据", min_items=3)
    min_strength: float = Field(0.5, description="最小强度", ge=0, le=1)


class StrokeAnalysisRequest(AnalysisRequest):
    """笔分析请求模型"""
    kline_data: list = Field(..., description="K线数据")
    fenxing_points: list = Field(..., description="分型点数据")


class CenterAnalysisRequest(AnalysisRequest):
    """中枢分析请求模型"""
    segments: list = Field(..., description="线段数据", min_items=3)


class DivergenceAnalysisRequest(AnalysisRequest):
    """背驰分析请求模型"""
    kline_data: list = Field(..., description="K线数据")
    centers: list = Field(..., description="中枢数据")


class CompleteAnalysisRequest(AnalysisRequest):
    """完整分析请求模型"""
    count: int = Field(100, description="K线数量", ge=10, le=1000)
    start_price: float = Field(100.0, description="起始价格", gt=0)
    time_interval: str = Field("1m", description="时间间隔")
    volatility: float = Field(0.02, description="波动率", ge=0.001, le=0.1)
    trend_bias: float = Field(0.0, description="趋势偏向", ge=-0.05, le=0.05)


class APIResponse(BaseModel):
    """API响应基础模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")
    timestamp: datetime = Field(..., description="响应时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }