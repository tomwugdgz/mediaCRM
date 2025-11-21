#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
库存管理仪表板 - Streamlit Web界面
提供直观的库存管理、定价分析和财务报告功能
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import os
import sys

# 导入自定义模块
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
    """初始化管理器实例"""
    return {
        'inventory': InventoryManager(),
        'pricing': PricingCalculator(),
        'financial': FinancialCalculator()
    }

# 自定义CSS样式
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
    st.sidebar.title("📊 导航菜单")
    
    menu_items = {
        "🏠 概览仪表板": "dashboard",
        "📦 库存管理": "inventory",
        "💰 定价分析": "pricing",
        "📈 财务测算": "financial",
        "⚠️ 风控检查": "risk",
        "📊 数据报表": "reports",
        "⚙️ 系统设置": "settings"
    }
    
    selected_menu = st.sidebar.radio("选择功能", list(menu_items.keys()))
    current_page = menu_items[selected_menu]
    
    # 主标题
    st.markdown('<div class="main-header">广告置换库存管理系统</div>', unsafe_allow_html=True)
    
    # 根据选择显示不同页面
    if current_page == "dashboard":
        show_dashboard(managers)
    elif current_page == "inventory":
        show_inventory_management(managers)
    elif current_page == "pricing":
        show_pricing_analysis(managers)
    elif current_page == "financial":
        show_financial_analysis(managers)
    elif current_page == "risk":
        show_risk_management(managers)
    elif current_page == "reports":
        show_reports(managers)
    elif current_page == "settings":
        show_settings(managers)

def show_dashboard(managers):
    """显示概览仪表板"""
    st.header("🏠 概览仪表板")
    
    # 获取库存概览
    inventory_summary = managers['inventory'].get_inventory_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_inventory = sum(item['count'] for item in inventory_summary['inventory_stats'])
        st.metric("总库存数量", f"{total_inventory} 件")
    
    with col2:
        total_value = sum(item['total_value'] for item in inventory_summary['inventory_stats'])
        st.metric("库存总价值", f"¥{total_value:,.2f}")
    
    with col3:
        pending_count = next((item['count'] for item in inventory_summary['inventory_stats'] 
                             if item['status'] == 'pending'), 0)
        st.metric("待处理库存", f"{pending_count} 件")
    
    with col4:
        avg_value = total_value / total_inventory if total_inventory > 0 else 0
        st.metric("平均单价", f"¥{avg_value:,.2f}")
    
    # 品类分布图表
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 品类分布")
        category_df = pd.DataFrame(inventory_summary['category_stats'])
        if not category_df.empty:
            fig_pie = px.pie(category_df, values='total_value', names='category', 
                           title='库存价值分布')
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("📈 库存状态")
        status_df = pd.DataFrame(inventory_summary['inventory_stats'])
        if not status_df.empty:
            fig_bar = px.bar(status_df, x='status', y='count', 
                           title='库存状态统计')
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # 品牌统计
    st.subheader("🏢 品牌合作情况")
    brand_df = pd.DataFrame(inventory_summary['brand_stats'])
    if not brand_df.empty:
        fig_brand = px.bar(brand_df, x='brand_name', y='inventory_count', 
                          title='各品牌库存数量')
        fig_brand.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_brand, use_container_width=True)

