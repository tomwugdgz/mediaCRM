#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版应用程序测试 - 专注于删除和更新功能
"""

import streamlit as st
import pandas as pd
from inventory_manager import InventoryManager

# 初始化管理器
@st.cache_resource
def init_manager():
    return InventoryManager()

def main():
    st.title("库存管理测试 - 删除和更新功能")
    
    manager = init_manager()
    
    # 获取库存列表
    inventory_data = manager.get_all_inventory()
    
    if not inventory_data:
        st.warning("暂无库存数据")
        return
    
    inventory_df = pd.DataFrame(inventory_data)
    
    st.subheader(f"当前库存 ({len(inventory_data)} 件商品)")
    
    # 显示库存表格
    st.dataframe(inventory_df[['id', 'product_name', 'category', 'quantity', 'status']])
    
    # 选择要操作的商品
    selected_product = st.selectbox(
        "选择要操作的商品",
        inventory_df['product_name'].tolist()
    )
    
    if selected_product:
        product_info = inventory_df[inventory_df['product_name'] == selected_product].iloc[0]
        
        st.subheader(f"操作商品: {selected_product}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**当前信息**")
            st.write(f"ID: {product_info['id']}")
            st.write(f"名称: {product_info['product_name']}")
            st.write(f"数量: {product_info['quantity']}")
            st.write(f"品类: {product_info['category']}")
            st.write(f"状态: {product_info['status']}")
        
        with col2:
            st.write("**操作选项**")
            
            # 更新功能
            with st.form("update_form"):
                st.write("**更新商品信息**")
                new_name = st.text_input("商品名称", value=product_info['product_name'])
                new_quantity = st.number_input("数量", min_value=1, value=product_info['quantity'])
                
                if st.form_submit_button("更新商品", type="primary"):
                    try:
                        success = manager.update_inventory(
                            product_info['id'],
                            product_name=new_name,
                            quantity=new_quantity
                        )
                        
                        if success:
                            st.success(f"✅ 商品更新成功！")
                            st.rerun()
                        else:
                            st.error("❌ 商品更新失败")
                            
                    except Exception as e:
                        st.error(f"更新失败: {str(e)}")
            
            # 删除功能
            st.write("**删除商品**")
            
            # 添加确认机制，但简化操作
            if st.button("删除商品", type="secondary"):
                try:
                    # 直接删除，无需复杂确认
                    success = manager.delete_inventory(product_info['id'])
                    
                    if success:
                        st.success(f"✅ 商品删除成功！")
                        st.rerun()
                    else:
                        st.error("❌ 商品删除失败")
                        
                except Exception as e:
                    st.error(f"删除失败: {str(e)}")

if __name__ == "__main__":
    main()