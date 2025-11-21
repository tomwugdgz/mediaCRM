#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库修复工具
用于添加示例交易数据和修复数据问题
"""

import sqlite3
from datetime import datetime, timedelta
import random

def add_sample_transactions():
    """添加示例交易数据"""
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        print("🛠️ 添加示例交易数据")
        print("=" * 50)
        
        # 获取现有的库存、品牌、渠道和广告资源
        cursor.execute('SELECT id, brand_id FROM inventory WHERE status = "pending"')
        inventory_items = cursor.fetchall()
        
        cursor.execute('SELECT id FROM brands')
        brands = cursor.fetchall()
        
        cursor.execute('SELECT id FROM sales_channels')
        channels = cursor.fetchall()
        
        cursor.execute('SELECT id FROM media_resources WHERE status = "idle"')
        ad_resources = cursor.fetchall()
        
        if not inventory_items:
            print("⚠️ 没有待处理的库存项目")
            return False
            
        if not ad_resources:
            print("⚠️ 没有可用的广告资源")
            return False
            
        if not channels:
            print("⚠️ 没有销售渠道")
            return False
        
        # 添加示例交易数据
        sample_transactions = []
        base_date = datetime.now()
        
        for i, (inventory_id, brand_id) in enumerate(inventory_items[:3]):  # 限制为3个交易
            # 获取库存详细信息
            cursor.execute('SELECT original_value, quantity, product_name FROM inventory WHERE id = ?', (inventory_id,))
            inventory_info = cursor.fetchone()
            if not inventory_info:
                continue
                
            original_value, quantity, product_name = inventory_info
            
            # 随机选择广告资源和渠道
            ad_resource_id = random.choice(ad_resources)[0]
            channel_id = random.choice(channels)[0]
            
            # 计算交易数据
            sale_price = original_value * random.uniform(0.6, 1.2)  # 售价在原价值的60%-120%之间
            ad_value = sale_price * random.uniform(0.2, 0.4)  # 广告价值占售价的20%-40%
            inventory_value = original_value * 0.8  # 库存价值
            profit = sale_price - ad_value - inventory_value  # 利润
            
            # 随机日期（最近30天内）
            days_ago = random.randint(1, 30)
            transaction_date = base_date - timedelta(days=days_ago)
            
            # 创建交易记录
            transaction = {
                'inventory_id': inventory_id,
                'ad_resource_id': ad_resource_id,
                'brand_id': brand_id,
                'channel_id': channel_id,
                'transaction_type': 'sale',
                'ad_value': round(ad_value, 2),
                'inventory_value': round(inventory_value, 2),
                'sale_price': round(sale_price, 2),
                'profit': round(profit, 2),
                'transaction_date': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'completed',
                'notes': f'示例交易 - {product_name}'
            }
            
            sample_transactions.append(transaction)
        
        # 插入交易数据
        for trans in sample_transactions:
            cursor.execute('''
                INSERT INTO transactions 
                (inventory_id, ad_resource_id, brand_id, channel_id, transaction_type, 
                 ad_value, inventory_value, sale_price, profit, transaction_date, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trans['inventory_id'], trans['ad_resource_id'], trans['brand_id'], 
                trans['channel_id'], trans['transaction_type'], trans['ad_value'], 
                trans['inventory_value'], trans['sale_price'], trans['profit'], 
                trans['transaction_date'], trans['status'], trans['notes']
            ))
            
            # 更新库存状态为已售
            cursor.execute('UPDATE inventory SET status = "sold" WHERE id = ?', (trans['inventory_id'],))
            
            print(f"✅ 添加交易: {trans['notes']} - 利润:¥{trans['profit']}")
        
        conn.commit()
        conn.close()
        
        print(f"\n📊 已添加 {len(sample_transactions)} 条示例交易记录")
        print("✅ 数据库修复完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据库修复失败: {e}")
        return False

def reset_inventory_status():
    """重置库存状态为pending"""
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        print("🔄 重置库存状态")
        cursor.execute('UPDATE inventory SET status = "pending" WHERE status = "sold"')
        updated_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ 已重置 {updated_count} 条库存记录状态为pending")
        return True
        
    except Exception as e:
        print(f"❌ 重置失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 数据库修复工具")
    print("=" * 50)
    
    # 首先重置库存状态
    reset_inventory_status()
    
    # 然后添加示例交易数据
    success = add_sample_transactions()
    
    if success:
        print("\n🎉 数据库修复成功！")
        print("现在可以正常使用财务分析功能了")
    else:
        print("\n⚠️ 数据库修复遇到问题，请检查错误信息")

if __name__ == "__main__":
    main()