#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定价计算器 - 基于拼多多/闲鱼价格的市场价值评估
用于计算库存商品的实际变现价值和建议回收价格
"""

import requests
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3
import pandas as pd

class PricingCalculator:
    """定价计算器类"""
    
    def __init__(self, db_path: str = "inventory.db"):
        """
        初始化定价计算器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.session = requests.Session()
        
        # 设置请求头，模拟真实浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def search_pdd_price(self, product_name: str) -> Optional[float]:
        """
        搜索拼多多价格（模拟实现）
        实际应用中需要接入拼多多API或使用爬虫
        
        Args:
            product_name: 商品名称
            
        Returns:
            拼多多平台价格，失败返回None
        """
        # 这里是模拟数据，实际应该调用真实的拼多多API
        # 拼多多百亿补贴价格通常是市场最低价
        
        # 模拟价格数据库（实际应该通过API获取）
        mock_pdd_prices = {
            '可口可乐': 35.9,  # 24罐装
            '元气森林': 45.8,  # 12瓶装
            '蓝月亮洗衣液': 29.9,  # 3kg装
            '康师傅方便面': 12.5,  # 5包装
            '三只松鼠坚果': 89.0,  # 礼盒装
            '维达纸巾': 22.9,  # 10包装
            '小米充电宝': 59.0,  # 10000mAh
            '美的电饭煲': 199.0,  # 3L容量
        }
        
        # 模糊匹配
        for key, price in mock_pdd_prices.items():
            if key in product_name:
                return float(price)
        
        # 如果找不到匹配，返回一个估算值（实际应用中应该返回None）
        # 这里模拟无法获取价格的情况
        return None
    
    def search_xianyu_price(self, product_name: str) -> Optional[float]:
        """
        搜索闲鱼价格（模拟实现）
        实际应用中需要接入闲鱼API或使用爬虫
        
        Args:
            product_name: 商品名称
            
        Returns:
            闲鱼平台价格，失败返回None
        """
        # 模拟闲鱼价格数据库
        mock_xianyu_prices = {
            '可口可乐': 28.0,  # 通常是批发价，比拼多多更低
            '元气森林': 38.0,
            '蓝月亮洗衣液': 25.0,
            '康师傅方便面': 10.0,
            '三只松鼠坚果': 75.0,
            '维达纸巾': 18.0,
            '小米充电宝': 45.0,
            '美的电饭煲': 150.0,
        }
        
        # 模糊匹配
        for key, price in mock_xianyu_prices.items():
            if key in product_name:
                return float(price)
        
        return None
    
    def get_market_price_range(self, product_name: str) -> Dict[str, Optional[float]]:
        """
        获取商品的市场价格区间
        
        Returns:
            {
                'pdd_price': float or None,  # 拼多多价格
                'xianyu_price': float or None, # 闲鱼价格
                'recommended_price': float or None # 建议回收价格
            }
        """
        pdd_price = self.search_pdd_price(product_name)
        xianyu_price = self.search_xianyu_price(product_name)
        
        # 计算建议回收价格
        # 规则：建议回收价 = 闲鱼最低价 × 0.6（留出40%给渠道商赚）
        if xianyu_price:
            recommended_price = xianyu_price * 0.6
        elif pdd_price:
            # 如果没有闲鱼价格，用拼多多价格作为参考
            recommended_price = pdd_price * 0.5  # 拼多多价格的50%
        else:
            recommended_price = None
        
        return {
            'pdd_price': pdd_price,
            'xianyu_price': xianyu_price,
            'recommended_price': recommended_price
        }
    
    def calculate_realization_value(self, inventory_id: int) -> Dict:
        """
        计算库存商品的实际变现价值
        
        Returns:
            {
                'inventory_id': int,
                'product_name': str,
                'original_value': float,  # 原始价值
                'market_value': float,    # 市场价值
                'realization_rate': float, # 变现率
                'recommended_sale_price': float, # 建议销售价格
                'expected_cash_return': float,   # 预期现金回报
                'profit_margin': float,          # 利润率
                'risk_level': str                # 风险等级
            }
        """
        conn = sqlite3.connect(self.db_path)
        
        # 获取库存信息
        try:
            inventory_df = pd.read_sql_query('''
                SELECT i.*, b.brand_name, b.reputation_score
                FROM inventory i
                JOIN brands b ON i.brand_id = b.id
                WHERE i.id = ?
            ''', conn, params=(inventory_id,))
            
            if inventory_df.empty:
                conn.close()
                print(f"⚠️ 定价计算器：库存记录不存在，ID: {inventory_id}")
                return {'error': f'库存记录不存在，ID: {inventory_id}'}
        except Exception as e:
            conn.close()
            print(f"❌ 定价计算器：获取库存信息失败，ID: {inventory_id}, 错误: {str(e)}")
            return {'error': f'获取库存信息失败: {str(e)}'}
        
        inventory = inventory_df.iloc[0]
        
        # 获取市场价格
        price_info = self.get_market_price_range(inventory['product_name'])
        
        # 计算变现价值
        original_value = float(inventory['original_value'])
        
        # 计算市场价值（基于拼多多或闲鱼价格）
        if price_info['xianyu_price']:
            market_value = price_info['xianyu_price']
        elif price_info['pdd_price']:
            market_value = price_info['pdd_price']
        else:
            market_value = original_value * 0.3  # 默认按原值30%
        
        # 变现率（实际变现金额占原始价值的比例）
        # 根据文档，接受5-8%的实际变现率
        if price_info['recommended_price']:
            # 基于建议回收价计算
            realization_value = price_info['recommended_price'] * inventory['quantity']
            realization_rate = realization_value / original_value
        else:
            # 使用默认变现率
            realization_rate = 0.08  # 8%的变现率
            realization_value = original_value * realization_rate
        
        # 建议销售价格（给渠道商的价格）
        if price_info['recommended_price']:
            recommended_sale_price = price_info['recommended_price']
        else:
            recommended_sale_price = market_value * 0.6
        
        # 预期现金回报
        expected_cash_return = realization_value
        
        # 计算利润率
        # 需要获取广告成本
        profit_margin = 0  # 这里需要更多数据计算
        
        # 风险等级评估
        risk_level = self.assess_risk_level(inventory, price_info)
        
        # 更新数据库中的市场价值
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE inventory 
            SET market_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (market_value, inventory_id))
        conn.commit()
        
        conn.close()
        
        return {
            'inventory_id': inventory_id,
            'product_name': inventory['product_name'],
            'original_value': original_value,
            'market_value': market_value,
            'realization_rate': realization_rate,
            'recommended_sale_price': recommended_sale_price,
            'expected_cash_return': expected_cash_return,
            'profit_margin': profit_margin,
            'risk_level': risk_level,
            'price_sources': price_info
        }
    
    def assess_risk_level(self, inventory: pd.Series, price_info: Dict) -> str:
        """
        评估风险等级
        
        Returns:
            'low', 'medium', 'high'
        """
        risk_score = 0
        
        # 品牌声誉评分
        reputation_score = inventory.get('reputation_score', 5)
        if reputation_score >= 8:
            risk_score += 1
        elif reputation_score >= 6:
            risk_score += 2
        else:
            risk_score += 3
        
        # 保质期风险
        if inventory.get('expiry_date'):
            expiry_date = pd.to_datetime(inventory['expiry_date'])
            months_until_expiry = (expiry_date - datetime.now()).days / 30
            
            if months_until_expiry >= 6:
                risk_score += 1
            elif months_until_expiry >= 3:
                risk_score += 2
            else:
                risk_score += 5  # 临期商品风险很高
        
        # 价格稳定性
        if price_info['pdd_price'] and price_info['xianyu_price']:
            price_diff = abs(price_info['pdd_price'] - price_info['xianyu_price'])
            price_diff_ratio = price_diff / max(price_info['pdd_price'], price_info['xianyu_price'])
            
            if price_diff_ratio < 0.2:
                risk_score += 1  # 价格稳定
            elif price_diff_ratio < 0.4:
                risk_score += 2
            else:
                risk_score += 3  # 价格波动大
        else:
            risk_score += 3  # 缺乏价格数据
        
        # 根据风险评分返回等级
        if risk_score <= 3:
            return 'low'
        elif risk_score <= 6:
            return 'medium'
        else:
            return 'high'
    
    def batch_calculate_prices(self, inventory_ids: List[int]) -> List[Dict]:
        """批量计算多个库存商品的价格"""
        results = []
        for inventory_id in inventory_ids:
            result = self.calculate_realization_value(inventory_id)
            results.append(result)
            time.sleep(random.uniform(0.5, 1.5))  # 避免请求过快
        
        return results
    
    def generate_pricing_report(self, inventory_ids: List[int] = None) -> str:
        """
        生成定价分析报告
        
        Returns:
            报告文件路径
        """
        conn = sqlite3.connect(self.db_path)
        
        if inventory_ids:
            # 获取指定库存
            placeholders = ','.join(['?' for _ in inventory_ids])
            inventory_df = pd.read_sql_query(f'''
                SELECT i.*, b.brand_name, b.reputation_score
                FROM inventory i
                JOIN brands b ON i.brand_id = b.id
                WHERE i.id IN ({placeholders})
            ''', conn, params=inventory_ids)
        else:
            # 获取所有待定价的库存
            inventory_df = pd.read_sql_query('''
                SELECT i.*, b.brand_name, b.reputation_score
                FROM inventory i
                JOIN brands b ON i.brand_id = b.id
                WHERE i.status = 'pending' OR i.market_value IS NULL
            ''', conn)
        
        if inventory_df.empty:
            conn.close()
            return "没有需要定价的库存商品"
        
        # 计算每个商品的价格
        pricing_results = []
        for _, inventory in inventory_df.iterrows():
            price_info = self.get_market_price_range(inventory['product_name'])
            realization_result = self.calculate_realization_value(inventory['id'])
            pricing_results.append(realization_result)
        
        conn.close()
        
        # 生成Excel报告
        report_df = pd.DataFrame(pricing_results)
        
        filename = f"pricing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 主要报告
            report_df.to_excel(writer, sheet_name='定价分析', index=False)
            
            # 汇总统计
            summary_data = {
                '总商品数': [len(report_df)],
                '总原始价值': [report_df['original_value'].sum()],
                '总预期回报': [report_df['expected_cash_return'].sum()],
                '平均变现率': [report_df['realization_rate'].mean()],
                '低风险商品数': [len(report_df[report_df['risk_level'] == 'low'])],
                '高风险商品数': [len(report_df[report_df['risk_level'] == 'high'])]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='汇总统计', index=False)
        
        return filename

