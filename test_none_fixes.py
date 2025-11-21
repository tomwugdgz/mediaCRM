#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试None值修复的脚本
验证添加、修改、删除功能中的None值处理问题是否已修复
"""

import sqlite3
import pandas as pd
from inventory_manager import InventoryManager
from pricing_calculator import PricingCalculator
from financial_calculator import FinancialCalculator

def test_inventory_operations():
    """测试库存操作中的None值处理"""
    print("=== 测试库存操作中的None值处理 ===")
    
    # 创建管理器实例
    manager = InventoryManager()
    pricing = PricingCalculator()
    financial = FinancialCalculator()
    
    # 测试1: 添加品牌
    print("\n1. 测试添加品牌...")
    try:
        brand_id = manager.add_brand(
            brand_name="测试品牌",
            contact_person=None,  # 测试None值
            contact_phone=None,   # 测试None值
            contact_email=None,   # 测试None值
            brand_type="饮料",
            reputation_score=8
        )
        print(f"✅ 品牌添加成功，ID: {brand_id}")
    except Exception as e:
        print(f"❌ 品牌添加失败: {e}")
    
    # 测试2: 添加库存（市场价值为None）
    print("\n2. 测试添加库存（市场价值为None）...")
    try:
        inventory_id = manager.add_inventory(
            brand_id=brand_id,
            product_name="测试商品",
            category="饮料",
            quantity=100,
            original_value=5000.0,
            market_value=None,  # 测试None值
            expiry_date=None,   # 测试None值
            storage_location=None,  # 测试None值
            jd_link=None,       # 测试None值
            tmall_link=None,    # 测试None值
            xianyu_link=None,   # 测试None值
            pdd_link=None       # 测试None值
        )
        print(f"✅ 库存添加成功，ID: {inventory_id}")
    except Exception as e:
        print(f"❌ 库存添加失败: {e}")
    
    # 测试3: 定价计算（None值市场价值）
    print("\n3. 测试定价计算（None值市场价值）...")
    try:
        pricing_result = pricing.calculate_realization_value(inventory_id)
        if 'error' not in pricing_result:
            print(f"✅ 定价计算成功")
            print(f"   原始价值: ¥{pricing_result['original_value']}")
            print(f"   市场价值: ¥{pricing_result['market_value']}")
            print(f"   建议销售价格: ¥{pricing_result['recommended_sale_price']}")
            print(f"   变现率: {pricing_result['realization_rate']:.2%}")
        else:
            print(f"❌ 定价计算失败: {pricing_result['error']}")
    except Exception as e:
        print(f"❌ 定价计算异常: {e}")
    
    # 测试4: 修改库存（None值处理）
    print("\n4. 测试修改库存（None值处理）...")
    try:
        success = manager.update_inventory(
            inventory_id,
            product_name="修改后的商品",
            quantity=150,
            original_value=6000.0,
            market_value=0.0,  # 测试0值（应该转换为None）
            status="approved",
            storage_location=None  # 测试None值
        )
        if success:
            print("✅ 库存修改成功")
        else:
            print("❌ 库存修改失败")
    except Exception as e:
        print(f"❌ 库存修改异常: {e}")
    
    # 测试5: 添加销售渠道（None值佣金率）
    print("\n5. 测试添加销售渠道（None值佣金率）...")
    try:
        channel_id = manager.add_sales_channel(
            channel_name="测试渠道",
            channel_type="B级",
            contact_person="测试联系人",
            contact_phone="13800138000",
            commission_rate=None,  # 测试None值
            payment_terms="现结"
        )
        print(f"✅ 销售渠道添加成功，ID: {channel_id}")
    except Exception as e:
        print(f"❌ 销售渠道添加失败: {e}")
    
    # 测试6: 添加媒体资源（None值处理）
    print("\n6. 测试添加媒体资源（None值处理）...")
    try:
        media_id = manager.add_media_resource(
            media_name="测试媒体",
            media_type="社区门禁",
            media_form="静态海报",
            location="测试小区",
            market_price=5000.0,
            discount_rate=80.0,
            actual_cost=None,  # 测试None值（应该自动计算）
            media_specs=None,   # 测试None值
            audience_info=None, # 测试None值
            owner_name=None,    # 测试None值
            contact_person=None,# 测试None值
            contact_phone=None, # 测试None值
            contract_start=None,# 测试None值
            contract_end=None   # 测试None值
        )
        print(f"✅ 媒体资源添加成功，ID: {media_id}")
    except Exception as e:
        print(f"❌ 媒体资源添加失败: {e}")
    
    # 测试7: 财务计算（None值处理）
    print("\n7. 测试财务计算（None值处理）...")
    try:
        # 注意：这里需要确保数据库中有完整的交易数据
        # 由于我们刚刚创建数据，可能没有完整的交易记录
        # 所以我们只测试计算逻辑，不依赖实际交易数据
        financial_result = financial.calculate_transaction_profit(
            inventory_id=inventory_id,
            ad_resource_id=media_id,
            channel_id=channel_id,
            proposed_sale_price=None  # 测试None值（使用默认定价）
        )
        if 'error' not in financial_result:
            print(f"✅ 财务计算成功")
            print(f"   可行性: {financial_result['feasibility']}")
            print(f"   总收入: ¥{financial_result['total_revenue']}")
            print(f"   净利润: ¥{financial_result['net_profit']}")
            print(f"   利润率: {financial_result['profit_margin']:.2%}")
            print(f"   投资回报率: {financial_result['return_on_investment']:.2%}")
        else:
            print(f"❌ 财务计算失败: {financial_result['error']}")
    except Exception as e:
        print(f"❌ 财务计算异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_inventory_operations()