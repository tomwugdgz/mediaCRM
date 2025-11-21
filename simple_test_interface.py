#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试界面 - 验证删除和修改功能
"""

import streamlit as st
import pandas as pd
import sqlite3
from inventory_manager import InventoryManager

def main():
    st.title("🔧 简化测试界面 - 验证删除和修改功能")
    
    # 创建管理器
    manager = InventoryManager()
    
    st.header("当前库存数据")
    
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
            st.warning("暂无库存数据，请先添加一些数据")
            # 添加测试数据
            if st.button("添加测试数据"):
                try:
                    # 添加品牌
                    brand_id = manager.add_brand("测试品牌", "测试联系人", "13800138000")
                    # 添加库存
                    inventory_id = manager.add_inventory(
                        brand_id=brand_id,
                        product_name="测试商品",
                        category="饮料",
                        quantity=100,
                        original_value=1000.0
                    )
                    st.success(f"添加测试数据成功！库存ID: {inventory_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"添加测试数据失败: {str(e)}")
            return
        
        # 显示数据
        st.dataframe(inventory_df)
        
        st.header("测试操作")
        
        # 选择商品
        selected_product = st.selectbox(
            "选择要操作的商品",
            inventory_df['product_name'].tolist()
        )
        
        if selected_product:
            product_info = inventory_df[inventory_df['product_name'] == selected_product].iloc[0]
            product_id = int(product_info['id'])
            
            st.info(f"""
            **选中商品信息:**
            - ID: {product_id}
            - 名称: {product_info['product_name']}
            - 数量: {product_info['quantity']}
            - 状态: {product_info['status']}
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("测试更新功能")
                
                new_name = st.text_input("新商品名称", value=product_info['product_name'])
                new_quantity = st.number_input("新数量", min_value=1, value=int(product_info['quantity']))
                
                if st.button("执行更新", key="test_update"):
                    try:
                        st.write(f"正在更新 ID: {product_id}")
                        success = manager.update_inventory(
                            product_id,
                            product_name=new_name,
                            quantity=new_quantity
                        )
                        
                        if success:
                            st.success("✅ 更新成功！")
                            st.balloons()
                            # 强制刷新数据
                            st.rerun()
                        else:
                            st.error("❌ 更新失败")
                            
                    except Exception as e:
                        st.error(f"更新异常: {str(e)}")
                        st.code(str(e))
            
            with col2:
                st.subheader("测试删除功能")
                
                confirm_delete = st.checkbox("确认删除此商品")
                
                if st.button("执行删除", key="test_delete", disabled=not confirm_delete):
                    try:
                        st.write(f"正在删除 ID: {product_id}")
                        success = manager.delete_inventory(product_id)
                        
                        if success:
                            st.success("✅ 删除成功！")
                            st.balloons()
                            # 强制刷新数据
                            st.rerun()
                        else:
                            st.error("❌ 删除失败")
                            
                    except Exception as e:
                        st.error(f"删除异常: {str(e)}")
                        st.code(str(e))
            
            st.header("直接数据库验证")
            
            if st.button("检查数据库状态"):
                try:
                    # 直接查询数据库
                    check_df = pd.read_sql_query(f'SELECT * FROM inventory WHERE id = {product_id}', conn)
                    if check_df.empty:
                        st.success("✅ 商品已从数据库中删除")
                    else:
                        st.info("商品仍然存在，当前数据:")
                        st.dataframe(check_df)
                except Exception as e:
                    st.error(f"数据库查询异常: {str(e)}")
                    
    except Exception as e:
        st.error(f"数据库查询异常: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()