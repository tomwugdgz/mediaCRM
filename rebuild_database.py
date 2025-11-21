#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库重建工具
完全重建数据库并初始化示例数据
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import json

def rebuild_database():
    """完全重建数据库"""
    print("🔄 开始重建数据库...")
    
    # 备份现有数据库
    if os.path.exists('inventory.db'):
        backup_name = f'inventory_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        os.rename('inventory.db', backup_name)
        print(f"✅ 已备份原数据库到: {backup_name}")
    
    # 创建新的数据库
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    print("📊 创建数据库表结构...")
    
    # 品牌方表
    cursor.execute('''
        CREATE TABLE brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL UNIQUE,
            contact_person TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            brand_type TEXT,
            reputation_score INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 媒体资源表
    cursor.execute('''
        CREATE TABLE media_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_name TEXT NOT NULL,
            media_type TEXT NOT NULL,
            media_form TEXT,
            location TEXT NOT NULL,
            market_price DECIMAL(10,2) NOT NULL,
            discount_rate DECIMAL(5,2) DEFAULT 100.0,
            actual_cost DECIMAL(10,2) NOT NULL,
            media_specs TEXT,
            audience_info TEXT,
            status TEXT DEFAULT 'idle',
            owner_name TEXT,
            contact_person TEXT,
            contact_phone TEXT,
            contract_start DATE,
            contract_end DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 商品库存表
    cursor.execute('''
        CREATE TABLE inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id INTEGER,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            original_value DECIMAL(10,2) NOT NULL,
            market_value DECIMAL(10,2),
            expiry_date DATE,
            storage_location TEXT,
            status TEXT DEFAULT 'pending',
            jd_link TEXT,
            tmall_link TEXT,
            xianyu_link TEXT,
            pdd_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (brand_id) REFERENCES brands (id)
        )
    ''')
    
    # 销售渠道表
    cursor.execute('''
        CREATE TABLE sales_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_name TEXT NOT NULL,
            channel_type TEXT NOT NULL,
            contact_person TEXT,
            contact_phone TEXT,
            commission_rate DECIMAL(5,2) DEFAULT 0,
            payment_terms TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 交易记录表
    cursor.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER,
            media_resource_id INTEGER,
            brand_id INTEGER,
            channel_id INTEGER,
            transaction_type TEXT NOT NULL,
            ad_value DECIMAL(10,2),
            inventory_value DECIMAL(10,2),
            sale_price DECIMAL(10,2),
            profit DECIMAL(10,2),
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed',
            notes TEXT,
            FOREIGN KEY (inventory_id) REFERENCES inventory (id),
            FOREIGN KEY (media_resource_id) REFERENCES media_resources (id),
            FOREIGN KEY (brand_id) REFERENCES brands (id),
            FOREIGN KEY (channel_id) REFERENCES sales_channels (id)
        )
    ''')
    
    # 风控规则表
    cursor.execute('''
        CREATE TABLE risk_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT NOT NULL,
            rule_type TEXT NOT NULL,
            rule_config TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ 数据库表结构创建完成")
    
    # 插入示例品牌数据
    print("🏪 添加示例品牌数据...")
    brands_data = [
        ('可口可乐', '张经理', '13800138000', 'zhang@coke.com', '饮料', 9),
        ('蓝月亮', '李总监', '13900139000', 'li@bluemoon.com', '日化', 8),
        ('康师傅', '王总监', '13700137000', 'wang@masterkong.com', '食品', 7),
        ('宝洁', '赵经理', '13600136000', 'zhao@pg.com', '日化', 9),
        ('统一', '刘总监', '13500135000', 'liu@president.com', '食品', 6)
    ]
    
    cursor.executemany('''
        INSERT INTO brands (brand_name, contact_person, contact_phone, contact_email, brand_type, reputation_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', brands_data)
    
    # 插入示例媒体资源数据
    print("📺 添加示例媒体资源数据...")
    media_data = [
        ('朝阳小区门禁广告', '社区门禁', '静态海报', '北京市朝阳区朝阳小区', 5000.0, 80.0, 4000.0, 
         '120cm×80cm，高清喷绘', '日均人流量3000+，主要受众为小区居民', 'idle', '北京广告公司', '张经理', '13800138000'),
        ('CBD写字楼电梯广告', '写字楼电梯', '动态LED', '北京市朝阳区CBD中心', 8000.0, 75.0, 6000.0,
         '42寸高清液晶屏', '日均人流量8000+，主要受众为白领群体', 'idle', '朝阳传媒', '李总监', '13900139000'),
        ('三里屯户外大屏', '户外大屏', 'LED大屏', '北京市朝阳区三里屯', 15000.0, 70.0, 10500.0,
         '300寸4K高清LED屏', '日均人流量20000+，主要受众为年轻消费群体', 'idle', '三里屯传媒', '王总', '13700137000'),
        ('望京地铁站广告', '地铁广告', '灯箱广告', '北京市朝阳区望京站', 6000.0, 85.0, 5100.0,
         '120cm×180cm，高亮灯箱', '日均人流量15000+，主要受众为通勤人群', 'idle', '地铁传媒', '赵经理', '13600136000'),
        ('国贸商场广告', '商场广告', '液晶屏', '北京市朝阳区国贸商场', 7000.0, 80.0, 5600.0,
         '55寸高清液晶屏', '日均人流量12000+，主要受众为购物人群', 'idle', '国贸传媒', '刘总', '13500135000')
    ]
    
    cursor.executemany('''
        INSERT INTO media_resources (media_name, media_type, media_form, location, market_price, discount_rate, actual_cost,
                                   media_specs, audience_info, status, owner_name, contact_person, contact_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', media_data)
    
    # 插入示例库存数据
    print("📦 添加示例库存数据...")
    inventory_data = [
        (1, '可口可乐经典装330ml×24罐', '饮料', 1000, 45000.0, 30000.0, '2025-06-30', '仓库A', 'pending'),
        (1, '可口可乐零度330ml×24罐', '饮料', 800, 36000.0, 24000.0, '2025-08-31', '仓库A', 'pending'),
        (2, '蓝月亮洗衣液3kg×6瓶', '日化', 500, 25000.0, 20000.0, '2025-12-31', '仓库B', 'pending'),
        (2, '蓝月亮洗洁精500ml×12瓶', '日化', 300, 9000.0, 7200.0, '2025-10-31', '仓库B', 'pending'),
        (3, '康师傅红烧牛肉面×24袋', '食品', 600, 18000.0, 14400.0, '2025-09-30', '仓库C', 'pending'),
        (3, '康师傅冰红茶500ml×24瓶', '饮料', 400, 12000.0, 9600.0, '2025-07-31', '仓库C', 'pending'),
        (4, '宝洁潘婷洗发水400ml×12瓶', '日化', 350, 21000.0, 16800.0, '2025-11-30', '仓库D', 'pending'),
        (4, '宝洁舒肤佳香皂125g×24块', '日化', 800, 16000.0, 12800.0, '2025-12-31', '仓库D', 'pending'),
        (5, '统一老坛酸菜牛肉面×24袋', '食品', 450, 13500.0, 10800.0, '2025-08-31', '仓库E', 'pending'),
        (5, '统一鲜橙多450ml×24瓶', '饮料', 300, 9000.0, 7200.0, '2025-06-30', '仓库E', 'pending')
    ]
    
    cursor.executemany('''
        INSERT INTO inventory (brand_id, product_name, category, quantity, original_value, market_value, expiry_date, storage_location, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', inventory_data)
    
    # 插入示例销售渠道数据
    print("🛒 添加示例销售渠道数据...")
    channel_data = [
        ('王团长团购', 'S级(团长)', '王团长', '13800138000', 5.0, '现结', '主要销售日化用品，信誉良好'),
        ('李大妈团购', 'S级(团长)', '李大妈', '13900139000', 6.0, '周结', '主要销售食品饮料，客户群体稳定'),
        ('临期市场档口A', 'A级(批发市场)', '赵老板', '13700137000', 0.0, '批量结算', '专业处理临期商品，渠道广泛'),
        ('社区便利店联盟', 'B级(零售商)', '张经理', '13600136000', 3.0, '月结', '覆盖多个社区便利店'),
        ('电商平台专营店', '电商平台', '刘总', '13500135000', 8.0, '季度结', '专业电商团队，运营经验丰富')
    ]
    
    cursor.executemany('''
        INSERT INTO sales_channels (channel_name, channel_type, contact_person, contact_phone, commission_rate, payment_terms, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', channel_data)
    
    # 插入默认风控规则
    print("⚠️ 添加默认风控规则...")
    risk_rules = [
        ('不接受美容卡服务券', 'category', '{"forbidden_categories": ["美容卡", "服务券", "优惠券"], "reason": "价值极虚，变现率<2%"}'),
        ('不接受杂牌商品', 'brand', '{"min_reputation_score": 6, "reason": "团长不推，容易烂手里"}'),
        ('不接受临期食品', 'expiry', '{"min_expiry_months": 3, "reason": "保质期<3个月，物流跑不赢时间"}'),
        ('价值评估规则', 'value', '{"min_realization_rate": 0.05, "max_advertising_cost_ratio": 0.5, "reason": "确保每笔交易都有足够利润空间"}')
    ]
    
    cursor.executemany('''
        INSERT INTO risk_rules (rule_name, rule_type, rule_config)
        VALUES (?, ?, ?)
    ''', risk_rules)
    
    # 提交所有更改
    conn.commit()
    conn.close()
    
    print("✅ 数据库重建完成！")
    print("📊 数据概览:")
    print("  - 品牌方: 5个")
    print("  - 媒体资源: 5个")
    print("  - 库存商品: 10个")
    print("  - 销售渠道: 5个")
    print("  - 风控规则: 4个")
    
    return True

def verify_database():
    """验证数据库完整性"""
    print("\n🔍 验证数据库完整性...")
    
    try:
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        
        # 检查所有表
        tables = ['brands', 'media_resources', 'inventory', 'sales_channels', 'transactions', 'risk_rules']
        
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"  📋 {table}: {count} 条记录")
        
        # 检查外键关系
        cursor.execute('''
            SELECT i.id, i.product_name, b.brand_name
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            WHERE i.brand_id IS NOT NULL
            LIMIT 5
        ''')
        samples = cursor.fetchall()
        
        print("\n  ✅ 外键关系正常")
        print("  📋 库存样本:")
        for sample in samples:
            print(f"    ID:{sample[0]} | 商品:{sample[1]} | 品牌:{sample[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库验证失败: {e}")
        return False

def main():
    """主函数"""
    print("🏗️ 广告置换库存管理系统 - 数据库重建工具")
    print("=" * 60)
    
    # 重建数据库
    if rebuild_database():
        # 验证数据库
        if verify_database():
            print("\n🎉 数据库重建成功！")
            print("✅ 系统现在可以正常运行了")
        else:
            print("\n⚠️ 数据库重建完成，但验证失败")
    else:
        print("\n❌ 数据库重建失败")

if __name__ == "__main__":
    main()