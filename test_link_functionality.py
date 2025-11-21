#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试商品链接功能
"""

import sqlite3
from inventory_manager import InventoryManager

def test_link_functionality():
    """测试商品链接功能"""
    print("🧪 测试商品链接功能...")
    
    # 创建管理器实例
    manager = InventoryManager()
    
    # 添加测试品牌
    brand_id = manager.add_brand("测试品牌", "测试联系人", "13800138000", "test@example.com", "饮料", 8)
    print(f"✅ 添加测试品牌，ID: {brand_id}")
    
    # 添加带链接的库存商品
    inventory_id = manager.add_inventory(
        brand_id=brand_id,
        product_name="测试商品",
        category="饮料",
        quantity=100,
        original_value=1000.0,
        market_value=800.0,
        expiry_date="2025-12-31",
        storage_location="仓库A",
        jd_link="https://item.jd.com/12345.html",
        tmall_link="https://detail.tmall.com/67890.htm",
        xianyu_link="https://2.taobao.com/abcde",
        pdd_link="https://mobile.yangkeduo.com/fghij.html"
    )
    print(f"✅ 添加测试商品，ID: {inventory_id}")
    
    # 获取商品信息
    inventory_info = manager.get_inventory_by_id(inventory_id)
    print(f"📋 商品信息:")
    print(f"  商品名称: {inventory_info['product_name']}")
    print(f"  品牌: {inventory_info['brand_name']}")
    print(f"  分类: {inventory_info['category']}")
    print(f"  数量: {inventory_info['quantity']}")
    print(f"  原价: ¥{inventory_info['original_value']}")
    print(f"  市场价: ¥{inventory_info['market_value']}")
    
    # 显示链接信息
    print(f"🔗 商品链接:")
    print(f"  京东: {inventory_info.get('jd_link', '无')}")
    print(f"  天猫: {inventory_info.get('tmall_link', '无')}")
    print(f"  闲鱼: {inventory_info.get('xianyu_link', '无')}")
    print(f"  拼多多: {inventory_info.get('pdd_link', '无')}")
    
    # 测试更新链接
    print("\n🔄 测试更新链接...")
    success = manager.update_inventory(
        inventory_id,
        jd_link="https://item.jd.com/54321.html",
        tmall_link=None,  # 清空天猫链接
        xianyu_link="https://2.taobao.com/newlink",
        pdd_link="https://mobile.yangkeduo.com/newpdd.html"
    )
    
    if success:
        print("✅ 链接更新成功")
        # 重新获取信息
        updated_info = manager.get_inventory_by_id(inventory_id)
        print(f"🔗 更新后的链接:")
        print(f"  京东: {updated_info.get('jd_link', '无')}")
        print(f"  天猫: {updated_info.get('tmall_link', '无')}")
        print(f"  闲鱼: {updated_info.get('xianyu_link', '无')}")
        print(f"  拼多多: {updated_info.get('pdd_link', '无')}")
    else:
        print("❌ 链接更新失败")
    
    # 测试删除功能
    print("\n🗑️ 测试删除功能...")
    delete_success = manager.delete_inventory(inventory_id)
    if delete_success:
        print("✅ 商品删除成功")
    else:
        print("❌ 商品删除失败")
    
    # 清理测试品牌
    manager.delete_brand(brand_id)
    print("✅ 测试品牌已清理")
    
    print("\n🎉 链接功能测试完成！")

if __name__ == "__main__":
    test_link_functionality()