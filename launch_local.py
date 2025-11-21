#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地Streamlit启动器
用于快速启动本地访问的Streamlit应用
"""

import subprocess
import sys
import os
import webbrowser
import time
import socket
from threading import Thread

def check_port_available(port):
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    except:
        return False

def wait_for_server(port=8501, timeout=30):
    """等待服务器启动"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(1)
    return False

def open_browser(port=8501):
    """自动打开浏览器"""
    time.sleep(3)  # 等待服务启动
    if wait_for_server(port):
        url = f"http://localhost:{port}"
        print(f"🌐 正在打开浏览器: {url}")
        webbrowser.open(url)
    else:
        print("⚠️  服务启动超时，请手动访问")

def main():
    """主函数"""
    print("🚀 启动广告置换库存管理系统")
    print("=" * 50)
    
    # 选择端口
    port = 8501
    if not check_port_available(port):
        print(f"⚠️  端口 {port} 被占用，尝试使用端口 {port + 1}")
        port += 1
    
    print(f"📍 使用端口: {port}")
    print(f"🔗 访问地址: http://localhost:{port}")
    print("⏳ 正在启动服务...")
    
    # 启动浏览器线程
    browser_thread = Thread(target=open_browser, args=(port,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动Streamlit
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "app.py",
            "--server.port", str(port),
            "--server.address", "127.0.0.1",  # 仅本地访问
            "--server.headless", "true",
            "--theme.primaryColor", "#1f77b4",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6",
            "--theme.textColor", "#262730"
        ]
        
        print(f"执行命令: {' '.join(cmd[:7])}...")  # 显示部分命令
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()