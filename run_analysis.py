#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日信息分析程序运行器
提供简单的命令行界面来运行不同的分析功能
"""

import argparse
import sys
import os
from daily_info_analyzer import DailyInfoAnalyzer
from enhanced_analyzer import EnhancedInfoAnalyzer

def run_basic_analysis():
    """运行基础分析"""
    print("=== 运行基础分析 ===")
    
    analyzer = DailyInfoAnalyzer()
    
    # 加载数据
    if not analyzer.load_links_data():
        return False
    
    analyzer.load_articles_data()
    
    # 生成报告
    report_file = analyzer.generate_report()
    
    print(f"基础分析报告已生成：{report_file}")
    return True

def run_enhanced_analysis():
    """运行增强分析"""
    print("=== 运行增强分析 ===")
    
    analyzer = EnhancedInfoAnalyzer()
    
    # 加载数据
    if not analyzer.load_and_process_data():
        return False
    
    # 生成静态报告
    report_dir = analyzer.generate_static_report()
    
    print(f"增强版分析报告已生成：{report_dir}")
    return True

def run_interactive_dashboard():
    """运行交互式仪表板"""
    print("=== 启动交互式仪表板 ===")
    
    try:
        analyzer = EnhancedInfoAnalyzer()
        
        # 加载数据
        if not analyzer.load_and_process_data():
            return False
        
        # 创建仪表板
        analyzer.create_interactive_dashboard()
        
    except ImportError:
        print("错误：需要安装 streamlit")
        print("请运行：pip install streamlit")
        return False
    except Exception as e:
        print(f"启动交互式仪表板失败：{e}")
        return False

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'pandas', 'matplotlib', 'seaborn', 'wordcloud', 
        'jieba', 'beautifulsoup4', 'requests', 'python-docx'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包：")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行：pip install -r requirements.txt")
        return False
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='每日信息分析程序',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python run_analysis.py --basic          # 运行基础分析
  python run_analysis.py --enhanced       # 运行增强分析
  python run_analysis.py --dashboard      # 启动交互式仪表板
  python run_analysis.py --check-deps     # 检查依赖项
  python run_analysis.py --help           # 显示帮助信息
        """
    )
    
    parser.add_argument(
        '--basic', 
        action='store_true',
        help='运行基础分析'
    )
    
    parser.add_argument(
        '--enhanced', 
        action='store_true',
        help='运行增强分析'
    )
    
    parser.add_argument(
        '--dashboard', 
        action='store_true',
        help='启动交互式仪表板'
    )
    
    parser.add_argument(
        '--check-deps', 
        action='store_true',
        help='检查依赖项'
    )
    
    args = parser.parse_args()
    
    # 如果没有指定任何参数，显示帮助
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # 检查依赖项
    if args.check_deps:
        if check_dependencies():
            print("所有依赖项都已安装！")
        return
    
    # 检查依赖项（运行分析前）
    if not check_dependencies():
        return
    
    # 运行相应的分析
    try:
        if args.basic:
            run_basic_analysis()
        
        if args.enhanced:
            run_enhanced_analysis()
        
        if args.dashboard:
            run_interactive_dashboard()
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"运行过程中出现错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()