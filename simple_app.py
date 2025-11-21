#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版广告置换库存管理系统
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="广告置换库存管理系统",
    page_icon="📊",
    layout="wide"
)

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # 创建库存表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT,
            quantity INTEGER,
            original_value REAL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建品牌表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL,
            contact_person TEXT,
            contact_phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def main():
    """主函数"""
    st.title("📊 广告置换库存管理系统")
    
    # 初始化数据库
    init_database()
    
    # 侧边栏导航
    st.sidebar.title("导航系统")
    
    menu = st.sidebar.radio("选择功能", ["系统概览", "库存管理", "品牌管理"])
    
    if menu == "系统概览":
        show_dashboard()
    elif menu == "库存管理":
        show_inventory()
    elif menu == "品牌管理":
        show_brands()

def show_dashboard():
    """显示系统概览"""
    st.header("🏠 系统概览")
    
    conn = sqlite3.connect("inventory.db")
    
    # 统计信息
    inventory_count = pd.read_sql_query("SELECT COUNT(*) as count FROM inventory", conn).iloc[0]['count']
    brand_count = pd.read_sql_query("SELECT COUNT(*) as count FROM brands", conn).iloc[0]['count']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("库存商品总数", f"{inventory_count} 件")
    
    with col2:
        st.metric("合作品牌数", f"{brand_count} 个")
    
    # 最近库存
    st.subheader("最近库存")
    recent_inventory = pd.read_sql_query(
        "SELECT * FROM inventory ORDER BY created_at DESC LIMIT 5", 
        conn
    )
    
    if not recent_inventory.empty:
        st.dataframe(recent_inventory)
    else:
        st.info("暂无库存数据")
    
    conn.close()

def show_inventory():
    """显示库存管理"""
    st.header("📦 库存管理")
    
    tab1, tab2 = st.tabs(["库存列表", "添加库存"])
    
    with tab1:
        show_inventory_list()
    
    with tab2:
        show_add_inventory()

def show_inventory_list():
    """显示库存列表"""
    st.subheader("库存列表")
    
    conn = sqlite3.connect("inventory.db")
    inventory_df = pd.read_sql_query("SELECT * FROM inventory ORDER BY created_at DESC", conn)
    conn.close()
    
    if not inventory_df.empty:
        st.dataframe(inventory_df)
    else:
        st.info("暂无库存数据")

def show_add_inventory():
    """显示添加库存"""
    st.subheader("添加库存")
    
    with st.form("add_inventory"):
        product_name = st.text_input("商品名称")
        category = st.selectbox("商品品类", ["饮料", "日化", "家电", "食品", "其他"])
        quantity = st.number_input("数量", min_value=1, value=100)
        original_value = st.number_input("原始价值 (元)", min_value=0.0, value=1000.0)
        
        submitted = st.form_submit_button("添加库存")
        
        if submitted and product_name:
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO inventory (product_name, category, quantity, original_value)
                VALUES (?, ?, ?, ?)
            ''', (product_name, category, quantity, original_value))
            conn.commit()
            conn.close()
            
            st.success("库存添加成功！")
            st.rerun()

def show_brands():
    """显示品牌管理"""
    st.header("🏢 品牌管理")
    
    tab1, tab2 = st.tabs(["品牌列表", "添加品牌"])
    
    with tab1:
        show_brand_list()
    
    with tab2:
        show_add_brand()

def show_brand_list():
    """显示品牌列表"""
    st.subheader("品牌列表")
    
    conn = sqlite3.connect("inventory.db")
    brands_df = pd.read_sql_query("SELECT * FROM brands ORDER BY created_at DESC", conn)
    conn.close()
    
    if not brands_df.empty:
        st.dataframe(brands_df)
    else:
        st.info("暂无品牌数据")

def show_add_brand():
    """显示添加品牌"""
    st.subheader("添加品牌")
    
    with st.form("add_brand"):
        brand_name = st.text_input("品牌名称")
        contact_person = st.text_input("联系人")
        contact_phone = st.text_input("联系电话")
        
        submitted = st.form_submit_button("添加品牌")
        
        if submitted and brand_name:
            conn = sqlite3.connect("inventory.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO brands (brand_name, contact_person, contact_phone)
                VALUES (?, ?, ?)
            ''', (brand_name, contact_person, contact_phone))
            conn.commit()
            conn.close()
            
            st.success("品牌添加成功！")
            st.rerun()

if __name__ == "__main__":
    main()