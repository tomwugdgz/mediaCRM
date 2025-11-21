#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版混合解决方案功能测试
"""

import sqlite3
from inventory_manager import InventoryManager

def test_basic_functions():
    """测试基本功能"""
    print("🚀 开始测试混合解决方案基本功能...")
    
    manager = InventoryManager()
    
    # 测试库存功能
    print("\n📦 测试库存功能...")
    
    # 添加品牌
    brand_id = manager.add_brand("测试品牌", "测试联系人", "13800138000", brand_type="饮料", reputation_score=8)
    print(f"✅ 添加品牌: ID={brand_id}")
    
    # 添加库存
    inventory_id = manager.add_inventory(brand_id, "测试商品", "饮料", 100, 1000.0)
    print(f"✅ 添加库存: ID={inventory_id}")
    
    # 修改库存
    success = manager.update_inventory(inventory_id, product_name="修改商品", quantity=150)
    print(f"{'✅' if success else '❌'} 修改库存: {success}")
    
    # 删除库存
    success = manager.delete_inventory(inventory_id)
    print(f"{'✅' if success else '❌'} 删除库存: {success}")
    
    # 清理品牌
    manager.delete_brand(brand_id)
    print("✅ 清理完成")
    
    # 测试媒体功能
    print("\n📺 测试媒体功能...")
    
    media_id = manager.add_media_resource("测试媒体", "社区门禁", "静态海报", "测试位置", 5000.0, 80.0, 4000.0)
    print(f"✅ 添加媒体: ID={media_id}")
    
    success = manager.update_media_resource(media_id, media_name="修改媒体")
    print(f"{'✅' if success else '❌'} 修改媒体: {success}")
    
    success = manager.delete_media_resource(media_id)
    print(f"{'✅' if success else '❌'} 删除媒体: {success}")
    
    # 测试渠道功能
    print("\n🛒 测试渠道功能...")
    
    channel_id = manager.add_sales_channel("测试渠道", "S级(团长)", "测试团长", "13800138000", 5.0, "月结")
    print(f"✅ 添加渠道: ID={channel_id}")
    
    success = manager.update_sales_channel(channel_id, channel_name="修改渠道")
    print(f"{'✅' if success else '❌'} 修改渠道: {success}")
    
    success = manager.delete_sales_channel(channel_id)
    print(f"{'✅' if success else '❌'} 删除渠道: {success}")
    
    print("\n🎉 混合解决方案基本功能测试完成！")

if __name__ == "__main__":
    test_basic_functions()