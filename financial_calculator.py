#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务测算器 - 利润分析和风险评估
基于文档中的现实财务模型进行精确的利润计算
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

class FinancialCalculator:
    """财务测算器类"""
    
    def __init__(self, db_path: str = "inventory.db"):
        """
        初始化财务计算器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        
        # 基于文档的财务参数
        self.financial_params = {
            'default_realization_rate': 0.08,  # 默认变现率8%
            'min_realization_rate': 0.05,      # 最低变现率5%
            'max_realization_rate': 0.15,      # 最高变现率15%
            'advertising_cost_ratio': 0.3,     # 广告成本占收入比例上限
            'min_profit_margin': 0.2,          # 最低利润率要求
            'channel_commission_range': (0.05, 0.15),  # 渠道佣金范围
            'storage_cost_per_unit': 2.0,      # 每单位仓储成本
            'logistics_cost_ratio': 0.02       # 物流成本比例
        }
    
    def calculate_transaction_profit(self, inventory_id: int, ad_resource_id: int,
                                   channel_id: int, proposed_sale_price: Optional[float] = None) -> Dict[str, Any]:
        """
        计算单个交易的详细利润分析
        
        基于文档中的现实模型：
        - 100万货值 × 8%变现率 = 8万现金
        - 8万收入 - 3万成本 = 5万净利
        - 回报率：5/3 ≈ 166%
        
        Returns:
            {
                'feasibility': bool,           # 交易可行性
                'total_revenue': float,        # 总收入
                'total_cost': float,           # 总成本
                'net_profit': float,           # 净利润
                'profit_margin': float,        # 利润率
                'return_on_investment': float, # 投资回报率
                'risk_assessment': dict,       # 风险评估
                'recommendations': list        # 建议措施
            }
        """
        conn = sqlite3.connect(self.db_path)
        
        try:
            # 获取库存信息
            inventory_df = pd.read_sql_query('''
                SELECT i.*, b.brand_name, b.reputation_score
                FROM inventory i
                JOIN brands b ON i.brand_id = b.id
                WHERE i.id = ?
            ''', conn, params=(inventory_id,))
            
            if inventory_df.empty:
                return {'error': '库存记录不存在', 'feasibility': False}
            
            inventory = inventory_df.iloc[0]
            
            # 获取广告资源信息
            ad_resource_df = pd.read_sql_query('''
                SELECT * FROM media_resources WHERE id = ?
            ''', conn, params=(ad_resource_id,))
            
            if ad_resource_df.empty:
                return {'error': '广告资源不存在', 'feasibility': False}
            
            ad_resource = ad_resource_df.iloc[0]
            
            # 获取销售渠道信息
            channel_df = pd.read_sql_query('''
                SELECT * FROM sales_channels WHERE id = ?
            ''', conn, params=(channel_id,))
            
            if channel_df.empty:
                return {'error': '销售渠道不存在', 'feasibility': False}
            
            channel = channel_df.iloc[0]
            
            # 基础财务数据
            original_value = float(inventory['original_value'])
            quantity = int(inventory['quantity'])
            ad_actual_cost = float(ad_resource['actual_cost'])
            
            # 计算变现价值
            if proposed_sale_price:
                # 如果提供了建议销售价格
                unit_sale_price = proposed_sale_price
                total_revenue = unit_sale_price * quantity
                realization_rate = total_revenue / original_value
            else:
                # 使用基于市场价格的变现率
                realization_rate = self.calculate_realization_rate(inventory, channel)
                total_revenue = original_value * realization_rate
            
            # 成本分析
            cost_breakdown = self.calculate_cost_breakdown(
                ad_actual_cost, total_revenue, quantity, channel
            )
            
            total_cost = sum(cost_breakdown.values())
            net_profit = total_revenue - total_cost
            profit_margin = net_profit / total_revenue if total_revenue > 0 else 0
            roi = net_profit / total_cost if total_cost > 0 else 0
            
            # 风险评估
            risk_assessment = self.assess_transaction_risk(
                inventory, ad_resource, channel, realization_rate, profit_margin
            )
            
            # 可行性判断
            feasibility = self.assess_transaction_feasibility(
                realization_rate, profit_margin, roi, risk_assessment
            )
            
            # 生成建议
            recommendations = self.generate_recommendations(
                feasibility, realization_rate, profit_margin, risk_assessment
            )
            
            return {
                'feasibility': feasibility,
                'total_revenue': round(total_revenue, 2),
                'total_cost': round(total_cost, 2),
                'net_profit': round(net_profit, 2),
                'profit_margin': round(profit_margin, 4),
                'return_on_investment': round(roi, 4),
                'realization_rate': round(realization_rate, 4),
                'cost_breakdown': {k: round(v, 2) for k, v in cost_breakdown.items()},
                'risk_assessment': risk_assessment,
                'recommendations': recommendations,
                'product_name': inventory['product_name'],
                'brand_name': inventory['brand_name'],
                'channel_name': channel['channel_name'],
                'ad_resource_name': ad_resource.get('resource_name') or ad_resource.get('media_name', '未知资源')
            }
            
        finally:
            conn.close()
    
    def calculate_realization_rate(self, inventory: pd.Series, channel: pd.Series) -> float:
        """
        计算变现率
        基于商品特性、渠道类型、市场情况等综合因素
        """
        base_rate = self.financial_params['default_realization_rate']  # 8%
        
        # 渠道类型调整
        if channel['channel_type'] == 'S级':
            # S级渠道（团长）变现能力较强
            channel_multiplier = 1.2
        elif channel['channel_type'] == 'A级':
            # A级渠道（批发市场）变现能力一般
            channel_multiplier = 0.8
        else:
            channel_multiplier = 1.0
        
        # 品牌声誉调整
        reputation_score = inventory.get('reputation_score', 5)
        if reputation_score >= 8:
            brand_multiplier = 1.1
        elif reputation_score >= 6:
            brand_multiplier = 1.0
        else:
            brand_multiplier = 0.7  # 低声誉品牌变现困难
        
        # 商品品类调整
        category = inventory['category']
        category_multipliers = {
            '饮料': 1.0,      # 标准变现率
            '日化': 0.9,      # 日化品稍低
            '家电': 0.6,      # 家电变现率较低
            '食品': 1.1,      # 食品变现率较高
            '其他': 0.8
        }
        category_multiplier = category_multipliers.get(category, 0.8)
        
        # 保质期调整
        expiry_multiplier = 1.0
        if inventory.get('expiry_date'):
            expiry_date = pd.to_datetime(inventory['expiry_date'])
            months_until_expiry = (expiry_date - datetime.now()).days / 30
            
            if months_until_expiry < 1:
                expiry_multiplier = 0.5  # 临期商品变现困难
            elif months_until_expiry < 3:
                expiry_multiplier = 0.8
            elif months_until_expiry < 6:
                expiry_multiplier = 0.9
        
        # 综合计算
        adjusted_rate = (base_rate * channel_multiplier * brand_multiplier * 
                        category_multiplier * expiry_multiplier)
        
        # 确保在合理范围内
        return max(self.financial_params['min_realization_rate'],
                   min(self.financial_params['max_realization_rate'], adjusted_rate))
    
    def calculate_cost_breakdown(self, ad_cost: float, revenue: float, 
                               quantity: int, channel: pd.Series) -> Dict[str, float]:
        """
        计算成本明细
        """
        # 广告成本
        advertising_cost = ad_cost
        
        # 渠道佣金
        commission_rate = float(channel.get('commission_rate') or 0) / 100
        channel_commission = revenue * commission_rate
        
        # 仓储成本
        storage_cost = quantity * self.financial_params['storage_cost_per_unit']
        
        # 物流成本
        logistics_cost = revenue * self.financial_params['logistics_cost_ratio']
        
        # 其他运营成本（人工、管理等）
        operational_cost = revenue * 0.01  # 1%的运营成本
        
        return {
            'advertising_cost': advertising_cost,
            'channel_commission': channel_commission,
            'storage_cost': storage_cost,
            'logistics_cost': logistics_cost,
            'operational_cost': operational_cost
        }
    
    def assess_transaction_risk(self, inventory: pd.Series, ad_resource: pd.Series,
                              channel: pd.Series, realization_rate: float, 
                              profit_margin: float) -> Dict[str, Any]:
        """
        评估交易风险
        """
        risk_factors = []
        risk_score = 0
        
        # 1. 变现率风险
        if realization_rate < 0.06:  # 低于6%
            risk_factors.append("变现率过低，可能无法达到预期收益")
            risk_score += 3
        elif realization_rate < 0.08:  # 6-8%
            risk_factors.append("变现率偏低，需要谨慎评估")
            risk_score += 1
        
        # 2. 利润率风险
        if profit_margin < 0.15:  # 低于15%
            risk_factors.append("利润率过低，抗风险能力弱")
            risk_score += 3
        elif profit_margin < 0.25:  # 15-25%
            risk_factors.append("利润率一般，需要控制成本")
            risk_score += 1
        
        # 3. 品牌风险
        reputation_score = inventory.get('reputation_score', 5)
        if reputation_score < 6:
            risk_factors.append("品牌知名度低，销售困难")
            risk_score += 2
        
        # 4. 保质期风险
        if inventory.get('expiry_date'):
            expiry_date = pd.to_datetime(inventory['expiry_date'])
            days_until_expiry = (expiry_date - datetime.now()).days
            
            if days_until_expiry < 30:
                risk_factors.append("商品即将过期，时间风险极高")
                risk_score += 4
            elif days_until_expiry < 90:
                risk_factors.append("商品临近保质期，需要快速处理")
                risk_score += 2
        
        # 5. 渠道风险
        if channel['channel_type'] not in ['S级', 'A级']:
            risk_factors.append("未认证渠道，回款风险较高")
            risk_score += 2
        
        # 风险等级评定
        if risk_score >= 8:
            risk_level = "高风险"
            risk_color = "red"
        elif risk_score >= 4:
            risk_level = "中等风险"
            risk_color = "yellow"
        else:
            risk_level = "低风险"
            risk_color = "green"
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_factors': risk_factors
        }
    
    def assess_transaction_feasibility(self, realization_rate: float, profit_margin: float,
                                     roi: float, risk_assessment: Dict) -> bool:
        """
        评估交易可行性
        """
        # 基本条件检查
        if realization_rate < self.financial_params['min_realization_rate']:
            return False
        
        if profit_margin < self.financial_params['min_profit_margin']:
            return False
        
        if roi < 0.5:  # 投资回报率低于50%
            return False
        
        # 风险等级检查
        if risk_assessment['risk_level'] == "高风险":
            # 高风险交易需要额外审核
            return profit_margin > 0.3 and roi > 1.0  # 更高的要求
        
        return True
    
    def generate_recommendations(self, feasibility: bool, realization_rate: float,
                               profit_margin: float, risk_assessment: Dict) -> List[str]:
        """
        生成交易建议
        """
        recommendations = []
        
        if feasibility:
            recommendations.append("✅ 交易可行，建议推进")
            
            if realization_rate < 0.08:
                recommendations.append("⚠️  变现率偏低，考虑寻找更优质渠道")
            
            if profit_margin < 0.25:
                recommendations.append("⚠️  利润率一般，需要严格控制成本")
            
            if risk_assessment['risk_level'] in ["中等风险", "高风险"]:
                recommendations.append("⚠️  存在风险因素，需要制定风险应对方案")
        else:
            recommendations.append("❌ 交易不可行，建议重新评估")
            
            if realization_rate < self.financial_params['min_realization_rate']:
                recommendations.append("💡 变现率过低，考虑更换商品或渠道")
            
            if profit_margin < self.financial_params['min_profit_margin']:
                recommendations.append("💡 利润率不达标，需要降低成本或提高售价")
            
            if risk_assessment['risk_level'] == "高风险":
                recommendations.append("🚨 风险过高，建议放弃或寻找替代方案")
        
        return recommendations
    
    def generate_profit_forecast(self, months: int = 3) -> Dict[str, Any]:
        """
        生成利润预测报告
        """
        conn = sqlite3.connect(self.db_path)
        
        try:
            # 获取历史交易数据
            historical_df = pd.read_sql_query('''
                SELECT
                    DATE(transaction_date) as date,
                    COUNT(*) as transaction_count,
                    SUM(sale_price) as daily_revenue,
                    SUM(profit) as daily_profit
                FROM transactions
                WHERE transaction_date >= datetime('now', '-30 days')
                GROUP BY DATE(transaction_date)
                ORDER BY date
            ''', conn)
            
            # 获取待处理库存
            pending_inventory_df = pd.read_sql_query('''
                SELECT 
                    COUNT(*) as total_items,
                    SUM(original_value) as total_value,
                    AVG(reputation_score) as avg_reputation
                FROM inventory i
                JOIN brands b ON i.brand_id = b.id
                WHERE i.status = 'pending'
            ''', conn)
            
            # 计算预测
            if not historical_df.empty:
                avg_daily_profit = historical_df['daily_profit'].mean()
                avg_transactions_per_day = historical_df['transaction_count'].mean()
            else:
                avg_daily_profit = 0
                avg_transactions_per_day = 0
            
            pending_inventory = pending_inventory_df.iloc[0]
            potential_inventory_value = pending_inventory['total_value'] or 0
            
            # 预测未来收益
            forecast_data = []
            for month in range(1, months + 1):
                # 基于历史数据的增长预测（考虑季节性因素）
                monthly_profit = avg_daily_profit * 30 * (1 + 0.05 * month)  # 每月5%增长
                monthly_transactions = avg_transactions_per_day * 30
                
                # 库存转化预测
                inventory_conversion_rate = 0.3  # 假设30%的库存能成功转化
                monthly_inventory_value = potential_inventory_value * inventory_conversion_rate / months
                monthly_inventory_profit = monthly_inventory_value * 0.08  # 8%变现率
                
                total_monthly_profit = monthly_profit + monthly_inventory_profit
                
                forecast_data.append({
                    'month': month,
                    'predicted_profit': round(total_monthly_profit, 2),
                    'predicted_transactions': int(monthly_transactions),
                    'inventory_conversion': round(monthly_inventory_value, 2),
                    'cumulative_profit': round(sum(d['predicted_profit'] for d in forecast_data) + total_monthly_profit, 2)
                })
            
            return {
                'forecast_period': months,
                'historical_avg_profit': round(avg_daily_profit * 30, 2),
                'pending_inventory_value': round(potential_inventory_value, 2),
                'monthly_forecast': forecast_data,
                'total_predicted_profit': sum(d['predicted_profit'] for d in forecast_data)
            }
            
        finally:
            conn.close()
    
    def generate_financial_report(self, start_date: str = None, end_date: str = None) -> str:
        """
        生成财务报告
        """
        conn = sqlite3.connect(self.db_path)
        
        try:
            # 构建查询条件
            date_condition = ""
            params = []
            if start_date and end_date:
                date_condition = "WHERE t.transaction_date BETWEEN ? AND ?"
                params = [start_date, end_date]
            
            # 获取交易数据
            transactions_df = pd.read_sql_query(f'''
                SELECT
                    t.*,
                    i.product_name,
                    b.brand_name,
                    ar.media_name as resource_name,
                    sc.channel_name,
                    (t.sale_price - t.ad_value - t.inventory_value) as net_profit,
                    t.sale_price as total_revenue
                FROM transactions t
                JOIN inventory i ON t.inventory_id = i.id
                JOIN brands b ON t.brand_id = b.id
                JOIN media_resources ar ON t.ad_resource_id = ar.id
                JOIN sales_channels sc ON t.channel_id = sc.id
                {date_condition}
                ORDER BY t.transaction_date DESC
            ''', conn, params=params)
            
            if transactions_df.empty:
                return "指定时间段内没有交易数据"
            
            # 计算财务指标
            total_revenue = transactions_df['total_revenue'].sum()
            total_cost = transactions_df['total_cost'].sum()
            total_profit = transactions_df['net_profit'].sum()
            total_transactions = len(transactions_df)
            
            # 按品类统计
            category_stats = transactions_df.groupby('product_name').agg({
                'sale_price': 'sum',
                'profit': 'sum',
                'id': 'count'
            }).rename(columns={'id': 'transaction_count'})
            
            # 按渠道统计
            channel_stats = transactions_df.groupby('channel_name').agg({
                'sale_price': 'sum',
                'profit': 'sum',
                'id': 'count'
            }).rename(columns={'id': 'transaction_count'})
            
            # 生成Excel报告
            filename = f"financial_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 总体统计
                summary_data = {
                    '指标': ['总收入', '总成本', '总利润', '交易笔数', '平均利润率', '投资回报率'],
                    '金额': [transactions_df['sale_price'].sum(),
                           (transactions_df['ad_value'].sum() + transactions_df['inventory_value'].sum()),
                           transactions_df['profit'].sum(),
                           total_transactions,
                           f"{(transactions_df['profit'].sum()/transactions_df['sale_price'].sum()*100):.2f}%",
                           f"{(transactions_df['profit'].sum()/(transactions_df['ad_value'].sum() + transactions_df['inventory_value'].sum())*100):.2f}%"]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='总体概况', index=False)
                
                # 品类统计
                category_stats.to_excel(writer, sheet_name='品类分析')
                
                # 渠道统计
                channel_stats.to_excel(writer, sheet_name='渠道分析')
                
                # 详细交易记录
                transactions_df.to_excel(writer, sheet_name='交易明细', index=False)
            
            return filename
            
        finally:
            conn.close()

if __name__ == "__main__":
    # 测试财务计算器
    calculator = FinancialCalculator()
    
    # 测试利润预测
    print("=== 利润预测报告 ===")
    forecast = calculator.generate_profit_forecast(months=3)
    print(f"历史月均利润: {forecast['historical_avg_profit']} 元")
    print(f"待处理库存价值: {forecast['pending_inventory_value']} 元")
    print(f"预测总利润: {forecast['total_predicted_profit']} 元")
    
    # 打印月度预测
    for month_data in forecast['monthly_forecast']:
        print(f"第{month_data['month']}月: 预测利润 {month_data['predicted_profit']} 元, "
              f"预计交易 {month_data['predicted_transactions']} 笔")
    
    print("\n=== 交易利润计算示例 ===")
    # 这里需要实际的ID进行测试
    # result = calculator.calculate_transaction_profit(1, 1, 1)
    # print(f"交易可行性: {result['feasibility']}")
    # print(f"净利润: {result['net_profit']} 元")
    # print(f"利润率: {result['profit_margin']:.2%}")
    # print(f"投资回报率: {result['return_on_investment']:.2%}")