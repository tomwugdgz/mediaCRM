#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试库存商品信息更新修复
验证各种边界情况和错误处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inventory_manager import InventoryManager

def test_inventory_update_edge_cases():
    """测试库存更新的边界情况"""
    print("🧪 测试库存更新边界情况...")
    
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
        storage_location="仓库A",
        jd_link="https://item.jd.com/123.html",
        tmall_link="https://detail.tmall.com/456.html"
    )
    
    print(f"✅ 添加测试库存，ID: {inventory_id}")
    
    # 测试1: 更新为None值
    print("\n1. 测试更新链接为None值...")
    success = manager.update_inventory(
        inventory_id,
        jd_link=None,
        tmall_link=None,
        xianyu_link=None,
        pdd_link=None
    )
    print(f"{'✅' if success else '❌'} 更新None值链接: {'成功' if success else '失败'}")
    
    # 测试2: 更新空字符串（应该转换为None）
    print("\n2. 测试更新空字符串...")
    success = manager.update_inventory(
        inventory_id,
        storage_location="",
        jd_link=""
    )
    print(f"{'✅' if success else '❌'} 更新空字符串: {'成功' if success else '失败'}")
    
    # 测试3: 更新负数值（应该被拒绝）
    print("\n3. 测试更新负数值...")
    success = manager.update_inventory(
        inventory_id,
        quantity=-10,
        original_value=-1000.0
    )
    print(f"{'✅' if not success else '❌'} 负数值被拒绝: {'正确' if not success else '错误'}")
    
    # 测试4: 更新无效数据类型
    print("\n4. 测试更新无效数据类型...")
    success = manager.update_inventory(
        inventory_id,
        quantity="invalid_number",
        original_value="not_a_number"
    )
    print(f"{'✅' if not success else '❌'} 无效数据类型被拒绝: {'正确' if not success else '错误'}")
    
    # 测试5: 更新到有效值
    print("\n5. 测试更新到有效值...")
    success = manager.update_inventory(
        inventory_id,
        product_name="更新后的商品名称",
        quantity=200,
        original_value=7500.0,
        market_value=6000.0,
        status="approved",
        storage_location="仓库B",
        jd_link="https://item.jd.com/789.html",
        xianyu_link="https://2.taobao.com/abc"
    )
    print(f"{'✅' if success else '❌'} 更新有效值: {'成功' if success else '失败'}")
    
    # 验证最终结果
    if success:
        updated_data = manager.get_inventory_by_id(inventory_id)
        checks = [
            updated_data['product_name'] == "更新后的商品名称",
            updated_data['quantity'] == 200,
            updated_data['original_value'] == 7500.0,
            updated_data['market_value'] == 6000.0,
            updated_data['status'] == "approved",
            updated_data['storage_location'] == "仓库B",
            updated_data['jd_link'] == "https://item.jd.com/789.html",
            updated_data['xianyu_link'] == "https://2.taobao.com/abc",
            updated_data['tmall_link'] is None,
            updated_data['pdd_link'] is None
        ]
        
        if all(checks):
