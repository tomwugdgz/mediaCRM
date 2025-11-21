#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit配置文件
用于生成Streamlit配置文件以支持公网访问
"""

import os
import configparser
from pathlib import Path

def create_streamlit_config():
    """创建Streamlit配置文件"""
    
    config = configparser.ConfigParser()
    
    # Streamlit配置
    config['server'] = {
        'port': '8501',
        'address': '0.0.0.0',  # 监听所有网络接口
        'baseUrlPath': '',
        'enableCORS': 'false',
        'enableXsrfProtection': 'false',
        'maxUploadSize': '200',
        'maxMessageSize': '200',
        'headless': 'true',
        'runOnSave': 'true',
        'allowRunOnSave': 'true'
    }
    
    config['browser'] = {
        'serverAddress': '0.0.0.0',
        'gatherUsageStats': 'false',
        'serverPort': '8501'
    }
    
    config['theme'] = {
        'primaryColor': '#1f77b4',
        'backgroundColor': '#ffffff',
        'secondaryBackgroundColor': '#f0f2f6',
        'textColor': '#262730',
        'font': 'sans serif'
    }
    
    # 创建配置目录
    config_dir = Path.home() / '.streamlit'
    config_dir.mkdir(exist_ok=True)
    
    # 写入配置文件
    config_file = config_dir / 'config.toml'
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)
    
    print(f"✅ Streamlit配置文件已创建: {config_file}")
    return str(config_file)

def create_credentials_file():
    """创建凭据文件（可选）"""
    
    config_dir = Path.home() / '.streamlit'
    config_dir.mkdir(exist_ok=True)
    
    # 创建空的凭据文件
    credentials_file = config_dir / 'credentials.toml'
    with open(credentials_file, 'w', encoding='utf-8') as f:
        f.write('[general]\n')
        f.write('email = ""\n')
    
    print(f"✅ 凭据文件已创建: {credentials_file}")

def create_public_access_script():
    """创建公网访问启动脚本"""
    
    script_content = '''#!/usr/bin/env python3
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
    print("\\n⚠️  请确保:")
    print("  1. 防火墙已放行8501端口")
    print("  2. 路由器已配置端口转发")
    print("  3. 云服务器安全组已开放端口")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\\n👋 应用已停止")

if __name__ == "__main__":
    main()
'''
    
    with open('start_public.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置可执行权限（Unix系统）
    if os.name != 'nt':
        os.chmod('start_public.py', 0o755)
    
    print("✅ 公网访问启动脚本已创建: start_public.py")

def main():
    """主函数"""
    print("🔧 配置Streamlit公网访问")
    print("=" * 50)
    
    # 创建配置文件
    config_file = create_streamlit_config()
    create_credentials_file()
    create_public_access_script()
    
    print("\\n" + "=" * 50)
    print("✅ 配置完成！")
    print(f"📁 配置文件位置: {Path.home() / '.streamlit'}")
    print("🚀 使用方法:")
    print("  1. 运行: python start_public.py")
    print("  2. 或运行: streamlit run app.py")
    print("\\n⚠️  重要提醒:")
    print("  • 确保防火墙放行8501端口")
    print("  • 配置路由器端口转发")
    print("  • 生产环境建议使用HTTPS")
    print("  • 考虑添加身份验证")

if __name__ == "__main__":
    main()