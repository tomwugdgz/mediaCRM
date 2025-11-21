#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试删除功能
"""

from inventory_manager import InventoryManager

def test_delete_functionality():
    """测试删除功能"""
    print("=== 测试删除功能 ===")
    
    manager = InventoryManager()
    
    # 获取当前库存列表
    inventory_list = manager.get_all_inventory()
    print(f"当前库存数量: {len(inventory_list)}")
    
    if not inventory_list:
        print("❌ 没有库存数据")
        return
    
    # 选择最后一个库存进行测试删除
    test_item = inventory_list[-1]
    test_id = test_item['id']
    test_name = test_item['product_name']
    
    print(f"准备删除库存: ID={test_id}, 名称={test_name}")
    
    # 测试删除
    try:
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
                
        else:
            print(f"❌ 删除失败: ID={test_id}")
            
    except Exception as e:
        print(f"❌ 删除时发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

def test_update_functionality():
    """测试更新功能"""
    print("\n=== 测试更新功能 ===")
    
    manager = InventoryManager()
    
    # 获取当前库存列表
    inventory_list = manager.get_all_inventory()
    
    if not inventory_list:
        print("❌ 没有库存数据")
        return
    
    # 选择第一个库存进行测试更新
    test_item = inventory_list[0]
    test_id = test_item['id']
    test_name = test_item['product_name']
    
    print(f"准备更新库存: ID={test_id}, 当前名称={test_name}")
    
    # 测试更新
    try:
        success = manager.update_inventory(
            test_id,
            product_name="测试更新后的商品名称",
            quantity=999
        )
        
        if success:
            print(f"✅ 更新成功: ID={test_id}")
            
            # 验证更新
            updated_item = manager.get_inventory_by_id(test_id)
            if updated_item:
                print(f"更新后信息: 名称={updated_item['product_name']}, 数量={updated_item['quantity']}")
            else:
                print(f"❌ 更新验证失败: 无法获取更新后的数据")
                
        else:
            print(f"❌ 更新失败: ID={test_id}")
            
    except Exception as e:
        print(f"❌ 更新时发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_update_functionality()
    test_delete_functionality()