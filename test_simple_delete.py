#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试删除功能
"""

from inventory_manager import InventoryManager

def test_simple_delete():
    """简单测试删除功能"""
    print("=== 简单测试删除功能 ===")
    
    manager = InventoryManager()
    
    # 获取当前库存列表
    inventory_list = manager.get_all_inventory()
    print(f"当前库存数量: {len(inventory_list)}")
    
    if not inventory_list:
        print("❌ 没有库存数据，先添加一些测试数据")
        # 添加测试数据
        brand_id = manager.add_brand("测试品牌", "测试联系人", "13800138000")
        inventory_id = manager.add_inventory(
            brand_id=brand_id,
            product_name="测试商品",
            category="饮料",
            quantity=100,
            original_value=1000.0
        )
        print(f"✅ 添加测试数据: ID={inventory_id}")
        inventory_list = manager.get_all_inventory()
    
    # 选择第一个库存进行测试删除
    test_item = inventory_list[0]
    test_id = test_item['id']
    test_name = test_item['product_name']
    
    print(f"准备删除库存: ID={test_id}, 名称={test_name}")
    
    # 测试删除
    success = manager.delete_inventory(test_id)
    if success:
        print(f"✅ 删除成功: ID={test_id}")
        
        # 验证删除
        remaining_list = manager.get_all_inventory()
        print(f"删除后库存数量: {len(remaining_list)}")
        
        # 检查是否真的没有这个ID了
        deleted_item = manager.get_inventory_by_id(test_id)
        if deleted_item is None:
            print(f"✅ 确认删除: ID={test_id} 已不存在")
        else:
            print(f"❌ 删除验证失败: ID={test_id} 仍然存在")
            print(f"仍然存在的数据: {deleted_item}")
            
    else:
        print(f"❌ 删除失败: ID={test_id}")

if __name__ == "__main__":
    test_simple_delete()