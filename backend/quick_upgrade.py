#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速数据库升级脚本
"""

import sqlite3
import os

def main():
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"🔧 连接数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🚀 开始升级数据库表结构...")
        
        # 1. 创建 asset_category 表（如果不存在）
        print("\n🔧 创建 asset_category 表...")
        
        create_category_sql = """
        CREATE TABLE IF NOT EXISTS asset_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL UNIQUE,
            code VARCHAR(20) NOT NULL UNIQUE,
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
            FOREIGN KEY (parent_id) REFERENCES asset_category(id)
        )
        """
        
        cursor.execute(create_category_sql)
        print("✅ 创建 asset_category 表")
        
        # 2. 插入基础资产类别数据
        print("\n🏷️  插入基础资产类别...")
        
        categories = [
            ('交换机', 'SWITCH', 1, 1, 0, 24, '🔀', '#409eff', '网络交换设备'),
            ('路由器', 'ROUTER', 1, 1, 0, 8, '🌐', '#67c23a', '网络路由设备'), 
            ('防火墙', 'FIREWALL', 1, 1, 0, 6, '🛡️', '#e6a23c', '网络安全设备'),
            ('服务器', 'SERVER', 1, 0, 1, 2, '🖥️', '#606266', '服务器设备'),
            ('工作站', 'WORKSTATION', 1, 0, 1, 1, '💻', '#909399', '办公工作站'),
            ('台式机', 'DESKTOP', 1, 0, 1, 1, '🖱️', '#c0c4cc', '台式计算机'),
            ('笔记本', 'LAPTOP', 1, 0, 1, 1, '💾', '#dcdfe6', '便携式计算机'),
            ('打印机', 'PRINTER', 0, 0, 0, 0, '🖨️', '#f56c6c', '打印设备'),
            ('显示器', 'MONITOR', 0, 0, 0, 0, '🖥️', '#909399', '显示设备'),
            ('网络设备', 'NETWORK_DEVICE', 1, 1, 0, 0, '📡', '#409eff', '通用网络设备')
        ]
        
        insert_count = 0
        for name, code, is_net, can_topo, is_term, port_count, icon, color, desc in categories:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO asset_category 
                    (name, code, is_network_device, can_topology, is_terminal, 
                     default_port_count, device_icon, device_color, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, code, is_net, can_topo, is_term, port_count, icon, color, desc))
                
                if cursor.rowcount > 0:
                    print(f"✅ 添加类别: {name}")
                    insert_count += 1
                else:
                    print(f"⚠️  类别 {name} 已存在，跳过")
                    
            except Exception as e:
                print(f"❌ 添加类别 {name} 失败: {str(e)}")
        
        # 3. 创建 asset_port 表
        print("\n🔧 创建 asset_port 表...")
        
        create_asset_port_sql = """
        CREATE TABLE IF NOT EXISTS asset_port (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER NOT NULL,
            port_name VARCHAR(50) NOT NULL,
            port_type VARCHAR(20),
            port_speed VARCHAR(20),
            port_status VARCHAR(20) DEFAULT 'unused',
            port_index INTEGER,
            is_uplink BOOLEAN DEFAULT 0,
            duplex_mode VARCHAR(10),
            vlan_id INTEGER,
            ip_address VARCHAR(15),
            mac_address VARCHAR(17),
            is_connected BOOLEAN DEFAULT 0,
            connected_port_id INTEGER,
            cable_type VARCHAR(20),
            cable_length REAL,
            description VARCHAR(255),
            last_link_time DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT 0,
            FOREIGN KEY (asset_id) REFERENCES it_asset(id),
            FOREIGN KEY (connected_port_id) REFERENCES asset_port(id),
            UNIQUE (asset_id, port_name)
        )
        """
        
        cursor.execute(create_asset_port_sql)
        print("✅ 创建 asset_port 表")
        
        # 4. 创建 port_connection 表
        print("\n🔧 创建 port_connection 表...")
        
        create_port_connection_sql = """
        CREATE TABLE IF NOT EXISTS port_connection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_port_id INTEGER NOT NULL,
            target_port_id INTEGER NOT NULL,
            cable_type VARCHAR(20),
            cable_length REAL,
            connection_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            disconnection_date DATETIME,
            connected_by INTEGER,
            disconnected_by INTEGER,
            notes TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT 0,
            FOREIGN KEY (source_port_id) REFERENCES asset_port(id),
            FOREIGN KEY (target_port_id) REFERENCES asset_port(id),
            FOREIGN KEY (connected_by) REFERENCES sys_user(id),
            FOREIGN KEY (disconnected_by) REFERENCES sys_user(id)
        )
        """
        
        cursor.execute(create_port_connection_sql)
        print("✅ 创建 port_connection 表")
        
        # 提交更改
        conn.commit()
        print(f"\n✅ 数据库升级完成!")
        print(f"   - 添加类别: {insert_count} 个")
        print(f"   - 创建表: asset_category, asset_port, port_connection")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 数据库升级失败: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    main()