
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广告置换库存管理系统 - Web界面
使用Streamlit构建的现代化用户界面
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os
import json
from inventory_manager import InventoryManager
from pricing_calculator import PricingCalculator
from financial_calculator import FinancialCalculator

# 页面配置
st.set_page_config(
    page_title="广告置换库存管理系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化管理器
@st.cache_resource
def init_managers():
    return {
        'inventory': InventoryManager(),
        'pricing': PricingCalculator(),
        'financial': FinancialCalculator()
    }

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .warning-text {
        color: #ffc107;
        font-weight: bold;
    }
    .danger-text {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主函数"""
    managers = init_managers()
    
    # 侧边栏导航
    st.sidebar.title("📊 导航系统")
    
    menu_items = {
        "🏠 系统概览": "dashboard",
        "📦 库存管理": "inventory",
        "📺 媒体管理": "media",
        "🛒 渠道管理": "channels",
        "💰 定价分析": "pricing",
        "📈 财务测算": "financial",
        "⚠️ 风控检查": "risk",
        "📊 数据报表": "reports",
        "🔧 系统设置": "settings"
    }
    
    selected_menu = st.sidebar.radio("选择功能", list(menu_items.keys()))
    selected_function = menu_items[selected_menu]
    
    # 主内容区
    st.markdown('<div class="main-header">广告置换库存管理系统</div>', unsafe_allow_html=True)
    
    if selected_function == "dashboard":
        show_dashboard(managers)
    elif selected_function == "inventory":
        show_inventory_management(managers)
    elif selected_function == "media":
        show_media_management(managers)
    elif selected_function == "channels":
        show_channel_management(managers)
    elif selected_function == "pricing":
        show_pricing_analysis(managers)
    elif selected_function == "financial":
        show_financial_analysis(managers)
    elif selected_function == "risk":
        show_risk_management(managers)
    elif selected_function == "reports":
        show_reports(managers)
    elif selected_function == "settings":
        show_settings(managers)

def show_dashboard(managers):
    """显示系统概览"""
    st.header("🏠 系统概览")
    
    # 获取统计数据
    summary = managers['inventory'].get_inventory_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_inventory = sum(item['count'] for item in summary['inventory_stats'])
        st.metric("库存商品总数", f"{total_inventory} 件")
    
    with col2:
        total_value = sum(item['total_value'] for item in summary['inventory_stats'])
        st.metric("库存总价值", f"¥{total_value:,.2f}")
    
    with col3:
        pending_count = next((item['count'] for item in summary['inventory_stats'] if item['status'] == 'pending'), 0)
        st.metric("待处理库存", f"{pending_count} 件")
    
    with col4:
        brand_count = len(summary['brand_stats'])
        st.metric("合作品牌数", f"{brand_count} 个")
    
    # 图表展示
    col1, col2 = st.columns(2)
    
    with col1:
        # 库存状态分布
        inventory_stats_df = pd.DataFrame(summary['inventory_stats'])
        if not inventory_stats_df.empty:
            fig_inventory = px.pie(inventory_stats_df, values='count', names='status',
                                 title='库存状态分布')
            st.plotly_chart(fig_inventory, use_container_width=True)
    
    with col2:
        # 品类分布
        category_stats_df = pd.DataFrame(summary['category_stats'])
        if not category_stats_df.empty:
            fig_category = px.bar(category_stats_df, x='category', y='count',
                                title='商品品类分布')
            st.plotly_chart(fig_category, use_container_width=True)
    
    # 最近交易概览
    st.subheader("最近交易")
    conn = sqlite3.connect("inventory.db")
    try:
        recent_transactions = pd.read_sql_query('''
            SELECT t.*, i.product_name, b.brand_name, sc.channel_name
            FROM transactions t
            JOIN inventory i ON t.inventory_id = i.id
            JOIN brands b ON t.brand_id = b.id
            JOIN sales_channels sc ON t.channel_id = sc.id
            ORDER BY t.transaction_date DESC
            LIMIT 10
        ''', conn)
        
        if not recent_transactions.empty:
            # 显示可用的交易记录字段
            display_columns = ['transaction_date', 'product_name', 'brand_name', 'channel_name', 'sale_price', 'profit']
            available_columns = [col for col in display_columns if col in recent_transactions.columns]
            if available_columns:
                st.dataframe(recent_transactions[available_columns])
            else:
                st.dataframe(recent_transactions)
        else:
            st.info("暂无交易记录")
    finally:
        conn.close()

def show_inventory_management(managers):
    """显示库存管理界面"""
    st.header("📦 库存管理")
    
    tab1, tab2, tab3, tab4 = st.tabs(["库存列表", "添加库存", "品牌管理", "库存操作"])
    
    with tab1:
        show_inventory_list(managers)
    
    with tab2:
        show_add_inventory(managers)
    
    with tab3:
        show_brand_management(managers)
    
    with tab4:
        show_inventory_operations(managers)

def show_inventory_list(managers):
    """显示库存列表"""
    st.subheader("库存列表")
    
    # 获取库存数据
    conn = sqlite3.connect("inventory.db")
    try:
        inventory_df = pd.read_sql_query('''
            SELECT i.*, b.brand_name, b.reputation_score
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            ORDER BY i.created_at DESC
        ''', conn)
        
        if not inventory_df.empty:
            # 搜索和筛选
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_term = st.text_input("搜索商品", "")
            
            with col2:
                status_filter = st.selectbox("状态筛选", ["全部", "pending", "approved", "rejected", "sold"])
            
            with col3:
                category_filter = st.selectbox("品类筛选", ["全部"] + list(inventory_df['category'].unique()))
            
            # 应用筛选
            filtered_df = inventory_df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['product_name'].str.contains(search_term, case=False)]
            if status_filter != "全部":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            if category_filter != "全部":
                filtered_df = filtered_df[filtered_df['category'] == category_filter]
            
            # 显示数据表格
            st.dataframe(filtered_df)
            
            # 显示商品详情和链接
            if st.checkbox("显示商品详情和电商链接"):
                selected_product = st.selectbox("选择商品查看详情", filtered_df['product_name'].tolist())
                if selected_product:
                    product_info = filtered_df[filtered_df['product_name'] == selected_product].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**商品信息**")
                        st.write(f"商品名称: {product_info['product_name']}")
                        st.write(f"品牌: {product_info['brand_name']}")
                        st.write(f"品类: {product_info['category']}")
                        st.write(f"数量: {product_info['quantity']}")
                        st.write(f"原始价值: ¥{product_info['original_value']:,.2f}")
                        if pd.notna(product_info['market_value']):
                            st.write(f"市场价值: ¥{product_info['market_value']:,.2f}")
                    
                    with col2:
                        st.write("**电商链接**")
                        if pd.notna(product_info.get('jd_link')):
                            st.markdown(f"[京东链接]({product_info['jd_link']})")
                        if pd.notna(product_info.get('tmall_link')):
                            st.markdown(f"[天猫链接]({product_info['tmall_link']})")
                        if pd.notna(product_info.get('xianyu_link')):
                            st.markdown(f"[闲鱼链接]({product_info['xianyu_link']})")
                        if pd.notna(product_info.get('pdd_link')):
                            st.markdown(f"[拼多多链接]({product_info['pdd_link']})")
                        
                        if pd.isna(product_info.get('jd_link')) and pd.isna(product_info.get('tmall_link')) and pd.isna(product_info.get('xianyu_link')) and pd.isna(product_info.get('pdd_link')):
                            st.info("暂无电商链接信息")
            
            # 操作按钮
            if st.button("导出库存数据"):
                filename = managers['inventory'].export_to_excel()
                st.success(f"数据已导出到: {filename}")
        else:
            st.info("暂无库存数据")
    finally:
        conn.close()

def show_add_inventory(managers):
    """显示添加库存界面"""
    st.subheader("添加库存")
    
    with st.form("add_inventory_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # 获取品牌列表
            conn = sqlite3.connect("inventory.db")
            brands_df = pd.read_sql_query("SELECT * FROM brands", conn)
            conn.close()
            
            brand_options = {row['brand_name']: row['id'] for _, row in brands_df.iterrows()}
            selected_brand = st.selectbox("选择品牌", list(brand_options.keys()))
            
            product_name = st.text_input("商品名称", placeholder="如：可口可乐经典装")
            category = st.selectbox("商品品类", ["饮料", "日化", "家电", "食品", "其他"])
            quantity = st.number_input("数量", min_value=1, value=100)
            original_value = st.number_input("原始价值 (元)", min_value=0.0, value=10000.0)
        
        with col2:
            market_value = st.number_input("市场价值 (元)", min_value=0.0, value=None,
                                         help="基于拼多多/闲鱼价格")
            expiry_date = st.date_input("保质期", value=None,
                                      help="可选，格式：YYYY-MM-DD")
            storage_location = st.text_input("存储位置", placeholder="如：仓库A")
            
            # 电商链接输入
            st.write("**电商链接**")
            jd_link = st.text_input("京东商品链接", placeholder="https://item.jd.com/xxx.html")
            tmall_link = st.text_input("天猫商品链接", placeholder="https://detail.tmall.com/xxx.html")
            xianyu_link = st.text_input("闲鱼商品链接", placeholder="https://2.taobao.com/xxx")
            pdd_link = st.text_input("拼多多商品链接", placeholder="https://mobile.yangkeduo.com/xxx.html")
        
        submitted = st.form_submit_button("添加库存", type="primary")
        
        if submitted:
            try:
                brand_id = brand_options[selected_brand]
                expiry_str = expiry_date.strftime('%Y-%m-%d') if expiry_date else None
                
                inventory_id = managers['inventory'].add_inventory(
                    brand_id=brand_id,
                    product_name=product_name,
                    category=category,
                    quantity=quantity,
                    original_value=original_value,
                    market_value=market_value if market_value is not None and market_value > 0 else None,
                    expiry_date=expiry_str,
                    storage_location=storage_location,
                    jd_link=jd_link if jd_link.strip() else None,
                    tmall_link=tmall_link if tmall_link.strip() else None,
                    xianyu_link=xianyu_link if xianyu_link.strip() else None,
                    pdd_link=pdd_link if pdd_link.strip() else None
                )
                
                st.success(f"库存添加成功！ID: {inventory_id}")
                
                # 自动进行定价分析
                if st.checkbox("立即进行定价分析"):
                    pricing_result = managers['pricing'].calculate_realization_value(inventory_id)
                    st.json(pricing_result)
                
            except Exception as e:
                st.error(f"添加失败: {str(e)}")

def show_brand_management(managers):
    """显示品牌管理界面"""
    st.subheader("品牌管理")
    
    with st.form("add_brand_form"):
        st.write("添加新品牌")
        
        col1, col2 = st.columns(2)
        
        with col1:
            brand_name = st.text_input("品牌名称", placeholder="如：可口可乐")
            contact_person = st.text_input("联系人", placeholder="如：张经理")
            contact_phone = st.text_input("联系电话", placeholder="如：13800138000")
        
        with col2:
            contact_email = st.text_input("邮箱", placeholder="如：zhang@coke.com")
            brand_type = st.selectbox("品牌类型", ["饮料", "日化", "家电", "食品", "其他"])
            reputation_score = st.slider("品牌声誉评分", 1, 10, 7)
        
        submitted = st.form_submit_button("添加品牌", type="primary")
        
        if submitted:
            try:
                brand_id = managers['inventory'].add_brand(
                    brand_name=brand_name,
                    contact_person=contact_person,
                    contact_phone=contact_phone,
                    contact_email=contact_email,
                    brand_type=brand_type,
                    reputation_score=reputation_score
                )
                st.success(f"品牌添加成功！ID: {brand_id}")
            except Exception as e:
                st.error(f"添加失败: {str(e)}")

def show_pricing_analysis(managers):
    """显示定价分析界面"""
    st.header("💰 定价分析")
    
    # 获取待定价的库存
    conn = sqlite3.connect("inventory.db")
    try:
        pending_inventory = pd.read_sql_query('''
            SELECT i.*, b.brand_name
            FROM inventory i
            JOIN brands b ON i.brand_id = b.id
            WHERE i.status = 'pending' OR i.market_value IS NULL
            ORDER BY i.created_at DESC
        ''', conn)
        
        if pending_inventory.empty:
            st.info("暂无需要定价的库存")
            return
        
        st.subheader(f"待定价商品 ({len(pending_inventory)} 件)")
        
        # 批量定价
        if st.button("批量定价分析", type="primary"):
            with st.spinner("正在进行定价分析..."):
                inventory_ids = pending_inventory['id'].tolist()
                pricing_results = managers['pricing'].batch_calculate_prices(inventory_ids)
                
                # 显示结果
                results_df = pd.DataFrame(pricing_results)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_realization_rate = results_df['realization_rate'].mean()
                    st.metric("平均变现率", f"{avg_realization_rate:.2%}")
                
                with col2:
                    total_expected_return = results_df['expected_cash_return'].sum()
                    st.metric("预期总回报", f"¥{total_expected_return:,.2f}")
                
                with col3:
                    high_risk_count = len(results_df[results_df['risk_level'] == 'high'])
                    st.metric("高风险商品", f"{high_risk_count} 件")
                
                # 详细结果表格
                st.dataframe(results_df[['product_name', 'original_value', 'market_value', 
                                       'realization_rate', 'expected_cash_return', 'risk_level']])
                
                # 生成报告
                if st.button("生成定价报告"):
                    report_file = managers['pricing'].generate_pricing_report(inventory_ids)
                    st.success(f"定价报告已生成: {report_file}")
                    
        else:
            # 单个商品定价
            selected_product = st.selectbox(
                "选择商品进行定价分析",
                pending_inventory['product_name'].tolist()
            )
            
            if st.button("分析选中商品"):
                product_info = pending_inventory[pending_inventory['product_name'] == selected_product].iloc[0]
                result = managers['pricing'].calculate_realization_value(product_info['id'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**定价分析结果**")
                    st.write(f"商品名称: {result.get('product_name', selected_product)}")
                    st.write(f"原始价值: ¥{result.get('original_value', 0):,.2f}")
                    st.write(f"市场价值: ¥{result.get('market_value', 0):,.2f}")
                    st.write(f"变现率: {result.get('realization_rate', 0):.2%}")
                
                with col2:
                    st.write("**收益预测**")
                    st.write(f"建议销售价格: ¥{result.get('recommended_sale_price', 0):,.2f}")
                    st.write(f"预期现金回报: ¥{result.get('expected_cash_return', 0):,.2f}")
                    st.write(f"风险等级: {result.get('risk_level', '未知')}")
                
                # 价格来源详情
                if 'price_sources' in result:
                    st.write("**价格来源**")
                    price_sources = result['price_sources']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"拼多多价格: ¥{price_sources.get('pdd_price', '暂无数据')}")
                    with col2:
                        st.write(f"闲鱼价格: ¥{price_sources.get('xianyu_price', '暂无数据')}")
    
    finally:
        conn.close()

def show_financial_analysis(managers):
    """显示财务分析界面"""
    st.header("📈 财务测算")
    
    tab1, tab2, tab3 = st.tabs(["交易测算", "利润预测", "财务报告"])
    
    with tab1:
        show_transaction_calculation(managers)
    
    with tab2:
        show_profit_forecast(managers)
    
    with tab3:
        show_financial_reports(managers)

def show_transaction_calculation(managers):
    """显示交易测算"""
    st.subheader("交易利润测算")
    
    # 获取选择项
    conn = sqlite3.connect("inventory.db")
    try:
        inventory_df = pd.read_sql_query("SELECT id, product_name FROM inventory WHERE status = 'pending'", conn)
        ad_resources_df = pd.read_sql_query("SELECT id, media_name as resource_name FROM media_resources WHERE status = 'idle'", conn)
        channels_df = pd.read_sql_query("SELECT id, channel_name FROM sales_channels", conn)
        
        if inventory_df.empty or ad_resources_df.empty or channels_df.empty:
            st.warning("请先添加库存、广告资源和销售渠道")
            return
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_inventory = st.selectbox(
                "选择库存商品",
                inventory_df['product_name'].tolist()
            )
        
        with col2:
            selected_ad_resource = st.selectbox(
                "选择广告资源",
                ad_resources_df['resource_name'].tolist()
            )
        
        with col3:
            selected_channel = st.selectbox(
                "选择销售渠道",
                channels_df['channel_name'].tolist()
            )
        
        proposed_price = st.number_input("建议销售价格 (可选)", min_value=0.0, value=0.0, 
                                       help="留空将使用自动定价")
        
        if st.button("计算利润", type="primary"):
            # 获取ID
            inventory_id = inventory_df[inventory_df['product_name'] == selected_inventory]['id'].iloc[0]
            ad_resource_id = ad_resources_df[ad_resources_df['resource_name'] == selected_ad_resource]['id'].iloc[0]
            channel_id = channels_df[channels_df['channel_name'] == selected_channel]['id'].iloc[0]
            
            # 计算利润
            result = managers['financial'].calculate_transaction_profit(
                inventory_id, ad_resource_id, channel_id,
                proposed_price if proposed_price > 0 else None
            )
            
            if 'error' in result:
                st.error(result['error'])
            else:
                # 显示结果
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if result['feasibility']:
                        st.success("✅ 交易可行")
                    else:
                        st.error("❌ 交易不可行")
                    
                    st.metric("总收入", f"¥{result['total_revenue']:,.2f}")
                    st.metric("总成本", f"¥{result['total_cost']:,.2f}")
                
                with col2:
                    st.metric("净利润", f"¥{result['net_profit']:,.2f}")
                    st.metric("利润率", f"{result['profit_margin']:.2%}")
                    st.metric("投资回报率", f"{result['return_on_investment']:.2%}")
                
                with col3:
                    st.metric("变现率", f"{result['realization_rate']:.2%}")
                    st.metric("风险等级", result['risk_assessment']['risk_level'])
                
                # 成本明细
                with st.expander("查看成本明细"):
                    cost_df = pd.DataFrame(list(result['cost_breakdown'].items()), 
                                         columns=['成本项目', '金额'])
                    st.dataframe(cost_df)
                
                # 建议
                if result['recommendations']:
                    with st.expander("查看建议"):
                        for rec in result['recommendations']:
                            st.write(rec)
    
    finally:
        conn.close()

def show_profit_forecast(managers):
    """显示利润预测"""
    st.subheader("利润预测")
    
    months = st.slider("预测月份", 1, 12, 3)
    
    if st.button("生成预测报告", type="primary"):
        with st.spinner("正在生成预测报告..."):
            forecast = managers['financial'].generate_profit_forecast(months)
            
            st.write(f"**预测期间: {months} 个月**")
            st.write(f"历史月均利润: ¥{forecast['historical_avg_profit']:,.2f}")
            st.write(f"待处理库存价值: ¥{forecast['pending_inventory_value']:,.2f}")
            st.write(f"预测总利润: ¥{forecast['total_predicted_profit']:,.2f}")
            
            # 预测图表
            forecast_df = pd.DataFrame(forecast['monthly_forecast'])
            fig = px.line(forecast_df, x='month', y='predicted_profit',
                         title='月度利润预测')
            st.plotly_chart(fig, use_container_width=True)
            
            # 详细数据
            st.dataframe(forecast_df)

def show_financial_reports(managers):
    """显示财务报告"""
    st.subheader("财务报告")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("开始日期", 
                                 value=datetime.now() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("结束日期", 
                               value=datetime.now())
    
    if st.button("生成财务报告", type="primary"):
        with st.spinner("正在生成财务报告..."):
            report_file = managers['financial'].generate_financial_report(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            st.success(f"财务报告已生成: {report_file}")

def show_risk_management(managers):
    """显示风险管理界面"""
    st.header("⚠️ 风控管理")
    
    tab1, tab2 = st.tabs(["风控检查", "风控规则"])
    
    with tab1:
        show_risk_check(managers)
    
    with tab2:
        show_risk_rules(managers)

def show_risk_check(managers):
    """显示风控检查"""
    st.subheader("库存风控检查")
    
    # 获取待检查库存
    conn = sqlite3.connect("inventory.db")
    try:
        inventory_df = pd.read_sql_query('''
            SELECT i.*, b.brand_name
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            WHERE i.status = 'pending'
            ORDER BY i.created_at DESC
        ''', conn)
        
        if inventory_df.empty:
            st.info("暂无待检查库存")
            return
        
        # 选择要检查的商品
        selected_products = st.multiselect(
            "选择要检查的商品",
            inventory_df['product_name'].tolist()
        )
        
        if st.button("执行风控检查", type="primary"):
            results = []
            for product_name in selected_products:
                product_info = inventory_df[inventory_df['product_name'] == product_name].iloc[0]
                result = managers['inventory'].check_inventory_risk(product_info['id'])
                results.append({
                    '商品名称': product_name,
                    '检查结果': '通过' if result['passed'] else '不通过',
                    '违规项': '; '.join(result['violations']) if result['violations'] else '无',
                    '建议': '; '.join(result['suggestions']) if result['suggestions'] else '无'
                })
            
            # 显示结果
            results_df = pd.DataFrame(results)
            
            for _, row in results_df.iterrows():
                if row['检查结果'] == '通过':
                    st.success(f"✅ {row['商品名称']} - 检查通过")
                else:
                    st.error(f"❌ {row['商品名称']} - 检查不通过")
                    if row['违规项']:
                        st.write(f"违规项: {row['违规项']}")
                    if row['建议']:
                        st.write(f"建议: {row['建议']}")
        
    finally:
        conn.close()

def show_risk_rules(managers):
    """显示风控规则"""
    st.subheader("风控规则管理")
    
    # 获取当前规则
    rules = managers['inventory'].get_active_risk_rules()
    
    if rules:
        for rule in rules:
            with st.expander(f"{rule['rule_name']}"):
                st.write(f"规则类型: {rule['rule_type']}")
                st.write(f"配置: {json.dumps(rule['rule_config'], ensure_ascii=False, indent=2)}")
    else:
        st.info("暂无风控规则")

def show_reports(managers):
    """显示报表界面"""
    st.header("📊 数据报表")
    
    st.subheader("数据导出")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("导出库存数据", type="primary"):
            filename = managers['inventory'].export_to_excel()
            st.success(f"库存数据已导出: {filename}")
    
    with col2:
        if st.button("生成定价报告"):
            conn = sqlite3.connect("inventory.db")
            try:
                pending_ids = pd.read_sql_query(
                    "SELECT id FROM inventory WHERE status = 'pending'", conn
                )['id'].tolist()
                if pending_ids:
                    report_file = managers['pricing'].generate_pricing_report(pending_ids)
                    st.success(f"定价报告已生成: {report_file}")
                else:
                    st.info("暂无待定价商品")
            finally:
                conn.close()
    
    with col3:
        if st.button("生成财务报告"):
            report_file = managers['financial'].generate_financial_report()
            st.success(f"财务报告已生成: {report_file}")

def show_settings(managers):
    """显示系统设置"""
    st.header("🔧 系统设置")
    
    st.subheader("数据库管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("初始化数据库", type="primary"):
            try:
                # 重新初始化数据库
                os.remove("inventory.db")
                managers['inventory'] = InventoryManager()
                st.success("数据库初始化成功！")
            except Exception as e:
                st.error(f"初始化失败: {str(e)}")
    
    with col2:
        if st.button("清理示例数据"):
            st.info("清理功能开发中...")
    
    st.subheader("系统信息")
    
    # 显示数据库统计
    conn = sqlite3.connect("inventory.db")
    try:
        tables = ['inventory', 'brands', 'media_resources', 'sales_channels', 'transactions']
        stats = {}
        for table in tables:
            count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn).iloc[0]['count']
            stats[table] = count
        
        stats_df = pd.DataFrame(list(stats.items()), columns=['表名', '记录数'])
        st.dataframe(stats_df)
        
    finally:
        conn.close()

def show_media_management(managers):
    """显示媒体管理界面"""
    st.header("📺 媒体管理")
    
    tab1, tab2, tab3, tab4 = st.tabs(["媒体列表", "添加媒体", "媒体分析", "媒体操作"])
    
    with tab1:
        show_media_list(managers)
    
    with tab2:
        show_add_media(managers)
    
    with tab3:
        show_media_analysis(managers)
    
    with tab4:
        show_media_operations(managers)

def show_media_list(managers):
    """显示媒体列表"""
    st.subheader("媒体资源列表")
    
    conn = sqlite3.connect("inventory.db")
    try:
        media_df = pd.read_sql_query('''
            SELECT * FROM media_resources
            ORDER BY created_at DESC
        ''', conn)
        
        if not media_df.empty:
            # 搜索和筛选
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_term = st.text_input("搜索媒体", "")
            
            with col2:
                media_type_filter = st.selectbox("媒体类型筛选", ["全部"] + list(media_df['media_type'].unique()))
            
            with col3:
                status_filter = st.selectbox("状态筛选", ["全部", "idle", "occupied", "maintenance", "reserved"])
            
            # 应用筛选
            filtered_df = media_df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['media_name'].str.contains(search_term, case=False)]
            if media_type_filter != "全部":
                filtered_df = filtered_df[filtered_df['media_type'] == media_type_filter]
            if status_filter != "全部":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            # 显示数据表格
            st.dataframe(filtered_df)
            
            # 操作按钮
            if st.button("导出媒体数据"):
                filename = f"media_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    filtered_df.to_excel(writer, sheet_name='媒体数据', index=False)
                st.success(f"媒体数据已导出到: {filename}")
        else:
            st.info("暂无媒体资源数据")
    finally:
        conn.close()

def show_add_media(managers):
    """显示添加媒体界面"""
    st.subheader("添加媒体资源")
    
    with st.form("add_media_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            media_name = st.text_input("媒体名称", placeholder="如：朝阳小区门禁广告")
            media_type = st.selectbox("媒体类型", ["社区门禁", "写字楼电梯", "户外大屏", "公交站牌", "地铁广告", "商场广告", "其他"])
            media_form = st.selectbox("媒体形式", ["静态海报", "动态LED", "液晶屏", "灯箱", "三面翻", "其他"])
            location = st.text_input("具体位置", placeholder="如：北京市朝阳区XX小区")
            market_price = st.number_input("刊例价格 (元)", min_value=0.0, value=5000.0)
            discount_rate = st.number_input("折扣率 (%)", min_value=0.0, max_value=100.0, value=80.0)
        
        with col2:
            actual_cost = st.number_input("实际成本 (元)", min_value=0.0, value=None,
                                         help="留空将自动计算：刊例价 × 折扣率")
            media_specs = st.text_area("媒体规格", placeholder="如：120cm×80cm，高清LED屏")
            audience_info = st.text_area("受众信息", placeholder="如：日均人流量5000+，主要受众为白领群体")
            owner_name = st.text_input("媒体主名称", placeholder="如：北京XX广告有限公司")
            contact_person = st.text_input("联系人", placeholder="如：张经理")
            contact_phone = st.text_input("联系电话", placeholder="如：13800138000")
            contract_start = st.date_input("合同开始日期", value=None)
            contract_end = st.date_input("合同结束日期", value=None)
        
        submitted = st.form_submit_button("添加媒体", type="primary")
        
        if submitted:
            try:
                # 计算实际成本
                if actual_cost is None or actual_cost == 0:
                    actual_cost = market_price * discount_rate / 100
                
                # 转换日期格式
                start_str = contract_start.strftime('%Y-%m-%d') if contract_start else None
                end_str = contract_end.strftime('%Y-%m-%d') if contract_end else None
                
                # 添加媒体资源
                media_id = managers['inventory'].add_media_resource(
                    media_name=media_name,
                    media_type=media_type,
                    media_form=media_form,
                    location=location,
                    market_price=market_price,
                    discount_rate=discount_rate,
                    actual_cost=actual_cost,
                    media_specs=media_specs,
                    audience_info=audience_info,
                    owner_name=owner_name,
                    contact_person=contact_person,
                    contact_phone=contact_phone,
                    contract_start=start_str,
                    contract_end=end_str
                )
                
                st.success(f"媒体资源添加成功！ID: {media_id}")
                
            except Exception as e:
                st.error(f"添加失败: {str(e)}")

def show_media_analysis(managers):
    """显示媒体分析"""
    st.subheader("媒体资源分析")
    
    conn = sqlite3.connect("inventory.db")
    try:
        media_df = pd.read_sql_query('SELECT * FROM media_resources', conn)
        
        if not media_df.empty:
            # 媒体类型分布
            col1, col2 = st.columns(2)
            
            with col1:
                type_stats = media_df['media_type'].value_counts()
                fig_type = px.pie(values=type_stats.values, names=type_stats.index,
                                title='媒体类型分布')
                st.plotly_chart(fig_type, use_container_width=True)
            
            with col2:
                status_stats = media_df['status'].value_counts()
                fig_status = px.bar(x=status_stats.index, y=status_stats.values,
                                  title='媒体状态分布')
                st.plotly_chart(fig_status, use_container_width=True)
            
            # 价格分析
            st.subheader("价格分析")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_market_price = media_df['market_price'].mean()
                st.metric("平均刊例价", f"¥{avg_market_price:,.2f}")
            
            with col2:
                avg_discount = media_df['discount_rate'].mean()
                st.metric("平均折扣率", f"{avg_discount:.1f}%")
            
            with col3:
                avg_actual_cost = media_df['actual_cost'].mean()
                st.metric("平均实际成本", f"¥{avg_actual_cost:,.2f}")
            
            # 合同到期提醒
            st.subheader("合同到期提醒")
            today = datetime.now().date()
            upcoming_end = []
            
            for _, row in media_df.iterrows():
                if row['contract_end']:
                    try:
                        end_date = pd.to_datetime(row['contract_end']).date()
                        days_until_end = (end_date - today).days
                        if 0 <= days_until_end <= 30:  # 30天内到期
                            upcoming_end.append({
                                '媒体名称': row['media_name'],
                                '到期日期': row['contract_end'],
                                '剩余天数': days_until_end
                            })
                    except:
                        continue
            
            if upcoming_end:
                reminder_df = pd.DataFrame(upcoming_end)
                st.dataframe(reminder_df)
                st.warning(f"⚠️ 有 {len(upcoming_end)} 个媒体资源即将在30天内到期")
            else:
                st.info("暂无即将到期的媒体资源")
                
        else:
            st.info("暂无媒体资源数据")
    finally:
        conn.close()

def show_channel_management(managers):
    """显示渠道管理界面"""
    st.header("🛒 渠道管理")
    
    tab1, tab2, tab3, tab4 = st.tabs(["渠道列表", "添加渠道", "渠道分析", "渠道操作"])
    
    with tab1:
        show_channel_list(managers)
    
    with tab2:
        show_add_channel(managers)
    
    with tab3:
        show_channel_analysis(managers)
    
    with tab4:
        show_channel_operations(managers)

def show_channel_list(managers):
    """显示渠道列表"""
    st.subheader("销售渠道列表")
    
    conn = sqlite3.connect("inventory.db")
    try:
        channels_df = pd.read_sql_query('''
            SELECT * FROM sales_channels
            ORDER BY created_at DESC
        ''', conn)
        
        if not channels_df.empty:
            # 搜索和筛选
            col1, col2 = st.columns(2)
            
            with col1:
                search_term = st.text_input("搜索渠道", "")
            
            with col2:
                channel_type_filter = st.selectbox("渠道类型筛选", ["全部"] + list(channels_df['channel_type'].unique()))
            
            # 应用筛选
            filtered_df = channels_df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['channel_name'].str.contains(search_term, case=False)]
            if channel_type_filter != "全部":
                filtered_df = filtered_df[filtered_df['channel_type'] == channel_type_filter]
            
            # 显示数据表格
            st.dataframe(filtered_df)
            
            # 操作按钮
            if st.button("导出渠道数据"):
                filename = f"channels_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    filtered_df.to_excel(writer, sheet_name='渠道数据', index=False)
                st.success(f"渠道数据已导出到: {filename}")
        else:
            st.info("暂无销售渠道数据")
    finally:
        conn.close()

def show_add_channel(managers):
    """显示添加渠道界面"""
    st.subheader("添加销售渠道")
    
    with st.form("add_channel_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            channel_name = st.text_input("渠道名称", placeholder="如：王团长团购")
            channel_type = st.selectbox("渠道类型", ["S级(团长)", "A级(批发市场)", "B级(零售商)", "C级(个体户)", "电商平台", "其他"])
            contact_person = st.text_input("联系人", placeholder="如：王团长")
            contact_phone = st.text_input("联系电话", placeholder="如：13800138000")
        
        with col2:
            commission_rate = st.number_input("佣金比例 (%)", min_value=0.0, max_value=100.0, value=5.0)
            payment_terms = st.selectbox("结算方式", ["现结", "周结", "月结", "季度结", "批量结算", "其他"])
            notes = st.text_area("备注信息", placeholder="如：主要销售日化用品，信誉良好")
        
        submitted = st.form_submit_button("添加渠道", type="primary")
        
        if submitted:
            try:
                # 添加销售渠道
                channel_id = managers['inventory'].add_sales_channel(
                    channel_name=channel_name,
                    channel_type=channel_type,
                    contact_person=contact_person,
                    contact_phone=contact_phone,
                    commission_rate=commission_rate,
                    payment_terms=payment_terms
                )
                
                st.success(f"销售渠道添加成功！ID: {channel_id}")
                
            except Exception as e:
                st.error(f"添加失败: {str(e)}")

def show_channel_analysis(managers):
    """显示渠道分析"""
    st.subheader("销售渠道分析")
    
    conn = sqlite3.connect("inventory.db")
    try:
        channels_df = pd.read_sql_query('SELECT * FROM sales_channels', conn)
        
        if not channels_df.empty:
            # 渠道类型分布
            col1, col2 = st.columns(2)
            
            with col1:
                type_stats = channels_df['channel_type'].value_counts()
                fig_type = px.pie(values=type_stats.values, names=type_stats.index,
                                title='渠道类型分布')
                st.plotly_chart(fig_type, use_container_width=True)
            
            with col2:
                commission_stats = channels_df.groupby('channel_type')['commission_rate'].mean()
                fig_commission = px.bar(x=commission_stats.index, y=commission_stats.values,
                                      title='各类型渠道平均佣金率')
                st.plotly_chart(fig_commission, use_container_width=True)
            
            # 统计信息
            st.subheader("渠道统计")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_channels = len(channels_df)
                st.metric("渠道总数", f"{total_channels} 个")
            
            with col2:
                s_level_channels = len(channels_df[channels_df['channel_type'] == 'S级(团长)'])
                st.metric("S级渠道", f"{s_level_channels} 个")
            
            with col3:
                avg_commission = channels_df['commission_rate'].mean()
                st.metric("平均佣金率", f"{avg_commission:.1f}%")
            
            with col4:
                active_channels = len(channels_df[channels_df['contact_phone'].notna()])
                st.metric("有效联系渠道", f"{active_channels} 个")
        else:
            st.info("暂无销售渠道数据")
    finally:
        conn.close()

def show_inventory_operations(managers):
    """显示库存操作界面（修改/删除）"""
    st.subheader("库存商品操作")
    
    # 获取库存数据
    inventory_data = managers['inventory'].get_all_inventory()
    
    if not inventory_data:
        st.info("暂无库存数据")
        return
    
    # 转换为DataFrame以便处理
    inventory_df = pd.DataFrame(inventory_data)
    
    # 选择要操作的商品
    selected_product = st.selectbox(
        "选择要操作的商品",
        inventory_df['product_name'].tolist(),
        key="inventory_operations_select"
    )
    
    if selected_product:
        product_info = inventory_df[inventory_df['product_name'] == selected_product].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**当前商品信息**")
            st.write(f"商品名称: {product_info['product_name']}")
            st.write(f"品牌: {product_info.get('brand_name', '未知')}")
            st.write(f"品类: {product_info['category']}")
            st.write(f"数量: {product_info['quantity']}")
            st.write(f"原始价值: ¥{product_info['original_value']:,.2f}")
            if pd.notna(product_info.get('market_value')):
                st.write(f"市场价值: ¥{product_info['market_value']:,.2f}")
            st.write(f"状态: {product_info['status']}")
            
            # 显示电商链接
            st.write("**电商链接**")
            if pd.notna(product_info.get('jd_link')):
                st.markdown(f"[京东链接]({product_info['jd_link']})")
            if pd.notna(product_info.get('tmall_link')):
                st.markdown(f"[天猫链接]({product_info['tmall_link']})")
            if pd.notna(product_info.get('xianyu_link')):
                st.markdown(f"[闲鱼链接]({product_info['xianyu_link']})")
            if pd.notna(product_info.get('pdd_link')):
                st.markdown(f"[拼多多链接]({product_info['pdd_link']})")
        
        with col2:
            st.write("**修改商品信息**")
            
            # 使用tabs来分离修改和删除操作
            tab1, tab2 = st.tabs(["修改信息", "删除商品"])
            
            with tab1:
                with st.form("update_inventory_form"):
                    new_product_name = st.text_input("商品名称", value=product_info['product_name'])
                    new_quantity = st.number_input("数量", min_value=1, value=product_info['quantity'])
                    new_original_value = st.number_input("原始价值", min_value=0.0, value=float(product_info['original_value']))
                    new_market_value = st.number_input("市场价值", min_value=0.0,
                                                      value=float(product_info['market_value']) if pd.notna(product_info.get('market_value')) else 0.0)
                    new_status = st.selectbox("状态", ["pending", "approved", "rejected", "sold"],
                                            index=["pending", "approved", "rejected", "sold"].index(product_info['status']))
                    new_storage_location = st.text_input("存储位置",
                                                       value=product_info.get('storage_location', '') or "")
                    
                    # 电商链接修改
                    st.write("**电商链接**")
                    new_jd_link = st.text_input("京东链接",
                                              value=product_info.get('jd_link', '') or "")
                    new_tmall_link = st.text_input("天猫链接",
                                                 value=product_info.get('tmall_link', '') or "")
                    new_xianyu_link = st.text_input("闲鱼链接",
                                                  value=product_info.get('xianyu_link', '') or "")
                    new_pdd_link = st.text_input("拼多多链接",
                                               value=product_info.get('pdd_link', '') or "")
                    
                    if st.form_submit_button("更新商品信息", type="primary"):
                        try:
                            # 清理链接数据
                            jd_link = new_jd_link.strip() if new_jd_link.strip() else None
                            tmall_link = new_tmall_link.strip() if new_tmall_link.strip() else None
                            xianyu_link = new_xianyu_link.strip() if new_xianyu_link.strip() else None
                            pdd_link = new_pdd_link.strip() if new_pdd_link.strip() else None
                            
                            success = managers['inventory'].update_inventory(
                                product_info['id'],
                                product_name=new_product_name,
                                quantity=new_quantity,
                                original_value=new_original_value,
                                market_value=new_market_value if new_market_value is not None and new_market_value > 0 else None,
                                status=new_status,
                                storage_location=new_storage_location if new_storage_location.strip() else None,
                                jd_link=jd_link,
                                tmall_link=tmall_link,
                                xianyu_link=xianyu_link,
                                pdd_link=pdd_link
                            )
                            
                            if success:
                                st.success("商品信息更新成功！")
                                st.rerun()
                            else:
                                st.error("商品信息更新失败")
                        except Exception as e:
                            st.error(f"更新失败: {str(e)}")
            
            with tab2:
                st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
                st.write(f"即将删除商品: **{product_info['product_name']}**")
                
                # 添加确认机制
                confirm_text = st.text_input("请输入商品名称以确认删除", placeholder=product_info['product_name'])
                
                col_delete1, col_delete2 = st.columns(2)
                with col_delete1:
                    if st.button("删除商品", type="secondary", disabled=(confirm_text != product_info['product_name'])):
                        try:
                            success = managers['inventory'].delete_inventory(product_info['id'])
                            if success:
                                st.success("商品删除成功！")
                                st.rerun()
                            else:
                                st.error("商品删除失败")
                        except Exception as e:
                            st.error(f"删除失败: {str(e)}")
                
                with col_delete2:
                    if st.button("清除选择", type="secondary"):
                        st.rerun()

def show_media_operations(managers):
    """显示媒体资源操作界面"""
    st.subheader("媒体资源操作")
    
    # 获取媒体资源数据
    conn = sqlite3.connect("inventory.db")
    try:
        media_df = pd.read_sql_query('SELECT * FROM media_resources ORDER BY created_at DESC', conn)
        
        if media_df.empty:
            st.info("暂无媒体资源数据")
            return
        
        selected_media = st.selectbox(
            "选择要操作的媒体资源",
            media_df['media_name'].tolist(),
            key="media_operations_select"
        )
        
        if selected_media:
            media_info = media_df[media_df['media_name'] == selected_media].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**当前媒体信息**")
                st.write(f"媒体名称: {media_info['media_name']}")
                st.write(f"媒体类型: {media_info['media_type']}")
                st.write(f"位置: {media_info['location']}")
                st.write(f"刊例价: ¥{media_info['market_price']:,.2f}")
                st.write(f"实际成本: ¥{media_info['actual_cost']:,.2f}")
                st.write(f"状态: {media_info['status']}")
                if pd.notna(media_info.get('contract_start')):
                    st.write(f"合同开始: {media_info['contract_start']}")
                if pd.notna(media_info.get('contract_end')):
                    st.write(f"合同结束: {media_info['contract_end']}")
                if pd.notna(media_info.get('contact_person')):
                    st.write(f"联系人: {media_info['contact_person']}")
                if pd.notna(media_info.get('contact_phone')):
                    st.write(f"联系电话: {media_info['contact_phone']}")
            
            with col2:
                st.write("**修改媒体信息**")
                
                # 使用tabs来分离修改和删除操作
                tab1, tab2 = st.tabs(["修改信息", "删除媒体"])
                
                with tab1:
                    with st.form("update_media_form"):
                        new_media_name = st.text_input("媒体名称", value=media_info['media_name'])
                        new_media_type = st.text_input("媒体类型", value=media_info['media_type'])
                        new_location = st.text_input("位置", value=media_info['location'])
                        new_market_price = st.number_input("刊例价", min_value=0.0, value=float(media_info['market_price']))
                        new_actual_cost = st.number_input("实际成本", min_value=0.0, value=float(media_info['actual_cost']))
                        new_status = st.selectbox("状态", ["idle", "occupied", "maintenance", "reserved"],
                                                index=["idle", "occupied", "maintenance", "reserved"].index(media_info['status']))
                        
                        # 扩展字段
                        new_media_specs = st.text_area("媒体规格", value=media_info.get('media_specs', '') or "")
                        new_audience_info = st.text_area("受众信息", value=media_info.get('audience_info', '') or "")
                        new_owner_name = st.text_input("媒体主名称", value=media_info.get('owner_name', '') or "")
                        new_contact_person = st.text_input("联系人", value=media_info.get('contact_person', '') or "")
                        new_contact_phone = st.text_input("联系电话", value=media_info.get('contact_phone', '') or "")
                        
                        if st.form_submit_button("更新媒体信息", type="primary"):
                            try:
                                success = managers['inventory'].update_media_resource(
                                    media_info['id'],
                                    media_name=new_media_name,
                                    media_type=new_media_type,
                                    location=new_location,
                                    market_price=new_market_price,
                                    actual_cost=new_actual_cost,
                                    status=new_status,
                                    media_specs=new_media_specs if new_media_specs.strip() else None,
                                    audience_info=new_audience_info if new_audience_info.strip() else None,
                                    owner_name=new_owner_name if new_owner_name.strip() else None,
                                    contact_person=new_contact_person if new_contact_person.strip() else None,
                                    contact_phone=new_contact_phone if new_contact_phone.strip() else None
                                )
                                
                                if success:
                                    st.success("媒体资源信息更新成功！")
                                    st.rerun()
                                else:
                                    st.error("媒体资源信息更新失败")
                            except Exception as e:
                                st.error(f"更新失败: {str(e)}")
                
                with tab2:
                    st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
                    st.write(f"即将删除媒体资源: **{media_info['media_name']}**")
                    
                    # 添加确认机制
                    confirm_text = st.text_input("请输入媒体名称以确认删除", placeholder=media_info['media_name'])
                    
                    col_delete1, col_delete2 = st.columns(2)
                    with col_delete1:
                        if st.button("删除媒体资源", type="secondary", disabled=(confirm_text != media_info['media_name'])):
                            try:
                                success = managers['inventory'].delete_media_resource(media_info['id'])
                                if success:
                                    st.success("媒体资源删除成功！")
                                    st.rerun()
                                else:
                                    st.error("媒体资源删除失败")
                            except Exception as e:
                                st.error(f"删除失败: {str(e)}")
                    
                    with col_delete2:
                        if st.button("清除选择", type="secondary"):
                            st.rerun()
    finally:
        conn.close()

def show_channel_operations(managers):
    """显示销售渠道操作界面"""
    st.subheader("销售渠道操作")
    
    # 获取销售渠道数据
    conn = sqlite3.connect("inventory.db")
    try:
        channel_df = pd.read_sql_query('SELECT * FROM sales_channels ORDER BY created_at DESC', conn)
        
        if channel_df.empty:
            st.info("暂无销售渠道数据")
            return
        
        selected_channel = st.selectbox(
            "选择要操作的销售渠道",
            channel_df['channel_name'].tolist(),
            key="channel_operations_select"
        )
        
        if selected_channel:
            channel_info = channel_df[channel_df['channel_name'] == selected_channel].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**当前渠道信息**")
                st.write(f"渠道名称: {channel_info['channel_name']}")
                st.write(f"渠道类型: {channel_info['channel_type']}")
                st.write(f"联系人: {channel_info.get('contact_person', '无')}")
                st.write(f"联系电话: {channel_info.get('contact_phone', '无')}")
                st.write(f"佣金比例: {channel_info['commission_rate']}%")
                st.write(f"结算方式: {channel_info.get('payment_terms', '无')}")
                if pd.notna(channel_info.get('notes')):
                    st.write(f"备注: {channel_info['notes']}")
            
            with col2:
                st.write("**修改渠道信息**")
                
                # 使用tabs来分离修改和删除操作
                tab1, tab2 = st.tabs(["修改信息", "删除渠道"])
                
                with tab1:
                    with st.form("update_channel_form"):
                        new_channel_name = st.text_input("渠道名称", value=channel_info['channel_name'])
                        new_channel_type = st.text_input("渠道类型", value=channel_info['channel_type'])
                        new_contact_person = st.text_input("联系人", value=channel_info.get('contact_person', '') or "")
                        new_contact_phone = st.text_input("联系电话", value=channel_info.get('contact_phone', '') or "")
                        new_commission_rate = st.number_input("佣金比例(%)", min_value=0.0, max_value=100.0,
                                                            value=float(channel_info['commission_rate']))
                        new_payment_terms = st.text_input("结算方式", value=channel_info.get('payment_terms', '') or "")
                        new_notes = st.text_area("备注信息", value=channel_info.get('notes', '') or "")
                        
                        if st.form_submit_button("更新渠道信息", type="primary"):
                            try:
                                success = managers['inventory'].update_sales_channel(
                                    channel_info['id'],
                                    channel_name=new_channel_name,
                                    channel_type=new_channel_type,
                                    contact_person=new_contact_person if new_contact_person.strip() else None,
                                    contact_phone=new_contact_phone if new_contact_phone.strip() else None,
                                    commission_rate=new_commission_rate,
                                    payment_terms=new_payment_terms if new_payment_terms.strip() else None,
                                    notes=new_notes if new_notes.strip() else None
                                )
                                
                                if success:
                                    st.success("销售渠道信息更新成功！")
                                    st.rerun()
                                else:
                                    st.error("销售渠道信息更新失败")
                            except Exception as e:
                                st.error(f"更新失败: {str(e)}")
                
                with tab2:
                    st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
                    st.write(f"即将删除销售渠道: **{channel_info['channel_name']}**")
                    
                    # 添加确认机制
                    confirm_text = st.text_input("请输入渠道名称以确认删除", placeholder=channel_info['channel_name'])
                    
                    col_delete1, col_delete2 = st.columns(2)
                    with col_delete1:
                        if st.button("删除销售渠道", type="secondary", disabled=(confirm_text != channel_info['channel_name'])):
                            try:
                                success = managers['inventory'].delete_sales_channel(channel_info['id'])
                                if success:
                                    st.success("销售渠道删除成功！")
                                    st.rerun()
                                else:
                                    st.error("销售渠道删除失败")
                            except Exception as e:
                                st.error(f"删除失败: {str(e)}")
                    
                    with col_delete2:
                        if st.button("清除选择", type="secondary"):
                            st.rerun()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
