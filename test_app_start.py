#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试应用程序启动
"""

import streamlit as st
from inventory_manager import InventoryManager

# 初始化管理器
manager = InventoryManager()

# 获取库存数据
inventory_data = manager.get_all_inventory()

print(f"库存数据数量: {len(inventory_data)}")
if inventory_data:
    print("第一个库存项目:")
    print(inventory_data[0])

# 获取品牌数据
brands_data = manager.get_all_brands()
print(f"品牌数据数量: {len(brands_data)}")

print("应用程序可以正常启动！")