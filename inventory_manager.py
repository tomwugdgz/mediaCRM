#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广告置换库存管理系统 - 核心数据库模型
用于管理广告资源、品牌方、商品库存、销售渠道等业务数据
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os

class InventoryManager:
    """广告置换库存管理核心类"""
    
    def __init__(self, db_path: str = "inventory.db"):
        """
        初始化库存管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 媒体资源表（增强版）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_name TEXT NOT NULL,
                media_type TEXT NOT NULL,  -- 社区门禁、写字楼电梯、户外大屏、公交站牌等
                media_form TEXT,  -- 媒体形式：静态、动态、LED、海报等
                location TEXT NOT NULL,
                market_price DECIMAL(10,2) NOT NULL,  -- 刊例价
                discount_rate DECIMAL(5,2) DEFAULT 100.0,  -- 折扣率（百分比）
                actual_cost DECIMAL(10,2) NOT NULL,   -- 实际成本（折扣后价格）
                media_specs TEXT,  -- 媒体规格：尺寸、分辨率等技术参数
                audience_info TEXT,  -- 受众信息：人流量、受众群体等
                status TEXT DEFAULT 'idle',  -- idle, occupied, maintenance, reserved
                owner_name TEXT,  -- 媒体主名称
                contact_person TEXT,  -- 联系人
                contact_phone TEXT,  -- 联系电话
                contract_start DATE,  -- 合同开始日期
                contract_end DATE,    -- 合同结束日期
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 如果旧的ad_resources表存在，迁移数据
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ad_resources'")
        if cursor.fetchone():
            # 迁移旧数据到新媒体表
            cursor.execute('''
                INSERT INTO media_resources (media_name, media_type, location, market_price,
                                           actual_cost, status, created_at, updated_at)
                SELECT resource_name, resource_type, location, market_price,
                       actual_cost, status, created_at, updated_at
                FROM ad_resources
            ''')
            # 删除旧表
            cursor.execute('DROP TABLE ad_resources')
        
        # 品牌方表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_name TEXT NOT NULL,
                contact_person TEXT,
                contact_phone TEXT,
                contact_email TEXT,
                brand_type TEXT,  -- 饮料、日化、家电等
                reputation_score INTEGER DEFAULT 5,  -- 品牌声誉评分1-10
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 商品库存表 - 先创建基础表结构
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_id INTEGER,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,  -- 饮料、日化、家电
                quantity INTEGER NOT NULL,
                original_value DECIMAL(10,2) NOT NULL,  -- 品牌方提供的账面价值
                market_value DECIMAL(10,2),  -- 市场实际价值（拼多多/闲鱼价）
                expiry_date DATE,  -- 保质期
                storage_location TEXT,
                status TEXT DEFAULT 'pending',  -- pending, approved, rejected, sold
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (brand_id) REFERENCES brands (id)
            )
        ''')
        
        # 添加商品链接字段（如果不存在）
        self.add_link_columns_if_not_exist(cursor)
        
        # 销售渠道表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name TEXT NOT NULL,
                channel_type TEXT NOT NULL,  -- S级(团长)、A级(批发市场)
                contact_person TEXT,
                contact_phone TEXT,
                commission_rate DECIMAL(5,2) DEFAULT 0,  -- 佣金比例
                payment_terms TEXT,  -- 结算方式
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER,
                ad_resource_id INTEGER,
                brand_id INTEGER,
                channel_id INTEGER,
                transaction_type TEXT NOT NULL,  -- barter, sale
                ad_value DECIMAL(10,2),  -- 广告价值
                inventory_value DECIMAL(10,2),  -- 库存价值
                sale_price DECIMAL(10,2),  -- 实际销售价格
                profit DECIMAL(10,2),  -- 利润
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed',  -- pending, completed, cancelled
                notes TEXT,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                FOREIGN KEY (ad_resource_id) REFERENCES media_resources (id),
                FOREIGN KEY (brand_id) REFERENCES brands (id),
                FOREIGN KEY (channel_id) REFERENCES sales_channels (id)
            )
        ''')
        
        # 风控规则表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL,  -- category, expiry, brand, value
                rule_config TEXT NOT NULL,  -- JSON格式的规则配置
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 初始化默认风控规则
        self.init_default_risk_rules(cursor)
        
        conn.commit()
        conn.close()
    
    def add_link_columns_if_not_exist(self, cursor):
        """添加商品链接字段（如果不存在）"""
        # 检查并添加京东链接字段
        cursor.execute("PRAGMA table_info(inventory)")
        columns = [column[1] for column in cursor.fetchall()]
        
        link_columns = {
            'jd_link': '京东商品链接',
            'tmall_link': '天猫商品链接',
            'xianyu_link': '闲鱼商品链接',
            'pdd_link': '拼多多商品链接'
        }
        
        for column_name, description in link_columns.items():
            if column_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE inventory ADD COLUMN {column_name} TEXT')
                    print(f"✅ 添加字段 {column_name}: {description}")
                except Exception as e:
                    print(f"⚠️ 添加字段 {column_name} 失败: {e}")
    
    def init_default_risk_rules(self, cursor):
        """初始化默认风控规则"""
        default_rules = [
            {
                'rule_name': '不接受美容卡服务券',
                'rule_type': 'category',
                'rule_config': json.dumps({
                    'forbidden_categories': ['美容卡', '服务券', '优惠券'],
                    'reason': '价值极虚，变现率<2%'
                })
            },
            {
                'rule_name': '不接受杂牌商品',
                'rule_type': 'brand',
                'rule_config': json.dumps({
                    'min_reputation_score': 6,
                    'reason': '团长不推，容易烂手里'
                })
            },
            {
                'rule_name': '不接受临期食品',
                'rule_type': 'expiry',
                'rule_config': json.dumps({
                    'min_expiry_months': 3,
                    'reason': '保质期<3个月，物流跑不赢时间'
                })
            },
            {
                'rule_name': '价值评估规则',
                'rule_type': 'value',
                'rule_config': json.dumps({
                    'min_realization_rate': 0.05,  # 最低变现率5%
                    'max_advertising_cost_ratio': 0.5,  # 广告成本不超过预期收入50%
                    'reason': '确保每笔交易都有足够利润空间'
                })
            }
        ]
        
        for rule in default_rules:
            cursor.execute('''
                INSERT OR IGNORE INTO risk_rules (rule_name, rule_type, rule_config)
                VALUES (?, ?, ?)
            ''', (rule['rule_name'], rule['rule_type'], rule['rule_config']))
    
    def add_media_resource(self, media_name: str, media_type: str, media_form: str,
                          location: str, market_price: float, discount_rate: float = 100.0,
                          actual_cost: float = None, media_specs: str = None,
                          audience_info: str = None, owner_name: str = None,
                          contact_person: str = None, contact_phone: str = None,
                          contract_start: str = None, contract_end: str = None) -> int:
        """
        添加媒体资源（增强版）
        
        Args:
            media_name: 媒体名称
            media_type: 媒体类型（社区门禁、写字楼电梯等）
            media_form: 媒体形式（静态、动态、LED等）
            location: 位置
            market_price: 刊例价
            discount_rate: 折扣率（百分比，默认100）
            actual_cost: 实际成本（如果为None则自动计算：market_price * discount_rate / 100）
            media_specs: 媒体规格
            audience_info: 受众信息
            owner_name: 媒体主名称
            contact_person: 联系人
            contact_phone: 联系电话
            contract_start: 合同开始日期
            contract_end: 合同结束日期
            
        Returns:
            新创建的资源ID
        """
        if actual_cost is None:
            actual_cost = market_price * discount_rate / 100
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO media_resources (media_name, media_type, media_form, location,
                                       market_price, discount_rate, actual_cost,
                                       media_specs, audience_info, owner_name,
                                       contact_person, contact_phone, contract_start,
                                       contract_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (media_name, media_type, media_form, location, market_price, discount_rate,
              actual_cost, media_specs, audience_info, owner_name, contact_person,
              contact_phone, contract_start, contract_end))
        
        resource_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return resource_id
    
    def add_brand(self, brand_name: str, contact_person: Optional[str] = None,
                  contact_phone: Optional[str] = None, contact_email: Optional[str] = None,
                  brand_type: Optional[str] = None, reputation_score: int = 5) -> int:
        """添加品牌方"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO brands (brand_name, contact_person, contact_phone, 
                              contact_email, brand_type, reputation_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (brand_name, contact_person, contact_phone, contact_email, 
              brand_type, reputation_score))
        
        brand_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return brand_id
    
    def add_media_resource(self, media_name: str, media_type: str, media_form: Optional[str] = None,
                           location: Optional[str] = None, market_price: float = 0,
                           discount_rate: float = 100.0, actual_cost: Optional[float] = None,
                           media_specs: Optional[str] = None, audience_info: Optional[str] = None,
                           owner_name: Optional[str] = None, contact_person: Optional[str] = None,
                           contact_phone: Optional[str] = None, contract_start: Optional[str] = None,
                           contract_end: Optional[str] = None) -> int:
        """
        添加媒体资源
        
        Returns:
            新创建的资源ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 如果没有提供实际成本，则自动计算
        if actual_cost is None:
            actual_cost = market_price * discount_rate / 100.0
        
        cursor.execute('''
            INSERT INTO media_resources (media_name, media_type, media_form, location,
                                       market_price, discount_rate, actual_cost, media_specs,
                                       audience_info, owner_name, contact_person, contact_phone,
                                       contract_start, contract_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (media_name, media_type, media_form, location, market_price, 
              discount_rate, actual_cost, media_specs, audience_info, owner_name,
              contact_person, contact_phone, contract_start, contract_end))
        
        resource_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return resource_id
    
    def add_ad_resource(self, resource_name: str, resource_type: str, 
                       location: str, market_price: float, actual_cost: float) -> int:
        """
        添加广告资源（兼容旧版本）
        
        Returns:
            新创建的资源ID
        """
        return self.add_media_resource(
            media_name=resource_name,
            media_type=resource_type,
            location=location,
            market_price=market_price,
            actual_cost=actual_cost
        )
    
    def add_inventory(self, brand_id: int, product_name: str, category: str,
                      quantity: int, original_value: float, market_value: Optional[float] = None,
                      expiry_date: Optional[str] = None, storage_location: Optional[str] = None,
                      jd_link: Optional[str] = None, tmall_link: Optional[str] = None,
                      xianyu_link: Optional[str] = None, pdd_link: Optional[str] = None) -> int:
        """添加库存商品"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO inventory (brand_id, product_name, category, quantity,
                                 original_value, market_value, expiry_date,
                                 storage_location, jd_link, tmall_link,
                                 xianyu_link, pdd_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (brand_id, product_name, category, quantity, original_value,
              market_value, expiry_date, storage_location, jd_link, tmall_link,
              xianyu_link, pdd_link))
        
        inventory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return inventory_id
    
    def update_inventory(self, inventory_id: int, **kwargs) -> bool:
        """
        更新库存商品信息
        
        Args:
            inventory_id: 库存ID
            **kwargs: 要更新的字段，如 product_name, category, quantity, original_value, market_value, expiry_date, storage_location, status
            
        Returns:
            更新成功返回True，失败返回False
        """
        conn = None
        try:
            # 参数验证
            if not inventory_id or inventory_id <= 0:
                print(f"❌ 无效的库存ID: {inventory_id}")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查库存是否存在
            cursor.execute('SELECT id FROM inventory WHERE id = ?', (inventory_id,))
            if not cursor.fetchone():
                print(f"❌ 库存记录不存在，ID: {inventory_id}")
                return False
            
            # 构建更新语句
            update_fields = []
            update_values = []
            
            allowed_fields = ['product_name', 'category', 'quantity', 'original_value',
                            'market_value', 'expiry_date', 'storage_location', 'status',
                            'jd_link', 'tmall_link', 'xianyu_link', 'pdd_link']
            
            # 验证并处理每个字段
            for field, value in kwargs.items():
                if field in allowed_fields:
                    # 特殊处理数值字段
                    if field in ['quantity', 'original_value', 'market_value']:
                        if value is not None:
                            try:
                                value = float(value) if field != 'quantity' else int(value)
                                if value < 0:
                                    print(f"⚠️ 字段 {field} 的值不能为负数: {value}")
                                    continue
                            except (ValueError, TypeError):
                                print(f"⚠️ 字段 {field} 的值无效: {value}")
                                continue
                    
                    # 特殊处理字符串字段
                    if field in ['product_name', 'category', 'status', 'storage_location']:
                        if value is not None:
                            value = str(value).strip()
                            if not value:
                                value = None
                    
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if not update_fields:
                print("⚠️ 没有有效的字段需要更新")
                return False
            
            # 添加更新时间
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(inventory_id)  # WHERE条件
            
            update_sql = f"UPDATE inventory SET {', '.join(update_fields)} WHERE id = ?"
            
            print(f"📝 执行更新SQL: {update_sql}")
            print(f"📝 更新参数: {update_values}")
            
            result = cursor.execute(update_sql, update_values)
            affected_rows = result.rowcount
            
            if affected_rows > 0:
                conn.commit()
                print(f"✅ 库存更新成功，影响行数: {affected_rows}")
                return True
            else:
                print("⚠️ 没有行被更新")
                return False
                
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ 数据库错误: {str(e)}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ 更新库存时发生错误: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()
    
    def update_brand(self, brand_id: int, **kwargs) -> bool:
        """
        更新品牌方信息
        
        Args:
            brand_id: 品牌ID
            **kwargs: 要更新的字段，如 brand_name, contact_person, contact_phone, contact_email, brand_type, reputation_score
            
        Returns:
            更新成功返回True，失败返回False
        """
        conn = None
        try:
            # 参数验证
            if not brand_id or brand_id <= 0:
                print(f"❌ 无效的品牌ID: {brand_id}")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查品牌是否存在
            cursor.execute('SELECT id FROM brands WHERE id = ?', (brand_id,))
            if not cursor.fetchone():
                print(f"❌ 品牌记录不存在，ID: {brand_id}")
                return False
            
            # 构建更新语句
            update_fields = []
            update_values = []
            
            allowed_fields = ['brand_name', 'contact_person', 'contact_phone',
                            'contact_email', 'brand_type', 'reputation_score']
            
            # 验证并处理每个字段
            for field, value in kwargs.items():
                if field in allowed_fields:
                    # 特殊处理字符串字段
                    if field in ['brand_name', 'contact_person', 'contact_phone', 'contact_email', 'brand_type']:
                        if value is not None:
                            value = str(value).strip()
                            if not value:
                                value = None
                    
                    # 特殊处理信誉评分
                    if field == 'reputation_score':
                        if value is not None:
                            try:
                                value = int(value)
                                if not (1 <= value <= 10):
                                    print(f"⚠️ 信誉评分必须在1-10之间: {value}")
                                    continue
                            except (ValueError, TypeError):
                                print(f"⚠️ 信誉评分必须是有效整数: {value}")
                                continue
                    
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if not update_fields:
                print("⚠️ 没有有效的字段需要更新")
                return False
            
            update_values.append(brand_id)  # WHERE条件
            
            update_sql = f"UPDATE brands SET {', '.join(update_fields)} WHERE id = ?"
            
            print(f"📝 执行品牌更新SQL: {update_sql}")
            print(f"📝 更新参数: {update_values}")
            
            result = cursor.execute(update_sql, update_values)
            affected_rows = result.rowcount
            
            if affected_rows > 0:
                conn.commit()
                print(f"✅ 品牌更新成功，影响行数: {affected_rows}")
                return True
            else:
                print("⚠️ 没有行被更新")
                return False
                
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ 数据库错误: {str(e)}")
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ 更新品牌时发生错误: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()
    
    def update_media_resource(self, resource_id: int, **kwargs) -> bool:
        """
        更新媒体资源信息（增强版）
        
        Args:
            resource_id: 资源ID
            **kwargs: 要更新的字段，如 media_name, media_type, media_form, location,
                     market_price, discount_rate, actual_cost, media_specs, audience_info,
                     owner_name, contact_person, contact_phone, contract_start, contract_end, status
            
        Returns:
            更新成功返回True，失败返回False
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查资源是否存在
            cursor.execute('SELECT id FROM media_resources WHERE id = ?', (resource_id,))
            if not cursor.fetchone():
                return False
            
            # 构建更新语句
            update_fields = []
            update_values = []
            
            allowed_fields = ['media_name', 'media_type', 'media_form', 'location',
                            'market_price', 'discount_rate', 'actual_cost', 'media_specs',
                            'audience_info', 'owner_name', 'contact_person', 'contact_phone',
                            'contract_start', 'contract_end', 'status']
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if not update_fields:
                return False
            
            # 添加更新时间
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(resource_id)  # WHERE条件
            
            update_sql = f"UPDATE media_resources SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(update_sql, update_values)
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_sales_channel(self, channel_id: int, **kwargs) -> bool:
        """
        更新销售渠道信息
        
        Args:
            channel_id: 渠道ID
            **kwargs: 要更新的字段，如 channel_name, channel_type, contact_person, contact_phone, commission_rate, payment_terms
            
        Returns:
            更新成功返回True，失败返回False
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查渠道是否存在
            cursor.execute('SELECT id FROM sales_channels WHERE id = ?', (channel_id,))
            if not cursor.fetchone():
                return False
            
            # 构建更新语句
            update_fields = []
            update_values = []
            
            allowed_fields = ['channel_name', 'channel_type', 'contact_person',
                            'contact_phone', 'commission_rate', 'payment_terms']
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
            
            if not update_fields:
                return False
            
            update_values.append(channel_id)  # WHERE条件
            
            update_sql = f"UPDATE sales_channels SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(update_sql, update_values)
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete_inventory(self, inventory_id: int) -> bool:
        """
        删除库存商品
        
        Args:
            inventory_id: 库存ID
            
        Returns:
            删除成功返回True，失败返回False
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查库存是否存在
            cursor.execute('SELECT id FROM inventory WHERE id = ?', (inventory_id,))
            if not cursor.fetchone():
                return False
            
            # 删除库存（如果有关联的交易记录，需要先处理）
            cursor.execute('DELETE FROM inventory WHERE id = ?', (inventory_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete_brand(self, brand_id: int) -> bool:
        """
        删除品牌方
        
        Args:
            brand_id: 品牌ID
            
        Returns:
            删除成功返回True，失败返回False
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查品牌是否存在
            cursor.execute('SELECT id FROM brands WHERE id = ?', (brand_id,))
            if not cursor.fetchone():
                return False
            
            # 检查是否有关联的库存
            cursor.execute('SELECT COUNT(*) FROM inventory WHERE brand_id = ?', (brand_id,))
            inventory_count = cursor.fetchone()[0]
            
            if inventory_count > 0:
                return False  # 有关联库存，不能删除
            
            # 删除品牌
            cursor.execute('DELETE FROM brands WHERE id = ?', (brand_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete_media_resource(self, resource_id: int) -> bool:
        """
        删除媒体资源
        
        Args:
            resource_id: 资源ID
            
        Returns:
            删除成功返回True，失败返回False
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查资源是否存在
            cursor.execute('SELECT id FROM media_resources WHERE id = ?', (resource_id,))
            if not cursor.fetchone():
                return False
            
            # 删除媒体资源
            cursor.execute('DELETE FROM media_resources WHERE id = ?', (resource_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete_sales_channel(self, channel_id: int) -> bool:
        """
        删除销售渠道
        
        Args:
            channel_id: 渠道ID
            
        Returns:
            删除成功返回True，失败返回False
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 检查渠道是否存在
            cursor.execute('SELECT id FROM sales_channels WHERE id = ?', (channel_id,))
            if not cursor.fetchone():
                return False
            
            # 删除销售渠道
            cursor.execute('DELETE FROM sales_channels WHERE id = ?', (channel_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def add_sales_channel(self, channel_name: str, channel_type: str,
                          contact_person: Optional[str] = None, contact_phone: Optional[str] = None,
                          commission_rate: float = 0, payment_terms: Optional[str] = None) -> int:
        """添加销售渠道"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sales_channels (channel_name, channel_type, contact_person, 
                                      contact_phone, commission_rate, payment_terms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (channel_name, channel_type, contact_person, contact_phone, 
              commission_rate, payment_terms))
        
        channel_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return channel_id
    
    def get_active_risk_rules(self) -> List[Dict]:
        """获取启用的风控规则"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rule_name, rule_type, rule_config 
            FROM risk_rules 
            WHERE is_active = 1
        ''')
        
        rules = []
        for row in cursor.fetchall():
            rules.append({
                'rule_name': row[0],
                'rule_type': row[1],
                'rule_config': json.loads(row[2])
            })
        
        conn.close()
        return rules
    
    def check_inventory_risk(self, inventory_id: int) -> Dict:
        """
        检查库存商品的风控合规性
        
        Returns:
            {'passed': bool, 'violations': List[str], 'suggestions': List[str]}
        """
        conn = sqlite3.connect(self.db_path)
        
        # 获取库存信息
        inventory_df = pd.read_sql_query('''
            SELECT i.*, b.brand_name, b.reputation_score, b.brand_type
            FROM inventory i
            JOIN brands b ON i.brand_id = b.id
            WHERE i.id = ?
        ''', conn, params=(inventory_id,))
        
        if inventory_df.empty:
            conn.close()
            return {'passed': False, 'violations': ['库存记录不存在'], 'suggestions': []}
        
        inventory = inventory_df.iloc[0]
        violations = []
        suggestions = []
        
        # 获取风控规则
        rules = self.get_active_risk_rules()
        
        for rule in rules:
            rule_config = rule['rule_config']
            
            if rule['rule_type'] == 'category':
                forbidden = rule_config.get('forbidden_categories', [])
                for category in forbidden:
                    if category in inventory['category'] or category in inventory['product_name']:
                        violations.append(f"{rule['rule_name']}: {rule_config['reason']}")
                        break
            
            elif rule['rule_type'] == 'brand':
                min_score = rule_config.get('min_reputation_score', 0)
                if inventory['reputation_score'] < min_score:
                    violations.append(f"{rule['rule_name']}: {rule_config['reason']}")
            
            elif rule['rule_type'] == 'expiry':
                if inventory['expiry_date']:
                    expiry_date = pd.to_datetime(inventory['expiry_date'])
                    min_months = rule_config.get('min_expiry_months', 0)
                    months_until_expiry = (expiry_date - datetime.now()).days / 30
                    if months_until_expiry < min_months:
                        violations.append(f"{rule['rule_name']}: {rule_config['reason']}")
            
            elif rule['rule_type'] == 'value':
                # 这里需要结合定价计算器的结果
                pass
        
        conn.close()
        
        return {
            'passed': len(violations) == 0,
            'violations': violations,
            'suggestions': suggestions
        }
    
    def get_inventory_summary(self) -> Dict:
        """获取库存概览"""
        conn = sqlite3.connect(self.db_path)
        
        # 库存统计
        inventory_stats = pd.read_sql_query('''
            SELECT 
                status,
                COUNT(*) as count,
                SUM(original_value) as total_value,
                SUM(quantity) as total_quantity
            FROM inventory
            GROUP BY status
        ''', conn)
        
        # 分类统计
        category_stats = pd.read_sql_query('''
            SELECT 
                category,
                COUNT(*) as count,
                SUM(original_value) as total_value
            FROM inventory
            GROUP BY category
        ''', conn)
        
        # 品牌统计
        brand_stats = pd.read_sql_query('''
            SELECT 
                b.brand_name,
                COUNT(i.id) as inventory_count,
                SUM(i.original_value) as total_value
            FROM brands b
            LEFT JOIN inventory i ON b.id = i.brand_id
            GROUP BY b.id, b.brand_name
        ''', conn)
        
        conn.close()
        
        return {
            'inventory_stats': inventory_stats.to_dict('records'),
            'category_stats': category_stats.to_dict('records'),
            'brand_stats': brand_stats.to_dict('records')
        }
    
    def get_inventory_by_id(self, inventory_id: int) -> Optional[Dict]:
        """
        根据ID获取库存商品信息
        
        Args:
            inventory_id: 库存ID
            
        Returns:
            库存商品信息字典，不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT i.*, b.brand_name
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            WHERE i.id = ?
        ''', (inventory_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # 获取列名
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(inventory)')
        columns = [column[1] for column in cursor.fetchall()]
        conn.close()
        
        # 添加品牌名称到结果中
        result = dict(zip(columns, row[:-1]))  # 排除最后一列的brand_name
        result['brand_name'] = row[-1]  # 添加品牌名称
        return result
    
    def get_brand_by_id(self, brand_id: int) -> Optional[Dict]:
        """
        根据ID获取品牌方信息
        
        Args:
            brand_id: 品牌ID
            
        Returns:
            品牌方信息字典，不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM brands WHERE id = ?', (brand_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # 获取列名
        cursor.execute('PRAGMA table_info(brands)')
        columns = [column[1] for column in cursor.fetchall()]
        
        conn.close()
        
        return dict(zip(columns, row))
    
    def get_all_inventory(self) -> List[Dict]:
        """
        获取所有库存商品信息
        
        Returns:
            库存商品信息列表
        """
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query('''
            SELECT i.*, b.brand_name
            FROM inventory i
            LEFT JOIN brands b ON i.brand_id = b.id
            ORDER BY i.created_at DESC
        ''', conn)
        
        conn.close()
        
        return df.to_dict('records')
    
    def get_all_brands(self) -> List[Dict]:
        """
        获取所有品牌方信息
        
        Returns:
            品牌方信息列表
        """
        conn = sqlite3.connect(self.db_path)
        
        df = pd.read_sql_query('SELECT * FROM brands ORDER BY created_at DESC', conn)
        
        conn.close()
        
        return df.to_dict('records')
    
    def export_to_excel(self, filename: str = None) -> str:
        """导出数据到Excel文件"""
        if not filename:
            filename = f"inventory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        conn = sqlite3.connect(self.db_path)
        
        # 导出各个表的数据
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 库存数据
            inventory_df = pd.read_sql_query('''
                SELECT i.*, b.brand_name 
                FROM inventory i
                LEFT JOIN brands b ON i.brand_id = b.id
            ''', conn)
            inventory_df.to_excel(writer, sheet_name='库存数据', index=False)
            
            # 品牌数据
            brands_df = pd.read_sql_query('SELECT * FROM brands', conn)
            brands_df.to_excel(writer, sheet_name='品牌数据', index=False)
            
            # 广告资源（优先使用新表，兼容旧表）
            try:
                ad_resources_df = pd.read_sql_query('SELECT * FROM media_resources', conn)
                ad_resources_df.to_excel(writer, sheet_name='广告资源', index=False)
            except:
                try:
                    ad_resources_df = pd.read_sql_query('SELECT * FROM ad_resources', conn)
                    ad_resources_df.to_excel(writer, sheet_name='广告资源', index=False)
                except:
                    # 如果两个表都不存在，创建空表
                    ad_resources_df = pd.DataFrame()
                    ad_resources_df.to_excel(writer, sheet_name='广告资源', index=False)
            
            # 销售渠道
            channels_df = pd.read_sql_query('SELECT * FROM sales_channels', conn)
            channels_df.to_excel(writer, sheet_name='销售渠道', index=False)
            
            # 交易记录
            transactions_df = pd.read_sql_query('''
                SELECT t.*,
                       i.product_name,
                       ar.media_name as resource_name,
                       b.brand_name,
                       sc.channel_name
                FROM transactions t
                LEFT JOIN inventory i ON t.inventory_id = i.id
                LEFT JOIN media_resources ar ON t.ad_resource_id = ar.id
                LEFT JOIN brands b ON t.brand_id = b.id
                LEFT JOIN sales_channels sc ON t.channel_id = sc.id
            ''', conn)
            transactions_df.to_excel(writer, sheet_name='交易记录', index=False)
        
        conn.close()
        return filename

if __name__ == "__main__":
    # 创建管理器实例
    manager = InventoryManager()
    
    # 添加一些示例数据
    print("正在初始化示例数据...")
    
    # 添加品牌方
    brand1 = manager.add_brand("可口可乐", "张经理", "13800138000", "zhang@coke.com", "饮料", 9)
    brand2 = manager.add_brand("蓝月亮", "李总监", "13900139000", "li@bluemoon.com", "日化", 8)
    
    # 添加广告资源
    ad1 = manager.add_ad_resource("社区门禁广告位A", "社区门禁", "朝阳区某小区", 5000.0, 200.0)
    ad2 = manager.add_ad_resource("写字楼电梯广告位B", "写字楼电梯", "CBD某大厦", 8000.0, 300.0)
    
    # 添加销售渠道
    channel1 = manager.add_sales_channel("王团长团购", "S级", "王团长", "13700137000", 5.0, "现结")
    channel2 = manager.add_sales_channel("临期市场档口A", "A级", "赵老板", "13600136000", 0.0, "批量结算")
    
    # 添加库存
    inv1 = manager.add_inventory(brand1, "可口可乐经典装", "饮料", 1000, 45000.0, 30000.0, "2025-06-30", "仓库A")
    inv2 = manager.add_inventory(brand2, "蓝月亮洗衣液", "日化", 500, 25000.0, 20000.0, "2025-12-31", "仓库B")
    
    print(f"数据库初始化完成！")
    print(f"品牌方数量: 2")
    print(f"广告资源数量: 2")
    print(f"库存商品数量: 2")
    print(f"销售渠道数量: 2")
    
    # 风控检查示例
    print("\n风控检查示例:")
    risk_result = manager.check_inventory_risk(inv1)
    print(f"库存ID {inv1} 风控结果: {risk_result}")
    
    # 导出数据
    print("\n正在导出数据...")
    export_file = manager.export_to_excel()
    print(f"数据已导出到: {export_file}")