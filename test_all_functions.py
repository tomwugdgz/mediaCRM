#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有功能的综合测试脚本
"""

from inventory_manager import InventoryManager

def test_comprehensive_functionality():
    """综合测试所有功能"""
    print("=== 综合功能测试 ===")
    
    manager = InventoryManager()
    
    # 测试1: 添加测试数据
    print("\n1. 添加测试数据...")
    brand_id = manager.add_brand("测试品牌综合", "测试联系人", "13800138000", "test@example.com", "饮料", 8)
    print(f"✅ 添加品牌: ID={brand_id}")
    
    inventory_id = manager.add_inventory(
        brand_id=brand_id,
        product_name="测试商品综合",
        category="饮料",
        quantity=100,
        original_value=1000.0,
        market_value=800.0,
        storage_location="仓库A"
    )
    print(f"✅ 添加库存: ID={inventory_id}")
    
    media_id = manager.add_media_resource(
        media_name="测试媒体资源",
        media_type="社区门禁",
        location="测试小区",
        market_price=5000.0,
        actual_cost=2000.0
    )
    print(f"✅ 添加媒体资源: ID={media_id}")
    
    channel_id = manager.add_sales_channel(
        channel_name="测试渠道",
        channel_type="S级(团长)",
        contact_person="测试团长",
        contact_phone="13900139000",
        commission_rate=5.0,
        payment_terms="现结"
    )
    print(f"✅ 添加销售渠道: ID={channel_id}")
    
    # 测试2: 更新功能
    print("\n2. 测试更新功能...")
    
    # 更新库存
    inventory_success = manager.update_inventory(
        inventory_id,
        product_name="更新后的商品名称",
        quantity=200,
        status="approved"
    )
    print(f"{'✅' if inventory_success else '❌'} 库存更新: {inventory_success}")
    
    # 更新媒体资源
    media_success = manager.update_media_resource(
        media_id,
        media_name="更新后的媒体资源",
        market_price=6000.0,
        status="occupied"
    )
    print(f"{'✅' if media_success else '❌'} 媒体资源更新: {media_success}")
    
    # 更新销售渠道
    channel_success = manager.update_sales_channel(
        channel_id,
        channel_name="更新后的渠道",
        commission_rate=6.0
    )
    print(f"{'✅' if channel_success else '❌'} 销售渠道更新: {channel_success}")
    
    # 测试3: 删除功能
    print("\n3. 测试删除功能...")
    
    # 删除库存
    inventory_delete_success = manager.delete_inventory(inventory_id)
    print(f"{'✅' if inventory_delete_success else '❌'} 库存删除: {inventory_delete_success}")
    
    # 删除媒体资源
    media_delete_success = manager.delete_media_resource(media_id)
    print(f"{'✅' if media_delete_success else '❌'} 媒体资源删除: {media_delete_success}")
    
    # 删除销售渠道
    channel_delete_success = manager.delete_sales_channel(channel_id)
    print(f"{'✅' if channel_delete_success else '❌'} 销售渠道删除: {channel_delete_success}")
    
    # 测试4: 验证删除
    print("\n4. 验证删除结果...")
    
    # 检查库存是否已删除
    remaining_inventory = manager.get_inventory_by_id(inventory_id)
    print(f"{'✅' if remaining_inventory is None else '❌'} 库存验证删除: {remaining_inventory is None}")
    
    # 检查品牌是否还存在（品牌删除需要没有关联库存）
    remaining_brand = manager.get_brand_by_id(brand_id)
    print(f"{'✅' if remaining_brand is not None else '❌'} 品牌仍然存在: {remaining_brand is not None}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_comprehensive_functionality()