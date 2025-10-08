#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
类别数据迁移脚本
将资产表中的类别信息迁移到类别管理表
"""
import sqlite3
import os
from datetime import datetime

def analyze_existing_categories():
    """分析现有的类别数据"""
    db_path = os.path.join('backend', 'it_ops_system.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== 分析资产表中的类别数据 ===")
    
    # 检查资产表中的类别
    cursor.execute('''
        SELECT DISTINCT category, COUNT(*) as count 
        FROM it_asset 
        WHERE category IS NOT NULL AND category != ""
        GROUP BY category
        ORDER BY category
    ''')
    
    asset_categories = cursor.fetchall()
    print(f"资产表中发现 {len(asset_categories)} 个不同的类别:")
    for category, count in asset_categories:
        print(f"- {category} ({count} 个资产)")
    
    # 检查类别管理表中的现有数据
    cursor.execute('SELECT COUNT(*) FROM asset_category WHERE (is_deleted = 0 OR is_deleted IS NULL)')
    category_count = cursor.fetchone()[0]
    print(f"\n类别管理表中现有 {category_count} 个类别")
    
    if category_count > 0:
        cursor.execute('''
            SELECT name, code, is_network_device 
            FROM asset_category 
            WHERE (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY name
        ''')
        existing_categories = cursor.fetchall()
        print("现有类别:")
        for name, code, is_network in existing_categories:
            print(f"- {name} ({code}) - 网络设备: {bool(is_network)}")
    
    conn.close()
    return asset_categories

def migrate_categories():
    """迁移类别数据"""
    db_path = os.path.join('backend', 'it_ops_system.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== 开始迁移类别数据 ===")
    
    # 获取资产表中的不重复类别
    cursor.execute('''
        SELECT DISTINCT category 
        FROM it_asset 
        WHERE category IS NOT NULL AND category != ""
        ORDER BY category
    ''')
    
    asset_categories = [row[0] for row in cursor.fetchall()]
    
    # 获取已存在的类别（避免重复）
    cursor.execute('''
        SELECT name FROM asset_category 
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
    ''')
    existing_categories = [row[0] for row in cursor.fetchall()]
    
    # 定义网络设备类型（根据常见的网络设备名称）
    network_device_keywords = [
        '交换机', 'switch', '路由器', 'router', '防火墙', 'firewall', 
        '网络设备', 'network', '核心交换', '接入交换', '汇聚交换',
        '无线', 'wifi', 'ap', '网关', 'gateway'
    ]
    
    # 定义终端设备类型
    terminal_device_keywords = [
        '台式机', 'desktop', '笔记本', 'laptop', '工作站', 'workstation',
        'pc', '电脑', '终端', 'terminal'
    ]
    
    migrated_count = 0
    skipped_count = 0
    
    for category in asset_categories:
        if category in existing_categories:
            print(f"跳过已存在的类别: {category}")
            skipped_count += 1
            continue
        
        # 生成类别编码（大写字母，替换中文和特殊字符）
        code = category.upper()
        code_mapping = {
            '服务器': 'SERVER',
            '交换机': 'SWITCH',
            '路由器': 'ROUTER',
            '防火墙': 'FIREWALL',
            '台式机': 'DESKTOP',
            '笔记本': 'LAPTOP',
            '工作站': 'WORKSTATION',
            '打印机': 'PRINTER',
            '显示器': 'MONITOR',
            '网络设备': 'NETWORK_DEVICE',
            '终端设备': 'TERMINAL_DEVICE',
            '办公设备': 'OFFICE_DEVICE',
            '存储设备': 'STORAGE_DEVICE',
            '安全设备': 'SECURITY_DEVICE'
        }
        
        if category in code_mapping:
            code = code_mapping[category]
        else:
            # 简单的编码生成逻辑
            code = ''.join([c if c.isalnum() else '_' for c in code])
        
        # 判断是否为网络设备
        is_network_device = any(keyword in category.lower() for keyword in network_device_keywords)
        
        # 判断是否为终端设备
        is_terminal = any(keyword in category.lower() for keyword in terminal_device_keywords)
        
        # 判断是否可以在拓扑图中显示（网络设备但不是终端设备）
        can_topology = is_network_device and not is_terminal
        
        # 设置默认端口数
        default_port_count = 0
        if '交换机' in category or 'switch' in category.lower():
            default_port_count = 24
        elif '路由器' in category or 'router' in category.lower():
            default_port_count = 4
        
        # 设置设备图标
        device_icons = {
            '服务器': '🖥️',
            '交换机': '🔀',
            '路由器': '🌐',
            '防火墙': '🛡️',
            '台式机': '💻',
            '笔记本': '💻',
            '工作站': '🖨️',
            '打印机': '🖨️',
            '显示器': '🖥️',
            '网络设备': '📡'
        }
        device_icon = device_icons.get(category, '📦')
        
        # 设置设备颜色
        device_color = '#409eff' if is_network_device else '#606266'
        
        # 插入新类别
        now = datetime.now().isoformat()
        try:
            cursor.execute('''
                INSERT INTO asset_category 
                (name, code, description, sort_order, is_network_device, can_topology, 
                 is_terminal, default_port_count, device_icon, device_color, 
                 created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                category, code, f'从资产数据迁移的{category}类别', 
                migrated_count,  # 使用计数作为排序
                is_network_device, can_topology, is_terminal, default_port_count,
                device_icon, device_color, now, now, False
            ))
            
            print(f"✅ 迁移类别: {category} -> {code} (网络设备: {is_network_device}, 拓扑显示: {can_topology}, 终端设备: {is_terminal})")
            migrated_count += 1
            
        except sqlite3.IntegrityError as e:
            print(f"❌ 迁移失败 {category}: {e}")
    
    # 提交事务
    conn.commit()
    conn.close()
    
    print(f"\n=== 迁移完成 ===")
    print(f"成功迁移: {migrated_count} 个类别")
    print(f"跳过已存在: {skipped_count} 个类别")
    print(f"总计处理: {migrated_count + skipped_count} 个类别")

def verify_migration():
    """验证迁移结果"""
    db_path = os.path.join('backend', 'it_ops_system.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== 验证迁移结果 ===")
    
    # 检查类别管理表
    cursor.execute('''
        SELECT name, code, is_network_device, can_topology, is_terminal 
        FROM asset_category 
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
        ORDER BY sort_order, name
    ''')
    
    categories = cursor.fetchall()
    print(f"类别管理表中现有 {len(categories)} 个类别:")
    for name, code, is_network, can_topo, is_term in categories:
        flags = []
        if is_network: flags.append("网络设备")
        if can_topo: flags.append("拓扑显示")
        if is_term: flags.append("终端设备")
        flag_str = " | ".join(flags) if flags else "一般设备"
        print(f"- {name} ({code}) - {flag_str}")
    
    # 检查是否所有资产类别都已覆盖
    cursor.execute('''
        SELECT DISTINCT a.category 
        FROM it_asset a
        LEFT JOIN asset_category c ON a.category = c.name
        WHERE a.category IS NOT NULL AND a.category != ""
        AND c.id IS NULL
    ''')
    
    missing_categories = cursor.fetchall()
    if missing_categories:
        print(f"\n⚠️ 以下资产类别还未在类别管理表中:")
        for cat in missing_categories:
            print(f"- {cat[0]}")
    else:
        print("\n✅ 所有资产类别都已成功迁移到类别管理表")
    
    conn.close()

if __name__ == '__main__':
    print("资产类别数据迁移工具")
    print("=" * 50)
    
    # 分析现有数据
    asset_categories = analyze_existing_categories()
    
    if not asset_categories:
        print("没有发现需要迁移的类别数据")
        exit(0)
    
    # 自动执行迁移
    print(f"\n准备迁移 {len(asset_categories)} 个类别到类别管理表中")
    print("开始自动迁移...")
    
    # 执行迁移
    migrate_categories()
    
    # 验证结果
    verify_migration()
    
    print("\n🎉 类别数据迁移完成！")
    print("现在可以通过类别管理界面管理这些类别了")