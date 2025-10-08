#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置资产类别的拓扑显示配置
确保服务器、工作站等设备可以在拓扑图中显示和连接
"""

import os
import sys
import sqlite3
from datetime import datetime

def setup_category_topology_config():
    """配置资产类别的拓扑显示"""
    # 数据库连接
    db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
    
    # 如果数据库不存在，先创建基本结构
    if not os.path.exists(db_path):
        print("数据库不存在，先创建基本结构...")
        create_basic_db_structure(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查asset_category表是否存在
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='asset_category'
    """)
    if not cursor.fetchone():
        print("创建asset_category表...")
        create_asset_category_table(cursor)
    
    # 资产类别配置数据
    categories_config = [
        # 网络设备（核心拓扑设备）
        {'name': '交换机', 'code': 'SWITCH', 'is_network_device': True, 'can_topology': True, 'is_terminal': False, 'default_port_count': 24, 'device_icon': '🔀', 'device_color': '#409eff'},
        {'name': '路由器', 'code': 'ROUTER', 'is_network_device': True, 'can_topology': True, 'is_terminal': False, 'default_port_count': 4, 'device_icon': '📡', 'device_color': '#67c23a'},
        {'name': '防火墙', 'code': 'FIREWALL', 'is_network_device': True, 'can_topology': True, 'is_terminal': False, 'default_port_count': 8, 'device_icon': '🛡️', 'device_color': '#e6a23c'},
        {'name': '网关', 'code': 'GATEWAY', 'is_network_device': True, 'can_topology': True, 'is_terminal': False, 'default_port_count': 4, 'device_icon': '🚪', 'device_color': '#909399'},
        {'name': '负载均衡器', 'code': 'LOAD_BALANCER', 'is_network_device': True, 'can_topology': True, 'is_terminal': False, 'default_port_count': 8, 'device_icon': '⚖️', 'device_color': '#7c4dff'},
        
        # 计算设备（可拓扑显示的终端设备）
        {'name': '服务器', 'code': 'SERVER', 'is_network_device': True, 'can_topology': True, 'is_terminal': True, 'default_port_count': 4, 'device_icon': '🖥️', 'device_color': '#606266'},
        {'name': '工作站', 'code': 'WORKSTATION', 'is_network_device': True, 'can_topology': True, 'is_terminal': True, 'default_port_count': 2, 'device_icon': '💻', 'device_color': '#909399'},
        {'name': '台式机', 'code': 'DESKTOP', 'is_network_device': True, 'can_topology': True, 'is_terminal': True, 'default_port_count': 1, 'device_icon': '🖱️', 'device_color': '#c0c4cc'},
        {'name': '笔记本', 'code': 'LAPTOP', 'is_network_device': True, 'can_topology': True, 'is_terminal': True, 'default_port_count': 1, 'device_icon': '💾', 'device_color': '#dcdfe6'},
        
        # 其他设备（不在拓扑中显示）
        {'name': '显示器', 'code': 'MONITOR', 'is_network_device': False, 'can_topology': False, 'is_terminal': False, 'default_port_count': 0, 'device_icon': '🖼️', 'device_color': '#f5f7fa'},
        {'name': '打印机', 'code': 'PRINTER', 'is_network_device': False, 'can_topology': False, 'is_terminal': False, 'default_port_count': 1, 'device_icon': '🖨️', 'device_color': '#ebeef5'},
        {'name': '办公设备', 'code': 'OFFICE_DEVICE', 'is_network_device': False, 'can_topology': False, 'is_terminal': False, 'default_port_count': 0, 'device_icon': '📱', 'device_color': '#f4f4f5'},
        {'name': '网络设备', 'code': 'NETWORK_DEVICE', 'is_network_device': True, 'can_topology': True, 'is_terminal': False, 'default_port_count': 8, 'device_icon': '📱', 'device_color': '#409eff'},
    ]
    
    print("配置资产类别...")
    current_time = datetime.now()
    
    for category in categories_config:
        # 检查类别是否已存在
        cursor.execute('SELECT id FROM asset_category WHERE name = ?', (category['name'],))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有类别
            cursor.execute('''
                UPDATE asset_category 
                SET is_network_device = ?, can_topology = ?, is_terminal = ?, 
                    default_port_count = ?, device_icon = ?, device_color = ?,
                    updated_at = ?
                WHERE name = ?
            ''', (
                category['is_network_device'], category['can_topology'], category['is_terminal'],
                category['default_port_count'], category['device_icon'], category['device_color'],
                current_time, category['name']
            ))
            print(f"  更新类别: {category['name']}")
        else:
            # 插入新类别
            cursor.execute('''
                INSERT INTO asset_category 
                (name, code, is_network_device, can_topology, is_terminal, 
                 default_port_count, device_icon, device_color, created_at, updated_at, is_deleted)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                category['name'], category['code'], category['is_network_device'], 
                category['can_topology'], category['is_terminal'], category['default_port_count'],
                category['device_icon'], category['device_color'], current_time, current_time
            ))
            print(f"  创建类别: {category['name']}")
    
    conn.commit()
    
    # 验证配置
    print("\n验证配置结果:")
    cursor.execute('''
        SELECT name, can_topology, is_network_device, is_terminal 
        FROM asset_category 
        WHERE (is_deleted = 0 OR is_deleted IS NULL)
        ORDER BY name
    ''')
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row[0]}: can_topology={row[1]}, is_network_device={row[2]}, is_terminal={row[3]}")
    
    # 统计拓扑设备数量
    cursor.execute('SELECT COUNT(*) FROM asset_category WHERE can_topology = 1 AND (is_deleted = 0 OR is_deleted IS NULL)')
    topology_count = cursor.fetchone()[0]
    print(f"\n✅ 配置完成！共有 {topology_count} 个类别支持拓扑显示")
    
    conn.close()

def create_basic_db_structure(db_path):
    """创建基本数据库结构"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 基本的it_asset表（简化版）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS it_asset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_code VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            brand VARCHAR(50),
            model VARCHAR(100),
            category VARCHAR(50),
            status VARCHAR(20) DEFAULT '在用',
            ip_address VARCHAR(15),
            mac_address VARCHAR(17),
            user_name VARCHAR(50),
            user_department VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def create_asset_category_table(cursor):
    """创建资产类别表"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asset_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL,
            code VARCHAR(20) UNIQUE NOT NULL,
            parent_id INTEGER,
            description TEXT,
            sort_order INTEGER DEFAULT 0,
            is_network_device BOOLEAN DEFAULT 0,
            can_topology BOOLEAN DEFAULT 0,
            is_terminal BOOLEAN DEFAULT 0,
            default_port_count INTEGER,
            device_icon VARCHAR(20),
            device_color VARCHAR(20),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT 0,
            FOREIGN KEY (parent_id) REFERENCES asset_category (id)
        )
    ''')

if __name__ == '__main__':
    try:
        setup_category_topology_config()
        print("\n🎉 资产类别配置成功！")
        print("现在服务器、工作站等设备都可以在拓扑图中显示和进行端口连接了。")
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)