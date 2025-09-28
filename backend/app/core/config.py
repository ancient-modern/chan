# FastAPI应用配置
import os

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    """应用设置"""
    app_name: str = "缠论K线分析系统"
    version: str = "1.0.0"
    description: str = "基于缠论理论的K线技术分析系统"
    
    # API设置
    api_v1_prefix: str = "/api"
    
    # CORS设置
    backend_cors_origins: list = ["*"]
    
    # 数据设置
    default_kline_count: int = 100
    max_kline_count: int = 1000
    
    class Config:
        env_file = ".env"


# 全局设置实例
settings = Settings()