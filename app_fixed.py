#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广告置换库存管理系统 - 修复版本
解决删除和修改功能无法使用的问题
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
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
    .success-text {
        color: #28a745;
        font-weight: bold;
    }
    .error-text {
        color: #dc3545;
        font-weight: bold;
    }
    .operation-result {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_managers():
    """获取管理器实例 - 不使用缓存避免状态问题"""
    return {
        'inventory': InventoryManager(),
        'pricing': PricingCalculator(),
        'financial': FinancialCalculator()
    }

def main():
    """主函数"""
    st.markdown('<div class="main-header">广告置换库存管理系统</div>', unsafe_allow_html=True)
    
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
    
    # 使用会话状态来管理操作结果
    if 'operation_result' not in st.session_state:
        st.session_state.operation_result = None
    
    # 显示操作结果
    if st.session_state.operation_result:
        result = st.session_state.operation_result
        if result['success']:
            st.success(f"✅ {result['message']}")
        else:
            st.error(f"❌ {result['message']}")
        st.session_state.operation_result = None
    
    managers = get_managers()
    
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

def show_inventory_operations(managers):
    """显示库存操作界面（修改/删除）- 修复版本"""
    st.subheader("库存商品操作")
    
    # 使用会话状态管理选中的商品
    if 'selected_inventory_id' not in st.session_state:
        st.session_state.selected_inventory_id = None
    
    # 获取库存数据
    conn = sqlite3.connect("inventory.db")
    try:
        inventory_df = pd.read_sql_query('''
            SELECT i.*, b.brand_name 
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            ORDER BY i.created_at DESC
        ''', conn)
        
        if inventory_df.empty:
            st.info("暂无库存数据")
            return
        
        # 选择要操作的商品
        product_names = inventory_df['product_name'].tolist()
        selected_product = st.selectbox(
            "选择要操作的商品",
            product_names,
            key="inventory_operations_select"
        )
        
        if selected_product:
            product_info = inventory_df[inventory_df['product_name'] == selected_product].iloc[0]
            product_id = int(product_info['id'])
            
            # 更新会话状态
            st.session_state.selected_inventory_id = product_id
            
            st.write("**当前商品信息:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **商品名称:** {product_info['product_name']}  
                **品牌:** {product_info.get('brand_name', '未知')}  
                **品类:** {product_info['category']}  
                **数量:** {product_info['quantity']}  
                **原始价值:** ¥{product_info['original_value']:,.2f}
                """)
            
            with col2:
                st.info(f"""
                **状态:** {product_info['status']}  
                **存储位置:** {product_info.get('storage_location', '无')}  
                **ID:** {product_id}
                """)
            
            # 使用tabs来分离修改和删除操作
            tab1, tab2 = st.tabs(["✏️ 修改信息", "🗑️ 删除商品"])
            
            with tab1:
                st.write("### 修改商品信息")
                
                # 获取当前值
                current_name = product_info['product_name']
                current_quantity = int(product_info['quantity'])
                current_original_value = float(product_info['original_value'])
                current_market_value = float(product_info['market_value']) if pd.notna(product_info.get('market_value')) else 0.0
                current_status = product_info['status']
                current_storage = product_info.get('storage_location', '') or ""
                
                # 创建独立的输入字段，不使用表单
                new_product_name = st.text_input("商品名称", value=current_name, key="update_name")
                new_quantity = st.number_input("数量", min_value=1, value=current_quantity, key="update_qty")
                new_original_value = st.number_input("原始价值", min_value=0.0, value=current_original_value, key="update_original")
                new_market_value = st.number_input("市场价值", min_value=0.0, value=current_market_value, key="update_market")
                new_status = st.selectbox("状态", ["pending", "approved", "rejected", "sold"], 
                                        index=["pending", "approved", "rejected", "sold"].index(current_status), key="update_status")
                new_storage_location = st.text_input("存储位置", value=current_storage, key="update_storage")
                
                # 电商链接
                st.write("**电商链接**")
                current_jd = product_info.get('jd_link', '') or ""
                current_tmall = product_info.get('tmall_link', '') or ""
                current_xianyu = product_info.get('xianyu_link', '') or ""
                current_pdd = product_info.get('pdd_link', '') or ""
                
                new_jd_link = st.text_input("京东链接", value=current_jd, key="update_jd")
                new_tmall_link = st.text_input("天猫链接", value=current_tmall, key="update_tmall")
                new_xianyu_link = st.text_input("闲鱼链接", value=current_xianyu, key="update_xianyu")
                new_pdd_link = st.text_input("拼多多链接", value=current_pdd, key="update_pdd")
                
                # 更新按钮
                if st.button("更新商品信息", type="primary", key="btn_update_inventory"):
                    try:
                        # 清理数据
                        jd_link = new_jd_link.strip() if new_jd_link.strip() else None
                        tmall_link = new_tmall_link.strip() if new_tmall_link.strip() else None
                        xianyu_link = new_xianyu_link.strip() if new_xianyu_link.strip() else None
                        pdd_link = new_pdd_link.strip() if new_pdd_link.strip() else None
                        
                        # 执行更新
                        success = managers['inventory'].update_inventory(
                            product_id,
                            product_name=new_product_name,
                            quantity=new_quantity,
                            original_value=new_original_value,
                            market_value=new_market_value if new_market_value > 0 else None,
                            status=new_status,
                            storage_location=new_storage_location if new_storage_location.strip() else None,
                            jd_link=jd_link,
                            tmall_link=tmall_link,
                            xianyu_link=xianyu_link,
                            pdd_link=pdd_link
                        )
                        
                        if success:
                            st.session_state.operation_result = {
                                'success': True,
                                'message': f"商品 [{current_name}] 更新成功！"
                            }
                            st.rerun()
                        else:
                            st.session_state.operation_result = {
                                'success': False,
                                'message': f"商品 [{current_name}] 更新失败"
                            }
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"更新失败: {str(e)}")
                        st.info("详细错误信息已记录，请检查日志")
            
            with tab2:
                st.write("### 删除商品")
                st.warning("⚠️ 此操作不可恢复，请谨慎操作！")
                
                st.info(f"即将删除商品: **{current_name}** (ID: {product_id})")
                
                # 确认删除
                confirm_text = st.text_input(
                    "请输入商品名称以确认删除", 
                    placeholder=current_name,
                    key="delete_confirm"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("确认删除", type="secondary", key="btn_delete_inventory",
                               disabled=(confirm_text != current_name)):
                        try:
                            success = managers['inventory'].delete_inventory(product_id)
                            
                            if success:
                                st.session_state.operation_result = {
                                    'success': True,
                                    'message': f"商品 [{current_name}] 删除成功！"
                                }
                                # 清除选中状态
                                st.session_state.selected_inventory_id = None
                                st.rerun()
                            else:
                                st.session_state.operation_result = {
                                    'success': False,
                                    'message': f"商品 [{current_name}] 删除失败"
                                }
                                st.rerun()
                                
                        except Exception as e:
                            st.error(f"删除失败: {str(e)}")
                
                with col2:
                    if st.button("取消", type="secondary", key="btn_cancel_delete"):
                        st.info("删除操作已取消")
                        
    except Exception as e:
        st.error(f"数据库查询异常: {str(e)}")
    finally:
        conn.close()

def show_media_operations(managers):
    """显示媒体资源操作界面 - 修复版本"""
    st.subheader("媒体资源操作")
    
    # 使用会话状态管理选中的媒体
    if 'selected_media_id' not in st.session_state:
        st.session_state.selected_media_id = None
    
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
            media_id = int(media_info['id'])
            
            # 更新会话状态
            st.session_state.selected_media_id = media_id
            
            st.write("**当前媒体信息:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **媒体名称:** {media_info['media_name']}  
                **媒体类型:** {media_info['media_type']}  
                **位置:** {media_info['location']}  
                **刊例价:** ¥{media_info['market_price']:,.2f}
                """)
            
            with col2:
                st.info(f"""
                **实际成本:** ¥{media_info['actual_cost']:,.2f}  
                **状态:** {media_info['status']}  
                **ID:** {media_id}
                """)
            
            # 使用tabs来分离修改和删除操作
            tab1, tab2 = st.tabs(["✏️ 修改信息", "🗑️ 删除媒体"])
            
            with tab1:
                st.write("### 修改媒体信息")
                
                # 获取当前值
                current_name = media_info['media_name']
                current_type = media_info['media_type']
                current_location = media_info['location']
                current_market_price = float(media_info['market_price'])
                current_actual_cost = float(media_info['actual_cost'])
                current_status = media_info['status']
                
                # 创建输入字段
                new_media_name = st.text_input("媒体名称", value=current_name, key="update_media_name")
                new_media_type = st.text_input("媒体类型", value=current_type, key="update_media_type")
                new_location = st.text_input("位置", value=current_location, key="update_media_location")
                new_market_price = st.number_input("刊例价", min_value=0.0, value=current_market_price, key="update_media_market")
                new_actual_cost = st.number_input("实际成本", min_value=0.0, value=current_actual_cost, key="update_media_actual")
                new_status = st.selectbox("状态", ["idle", "occupied", "maintenance", "reserved"],
                                        index=["idle", "occupied", "maintenance", "reserved"].index(current_status), key="update_media_status")
                
                # 扩展字段
                current_specs = media_info.get('media_specs', '') or ""
                current_audience = media_info.get('audience_info', '') or ""
                current_owner = media_info.get('owner_name', '') or ""
                current_contact = media_info.get('contact_person', '') or ""
                current_phone = media_info.get('contact_phone', '') or ""
                
                new_media_specs = st.text_area("媒体规格", value=current_specs, key="update_media_specs")
                new_audience_info = st.text_area("受众信息", value=current_audience, key="update_media_audience")
                new_owner_name = st.text_input("媒体主名称", value=current_owner, key="update_media_owner")
                new_contact_person = st.text_input("联系人", value=current_contact, key="update_media_contact")
                new_contact_phone = st.text_input("联系电话", value=current_phone, key="update_media_phone")
                
                # 更新按钮
                if st.button("更新媒体信息", type="primary", key="btn_update_media"):
                    try:
                        success = managers['inventory'].update_media_resource(
                            media_id,
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
                            st.session_state.operation_result = {
                                'success': True,
                                'message': f"媒体资源 [{current_name}] 更新成功！"
                            }
                            st.rerun()
                        else:
                            st.session_state.operation_result = {
                                'success': False,
                                'message': f"媒体资源 [{current_name}] 更新失败"
                            }
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"更新失败: {str(e)}")
            
            with tab2:
                st.write("### 删除媒体资源")
                st.warning("⚠️ 此操作不可恢复，请谨慎操作！")
                
                st.info(f"即将删除媒体资源: **{current_name}** (ID: {media_id})")
                
                # 确认删除
                confirm_text = st.text_input(
                    "请输入媒体名称以确认删除", 
                    placeholder=current_name,
                    key="delete_media_confirm"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("确认删除", type="secondary", key="btn_delete_media",
                               disabled=(confirm_text != current_name)):
                        try:
                            success = managers['inventory'].delete_media_resource(media_id)
                            
                            if success:
                                st.session_state.operation_result = {
                                    'success': True,
                                    'message': f"媒体资源 [{current_name}] 删除成功！"
                                }
                                # 清除选中状态
                                st.session_state.selected_media_id = None
                                st.rerun()
                            else:
                                st.session_state.operation_result = {
                                    'success': False,
                                    'message': f"媒体资源 [{current_name}] 删除失败"
                                }
                                st.rerun()
                                
                        except Exception as e:
                            st.error(f"删除失败: {str(e)}")
                
                with col2:
                    if st.button("取消", type="secondary", key="btn_cancel_media_delete"):
                        st.info("删除操作已取消")
                        
    except Exception as e:
        st.error(f"数据库查询异常: {str(e)}")
    finally:
        conn.close()

def show_channel_operations(managers):
    """显示销售渠道操作界面 - 修复版本"""
    st.subheader("销售渠道操作")
    
    # 使用会话状态管理选中的渠道
    if 'selected_channel_id' not in st.session_state:
        st.session_state.selected_channel_id = None
    
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
            channel_id = int(channel_info['id'])
            
            # 更新会话状态
            st.session_state.selected_channel_id = channel_id
            
            st.write("**当前渠道信息:**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **渠道名称:** {channel_info['channel_name']}  
                **渠道类型:** {channel_info['channel_type']}  
                **联系人:** {channel_info.get('contact_person', '无')}  
                **联系电话:** {channel_info.get('contact_phone', '无')}
                """)
            
            with col2:
                st.info(f"""
                **佣金比例:** {channel_info['commission_rate']}%  
                **结算方式:** {channel_info.get('payment_terms', '无')}  
                **ID:** {channel_id}
                """)
            
            # 使用tabs来分离修改和删除操作
            tab1, tab2 = st.tabs(["✏️ 修改信息", "🗑️ 删除渠道"])
            
            with tab1:
                st.write("### 修改渠道信息")
                
                # 获取当前值
                current_name = channel_info['channel_name']
                current_type = channel_info['channel_type']
                current_contact = channel_info.get('contact_person', '') or ""
                current_phone = channel_info.get('contact_phone', '') or ""
                current_commission = float(channel_info['commission_rate'])
                current_payment = channel_info.get('payment_terms', '') or ""
                current_notes = channel_info.get('notes', '') or ""
                
                # 创建输入字段
                new_channel_name = st.text_input("渠道名称", value=current_name, key="update_channel_name")
                new_channel_type = st.text_input("渠道类型", value=current_type, key="update_channel_type")
                new_contact_person = st.text_input("联系人", value=current_contact, key="update_channel_contact")
                new_contact_phone = st.text_input("联系电话", value=current_phone, key="update_channel_phone")
                new_commission_rate = st.number_input("佣金比例(%)", min_value=0.0, max_value=100.0,
                                                    value=current_commission, key="update_channel_commission")
                new_payment_terms = st.text_input("结算方式", value=current_payment, key="update_channel_payment")
                new_notes = st.text_area("备注信息", value=current_notes, key="update_channel_notes")
                
                # 更新按钮
                if st.button("更新渠道信息", type="primary", key="btn_update_channel"):
                    try:
                        success = managers['inventory'].update_sales_channel(
                            channel_id,
                            channel_name=new_channel_name,
                            channel_type=new_channel_type,
                            contact_person=new_contact_person if new_contact_person.strip() else None,
                            contact_phone=new_contact_phone if new_contact_phone.strip() else None,
                            commission_rate=new_commission_rate,
                            payment_terms=new_payment_terms if new_payment_terms.strip() else None,
                            notes=new_notes if new_notes.strip() else None
                        )
                        
                        if success:
                            st.session_state.operation_result = {
                                'success': True,
                                'message': f"销售渠道 [{current_name}] 更新成功！"
                            }
                            st.rerun()
                        else:
                            st.session_state.operation_result = {
                                'success': False,
                                'message': f"销售渠道 [{current_name}] 更新失败"
                            }
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"更新失败: {str(e)}")
            
            with tab2:
                st.write("### 删除销售渠道")
                st.warning("⚠️ 此操作不可恢复，请谨慎操作！")
                
                st.info(f"即将删除销售渠道: **{current_name}** (ID: {channel_id})")
                
                # 确认删除
                confirm_text = st.text_input(
                    "请输入渠道名称以确认删除", 
                    placeholder=current_name,
                    key="delete_channel_confirm"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("确认删除", type="secondary", key="btn_delete_channel",
                               disabled=(confirm_text != current_name)):
                        try:
                            success = managers['inventory'].delete_sales_channel(channel_id)
                            
                            if success:
                                st.session_state.operation_result = {
                                    'success': True,
                                    'message': f"销售渠道 [{current_name}] 删除成功！"
                                }
                                # 清除选中状态
                                st.session_state.selected_channel_id = None
                                st.rerun()
                            else:
                                st.session_state.operation_result = {
                                    'success': False,
                                    'message': f"销售渠道 [{current_name}] 删除失败"
                                }
                                st.rerun()
                                
                        except Exception as e:
                            st.error(f"删除失败: {str(e)}")
                
                with col2:
                    if st.button("取消", type="secondary", key="btn_cancel_channel_delete"):
                        st.info("删除操作已取消")
                        
    except Exception as e:
        st.error(f"数据库查询异常: {str(e)}")
    finally:
        conn.close()

# 其他函数保持不变，只复制必要的部分
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
            st.dataframe(inventory_df)
        else:
            st.info("暂无库存数据")
    finally:
        conn.close()

def show_add_inventory(managers):
    """显示添加库存界面"""
    st.subheader("添加库存")
    
    with st.form("add_inventory_form"):
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
        
        submitted = st.form_submit_button("添加库存", type="primary")
        
        if submitted:
            try:
                brand_id = brand_options[selected_brand]
                inventory_id = managers['inventory'].add_inventory(
                    brand_id=brand_id,
                    product_name=product_name,
                    category=category,
                    quantity=quantity,
                    original_value=original_value
                )
                st.success(f"库存添加成功！ID: {inventory_id}")
            except Exception as e:
                st.error(f"添加失败: {str(e)}")

def show_brand_management(managers):
    """显示品牌管理界面"""
    st.subheader("品牌管理")
    
    with st.form("add_brand_form"):
        brand_name = st.text_input("品牌名称", placeholder="如：可口可乐")
        contact_person = st.text_input("联系人", placeholder="如：张经理")
        contact_phone = st.text_input("联系电话", placeholder="如：13800138000")
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
        media_df = pd.read_sql_query('SELECT * FROM media_resources ORDER BY created_at DESC', conn)
        if not media_df.empty:
            st.dataframe(media_df)
        else:
            st.info("暂无媒体资源数据")
    finally:
        conn.close()

def show_add_media(managers):
    """显示添加媒体界面"""
    st.subheader("添加媒体资源")
    
    with st.form("add_media_form"):
        media_name = st.text_input("媒体名称", placeholder="如：朝阳小区门禁广告")
        media_type = st.selectbox("媒体类型", ["社区门禁", "写字楼电梯", "户外大屏", "公交站牌", "地铁广告", "商场广告", "其他"])
        location = st.text_input("具体位置", placeholder="如：北京市朝阳区XX小区")
        market_price = st.number_input("刊例价格 (元)", min_value=0.0, value=5000.0)
        
        submitted = st.form_submit_button("添加媒体", type="primary")
        
        if submitted:
            try:
                media_id = managers['inventory'].add_media_resource(
                    media_name=media_name,
                    media_type=media_type,
                    location=location,
                    market_price=market_price,
                    actual_cost=market_price * 0.8  # 默认8折
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
            st.dataframe(media_df)
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
        channels_df = pd.read_sql_query('SELECT * FROM sales_channels ORDER BY created_at DESC', conn)
        if not channels_df.empty:
            st.dataframe(channels_df)
        else:
            st.info("暂无销售渠道数据")
    finally:
        conn.close()

def show_add_channel(managers):
    """显示添加渠道界面"""
    st.subheader("添加销售渠道")
    
    with st.form("add_channel_form"):
        channel_name = st.text_input("渠道名称", placeholder="如：王团长团购")
        channel_type = st.selectbox("渠道类型", ["S级(团长)", "A级(批发市场)", "B级(零售商)", "C级(个体户)", "电商平台", "其他"])
        contact_person = st.text_input("联系人", placeholder="如：王团长")
        contact_phone = st.text_input("联系电话", placeholder="如：13800138000")
        commission_rate = st.number_input("佣金比例 (%)", min_value=0.0, max_value=100.0, value=5.0)
        
        submitted = st.form_submit_button("添加渠道", type="primary")
        
        if submitted:
            try:
                channel_id = managers['inventory'].add_sales_channel(
                    channel_name=channel_name,
                    channel_type=channel_type,
                    contact_person=contact_person,
                    contact_phone=contact_phone,
                    commission_rate=commission_rate
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
            st.dataframe(channels_df)
        else:
            st.info("暂无销售渠道数据")
    finally:
        conn.close()

def show_pricing_analysis(managers):
    """显示定价分析界面"""
    st.header("💰 定价分析")
    st.info("定价分析功能开发中...")

def show_financial_analysis(managers):
    """显示财务分析界面"""
    st.header("📈 财务测算")
    st.info("财务测算功能开发中...")

def show_risk_management(managers):
    """显示风险管理界面"""
    st.header("⚠️ 风控管理")
    st.info("风控管理功能开发中...")

def show_reports(managers):
    """显示报表界面"""
    st.header("📊 数据报表")
    st.info("数据报表功能开发中...")

def show_settings(managers):
    """显示系统设置"""
    st.header("🔧 系统设置")
    st.info("系统设置功能开发中...")

if __name__ == "__main__":
    main()