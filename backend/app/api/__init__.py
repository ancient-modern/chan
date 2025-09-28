from fastapi import APIRouter
from api.kline import router as kline_router
from api.analysis import router as analysis_router

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(kline_router, prefix="/kline", tags=["K线数据"])
api_router.include_router(analysis_router, prefix="/analysis", tags=["缠论分析"])