def show_inventory_management(managers):
    """显示库存管理页面"""
    st.header("📦 库存管理")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 库存列表", "➕ 添加库存", "🔍 库存查询", "🏢 品牌管理"])
    
    with tab1:
        # 获取库存列表
        conn = sqlite3.connect("inventory.db")
        inventory_df = pd.read_sql_query('''
            SELECT i.*, b.brand_name 
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            ORDER BY i.created_at DESC
        ''', conn)
        conn.close()
        
        if not inventory_df.empty:
            # 添加状态颜色
            def get_status_color(status):
                color_map = {
                    'pending': '🟡',
                    'approved': '🟢',
                    'rejected': '🔴',
                    'sold': '🔵'
                }
                return color_map.get(status, '⚪')
            
            inventory_df['状态图标'] = inventory_df['status'].apply(get_status_color)
            inventory_df['状态'] = inventory_df['状态图标'] + ' ' + inventory_df['status']
            
            # 显示数据表格
            display_columns = ['状态', 'product_name', 'brand_name', 'category',
                             'quantity', 'original_value', 'expiry_date']
            st.dataframe(inventory_df[display_columns], use_container_width=True)
            
            # 显示商品链接
            st.subheader("🔗 商品链接信息")
            if not inventory_df.empty:
                # 选择要查看链接的商品
                selected_item_for_links = st.selectbox(
                    "选择商品查看链接",
                    inventory_df['id'].tolist(),
                    format_func=lambda x: f"{inventory_df[inventory_df['id']==x]['product_name'].iloc[0]} - {inventory_df[inventory_df['id']==x]['brand_name'].iloc[0]}"
                )
                
                # 获取选中商品的链接信息
                selected_item_data = inventory_df[inventory_df['id']==selected_item_for_links].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if pd.notna(selected_item_data.get('jd_link')) and selected_item_data['jd_link']:
                        st.markdown(f"**京东:** [{selected_item_data['jd_link']}]({selected_item_data['jd_link']})")
                    else:
                        st.text("京东: 无链接")
                    
                    if pd.notna(selected_item_data.get('tmall_link')) and selected_item_data['tmall_link']:
                        st.markdown(f"**天猫:** [{selected_item_data['tmall_link']}]({selected_item_data['tmall_link']})")
                    else:
                        st.text("天猫: 无链接")
                
                with col2:
                    if pd.notna(selected_item_data.get('xianyu_link')) and selected_item_data['xianyu_link']:
                        st.markdown(f"**闲鱼:** [{selected_item_data['xianyu_link']}]({selected_item_data['xianyu_link']})")
                    else:
                        st.text("闲鱼: 无链接")
                    
                    if pd.notna(selected_item_data.get('pdd_link')) and selected_item_data['pdd_link']:
                        st.markdown(f"**拼多多:** [{selected_item_data['pdd_link']}]({selected_item_data['pdd_link']})")
                    else:
                        st.text("拼多多: 无链接")
            
            # 库存操作
            st.subheader("🔧 库存操作")
            
            # 第一行操作
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 生成库存报告"):
                    filename = managers['inventory'].export_to_excel()
                    st.success(f"库存报告已生成: {filename}")
            
            with col2:
                selected_inventory = st.selectbox("选择库存进行定价", inventory_df['id'].tolist())
                if st.button("💰 计算定价"):
                    pricing_result = managers['pricing'].calculate_realization_value(selected_inventory)
                    if 'error' not in pricing_result:
                        st.success("定价计算完成！")
                        st.json(pricing_result)
                    else:
                        st.error(pricing_result['error'])
            
            with col3:
                selected_inventory_for_edit = st.selectbox("选择要修改的库存", inventory_df['id'].tolist(), key="edit_inventory")
                if st.button("✏️ 修改库存", type="primary"):
                    # 加载库存信息到session state
                    inventory_item = managers['inventory'].get_inventory_by_id(selected_inventory_for_edit)
                    if inventory_item:
                        st.session_state['edit_inventory_data'] = inventory_item
                        st.session_state['show_edit_form'] = True
                        st.rerun()
            
            # 修改库存表单
            if st.session_state.get('show_edit_form', False):
                st.subheader("✏️ 修改库存信息")
                
                edit_data = st.session_state['edit_inventory_data']
                
                with st.form("edit_inventory_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # 获取品牌列表
                        conn = sqlite3.connect("inventory.db")
                        brands_df = pd.read_sql_query('SELECT id, brand_name FROM brands', conn)
                        conn.close()
                        
                        edit_brand_id = st.selectbox("品牌", brands_df['id'].tolist(),
                                                   index=int(brands_df[brands_df['id']==edit_data['brand_id']].index[0]) if len(brands_df[brands_df['id']==edit_data['brand_id']]) > 0 else 0,
                                                   format_func=lambda x: brands_df[brands_df['id']==x]['brand_name'].iloc[0])
                        edit_product_name = st.text_input("商品名称", value=edit_data['product_name'])
                        edit_category = st.text_input("商品类别", value=edit_data['category'])
                        edit_quantity = st.number_input("数量", min_value=1, value=edit_data['quantity'])
                    
                    with col2:
                        edit_original_value = st.number_input("原价(元)", min_value=0.0, value=float(edit_data['original_value']))
                        edit_market_value = st.number_input("市场价值(元)", min_value=0.0, value=float(edit_data['market_value']))
                        edit_expiry_date = st.date_input("保质期", value=pd.to_datetime(edit_data['expiry_date']).date() if edit_data['expiry_date'] else None)
                        edit_storage_location = st.text_input("存储位置", value=edit_data['storage_location'])
                        edit_status = st.selectbox("状态", ["pending", "approved", "rejected", "sold"],
                                                   index=["pending", "approved", "rejected", "sold"].index(edit_data['status']))
                    
                    # 商品链接编辑
                    st.subheader("🔗 商品链接")
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        edit_jd_link = st.text_input("京东链接", value=edit_data.get('jd_link', ''), placeholder="https://item.jd.com/xxx.html")
                        edit_tmall_link = st.text_input("天猫链接", value=edit_data.get('tmall_link', ''), placeholder="https://detail.tmall.com/xxx.htm")
                    
                    with col4:
                        edit_xianyu_link = st.text_input("闲鱼链接", value=edit_data.get('xianyu_link', ''), placeholder="https://2.taobao.com/xxx")
                        edit_pdd_link = st.text_input("拼多多链接", value=edit_data.get('pdd_link', ''), placeholder="https://mobile.yangkeduo.com/xxx.html")
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        if st.form_submit_button("💾 保存修改"):
                            success = managers['inventory'].update_inventory(
                                selected_inventory_for_edit,
                                brand_id=edit_brand_id,
                                product_name=edit_product_name,
                                category=edit_category,
                                quantity=edit_quantity,
                                original_value=edit_original_value,
                                market_value=edit_market_value,
                                expiry_date=edit_expiry_date.strftime('%Y-%m-%d') if edit_expiry_date else None,
                                storage_location=edit_storage_location,
                                status=edit_status,
                                jd_link=edit_jd_link if edit_jd_link else None,
                                tmall_link=edit_tmall_link if edit_tmall_link else None,
                                xianyu_link=edit_xianyu_link if edit_xianyu_link else None,
                                pdd_link=edit_pdd_link if edit_pdd_link else None
                            )
                            if success:
                                st.success("库存信息修改成功！")
                                del st.session_state['edit_inventory_data']
                                del st.session_state['show_edit_form']
                                st.rerun()
                            else:
                                st.error("修改失败，请重试")
                    
                    with col4:
                        if st.form_submit_button("❌ 取消修改"):
                            del st.session_state['edit_inventory_data']
                            del st.session_state['show_edit_form']
                            st.rerun()
            
            # 删除功能
            st.subheader("🗑️ 删除库存商品")
            col1, col2 = st.columns(2)
            
            with col1:
                selected_inventory_for_delete = st.selectbox("选择要删除的库存", inventory_df['id'].tolist(), key="delete_inventory")
                if st.button("🗑️ 删除库存", type="secondary"):
                    if managers['inventory'].delete_inventory(selected_inventory_for_delete):
                        st.success(f"库存 ID {selected_inventory_for_delete} 已删除")
                        st.rerun()
                    else:
                        st.error("删除失败，请检查库存是否存在或是否有关联数据")
            
            with col2:
                # 按状态批量删除
                status_to_delete = st.selectbox("按状态删除库存", ["pending", "approved", "rejected", "sold"])
                if st.button("🗑️ 删除指定状态库存", type="secondary"):
                    # 获取该状态的所有库存
                    conn = sqlite3.connect("inventory.db")
                    status_df = pd.read_sql_query(
                        'SELECT id FROM inventory WHERE status = ?',
                        conn,
                        params=(status_to_delete,)
                    )
                    conn.close()
                    
                    if not status_df.empty:
                        deleted_count = 0
                        for inv_id in status_df['id']:
                            if managers['inventory'].delete_inventory(inv_id):
                                deleted_count += 1
                        
                        if deleted_count > 0:
                            st.success(f"已删除 {deleted_count} 个 {status_to_delete} 状态的库存")
                            st.rerun()
                        else:
                            st.error("删除失败")
                    else:
                        st.info(f"没有 {status_to_delete} 状态的库存")
            col1, col2 = st.columns(2)
            
            with col1:
                # 按状态批量删除
                status_to_delete = st.selectbox("按状态删除库存", ["pending", "approved", "rejected", "sold"], key="status_delete_2")
                if st.button("🗑️ 删除指定状态库存", type="secondary", key="delete_by_status_2"):
                    # 获取该状态的所有库存
                    conn = sqlite3.connect("inventory.db")
                    status_df = pd.read_sql_query(
                        'SELECT id FROM inventory WHERE status = ?',
                        conn,
                        params=(status_to_delete,)
                    )
                    conn.close()
                    
                    if not status_df.empty:
                        deleted_count = 0
                        for inv_id in status_df['id']:
                            if managers['inventory'].delete_inventory(inv_id):
                                deleted_count += 1
                        
                        if deleted_count > 0:
                            st.success(f"已删除 {deleted_count} 个 {status_to_delete} 状态的库存")
                            st.rerun()
                        else:
                            st.error("删除失败")
                    else:
                        st.info(f"没有 {status_to_delete} 状态的库存")
            
            # 清空所有库存（需要确认）
            st.subheader("⚠️ 危险操作")
            confirm_text = st.text_input("输入 '确认删除' 以清空所有库存", "")
            if st.button("⚠️ 清空所有库存", type="primary"):
                if confirm_text == "确认删除":
                    # 获取所有库存ID
                    conn = sqlite3.connect("inventory.db")
                    all_df = pd.read_sql_query('SELECT id FROM inventory', conn)
                    conn.close()
                    
                    deleted_count = 0
                    for inv_id in all_df['id']:
                        if managers['inventory'].delete_inventory(inv_id):
                            deleted_count += 1
                    
                    st.success(f"已删除 {deleted_count} 个库存记录")
                    st.rerun()
                else:
                    st.error("请输入正确的确认文本")
        else:
            st.info("暂无库存数据")
    
    with tab2:
        st.subheader("➕ 添加新库存")
        
        with st.form("add_inventory_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # 获取品牌列表
                conn = sqlite3.connect("inventory.db")
                brands_df = pd.read_sql_query('SELECT id, brand_name FROM brands', conn)
                conn.close()
                
                brand_id = st.selectbox("选择品牌", brands_df['id'].tolist(),
                                       format_func=lambda x: brands_df[brands_df['id']==x]['brand_name'].iloc[0])
                product_name = st.text_input("商品名称")
                category = st.selectbox("商品品类", ["饮料", "日化", "家电", "食品", "其他"])
                quantity = st.number_input("数量", min_value=1, value=100)
            
            with col2:
                original_value = st.number_input("原始价值 (元)", min_value=0.0, value=10000.0)
                market_value = st.number_input("市场价值 (元)", min_value=0.0, value=None)
                expiry_date = st.date_input("保质期", value=None)
                storage_location = st.text_input("存储位置")
            
            # 商品链接输入
            st.subheader("🔗 商品链接")
            col3, col4 = st.columns(2)
            
            with col3:
                jd_link = st.text_input("京东链接", placeholder="https://item.jd.com/xxx.html")
                tmall_link = st.text_input("天猫链接", placeholder="https://detail.tmall.com/xxx.htm")
            
            with col4:
                xianyu_link = st.text_input("闲鱼链接", placeholder="https://2.taobao.com/xxx")
                pdd_link = st.text_input("拼多多链接", placeholder="https://mobile.yangkeduo.com/xxx.html")
            
            submitted = st.form_submit_button("添加库存")
            if submitted and product_name:
                try:
                    inventory_id = managers['inventory'].add_inventory(
                        brand_id=brand_id,
                        product_name=product_name,
                        category=category,
                        quantity=quantity,
                        original_value=original_value,
                        market_value=market_value,
                        expiry_date=expiry_date.strftime('%Y-%m-%d') if expiry_date else None,
                        storage_location=storage_location,
                        jd_link=jd_link if jd_link else None,
                        tmall_link=tmall_link if tmall_link else None,
                        xianyu_link=xianyu_link if xianyu_link else None,
                        pdd_link=pdd_link if pdd_link else None
                    )
                    st.success(f"库存添加成功！ID: {inventory_id}")
                except Exception as e:
                    st.error(f"添加失败: {str(e)}")
    
    with tab3:
        st.subheader("🔍 库存查询")
        
        search_term = st.text_input("搜索商品名称")
        if search_term:
            conn = sqlite3.connect("inventory.db")
            search_df = pd.read_sql_query('''
                SELECT i.*, b.brand_name 
                FROM inventory i
                LEFT JOIN brands b ON i.brand_id = b.id
                WHERE i.product_name LIKE ?
                ORDER BY i.created_at DESC
            ''', conn, params=(f'%{search_term}%',))
            conn.close()
            
            if not search_df.empty:
                st.dataframe(search_df, use_container_width=True)
            else:
                st.info("未找到匹配的商品")
    
    with tab4:
        st.subheader("🏢 品牌管理")
        
        # 获取品牌列表
        conn = sqlite3.connect("inventory.db")
        brands_df = pd.read_sql_query('SELECT * FROM brands', conn)
        conn.close()
        
        if not brands_df.empty:
            # 显示品牌表格
            display_columns = ['brand_name', 'brand_type', 'contact_person', 'reputation_score']
            st.dataframe(brands_df[display_columns], use_container_width=True)
            
            # 品牌操作
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("品牌详情")
                selected_brand = st.selectbox("选择品牌查看详情", brands_df['id'].tolist(),
                                            format_func=lambda x: brands_df[brands_df['id']==x]['brand_name'].iloc[0])
                
                if st.button("查看品牌详情"):
                    brand_info = brands_df[brands_df['id']==selected_brand].iloc[0]
                    st.write(f"**品牌名称:** {brand_info['brand_name']}")
                    st.write(f"**品类:** {brand_info['brand_type']}")
                    st.write(f"**联系人:** {brand_info['contact_person']}")
                    st.write(f"**联系方式:** {brand_info['contact_phone']}")
                    st.write(f"**邮箱:** {brand_info['contact_email']}")
                    st.write(f"**声誉评分:** {brand_info['reputation_score']}/10")
            
            with col2:
                st.write("添加新品牌")
                with st.form("add_brand_form"):
                    brand_name = st.text_input("品牌名称*")
                    brand_type = st.text_input("品牌品类")
                    contact_person = st.text_input("联系人")
                    contact_phone = st.text_input("联系电话")
                    contact_email = st.text_input("邮箱")
                    reputation_score = st.slider("声誉评分", 1, 10, 5)
                    
                    if st.form_submit_button("添加品牌"):
                        if brand_name:
                            try:
                                brand_id = managers['inventory'].add_brand(
                                    brand_name=brand_name,
                                    brand_type=brand_type,
                                    contact_person=contact_person,
                                    contact_phone=contact_phone,
                                    contact_email=contact_email,
                                    reputation_score=reputation_score
                                )
                                st.success(f"品牌添加成功！ID: {brand_id}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"添加失败: {str(e)}")
                        else:
                            st.error("品牌名称不能为空")
            
            with col3:
                st.write("品牌操作")
                selected_brand_for_action = st.selectbox("选择要操作的品牌", brands_df['id'].tolist(),
                                                       format_func=lambda x: brands_df[brands_df['id']==x]['brand_name'].iloc[0],
                                                       key="action_brand")
                
                col_action1, col_action2 = st.columns(2)
                
                with col_action1:
                    if st.button("✏️ 修改品牌", type="primary"):
                        # 加载品牌信息到session state
                        brand_item = managers['inventory'].get_brand_by_id(selected_brand_for_action)
                        if brand_item:
                            st.session_state['edit_brand_data'] = brand_item
                            st.session_state['show_edit_brand_form'] = True
                            st.rerun()
                
                with col_action2:
                    # 检查是否有关联库存
                    conn = sqlite3.connect("inventory.db")
                    related_inventory = pd.read_sql_query(
                        'SELECT COUNT(*) as count FROM inventory WHERE brand_id = ?',
                        conn,
                        params=(selected_brand_for_action,)
                    )
                    conn.close()
                    
                    inventory_count = related_inventory.iloc[0]['count']
                    
                    if inventory_count > 0:
                        st.warning(f"⚠️ 该品牌下有 {inventory_count} 个库存商品，无法删除")
                    else:
                        if st.button("🗑️ 删除品牌", type="secondary"):
                            if managers['inventory'].delete_brand(selected_brand_for_action):
                                st.success(f"品牌 '{brands_df[brands_df['id']==selected_brand_for_action]['brand_name'].iloc[0]}' 已删除")
                                st.rerun()
                            else:
                                st.error("删除失败")
            
            # 修改品牌表单
            if st.session_state.get('show_edit_brand_form', False):
                st.subheader("✏️ 修改品牌信息")
                
                edit_data = st.session_state['edit_brand_data']
                
                with st.form("edit_brand_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_brand_name = st.text_input("品牌名称", value=edit_data['brand_name'])
                        edit_contact_person = st.text_input("联系人", value=edit_data['contact_person'])
                        edit_contact_phone = st.text_input("联系电话", value=edit_data['contact_phone'])
                        edit_contact_email = st.text_input("联系邮箱", value=edit_data['contact_email'])
                    
                    with col2:
                        edit_brand_type = st.selectbox("品牌类型", ["饮料", "日化", "小家电", "食品", "其他"],
                                                     index=["饮料", "日化", "小家电", "食品", "其他"].index(edit_data['brand_type']))
                        edit_reputation_score = st.slider("品牌信誉评分", 1, 10, value=edit_data['reputation_score'])
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        if st.form_submit_button("💾 保存修改"):
                            success = managers['inventory'].update_brand(
                                selected_brand_for_action,
                                brand_name=edit_brand_name,
                                contact_person=edit_contact_person,
                                contact_phone=edit_contact_phone,
                                contact_email=edit_contact_email,
                                brand_type=edit_brand_type,
                                reputation_score=edit_reputation_score
                            )
                            if success:
                                st.success("品牌信息修改成功！")
                                del st.session_state['edit_brand_data']
                                del st.session_state['show_edit_brand_form']
                                st.rerun()
                            else:
                                st.error("修改失败，请重试")
                    
                    with col4:
                        if st.form_submit_button("❌ 取消修改"):
                            del st.session_state['edit_brand_data']
                            del st.session_state['show_edit_brand_form']
                            st.rerun()
        else:
            st.info("暂无品牌数据")

def show_pricing_analysis(managers):
    """显示定价分析页面"""
    st.header("💰 定价分析")
    
    tab1, tab2, tab3 = st.tabs(["🔍 单品定价", "📊 批量定价", "📈 价格趋势"])
    
    with tab1:
        st.subheader("🔍 单品定价分析")
        
        # 获取库存列表
        conn = sqlite3.connect("inventory.db")
        inventory_df = pd.read_sql_query('''
            SELECT i.id, i.product_name, b.brand_name, i.category, i.quantity, i.original_value
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            WHERE i.status = 'pending'
        ''', conn)
        conn.close()
        
        if not inventory_df.empty:
            selected_product = st.selectbox(
                "选择商品", 
                inventory_df['id'].tolist(),
                format_func=lambda x: f"{inventory_df[inventory_df['id']==x]['product_name'].iloc[0]} - {inventory_df[inventory_df['id']==x]['brand_name'].iloc[0]}"
            )
            
            if st.button("计算定价"):
                with st.spinner("正在计算市场价格..."):
                    result = managers['pricing'].calculate_realization_value(selected_product)
                    
                    if 'error' not in result:
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("原始价值", f"¥{result['original_value']:,.2f}")
                            st.metric("市场价值", f"¥{result['market_value']:,.2f}")
                        
                        with col2:
                            st.metric("变现率", f"{result['realization_rate']:.2%}")
                            st.metric("建议售价", f"¥{result['recommended_sale_price']:,.2f}")
                        
                        with col3:
                            expected_return = result['expected_cash_return']
                            st.metric("预期回报", f"¥{expected_return:,.2f}")
                            
                            # 风险等级显示
                            risk_level = result['risk_level']
                            risk_display = {
                                "low": "🟢 低风险",
                                "medium": "🟡 中风险",
                                "high": "🔴 高风险"
                            }.get(risk_level, "⚪ 未知")
                            st.metric("风险等级", risk_display)
                        
                        # 价格来源详情
                        with st.expander("查看价格来源详情"):
                            price_sources = result.get('price_sources', {})
                            if price_sources.get('pdd_price'):
                                st.write(f"拼多多价格: ¥{price_sources['pdd_price']}")
                            if price_sources.get('xianyu_price'):
                                st.write(f"闲鱼价格: ¥{price_sources['xianyu_price']}")
                            if price_sources.get('recommended_price'):
                                st.write(f"建议回收价: ¥{price_sources['recommended_price']}")
                    else:
                        st.error(result['error'])
        else:
            st.info("暂无待定价的商品")
    
    with tab2:
        st.subheader("📊 批量定价分析")
        
        if st.button("批量计算所有待定价商品"):
            with st.spinner("正在批量计算定价..."):
                # 获取所有待定价库存
                conn = sqlite3.connect("inventory.db")
                pending_df = pd.read_sql_query('''
                    SELECT id FROM inventory WHERE status = 'pending' OR market_value IS NULL
                ''', conn)
                conn.close()
                
                if not pending_df.empty:
                    inventory_ids = pending_df['id'].tolist()
                    results = managers['pricing'].batch_calculate_prices(inventory_ids)
                    
                    # 显示结果表格
                    results_df = pd.DataFrame(results)
                    if not results_df.empty:
                        display_columns = ['product_name', 'original_value', 'market_value', 
                                         'realization_rate', 'expected_cash_return', 'risk_level']
                        st.dataframe(results_df[display_columns], use_container_width=True)
                        
                        # 生成报告
                        if st.button("生成定价报告"):
                            report_file = managers['pricing'].generate_pricing_report(inventory_ids)
                            st.success(f"定价报告已生成: {report_file}")
                else:
                    st.info("没有需要定价的商品")
    
    with tab3:
        st.subheader("📈 价格趋势分析")
        st.info("价格趋势分析功能开发中...")

def show_financial_analysis(managers):
    """显示财务分析页面"""
    st.header("📈 财务测算")
    
    tab1, tab2, tab3 = st.tabs(["💹 交易测算", "📊 利润预测", "📋 财务报告"])
    
    with tab1:
        st.subheader("💹 单笔交易测算")
        
        # 获取库存、广告资源、渠道列表
        conn = sqlite3.connect("inventory.db")
        inventory_df = pd.read_sql_query('SELECT id, product_name FROM inventory WHERE status = "pending"', conn)
        ad_resources_df = pd.read_sql_query('SELECT id, resource_name FROM ad_resources WHERE status = "idle"', conn)
        channels_df = pd.read_sql_query('SELECT id, channel_name FROM sales_channels', conn)
        conn.close()
        
        if not inventory_df.empty and not ad_resources_df.empty and not channels_df.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                inventory_id = st.selectbox("选择库存商品", inventory_df['id'].tolist(),
                                           format_func=lambda x: inventory_df[inventory_df['id']==x]['product_name'].iloc[0])
            
            with col2:
                ad_resource_id = st.selectbox("选择广告资源", ad_resources_df['id'].tolist(),
                                             format_func=lambda x: ad_resources_df[ad_resources_df['id']==x]['resource_name'].iloc[0])
            
            with col3:
                channel_id = st.selectbox("选择销售渠道", channels_df['id'].tolist(),
                                         format_func=lambda x: channels_df[channels_df['id']==x]['channel_name'].iloc[0])
            
            proposed_price = st.number_input("建议销售价格 (可选)", min_value=0.0, value=0.0, 
                                           help="留空则使用系统自动计算的价格")
            
            if st.button("计算交易利润"):
                result = managers['financial'].calculate_transaction_profit(
                    inventory_id, ad_resource_id, channel_id, 
                    proposed_price if proposed_price > 0 else None
                )
                
                if 'error' not in result:
                    # 结果显示
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("总收入", f"¥{result['total_revenue']:,.2f}")
                        st.metric("总成本", f"¥{result['total_cost']:,.2f}")
                    
                    with col2:
                        st.metric("净利润", f"¥{result['net_profit']:,.2f}")
                        st.metric("利润率", f"{result['profit_margin']:.2%}")
                    
                    with col3:
                        st.metric("投资回报率", f"{result['return_on_investment']:.2%}")
                        
                        if result['feasibility']:
                            st.success("✅ 交易可行")
                        else:
                            st.error("❌ 交易不可行")
                    
                    # 成本明细
                    with st.expander("查看成本明细"):
                        cost_df = pd.DataFrame(list(result['cost_breakdown'].items()), 
                                             columns=['成本项目', '金额'])
                        st.dataframe(cost_df, use_container_width=True)
                    
                    # 风险评估
                    with st.expander("查看风险评估"):
                        risk_assessment = result['risk_assessment']
                        st.write(f"风险等级: **{risk_assessment['risk_level']}**")
                        st.write("风险因素:")
                        for factor in risk_assessment['risk_factors']:
                            st.write(f"- {factor}")
                    
                    # 建议
                    with st.expander("查看建议"):
                        for recommendation in result['recommendations']:
                            st.write(f"- {recommendation}")
                else:
                    st.error(result['error'])
        else:
            st.warning("请确保有足够的库存、广告资源和销售渠道数据")
    
    with tab2:
        st.subheader("📊 利润预测")
        
        months = st.slider("预测月份", min_value=1, max_value=12, value=3)
        
        if st.button("生成利润预测"):
            with st.spinner("正在生成预测..."):
                forecast = managers['financial'].generate_profit_forecast(months)
                
                st.metric("预测总利润", f"¥{forecast['total_predicted_profit']:,.2f}")
                st.metric("历史月均利润", f"¥{forecast['historical_avg_profit']:,.2f}")
                st.metric("待处理库存价值", f"¥{forecast['pending_inventory_value']:,.2f}")
                
                # 月度预测图表
                forecast_df = pd.DataFrame(forecast['monthly_forecast'])
                if not forecast_df.empty:
                    fig = px.line(forecast_df, x='month', y='predicted_profit', 
                                title='月度利润预测')
                    fig.update_layout(xaxis_title='月份', yaxis_title='预测利润(元)')
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📋 财务报告")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("开始日期", 
                                     value=datetime.now() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("结束日期", value=datetime.now())
        
        if st.button("生成财务报告"):
            with st.spinner("正在生成财务报告..."):
                report_file = managers['financial'].generate_financial_report(
                    start_date.strftime('%Y-%m-%d'), 
                    end_date.strftime('%Y-%m-%d')
                )
                st.success(f"财务报告已生成: {report_file}")

def show_risk_management(managers):
    """显示风控管理页面"""
    st.header("⚠️ 风控管理")
    
    tab1, tab2, tab3 = st.tabs(["🔍 风控检查", "📋 风控规则", "🚨 风险预警"])
    
    with tab1:
        st.subheader("🔍 库存风控检查")
        
        # 获取库存列表
        conn = sqlite3.connect("inventory.db")
        inventory_df = pd.read_sql_query('SELECT id, product_name FROM inventory', conn)
        conn.close()
        
        if not inventory_df.empty:
            selected_inventory = st.selectbox("选择库存进行风控检查", inventory_df['id'].tolist(),
                                            format_func=lambda x: inventory_df[inventory_df['id']==x]['product_name'].iloc[0])
            
            if st.button("执行风控检查"):
                risk_result = managers['inventory'].check_inventory_risk(selected_inventory)
                
                if risk_result['passed']:
                    st.success("✅ 通过风控检查")
                else:
                    st.error("❌ 未通过风控检查")
                    st.write("违规项目:")
                    for violation in risk_result['violations']:
                        st.write(f"- {violation}")
                
                if risk_result['suggestions']:
                    st.write("建议:")
                    for suggestion in risk_result['suggestions']:
                        st.write(f"- {suggestion}")
        else:
            st.info("暂无库存数据")
    
    with tab2:
        st.subheader("📋 风控规则管理")
        
        # 获取风控规则
        rules = managers['inventory'].get_active_risk_rules()
        
        if rules:
            for rule in rules:
                with st.expander(f"{rule['rule_name']}"):
                    rule_config = rule['rule_config']
                    st.write(f"规则类型: {rule['rule_type']}")
                    if 'reason' in rule_config:
                        st.write(f"原因: {rule_config['reason']}")
                    
                    # 显示具体规则配置
                    if rule['rule_type'] == 'category':
                        if 'forbidden_categories' in rule_config:
                            st.write("禁止的品类:")
                            for category in rule_config['forbidden_categories']:
                                st.write(f"- {category}")
                    elif rule['rule_type'] == 'brand':
                        if 'min_reputation_score' in rule_config:
                            st.write(f"最低品牌声誉评分: {rule_config['min_reputation_score']}")
                    elif rule['rule_type'] == 'expiry':
                        if 'min_expiry_months' in rule_config:
                            st.write(f"最低保质期月份: {rule_config['min_expiry_months']}")
        else:
            st.info("暂无风控规则")
    
    with tab3:
        st.subheader("🚨 风险预警")
        st.info("风险预警功能开发中...")

def show_reports(managers):
    """显示报表页面"""
    st.header("📊 数据报表")
    
    tab1, tab2, tab3 = st.tabs(["📈 库存报表", "💰 定价报表", "📊 财务报表"])
    
    with tab1:
        st.subheader("📈 库存报表")
        
        if st.button("生成库存Excel报表"):
            with st.spinner("正在生成库存报表..."):
                filename = managers['inventory'].export_to_excel()
                st.success(f"库存报表已生成: {filename}")
    
    with tab2:
        st.subheader("💰 定价分析报表")
        
        # 获取待定价库存
        conn = sqlite3.connect("inventory.db")
        pending_df = pd.read_sql_query('SELECT id FROM inventory WHERE status = "pending"', conn)
        conn.close()
        
        if not pending_df.empty:
            if st.button("生成定价分析报表"):
                with st.spinner("正在生成定价报表..."):
                    inventory_ids = pending_df['id'].tolist()
                    report_file = managers['pricing'].generate_pricing_report(inventory_ids)
                    st.success(f"定价分析报表已生成: {report_file}")
        else:
            st.info("没有需要定价的商品")
    
    with tab3:
        st.subheader("📊 财务分析报表")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("开始日期", 
                                     value=datetime.now() - timedelta(days=30),
                                     key="financial_start")
        
        with col2:
            end_date = st.date_input("结束日期", value=datetime.now(),
                                   key="financial_end")
        
        if st.button("生成财务分析报表"):
            with st.spinner("正在生成财务分析报表..."):
                report_file = managers['financial'].generate_financial_report(
                    start_date.strftime('%Y-%m-%d'), 
                    end_date.strftime('%Y-%m-%d')
                )
                st.success(f"财务分析报表已生成: {report_file}")

def show_settings(managers):
    """显示设置页面"""
    st.header("⚙️ 系统设置")
    
    tab1, tab2 = st.tabs(["🔧 基础设置", "📊 数据管理"])
    
    with tab1:
        st.subheader("🔧 基础设置")
        
        # 数据库状态
        if os.path.exists("inventory.db"):
            db_size = os.path.getsize("inventory.db")
            st.info(f"数据库文件大小: {db_size / 1024:.2f} KB")
        else:
            st.warning("数据库文件不存在")
        
        # 系统信息
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**模块状态:**")
            st.write("- ✅ 库存管理模块")
            st.write("- ✅ 定价计算模块") 
            st.write("- ✅ 财务测算模块")
            st.write("- ✅ 风控检查模块")
        
        with col2:
            st.write("**数据状态:**")
            conn = sqlite3.connect("inventory.db")
            
            # 统计各表数据量
            tables = ['inventory', 'brands', 'ad_resources', 'sales_channels', 'transactions']
            for table in tables:
                count = pd.read_sql_query(f'SELECT COUNT(*) as count FROM {table}', conn).iloc[0]['count']
                st.write(f"- {table}: {count} 条记录")
            
            conn.close()
    
    with tab2:
        st.subheader("📊 数据管理")
        
        # 数据备份
        if st.button("创建数据备份"):
            backup_filename = f"inventory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            import shutil
            shutil.copy("inventory.db", backup_filename)
            st.success(f"数据备份已创建: {backup_filename}")
        
        # 数据导入
        uploaded_file = st.file_uploader("导入Excel数据", type=['xlsx', 'xls'])
        if uploaded_file is not None:
            if st.button("导入数据"):
                try:
                    # 这里可以实现Excel数据导入功能
                    st.success("数据导入功能开发中...")
                except Exception as e:
                    st.error(f"导入失败: {str(e)}")

if __name__ == "__main__":
    main()