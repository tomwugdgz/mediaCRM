#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公网访问启动脚本
"""

import subprocess
import sys
import os

def main():
    """启动Streamlit应用"""
    
    # 设置环境变量
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLECORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLEXSRFPROTECTION'] = 'false'
    
    # 启动命令
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--theme.primaryColor", "#1f77b4",
        "--theme.backgroundColor", "#ffffff",
        "--theme.secondaryBackgroundColor", "#f0f2f6",
        "--theme.textColor", "#262730"
    ]
    
    print("🚀 启动Streamlit应用...")
    print("📍 访问地址:")
    print("  • 本地: http://localhost:8501")
    print("  • 局域网: http://YOUR_IP:8501")
    print("  • 公网: http://YOUR_PUBLIC_IP:8501")
    print("\n⚠️  请确保:")
    print("  1. 防火墙已放行8501端口")
    print("  2. 路由器已配置端口转发")
    print("  3. 云服务器安全组已开放端口")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")

if __name__ == "__main__":
    main()
