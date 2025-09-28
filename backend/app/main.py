from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import api_router
from core.config import settings


def create_application() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=settings.description,
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册API路由
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # 静态文件服务
    app.mount("/", StaticFiles(directory="../../frontend", html=True), name="frontend")

    return app


# 创建应用实例
app = create_application()


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "version": settings.version}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
