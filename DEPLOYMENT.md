# 缠论K线分析系统部署指南

## 系统概述

缠论K线分析系统是一个基于缠论理论的K线技术分析平台，包含完整的后端API服务和交互式前端界面。

## 技术架构

### 后端技术栈
- **FastAPI**: 高性能异步Web框架
- **pandas**: 金融数据分析库
- **numpy**: 数值计算库
- **Pydantic**: 数据验证库
- **uvicorn**: ASGI服务器

### 前端技术栈
- **原生HTML/JavaScript**: 轻量级前端实现
- **ECharts**: 专业金融图表库
- **CSS3**: 响应式界面设计

## 部署准备

### 系统要求
- Python 3.8+
- 内存: 最小 2GB，推荐 4GB+
- 存储: 最小 1GB 可用空间
- 网络: 支持HTTP/HTTPS协议

### 依赖安装

1. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2. **安装Python依赖**
```bash
pip install -r requirements.txt
```

如果requirements.txt不存在，手动安装：
```bash
pip install fastapi==0.104.1 uvicorn==0.24.0 pandas==2.1.3 numpy==1.25.2 pydantic==2.5.0
```

## 部署方式

### 1. 开发环境部署

**启动后端服务**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**访问应用**
- 前端界面: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 2. 生产环境部署

**使用Gunicorn（推荐）**
```bash
pip install gunicorn
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**使用Docker**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：
```bash
docker build -t chan-theory-app .
docker run -p 8000:8000 chan-theory-app
```

### 3. 云平台部署

**Heroku部署**
1. 创建Procfile文件：
```
web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

2. 部署命令：
```bash
heroku create your-app-name
git push heroku main
```

**Vercel部署**
1. 创建vercel.json：
```json
{
  "builds": [
    {
      "src": "backend/app/main.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/app/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ]
}
```

## 配置管理

### 环境变量
创建 `.env` 文件：
```env
# 应用配置
APP_NAME=缠论K线分析系统
VERSION=1.0.0
DEBUG=false

# 数据配置
DEFAULT_KLINE_COUNT=100
MAX_KLINE_COUNT=1000

# CORS配置
BACKEND_CORS_ORIGINS=["*"]
```

### 性能优化
```python
# backend/app/core/config.py 中的设置
class Settings(BaseSettings):
    # 工作进程数
    workers: int = 4
    
    # 最大并发请求
    max_requests: int = 1000
    
    # 数据缓存设置
    cache_ttl: int = 300  # 5分钟
```

## 监控和维护

### 健康检查
```bash
curl http://localhost:8000/health
```

期望响应：
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
```

### 性能监控
```bash
# 查看系统资源使用
top -p $(pgrep -f uvicorn)

# 查看网络连接
netstat -tlnp | grep :8000

# 查看应用日志
tail -f app.log
```

## 故障排除

### 常见问题

1. **模块导入错误**
```bash
# 检查Python路径
python -c "import sys; print('\n'.join(sys.path))"

# 检查依赖安装
pip list | grep fastapi
```

2. **端口被占用**
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>
```

3. **内存不足**
```bash
# 减少工作进程数
uvicorn app.main:app --workers 1

# 监控内存使用
free -h
```

4. **CORS错误**
在 `backend/app/core/config.py` 中检查CORS设置：
```python
backend_cors_origins: list = ["http://localhost:3000", "http://localhost:8080"]
```

### 性能调优

1. **数据库连接池**（如果使用数据库）
```python
# 配置连接池大小
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 0
```

2. **异步处理**
```python
# 使用异步函数处理耗时操作
async def heavy_computation():
    # 耗时的缠论分析
    pass
```

3. **缓存策略**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_analysis(params_hash):
    # 缓存分析结果
    pass
```

## 安全考虑

### API安全
```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # 实现速率限制
    pass
```

### 数据验证
```python
from pydantic import validator

class AnalysisRequest(BaseModel):
    count: int
    
    @validator('count')
    def validate_count(cls, v):
        if v < 10 or v > 1000:
            raise ValueError('count must be between 10 and 1000')
        return v
```

## 扩展和定制

### 添加新的技术指标
1. 在 `backend/app/services/` 下创建新的服务模块
2. 实现指标计算逻辑
3. 在API中添加对应端点
4. 在前端添加可视化支持

### 支持实时数据
1. 集成WebSocket支持
2. 连接数据源API
3. 实现实时数据推送
4. 前端实时图表更新

### 数据持久化
1. 集成数据库（PostgreSQL/MongoDB）
2. 实现数据模型
3. 添加数据存储和查询API
4. 实现历史数据分析

## 备份和恢复

### 配置备份
```bash
# 备份配置文件
tar -czf config_backup.tar.gz backend/app/core/config.py .env

# 恢复配置
tar -xzf config_backup.tar.gz
```

### 应用更新
```bash
# 拉取最新代码
git pull origin main

# 重启服务
pkill -f uvicorn
nohup uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
```

## 联系支持

如遇到部署问题，请检查：
1. 系统日志文件
2. Python版本兼容性
3. 依赖包版本
4. 网络和防火墙设置

更多技术支持，请参考项目文档或提交Issue。