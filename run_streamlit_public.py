#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit公网访问启动脚本
用于配置和启动Streamlit应用以支持公网访问
"""

import os
import sys
import subprocess
import socket
import platform

def get_local_ip():
    """获取本地IP地址"""
    try:
        # 创建一个UDP socket来获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def check_port_available(port):
    """检查端口是否可用"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', port))
        s.close()
        return True
    except OSError:
        return False

def setup_firewall(port):
    """配置防火墙规则"""
    system = platform.system()
    
    if system == "Windows":
        try:
            # Windows防火墙配置
            cmd = f'netsh advfirewall firewall add rule name="Streamlit Public {port}" dir=in action=allow protocol=TCP localport={port}'
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ Windows防火墙规则已添加: 端口 {port}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  防火墙配置失败: {e}")
            print("请手动在Windows防火墙中添加端口规则")
    
    elif system == "Linux":
        try:
            # Linux iptables配置
            subprocess.run(f'sudo iptables -A INPUT -p tcp --dport {port} -j ACCEPT', shell=True, check=True)
            print(f"✅ Linux防火墙规则已添加: 端口 {port}")
        except subprocess.CalledProcessError:
            print("⚠️  需要sudo权限配置防火墙")
    
    elif system == "Darwin":  # macOS
        print("⚠️  请手动在macOS防火墙中配置端口规则")

def main():
    """主函数"""
    print("🚀 配置Streamlit公网访问")
    print("=" * 50)
    
    # 获取IP地址
    local_ip = get_local_ip()
    print(f"📍 本地IP地址: {local_ip}")
    
    # 选择端口
    default_port = 8501
    port = default_port
    
    # 检查默认端口是否可用
    if not check_port_available(port):
        print(f"⚠️  端口 {port} 已被占用")
        for p in range(8502, 8600):
            if check_port_available(p):
                port = p
                print(f"✅ 使用可用端口: {port}")
                break
        else:
            print("❌ 没有找到可用端口")
            return
    
    print(f"🌐 将使用端口: {port}")
    
    # 配置防火墙
    print("\n🔒 配置防火墙...")
    setup_firewall(port)
    
    # 获取公网IP
    try:
        import requests
        public_ip = requests.get('https://api.ipify.org', timeout=5).text
        print(f"🌍 公网IP地址: {public_ip}")
    except:
        print("⚠️  无法获取公网IP地址")
        public_ip = None
    
    print("\n" + "=" * 50)
    print("📋 配置信息:")
    print(f"本地访问地址: http://localhost:{port}")
    print(f"局域网访问地址: http://{local_ip}:{port}")
    if public_ip:
        print(f"公网访问地址: http://{public_ip}:{port}")
    
    print("\n⚠️  重要提示:")
    print("1. 确保路由器配置了端口转发")
    print("2. 如果使用云服务器，请配置安全组规则")
    print("3. 生产环境建议使用HTTPS和认证")
    print("\n🎯 启动Streamlit应用...")
    
    # 启动Streamlit
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "app.py",
            "--server.port", str(port),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()