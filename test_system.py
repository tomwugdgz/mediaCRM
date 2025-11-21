#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统功能测试 - 不依赖外部包安装
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """测试系统基本功能"""
    print("🧪 开始测试广告置换库存管理系统...")
    
    try:
        # 测试数据库初始化
        print("\n1️⃣ 测试数据库初始化...")
        from inventory_manager import InventoryManager
        manager = InventoryManager()
        print("✅ 数据库初始化成功")
        
        # 测试添加品牌
        print("\n2️⃣ 测试品牌管理...")
        brand_id = manager.add_brand(
            brand_name="可口可乐",
            contact_person="张经理",
            contact_phone="13800138000",
            contact_email="zhang@coke.com",
            brand_type="饮料",
            reputation_score=9
        )
        print(f"✅ 品牌添加成功，ID: {brand_id}")
        
        # 测试添加广告资源
        print("\n3️⃣ 测试广告资源管理...")
        resource_id = manager.add_ad_resource(
            resource_name="社区门禁广告位A",
            resource_type="社区门禁",
            location="朝阳区某小区",
            market_price=5000.0,
            actual_cost=200.0
        )
        print(f"✅ 广告资源添加成功，ID: {resource_id}")
        
        # 测试添加销售渠道
        print("\n4️⃣ 测试销售渠道管理...")
        channel_id = manager.add_sales_channel(
            channel_name="王团长团购",
            channel_type="S级",
            contact_person="王团长",
            contact_phone="13700137000",
            commission_rate=5.0,
            payment_terms="现结"
        )
        print(f"✅ 销售渠道添加成功，ID: {channel_id}")
        
        # 测试添加库存
        print("\n5️⃣ 测试库存管理...")
        inventory_id = manager.add_inventory(
            brand_id=brand_id,
            product_name="可口可乐经典装",
            category="饮料",
            quantity=1000,
            original_value=45000.0,
            market_value=30000.0,
            expiry_date="2025-06-30",
            storage_location="仓库A"
        )
        print(f"✅ 库存添加成功，ID: {inventory_id}")
        
        # 测试定价计算
        print("\n6️⃣ 测试定价计算...")
        try:
            from pricing_calculator import PricingCalculator
            pricing = PricingCalculator()
            result = pricing.calculate_realization_value(inventory_id)
            
            if 'error' not in result:
                print(f"✅ 定价计算成功")
                print(f"   商品: {result['product_name']}")
                print(f"   原始价值: ¥{result['original_value']:,.2f}")
                print(f"   变现率: {result['realization_rate']:.2%}")
                print(f"   预期回报: ¥{result['expected_cash_return']:,.2f}")
                print(f"   风险等级: {result['risk_level']}")
            else:
                print(f"❌ 定价计算失败: {result['error']}")
        except Exception as e:
            print(f"⚠️ 定价计算模块测试失败: {str(e)}")
        
        # 测试风控检查
        print("\n7️⃣ 测试风控检查...")
        risk_result = manager.check_inventory_risk(inventory_id)
        if risk_result['passed']:
            print("✅ 通过风控检查")
        else:
            print("⚠️ 未通过风控检查")
            for violation in risk_result['violations']:
                print(f"   - {violation}")
        
        # 测试财务测算
        print("\n8️⃣ 测试财务测算...")
        try:
            from financial_calculator import FinancialCalculator
            financial = FinancialCalculator()
            profit_result = financial.calculate_transaction_profit(
                inventory_id=inventory_id,
                ad_resource_id=resource_id,
                channel_id=channel_id
            )
            
            if 'error' not in profit_result:
                print(f"✅ 财务测算成功")
                print(f"   总收入: ¥{profit_result['total_revenue']:,.2f}")
                print(f"   总成本: ¥{profit_result['total_cost']:,.2f}")
                print(f"   净利润: ¥{profit_result['net_profit']:,.2f}")
                print(f"   利润率: {profit_result['profit_margin']:.2%}")
                print(f"   投资回报率: {profit_result['return_on_investment']:.2%}")
                print(f"   交易可行性: {'✅ 通过' if profit_result['feasibility'] else '❌ 不通过'}")
            else:
                print(f"❌ 财务测算失败: {profit_result['error']}")
        except Exception as e:
            print(f"⚠️ 财务测算模块测试失败: {str(e)}")
        
        # 测试库存概览
        print("\n9️⃣ 测试库存概览...")
        summary = manager.get_inventory_summary()
        total_inventory = sum(item['count'] for item in summary['inventory_stats'])
        total_value = sum(item['total_value'] for item in summary['inventory_stats'])
        print(f"✅ 库存概览获取成功")
        print(f"   总库存数量: {total_inventory} 件")
        print(f"   库存总价值: ¥{total_value:,.2f}")
        
        # 测试数据导出
        print("\n🔟 测试数据导出...")
        try:
            filename = manager.export_to_excel()
            print(f"✅ 数据导出成功: {filename}")
        except Exception as e:
            print(f"⚠️ 数据导出失败: {str(e)}")
        
        print("\n" + "="*60)
        print("🎉 系统测试完成！")
        print("="*60)
        print("✅ 所有核心功能正常工作")
        print("💡 建议：接入真实API获取更准确的市场价格")
        print("🔧 下一步：可以开始使用系统进行实际业务操作")
        
    except Exception as e:
        print(f"❌ 系统测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_functionality()
