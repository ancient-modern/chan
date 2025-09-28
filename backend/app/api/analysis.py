from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List, Dict, Any
from models.requests import (
    FenxingAnalysisRequest, StrokeAnalysisRequest, 
    CenterAnalysisRequest, DivergenceAnalysisRequest,
    CompleteAnalysisRequest, APIResponse
)
from models.analysis import KlineData
from services.chan_theory_engine import chan_theory_engine

router = APIRouter()


def convert_kline_data(kline_list: List[Dict[str, Any]]) -> List[KlineData]:
    """
    转换字典格式的K线数据为KlineData对象
    
    Args:
        kline_list: K线数据字典列表
        
    Returns:
        KlineData对象列表
    """
    result = []
    for kline_dict in kline_list:
        kline = KlineData(
            timestamp=datetime.fromisoformat(kline_dict["timestamp"].replace("Z", "+00:00")),
            open=float(kline_dict["open"]),
            high=float(kline_dict["high"]),
            low=float(kline_dict["low"]),
            close=float(kline_dict["close"]),
            volume=int(kline_dict["volume"])
        )
        result.append(kline)
    return result


def serialize_analysis_result(result) -> Dict[str, Any]:
    """
    序列化分析结果为字典格式
    
    Args:
        result: 分析结果对象
        
    Returns:
        序列化后的字典
    """
    # 序列化K线数据
    kline_data = []
    for kline in result.kline_data:
        kline_data.append({
            "timestamp": kline.timestamp.isoformat(),
            "open": kline.open,
            "high": kline.high,
            "low": kline.low,
            "close": kline.close,
            "volume": kline.volume
        })
    
    # 序列化分型点
    fenxing_points = []
    for fenxing in result.fenxing_points:
        fenxing_points.append({
            "index": fenxing.index,
            "type": fenxing.type.value,
            "high": fenxing.high,
            "low": fenxing.low,
            "price": fenxing.price,
            "timestamp": fenxing.timestamp.isoformat(),
            "confidence": fenxing.confidence
        })
    
    # 序列化笔
    strokes = []
    for stroke in result.strokes:
        strokes.append({
            "start_fenxing": {
                "index": stroke.start_fenxing.index,
                "type": stroke.start_fenxing.type.value,
                "price": stroke.start_fenxing.price,
                "timestamp": stroke.start_fenxing.timestamp.isoformat()
            },
            "end_fenxing": {
                "index": stroke.end_fenxing.index,
                "type": stroke.end_fenxing.type.value,
                "price": stroke.end_fenxing.price,
                "timestamp": stroke.end_fenxing.timestamp.isoformat()
            },
            "direction": stroke.direction.value,
            "price_range": stroke.price_range,
            "kline_count": stroke.kline_count,
            "start_time": stroke.start_time.isoformat(),
            "end_time": stroke.end_time.isoformat()
        })
    
    # 序列化线段
    segments = []
    for segment in result.segments:
        segments.append({
            "direction": segment.direction.value,
            "start_price": segment.start_price,
            "end_price": segment.end_price,
            "price_range": segment.price_range,
            "start_time": segment.start_time.isoformat(),
            "end_time": segment.end_time.isoformat(),
            "stroke_count": len(segment.strokes)
        })
    
    # 序列化中枢
    centers = []
    for center in result.centers:
        centers.append({
            "center_type": center.center_type.value,
            "high_price": center.high_price,
            "low_price": center.low_price,
            "center_range": center.center_range,
            "start_time": center.start_time.isoformat(),
            "end_time": center.end_time.isoformat(),
            "strength": center.strength,
            "segment_count": len(center.segments)
        })
    
    # 序列化MACD数据
    macd_data = []
    for macd in result.macd_data:
        macd_data.append({
            "timestamp": macd.timestamp.isoformat(),
            "dif": macd.dif,
            "dea": macd.dea,
            "macd": macd.macd
        })
    
    # 序列化背驰信号
    divergence_signals = []
    for signal in result.divergence_signals:
        divergence_signals.append({
            "signal_time": signal.signal_time.isoformat(),
            "signal_type": signal.signal_type,
            "strength": signal.strength,
            "description": signal.description
        })
    
    return {
        "kline_data": kline_data,
        "fenxing_points": fenxing_points,
        "strokes": strokes,
        "segments": segments,
        "centers": centers,
        "macd_data": macd_data,
        "divergence_signals": divergence_signals,
        "analysis_time": result.analysis_time.isoformat()
    }


@router.post("/complete", response_model=APIResponse)
async def complete_analysis(request: CompleteAnalysisRequest):
    """
    完整的缠论分析
    
    Args:
        request: 完整分析请求
        
    Returns:
        完整的分析结果
    """
    try:
        result = chan_theory_engine.complete_analysis(
            count=request.count,
            start_price=request.start_price,
            time_interval=request.time_interval,
            volatility=request.volatility,
            trend_bias=request.trend_bias
        )
        
        # 获取分析摘要
        summary = chan_theory_engine.get_analysis_summary(result)
        
        # 获取质量评估
        quality = chan_theory_engine.validate_analysis_quality(result)
        
        return APIResponse(
            success=True,
            message="完整缠论分析完成",
            data={
                "analysis_result": serialize_analysis_result(result),
                "summary": summary,
                "quality": quality
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=f"缠论分析失败: {str(e)}")


@router.post("/fenxing", response_model=APIResponse)
async def analyze_fenxing(request: FenxingAnalysisRequest):
    """
    分型分析
    
    Args:
        request: 分型分析请求
        
    Returns:
        分型分析结果
    """
    try:
        # 转换K线数据
        kline_data = convert_kline_data(request.kline_data)
        
        # 进行分型分析
        fenxing_points = chan_theory_engine.analyze_fenxing_only(
            kline_data, request.min_strength
        )
        
        # 序列化分型点
        fenxing_list = []
        for fenxing in fenxing_points:
            fenxing_list.append({
                "index": fenxing.index,
                "type": fenxing.type.value,
                "high": fenxing.high,
                "low": fenxing.low,
                "price": fenxing.price,
                "timestamp": fenxing.timestamp.isoformat(),
                "confidence": fenxing.confidence
            })
        
        return APIResponse(
            success=True,
            message=f"识别到{len(fenxing_points)}个分型点",
            data={
                "fenxing_points": fenxing_list,
                "total_count": len(fenxing_points),
                "top_count": len([f for f in fenxing_points if f.type.value == "top"]),
                "bottom_count": len([f for f in fenxing_points if f.type.value == "bottom"]),
                "avg_confidence": sum(f.confidence for f in fenxing_points) / len(fenxing_points) if fenxing_points else 0
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分型分析失败: {str(e)}")


@router.post("/stroke", response_model=APIResponse)
async def analyze_stroke(request: StrokeAnalysisRequest):
    """
    笔分析
    
    Args:
        request: 笔分析请求
        
    Returns:
        笔分析结果
    """
    try:
        # 转换K线数据
        kline_data = convert_kline_data(request.kline_data)
        
        # 转换分型点数据
        fenxing_points = []
        for fenxing_dict in request.fenxing_points:
            from models.analysis import FenxingPoint, FenxingType
            fenxing = FenxingPoint(
                index=fenxing_dict["index"],
                type=FenxingType(fenxing_dict["type"]),
                high=fenxing_dict["high"],
                low=fenxing_dict["low"],
                price=fenxing_dict["price"],
                timestamp=datetime.fromisoformat(fenxing_dict["timestamp"]),
                confidence=fenxing_dict["confidence"]
            )
            fenxing_points.append(fenxing)
        
        # 进行笔分析
        strokes = chan_theory_engine.analyze_strokes_only(kline_data, fenxing_points)
        
        # 序列化笔数据
        stroke_list = []
        for stroke in strokes:
            stroke_list.append({
                "start_fenxing": {
                    "index": stroke.start_fenxing.index,
                    "type": stroke.start_fenxing.type.value,
                    "price": stroke.start_fenxing.price
                },
                "end_fenxing": {
                    "index": stroke.end_fenxing.index,
                    "type": stroke.end_fenxing.type.value,
                    "price": stroke.end_fenxing.price
                },
                "direction": stroke.direction.value,
                "price_range": stroke.price_range,
                "kline_count": stroke.kline_count,
                "start_time": stroke.start_time.isoformat(),
                "end_time": stroke.end_time.isoformat()
            })
        
        # 获取笔特征统计
        stroke_features = chan_theory_engine.stroke_builder.analyze_stroke_features(strokes)
        
        return APIResponse(
            success=True,
            message=f"构建了{len(strokes)}个笔",
            data={
                "strokes": stroke_list,
                "features": stroke_features
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"笔分析失败: {str(e)}")


@router.post("/center", response_model=APIResponse)
async def analyze_center(request: CenterAnalysisRequest):
    """
    中枢分析
    
    Args:
        request: 中枢分析请求
        
    Returns:
        中枢分析结果
    """
    try:
        # 这里简化处理，实际应该从segments数据重构Segment对象
        # 暂时返回示例数据
        return APIResponse(
            success=True,
            message="中枢分析功能正在开发中",
            data={
                "centers": [],
                "message": "请使用完整分析接口获取中枢分析结果"
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"中枢分析失败: {str(e)}")


@router.post("/divergence", response_model=APIResponse)
async def analyze_divergence(request: DivergenceAnalysisRequest):
    """
    背驰分析
    
    Args:
        request: 背驰分析请求
        
    Returns:
        背驰分析结果
    """
    try:
        # 这里简化处理，实际应该从输入数据重构所需对象
        # 暂时返回示例数据
        return APIResponse(
            success=True,
            message="背驰分析功能正在开发中",
            data={
                "divergence_signals": [],
                "message": "请使用完整分析接口获取背驰分析结果"
            },
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"背驰分析失败: {str(e)}")


@router.get("/summary")
async def get_analysis_info():
    """
    获取分析功能信息
    
    Returns:
        分析功能介绍
    """
    return APIResponse(
        success=True,
        message="缠论分析功能介绍",
        data={
            "features": {
                "complete_analysis": "完整缠论分析，包含分型、笔、线段、中枢、背驰",
                "fenxing_analysis": "分型识别，寻找顶分型和底分型",
                "stroke_analysis": "笔构建，连接相邻分型形成笔",
                "center_analysis": "中枢识别，寻找价格重叠区间",
                "divergence_analysis": "背驰检测，基于MACD指标判断背驰"
            },
            "algorithms": {
                "fenxing_detector": "基于价格突出程度、成交量确认等多维度评估",
                "stroke_builder": "严格按照缠论定义构建笔和线段",
                "center_detector": "识别线段重叠区间，分类中枢类型",
                "divergence_detector": "MACD背驰算法，趋势力度对比"
            },
            "supported_patterns": [
                "double_top", "double_bottom", "head_shoulders"
            ],
            "supported_trends": [
                "up", "down", "sideways"
            ]
        },
        timestamp=datetime.now()
    )