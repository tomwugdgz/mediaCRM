0#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广告置换库存管理系统 - 混合解决方案
结合原有UI排版优点和修复后功能优势的最佳版本
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

# 页面配置 - 保持原有的专业配置
st.set_page_config(
    page_title="广告置换库存管理系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS - 保持原有的精美样式
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
    .operation-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.8rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .info-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background-color: #e3f2fd;
        color: #1976d2;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        margin: 0.125rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主函数 - 混合解决方案"""
    # 修复：移除缓存装饰器，直接创建管理器实例
    managers = {
        'inventory': InventoryManager(),
        'pricing': PricingCalculator(),
        'financial': FinancialCalculator()
    }
    
    # 侧边栏导航 - 保持原有的专业导航
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
    
    # 主内容区 - 保持原有的精美标题
    st.markdown('<div class="main-header">广告置换库存管理系统</div>', unsafe_allow_html=True)
    
    if selected_function == "dashboard":
        show_dashboard_hybrid(managers)
    elif selected_function == "inventory":
        show_inventory_management_hybrid(managers)
    elif selected_function == "media":
        show_media_management_hybrid(managers)
    elif selected_function == "channels":
        show_channel_management_hybrid(managers)
    elif selected_function == "pricing":
        show_pricing_analysis_hybrid(managers)
    elif selected_function == "financial":
        show_financial_analysis_hybrid(managers)
    elif selected_function == "risk":
        show_risk_management_hybrid(managers)
    elif selected_function == "reports":
        show_reports_hybrid(managers)
    elif selected_function == "settings":
        show_settings_hybrid(managers)

def show_dashboard_hybrid(managers):
    """混合版系统概览 - 结合原有图表和增强功能"""
    st.header("🏠 系统概览")
    
    # 获取统计数据 - 保持原有统计逻辑
    summary = managers['inventory'].get_inventory_summary()
    
    # 指标卡片 - 保持原有四栏布局
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
    
    # 增强：添加快速操作卡片
    st.subheader("🚀 快速操作")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("➕ 添加库存", use_container_width=True):
            st.session_state.quick_action = "add_inventory"
    
    with col2:
        if st.button("📺 添加媒体", use_container_width=True):
            st.session_state.quick_action = "add_media"
    
    with col3:
        if st.button("🛒 添加渠道", use_container_width=True):
            st.session_state.quick_action = "add_channel"
    
    with col4:
        if st.button("⚠️ 风控检查", use_container_width=True):
            st.session_state.quick_action = "risk_check"
    
    # 图表展示 - 保持原有图表配置
    col1, col2 = st.columns(2)
    
    with col1:
        # 库存状态分布 - 保持原有饼图
        inventory_stats_df = pd.DataFrame(summary['inventory_stats'])
        if not inventory_stats_df.empty:
            fig_inventory = px.pie(inventory_stats_df, values='count', names='status',
                                 title='库存状态分布')
            st.plotly_chart(fig_inventory, use_container_width=True)
    
    with col2:
        # 品类分布 - 保持原有柱状图
        category_stats_df = pd.DataFrame(summary['category_stats'])
        if not category_stats_df.empty:
            fig_category = px.bar(category_stats_df, x='category', y='count',
                                title='商品品类分布')
            st.plotly_chart(fig_category, use_container_width=True)
    
    # 最近交易概览 - 保持原有查询逻辑
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
            # 显示可用的交易记录字段 - 保持原有字段处理
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

def show_inventory_management_hybrid(managers):
    """混合版库存管理 - 改进的布局但保持熟悉感"""
    st.header("📦 库存管理")
    
    # 增强：添加快速导航标签
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📋 查看列表", use_container_width=True):
            st.session_state.inventory_tab = "list"
    with col2:
        if st.button("➕ 添加商品", use_container_width=True):
            st.session_state.inventory_tab = "add"
    with col3:
        if st.button("⚙️ 商品操作", use_container_width=True):
            st.session_state.inventory_tab = "operations"
    with col4:
        if st.button("🏢 品牌管理", use_container_width=True):
            st.session_state.inventory_tab = "brands"
    
    # 标签页 - 保持原有结构但增强功能
    tab1, tab2, tab3, tab4 = st.tabs(["库存列表", "添加库存", "商品操作", "品牌管理"])
    
    with tab1:
        show_inventory_list_hybrid(managers)
    
    with tab2:
        show_add_inventory_hybrid(managers)
    
    with tab3:
        show_inventory_operations_hybrid(managers)
    
    with tab4:
        show_brand_management_hybrid(managers)

def show_inventory_list_hybrid(managers):
    """混合版库存列表 - 增强功能但保持熟悉操作"""
    st.subheader("库存列表")
    
    # 获取库存数据 - 保持原有查询逻辑
    conn = sqlite3.connect("inventory.db")
    try:
        inventory_df = pd.read_sql_query('''
            SELECT i.*, b.brand_name, b.reputation_score
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            ORDER BY i.created_at DESC
        ''', conn)
        
        if not inventory_df.empty:
            # 增强：添加统计卡片
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("总商品数", len(inventory_df))
            with col2:
                st.metric("总库存价值", f"¥{inventory_df['original_value'].sum():,.2f}")
            with col3:
                pending_count = len(inventory_df[inventory_df['status'] == 'pending'])
                st.metric("待处理", pending_count)
            with col4:
                avg_reputation = inventory_df['reputation_score'].mean() if 'reputation_score' in inventory_df.columns else 0
                st.metric("平均信誉分", f"{avg_reputation:.1f}")
            
            # 搜索和筛选 - 保持原有布局但增强功能
            with st.expander("🔍 高级筛选", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    search_term = st.text_input("搜索商品", "", placeholder="输入商品名称关键词")
                
                with col2:
                    status_filter = st.selectbox("状态筛选", ["全部", "pending", "approved", "rejected", "sold"])
                
                with col3:
                    category_filter = st.selectbox("品类筛选", ["全部"] + list(inventory_df['category'].unique()))
            
            # 应用筛选 - 保持原有筛选逻辑
            filtered_df = inventory_df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['product_name'].str.contains(search_term, case=False)]
            if status_filter != "全部":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            if category_filter != "全部":
                filtered_df = filtered_df[filtered_df['category'] == category_filter]
            
            # 增强：添加批量操作
            if len(filtered_df) > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 导出筛选结果"):
                        filename = f"filtered_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                            filtered_df.to_excel(writer, sheet_name='筛选结果', index=False)
                        st.success(f"筛选结果已导出: {filename}")
                
                with col2:
                    if st.button("🔄 刷新数据"):
                        st.rerun()
                
                with col3:
                    selected_for_action = st.selectbox("选择商品进行快速操作", ["请选择"] + filtered_df['product_name'].tolist())
                    if selected_for_action != "请选择":
                        st.session_state.selected_product_quick = selected_for_action
            
            # 显示数据表格 - 保持原有显示方式
            st.dataframe(filtered_df)
            
            # 显示商品详情和链接 - 保持原有详细信息展示但增强交互
            if st.checkbox("显示商品详情和电商链接", value=True):
                selected_product = st.selectbox("选择商品查看详情", filtered_df['product_name'].tolist())
                if selected_product:
                    product_info = filtered_df[filtered_df['product_name'] == selected_product].iloc[0]
                    
                    # 增强：使用卡片式布局显示详情
                    with st.container():
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📋 商品信息**")
                            st.markdown(f"""
                            <div class="info-badge">商品名称: {product_info['product_name']}</div>
                            <div class="info-badge">品牌: {product_info.get('brand_name', '未知')}</div>
                            <div class="info-badge">品类: {product_info['category']}</div>
                            <div class="info-badge">数量: {product_info['quantity']}</div>
                            <div class="info-badge">原始价值: ¥{product_info['original_value']:,.2f}</div>
                            """, unsafe_allow_html=True)
                            if pd.notna(product_info.get('market_value')):
                                st.markdown(f'<div class="info-badge">市场价值: ¥{product_info["market_value"]:,.2f}</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("**🔗 电商链接**")
                            links = []
                            if pd.notna(product_info.get('jd_link')):
                                links.append(f"[京东链接]({product_info['jd_link']})")
                            if pd.notna(product_info.get('tmall_link')):
                                links.append(f"[天猫链接]({product_info['tmall_link']})")
                            if pd.notna(product_info.get('xianyu_link')):
                                links.append(f"[闲鱼链接]({product_info['xianyu_link']})")
                            if pd.notna(product_info.get('pdd_link')):
                                links.append(f"[拼多多链接]({product_info['pdd_link']})")
                            
                            if links:
                                for link in links:
                                    st.markdown(f'<div class="info-badge">{link}</div>', unsafe_allow_html=True)
                            else:
                                st.info("暂无电商链接信息")
                        
                        # 增强：快速操作按钮
                        st.write("**⚡ 快速操作**")
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        with col_btn1:
                            if st.button("✏️ 编辑商品", key=f"edit_{product_info['id']}"):
                                st.session_state.edit_product_id = product_info['id']
                        with col_btn2:
                            if st.button("📊 查看定价", key=f"price_{product_info['id']}"):
                                pricing_result = managers['pricing'].calculate_realization_value(product_info['id'])
                                st.json(pricing_result)
                        with col_btn3:
                            if st.button("⚠️ 风控检查", key=f"risk_{product_info['id']}"):
                                risk_result = managers['inventory'].check_inventory_risk(product_info['id'])
                                st.json(risk_result)
        else:
            st.info("暂无库存数据")
            if st.button("🔄 添加测试数据"):
                add_sample_data(managers)
                st.rerun()
    finally:
        conn.close()

def show_add_inventory_hybrid(managers):
    """混合版添加库存 - 保持原有表单但增强用户体验"""
    st.subheader("添加库存")
    
    # 增强：添加步骤指示器
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**步骤 1: 基本信息**")
        with col2:
            st.markdown("**步骤 2: 价值信息**")
        with col3:
            st.markdown("**步骤 3: 链接信息**")
    
    with st.form("add_inventory_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # 获取品牌列表 - 保持原有查询方式
            conn = sqlite3.connect("inventory.db")
            brands_df = pd.read_sql_query("SELECT * FROM brands", conn)
            conn.close()
            
            brand_options = {row['brand_name']: row['id'] for _, row in brands_df.iterrows()}
            
            # 增强：添加品牌选择帮助
            selected_brand = st.selectbox("选择品牌*", list(brand_options.keys()), 
                                        help="选择商品所属的品牌方")
            
            product_name = st.text_input("商品名称*", placeholder="如：可口可乐经典装", 
                                       help="请输入具体的商品名称")
            category = st.selectbox("商品品类*", ["饮料", "日化", "家电", "食品", "其他"], 
                                  help="选择商品的主要品类")
            quantity = st.number_input("数量*", min_value=1, value=100, 
                                     help="请输入库存数量")
            original_value = st.number_input("原始价值 (元)*", min_value=0.0, value=10000.0, 
                                           help="品牌方提供的账面价值")
        
        with col2:
            market_value = st.number_input("市场价值 (元)", min_value=0.0, value=None,
                                         help="基于拼多多/闲鱼价格，可选")
            expiry_date = st.date_input("保质期", value=None,
                                      help="可选，格式：YYYY-MM-DD")
            storage_location = st.text_input("存储位置", placeholder="如：仓库A", 
                                           help="商品存放的具体位置")
            
            # 电商链接输入 - 保持原有布局但增强提示
            st.write("**电商链接 (可选)**")
            jd_link = st.text_input("京东商品链接", placeholder="https://item.jd.com/xxx.html", 
                                  help="京东平台的商品链接")
            tmall_link = st.text_input("天猫商品链接", placeholder="https://detail.tmall.com/xxx.html", 
                                     help="天猫平台的商品链接")
            xianyu_link = st.text_input("闲鱼商品链接", placeholder="https://2.taobao.com/xxx", 
                                     help="闲鱼平台的商品链接")
            pdd_link = st.text_input("拼多多商品链接", placeholder="https://mobile.yangkeduo.com/xxx.html", 
                                   help="拼多多平台的商品链接")
        
        # 增强：添加表单验证提示
        st.info("💡 提示：带 * 的为必填项，请确保信息准确完整")
        
        submitted = st.form_submit_button("添加库存", type="primary")
        
        if submitted:
            try:
                # 增强：添加数据验证
                if not product_name.strip():
                    st.error("商品名称不能为空")
                    return
                
                if quantity <= 0:
                    st.error("数量必须大于0")
                    return
                
                if original_value <= 0:
                    st.error("原始价值必须大于0")
                    return
                
                brand_id = brand_options[selected_brand]
                expiry_str = expiry_date.strftime('%Y-%m-%d') if expiry_date else None
                
                inventory_id = managers['inventory'].add_inventory(
                    brand_id=brand_id,
                    product_name=product_name.strip(),
                    category=category,
                    quantity=quantity,
                    original_value=original_value,
                    market_value=market_value if market_value is not None and market_value > 0 else None,
                    expiry_date=expiry_str,
                    storage_location=storage_location.strip() if storage_location.strip() else None,
                    jd_link=jd_link.strip() if jd_link.strip() else None,
                    tmall_link=tmall_link.strip() if tmall_link.strip() else None,
                    xianyu_link=xianyu_link.strip() if xianyu_link.strip() else None,
                    pdd_link=pdd_link.strip() if pdd_link.strip() else None
                )
                
                # 增强：成功后的后续操作提示
                st.success(f"✅ 库存添加成功！ID: {inventory_id}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 继续添加"):
                        st.rerun()
                with col2:
                    if st.button("📊 立即定价"):
                        pricing_result = managers['pricing'].calculate_realization_value(inventory_id)
                        st.json(pricing_result)
                
            except Exception as e:
                st.error(f"❌ 添加失败: {str(e)}")

def show_brand_management_hybrid(managers):
    """混合版品牌管理 - 保持原有表单但增强功能"""
    st.subheader("品牌管理")
    
    # 增强：显示现有品牌列表
    with st.expander("📋 查看现有品牌", expanded=False):
        brands = managers['inventory'].get_all_brands()
        if brands:
            brands_df = pd.DataFrame(brands)
            st.dataframe(brands_df[['brand_name', 'contact_person', 'contact_phone', 'brand_type', 'reputation_score']])
        else:
            st.info("暂无品牌数据")
    
    with st.form("add_brand_form"):
        st.write("**添加新品牌**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            brand_name = st.text_input("品牌名称*", placeholder="如：可口可乐", 
                                     help="请输入品牌名称")
            contact_person = st.text_input("联系人", placeholder="如：张经理", 
                                         help="品牌方的主要联系人")
            contact_phone = st.text_input("联系电话", placeholder="如：13800138000", 
                                        help="联系人的电话号码")
        
        with col2:
            contact_email = st.text_input("邮箱", placeholder="如：zhang@coke.com", 
                                        help="联系人的电子邮箱")
            brand_type = st.selectbox("品牌类型*", ["饮料", "日化", "家电", "食品", "其他"], 
                                    help="选择品牌的主要类型")
            reputation_score = st.slider("品牌声誉评分*", 1, 10, 7, 
                                       help="品牌声誉评分，1-10分，分数越高信誉越好")
        
        # 增强：添加品牌声誉说明
        st.info("💡 品牌声誉评分说明：1-3分(较差)，4-6分(一般)，7-8分(良好)，9-10分(优秀)")
        
        submitted = st.form_submit_button("添加品牌", type="primary")
        
        if submitted:
            try:
                # 增强：数据验证
                if not brand_name.strip():
                    st.error("品牌名称不能为空")
                    return
                
                brand_id = managers['inventory'].add_brand(
                    brand_name=brand_name.strip(),
                    contact_person=contact_person.strip() if contact_person.strip() else None,
                    contact_phone=contact_phone.strip() if contact_phone.strip() else None,
                    contact_email=contact_email.strip() if contact_email.strip() else None,
                    brand_type=brand_type,
                    reputation_score=reputation_score
                )
                st.success(f"✅ 品牌添加成功！ID: {brand_id}")
                
                # 增强：添加后续操作
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 继续添加品牌"):
                        st.rerun()
                with col2:
                    st.info("💡 现在您可以为这个品牌添加库存商品了")
                
            except Exception as e:
                st.error(f"❌ 添加失败: {str(e)}")

def show_inventory_operations_hybrid(managers):
    """混合版库存操作 - 结合原有界面和修复后功能"""
    st.subheader("库存商品操作")
    
    # 获取库存数据
    inventory_data = managers['inventory'].get_all_inventory()
    
    if not inventory_data:
        st.info("暂无库存数据")
        if st.button("🔄 添加测试数据"):
            add_sample_data(managers)
            st.rerun()
        return
    
    # 转换为DataFrame以便处理
    inventory_df = pd.DataFrame(inventory_data)
    
    # 增强：添加操作统计
    col1, col2, col3 = st.columns(3)
    with col1:
        total_products = len(inventory_df)
        st.metric("总商品数", total_products)
    with col2:
        pending_products = len(inventory_df[inventory_df['status'] == 'pending'])
        st.metric("待处理", pending_products)
    with col3:
        approved_products = len(inventory_df[inventory_df['status'] == 'approved'])
        st.metric("已批准", approved_products)
    
    # 选择要操作的商品 - 保持原有选择器但增强功能
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_product = st.selectbox(
            "选择要操作的商品",
            inventory_df['product_name'].tolist(),
            key="inventory_operations_select_hybrid",
            help="选择要修改或删除的商品"
        )
    
    with col2:
        if st.button("🔄 刷新列表"):
            st.rerun()
    
    if selected_product:
        product_info = inventory_df[inventory_df['product_name'] == selected_product].iloc[0]
        
        # 增强：使用卡片式布局显示当前信息
        with st.container():
            st.markdown("### 📋 当前商品信息")
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.container():
                    st.markdown("**基本信息**")
                    st.markdown(f"""
                    <div class="info-badge">商品名称: {product_info['product_name']}</div>
                    <div class="info-badge">品牌: {product_info.get('brand_name', '未知')}</div>
                    <div class="info-badge">品类: {product_info['category']}</div>
                    <div class="info-badge">数量: {product_info['quantity']}</div>
                    <div class="info-badge">状态: {product_info['status']}</div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**价值信息**")
                    st.markdown(f"""
                    <div class="info-badge">原始价值: ¥{product_info['original_value']:,.2f}</div>
                    """, unsafe_allow_html=True)
                    if pd.notna(product_info.get('market_value')):
                        st.markdown(f'<div class="info-badge">市场价值: ¥{product_info["market_value"]:,.2f}</div>', unsafe_allow_html=True)
            
            with col2:
                with st.container():
                    st.markdown("**存储信息**")
                    st.markdown(f"""
                    <div class="info-badge">存储位置: {product_info.get('storage_location', '未指定')}</div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**电商链接**")
                    links = []
                    if pd.notna(product_info.get('jd_link')):
                        links.append(f"[京东链接]({product_info['jd_link']})")
                    if pd.notna(product_info.get('tmall_link')):
                        links.append(f"[天猫链接]({product_info['tmall_link']})")
                    if pd.notna(product_info.get('xianyu_link')):
                        links.append(f"[闲鱼链接]({product_info['xianyu_link']})")
                    if pd.notna(product_info.get('pdd_link')):
                        links.append(f"[拼多多链接]({product_info['pdd_link']})")
                    
                    if links:
                        for link in links:
                            st.markdown(f'<div class="info-badge">{link}</div>', unsafe_allow_html=True)
                    else:
                        st.info("暂无电商链接信息")
        
        # 使用tabs来分离修改和删除操作 - 保持原有标签页结构
        tab1, tab2 = st.tabs(["✏️ 修改信息", "🗑️ 删除商品"])
        
        with tab1:
            # 修复：使用独立的表单，避免嵌套表单问题
            with st.form("update_inventory_form_hybrid"):
                st.markdown("### 📝 修改商品信息")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_product_name = st.text_input("商品名称*", value=product_info['product_name'], 
                                                   help="商品的名称")
                    new_quantity = st.number_input("数量*", min_value=1, value=product_info['quantity'], 
                                                 help="库存数量")
                    new_original_value = st.number_input("原始价值*", min_value=0.0, value=float(product_info['original_value']), 
                                                       help="品牌方提供的账面价值")
                    new_market_value = st.number_input("市场价值", min_value=0.0, 
                                                     value=float(product_info['market_value']) if pd.notna(product_info.get('market_value')) else 0.0,
                                                     help="基于市场价格的估值")
                    new_status = st.selectbox("状态*", ["pending", "approved", "rejected", "sold"],
                                            index=["pending", "approved", "rejected", "sold"].index(product_info['status']),
                                            help="商品的当前状态")
                
                with col2:
                    new_storage_location = st.text_input("存储位置", 
                                                       value=product_info.get('storage_location', '') or "",
                                                       help="商品存放的具体位置")
                    
                    # 电商链接修改 - 保持原有输入框布局
                    st.markdown("**电商链接 (可选)**")
                    new_jd_link = st.text_input("京东链接", 
                                              value=product_info.get('jd_link', '') or "",
                                              help="京东平台的商品链接")
                    new_tmall_link = st.text_input("天猫链接", 
                                                 value=product_info.get('tmall_link', '') or "",
                                                 help="天猫平台的商品链接")
                    new_xianyu_link = st.text_input("闲鱼链接", 
                                                  value=product_info.get('xianyu_link', '') or "",
                                                  help="闲鱼平台的商品链接")
                    new_pdd_link = st.text_input("拼多多链接", 
                                               value=product_info.get('pdd_link', '') or "",
                                               help="拼多多平台的商品链接")
                
                # 增强：添加修改提示
                st.info("💡 修改提示：确保信息准确，修改后将自动更新数据库")
                
                if st.form_submit_button("💾 更新商品信息", type="primary"):
                    try:
                        # 清理链接数据
                        jd_link = new_jd_link.strip() if new_jd_link.strip() else None
                        tmall_link = new_tmall_link.strip() if new_tmall_link.strip() else None
                        xianyu_link = new_xianyu_link.strip() if new_xianyu_link.strip() else None
                        pdd_link = new_pdd_link.strip() if new_pdd_link.strip() else None
                        
                        # 修复：直接使用管理器的更新功能
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
                            st.success("✅ 商品信息更新成功！")
                            st.rerun()
                        else:
                            st.error("❌ 商品信息更新失败")
                    except Exception as e:
                        st.error(f"❌ 更新失败: {str(e)}")
        
        with tab2:
            # 增强：更友好的删除界面
            st.markdown("### ⚠️ 删除商品")
            
            warning_container = st.container()
            with warning_container:
                st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
                st.markdown(f"**即将删除商品:** `{product_info['product_name']}`")
                st.markdown(f"**商品ID:** `{product_info['id']}`")
                
                # 显示将要删除的商品信息摘要
                with st.expander("查看商品详细信息"):
                    st.json({
                        "商品名称": product_info['product_name'],
                        "品牌": product_info.get('brand_name', '未知'),
                        "品类": product_info['category'],
                        "数量": product_info['quantity'],
                        "价值": f"¥{product_info['original_value']:,.2f}",
                        "状态": product_info['status']
                    })
            
            # 修复：改进确认机制，但保持原有视觉样式
            st.markdown("**请输入商品名称以确认删除:**")
            confirm_text = st.text_input("", placeholder=product_info['product_name'], 
                                         help="输入完整的商品名称以确认删除操作")
            
            col_delete1, col_delete2 = st.columns(2)
            with col_delete1:
                # 修复：使用正确的按钮状态控制
                if st.button("🗑️ 确认删除", type="secondary", 
                           disabled=(confirm_text != product_info['product_name']),
                           help="确认删除此商品"):
                    try:
                        # 修复：直接使用管理器的删除功能
                        success = managers['inventory'].delete_inventory(product_info['id'])
                        if success:
                            st.success("✅ 商品删除成功！")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ 商品删除失败")
                    except Exception as e:
                        st.error(f"❌ 删除失败: {str(e)}")
            
            with col_delete2:
                if st.button("❌ 取消操作", type="secondary", help="取消删除操作"):
                    st.info("已取消删除操作")
                    st.rerun()

def show_media_management_hybrid(managers):
    """混合版媒体管理 - 结合原有界面和修复后功能"""
    st.header("📺 媒体管理")
    
    # 增强：添加快速导航
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📋 媒体列表", use_container_width=True):
            st.session_state.media_tab = "list"
    with col2:
        if st.button("➕ 添加媒体", use_container_width=True):
            st.session_state.media_tab = "add"
    with col3:
        if st.button("📊 媒体分析", use_container_width=True):
            st.session_state.media_tab = "analysis"
    with col4:
        if st.button("⚙️ 媒体操作", use_container_width=True):
            st.session_state.media_tab = "operations"
    
    tab1, tab2, tab3, tab4 = st.tabs(["媒体列表", "添加媒体", "媒体分析", "媒体操作"])
    
    with tab1:
        show_media_list_hybrid(managers)
    
    with tab2:
        show_add_media_hybrid(managers)
    
    with tab3:
        show_media_analysis_hybrid(managers)
    
    with tab4:
        show_media_operations_hybrid(managers)

def show_media_list_hybrid(managers):
    """混合版媒体列表 - 增强功能但保持熟悉操作"""
    st.subheader("媒体资源列表")
    
    conn = sqlite3.connect("inventory.db")
    try:
        media_df = pd.read_sql_query('''
            SELECT * FROM media_resources
            ORDER BY created_at DESC
        ''', conn)
        
        if not media_df.empty:
            # 增强：添加统计信息
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_media = len(media_df)
                st.metric("总媒体数", total_media)
            with col2:
                idle_media = len(media_df[media_df['status'] == 'idle'])
                st.metric("空闲媒体", idle_media)
            with col3:
                avg_market_price = media_df['market_price'].mean()
                st.metric("平均刊例价", f"¥{avg_market_price:,.0f}")
            with col4:
                avg_discount = media_df['discount_rate'].mean()
                st.metric("平均折扣率", f"{avg_discount:.1f}%")
            
            # 搜索和筛选 - 保持原有布局但增强功能
            with st.expander("🔍 高级筛选", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    search_term = st.text_input("搜索媒体", "", placeholder="输入媒体名称关键词")
                
                with col2:
                    media_type_filter = st.selectbox("媒体类型筛选", ["全部"] + list(media_df['media_type'].unique()))
                
                with col3:
                    status_filter = st.selectbox("状态筛选", ["全部", "idle", "occupied", "maintenance", "reserved"])
            
            # 应用筛选 - 保持原有筛选逻辑
            filtered_df = media_df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['media_name'].str.contains(search_term, case=False)]
            if media_type_filter != "全部":
                filtered_df = filtered_df[filtered_df['media_type'] == media_type_filter]
            if status_filter != "全部":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            # 增强：添加批量操作
            if len(filtered_df) > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 导出筛选结果"):
                        filename = f"filtered_media_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                            filtered_df.to_excel(writer, sheet_name='筛选结果', index=False)
                        st.success(f"筛选结果已导出: {filename}")
                
                with col2:
                    if st.button("🔄 刷新数据"):
                        st.rerun()
                
                with col3:
                    selected_for_action = st.selectbox("选择媒体进行快速操作", ["请选择"] + filtered_df['media_name'].tolist())
                    if selected_for_action != "请选择":
                        st.session_state.selected_media_quick = selected_for_action
            
            # 显示数据表格 - 保持原有显示方式
            st.dataframe(filtered_df)
            
            # 增强：快速预览和操作
            if st.checkbox("显示媒体详情和操作", value=True):
                selected_media = st.selectbox("选择媒体查看详情", filtered_df['media_name'].tolist())
                if selected_media:
                    media_info = filtered_df[filtered_df['media_name'] == selected_media].iloc[0]
                    
                    with st.container():
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📺 媒体基本信息**")
                            st.markdown(f"""
                            <div class="info-badge">媒体名称: {media_info['media_name']}</div>
                            <div class="info-badge">媒体类型: {media_info['media_type']}</div>
                            <div class="info-badge">位置: {media_info['location']}</div>
                            <div class="info-badge">状态: {media_info['status']}</div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("**💰 价格信息**")
                            st.markdown(f"""
                            <div class="info-badge">刊例价: ¥{media_info['market_price']:,.2f}</div>
                            <div class="info-badge">实际成本: ¥{media_info['actual_cost']:,.2f}</div>
                            <div class="info-badge">折扣率: {media_info['discount_rate']:.1f}%</div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("**📋 详细信息**")
                            if pd.notna(media_info.get('media_specs')):
                                st.markdown(f'<div class="info-badge">规格: {media_info["media_specs"]}</div>', unsafe_allow_html=True)
                            if pd.notna(media_info.get('audience_info')):
                                st.markdown(f'<div class="info-badge">受众: {media_info["audience_info"]}</div>', unsafe_allow_html=True)
                            if pd.notna(media_info.get('contact_person')):
                                st.markdown(f'<div class="info-badge">联系人: {media_info["contact_person"]}</div>', unsafe_allow_html=True)
                            if pd.notna(media_info.get('contact_phone')):
                                st.markdown(f'<div class="info-badge">电话: {media_info["contact_phone"]}</div>', unsafe_allow_html=True)
                        
                        # 快速操作按钮
                        st.write("**⚡ 快速操作**")
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        with col_btn1:
                            if st.button("✏️ 编辑媒体", key=f"edit_media_{media_info['id']}"):
                                st.session_state.edit_media_id = media_info['id']
                        with col_btn2:
                            if st.button("📊 查看合同", key=f"contract_{media_info['id']}"):
                                contract_info = {
                                    "合同开始": str(media_info.get('contract_start', '未设置')),
                                    "合同结束": str(media_info.get('contract_end', '未设置')),
                                    "剩余天数": "计算中..." if media_info.get('contract_end') else "无到期时间"
                                }
                                st.json(contract_info)
                        with col_btn3:
                            if st.button("📞 联系信息", key=f"contact_{media_info['id']}"):
                                contact_info = {
                                    "媒体主": media_info.get('owner_name', '未设置'),
                                    "联系人": media_info.get('contact_person', '未设置'),
                                    "电话": media_info.get('contact_phone', '未设置')
                                }
                                st.json(contact_info)
        else:
            st.info("暂无媒体资源数据")
            if st.button("🔄 添加测试媒体"):
                add_sample_media(managers)
                st.rerun()
    finally:
        conn.close()

def show_add_media_hybrid(managers):
    """混合版添加媒体 - 保持原有表单但增强用户体验"""
    st.subheader("添加媒体资源")
    
    # 增强：添加步骤指示器
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**步骤 1: 基本信息**")
        with col2:
            st.markdown("**步骤 2: 价格信息**")
        with col3:
            st.markdown("**步骤 3: 联系信息**")
    
    with st.form("add_media_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            media_name = st.text_input("媒体名称*", placeholder="如：朝阳小区门禁广告", 
                                     help="请输入媒体资源的名称")
            media_type = st.selectbox("媒体类型*", ["社区门禁", "写字楼电梯", "户外大屏", "公交站牌", "地铁广告", "商场广告", "其他"], 
                                    help="选择媒体的类型")
            media_form = st.selectbox("媒体形式*", ["静态海报", "动态LED", "液晶屏", "灯箱", "三面翻", "其他"], 
                                    help="选择媒体的表现形式")
            location = st.text_input("具体位置*", placeholder="如：北京市朝阳区XX小区", 
                                   help="媒体的详细位置信息")
            market_price = st.number_input("刊例价格 (元)*", min_value=0.0, value=5000.0, 
                                         help="媒体的官方刊例价格")
            discount_rate = st.number_input("折扣率 (%)*", min_value=0.0, max_value=100.0, value=80.0, 
                                            help="实际执行的折扣比例")
        
        with col2:
            actual_cost = st.number_input("实际成本 (元)", min_value=0.0, value=None,
                                         help="留空将自动计算：刊例价 × 折扣率")
            media_specs = st.text_area("媒体规格", placeholder="如：120cm×80cm，高清LED屏", 
                                     help="媒体的技术规格和参数")
            audience_info = st.text_area("受众信息", placeholder="如：日均人流量5000+，主要受众为白领群体", 
                                       help="媒体的受众群体和流量信息")
            owner_name = st.text_input("媒体主名称", placeholder="如：北京XX广告有限公司", 
                                     help="媒体资源的所有者名称")
            contact_person = st.text_input("联系人", placeholder="如：张经理", 
                                         help="媒体主的联系人")
            contact_phone = st.text_input("联系电话", placeholder="如：13800138000", 
                                        help="联系人的电话号码")
            contract_start = st.date_input("合同开始日期", value=None, 
                                         help="媒体资源合同的开始日期")
            contract_end = st.date_input("合同结束日期", value=None, 
                                       help="媒体资源合同的结束日期")
        
        # 增强：添加成本计算提示
        if actual_cost is None or actual_cost == 0:
            calculated_cost = market_price * discount_rate / 100
            st.info(f"💡 系统将自动计算实际成本为: ¥{calculated_cost:,.2f}")
        
        # 增强：添加表单验证提示
        st.info("💡 提示：带 * 的为必填项，请确保信息准确完整")
        
        submitted = st.form_submit_button("添加媒体", type="primary")
        
        if submitted:
            try:
                # 增强：数据验证
                if not media_name.strip():
                    st.error("媒体名称不能为空")
                    return
                
                if market_price <= 0:
                    st.error("刊例价格必须大于0")
                    return
                
                if discount_rate < 0 or discount_rate > 100:
                    st.error("折扣率必须在0-100之间")
                    return
                
                # 计算实际成本
                if actual_cost is None or actual_cost == 0:
                    actual_cost = market_price * discount_rate / 100
                
                # 转换日期格式
                start_str = contract_start.strftime('%Y-%m-%d') if contract_start else None
                end_str = contract_end.strftime('%Y-%m-%d') if contract_end else None
                
                # 添加媒体资源
                media_id = managers['inventory'].add_media_resource(
                    media_name=media_name.strip(),
                    media_type=media_type,
                    media_form=media_form,
                    location=location.strip(),
                    market_price=market_price,
                    discount_rate=discount_rate,
                    actual_cost=actual_cost,
                    media_specs=media_specs.strip() if media_specs.strip() else None,
                    audience_info=audience_info.strip() if audience_info.strip() else None,
                    owner_name=owner_name.strip() if owner_name.strip() else None,
                    contact_person=contact_person.strip() if contact_person.strip() else None,
                    contact_phone=contact_phone.strip() if contact_phone.strip() else None,
                    contract_start=start_str,
                    contract_end=end_str
                )
                
                st.success(f"✅ 媒体资源添加成功！ID: {media_id}")
                
                # 增强：成功后的后续操作
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 继续添加媒体"):
                        st.rerun()
                with col2:
                    st.info("💡 现在您可以为这个媒体资源设置定价或使用它进行交易")
                
            except Exception as e:
                st.error(f"❌ 添加失败: {str(e)}")

def show_media_analysis_hybrid(managers):
    """混合版媒体分析 - 保持原有图表但增强功能"""
    st.subheader("媒体资源分析")
    
    conn = sqlite3.connect("inventory.db")
    try:
        media_df = pd.read_sql_query('SELECT * FROM media_resources', conn)
        
        if not media_df.empty:
            # 媒体类型分布 - 保持原有图表配置
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
            
            # 价格分析 - 保持原有指标卡片布局
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
            
            # 增强：添加价格趋势分析
            if len(media_df) > 5:
                st.subheader("价格分布分析")
                col1, col2 = st.columns(2)
                
                with col1:
                    # 刊例价分布
                    fig_price_dist = px.histogram(media_df, x='market_price', nbins=20,
                                                title='刊例价格分布')
                    st.plotly_chart(fig_price_dist, use_container_width=True)
                
                with col2:
                    # 折扣率vs实际成本散点图
                    fig_scatter = px.scatter(media_df, x='discount_rate', y='actual_cost',
                                           color='media_type', size='market_price',
                                           title='折扣率与实际成本关系')
                    st.plotly_chart(fig_scatter, use_container_width=True)
            
            # 合同到期提醒 - 保持原有提醒样式
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
                                '剩余天数': days_until_end,
                                '联系人': row.get('contact_person', '无'),
                                '电话': row.get('contact_phone', '无')
                            })
                    except:
                        continue
            
            if upcoming_end:
                reminder_df = pd.DataFrame(upcoming_end)
                st.dataframe(reminder_df)
                st.warning(f"⚠️ 有 {len(upcoming_end)} 个媒体资源即将在30天内到期")
                
                # 增强：添加导出到期提醒
                if st.button("📊 导出到期提醒"):
                    filename = f"contract_reminder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                        reminder_df.to_excel(writer, sheet_name='到期提醒', index=False)
                    st.success(f"到期提醒已导出: {filename}")
            else:
                st.info("暂无即将到期的媒体资源")
                
        else:
            st.info("暂无媒体资源数据")
            if st.button("🔄 添加测试媒体"):
                add_sample_media(managers)
                st.rerun()
    finally:
        conn.close()

def show_media_operations_hybrid(managers):
    """混合版媒体资源操作 - 使用修复后的功能逻辑"""
    st.subheader("媒体资源操作")
    
    # 获取媒体资源数据
    conn = sqlite3.connect("inventory.db")
    try:
        media_df = pd.read_sql_query('SELECT * FROM media_resources ORDER BY created_at DESC', conn)
        
        if media_df.empty:
            st.info("暂无媒体资源数据")
            if st.button("🔄 添加测试媒体"):
                add_sample_media(managers)
                st.rerun()
            return
        
        # 增强：添加操作统计
        col1, col2, col3 = st.columns(3)
        with col1:
            total_media = len(media_df)
            st.metric("总媒体数", total_media)
        with col2:
            editable_media = len(media_df[media_df['status'] == 'idle'])
            st.metric("可编辑媒体", editable_media)
        with col3:
            active_media = len(media_df[media_df['status'] == 'occupied'])
            st.metric("使用中媒体", active_media)
        
        # 选择要操作的媒体资源 - 增强选择功能
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_media = st.selectbox(
                "选择要操作的媒体资源",
                media_df['media_name'].tolist(),
                key="media_operations_select_hybrid",
                help="选择要修改或删除的媒体资源"
            )
        
        with col2:
            if st.button("🔄 刷新列表"):
                st.rerun()
        
        if selected_media:
            media_info = media_df[media_df['media_name'] == selected_media].iloc[0]
            
            # 增强：使用卡片式布局显示当前信息
            with st.container():
                st.markdown("### 📺 当前媒体信息")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**基本信息**")
                    st.markdown(f"""
                    <div class="info-badge">媒体名称: {media_info['media_name']}</div>
                    <div class="info-badge">媒体类型: {media_info['media_type']}</div>
                    <div class="info-badge">位置: {media_info['location']}</div>
                    <div class="info-badge">状态: {media_info['status']}</div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("**价格信息**")
                    st.markdown(f"""
                    <div class="info-badge">刊例价: ¥{media_info['market_price']:,.2f}</div>
                    <div class="info-badge">实际成本: ¥{media_info['actual_cost']:,.2f}</div>
                    <div class="info-badge">折扣率: {media_info['discount_rate']:.1f}%</div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**详细信息**")
                    if pd.notna(media_info.get('media_specs')):
                        st.markdown(f'<div class="info-badge">规格: {media_info["media_specs"]}</div>', unsafe_allow_html=True)
                    if pd.notna(media_info.get('audience_info')):
                        st.markdown(f'<div class="info-badge">受众: {media_info["audience_info"]}</div>', unsafe_allow_html=True)
                    if pd.notna(media_info.get('owner_name')):
                        st.markdown(f'<div class="info-badge">媒体主: {media_info["owner_name"]}</div>', unsafe_allow_html=True)
                    if pd.notna(media_info.get('contact_person')):
                        st.markdown(f'<div class="info-badge">联系人: {media_info["contact_person"]}</div>', unsafe_allow_html=True)
                    if pd.notna(media_info.get('contact_phone')):
                        st.markdown(f'<div class="info-badge">电话: {media_info["contact_phone"]}</div>', unsafe_allow_html=True)
                    if pd.notna(media_info.get('contract_start')):
                        st.markdown(f'<div class="info-badge">合同开始: {media_info["contract_start"]}</div>', unsafe_allow_html=True)
                    if pd.notna(media_info.get('contract_end')):
                        st.markdown(f'<div class="info-badge">合同结束: {media_info["contract_end"]}</div>', unsafe_allow_html=True)
            
            # 使用tabs来分离修改和删除操作 - 保持原有标签页结构
            tab1, tab2 = st.tabs(["✏️ 修改信息", "🗑️ 删除媒体"])
            
            with tab1:
                # 修复：使用独立的表单，避免嵌套表单问题
                with st.form("update_media_form_hybrid"):
                    st.markdown("### 📝 修改媒体信息")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_media_name = st.text_input("媒体名称*", value=media_info['media_name'], 
                                                     help="媒体资源的名称")
                        new_media_type = st.text_input("媒体类型*", value=media_info['media_type'], 
                                                     help="媒体的类型分类")
                        new_location = st.text_input("位置*", value=media_info['location'], 
                                                   help="媒体的具体位置")
                        new_market_price = st.number_input("刊例价*", min_value=0.0, value=float(media_info['market_price']), 
                                                         help="媒体的官方刊例价格")
                        new_actual_cost = st.number_input("实际成本*", min_value=0.0, value=float(media_info['actual_cost']), 
                                                        help="媒体的实际成本价格")
                        new_status = st.selectbox("状态*", ["idle", "occupied", "maintenance", "reserved"],
                                                index=["idle", "occupied", "maintenance", "reserved"].index(media_info['status']),
                                                help="媒体的当前状态")
                    
                    with col2:
                        # 扩展字段
                        new_media_specs = st.text_area("媒体规格", value=media_info.get('media_specs', '') or "", 
                                                     help="媒体的技术规格和参数")
                        new_audience_info = st.text_area("受众信息", value=media_info.get('audience_info', '') or "", 
                                                       help="媒体的受众群体和流量信息")
                        new_owner_name = st.text_input("媒体主名称", value=media_info.get('owner_name', '') or "", 
                                                     help="媒体资源的所有者名称")
                        new_contact_person = st.text_input("联系人", value=media_info.get('contact_person', '') or "", 
                                                         help="媒体主的联系人")
                        new_contact_phone = st.text_input("联系电话", value=media_info.get('contact_phone', '') or "", 
                                                        help="联系人的电话号码")
                    
                    # 增强：添加修改提示
                    st.info("💡 修改提示：确保信息准确，修改后将自动更新数据库")
                    
                    if st.form_submit_button("💾 更新媒体信息", type="primary"):
                        try:
                            # 修复：直接使用管理器的更新功能
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
                                st.success("✅ 媒体资源信息更新成功！")
                                st.rerun()
                            else:
                                st.error("❌ 媒体资源信息更新失败")
                        except Exception as e:
                            st.error(f"❌ 更新失败: {str(e)}")
            
            with tab2:
                # 增强：更友好的删除界面
                st.markdown("### ⚠️ 删除媒体资源")
                
                warning_container = st.container()
                with warning_container:
                    st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
                    st.markdown(f"**即将删除媒体资源:** `{media_info['media_name']}`")
                    st.markdown(f"**媒体ID:** `{media_info['id']}`")
                    
                    # 显示将要删除的媒体信息摘要
                    with st.expander("查看媒体详细信息"):
                        st.json({
                            "媒体名称": media_info['media_name'],
                            "媒体类型": media_info['media_type'],
                            "位置": media_info['location'],
                            "刊例价": f"¥{media_info['market_price']:,.2f}",
                            "状态": media_info['status'],
                            "联系人": media_info.get('contact_person', '无'),
                            "电话": media_info.get('contact_phone', '无')
                        })
                
                # 修复：改进确认机制，但保持原有视觉样式
                st.markdown("**请输入媒体名称以确认删除:**")
                confirm_text = st.text_input("", placeholder=media_info['media_name'], 
                                             help="输入完整的媒体名称以确认删除操作")
                
                col_delete1, col_delete2 = st.columns(2)
                with col_delete1:
                    # 修复：使用正确的按钮状态控制
                    if st.button("🗑️ 确认删除", type="secondary", 
                               disabled=(confirm_text != media_info['media_name']),
                               help="确认删除此媒体资源"):
                        try:
                            # 修复：直接使用管理器的删除功能
                            success = managers['inventory'].delete_media_resource(media_info['id'])
                            if success:
                                st.success("✅ 媒体资源删除成功！")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ 媒体资源删除失败")
                        except Exception as e:
                            st.error(f"❌ 删除失败: {str(e)}")
                
                with col_delete2:
                    if st.button("❌ 取消操作", type="secondary", help="取消删除操作"):
                        st.info("已取消删除操作")
                        st.rerun()
    finally:
        conn.close()

def show_channel_management_hybrid(managers):
    """混合版渠道管理 - 结合原有界面和修复后功能"""
    st.header("🛒 渠道管理")
    
    # 增强：添加快速导航
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📋 渠道列表", use_container_width=True):
            st.session_state.channel_tab = "list"
    with col2:
        if st.button("➕ 添加渠道", use_container_width=True):
            st.session_state.channel_tab = "add"
    with col3:
        if st.button("📊 渠道分析", use_container_width=True):
            st.session_state.channel_tab = "analysis"
    with col4:
        if st.button("⚙️ 渠道操作", use_container_width=True):
            st.session_state.channel_tab = "operations"
    
    tab1, tab2, tab3, tab4 = st.tabs(["渠道列表", "添加渠道", "渠道分析", "渠道操作"])
    
    with tab1:
        show_channel_list_hybrid(managers)
    
    with tab2:
        show_add_channel_hybrid(managers)
    
    with tab3:
        show_channel_analysis_hybrid(managers)
    
    with tab4:
        show_channel_operations_hybrid(managers)

def show_channel_list_hybrid(managers):
    """混合版渠道列表 - 增强功能但保持熟悉操作"""
    st.subheader("销售渠道列表")
    
    conn = sqlite3.connect("inventory.db")
    try:
        channels_df = pd.read_sql_query('''
            SELECT * FROM sales_channels
            ORDER BY created_at DESC
        ''', conn)
        
        if not channels_df.empty:
            # 增强：添加统计信息
            col1, col2, col3 = st.columns(3)
            with col1:
                total_channels = len(channels_df)
                st.metric("总渠道数", total_channels)
            with col2:
                s_level_channels = len(channels_df[channels_df['channel_type'] == 'S级(团长)'])
                st.metric("S级渠道", s_level_channels)
            with col3:
                avg_commission = channels_df['commission_rate'].mean()
                st.metric("平均佣金率", f"{avg_commission:.1f}%")
            
            # 搜索和筛选 - 保持原有布局但增强功能
            with st.expander("🔍 高级筛选", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    search_term = st.text_input("搜索渠道", "", placeholder="输入渠道名称关键词")
                
                with col2:
                    channel_type_filter = st.selectbox("渠道类型筛选", ["全部"] + list(channels_df['channel_type'].unique()))
            
            # 应用筛选 - 保持原有筛选逻辑
            filtered_df = channels_df.copy()
            if search_term:
                filtered_df = filtered_df[filtered_df['channel_name'].str.contains(search_term, case=False)]
            if channel_type_filter != "全部":
                filtered_df = filtered_df[filtered_df['channel_type'] == channel_type_filter]
            
            # 增强：添加批量操作
            if len(filtered_df) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 导出筛选结果"):
                        filename = f"filtered_channels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                            filtered_df.to_excel(writer, sheet_name='筛选结果', index=False)
                        st.success(f"筛选结果已导出: {filename}")
                
                with col2:
                    if st.button("🔄 刷新数据"):
                        st.rerun()
            
            # 显示数据表格 - 保持原有显示方式
            st.dataframe(filtered_df)
            
            # 增强：快速预览和操作
            if st.checkbox("显示渠道详情和操作", value=True):
                selected_channel = st.selectbox("选择渠道查看详情", filtered_df['channel_name'].tolist())
                if selected_channel:
                    channel_info = filtered_df[filtered_df['channel_name'] == selected_channel].iloc[0]
                    
                    with st.container():
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**📋 渠道基本信息**")
                            st.markdown(f"""
                            <div class="info-badge">渠道名称: {channel_info['channel_name']}</div>
                            <div class="info-badge">渠道类型: {channel_info['channel_type']}</div>
                            <div class="info-badge">佣金比例: {channel_info['commission_rate']}%</div>
                            <div class="info-badge">结算方式: {channel_info.get('payment_terms', '未设置')}</div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("**📞 联系信息**")
                            st.markdown(f"""
                            <div class="info-badge">联系人: {channel_info.get('contact_person', '未设置')}</div>
                            <div class="info-badge">电话: {channel_info.get('contact_phone', '未设置')}</div>
                            """, unsafe_allow_html=True)
                            if pd.notna(channel_info.get('notes')):
                                st.markdown(f'<div class="info-badge">备注: {channel_info["notes"]}</div>', unsafe_allow_html=True)
                        
                        # 快速操作按钮
                        st.write("**⚡ 快速操作**")
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("✏️ 编辑渠道", key=f"edit_channel_{channel_info['id']}"):
                                st.session_state.edit_channel_id = channel_info['id']
                        with col_btn2:
                            if st.button("📊 查看交易", key=f"transactions_{channel_info['id']}"):
                                st.info("交易记录功能开发中...")
        else:
            st.info("暂无销售渠道数据")
            if st.button("🔄 添加测试渠道"):
                add_sample_channel(managers)
                st.rerun()
    finally:
        conn.close()

def show_add_channel_hybrid(managers):
    """混合版添加渠道 - 保持原有表单但增强用户体验"""
    st.subheader("添加销售渠道")
    
    # 增强：显示现有渠道类型分布
    with st.expander("📊 查看现有渠道分布", expanded=False):
        conn = sqlite3.connect("inventory.db")
        try:
            existing_channels = pd.read_sql_query("SELECT channel_type, COUNT(*) as count FROM sales_channels GROUP BY channel_type", conn)
            if not existing_channels.empty:
                st.dataframe(existing_channels)
                fig = px.pie(existing_channels, values='count', names='channel_type', title='现有渠道类型分布')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无现有渠道数据")
        finally:
            conn.close()
    
    with st.form("add_channel_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            channel_name = st.text_input("渠道名称*", placeholder="如：王团长团购", 
                                       help="销售渠道的名称")
            channel_type = st.selectbox("渠道类型*", ["S级(团长)", "A级(批发市场)", "B级(零售商)", "C级(个体户)", "电商平台", "其他"], 
                                      help="选择渠道的类型等级")
            contact_person = st.text_input("联系人", placeholder="如：王团长", 
                                         help="渠道的主要联系人")
            contact_phone = st.text_input("联系电话", placeholder="如：13800138000", 
                                        help="联系人的电话号码")
        
        with col2:
            commission_rate = st.number_input("佣金比例 (%)", min_value=0.0, max_value=100.0, value=5.0, 
                                            help="给渠道的佣金比例，0-100%")
            payment_terms = st.selectbox("结算方式*", ["现结", "周结", "月结", "季度结", "批量结算", "其他"], 
                                       help="与渠道的结算方式")
            notes = st.text_area("备注信息", placeholder="如：主要销售日化用品，信誉良好", 
                               help="关于此渠道的其他重要信息")
        
        # 增强：添加渠道信息说明
        st.info("💡 渠道类型说明：S级(顶级团长) > A级(批发市场) > B级(零售商) > C级(个体户)")
        
        submitted = st.form_submit_button("添加渠道", type="primary")
        
        if submitted:
            try:
                # 增强：数据验证
                if not channel_name.strip():
                    st.error("渠道名称不能为空")
                    return
                
                if commission_rate < 0 or commission_rate > 100:
                    st.error("佣金比例必须在0-100之间")
                    return
                
                # 添加销售渠道 - 使用原有添加逻辑
                channel_id = managers['inventory'].add_sales_channel(
                    channel_name=channel_name.strip(),
                    channel_type=channel_type,
                    contact_person=contact_person.strip() if contact_person.strip() else None,
                    contact_phone=contact_phone.strip() if contact_phone.strip() else None,
                    commission_rate=commission_rate,
                    payment_terms=payment_terms,
                    notes=notes.strip() if notes.strip() else None
                )
                
                st.success(f"✅ 销售渠道添加成功！ID: {channel_id}")
                
                # 增强：成功后的后续操作
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 继续添加渠道"):
                        st.rerun()
                with col2:
                    st.info("💡 现在您可以使用这个渠道进行库存销售了")
                
            except Exception as e:
                st.error(f"❌ 添加失败: {str(e)}")

def show_channel_analysis_hybrid(managers):
    """混合版渠道分析 - 保持原有图表但增强功能"""
    st.subheader("销售渠道分析")
    
    conn = sqlite3.connect("inventory.db")
    try:
        channels_df = pd.read_sql_query('SELECT * FROM sales_channels', conn)
        
        if not channels_df.empty:
            # 渠道类型分布 - 保持原有图表配置
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
            
            # 统计信息 - 保持原有指标卡片布局
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
            
            # 增强：添加佣金分布分析
            if len(channels_df) > 5:
                st.subheader("佣金分布分析")
                col1, col2 = st.columns(2)
                
                with col1:
                    # 佣金率分布直方图
                    fig_commission_dist = px.histogram(channels_df, x='commission_rate', nbins=20,
                                                     title='佣金率分布')
                    st.plotly_chart(fig_commission_dist, use_container_width=True)
                
                with col2:
                    # 渠道类型vs佣金率箱线图
                    fig_box = px.box(channels_df, x='channel_type', y='commission_rate',
                                   title='各类型渠道佣金率分布')
                    st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("暂无销售渠道数据")
            if st.button("🔄 添加测试渠道"):
                add_sample_channel(managers)
                st.rerun()
    finally:
        conn.close()

def show_channel_operations_hybrid(managers):
    """混合版销售渠道操作 - 使用修复后的功能逻辑"""
    st.subheader("销售渠道操作")
    
    # 获取销售渠道数据
    conn = sqlite3.connect("inventory.db")
    try:
        channel_df = pd.read_sql_query('SELECT * FROM sales_channels ORDER BY created_at DESC', conn)
        
        if channel_df.empty:
            st.info("暂无销售渠道数据")
            if st.button("🔄 添加测试渠道"):
                add_sample_channel(managers)
                st.rerun()
            return
        
        # 增强：添加操作统计
        col1, col2, col3 = st.columns(3)
        with col1:
            total_channels = len(channel_df)
            st.metric("总渠道数", total_channels)
        with col2:
            s_level_channels = len(channel_df[channel_df['channel_type'] == 'S级(团长)'])
            st.metric("S级渠道", s_level_channels)
        with col3:
            active_channels = len(channel_df[channel_df['contact_phone'].notna()])
            st.metric("有效联系渠道", active_channels)
        
        # 选择要操作的销售渠道 - 增强选择功能
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_channel = st.selectbox(
                "选择要操作的销售渠道",
                channel_df['channel_name'].tolist(),
                key="channel_operations_select_hybrid",
                help="选择要修改或删除的销售渠道"
            )
        
        with col2:
            if st.button("🔄 刷新列表"):
                st.rerun()
        
        if selected_channel:
            channel_info = channel_df[channel_df['channel_name'] == selected_channel].iloc[0]
            
            # 增强：使用卡片式布局显示当前信息
            with st.container():
                st.markdown("### 🛒 当前渠道信息")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**基本信息**")
                    st.markdown(f"""
                    <div class="info-badge">渠道名称: {channel_info['channel_name']}</div>
                    <div class="info-badge">渠道类型: {channel_info['channel_type']}</div>
                    <div class="info-badge">佣金比例: {channel_info['commission_rate']}%</div>
                    <div class="info-badge">结算方式: {channel_info.get('payment_terms', '未设置')}</div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**联系信息**")
                    st.markdown(f"""
                    <div class="info-badge">联系人: {channel_info.get('contact_person', '未设置')}</div>
                    <div class="info-badge">电话: {channel_info.get('contact_phone', '未设置')}</div>
                    """, unsafe_allow_html=True)
                    if pd.notna(channel_info.get('notes')):
                        st.markdown(f'<div class="info-badge">备注: {channel_info["notes"]}</div>', unsafe_allow_html=True)
            
            # 使用tabs来分离修改和删除操作 - 保持原有标签页结构
            tab1, tab2 = st.tabs(["✏️ 修改信息", "🗑️ 删除渠道"])
            
            with tab1:
                # 修复：使用独立的表单，避免嵌套表单问题
                with st.form("update_channel_form_hybrid"):
                    st.markdown("### 📝 修改渠道信息")
                    
                    new_channel_name = st.text_input("渠道名称*", value=channel_info['channel_name'], 
                                                   help="销售渠道的名称")
                    new_channel_type = st.text_input("渠道类型*", value=channel_info['channel_type'], 
                                                   help="渠道的类型等级")
                    new_contact_person = st.text_input("联系人", value=channel_info.get('contact_person', '') or "", 
                                                     help="渠道的主要联系人")
                    new_contact_phone = st.text_input("联系电话", value=channel_info.get('contact_phone', '') or "", 
                                                    help="联系人的电话号码")
                    new_commission_rate = st.number_input("佣金比例(%)*", min_value=0.0, max_value=100.0,
                                                        value=float(channel_info['commission_rate']), 
                                                        help="给渠道的佣金比例，0-100%")
                    new_payment_terms = st.text_input("结算方式*", value=channel_info.get('payment_terms', '') or "", 
                                                    help="与渠道的结算方式")
                    new_notes = st.text_area("备注信息", value=channel_info.get('notes', '') or "", 
                                           help="关于此渠道的其他重要信息")
                    
                    # 增强：添加修改提示
                    st.info("💡 修改提示：确保信息准确，修改后将自动更新数据库")
                    
                    if st.form_submit_button("💾 更新渠道信息", type="primary"):
                        try:
                            # 修复：直接使用管理器的更新功能
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
                                st.success("✅ 销售渠道信息更新成功！")
                                st.rerun()
                            else:
                                st.error("❌ 销售渠道信息更新失败")
                        except Exception as e:
                            st.error(f"❌ 更新失败: {str(e)}")
            
            with tab2:
                # 增强：更友好的删除界面
                st.markdown("### ⚠️ 删除销售渠道")
                
                warning_container = st.container()
                with warning_container:
                    st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
                    st.markdown(f"**即将删除销售渠道:** `{channel_info['channel_name']}`")
                    st.markdown(f"**渠道ID:** `{channel_info['id']}`")
                    
                    # 显示将要删除的渠道信息摘要
                    with st.expander("查看渠道详细信息"):
                        st.json({
                            "渠道名称": channel_info['channel_name'],
                            "渠道类型": channel_info['channel_type'],
                            "联系人": channel_info.get('contact_person', '无'),
                            "电话": channel_info.get('contact_phone', '无'),
                            "佣金率": f"{channel_info['commission_rate']}%",
                            "结算方式": channel_info.get('payment_terms', '无')
                        })
                
                # 修复：改进确认机制，但保持原有视觉样式
                st.markdown("**请输入渠道名称以确认删除:**")
                confirm_text = st.text_input("", placeholder=channel_info['channel_name'], 
                                             help="输入完整的渠道名称以确认删除操作")
                
                col_delete1, col_delete2 = st.columns(2)
                with col_delete1:
                    # 修复：使用正确的按钮状态控制
                    if st.button("🗑️ 确认删除", type="secondary", 
                               disabled=(confirm_text != channel_info['channel_name']),
                               help="确认删除此销售渠道"):
                        try:
                            # 修复：直接使用管理器的删除功能
                            success = managers['inventory'].delete_sales_channel(channel_info['id'])
                            if success:
                                st.success("✅ 销售渠道删除成功！")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ 销售渠道删除失败")
                        except Exception as e:
                            st.error(f"❌ 删除失败: {str(e)}")
                
                with col_delete2:
                    if st.button("❌ 取消操作", type="secondary", help="取消删除操作"):
                        st.info("已取消删除操作")
                        st.rerun()
    finally:
        conn.close()

def show_pricing_analysis_hybrid(managers):
    """混合版定价分析 - 保持原有结构但增强功能"""
    st.header("💰 定价分析")
    
    tab1, tab2, tab3 = st.tabs(["批量定价", "单个定价", "定价历史"])
    
    with tab1:
        show_batch_pricing_hybrid(managers)
    
    with tab2:
        show_single_pricing_hybrid(managers)
    
    with tab3:
        show_pricing_history_hybrid(managers)

def show_batch_pricing_hybrid(managers):
    """混合版批量定价 - 保持原有功能但增强界面"""
    st.subheader("批量定价分析")
    
    # 获取待定价的库存 - 保持原有查询逻辑
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
        
        # 增强：显示待定价统计
        st.markdown(f"### 📊 待定价商品统计 ({len(pending_inventory)} 件)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_value = pending_inventory['original_value'].sum()
            st.metric("总原始价值", f"¥{total_value:,.2f}")
        with col2:
            avg_value = pending_inventory['original_value'].mean()
            st.metric("平均原始价值", f"¥{avg_value:,.2f}")
        with col3:
            category_count = len(pending_inventory['category'].unique())
            st.metric("涉及品类", f"{category_count} 个")
        
        # 批量定价 - 保持原有按钮样式但增强功能
        if st.button("🚀 开始批量定价分析", type="primary"):
            with st.spinner("正在进行定价分析..."):
                inventory_ids = pending_inventory['id'].tolist()
                pricing_results = managers['pricing'].batch_calculate_prices(inventory_ids)
                
                # 显示结果 - 保持原有指标卡片布局但增强信息
                results_df = pd.DataFrame(pricing_results)
                
                st.markdown("### 📈 定价分析结果")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_price = results_df['suggested_price'].mean()
                    st.metric("平均建议售价", f"¥{avg_price:,.2f}")
                
                with col2:
                    avg_profit = results_df['estimated_profit'].mean()
                    st.metric("平均预计利润", f"¥{avg_profit:,.2f}")
                
                with col3:
                    total_profit = results_df['estimated_profit'].sum()
                    st.metric("总预计利润", f"¥{total_profit:,.2f}")
                
                # 增强：显示详细结果表格
                st.markdown("### 📋 详细定价结果")
                
                # 合并原始信息和定价结果
                detailed_results = pending_inventory.merge(results_df, left_on='id', right_on='inventory_id')
                
                # 显示关键列
                display_columns = ['product_name', 'brand_name', 'category', 'original_value', 'suggested_price', 'estimated_profit', 'profit_margin']
                st.dataframe(detailed_results[display_columns])
                
                # 增强：添加导出功能
                if st.button("📊 导出定价结果"):
                    filename = f"pricing_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                        detailed_results.to_excel(writer, sheet_name='定价分析结果', index=False)
                    st.success(f"定价分析结果已导出: {filename}")
                
                # 增强：添加图表分析
                col1, col2 = st.columns(2)
                
                with col1:
                    # 利润率分布
                    fig_profit_margin = px.histogram(detailed_results, x='profit_margin', nbins=20,
                                                   title='利润率分布')
                    st.plotly_chart(fig_profit_margin, use_container_width=True)
                
                with col2:
                    # 原始价值vs建议售价散点图
                    fig_scatter = px.scatter(detailed_results, x='original_value', y='suggested_price',
                                           color='category', size='estimated_profit',
                                           title='原始价值与建议售价关系')
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
    finally:
        conn.close()

def show_single_pricing_hybrid(managers):
    """混合版单个定价 - 保持原有功能但增强界面"""
    st.subheader("单个商品定价")
    
    # 获取库存列表 - 保持原有查询逻辑
    conn = sqlite3.connect("inventory.db")
    try:
        inventory_df = pd.read_sql_query('''
            SELECT i.*, b.brand_name
            FROM inventory i
            JOIN brands b ON i.brand_id = b.id
            ORDER BY i.created_at DESC
        ''', conn)
        
        if inventory_df.empty:
            st.info("暂无库存数据")
            return
        
        # 增强：显示库存统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总商品数", len(inventory_df))
        with col2:
            pending_count = len(inventory_df[inventory_df['status'] == 'pending'])
            st.metric("待处理商品", pending_count)
        with col3:
            avg_value = inventory_df['original_value'].mean()
            st.metric("平均价值", f"¥{avg_value:,.2f}")
        
        # 选择商品 - 保持原有选择器但增强功能
        selected_product = st.selectbox(
            "选择要定价的商品",
            inventory_df['product_name'].tolist(),
            help="选择要进行定价分析的商品"
        )
        
        if selected_product:
            product_info = inventory_df[inventory_df['product_name'] == selected_product].iloc[0]
            
            # 增强：显示商品信息卡片
            with st.container():
                st.markdown("### 📋 商品信息")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**基本信息**")
                    st.markdown(f"""
                    <div class="info-badge">商品名称: {product_info['product_name']}</div>
                    <div class="info-badge">品牌: {product_info.get('brand_name', '未知')}</div>
                    <div class="info-badge">品类: {product_info['category']}</div>
                    <div class="info-badge">数量: {product_info['quantity']}</div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**价值信息**")
                    st.markdown(f"""
                    <div class="info-badge">原始价值: ¥{product_info['original_value']:,.2f}</div>
                    """, unsafe_allow_html=True)
                    if pd.notna(product_info.get('market_value')):
                        st.markdown(f'<div class="info-badge">市场价值: ¥{product_info["market_value"]:,.2f}</div>', unsafe_allow_html=True)
            
            # 定价分析 - 保持原有按钮样式
            if st.button("🔍 开始定价分析", type="primary"):
                with st.spinner("正在进行定价分析..."):
                    pricing_result = managers['pricing'].calculate_realization_value(product_info['id'])
                    
                    if pricing_result:
                        # 增强：显示详细的定价结果
                        st.markdown("### 📊 定价分析结果")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            suggested_price = pricing_result.get('suggested_price', 0)
                            st.metric("建议售价", f"¥{suggested_price:,.2f}")
                        
                        with col2:
                            estimated_profit = pricing_result.get('estimated_profit', 0)
                            st.metric("预计利润", f"¥{estimated_profit:,.2f}")
                        
                        with col3:
                            profit_margin = pricing_result.get('profit_margin', 0)
                            st.metric("利润率", f"{profit_margin:.1f}%")
                        
                        # 增强：显示定价依据
                        st.markdown("### 📋 定价依据")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**市场分析**")
                            market_analysis = pricing_result.get('market_analysis', {})
                            if market_analysis:
                                for key, value in market_analysis.items():
                                    st.markdown(f'<div class="info-badge">{key}: {value}</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("**风险评估**")
                            risk_factors = pricing_result.get('risk_factors', [])
                            if risk_factors:
                                for factor in risk_factors:
                                    st.markdown(f'<div class="info-badge">⚠️ {factor}</div>', unsafe_allow_html=True)
                        
                        # 增强：显示完整定价结果
                        if st.checkbox("显示完整定价结果"):
                            st.json(pricing_result)
                        
                        # 增强：添加操作建议
                        st.markdown("### 💡 操作建议")
                        
                        if profit_margin > 30:
                            st.success("✅ 利润率较高，建议尽快销售")
                        elif profit_margin > 15:
                            st.info("ℹ️ 利润率适中，可以考虑销售")
                        else:
                            st.warning("⚠️ 利润率较低，建议重新评估或寻找更好的销售渠道")
                        
                        # 增强：添加导出功能
                        if st.button("📊 导出定价结果"):
                            result_df = pd.DataFrame([pricing_result])
                            filename = f"single_pricing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                                result_df.to_excel(writer, sheet_name='单个商品定价', index=False)
                            st.success(f"定价结果已导出: {filename}")
                    
                    else:
                        st.error("定价分析失败，请检查商品信息是否完整")
    
    finally:
        conn.close()

def show_pricing_history_hybrid(managers):
    """混合版定价历史 - 保持原有功能但增强界面"""
    st.subheader("定价历史记录")
    
    # 获取定价历史 - 保持原有查询逻辑
    conn = sqlite3.connect("inventory.db")
    try:
        pricing_history = pd.read_sql_query('''
            SELECT ph.*, i.product_name, b.brand_name
            FROM pricing_history ph
            JOIN inventory i ON ph.inventory_id = i.id
            JOIN brands b ON i.brand_id = b.id
            ORDER BY ph.created_at DESC
            LIMIT 50
        ''', conn)
        
        if pricing_history.empty:
            st.info("暂无定价历史记录")
            return
        
        # 增强：显示历史统计
        st.markdown("### 📊 定价历史统计")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_records = len(pricing_history)
            st.metric("总记录数", total_records)
        with col2:
            avg_price_change = pricing_history['price_change'].mean()
            st.metric("平均价格变化", f"¥{avg_price_change:,.2f}")
        with col3:
            price_increase_count = len(pricing_history[pricing_history['price_change'] > 0])
            st.metric("涨价次数", price_increase_count)
        
        # 显示历史记录 - 保持原有表格显示但增强功能
        st.markdown("### 📋 定价历史记录")
        
        # 增强：添加筛选功能
        with st.expander("🔍 筛选历史记录", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                search_product = st.text_input("搜索商品", "", placeholder="输入商品名称")
            
            with col2:
                date_range = st.date_input("选择日期范围", value=None)
        
        # 应用筛选 - 保持原有筛选逻辑
        filtered_history = pricing_history.copy()
        if search_product:
            filtered_history = filtered_history[filtered_history['product_name'].str.contains(search_product, case=False)]
        
        # 显示筛选结果
        st.dataframe(filtered_history)
        
        # 增强：添加图表分析
        col1, col2 = st.columns(2)
        
        with col1:
            # 价格变化趋势
            fig_trend = px.line(filtered_history, x='created_at', y='price_change',
                              color='product_name', title='价格变化趋势')
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # 价格变化分布
            fig_dist = px.histogram(filtered_history, x='price_change', nbins=20,
                                  title='价格变化分布')
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # 增强：添加导出功能
        if st.button("📊 导出定价历史"):
            filename = f"pricing_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                filtered_history.to_excel(writer, sheet_name='定价历史', index=False)
            st.success(f"定价历史已导出: {filename}")
    
    finally:
        conn.close()

def show_financial_analysis_hybrid(managers):
    """混合版财务测算 - 简化版占位函数"""
    st.header("📈 财务测算")
    st.info("财务测算功能开发中...")

def show_risk_management_hybrid(managers):
    """混合版风控检查 - 简化版占位函数"""
    st.header("⚠️ 风控检查")
    st.info("风控检查功能开发中...")

def show_reports_hybrid(managers):
    """混合版数据报表 - 简化版占位函数"""
    st.header("📊 数据报表")
    st.info("数据报表功能开发中...")

def show_settings_hybrid(managers):
    """混合版系统设置 - 简化版占位函数"""
    st.header("🔧 系统设置")
    st.info("系统设置功能开发中...")

def add_sample_data(managers):
    """添加测试数据 - 保持原有功能"""
    try:
        # 添加测试品牌
        brand_id = managers['inventory'].add_brand(
            brand_name="测试品牌",
            contact_person="测试联系人",
            contact_phone="13800138000",
            brand_type="饮料",
            reputation_score=8
        )
        
        # 添加测试库存
        inventory_id = managers['inventory'].add_inventory(
            brand_id=brand_id,
            product_name="测试商品",
            category="饮料",
            quantity=100,
            original_value=1000.0,
            market_value=1200.0,
            storage_location="仓库A"
        )
        
        st.success("测试数据添加成功！")
        
    except Exception as e:
        st.error(f"添加测试数据失败: {str(e)}")

def add_sample_media(managers):
    """添加测试媒体数据"""
    try:
        media_id = managers['inventory'].add_media_resource(
            media_name="测试媒体资源",
            media_type="社区门禁",
            media_form="静态海报",
            location="测试小区",
            market_price=5000.0,
            discount_rate=80.0,
            actual_cost=4000.0
        )
        
        st.success("测试媒体数据添加成功！")
        
    except Exception as e:
        st.error(f"添加测试媒体数据失败: {str(e)}")

def add_sample_channel(managers):
    """添加测试渠道数据"""
    try:
        channel_id = managers['inventory'].add_sales_channel(
            channel_name="测试渠道",
            channel_type="S级(团长)",
            contact_person="测试团长",
            contact_phone="13800138000",
            commission_rate=5.0,
            payment_terms="月结"
        )
        
        st.success("测试渠道数据添加成功！")
        
    except Exception as e:
        st.error(f"添加测试渠道数据失败: {str(e)}")

if __name__ == "__main__":
    main()
