#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库检查工具
用于检查数据库状态和数据完整性
"""

import sqlite3
import pandas as pd

def check_database():
    """检查数据库状态"""
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        print("🔍 数据库状态检查")
        print("=" * 50)
        
        # 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("📊 数据库中的表:")
        for table in tables:
            print(f"  📋 {table[0]}")
        
        print("\n📈 各表记录数:")
        # 检查每个表的记录数
        for table in tables:
            table_name = table[0]
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'  {table_name}: {count} 条记录')
        
        print("\n🛍️ 库存数据检查:")
        # 检查库存数据
        cursor.execute('SELECT id, product_name, status, original_value FROM inventory LIMIT 10')
        inventory_samples = cursor.fetchall()
        if inventory_samples:
            print("  库存样本数据:")
            for item in inventory_samples:
                print(f'    ID:{item[0]} | 商品:{item[1]} | 状态:{item[2]} | 价值:¥{item[3]}')
        else:
            print("  ⚠️ 库存表中没有数据")
        
        print("\n🏪 品牌和渠道检查:")
        # 检查品牌数据
        cursor.execute('SELECT COUNT(*) FROM brands')
        brand_count = cursor.fetchone()[0]
        print(f'  品牌数量: {brand_count}')
        
        # 检查销售渠道
        cursor.execute('SELECT COUNT(*) FROM sales_channels')
        channel_count = cursor.fetchone()[0]
        print(f'  销售渠道: {channel_count}')
        
        print("\n💰 交易数据检查:")
        # 检查交易数据
        cursor.execute('SELECT COUNT(*) FROM transactions')
        transaction_count = cursor.fetchone()[0]
        print(f'  交易记录: {transaction_count}')
        
        if transaction_count > 0:
            cursor.execute('SELECT id, product_name, sale_price, profit, transaction_date FROM transactions ORDER BY id DESC LIMIT 5')
            transactions = cursor.fetchall()
            print("  最近交易样本:")
            for trans in transactions:
                print(f'    ID:{trans[0]} | 商品:{trans[1]} | 售价:¥{trans[2]} | 利润:¥{trans[3]} | 日期:{trans[4]}')
        
        print("\n🔧 数据库完整性检查:")
        # 检查外键关系
        cursor.execute('''
            SELECT i.id, i.product_name, i.brand_id, b.brand_name
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            WHERE i.brand_id IS NOT NULL AND b.id IS NULL
            LIMIT 5
        ''')
        orphaned_inventory = cursor.fetchall()
        if orphaned_inventory:
            print("  ⚠️ 发现孤立的库存记录（品牌ID不存在）:")
            for item in orphaned_inventory:
                print(f'    库存ID:{item[0]} 商品:{item[1]} 无效品牌ID:{item[2]}')
        else:
            print("  ✅ 外键关系正常")
        
        # 检查交易记录的外键
        cursor.execute('''
            SELECT t.id, t.inventory_id, t.brand_id, t.channel_id
            FROM transactions t
            LEFT JOIN inventory i ON t.inventory_id = i.id
            WHERE t.inventory_id IS NOT NULL AND i.id IS NULL
            LIMIT 5
        ''')
        orphaned_transactions = cursor.fetchall()
        if orphaned_transactions:
            print("  ⚠️ 发现孤立的交易记录（库存ID不存在）:")
            for trans in orphaned_transactions:
                print(f'    交易ID:{trans[0]} 无效库存ID:{trans[1]}')
        else:
            print("  ✅ 交易外键关系正常")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("✅ 数据库检查完成")
        
        # 返回检查结果
        return {
            'tables': len(tables),
            'inventory_count': len(inventory_samples) if 'inventory_samples' in locals() else 0,
            'brand_count': brand_count,
            'channel_count': channel_count,
            'transaction_count': transaction_count,
            'has_orphaned_inventory': len(orphaned_inventory) > 0 if 'orphaned_inventory' in locals() else False,
            'has_orphaned_transactions': len(orphaned_transactions) > 0 if 'orphaned_transactions' in locals() else False
        }
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return None

if __name__ == "__main__":
    check_database()