#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络访问测试脚本
用于测试Streamlit应用的本地和公网访问
"""

import socket
import requests
import subprocess
import platform
import json
from datetime import datetime

def get_network_info():
    """获取网络信息"""
    info = {}
    
    # 获取主机名
    info['hostname'] = socket.gethostname()
    
    # 获取本地IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info['local_ip'] = s.getsockname()[0]
        s.close()
    except Exception:
        info['local_ip'] = "127.0.0.1"
    
    # 获取公网IP
    try:
        info['public_ip'] = requests.get('https://api.ipify.org', timeout=5).text
    except:
        info['public_ip'] = "无法获取"
    
    # 获取系统信息
    info['system'] = platform.system()
    info['platform'] = platform.platform()
    
    return info

def test_port_access(port=8501):
    """测试端口访问"""
    results = {}
    
    # 测试本地访问
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        results['localhost'] = result == 0
    except Exception as e:
        results['localhost'] = False
        results['localhost_error'] = str(e)
    
    # 测试局域网IP访问
    try:
        local_ip = get_network_info()['local_ip']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((local_ip, port))
        sock.close()
        results['local_network'] = result == 0
        results['local_ip'] = local_ip
    except Exception as e:
        results['local_network'] = False
        results['local_network_error'] = str(e)
    
    return results

def test_streamlit_response(url):
    """测试Streamlit响应"""
    try:
        response = requests.get(url, timeout=10)
        return {
            'status_code': response.status_code,
            'accessible': response.status_code == 200,
            'title': '广告置换库存管理系统' if '广告置换库存管理系统' in response.text else 'Unknown'
        }
    except Exception as e:
        return {
            'accessible': False,
            'error': str(e)
        }

def check_firewall_status():
    """检查防火墙状态"""
    system = platform.system()
    firewall_status = {}
    
    if system == "Windows":
        try:
            # 检查Windows防火墙规则
            result = subprocess.run(
                'netsh advfirewall firewall show rule name="Streamlit-8501"',
                shell=True,
                capture_output=True,
                text=True
            )
            firewall_status['rule_exists'] = 'Streamlit-8501' in result.stdout
            firewall_status['rule_details'] = result.stdout if result.returncode == 0 else "规则不存在"
        except Exception as e:
            firewall_status['error'] = str(e)
    
    return firewall_status

def generate_access_report():
    """生成访问报告"""
    print("🔍 网络访问测试报告")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 网络信息
    network_info = get_network_info()
    print("📊 网络信息:")
    print(f"  主机名: {network_info['hostname']}")
    print(f"  本地IP: {network_info['local_ip']}")
    print(f"  公网IP: {network_info['public_ip']}")
    print(f"  系统: {network_info['system']}")
    print()
    
    # 端口测试
    port_test = test_port_access()
    print("🔌 端口访问测试 (端口 8501):")
    print(f"  本地访问 (127.0.0.1:8501): {'✅ 正常' if port_test['localhost'] else '❌ 失败'}")
    print(f"  局域网访问 ({network_info['local_ip']}:8501): {'✅ 正常' if port_test['local_network'] else '❌ 失败'}")
    if not port_test['localhost']:
        print(f"  错误信息: {port_test.get('localhost_error', '未知错误')}")
    if not port_test['local_network']:
        print(f"  错误信息: {port_test.get('local_network_error', '未知错误')}")
    print()
    
    # Streamlit响应测试
    if port_test['localhost']:
        print("🌐 Streamlit响应测试:")
        local_test = test_streamlit_response("http://127.0.0.1:8501")
        print(f"  本地响应: {'✅ 正常' if local_test['accessible'] else '❌ 失败'}")
        if local_test['accessible']:
            print(f"  页面标题: {local_test['title']}")
        
        # 测试局域网IP
        local_ip_test = test_streamlit_response(f"http://{network_info['local_ip']}:8501")
        print(f"  局域网响应: {'✅ 正常' if local_ip_test['accessible'] else '❌ 失败'}")
        print()
    
    # 防火墙状态
    firewall_info = check_firewall_status()
    if firewall_info:
        print("🔒 防火墙状态:")
        print(f"  Streamlit规则: {'✅ 已配置' if firewall_info.get('rule_exists') else '❌ 未配置'}")
        if firewall_info.get('rule_exists'):
            print("  规则详情: 已添加防火墙放行规则")
        print()
    
    # 访问地址总结
    print("🌍 访问地址:")
    print(f"  本地访问: http://127.0.0.1:8501")
    print(f"  局域网访问: http://{network_info['local_ip']}:8501")
    print(f"  公网访问: http://{network_info['public_ip']}:8501 (需端口转发)")
    print()
    
    # 建议和注意事项
    print("⚠️  配置建议:")
    if not port_test['localhost']:
        print("  • Streamlit服务可能未启动，请检查应用状态")
    if not port_test['local_network']:
        print("  • 检查防火墙设置，确保8501端口已放行")
        print("  • 检查Streamlit配置，确保监听地址为0.0.0.0")
    if not firewall_info.get('rule_exists'):
        print("  • 建议运行 setup_firewall.bat (以管理员身份) 配置防火墙")
    
    print("  • 如需公网访问，请配置路由器端口转发")
    print("  • 生产环境建议使用HTTPS和身份验证")
    print()
    
    # 生成配置文件
    config = {
        'network_info': network_info,
        'port_test': port_test,
        'firewall_status': firewall_info,
        'access_urls': {
            'localhost': 'http://127.0.0.1:8501',
            'local_network': f"http://{network_info['local_ip']}:8501",
            'public': f"http://{network_info['public_ip']}:8501"
        },
        'timestamp': datetime.now().isoformat()
    }
    
    with open('network_test_report.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("📄 详细报告已保存到: network_test_report.json")

def main():
    """主函数"""
    generate_access_report()

if __name__ == "__main__":
    main()