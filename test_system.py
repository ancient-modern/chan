#!/usr/bin/env python3
"""
系统启动和测试脚本
用于验证缠论K线分析系统的基本功能
"""

import sys
import os
from pathlib import Path

# 添加backend路径到Python path
current_dir = Path(__file__).parent
backend_path = current_dir / "backend"
sys.path.insert(0, str(backend_path))

try:
    print("🚀 启动缠论K线分析系统测试...")
    
    # 测试核心模块导入
    print("📦 测试模块导入...")
    
    from app.services.kline_simulator import KlineSimulator
    print("✅ KlineSimulator 导入成功")
    
    from app.services.fenxing_detector import FenxingDetector  
    print("✅ FenxingDetector 导入成功")
    
    from app.services.stroke_builder import StrokeBuilder
    print("✅ StrokeBuilder 导入成功")
    
    from app.services.center_detector import CenterDetector
    print("✅ CenterDetector 导入成功")
    
    from app.services.divergence_detector import DivergenceDetector
    print("✅ DivergenceDetector 导入成功")
    
    from app.services.chan_theory_engine import ChanTheoryEngine
    print("✅ ChanTheoryEngine 导入成功")
    
    # 测试基本功能
    print("\n🔧 测试基本功能...")
    
    # 创建引擎实例
    engine = ChanTheoryEngine()
    print("✅ 缠论分析引擎创建成功")
    
    # 生成测试数据
    print("📊 生成测试K线数据...")
    kline_data = engine.generate_kline_only(count=50, start_price=100.0)
    print(f"✅ 生成了 {len(kline_data)} 根K线数据")
    
    # 测试分型识别
    print("🔍 测试分型识别...")
    fenxing_points = engine.analyze_fenxing_only(kline_data)
    print(f"✅ 识别到 {len(fenxing_points)} 个分型点")
    
    # 测试笔构建
    if fenxing_points:
        print("📈 测试笔构建...")
        strokes = engine.analyze_strokes_only(kline_data, fenxing_points)
        print(f"✅ 构建了 {len(strokes)} 个笔")
    
    # 测试完整分析
    print("🎯 测试完整缠论分析...")
    result = engine.complete_analysis(count=80, start_price=100.0)
    
    print(f"✅ 完整分析完成:")
    print(f"   - K线数据: {len(result.kline_data)} 根")
    print(f"   - 分型点: {len(result.fenxing_points)} 个")
    print(f"   - 笔: {len(result.strokes)} 个")
    print(f"   - 线段: {len(result.segments)} 个")
    print(f"   - 中枢: {len(result.centers)} 个")
    print(f"   - MACD数据: {len(result.macd_data)} 个")
    print(f"   - 背驰信号: {len(result.divergence_signals)} 个")
    
    # 测试分析摘要
    print("📋 测试分析摘要...")
    summary = engine.get_analysis_summary(result)
    print("✅ 分析摘要生成成功")
    
    # 测试质量评估
    print("📏 测试质量评估...")
    quality = engine.validate_analysis_quality(result)
    print(f"✅ 质量评估完成，整体评分: {quality['overall_score']:.2f}")
    
    # 测试FastAPI应用
    print("\n🌐 测试FastAPI应用...")
    try:
        from app.main import app
        print("✅ FastAPI应用导入成功")
        print(f"   - 应用标题: {app.title}")
        print(f"   - 应用版本: {app.version}")
    except Exception as e:
        print(f"⚠️ FastAPI应用测试失败: {e}")
    
    print("\n🎉 所有基本功能测试通过!")
    print("\n💡 下一步:")
    print("   1. 启动后端服务: cd backend && uvicorn app.main:app --reload")
    print("   2. 打开前端界面: 访问 http://localhost:8000")
    print("   3. 运行完整测试: python run_tests.py unit")
    
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    print("💡 请确保安装了所需的依赖:")
    print("   pip install fastapi uvicorn pandas numpy pydantic")
except Exception as e:
    print(f"❌ 测试过程中出现错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)