#!/usr/bin/env python3
"""
测试运行脚本
提供不同类型的测试执行选项
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """执行命令并处理结果"""
    print(f"\n{'='*60}")
    print(f"执行: {description or cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✅ {description or '命令'} 执行成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or '命令'} 执行失败: {e}")
        return False


def install_dependencies():
    """安装测试依赖"""
    print("安装测试依赖...")
    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "httpx>=0.24.0",
        "coverage>=7.0.0"
    ]
    
    cmd = f"pip install {' '.join(dependencies)}"
    return run_command(cmd, "安装测试依赖")


def run_unit_tests():
    """运行单元测试"""
    cmd = "pytest tests/unit/ -v --tb=short --durations=10"
    return run_command(cmd, "单元测试")


def run_integration_tests():
    """运行集成测试"""
    cmd = "pytest tests/integration/ -v --tb=short --durations=10"
    return run_command(cmd, "集成测试")


def run_all_tests():
    """运行所有测试"""
    cmd = "pytest tests/ -v --tb=short --durations=10"
    return run_command(cmd, "全部测试")


def run_tests_with_coverage():
    """运行测试并生成覆盖率报告"""
    cmd = "pytest tests/ --cov=backend/app --cov-report=html --cov-report=term-missing --cov-fail-under=60"
    return run_command(cmd, "测试覆盖率分析")


def run_performance_tests():
    """运行性能测试"""
    cmd = "pytest tests/ -m slow -v --tb=short"
    return run_command(cmd, "性能测试")


def run_quick_tests():
    """运行快速测试（跳过慢速测试）"""
    cmd = "pytest tests/ -m 'not slow' -v --tb=short"
    return run_command(cmd, "快速测试")


def lint_code():
    """代码质量检查"""
    print("进行代码质量检查...")
    
    # 检查Python语法
    cmd = "python -m py_compile backend/app/main.py"
    if not run_command(cmd, "Python语法检查"):
        return False
    
    # 检查导入
    cmd = "python -c 'import backend.app.main'"
    if not run_command(cmd, "导入检查"):
        return False
    
    return True


def check_api_server():
    """检查API服务器状态"""
    print("检查API服务器...")
    
    # 尝试导入FastAPI应用
    try:
        sys.path.append('backend')
        from app.main import app
        print("✅ FastAPI应用导入成功")
        return True
    except Exception as e:
        print(f"❌ FastAPI应用导入失败: {e}")
        return False


def generate_test_report():
    """生成测试报告"""
    print("生成测试报告...")
    
    # 创建报告目录
    os.makedirs("test_reports", exist_ok=True)
    
    # 生成HTML覆盖率报告
    cmd = "pytest tests/ --cov=backend/app --cov-report=html:test_reports/coverage --html=test_reports/report.html --self-contained-html"
    return run_command(cmd, "生成测试报告")


def clean_test_artifacts():
    """清理测试产生的文件"""
    print("清理测试文件...")
    
    import shutil
    
    artifacts = [
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "test_reports",
        "__pycache__"
    ]
    
    for artifact in artifacts:
        if os.path.exists(artifact):
            if os.path.isdir(artifact):
                shutil.rmtree(artifact)
            else:
                os.remove(artifact)
            print(f"删除: {artifact}")
    
    # 递归删除__pycache__
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                shutil.rmtree(pycache_path)
                print(f"删除: {pycache_path}")
    
    print("✅ 清理完成")


def main():
    parser = argparse.ArgumentParser(description="缠论K线分析系统测试工具")
    parser.add_argument(
        "command",
        choices=[
            "install", "unit", "integration", "all", "coverage", 
            "performance", "quick", "lint", "check", "report", "clean"
        ],
        help="测试命令"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 切换到项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"缠论K线分析系统测试工具")
    print(f"当前目录: {os.getcwd()}")
    print(f"执行命令: {args.command}")
    
    success = False
    
    if args.command == "install":
        success = install_dependencies()
    elif args.command == "unit":
        success = run_unit_tests()
    elif args.command == "integration":
        success = run_integration_tests()
    elif args.command == "all":
        success = run_all_tests()
    elif args.command == "coverage":
        success = run_tests_with_coverage()
    elif args.command == "performance":
        success = run_performance_tests()
    elif args.command == "quick":
        success = run_quick_tests()
    elif args.command == "lint":
        success = lint_code()
    elif args.command == "check":
        success = check_api_server()
    elif args.command == "report":
        success = generate_test_report()
    elif args.command == "clean":
        clean_test_artifacts()
        success = True
    
    if success:
        print(f"\n✅ {args.command} 命令执行成功!")
        sys.exit(0)
    else:
        print(f"\n❌ {args.command} 命令执行失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
