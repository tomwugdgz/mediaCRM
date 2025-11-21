#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
库存管理系统 - 命令行界面
提供基本的库存管理功能，适合快速操作和自动化脚本
"""

import argparse
import json
import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

# 导入自定义模块
from inventory_manager import InventoryManager
from pricing_calculator import PricingCalculator
from financial_calculator import FinancialCalculator

class InventoryCLI:
    """库存管理命令行界面"""
    
    def __init__(self):
        self.manager = InventoryManager()
        self.pricing = PricingCalculator()
        self.financial = FinancialCalculator()
    
    def show_inventory_summary(self):
        """显示库存概览"""
        summary = self.manager.get_inventory_summary()
        
        print("\n" + "="*60)
        print("📊 库存概览")
        print("="*60)
        
        # 总体统计
        total_inventory = sum(item['count'] for item in summary['inventory_stats'])
        total_value = sum(item['total_value'] for item in summary['inventory_stats'])
        
        print(f"总库存数量: {total_inventory:,} 件")
        print(f"库存总价值: ¥{total_value:,.2f}")
        
        # 状态分布
        print("\n📈 库存状态分布:")
        for stat in summary['inventory_stats']:
            status_emoji = {
                'pending': '⏳',
                'approved': '✅',
                'rejected': '❌',
                'sold': '💰'
            }.get(stat['status'], '📦')
            print(f"  {status_emoji} {stat['status']}: {stat['count']} 件 (价值: ¥{stat['total_value']:,.2f})")
        
        # 品类分布
        print("\n🏷️  品类分布:")
        for category in summary['category_stats']:
            print(f"  📦 {category['category']}: {category['count']} 件 (价值: ¥{category['total_value']:,.2f})")
        
        # 品牌合作情况
        print("\n🏢 品牌合作情况:")
        for brand in summary['brand_stats']:
            print(f"  🔗 {brand['brand_name']}: {brand['inventory_count']} 件 (价值: ¥{brand['total_value']:,.2f})")
    
    def add_brand_interactive(self):
        """交互式添加品牌"""
        print("\n" + "="*60)
        print("🏢 添加新品牌")
        print("="*60)
        
        brand_name = input("品牌名称: ").strip()
        if not brand_name:
            print("❌ 品牌名称不能为空")
            return
        
        contact_person = input("联系人 (可选): ").strip() or None
        contact_phone = input("联系电话 (可选): ").strip() or None
        contact_email = input("联系邮箱 (可选): ").strip() or None
        brand_type = input("品牌类型 (可选，如饮料/日化/家电): ").strip() or None
        
        try:
            reputation_score = int(input("品牌声誉评分 (1-10, 默认5): ") or "5")
            if not 1 <= reputation_score <= 10:
                print("❌ 评分必须在1-10之间")
                return
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        try:
            brand_id = self.manager.add_brand(
                brand_name=brand_name,
                contact_person=contact_person,
                contact_phone=contact_phone,
                contact_email=contact_email,
                brand_type=brand_type,
                reputation_score=reputation_score
            )
            print(f"✅ 品牌添加成功！ID: {brand_id}")
        except Exception as e:
            print(f"❌ 添加失败: {str(e)}")
    
    def add_inventory_interactive(self):
        """交互式添加库存"""
        print("\n" + "="*60)
        print("📦 添加新库存")
        print("="*60)
        
        # 获取品牌列表
        conn = sqlite3.connect(self.manager.db_path)
        brands_df = pd.read_sql_query('SELECT id, brand_name FROM brands', conn)
        conn.close()
        
        if brands_df.empty:
            print("❌ 请先添加品牌")
            return
        
        print("可选品牌:")
        for _, brand in brands_df.iterrows():
            print(f"  {brand['id']}: {brand['brand_name']}")
        
        try:
            brand_id = int(input("选择品牌ID: "))
            if brand_id not in brands_df['id'].values:
                print("❌ 无效的品牌ID")
                return
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        product_name = input("商品名称: ").strip()
        if not product_name:
            print("❌ 商品名称不能为空")
            return
        
        print("商品品类:")
        categories = ["饮料", "日化", "家电", "食品", "其他"]
        for i, category in enumerate(categories, 1):
            print(f"  {i}: {category}")
        
        try:
            category_choice = int(input("选择品类 (1-5): ") or "1")
            if not 1 <= category_choice <= 5:
                print("❌ 请选择1-5")
                return
            category = categories[category_choice - 1]
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        try:
            quantity = int(input("数量: ") or "100")
            if quantity <= 0:
                print("❌ 数量必须大于0")
                return
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        try:
            original_value = float(input("原始价值 (元): ") or "10000")
            if original_value <= 0:
                print("❌ 价值必须大于0")
                return
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        market_value_input = input("市场价值 (元，可选): ").strip()
        market_value = float(market_value_input) if market_value_input else None
        
        expiry_input = input("保质期 (YYYY-MM-DD，可选): ").strip()
        expiry_date = expiry_input if expiry_input else None
        
        storage_location = input("存储位置 (可选): ").strip() or None
        
        try:
            inventory_id = self.manager.add_inventory(
                brand_id=brand_id,
                product_name=product_name,
                category=category,
                quantity=quantity,
                original_value=original_value,
                market_value=market_value,
                expiry_date=expiry_date,
                storage_location=storage_location
            )
            print(f"✅ 库存添加成功！ID: {inventory_id}")
        except Exception as e:
            print(f"❌ 添加失败: {str(e)}")
    
    def update_inventory_interactive(self):
        """交互式修改库存"""
        print("\n" + "="*60)
        print("✏️ 修改库存信息")
        print("="*60)
        
        # 获取库存列表
        conn = sqlite3.connect(self.manager.db_path)
        inventory_df = pd.read_sql_query('SELECT id, product_name, brand_id FROM inventory', conn)
        conn.close()
        
        if inventory_df.empty:
            print("❌ 没有库存数据")
            return
        
        print("库存列表:")
        for _, item in inventory_df.iterrows():
            print(f"  {item['id']}: {item['product_name']}")
        
        try:
            inventory_id = int(input("选择要修改的库存ID: "))
            if inventory_id not in inventory_df['id'].values:
                print("❌ 无效的库存ID")
                return
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        # 获取当前库存信息
        current_data = self.manager.get_inventory_by_id(inventory_id)
        if not current_data:
            print(f"❌ 未找到库存ID {inventory_id}")
            return
        
        print(f"\n当前库存信息:")
        print(f"  商品名称: {current_data['product_name']}")
        print(f"  商品类别: {current_data['category']}")
        print(f"  数量: {current_data['quantity']}")
        print(f"  原价: ¥{current_data['original_value']}")
        print(f"  市场价值: ¥{current_data['market_value']}")
        print(f"  品牌ID: {current_data['brand_id']}")
        print(f"  保质期: {current_data['expiry_date']}")
        print(f"  存储位置: {current_data['storage_location']}")
        print(f"  状态: {current_data['status']}")
        
        # 交互式修改
        update_fields = {}
        
        if input("\n是否修改商品名称？(y/n): ").lower() == 'y':
            update_fields['product_name'] = input("新商品名称: ").strip()
        
        if input("是否修改商品类别？(y/n): ").lower() == 'y':
            update_fields['category'] = input("新商品类别: ").strip()
        
        if input("是否修改数量？(y/n): ").lower() == 'y':
            try:
                update_fields['quantity'] = int(input("新数量: "))
            except ValueError:
                print("❌ 请输入有效的数字")
                return
        
        if input("是否修改原价？(y/n): ").lower() == 'y':
            try:
                update_fields['original_value'] = float(input("新原价: "))
            except ValueError:
                print("❌ 请输入有效的数字")
                return
        
        if input("是否修改市场价值？(y/n): ").lower() == 'y':
            try:
                update_fields['market_value'] = float(input("新市场价值: "))
            except ValueError:
                print("❌ 请输入有效的数字")
                return
        
        if input("是否修改品牌ID？(y/n): ").lower() == 'y':
            # 获取品牌列表
            conn = sqlite3.connect(self.manager.db_path)
            brands_df = pd.read_sql_query('SELECT id, brand_name FROM brands', conn)
            conn.close()
            
            if brands_df.empty:
                print("❌ 没有品牌数据")
                return
            
            print("可选品牌:")
            for _, brand in brands_df.iterrows():
                print(f"  {brand['id']}: {brand['brand_name']}")
            
            try:
                new_brand_id = int(input("新品牌ID: "))
                if new_brand_id not in brands_df['id'].values:
                    print("❌ 无效的品牌ID")
                    return
                update_fields['brand_id'] = new_brand_id
            except ValueError:
                print("❌ 请输入有效的数字")
                return
        
        if input("是否修改保质期？(y/n): ").lower() == 'y':
            update_fields['expiry_date'] = input("新保质期 (YYYY-MM-DD): ").strip()
        
        if input("是否修改存储位置？(y/n): ").lower() == 'y':
            update_fields['storage_location'] = input("新存储位置: ").strip()
        
        if input("是否修改状态？(y/n): ").lower() == 'y':
            print("可选状态: pending, approved, rejected, sold")
            new_status = input("新状态: ").strip()
            if new_status in ['pending', 'approved', 'rejected', 'sold']:
                update_fields['status'] = new_status
            else:
                print("❌ 无效的状态")
                return
        
        if update_fields:
            success = self.manager.update_inventory(inventory_id, **update_fields)
            if success:
                print(f"✅ 库存ID {inventory_id} 修改成功！")
            else:
                print(f"❌ 修改失败，请重试")
        else:
            print("未进行任何修改")
    
    def update_brand_interactive(self):
        """交互式修改品牌"""
        print("\n" + "="*60)
        print("✏️ 修改品牌信息")
        print("="*60)
        
        # 获取品牌列表
        conn = sqlite3.connect(self.manager.db_path)
        brands_df = pd.read_sql_query('SELECT id, brand_name FROM brands', conn)
        conn.close()
        
        if brands_df.empty:
            print("❌ 没有品牌数据")
            return
        
        print("品牌列表:")
        for _, brand in brands_df.iterrows():
            print(f"  {brand['id']}: {brand['brand_name']}")
        
        try:
            brand_id = int(input("选择要修改的品牌ID: "))
            if brand_id not in brands_df['id'].values:
                print("❌ 无效的品牌ID")
                return
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        # 获取当前品牌信息
        current_data = self.manager.get_brand_by_id(brand_id)
        if not current_data:
            print(f"❌ 未找到品牌ID {brand_id}")
            return
        
        print(f"\n当前品牌信息:")
        print(f"  品牌名称: {current_data['brand_name']}")
        print(f"  联系人: {current_data['contact_person']}")
        print(f"  联系电话: {current_data['contact_phone']}")
        print(f"  联系邮箱: {current_data['contact_email']}")
        print(f"  品牌类型: {current_data['brand_type']}")
        print(f"  声誉评分: {current_data['reputation_score']}")
        
        # 交互式修改
        update_fields = {}
        
        if input("\n是否修改品牌名称？(y/n): ").lower() == 'y':
            update_fields['brand_name'] = input("新品牌名称: ").strip()
        
        if input("是否修改联系人？(y/n): ").lower() == 'y':
            update_fields['contact_person'] = input("新联系人: ").strip()
        
        if input("是否修改联系电话？(y/n): ").lower() == 'y':
            update_fields['contact_phone'] = input("新联系电话: ").strip()
        
        if input("是否修改联系邮箱？(y/n): ").lower() == 'y':
            update_fields['contact_email'] = input("新联系邮箱: ").strip()
        
        if input("是否修改品牌类型？(y/n): ").lower() == 'y':
            update_fields['brand_type'] = input("新品牌类型: ").strip()
        
        if input("是否修改声誉评分？(y/n): ").lower() == 'y':
            try:
                new_score = int(input("新声誉评分 (1-10): "))
                if not 1 <= new_score <= 10:
                    print("❌ 评分必须在1-10之间")
                    return
                update_fields['reputation_score'] = new_score
            except ValueError:
                print("❌ 请输入有效的数字")
                return
        
        if update_fields:
            success = self.manager.update_brand(brand_id, **update_fields)
            if success:
                print(f"✅ 品牌ID {brand_id} 修改成功！")
            else:
                print(f"❌ 修改失败，请重试")
        else:
            print("未进行任何修改")
    
    def calculate_pricing_interactive(self):
        """交互式定价计算"""
        print("\n" + "="*60)
        print("💰 定价计算")
        print("="*60)
        
        # 获取待定价库存
        conn = sqlite3.connect(self.manager.db_path)
        inventory_df = pd.read_sql_query('''
            SELECT i.id, i.product_name, b.brand_name, i.original_value
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            WHERE i.status = 'pending' OR i.market_value IS NULL
        ''', conn)
        conn.close()
        
        if inventory_df.empty:
            print("❌ 没有需要定价的库存")
            return
        
        print("待定价库存:")
        for _, item in inventory_df.iterrows():
            print(f"  {item['id']}: {item['product_name']} ({item['brand_name']}) - 原始价值: ¥{item['original_value']:,.2f}")
        
        try:
            inventory_id = int(input("选择库存ID: "))
            if inventory_id not in inventory_df['id'].values:
                print("❌ 无效的库存ID")
                return
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        print("\n正在计算定价...")
        result = self.pricing.calculate_realization_value(inventory_id)
        
        if 'error' not in result:
            print(f"\n📊 定价分析结果:")
            print(f"商品名称: {result['product_name']}")
            print(f"原始价值: ¥{result['original_value']:,.2f}")
            print(f"市场价值: ¥{result['market_value']:,.2f}")
            print(f"变现率: {result['realization_rate']:.2%}")
            print(f"建议售价: ¥{result['recommended_sale_price']:,.2f}")
            print(f"预期回报: ¥{result['expected_cash_return']:,.2f}")
            print(f"风险等级: {result['risk_level'].upper()}")
            
            # 价格来源
            price_sources = result.get('price_sources', {})
            if price_sources:
                print(f"\n💡 价格来源:")
                if price_sources.get('pdd_price'):
                    print(f"  拼多多价格: ¥{price_sources['pdd_price']}")
                if price_sources.get('xianyu_price'):
                    print(f"  闲鱼价格: ¥{price_sources['xianyu_price']}")
                if price_sources.get('recommended_price'):
                    print(f"  建议回收价: ¥{price_sources['recommended_price']}")
        else:
            print(f"❌ 计算失败: {result['error']}")
    
    def check_risk_interactive(self):
        """交互式风控检查"""
        print("\n" + "="*60)
        print("⚠️ 风控检查")
        print("="*60)
        
        # 获取库存列表
        conn = sqlite3.connect(self.manager.db_path)
        inventory_df = pd.read_sql_query('SELECT id, product_name FROM inventory', conn)
        conn.close()
        
        if inventory_df.empty:
            print("❌ 没有库存数据")
            return
        
        print("库存列表:")
        for _, item in inventory_df.iterrows():
            print(f"  {item['id']}: {item['product_name']}")
        
        try:
            inventory_id = int(input("选择库存ID: "))
            if inventory_id not in inventory_df['id'].values:
                print("❌ 无效的库存ID")
                return
        except ValueError:
            print("❌ 请输入有效的数字")
            return
        
        print("\n正在执行风控检查...")
        risk_result = self.manager.check_inventory_risk(inventory_id)
        
        if risk_result['passed']:
            print("✅ 通过风控检查")
        else:
            print("❌ 未通过风控检查")
            print("\n违规项目:")
            for violation in risk_result['violations']:
                print(f"  - {violation}")
        
        if risk_result['suggestions']:
            print("\n建议:")
            for suggestion in risk_result['suggestions']:
                print(f"  - {suggestion}")
    
    def batch_pricing_analysis(self):
        """批量定价分析"""
        print("\n" + "="*60)
        print("📊 批量定价分析")
        print("="*60)
        
        # 获取待定价库存
        conn = sqlite3.connect(self.manager.db_path)
        pending_df = pd.read_sql_query('''
            SELECT id, product_name FROM inventory WHERE status = 'pending' OR market_value IS NULL
        ''', conn)
        conn.close()
        
        if pending_df.empty:
            print("❌ 没有需要定价的库存")
            return
        
        print(f"发现 {len(pending_df)} 个待定价商品")
        confirm = input("是否继续批量定价分析? (y/N): ").strip().lower()
        
        if confirm != 'y':
            print("❌ 操作已取消")
            return
        
        print("\n正在批量计算定价...")
        inventory_ids = pending_df['id'].tolist()
        results = self.pricing.batch_calculate_prices(inventory_ids)
        
        # 显示结果摘要
        total_items = len(results)
        total_original_value = sum(result.get('original_value', 0) for result in results)
        total_expected_return = sum(result.get('expected_cash_return', 0) for result in results)
        avg_realization_rate = sum(result.get('realization_rate', 0) for result in results) / total_items if total_items > 0 else 0
        
        print(f"\n📈 批量定价分析结果:")
        print(f"分析商品数: {total_items}")
        print(f"总原始价值: ¥{total_original_value:,.2f}")
        print(f"总预期回报: ¥{total_expected_return:,.2f}")
        print(f"平均变现率: {avg_realization_rate:.2%}")
        
        # 风险等级统计
        risk_levels = {'low': 0, 'medium': 0, 'high': 0}
        for result in results:
            risk_level = result.get('risk_level', 'unknown')
            if risk_level in risk_levels:
                risk_levels[risk_level] += 1
        
        print(f"\n风险等级分布:")
        print(f"  🟢 低风险: {risk_levels['low']} 件")
        print(f"  🟡 中风险: {risk_levels['medium']} 件")
        print(f"  🔴 高风险: {risk_levels['high']} 件")
        
        # 详细结果
        show_details = input("\n是否显示详细结果? (y/N): ").strip().lower()
        if show_details == 'y':
            print("\n详细定价结果:")
            for result in results:
                if 'error' not in result:
                    print(f"\n{result['product_name']}:")
                    print(f"  原始价值: ¥{result['original_value']:,.2f}")
                    print(f"  变现率: {result['realization_rate']:.2%}")
                    print(f"  预期回报: ¥{result['expected_cash_return']:,.2f}")
                    print(f"  风险等级: {result['risk_level']}")
                else:
                    print(f"\n错误: {result['error']}")
    
    def export_data(self, export_type='all'):
        """导出数据"""
        print("\n" + "="*60)
        print("📤 数据导出")
        print("="*60)
        
        try:
            if export_type == 'all':
                filename = self.manager.export_to_excel()
            elif export_type == 'financial':
                filename = self.financial.generate_financial_report()
            else:
                print(f"❌ 不支持的导出类型: {export_type}")
                return
            
            print(f"✅ 数据导出成功: {filename}")
        except Exception as e:
            print(f"❌ 导出失败: {str(e)}")
    
    def run_interactive_mode(self):
        """运行交互式模式"""
        print("\n" + "="*60)
        print("📊 广告置换库存管理系统 - 命令行界面")
        print("="*60)
        
        while True:
            print("\n📋 主菜单:")
            print("  1. 查看库存概览")
            print("  2. 添加品牌")
            print("  3. 添加库存")
            print("  4. 定价计算")
            print("  5. 风控检查")
            print("  6. 批量定价分析")
            print("  7. 导出数据")
            print("  8. 修改库存")
            print("  9. 修改品牌")
            print("  0. 退出系统")
            
            choice = input("\n请选择操作 (0-9): ").strip()
            
            if choice == '0':
                print("👋 感谢使用，再见！")
                break
            elif choice == '1':
                self.show_inventory_summary()
            elif choice == '2':
                self.add_brand_interactive()
            elif choice == '3':
                self.add_inventory_interactive()
            elif choice == '4':
                self.calculate_pricing_interactive()
            elif choice == '5':
                self.check_risk_interactive()
            elif choice == '6':
                self.batch_pricing_analysis()
            elif choice == '7':
                print("\n导出选项:")
                print("  1. 导出所有数据")
                print("  2. 导出财务报告")
                export_choice = input("请选择 (1-2): ").strip()
                if export_choice == '1':
                    self.export_data('all')
                elif export_choice == '2':
                    self.export_data('financial')
                else:
                    print("❌ 无效选择")
            elif choice == '8':
                self.update_inventory_interactive()
            elif choice == '9':
                self.update_brand_interactive()
            else:
                print("❌ 无效选择，请重新输入")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='广告置换库存管理系统')
    parser.add_argument('--mode', choices=['interactive', 'summary', 'add-brand', 'add-inventory',
                                          'pricing', 'risk', 'batch-pricing', 'export', 'update-inventory', 'update-brand'],
                       default='interactive', help='运行模式')
    parser.add_argument('--inventory-id', type=int, help='库存ID')
    parser.add_argument('--export-type', choices=['all', 'financial'], default='all', help='导出类型')
    
    args = parser.parse_args()
    
    cli = InventoryCLI()
    
    if args.mode == 'interactive':
        cli.run_interactive_mode()
    elif args.mode == 'summary':
        cli.show_inventory_summary()
    elif args.mode == 'add-brand':
        cli.add_brand_interactive()
    elif args.mode == 'add-inventory':
        cli.add_inventory_interactive()
    elif args.mode == 'pricing':
        if args.inventory_id:
            result = cli.pricing.calculate_realization_value(args.inventory_id)
            if 'error' not in result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"错误: {result['error']}")
        else:
            cli.calculate_pricing_interactive()
    elif args.mode == 'risk':
        if args.inventory_id:
            result = cli.manager.check_inventory_risk(args.inventory_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            cli.check_risk_interactive()
    elif args.mode == 'batch-pricing':
        cli.batch_pricing_analysis()
    elif args.mode == 'export':
        cli.export_data(args.export_type)

if __name__ == "__main__":
    main()