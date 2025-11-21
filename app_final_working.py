#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广告置换库存管理系统 - 修复版
完全重写的前端界面，解决删除和修改功能问题
"""

import streamlit as st
import pandas as pd
import sqlite3
from inventory_manager import InventoryManager
from datetime import datetime

def main():
    st.set_page_config(
        page_title="广告置换库存管理系统",
        page_icon="📦",
        layout="wide"
    )
    
    st.title("📦 广告置换库存管理系统 - 修复版")
    
    # 创建管理器实例
    manager = InventoryManager()
    
    # 侧边栏导航
    with st.sidebar:
        st.header("导航菜单")
        selected_tab = st.selectbox(
            "选择功能模块",
            ["库存管理", "媒体资源管理", "销售渠道管理", "品牌管理", "数据概览"]
        )
        
        st.divider()
        
        # 显示当前时间
        st.write(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 快速统计
        try:
            summary = manager.get_inventory_summary()
            total_items = sum(stat['count'] for stat in summary['inventory_stats'])
            total_value = sum(stat['total_value'] for stat in summary['inventory_stats'])
            st.metric("库存商品数", total_items)
            st.metric("总价值", f"¥{total_value:,.0f}")
        except:
            pass
    
    # 库存管理模块
    if selected_tab == "库存管理":
        st.header("库存商品管理")
        
        # 获取库存数据
        inventory_data = manager.get_all_inventory()
        
        if not inventory_data:
            st.warning("暂无库存数据")
            if st.button("添加测试数据"):
                add_test_data(manager)
                st.rerun()
            return
        
        # 创建DataFrame
        df = pd.DataFrame(inventory_data)
        
        # 显示库存列表
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("库存列表")
            # 使用session state管理选中项
            if 'selected_inventory_id' not in st.session_state:
                st.session_state.selected_inventory_id = None
            
            # 创建可选择的列表
            for idx, item in enumerate(inventory_data):
                with st.container():
                    col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
                    
                    with col_a:
                        st.write(f"**{item['product_name']}**")
                        st.caption(f"品牌: {item.get('brand_name', '未知')} | 分类: {item['category']}")
                    
                    with col_b:
                        st.write(f"数量: {item['quantity']}")
                    
                    with col_c:
                        status_color = {
                            'pending': '🟡',
                            'approved': '🟢',
                            'rejected': '🔴',
                            'sold': '⚫'
                        }
                        st.write(f"{status_color.get(item['status'], '⚪')} {item['status']}")
                    
                    with col_d:
                        if st.button("选择", key=f"select_inv_{item['id']}"):
                            st.session_state.selected_inventory_id = item['id']
                            st.rerun()
                    
                    st.divider()
        
        with col2:
            st.subheader("操作面板")
            
            if st.session_state.selected_inventory_id:
                # 获取选中的商品信息
                selected_item = None
                for item in inventory_data:
                    if item['id'] == st.session_state.selected_inventory_id:
                        selected_item = item
                        break
                
                if selected_item:
                    st.info(f"""
                    **选中商品:**
                    - 名称: {selected_item['product_name']}
                    - 数量: {selected_item['quantity']}
                    - 状态: {selected_item['status']}
                    """)
                    
                    # 修改功能
                    with st.expander("📝 修改商品", expanded=True):
                        new_name = st.text_input("商品名称", value=selected_item['product_name'])
                        new_quantity = st.number_input("数量", min_value=1, value=selected_item['quantity'])
                        
                        if st.button("确认修改", key="update_inventory"):
                            try:
                                success = manager.update_inventory(
                                    st.session_state.selected_inventory_id,
                                    product_name=new_name,
                                    quantity=new_quantity
                                )
                                
                                if success:
                                    st.success("✅ 修改成功！")
                                    st.session_state.selected_inventory_id = None
                                    st.rerun()
                                else:
                                    st.error("❌ 修改失败")
                            except Exception as e:
                                st.error(f"修改异常: {str(e)}")
                    
                    # 删除功能
                    with st.expander("🗑️ 删除商品", expanded=False):
                        confirm_delete = st.checkbox("确认删除此商品", key="confirm_delete_inv")
                        
                        if st.button("确认删除", key="delete_inventory", disabled=not confirm_delete):
                            try:
                                success = manager.delete_inventory(st.session_state.selected_inventory_id)
                                
                                if success:
                                    st.success("✅ 删除成功！")
                                    st.session_state.selected_inventory_id = None
                                    st.rerun()
                                else:
                                    st.error("❌ 删除失败")
                            except Exception as e:
                                st.error(f"删除异常: {str(e)}")
            else:
                st.info("请先选择一个商品进行操作")
    
    # 媒体资源管理模块
    elif selected_tab == "媒体资源管理":
        st.header("媒体资源管理")
        
        # 获取媒体数据
        conn = sqlite3.connect("inventory.db")
        try:
            media_df = pd.read_sql_query('SELECT * FROM media_resources ORDER BY created_at DESC', conn)
            
            if media_df.empty:
                st.warning("暂无媒体资源数据")
                return
            
            # 显示媒体列表
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader("媒体资源列表")
                
                if 'selected_media_id' not in st.session_state:
                    st.session_state.selected_media_id = None
                
                for idx, media in media_df.iterrows():
                    with st.container():
                        col_a, col_b, col_c = st.columns([2, 1, 1])
                        
                        with col_a:
                            st.write(f"**{media['media_name']}**")
                            st.caption(f"类型: {media['media_type']} | 位置: {media['location']}")
                        
                        with col_b:
                            st.write(f"刊例价: ¥{media['market_price']:,.0f}")
                        
                        with col_c:
                            if st.button("选择", key=f"select_media_{media['id']}"):
                                st.session_state.selected_media_id = media['id']
                                st.rerun()
                        
                        st.divider()
            
            with col2:
                st.subheader("操作面板")
                
                if st.session_state.selected_media_id:
                    selected_media = media_df[media_df['id'] == st.session_state.selected_media_id].iloc[0]
                    
                    st.info(f"""
                    **选中媒体:**
                    - 名称: {selected_media['media_name']}
                    - 类型: {selected_media['media_type']}
                    - 位置: {selected_media['location']}
                    """)
                    
                    # 修改功能
                    with st.expander("📝 修改媒体信息", expanded=True):
                        new_name = st.text_input("媒体名称", value=selected_media['media_name'])
                        new_location = st.text_input("位置", value=selected_media['location'])
                        new_price = st.number_input("刊例价", min_value=0.0, value=float(selected_media['market_price']))
                        
                        if st.button("确认修改", key="update_media"):
                            try:
                                success = manager.update_media_resource(
                                    st.session_state.selected_media_id,
                                    media_name=new_name,
                                    location=new_location,
                                    market_price=new_price
                                )
                                
                                if success:
                                    st.success("✅ 修改成功！")
                                    st.session_state.selected_media_id = None
                                    st.rerun()
                                else:
                                    st.error("❌ 修改失败")
                            except Exception as e:
                                st.error(f"修改异常: {str(e)}")
                    
                    # 删除功能
                    with st.expander("🗑️ 删除媒体", expanded=False):
                        confirm_delete = st.checkbox("确认删除此媒体", key="confirm_delete_media")
                        
                        if st.button("确认删除", key="delete_media", disabled=not confirm_delete):
                            try:
                                success = manager.delete_media_resource(st.session_state.selected_media_id)
                                
                                if success:
                                    st.success("✅ 删除成功！")
                                    st.session_state.selected_media_id = None
                                    st.rerun()
                                else:
                                    st.error("❌ 删除失败")
                            except Exception as e:
                                st.error(f"删除异常: {str(e)}")
                else:
                    st.info("请先选择一个媒体进行操作")
                    
        except Exception as e:
            st.error(f"查询媒体数据失败: {str(e)}")
        finally:
            conn.close()
    
    # 销售渠道管理模块
    elif selected_tab == "销售渠道管理":
        st.header("销售渠道管理")
        
        # 获取渠道数据
        conn = sqlite3.connect("inventory.db")
        try:
            channel_df = pd.read_sql_query('SELECT * FROM sales_channels ORDER BY created_at DESC', conn)
            
            if channel_df.empty:
                st.warning("暂无销售渠道数据")
                return
            
            # 显示渠道列表
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader("销售渠道列表")
                
                if 'selected_channel_id' not in st.session_state:
                    st.session_state.selected_channel_id = None
                
                for idx, channel in channel_df.iterrows():
                    with st.container():
                        col_a, col_b, col_c = st.columns([2, 1, 1])
                        
                        with col_a:
                            st.write(f"**{channel['channel_name']}**")
                            st.caption(f"类型: {channel['channel_type']} | 联系人: {channel['contact_person']}")
                        
                        with col_b:
                            st.write(f"佣金率: {channel['commission_rate']}%")
                        
                        with col_c:
                            if st.button("选择", key=f"select_channel_{channel['id']}"):
                                st.session_state.selected_channel_id = channel['id']
                                st.rerun()
                        
                        st.divider()
            
            with col2:
                st.subheader("操作面板")
                
                if st.session_state.selected_channel_id:
                    selected_channel = channel_df[channel_df['id'] == st.session_state.selected_channel_id].iloc[0]
                    
                    st.info(f"""
                    **选中渠道:**
                    - 名称: {selected_channel['channel_name']}
                    - 类型: {selected_channel['channel_type']}
                    - 联系人: {selected_channel['contact_person']}
                    """)
                    
                    # 修改功能
                    with st.expander("📝 修改渠道信息", expanded=True):
                        new_name = st.text_input("渠道名称", value=selected_channel['channel_name'])
                        new_type = st.text_input("渠道类型", value=selected_channel['channel_type'])
                        new_contact = st.text_input("联系人", value=selected_channel['contact_person'] or "")
                        
                        if st.button("确认修改", key="update_channel"):
                            try:
                                success = manager.update_sales_channel(
                                    st.session_state.selected_channel_id,
                                    channel_name=new_name,
                                    channel_type=new_type,
                                    contact_person=new_contact
                                )
                                
                                if success:
                                    st.success("✅ 修改成功！")
                                    st.session_state.selected_channel_id = None
                                    st.rerun()
                                else:
                                    st.error("❌ 修改失败")
                            except Exception as e:
                                st.error(f"修改异常: {str(e)}")
                    
                    # 删除功能
                    with st.expander("🗑️ 删除渠道", expanded=False):
                        confirm_delete = st.checkbox("确认删除此渠道", key="confirm_delete_channel")
                        
                        if st.button("确认删除", key="delete_channel", disabled=not confirm_delete):
                            try:
                                success = manager.delete_sales_channel(st.session_state.selected_channel_id)
                                
                                if success:
                                    st.success("✅ 删除成功！")
                                    st.session_state.selected_channel_id = None
                                    st.rerun()
                                else:
                                    st.error("❌ 删除失败")
                            except Exception as e:
                                st.error(f"删除异常: {str(e)}")
                else:
                    st.info("请先选择一个渠道进行操作")
                    
        except Exception as e:
            st.error(f"查询渠道数据失败: {str(e)}")
        finally:
            conn.close()
    
    # 品牌管理模块
    elif selected_tab == "品牌管理":
        st.header("品牌方管理")
        
        # 获取品牌数据
        brand_data = manager.get_all_brands()
        
        if not brand_data:
            st.warning("暂无品牌数据")
            return
        
        # 显示品牌列表
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("品牌列表")
            
            if 'selected_brand_id' not in st.session_state:
                st.session_state.selected_brand_id = None
            
            for brand in brand_data:
                with st.container():
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    
                    with col_a:
                        st.write(f"**{brand['brand_name']}**")
                        st.caption(f"类型: {brand.get('brand_type', '未知')} | 联系人: {brand.get('contact_person', '未知')}")
                    
                    with col_b:
                        st.write(f"信誉分: {brand.get('reputation_score', 0)}/10")
                    
                    with col_c:
                        if st.button("选择", key=f"select_brand_{brand['id']}"):
                            st.session_state.selected_brand_id = brand['id']
                            st.rerun()
                    
                    st.divider()
        
        with col2:
            st.subheader("操作面板")
            
            if st.session_state.selected_brand_id:
                selected_brand = None
                for brand in brand_data:
                    if brand['id'] == st.session_state.selected_brand_id:
                        selected_brand = brand
                        break
                
                if selected_brand:
                    st.info(f"""
                    **选中品牌:**
                    - 名称: {selected_brand['brand_name']}
                    - 联系人: {selected_brand.get('contact_person', '未知')}
                    - 信誉分: {selected_brand.get('reputation_score', 0)}/10
                    """)
                    
                    # 修改功能
                    with st.expander("📝 修改品牌信息", expanded=True):
                        new_name = st.text_input("品牌名称", value=selected_brand['brand_name'])
                        new_contact = st.text_input("联系人", value=selected_brand.get('contact_person', '') or "")
                        new_phone = st.text_input("联系电话", value=selected_brand.get('contact_phone', '') or "")
                        new_score = st.number_input("信誉评分", min_value=1, max_value=10, value=selected_brand.get('reputation_score', 5))
                        
                        if st.button("确认修改", key="update_brand"):
                            try:
                                success = manager.update_brand(
                                    st.session_state.selected_brand_id,
                                    brand_name=new_name,
                                    contact_person=new_contact,
                                    contact_phone=new_phone,
                                    reputation_score=new_score
                                )
                                
                                if success:
                                    st.success("✅ 修改成功！")
                                    st.session_state.selected_brand_id = None
                                    st.rerun()
                                else:
                                    st.error("❌ 修改失败")
                            except Exception as e:
                                st.error(f"修改异常: {str(e)}")
            else:
                st.info("请先选择一个品牌进行操作")
    
    # 数据概览模块
    elif selected_tab == "数据概览":
        st.header("数据概览")
        
        try:
            summary = manager.get_inventory_summary()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("库存统计")
                for stat in summary['inventory_stats']:
                    st.metric(
                        f"{stat['status']} 状态",
                        f"{stat['count']} 件",
                        f"¥{stat['total_value']:,.0f}"
                    )
            
            with col2:
                st.subheader("分类统计")
                for stat in summary['category_stats']:
                    st.metric(
                        stat['category'],
                        f"{stat['count']} 件",
                        f"¥{stat['total_value']:,.0f}"
                    )
            
            with col3:
                st.subheader("品牌统计")
                for stat in summary['brand_stats']:
                    if stat['inventory_count'] > 0:
                        st.metric(
                            stat['brand_name'],
                            f"{stat['inventory_count']} 件",
                            f"¥{stat['total_value']:,.0f}"
                        )
        
        except Exception as e:
            st.error(f"获取数据概览失败: {str(e)}")

def add_test_data(manager):
    """添加测试数据"""
    try:
        # 添加测试品牌
        brand_id = manager.add_brand("测试品牌", "测试联系人", "13800138000", brand_type="饮料", reputation_score=8)
        
        # 添加测试库存
        manager.add_inventory(
            brand_id=brand_id,
            product_name="测试商品",
            category="饮料",
            quantity=100,
            original_value=1000.0,
            market_value=800.0
        )
        
        # 添加测试媒体
        manager.add_media_resource(
            media_name="测试媒体",
            media_type="电视",
            location="测试地点",
            market_price=5000.0,
            contact_person="媒体联系人",
            contact_phone="13900139000"
        )
        
        # 添加测试渠道
        manager.add_sales_channel(
            channel_name="测试渠道",
            channel_type="超市",
            contact_person="渠道联系人",
            contact_phone="13700137000"
        )
        
        st.success("测试数据添加成功！")
        
    except Exception as e:
        st.error(f"添加测试数据失败: {str(e)}")

if __name__ == "__main__":
    main()