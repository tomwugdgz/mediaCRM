#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改功能
验证库存和品牌修改功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inventory_manager import InventoryManager

def test_update_inventory():
    """测试修改库存功能"""
    print("🧪 测试修改库存功能...")
    
    manager = InventoryManager()
    
    # 首先添加一个测试品牌
    brand_id = manager.add_brand(
        brand_name="测试品牌",
        contact_person="测试联系人",
        contact_phone="13800138000",
        brand_type="饮料",
        reputation_score=8
    )
    
    # 添加测试库存
    inventory_id = manager.add_inventory(
        brand_id=brand_id,
        product_name="测试商品",
        category="饮料",
        quantity=100,
        original_value=5000.0,
        market_value=4500.0,
        expiry_date="2025-12-31",
        storage_location="仓库A"
    )
    
    print(f"✅ 添加测试库存，ID: {inventory_id}")
    
    # 获取原始数据
    original_data = manager.get_inventory_by_id(inventory_id)
    print(f"原始数据: {original_data}")
    
    # 测试修改功能
    success = manager.update_inventory(
        inventory_id,
        product_name="修改后的商品名称",
        quantity=150,
        original_value=5500.0,
        status="approved"
    )
    
    if success:
        print("✅ 库存修改成功")
        
        # 验证修改结果
        updated_data = manager.get_inventory_by_id(inventory_id)
        print(f"修改后数据: {updated_data}")
        
        # 检查修改是否正确
        checks = [
            updated_data['product_name'] == "修改后的商品名称",
            updated_data['quantity'] == 150,
            updated_data['original_value'] == 5500.0,
            updated_data['status'] == "approved"
        ]
        
        if all(checks):
            print("✅ 所有字段修改正确")
            return True
        else:
            print("❌ 字段修改不正确")
            return False
    else:
        print("❌ 库存修改失败")
        return False

def test_update_brand():
    """测试修改品牌功能"""
    print("\n🧪 测试修改品牌功能...")
    
    manager = InventoryManager()
    
    # 添加测试品牌
    brand_id = manager.add_brand(
        brand_name="原始品牌名称",
        contact_person="原始联系人",
        contact_phone="13900139000",
        contact_email="original@example.com",
        brand_type="日化",
        reputation_score=7
    )
    
    print(f"✅ 添加测试品牌，ID: {brand_id}")
    
    # 获取原始数据
    original_data = manager.get_brand_by_id(brand_id)
    print(f"原始数据: {original_data}")
    
    # 测试修改功能
    success = manager.update_brand(
        brand_id,
        brand_name="修改后的品牌名称",
        contact_person="修改后的联系人",
        contact_email="updated@example.com",
        reputation_score=9
    )
    
    if success:
        print("✅ 品牌修改成功")
        
        # 验证修改结果
        updated_data = manager.get_brand_by_id(brand_id)
        print(f"修改后数据: {updated_data}")
        
        # 检查修改是否正确
        checks = [
            updated_data['brand_name'] == "修改后的品牌名称",
            updated_data['contact_person'] == "修改后的联系人",
            updated_data['contact_email'] == "updated@example.com",
            updated_data['reputation_score'] == 9
        ]
        
        if all(checks):
            print("✅ 所有字段修改正确")
            return True
        else:
            print("❌ 字段修改不正确")
            return False
    else:
        print("❌ 品牌修改失败")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("🧪 修改功能测试")
    print("="*60)
    
    # 测试库存修改
    inventory_test_passed = test_update_inventory()
    
    # 测试品牌修改
    brand_test_passed = test_update_brand()
    
    print("\n" + "="*60)
    print("📊 测试结果总结:")
    print(f"库存修改功能: {'✅ 通过' if inventory_test_passed else '❌ 失败'}")
    print(f"品牌修改功能: {'✅ 通过' if brand_test_passed else '❌ 失败'}")
    
    if inventory_test_passed and brand_test_passed:
        print("\n🎉 所有修改功能测试通过！")
        return True
    else:
        print("\n❌ 部分功能测试失败！")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)