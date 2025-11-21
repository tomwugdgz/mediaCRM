#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试库存管理器的删除和修改功能
"""

import sqlite3
from inventory_manager import InventoryManager

def test_manager_functions():
    print("🧪 开始测试库存管理器功能...")
    
    # 创建管理器
    manager = InventoryManager()
    
    print("1. 清理测试数据...")
    # 清理现有测试数据
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    
    # 检查是否存在测试数据
    cursor.execute("SELECT id FROM brands WHERE brand_name = '测试品牌'")
    existing_brand = cursor.fetchone()
    
    if existing_brand:
        brand_id = existing_brand[0]
        # 删除相关的库存数据
        cursor.execute("DELETE FROM inventory WHERE brand_id = ?", (brand_id,))
        # 删除品牌
        cursor.execute("DELETE FROM brands WHERE id = ?", (brand_id,))
        conn.commit()
        print(f"✅ 清理了现有的测试数据")
    
    print("2. 创建测试品牌...")
    try:
        brand_id = manager.add_brand("测试品牌", "测试联系人", "13800138000")
        print(f"✅ 创建测试品牌成功，ID: {brand_id}")
    except Exception as e:
        print(f"❌ 创建测试品牌失败: {str(e)}")
        return False
    
    print("3. 创建测试库存...")
    try:
        inventory_id = manager.add_inventory(
            brand_id=brand_id,
            product_name="测试商品",
            category="饮料",
            quantity=100,
            original_value=1000.0
        )
        print(f"✅ 创建测试库存成功，ID: {inventory_id}")
    except Exception as e:
        print(f"❌ 创建测试库存失败: {str(e)}")
        return False
    
    print("4. 验证库存存在...")
    try:
        # 直接查询数据库
        cursor.execute("SELECT * FROM inventory WHERE id = ?", (inventory_id,))
        result = cursor.fetchone()
        if result:
            print(f"✅ 库存记录在数据库中存在: ID={result[0]}, 名称={result[2]}, 数量={result[3]}")
        else:
            print("❌ 库存记录在数据库中不存在")
            return False
    except Exception as e:
        print(f"❌ 验证库存失败: {str(e)}")
        return False
    
    print("5. 测试更新功能...")
    try:
        success = manager.update_inventory(
            inventory_id,
            product_name="更新后的商品名称",
            quantity=200
        )
        
        if success:
            print("✅ 更新功能正常")
            # 验证更新结果
            cursor.execute("SELECT product_name, quantity FROM inventory WHERE id = ?", (inventory_id,))
            updated_result = cursor.fetchone()
            if updated_result:
                print(f"   更新后数据: 名称={updated_result[0]}, 数量={updated_result[1]}")
        else:
            print("❌ 更新功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 更新功能异常: {str(e)}")
        return False
    
    print("6. 测试删除功能...")
    try:
        success = manager.delete_inventory(inventory_id)
        
        if success:
            print("✅ 删除功能正常")
            # 验证删除结果
            cursor.execute("SELECT * FROM inventory WHERE id = ?", (inventory_id,))
            deleted_result = cursor.fetchone()
            if deleted_result:
                print("❌ 警告：删除后数据仍然存在")
                return False
            else:
                print("✅ 删除验证：数据已从数据库中移除")
        else:
            print("❌ 删除功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 删除功能异常: {str(e)}")
        return False
    
    print("7. 测试媒体管理功能...")
    try:
        # 添加测试媒体
        media_id = manager.add_media_resource(
            media_name="测试媒体",
            media_type="电视",
            location="测试地点",
            market_price=5000.0,
            contact_person="媒体联系人",
            contact_phone="13900139000"
        )
        print(f"✅ 添加媒体成功，ID: {media_id}")
        
        # 更新媒体
        success = manager.update_media_resource(
            media_id,
            media_name="更新后的媒体名称",
            contact_person="新的联系人"
        )
        if success:
            print("✅ 媒体更新功能正常")
        else:
            print("❌ 媒体更新功能异常")
            return False
        
        # 删除媒体
        success = manager.delete_media_resource(media_id)
        if success:
            print("✅ 媒体删除功能正常")
        else:
            print("❌ 媒体删除功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 媒体管理功能异常: {str(e)}")
        return False
    
    print("8. 测试渠道管理功能...")
    try:
        # 添加测试渠道
        channel_id = manager.add_sales_channel(
            channel_name="测试渠道",
            channel_type="超市",
            contact_person="渠道联系人",
            contact_phone="13700137000"
        )
        print(f"✅ 添加渠道成功，ID: {channel_id}")
        
        # 更新渠道
        success = manager.update_sales_channel(
            channel_id,
            channel_name="更新后的渠道名称",
            contact_person="新的渠道联系人"
        )
        if success:
            print("✅ 渠道更新功能正常")
        else:
            print("❌ 渠道更新功能异常")
            return False
        
        # 删除渠道
        success = manager.delete_sales_channel(channel_id)
        if success:
            print("✅ 渠道删除功能正常")
        else:
            print("❌ 渠道删除功能异常")
            return False
            
    except Exception as e:
        print(f"❌ 渠道管理功能异常: {str(e)}")
        return False
    
    conn.close()
    print("\n🎉 所有测试通过！管理器功能正常。")
    return True

if __name__ == "__main__":
    test_manager_functions()