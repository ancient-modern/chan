from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class FenxingType(str, Enum):
    """分型类型枚举"""
    TOP = "top"        # 顶分型
    BOTTOM = "bottom"  # 底分型


class StrokeDirection(str, Enum):
    """笔方向枚举"""
    UP = "up"      # 上升笔
    DOWN = "down"  # 下降笔


class CenterType(str, Enum):
    """中枢类型枚举"""
    UP = "up"           # 上涨中枢
    DOWN = "down"       # 下跌中枢
    CONSOLIDATION = "consolidation"  # 整理中枢


class KlineData(BaseModel):
    """K线数据模型"""
    timestamp: datetime = Field(..., description="时间戳")
    open: float = Field(..., description="开盘价", gt=0)
    high: float = Field(..., description="最高价", gt=0)
    low: float = Field(..., description="最低价", gt=0)
    close: float = Field(..., description="收盘价", gt=0)
    volume: int = Field(..., description="成交量", ge=0)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FenxingPoint(BaseModel):
    """分型点模型"""
    index: int = Field(..., description="K线索引位置", ge=0)
    type: FenxingType = Field(..., description="分型类型")
    high: float = Field(..., description="最高价", gt=0)
    low: float = Field(..., description="最低价", gt=0)
    price: float = Field(..., description="关键价格点", gt=0)
    timestamp: datetime = Field(..., description="时间戳")
    confidence: float = Field(1.0, description="置信度", ge=0, le=1)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Stroke(BaseModel):
    """笔模型"""
    start_fenxing: FenxingPoint = Field(..., description="起始分型")
    end_fenxing: FenxingPoint = Field(..., description="结束分型")
    direction: StrokeDirection = Field(..., description="笔方向")
    price_range: float = Field(..., description="价格幅度", ge=0)
    kline_count: int = Field(..., description="包含K线数量", gt=0)
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Segment(BaseModel):
    """线段模型"""
    strokes: List[Stroke] = Field(..., description="组成笔列表", min_items=1)
    direction: StrokeDirection = Field(..., description="线段方向")
    start_price: float = Field(..., description="起始价格", gt=0)
    end_price: float = Field(..., description="结束价格", gt=0)
    price_range: float = Field(..., description="价格幅度", ge=0)
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Center(BaseModel):
    """中枢模型"""
    segments: List[Segment] = Field(..., description="构成线段列表", min_items=3)
    center_type: CenterType = Field(..., description="中枢类型")
    high_price: float = Field(..., description="中枢高点", gt=0)
    low_price: float = Field(..., description="中枢低点", gt=0)
    center_range: float = Field(..., description="中枢区间幅度", ge=0)
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    strength: float = Field(0.5, description="中枢强度", ge=0, le=1)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MACDData(BaseModel):
    """MACD指标数据"""
    timestamp: datetime = Field(..., description="时间戳")
    dif: float = Field(..., description="快线DIF")
    dea: float = Field(..., description="慢线DEA")
    macd: float = Field(..., description="MACD柱状图")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DivergenceSignal(BaseModel):
    """背驰信号模型"""
    center: Center = Field(..., description="相关中枢")
    signal_time: datetime = Field(..., description="信号时间")
    signal_type: str = Field(..., description="信号类型")
    strength: float = Field(..., description="背驰强度", ge=0, le=1)
    description: str = Field(..., description="背驰描述")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisResult(BaseModel):
    """完整分析结果模型"""
    kline_data: List[KlineData] = Field(..., description="K线数据")
    fenxing_points: List[FenxingPoint] = Field(..., description="分型点列表")
    strokes: List[Stroke] = Field(..., description="笔列表")
    segments: List[Segment] = Field(..., description="线段列表")
    centers: List[Center] = Field(..., description="中枢列表")
    macd_data: List[MACDData] = Field(..., description="MACD数据")
    divergence_signals: List[DivergenceSignal] = Field(..., description="背驰信号")
    analysis_time: datetime = Field(..., description="分析时间")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }