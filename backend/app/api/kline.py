from datetime import datetime

from fastapi import APIRouter, HTTPException

from models.requests import (
    KlineGenerateRequest, APIResponse
)
from services.chan_theory_engine import chan_theory_engine

router = APIRouter()


@router.post("/generate", response_model=APIResponse)
async def generate_kline_data(request: KlineGenerateRequest):
    """
    生成模拟K线数据
    
    Args:
        request: K线生成请求
        
    Returns:
        生成的K线数据
    """
    try:
        kline_data = chan_theory_engine.generate_kline_only(
            count=request.count,
            start_price=request.start_price,
            time_interval=request.time_interval,
            volatility=request.volatility,
            trend_bias=request.trend_bias
        )

        # 转换为字典格式便于JSON序列化
        kline_dict_list = []
        for kline in kline_data:
            kline_dict = {
                "timestamp": kline.timestamp.isoformat(),
                "open": kline.open,
                "high": kline.high,
                "low": kline.low,
                "close": kline.close,
                "volume": kline.volume
            }
            kline_dict_list.append(kline_dict)

        return APIResponse(
            success=True,
            message=f"成功生成{len(kline_data)}根K线数据",
            data={
                "kline_data": kline_dict_list,
                "count": len(kline_data),
                "start_price": request.start_price,
                "end_price": kline_data[-1].close if kline_data else request.start_price,
                "price_change": kline_data[-1].close - request.start_price if kline_data else 0,
                "price_change_ratio": (kline_data[
                                           -1].close - request.start_price) / request.start_price if kline_data else 0
            },
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成K线数据失败: {str(e)}")


@router.get("/patterns/{pattern_type}")
async def generate_pattern_data(
        pattern_type: str,
        count: int = 100,
        start_price: float = 100.0,
        volatility: float = 0.02
):
    """
    生成特定技术分析模式的K线数据
    
    Args:
        pattern_type: 模式类型 (double_top, double_bottom, head_shoulders)
        count: K线数量
        start_price: 起始价格
        volatility: 波动率
        
    Returns:
        包含特定模式的K线数据
    """
    try:
        valid_patterns = ["double_top", "double_bottom", "head_shoulders"]
        if pattern_type not in valid_patterns:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的模式类型。支持的类型: {', '.join(valid_patterns)}"
            )

        kline_data = chan_theory_engine.kline_simulator.generate_with_patterns(
            count=count,
            start_price=start_price,
            pattern_type=pattern_type,
            volatility=volatility
        )

        # 转换为字典格式
        kline_dict_list = []
        for kline in kline_data:
            kline_dict = {
                "timestamp": kline.timestamp.isoformat(),
                "open": kline.open,
                "high": kline.high,
                "low": kline.low,
                "close": kline.close,
                "volume": kline.volume
            }
            kline_dict_list.append(kline_dict)

        return APIResponse(
            success=True,
            message=f"成功生成{pattern_type}模式K线数据",
            data={
                "pattern_type": pattern_type,
                "kline_data": kline_dict_list,
                "count": len(kline_data)
            },
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成模式K线数据失败: {str(e)}")


@router.get("/trending/{direction}")
async def generate_trending_data(
        direction: str,
        count: int = 100,
        start_price: float = 100.0,
        volatility: float = 0.02
):
    """
    生成特定趋势的K线数据
    
    Args:
        direction: 趋势方向 (up, down, sideways)
        count: K线数量
        start_price: 起始价格
        volatility: 波动率
        
    Returns:
        特定趋势的K线数据
    """
    try:
        valid_directions = ["up", "down", "sideways"]
        if direction not in valid_directions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的趋势方向。支持的方向: {', '.join(valid_directions)}"
            )

        kline_data = chan_theory_engine.kline_simulator.generate_trending_data(
            count=count,
            start_price=start_price,
            trend_direction=direction,
            volatility=volatility
        )

        # 转换为字典格式
        kline_dict_list = []
        for kline in kline_data:
            kline_dict = {
                "timestamp": kline.timestamp.isoformat(),
                "open": kline.open,
                "high": kline.high,
                "low": kline.low,
                "close": kline.close,
                "volume": kline.volume
            }
            kline_dict_list.append(kline_dict)

        return APIResponse(
            success=True,
            message=f"成功生成{direction}趋势K线数据",
            data={
                "trend_direction": direction,
                "kline_data": kline_dict_list,
                "count": len(kline_data),
                "start_price": start_price,
                "end_price": kline_data[-1].close if kline_data else start_price
            },
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成趋势K线数据失败: {str(e)}")
