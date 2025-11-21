#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导入导出工具
支持Excel、CSV等格式的数据导入导出，以及数据模板生成
"""

import pandas as pd
import sqlite3
from datetime import datetime
import os
import json
from typing import Dict, List, Optional, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataImporter:
    """数据导入导出工具类"""
    
    def __init__(self, db_path: str = "inventory.db"):
        """
        初始化数据导入导出工具
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        
        # 定义标准的数据模板结构
        self.templates = {
            'brands': {
                'columns': ['brand_name', 'contact_person', 'contact_phone', 'contact_email', 'brand_type', 'reputation_score'],
                'required': ['brand_name'],
                'defaults': {
                    'reputation_score': 5
                }
            },
            'inventory': {
                'columns': ['brand_name', 'product_name', 'category', 'quantity', 'original_value', 'market_value', 'expiry_date', 'storage_location'],
                'required': ['brand_name', 'product_name', 'category', 'quantity', 'original_value'],
                'defaults': {}
            },
            'media_resources': {
                'columns': ['media_name', 'media_type', 'location', 'market_price', 'actual_cost'],
                'required': ['media_name', 'media_type', 'location', 'market_price', 'actual_cost'],
                'defaults': {}
            },
            'sales_channels': {
                'columns': ['channel_name', 'channel_type', 'contact_person', 'contact_phone', 'commission_rate', 'payment_terms'],
                'required': ['channel_name', 'channel_type'],
                'defaults': {
                    'commission_rate': 0
                }
            }
        }
    
    def generate_template(self, template_type: str, filename: str = None) -> str:
        """
        生成数据导入模板
        
        Args:
            template_type: 模板类型 ('brands', 'inventory', 'media_resources', 'sales_channels')
            filename: 输出文件名，如果为None则自动生成
            
        Returns:
            生成的文件名
        """
        if template_type not in self.templates:
            raise ValueError(f"不支持的模板类型: {template_type}")
        
        if not filename:
            filename = f"{template_type}_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        template_info = self.templates[template_type]
        
        # 创建示例数据
        sample_data = self._generate_sample_data(template_type)
        df = pd.DataFrame(sample_data)
        
        # 创建Excel文件，包含说明和模板两个工作表
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 主模板工作表
            df.to_excel(writer, sheet_name='模板数据', index=False)
            
            # 说明文档工作表
            instructions = self._generate_instructions(template_type)
            instructions_df = pd.DataFrame(instructions)
            instructions_df.to_excel(writer, sheet_name='使用说明', index=False)
            
            # 列说明工作表
            column_descriptions = self._generate_column_descriptions(template_type)
            desc_df = pd.DataFrame(column_descriptions)
            desc_df.to_excel(writer, sheet_name='列说明', index=False)
        
        logger.info(f"模板文件已生成: {filename}")
        return filename
    
    def _generate_sample_data(self, template_type: str) -> List[Dict]:
        """生成示例数据"""
        sample_data_map = {
            'brands': [
                {
                    'brand_name': '可口可乐',
                    'contact_person': '张经理',
                    'contact_phone': '13800138000',
                    'contact_email': 'zhang@coke.com',
                    'brand_type': '饮料',
                    'reputation_score': 9
                },
                {
                    'brand_name': '蓝月亮',
                    'contact_person': '李总监',
                    'contact_phone': '13900139000',
                    'contact_email': 'li@bluemoon.com',
                    'brand_type': '日化',
                    'reputation_score': 8
                }
            ],
            'inventory': [
                {
                    'brand_name': '可口可乐',
                    'product_name': '可口可乐经典装',
                    'category': '饮料',
                    'quantity': 1000,
                    'original_value': 45000.0,
                    'market_value': 30000.0,
                    'expiry_date': '2025-06-30',
                    'storage_location': '仓库A'
                },
                {
                    'brand_name': '蓝月亮',
                    'product_name': '蓝月亮洗衣液',
                    'category': '日化',
                    'quantity': 500,
                    'original_value': 25000.0,
                    'market_value': 20000.0,
                    'expiry_date': '2025-12-31',
                    'storage_location': '仓库B'
                }
            ],
            'media_resources': [
                {
                    'media_name': '社区门禁广告位A',
                    'media_type': '社区门禁',
                    'location': '朝阳区某小区',
                    'market_price': 5000.0,
                    'actual_cost': 200.0
                },
                {
                    'media_name': '写字楼电梯广告位B',
                    'media_type': '写字楼电梯',
                    'location': 'CBD某大厦',
                    'market_price': 8000.0,
                    'actual_cost': 300.0
                }
            ],
            'sales_channels': [
                {
                    'channel_name': '王团长团购',
                    'channel_type': 'S级',
                    'contact_person': '王团长',
                    'contact_phone': '13700137000',
                    'commission_rate': 5.0,
                    'payment_terms': '现结'
                },
                {
                    'channel_name': '临期市场档口A',
                    'channel_type': 'A级',
                    'contact_person': '赵老板',
                    'contact_phone': '13600136000',
                    'commission_rate': 0.0,
                    'payment_terms': '批量结算'
                }
            ]
        }
        
        return sample_data_map.get(template_type, [])
    
    def _generate_instructions(self, template_type: str) -> List[Dict]:
        """生成使用说明"""
        instructions_map = {
            'brands': [
                {'步骤': '1', '说明': '在"模板数据"工作表中填写品牌信息'},
                {'步骤': '2', '说明': '品牌名称不能为空，必须唯一'},
                {'步骤': '3', '说明': '品牌声誉评分范围为1-10，10为最高'},
                {'步骤': '4', '说明': '联系信息可选，但建议填写完整'},
                {'步骤': '5', '说明': '保存文件后使用导入功能导入数据'}
            ],
            'inventory': [
                {'步骤': '1', '说明': '在"模板数据"工作表中填写库存信息'},
                {'步骤': '2', '说明': '品牌名称必须已在系统中存在'},
                {'步骤': '3', '说明': '商品名称、品类、数量、原始价值为必填项'},
                {'步骤': '4', '说明': '保质期格式为YYYY-MM-DD，可选'},
                {'步骤': '5', '说明': '保存文件后使用导入功能导入数据'}
            ],
            'media_resources': [
                {'步骤': '1', '说明': '在"模板数据"工作表中填写媒体资源信息'},
                {'步骤': '2', '说明': '所有字段都为必填项'},
                {'步骤': '3', '说明': '刊例价应高于实际成本'},
                {'步骤': '4', '说明': '媒体类型包括: 社区门禁、写字楼电梯等'},
                {'步骤': '5', '说明': '保存文件后使用导入功能导入数据'}
            ],
            'sales_channels': [
                {'步骤': '1', '说明': '在"模板数据"工作表中填写销售渠道信息'},
                {'步骤': '2', '说明': '渠道名称、渠道类型为必填项'},
                {'步骤': '3', '说明': '渠道类型: S级(团长)、A级(批发市场)'},
                {'步骤': '4', '说明': '佣金比例为小数，如5%填写5.0'},
                {'步骤': '5', '说明': '保存文件后使用导入功能导入数据'}
            ]
        }
        
        return instructions_map.get(template_type, [])
    
    def _generate_column_descriptions(self, template_type: str) -> List[Dict]:
        """生成列说明"""
        descriptions_map = {
            'brands': [
                {'列名': 'brand_name', '说明': '品牌名称，必填，唯一', '示例': '可口可乐', '数据类型': '文本'},
                {'列名': 'contact_person', '说明': '联系人姓名，可选', '示例': '张经理', '数据类型': '文本'},
                {'列名': 'contact_phone', '说明': '联系电话，可选', '示例': '13800138000', '数据类型': '文本'},
                {'列名': 'contact_email', '说明': '联系邮箱，可选', '示例': 'zhang@coke.com', '数据类型': '文本'},
                {'列名': 'brand_type', '说明': '品牌类型，可选', '示例': '饮料', '数据类型': '文本'},
                {'列名': 'reputation_score', '说明': '品牌声誉评分，可选，1-10', '示例': '9', '数据类型': '数字'}
            ],
            'inventory': [
                {'列名': 'brand_name', '说明': '品牌名称，必填，必须存在', '示例': '可口可乐', '数据类型': '文本'},
                {'列名': 'product_name', '说明': '商品名称，必填', '示例': '可口可乐经典装', '数据类型': '文本'},
                {'列名': 'category', '说明': '商品品类，必填', '示例': '饮料', '数据类型': '文本'},
                {'列名': 'quantity', '说明': '数量，必填', '示例': '1000', '数据类型': '数字'},
                {'列名': 'original_value', '说明': '原始价值，必填', '示例': '45000.0', '数据类型': '数字'},
                {'列名': 'market_value', '说明': '市场价值，可选', '示例': '30000.0', '数据类型': '数字'},
                {'列名': 'expiry_date', '说明': '保质期，可选', '示例': '2025-06-30', '数据类型': '日期'},
                {'列名': 'storage_location', '说明': '存储位置，可选', '示例': '仓库A', '数据类型': '文本'}
            ],
            'media_resources': [
                {'列名': 'media_name', '说明': '媒体名称，必填', '示例': '社区门禁广告位A', '数据类型': '文本'},
                {'列名': 'media_type', '说明': '媒体类型，必填', '示例': '社区门禁', '数据类型': '文本'},
                {'列名': 'location', '说明': '位置，必填', '示例': '朝阳区某小区', '数据类型': '文本'},
                {'列名': 'market_price', '说明': '刊例价，必填', '示例': '5000.0', '数据类型': '数字'},
                {'列名': 'actual_cost', '说明': '实际成本，必填', '示例': '200.0', '数据类型': '数字'}
            ],
            'sales_channels': [
                {'列名': 'channel_name', '说明': '渠道名称，必填', '示例': '王团长团购', '数据类型': '文本'},
                {'列名': 'channel_type', '说明': '渠道类型，必填', '示例': 'S级', '数据类型': '文本'},
                {'列名': 'contact_person', '说明': '联系人，可选', '示例': '王团长', '数据类型': '文本'},
                {'列名': 'contact_phone', '说明': '联系电话，可选', '示例': '13700137000', '数据类型': '文本'},
                {'列名': 'commission_rate', '说明': '佣金比例，可选', '示例': '5.0', '数据类型': '数字'},
                {'列名': 'payment_terms', '说明': '结算方式，可选', '示例': '现结', '数据类型': '文本'}
            ]
        }
        
        return descriptions_map.get(template_type, [])
    
    def import_from_excel(self, filename: str, import_type: str) -> Dict[str, Any]:
        """
        从Excel文件导入数据
        
        Args:
            filename: Excel文件名
            import_type: 导入类型 ('brands', 'inventory', 'media_resources', 'sales_channels')
            
        Returns:
            导入结果统计
        """
        if import_type not in self.templates:
            raise ValueError(f"不支持的导入类型: {import_type}")
        
        if not os.path.exists(filename):
            raise FileNotFoundError(f"文件不存在: {filename}")
        
        try:
            # 读取Excel文件
            df = pd.read_excel(filename, sheet_name='模板数据')
            
            if df.empty:
                return {'success': False, 'message': 'Excel文件为空', 'imported': 0, 'failed': 0}
            
            # 验证必填字段
            template_info = self.templates[import_type]
            required_fields = template_info['required']
            
            missing_fields = []
            for field in required_fields:
                if field not in df.columns:
                    missing_fields.append(field)
                elif df[field].isnull().all():
                    missing_fields.append(f"{field}(全部为空)")
            
            if missing_fields:
                return {
                    'success': False, 
                    'message': f'缺少必填字段: {", ".join(missing_fields)}',
                    'imported': 0, 
                    'failed': 0
                }
            
            # 数据清洗和验证
            df = self._clean_and_validate_data(df, import_type)
            
            # 导入数据
            return self._import_data(df, import_type)
            
        except Exception as e:
            logger.error(f"导入失败: {str(e)}")
            return {'success': False, 'message': f'导入失败: {str(e)}', 'imported': 0, 'failed': 0}
    
    def _clean_and_validate_data(self, df: pd.DataFrame, import_type: str) -> pd.DataFrame:
        """清洗和验证数据"""
        # 去除空行
        df = df.dropna(how='all')
        
        # 去除前后空格
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            # 将空字符串转换为None
            df[col] = df[col].replace('', None)
        
        # 数据类型转换
        if import_type == 'brands':
            # 声誉评分转换为整数
            if 'reputation_score' in df.columns:
                df['reputation_score'] = pd.to_numeric(df['reputation_score'], errors='coerce')
                df['reputation_score'] = df['reputation_score'].fillna(5)
                df['reputation_score'] = df['reputation_score'].clip(1, 10)
        
        elif import_type == 'inventory':
            # 数值字段转换
            numeric_fields = ['quantity', 'original_value', 'market_value']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
            
            # 日期字段转换
            if 'expiry_date' in df.columns:
                df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce')
                df['expiry_date'] = df['expiry_date'].dt.strftime('%Y-%m-%d')
        
        elif import_type == 'media_resources':
            # 数值字段转换
            numeric_fields = ['market_price', 'actual_cost']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
        
        elif import_type == 'sales_channels':
            # 佣金比例转换
            if 'commission_rate' in df.columns:
                df['commission_rate'] = pd.to_numeric(df['commission_rate'], errors='coerce')
                df['commission_rate'] = df['commission_rate'].fillna(0)
        
        return df
    
    def _import_data(self, df: pd.DataFrame, import_type: str) -> Dict[str, Any]:
        """导入数据到数据库"""
        from inventory_manager import InventoryManager
        
        manager = InventoryManager()
        imported_count = 0
        failed_count = 0
        errors = []
        
        try:
            conn = sqlite3.connect(manager.db_path)
            cursor = conn.cursor()
            
            for index, row in df.iterrows():
                try:
                    if import_type == 'brands':
                        brand_id = manager.add_brand(
                            brand_name=row['brand_name'],
                            contact_person=row.get('contact_person'),
                            contact_phone=row.get('contact_phone'),
                            contact_email=row.get('contact_email'),
                            brand_type=row.get('brand_type'),
                            reputation_score=row.get('reputation_score', 5)
                        )
                        if brand_id:
                            imported_count += 1
                    
                    elif import_type == 'inventory':
                        # 需要先获取品牌ID
                        brand_name = row['brand_name']
                        cursor.execute('SELECT id FROM brands WHERE brand_name = ?', (brand_name,))
                        brand_result = cursor.fetchone()
                        
                        if brand_result:
                            inventory_id = manager.add_inventory(
                                brand_id=brand_result[0],
                                product_name=row['product_name'],
                                category=row['category'],
                                quantity=int(row['quantity']),
                                original_value=float(row['original_value']),
                                market_value=row.get('market_value'),
                                expiry_date=row.get('expiry_date'),
                                storage_location=row.get('storage_location')
                            )
                            if inventory_id:
                                imported_count += 1
                        else:
                            failed_count += 1
                            errors.append(f"第{index + 1}行: 品牌 '{brand_name}' 不存在")
                    
                    elif import_type == 'media_resources':
                        resource_id = manager.add_media_resource(
                            media_name=row['media_name'],
                            media_type=row['media_type'],
                            location=row['location'],
                            market_price=float(row['market_price']),
                            actual_cost=float(row['actual_cost'])
                        )
                        if resource_id:
                            imported_count += 1
                    
                    elif import_type == 'sales_channels':
                        channel_id = manager.add_sales_channel(
                            channel_name=row['channel_name'],
                            channel_type=row['channel_type'],
                            contact_person=row.get('contact_person'),
                            contact_phone=row.get('contact_phone'),
                            commission_rate=row.get('commission_rate', 0),
                            payment_terms=row.get('payment_terms')
                        )
                        if channel_id:
                            imported_count += 1
                
                except Exception as e:
                    failed_count += 1
                    errors.append(f"第{index + 1}行: {str(e)}")
            
            conn.close()
            
            result = {
                'success': True,
                'imported': imported_count,
                'failed': failed_count,
                'total': len(df)
            }
            
            if errors:
                result['errors'] = errors[:10]  # 只显示前10个错误
            
            logger.info(f"数据导入完成: 成功 {imported_count}, 失败 {failed_count}")
            return result
            
        except Exception as e:
            logger.error(f"数据导入失败: {str(e)}")
            return {
                'success': False,
                'message': f'数据导入失败: {str(e)}',
                'imported': imported_count,
                'failed': failed_count
            }
    
    def export_to_csv(self, table_name: str, filename: str = None) -> str:
        """
        导出数据到CSV文件
        
        Args:
            table_name: 表名
            filename: 输出文件名，如果为None则自动生成
            
        Returns:
            生成的文件名
        """
        if not filename:
            filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 获取表数据
            if table_name == 'inventory':
                query = '''
                    SELECT i.*, b.brand_name 
                    FROM inventory i
                    LEFT JOIN brands b ON i.brand_id = b.id
                '''
            elif table_name == 'transactions':
                query = '''
                    SELECT 
                        t.*,
                        i.product_name,
                        b.brand_name,
                        ar.resource_name,
                        sc.channel_name
                    FROM transactions t
                    LEFT JOIN inventory i ON t.inventory_id = i.id
                    LEFT JOIN brands b ON t.brand_id = b.id
                    LEFT JOIN ad_resources ar ON t.ad_resource_id = ar.id
                    LEFT JOIN sales_channels sc ON t.channel_id = sc.id
                '''
            else:
                query = f'SELECT * FROM {table_name}'
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                logger.warning(f"表 {table_name} 没有数据")
                return None
            
            # 导出到CSV
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"数据已导出到CSV: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"CSV导出失败: {str(e)}")
            return None
    
    def validate_data_quality(self, filename: str, data_type: str) -> Dict[str, Any]:
        """
        验证数据质量
        
        Args:
            filename: 数据文件路径
            data_type: 数据类型
            
        Returns:
            验证结果
        """
        try:
            # 读取数据
            if filename.endswith('.xlsx'):
                df = pd.read_excel(filename, sheet_name='模板数据')
            elif filename.endswith('.csv'):
                df = pd.read_csv(filename)
            else:
                return {'valid': False, 'message': '不支持的文件格式'}
            
            if df.empty:
                return {'valid': False, 'message': '文件为空'}
            
            # 基本验证
            validation_result = {
                'valid': True,
                'total_rows': len(df),
                'missing_required': 0,
                'data_type_errors': 0,
                'duplicate_entries': 0,
                'warnings': []
            }
            
            # 验证必填字段
            template_info = self.templates[data_type]
            required_fields = template_info['required']
            
            for field in required_fields:
                if field not in df.columns:
                    validation_result['warnings'].append(f'缺少字段: {field}')
                else:
                    missing_count = df[field].isnull().sum()
                    if missing_count > 0:
                        validation_result['missing_required'] += missing_count
                        validation_result['warnings'].append(f'字段 {field} 有 {missing_count} 个缺失值')
            
            # 验证数据类型
            if data_type == 'brands' and 'reputation_score' in df.columns:
                invalid_scores = df[~df['reputation_score'].between(1, 10)]
                if len(invalid_scores) > 0:
                    validation_result['data_type_errors'] += len(invalid_scores)
                    validation_result['warnings'].append(f'声誉评分超出范围 (1-10): {len(invalid_scores)} 个')
            
            # 检查重复项
            if 'brand_name' in df.columns:
                duplicates = df[df.duplicated(subset=['brand_name'], keep=False)]
                if len(duplicates) > 0:
                    validation_result['duplicate_entries'] = len(duplicates)
                    validation_result['warnings'].append(f'发现重复的品牌名称: {len(duplicates)} 个')
            
            # 总体评估
            total_warnings = (validation_result['missing_required'] + 
                            validation_result['data_type_errors'] + 
                            validation_result['duplicate_entries'])
            
            if total_warnings == 0:
                validation_result['quality'] = '优秀'
            elif total_warnings < len(df) * 0.1:  # 错误率小于10%
                validation_result['quality'] = '良好'
            elif total_warnings < len(df) * 0.2:  # 错误率小于20%
                validation_result['quality'] = '一般'
            else:
                validation_result['quality'] = '较差'
                validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            return {'valid': False, 'message': f'验证失败: {str(e)}'}

