#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试应用程序启动问题
"""

import sqlite3
import pandas as pd

def debug_inventory_ids():
    """检查数据库中的库存ID"""
    print("=== 调试库存ID ===")
    
    conn = sqlite3.connect("inventory.db")
    try:
        # 获取所有库存ID
        inventory_df = pd.read_sql_query("SELECT id, product_name FROM inventory ORDER BY id", conn)
        print("当前库存记录:")
        print(inventory_df)
        
        # 检查特定的ID 17
        id_17_df = pd.read_sql_query("SELECT * FROM inventory WHERE id = 17", conn)
        if id_17_df.empty:
            print("❌ ID 17 不存在")
        else:
            print("✅ ID 17 存在:")
            print(id_17_df)
            
        # 获取最大ID
        max_id_df = pd.read_sql_query("SELECT MAX(id) as max_id FROM inventory", conn)
        max_id = max_id_df.iloc[0]['max_id'] if not max_id_df.empty else 0
        print(f"最大库存ID: {max_id}")
        
    finally:
        conn.close()

def debug_app_initialization():
    """调试应用程序初始化"""
    print("\n=== 调试应用程序初始化 ===")
    
    try:
        from inventory_manager import InventoryManager
        from pricing_calculator import PricingCalculator
        from financial_calculator import FinancialCalculator
        
        print("正在初始化管理器...")
        inventory_manager = InventoryManager()
        pricing_calculator = PricingCalculator()
        financial_calculator = FinancialCalculator()
        
        print("✅ 管理器初始化成功")
        
        # 检查哪些函数可能被自动调用
        print("\n检查库存概览...")
        summary = inventory_manager.get_inventory_summary()
        print("库存概览:", summary)
        
        # 检查是否有待处理库存
        conn = sqlite3.connect("inventory.db")
        try:
            pending_df = pd.read_sql_query("SELECT id, product_name FROM inventory WHERE status = 'pending'", conn)
            print(f"待处理库存数量: {len(pending_df)}")
            if not pending_df.empty:
                print("待处理库存:")
                print(pending_df)
                
                # 尝试获取第一个待处理库存的定价
                first_id = pending_df.iloc[0]['id']
                print(f"\n尝试获取ID {first_id} 的定价信息...")
                pricing_result = pricing_calculator.calculate_realization_value(first_id)
                print("定价结果:", pricing_result)
        finally:
            conn.close()
            
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_inventory_ids()
    debug_app_initialization()