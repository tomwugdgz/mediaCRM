@echo off
echo 🔧 配置Windows防火墙规则
echo ============================

echo 正在添加Streamlit防火墙规则...
netsh advfirewall firewall add rule name="Streamlit-8501" dir=in action=allow protocol=TCP localport=8501
if %errorlevel% == 0 (
    echo ✅ 防火墙规则添加成功
) else (
    echo ❌ 防火墙规则添加失败，请以管理员身份运行
)

echo.
echo 正在添加Streamlit-8502防火墙规则...
netsh advfirewall firewall add rule name="Streamlit-8502" dir=in action=allow protocol=TCP localport=8502
if %errorlevel% == 0 (
    echo ✅ 防火墙规则添加成功
) else (
    echo ❌ 防火墙规则添加失败，请以管理员身份运行
)

echo.
echo 防火墙规则状态:
netsh advfirewall firewall show rule name="Streamlit-8501"
echo.
netsh advfirewall firewall show rule name="Streamlit-8502"

echo.
echo ============================
echo 配置完成！
echo 请确保:
echo 1. 路由器配置了端口转发
echo 2. 云服务器安全组开放了端口
echo 3. 公网IP正确配置
pause