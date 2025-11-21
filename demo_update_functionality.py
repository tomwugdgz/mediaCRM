#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改功能演示脚本
展示Web界面和命令行界面的修改功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inventory_manager import InventoryManager

def demo_web_interface_modification():
    """演示Web界面的修改功能"""
    print("="*60)
    print("🌐 Web界面修改功能演示")
    print("="*60)
    
    print("📱 Web界面访问地址:")
    print("   http://localhost:8501  (主界面)")
    print("   http://localhost:8502  (备用端口)")
    print()
    
    print("✏️ 修改功能位置:")
    print("   1. 📦 库存管理 → 📋 库存列表 → ✏️ 修改库存")
    print("   2. 🏢 品牌管理 → 品牌操作 → ✏️ 修改品牌")
    print()
    
    print("🔧 操作步骤:")
    print("   ① 选择要修改的库存/品牌ID")
    print("   ② 点击'✏️ 修改'按钮加载当前信息")
    print("   ③ 在表单中修改需要更新的字段")
    print("   ④ 点击'💾 保存修改'完成更新")
    print("   ⑤ 点击'❌ 取消修改'放弃更改")
    print()
    
    print("💡 功能特点:")
    print("   ✅ 智能表单预填充当前值")
    print("   ✅ 支持选择性字段修改")
    print("   ✅ 实时数据验证")
    print("   ✅ 修改前后对比显示")
    print("   ✅ 事务安全保证")

def demo_cli_modification():
    """演示命令行界面的修改功能"""
    print("="*60)
    print("💻 命令行界面修改功能演示")
    print("="*60)
    
    manager = InventoryManager()
    
    # 创建测试数据
    print("🧪 创建测试数据...")
    
    # 添加测试品牌
    brand_id = manager.add_brand(
        brand_name="演示品牌",
        contact_person="演示联系人",
        contact_phone="13800138000",
        brand_type="饮料",
        reputation_score=8
    )
    print(f"✅ 添加测试品牌，ID: {brand_id}")
    
    # 添加测试库存
    inventory_id = manager.add_inventory(
        brand_id=brand_id,
        product_name="演示商品",
        category="饮料",
        quantity=100,
        original_value=5000.0,
        market_value=4500.0,
        expiry_date="2025-12-31",
        storage_location="演示仓库"
    )
    print(f"✅ 添加测试库存，ID: {inventory_id}")
    
    print("\n📋 可用的命令行命令:")
    print("   # 交互式修改库存")
    print("   python inventory_cli.py --mode update-inventory")
    print()
    print("   # 交互式修改品牌")
    print("   python inventory_cli.py --mode update-brand")
    print()
    print("   # 或者直接运行交互模式")
    print("   python inventory_cli.py")
    print("   # 然后选择菜单选项 8 或 9")
    
    print(f"\n🎯 当前测试数据:")
    print(f"   库存ID: {inventory_id} - 演示商品")
    print(f"   品牌ID: {brand_id} - 演示品牌")
    
    # 显示当前数据
    inventory_data = manager.get_inventory_by_id(inventory_id)
    brand_data = manager.get_brand_by_id(brand_id)
    
    if inventory_data:
        print(f"\n📦 当前库存信息:")
        print(f"   商品名称: {inventory_data['product_name']}")
        print(f"   数量: {inventory_data['quantity']}")
        print(f"   原价: ¥{inventory_data['original_value']}")
        print(f"   状态: {inventory_data['status']}")
    
    if brand_data:
        print(f"\n🏢 当前品牌信息:")
        print(f"   品牌名称: {brand_data['brand_name']}")
        print(f"   联系人: {brand_data['contact_person']}")
        print(f"   声誉评分: {brand_data['reputation_score']}")

def show_modification_examples():
    """展示修改示例"""
    print("="*60)
    print("📝 修改功能使用示例")
    print("="*60)
    
    print("🔄 库存修改示例:")
    print("   • 商品名称: '可口可乐经典装' → '可口可乐零糖装'")
    print("   • 数量: 1000 → 1200")
    print("   • 状态: pending → approved")
    print("   • 存储位置: '仓库A' → '仓库B-货架3'")
    
    print("\n🏷️ 品牌修改示例:")
    print("   • 品牌名称: '可口可乐' → '可口可乐中国'")
    print("   • 联系人: '张经理' → '李总监'")
    print("   • 声誉评分: 8 → 9")
    print("   • 联系电话: '13800138000' → '13900139000'")
    
    print("\n⚠️ 注意事项:")
    print("   • 有关联库存的品牌无法删除，但可以修改信息")
    print("   • 修改操作会更新updated_at时间戳")
    print("   • 所有修改都有事务保护，失败会自动回滚")
    print("   • 建议先在小批量数据上测试修改功能")

def main():
    """主演示函数"""
    print("🎉 广告置换库存管理系统 - 修改功能演示")
    print("="*80)
    
    demo_web_interface_modification()
    print()
    demo_cli_modification()
    print()
    show_modification_examples()
    
    print("\n" + "="*80)
    print("🚀 现在您可以:")
    print("   1. 打开浏览器访问 http://localhost:8501")
    print("   2. 使用命令行: python inventory_cli.py --mode update-inventory")
    print("   3. 测试修改功能，体验完整的CRUD操作")
    print("\n💡 提示: 系统已内置测试数据，可以直接开始体验修改功能！")
    
    print("\n📚 相关文档:")
    print("   • README_INVENTORY.md - 快速开始指南")
    print("   • INVENTORY_SYSTEM_GUIDE.md - 完整使用手册")
    print("   • test_update_functionality.py - 功能测试脚本")

if __name__ == "__main__":
    main()