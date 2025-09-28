# 缠论K线分析系统

## 项目简介

基于缠论（Chan Theory）的K线分析系统，包含K线数据模拟、缠论核心算法实现、RESTful API服务和交互式前端可视化界面。

## 功能特性

- 自动识别顶分型、底分型
- 笔和线段构建
- 中枢识别与分类
- 背驰检测算法
- K线数据模拟生成
- 专业级可视化图表

## 技术栈

### 后端
- FastAPI - 高性能异步Web框架
- pandas - 金融数据分析
- numpy - 数值计算
- Pydantic - 数据验证

### 前端
- 原生HTML/JavaScript
- ECharts - 专业金融图表库
- CSS3 - 响应式设计

## 项目结构

```
├── backend/                # 后端代码
│   ├── app/
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
├── frontend/              # 前端代码
│   ├── js/               # JavaScript文件
│   ├── css/              # 样式文件
│   └── assets/           # 静态资源
├── tests/                # 测试代码
│   ├── unit/             # 单元测试
│   └── integration/      # 集成测试
└── requirements.txt      # Python依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问应用

前端界面：http://localhost:8000/
API文档：http://localhost:8000/docs

## API接口

| 接口路径 | 方法 | 功能描述 |
|---------|------|---------|
| `/api/kline/generate` | POST | 生成模拟K线数据 |
| `/api/analysis/fenxing` | POST | 识别顶底分型 |
| `/api/analysis/stroke` | POST | 计算笔和线段 |
| `/api/analysis/center` | POST | 识别中枢 |
| `/api/analysis/divergence` | POST | 判断背驰 |
| `/api/analysis/complete` | POST | 完整缠论分析 |

## 缠论算法

### 分型识别
- 顶分型：连续3根K线形成局部高点
- 底分型：连续3根K线形成局部低点

### 笔线段构建
- 笔：连接相邻分型的线段
- 线段：由多个笔组成的较长趋势

### 中枢识别
- 三个以上线段重叠区域
- 区分上涨、下跌、整理中枢

### 背驰检测
- 基于MACD指标
- 趋势力度对比分析

## 许可证

MIT License