#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit应用调试版本 - 用于排查删除和修改功能问题
"""

import streamlit as st
import pandas as pd
import sqlite3
from inventory_manager import InventoryManager
import traceback

# 页面配置
st.set_page_config(
    page_title="广告置换库存管理系统 - 调试版",
    page_icon="🔧",
    layout="wide"
)

def debug_inventory_operations():
    """调试库存操作功能"""
    st.header("🔧 调试库存操作功能")
    
    # 获取库存数据
    conn = sqlite3.connect("inventory.db")
    try:
        inventory_df = pd.read_sql_query('''
            SELECT i.*, b.brand_name 
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            ORDER BY i.created_at DESC
        ''', conn)
        
        st.write(f"库存数据数量: {len(inventory_df)}")
        
        if inventory_df.empty:
            st.info("暂无库存数据")
            return
        
        # 显示原始数据
        with st.expander("查看原始数据"):
            st.dataframe(inventory_df)
        
        # 选择要操作的商品
        selected_product = st.selectbox(
            "选择要操作的商品",
            inventory_df['product_name'].tolist(),
            key="debug_inventory_select"
        )
        
        if selected_product:
            product_info = inventory_df[inventory_df['product_name'] == selected_product].iloc[0]
            
            st.write("**选中商品信息:**")
            st.json({
                'id': int(product_info['id']),
                'product_name': product_info['product_name'],
                'quantity': int(product_info['quantity']),
                'status': product_info['status']
            })
            
            # 创建管理器实例
            manager = InventoryManager()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("测试更新功能")
                new_name = st.text_input("新商品名称", value=product_info['product_name'], key="debug_new_name")
                new_quantity = st.number_input("新数量", min_value=1, value=int(product_info['quantity']), key="debug_new_qty")
                
                if st.button("测试更新", key="debug_test_update"):
                    try:
                        st.write(f"尝试更新 ID: {product_info['id']}")
                        st.write(f"新名称: {new_name}")
                        st.write(f"新数量: {new_quantity}")
                        
                        success = manager.update_inventory(
                            int(product_info['id']),
                            product_name=new_name,
                            quantity=new_quantity
                        )
                        
                        if success:
                            st.success("✅ 更新成功！")
                            st.write("请手动刷新页面查看结果")
                        else:
                            st.error("❌ 更新失败")
                            
                    except Exception as e:
                        st.error(f"更新异常: {str(e)}")
                        st.code(traceback.format_exc())
            
            with col2:
                st.subheader("测试删除功能")
                confirm_delete = st.checkbox("确认删除此商品", key="debug_confirm_delete")
                
                if st.button("测试删除", key="debug_test_delete", disabled=not confirm_delete):
                    try:
                        st.write(f"尝试删除 ID: {product_info['id']}")
                        
                        success = manager.delete_inventory(int(product_info['id']))
                        
                        if success:
                            st.success("✅ 删除成功！")
                            st.write("请手动刷新页面查看结果")
                        else:
                            st.error("❌ 删除失败")
                            
                    except Exception as e:
                        st.error(f"删除异常: {str(e)}")
                        st.code(traceback.format_exc())
            
            with col3:
                st.subheader("直接数据库操作")
                
                if st.button("直接SQL更新", key="debug_direct_sql"):
                    try:
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE inventory 
                            SET product_name = ?, quantity = ?, updated_at = CURRENT_TIMESTAMP 
                            WHERE id = ?
                        ''', (f"直接更新_{product_info['product_name']}", 999, int(product_info['id'])))
                        conn.commit()
                        
                        affected_rows = cursor.rowcount
                        st.success(f"✅ SQL更新成功，影响行数: {affected_rows}")
                        
                    except Exception as e:
                        st.error(f"SQL更新异常: {str(e)}")
                
                if st.button("直接SQL删除", key="debug_direct_sql_delete"):
                    try:
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM inventory WHERE id = ?', (int(product_info['id']),))
                        conn.commit()
                        
                        affected_rows = cursor.rowcount
                        st.success(f"✅ SQL删除成功，影响行数: {affected_rows}")
                        
                    except Exception as e:
                        st.error(f"SQL删除异常: {str(e)}")

    except Exception as e:
        st.error(f"数据库查询异常: {str(e)}")
        st.code(traceback.format_exc())
    finally:
        conn.close()

def debug_session_state():
    """调试Streamlit会话状态"""
    st.header("🔧 Streamlit会话状态调试")
    
    st.write("当前会话状态:")
    st.json(st.session_state.to_dict())
    
    if st.button("清除会话状态"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("会话状态已清除")
        st.rerun()

if __name__ == "__main__":
    st.title("广告置换库存管理系统 - 调试模式")
    
    tab1, tab2 = st.tabs(["库存操作调试", "会话状态调试"])
    
    with tab1:
        debug_inventory_operations()
    
    with tab2:
        debug_session_state()