def main():
    """主函数"""
    importer = DataImporter()
    
    # 示例：生成模板
    print("=== 数据导入导出工具 ===")
    
    while True:
        print("\n📋 主菜单:")
        print("  1. 生成数据模板")
        print("  2. 导入Excel数据")
        print("  3. 导出CSV数据")
        print("  4. 验证数据质量")
        print("  0. 退出")
        
        choice = input("\n请选择操作 (0-4): ").strip()
        
        if choice == '0':
            print("👋 再见！")
            break
        
        elif choice == '1':
            print("\n可生成的模板类型:")
            template_types = ['brands', 'inventory', 'media_resources', 'sales_channels']
            for i, template_type in enumerate(template_types, 1):
                print(f"  {i}: {template_type}")
            
            try:
                template_choice = int(input("选择模板类型 (1-4): "))
                if 1 <= template_choice <= 4:
                    template_type = template_types[template_choice - 1]
                    filename = importer.generate_template(template_type)
                    print(f"✅ 模板已生成: {filename}")
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        elif choice == '2':
            filename = input("输入Excel文件路径: ").strip()
            if os.path.exists(filename):
                print("\n导入类型:")
                for i, import_type in enumerate(['brands', 'inventory', 'media_resources', 'sales_channels'], 1):
                    print(f"  {i}: {import_type}")
                
                try:
                    import_choice = int(input("选择导入类型 (1-4): "))
                    if 1 <= import_choice <= 4:
                        import_type = ['brands', 'inventory', 'media_resources', 'sales_channels'][import_choice - 1]
                        result = importer.import_from_excel(filename, import_type)
                        if result['success']:
                            print(f"✅ 导入完成: 成功 {result['imported']}, 失败 {result['failed']}")
                            if 'errors' in result:
                                print("错误信息:")
                                for error in result['errors']:
                                    print(f"  - {error}")
                        else:
                            print(f"❌ 导入失败: {result['message']}")
                    else:
                        print("❌ 无效选择")
                except ValueError:
                    print("❌ 请输入有效的数字")
            else:
                print("❌ 文件不存在")
        
        elif choice == '3':
            print("\n可导出的表:")
            tables = ['brands', 'inventory', 'media_resources', 'sales_channels', 'transactions']
            for i, table in enumerate(tables, 1):
                print(f"  {i}: {table}")
            
            try:
                export_choice = int(input("选择导出表 (1-5): "))
                if 1 <= export_choice <= 5:
                    table_name = tables[export_choice - 1]
                    filename = input("输出文件名 (可选，留空自动生成): ").strip()
                    result = importer.export_to_csv(table_name, filename if filename else None)
                    if result:
                        print(f"✅ 数据已导出: {result}")
                    else:
                        print("❌ 导出失败")
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入有效的数字")
        
        elif choice == '4':
            filename = input("输入要验证的文件路径: ").strip()
            if os.path.exists(filename):
                print("\n数据类型:")
                for i, data_type in enumerate(['brands', 'inventory', 'media_resources', 'sales_channels'], 1):
                    print(f"  {i}: {data_type}")
                
                try:
                    validate_choice = int(input("选择数据类型 (1-4): "))
                    if 1 <= validate_choice <= 4:
                        data_type = ['brands', 'inventory', 'media_resources', 'sales_channels'][validate_choice - 1]
                        result = importer.validate_data_quality(filename, data_type)
                        if result['valid']:
                            print(f"✅ 数据质量: {result['quality']}")
                            print(f"总行数: {result['total_rows']}")
                            print(f"缺失必填项: {result['missing_required']}")
                            print(f"数据类型错误: {result['data_type_errors']}")
                            print(f"重复项: {result['duplicate_entries']}")
                            if result['warnings']:
                                print("警告信息:")
                                for warning in result['warnings']:
                                    print(f"  - {warning}")
                        else:
                            print(f"❌ 验证失败: {result['message']}")
                    else:
                        print("❌ 无效选择")
                except ValueError:
                    print("❌ 请输入有效的数字")
            else:
                print("❌ 文件不存在")
        
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()