class PricingRuleEngine:
    """定价规则引擎"""
    
    def __init__(self):
        self.rules = {
            'high_reputation_bonus': 0.05,  # 高声誉品牌加成5%
            'low_reputation_penalty': -0.1,  # 低声誉品牌惩罚10%
            'expiry_discount': {
                '6_months': 0.0,     # 6个月以上无折扣
                '3_6_months': -0.05, # 3-6个月折扣5%
                '1_3_months': -0.15, # 1-3个月折扣15%
                '1_month': -0.3      # 1个月内折扣30%
            },
            'category_multipliers': {
                '饮料': 1.0,      # 标准变现率
                '日化': 0.9,      # 日化品稍低
                '家电': 0.7,      # 家电变现率较低
                '食品': 1.1       # 食品变现率较高
            }
        }
    
    def apply_pricing_rules(self, base_price: float, inventory_info: Dict) -> float:
        """
        应用定价规则调整价格
        
        Returns:
            调整后的价格
        """
        adjusted_price = base_price
        
        # 品牌声誉调整
        reputation_score = inventory_info.get('reputation_score', 5)
        if reputation_score >= 8:
            adjusted_price *= (1 + self.rules['high_reputation_bonus'])
        elif reputation_score <= 4:
            adjusted_price *= (1 + self.rules['low_reputation_penalty'])
        
        # 保质期调整
        expiry_date = inventory_info.get('expiry_date')
        if expiry_date:
            months_until_expiry = (pd.to_datetime(expiry_date) - datetime.now()).days / 30
            
            if months_until_expiry < 1:
                adjusted_price *= (1 + self.rules['expiry_discount']['1_month'])
            elif months_until_expiry < 3:
                adjusted_price *= (1 + self.rules['expiry_discount']['1_3_months'])
            elif months_until_expiry < 6:
                adjusted_price *= (1 + self.rules['expiry_discount']['3_6_months'])
        
        # 品类调整
        category = inventory_info.get('category', '')
        if category in self.rules['category_multipliers']:
            adjusted_price *= self.rules['category_multipliers'][category]
        
        return max(adjusted_price, base_price * 0.3)  # 最低不低于原价的30%

if __name__ == "__main__":
    # 测试定价计算器
    calculator = PricingCalculator()
    
    # 测试单个商品定价
    test_products = [
        "可口可乐经典装",
        "元气森林气泡水",
        "蓝月亮洗衣液",
        "康师傅方便面",
        "三只松鼠坚果礼盒"
    ]
    
    print("=== 定价计算器测试 ===")
    for product in test_products:
        price_info = calculator.get_market_price_range(product)
        print(f"\n商品: {product}")
        print(f"拼多多价格: {price_info['pdd_price']}")
        print(f"闲鱼价格: {price_info['xianyu_price']}")
        print(f"建议回收价: {price_info['recommended_price']}")
        
        if price_info['recommended_price']:
            print(f"变现率估算: {price_info['recommended_price'] / (price_info['xianyu_price'] or price_info['pdd_price']):.2%}")
    
    # 测试批量定价报告生成
    print("\n=== 生成定价报告 ===")
    # 这里需要实际的inventory_id
    # report_file = calculator.generate_pricing_report([1, 2])
    # print(f"报告已生成: {report_file}")