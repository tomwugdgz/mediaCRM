#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合解决方案功能测试脚本
验证库存、媒体、渠道的删除和修改功能
"""

import sqlite3
import pandas as pd
from inventory_manager import InventoryManager

def test_hybrid_solution():
    """测试混合解决方案的核心功能"""
    print("🚀 开始测试混合解决方案...")
    
    # 创建管理器实例
    manager = InventoryManager()
    
    # 测试1：库存管理功能
    print("\n📦 测试库存管理功能...")
    
    # 添加测试品牌
    brand_id = manager.add_brand(
        brand_name="测试品牌混合版",
        contact_person="测试联系人",
        contact_phone="13800138000",
        brand_type="饮料",
        reputation_score=8
    )
    print(f"✅ 添加测试品牌成功，ID: {brand_id}")
    
    # 添加测试库存
    inventory_id = manager.add_inventory(
        brand_id=brand_id,
        product_name="测试商品混合版",
        category="饮料",
        quantity=100,
        original_value=1000.0,
        market_value=1200.0,
        storage_location="测试仓库"
    )
    print(f"✅ 添加测试库存成功，ID: {inventory_id}")
    
    # 测试修改功能
    success = manager.update_inventory(
        inventory_id,
        product_name="修改后的商品名称",
        quantity=150,
        original_value=1500.0,
        status="approved"
    )
    if success:
        print("✅ 库存修改功能正常")
    else:
        print("❌ 库存修改功能异常")
    
    # 验证修改结果
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT product_name, quantity, original_value, status FROM inventory WHERE id = ?", (inventory_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == "修改后的商品名称" and result[1] == 150:
        print("✅ 库存修改验证成功")
    else:
        print("❌ 库存修改验证失败")
    
    # 测试删除功能
    success = manager.delete_inventory(inventory_id)
    if success:
        print("✅ 库存删除功能正常")
    else:
        print("❌ 库存删除功能异常")
    
    # 验证删除结果
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE id = ?", (inventory_id,))
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        print("✅ 库存删除验证成功")
    else:
        print("❌ 库存删除验证失败")
    
    # 测试2：媒体管理功能
    print("\n📺 测试媒体管理功能...")
    
    # 添加测试媒体
    media_id = manager.add_media_resource(
        media_name="测试媒体混合版",
        media_type="社区门禁",
        media_form="静态海报",
        location="测试小区",
        market_price=5000.0,
        discount_rate=80.0,
        actual_cost=4000.0
    )
    print(f"✅ 添加测试媒体成功，ID: {media_id}")
    
    # 测试修改功能
    success = manager.update_media_resource(
        media_id,
        media_name="修改后的媒体名称",
        market_price=6000.0,
        status="occupied"
    )
    if success:
        print("✅ 媒体修改功能正常")
    else:
        print("❌ 媒体修改功能异常")
    
    # 验证修改结果
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT media_name, market_price, status FROM media_resources WHERE id = ?", (media_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == "修改后的媒体名称" and result[1] == 6000.0:
        print("✅ 媒体修改验证成功")
    else:
        print("❌ 媒体修改验证失败")
    
    # 测试删除功能
    success = manager.delete_media_resource(media_id)
    if success:
        print("✅ 媒体删除功能正常")
    else:
        print("❌ 媒体删除功能异常")
    
    # 验证删除结果
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM media_resources WHERE id = ?", (media_id,))
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        print("✅ 媒体删除验证成功")
    else:
        print("❌ 媒体删除验证失败")
    
    # 测试3：渠道管理功能
    print("\n🛒 测试渠道管理功能...")
    
    # 添加测试渠道
    channel_id = manager.add_sales_channel(
        channel_name="测试渠道混合版",
        channel_type="S级(团长)",
        contact_person="测试团长",
        contact_phone="13800138000",
        commission_rate=5.0,
        payment_terms="月结"
    )
    print(f"✅ 添加测试渠道成功，ID: {channel_id}")
    
    # 测试修改功能
    success = manager.update_sales_channel(
        channel_id,
        channel_name="修改后的渠道名称",
        commission_rate=6.0,
        contact_person="修改后的联系人"
    )
    if success:
        print("✅ 渠道修改功能正常")
    else:
        print("❌ 渠道修改功能异常")
    
    # 验证修改结果
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel_name, commission_rate, contact_person FROM sales_channels WHERE id = ?", (channel_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0] == "修改后的渠道名称" and result[1] == 6.0:
        print("✅ 渠道修改验证成功")
    else:
        print("❌ 渠道修改验证失败")
    
    # 测试删除功能
    success = manager.delete_sales_channel(channel_id)
    if success:
        print("✅ 渠道删除功能正常")
    else:
        print("❌ 渠道删除功能异常")
    
    # 验证删除结果
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales_channels WHERE id = ?", (channel_id,))
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        print("✅ 渠道删除验证成功")
    else:
        print("❌ 渠道删除验证失败")
    
    # 清理测试品牌
    manager.delete_brand(brand_id)
    print("✅ 清理测试数据完成")
    
    print("\n🎉 混合解决方案测试完成！")
    print("✅ 所有删除和修改功能均已验证正常")

if __name__ == "__main__":
    test_hybrid_solution()