#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库表结构升级脚本 V2
支持可配置的网络设备分类和完整的端口管理
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置Flask配置为SQLite
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///it_ops_system.db'

from app import create_app, db
from sqlalchemy import text


def upgrade_database_schema_v2():
    """升级数据库表结构到V2版本"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始升级数据库表结构到V2版本...")
        
        try:
            # 1. 升级 asset_category 表
            print("\n🔧 升级 asset_category 表...")
            
            category_columns = [
                "ADD COLUMN is_network_device BOOLEAN DEFAULT FALSE COMMENT '是否为网络设备'",
                "ADD COLUMN can_topology BOOLEAN DEFAULT FALSE COMMENT '是否可用于拓扑图'",
                "ADD COLUMN is_terminal BOOLEAN DEFAULT FALSE COMMENT '是否为终端设备'",
                "ADD COLUMN default_port_count INTEGER COMMENT '默认端口数量'",
                "ADD COLUMN device_icon VARCHAR(20) COMMENT '设备图标'",
                "ADD COLUMN device_color VARCHAR(20) COMMENT '设备颜色'"
            ]
            
            # 检查现有列
            existing_columns = db.session.execute(text("DESCRIBE asset_category")).fetchall()
            existing_column_names = [col[0] for col in existing_columns]
            
            added_count = 0
            for column_def in category_columns:
                column_name = column_def.split()[2]
                if column_name not in existing_column_names:
                    try:
                        sql = f"ALTER TABLE asset_category {column_def}"
                        db.session.execute(text(sql))
                        print(f"✅ 添加列: asset_category.{column_name}")
                        added_count += 1
                    except Exception as e:
                        print(f"❌ 添加列 {column_name} 失败: {str(e)}")
                else:
                    print(f"⚠️  列 asset_category.{column_name} 已存在，跳过")
            
            # 2. 创建 asset_port 表
            print("\n🔧 创建 asset_port 表...")
            
            create_asset_port_sql = """
            CREATE TABLE IF NOT EXISTS asset_port (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                asset_id INTEGER NOT NULL,
                port_name VARCHAR(50) NOT NULL,
                port_type VARCHAR(20) COMMENT '端口类型',
                port_speed VARCHAR(20) COMMENT '端口速率',
                port_status VARCHAR(20) DEFAULT 'unused' COMMENT '端口状态',
                port_index INTEGER COMMENT '端口序号',
                is_uplink BOOLEAN DEFAULT FALSE COMMENT '是否为上联端口',
                duplex_mode VARCHAR(10) COMMENT '双工模式',
                vlan_id INTEGER COMMENT 'VLAN ID',
                ip_address VARCHAR(15) COMMENT '端口IP地址',
                mac_address VARCHAR(17) COMMENT '端口MAC地址',
                is_connected BOOLEAN DEFAULT FALSE COMMENT '是否已连接',
                connected_port_id INTEGER COMMENT '连接的端口ID',
                cable_type VARCHAR(20) COMMENT '线缆类型',
                cable_length FLOAT COMMENT '线缆长度',
                description VARCHAR(255) COMMENT '端口描述',
                last_link_time DATETIME COMMENT '最后连接时间',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (asset_id) REFERENCES it_asset(id),
                FOREIGN KEY (connected_port_id) REFERENCES asset_port(id),
                UNIQUE KEY uk_asset_port_name (asset_id, port_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资产端口表'
            """
            
            db.session.execute(text(create_asset_port_sql))
            print("✅ 创建 asset_port 表")
            
            # 3. 创建 port_connection 表
            print("\n🔧 创建 port_connection 表...")
            
            create_port_connection_sql = """
            CREATE TABLE IF NOT EXISTS port_connection (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                source_port_id INTEGER NOT NULL,
                target_port_id INTEGER NOT NULL,
                cable_type VARCHAR(20) COMMENT '线缆类型',
                cable_length FLOAT COMMENT '线缆长度',
                connection_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '连接时间',
                disconnection_date DATETIME COMMENT '断开时间',
                connected_by INTEGER COMMENT '连接操作人',
                disconnected_by INTEGER COMMENT '断开操作人',
                notes TEXT COMMENT '备注',
                is_active BOOLEAN DEFAULT TRUE COMMENT '是否为当前连接',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (source_port_id) REFERENCES asset_port(id),
                FOREIGN KEY (target_port_id) REFERENCES asset_port(id),
                FOREIGN KEY (connected_by) REFERENCES sys_user(id),
                FOREIGN KEY (disconnected_by) REFERENCES sys_user(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='端口连接历史表'
            """
            
            db.session.execute(text(create_port_connection_sql))
            print("✅ 创建 port_connection 表")
            
            # 提交更改
            db.session.commit()
            print(f"\n✅ 数据库表结构升级到V2版本完成，共添加 {added_count} 个字段")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 数据库升级失败: {str(e)}")
            return False


def init_network_device_categories():
    """初始化网络设备类别配置"""
    app = create_app()
    
    with app.app_context():
        print("🏷️  初始化网络设备类别配置...")
        
        try:
            # 更新现有类别的网络设备配置
            updates = [
                # 拓扑设备
                ('交换机', {'is_network_device': True, 'can_topology': True, 'default_port_count': 24, 'device_icon': '🔀', 'device_color': '#409eff'}),
                ('路由器', {'is_network_device': True, 'can_topology': True, 'default_port_count': 8, 'device_icon': '🌐', 'device_color': '#67c23a'}),
                ('防火墙', {'is_network_device': True, 'can_topology': True, 'default_port_count': 6, 'device_icon': '🛡️', 'device_color': '#e6a23c'}),
                
                # 终端设备
                ('服务器', {'is_network_device': True, 'is_terminal': True, 'default_port_count': 2, 'device_icon': '🖥️', 'device_color': '#606266'}),
                ('工作站', {'is_network_device': True, 'is_terminal': True, 'default_port_count': 1, 'device_icon': '💻', 'device_color': '#909399'}),
                ('台式机', {'is_network_device': True, 'is_terminal': True, 'default_port_count': 1, 'device_icon': '🖱️', 'device_color': '#c0c4cc'}),
                ('笔记本', {'is_network_device': True, 'is_terminal': True, 'default_port_count': 1, 'device_icon': '💾', 'device_color': '#dcdfe6'}),
            ]
            
            updated_count = 0
            for category_name, config in updates:
                try:
                    # 构建更新SQL
                    set_clauses = []
                    for key, value in config.items():
                        if isinstance(value, bool):
                            set_clauses.append(f"{key} = {1 if value else 0}")
                        elif isinstance(value, int):
                            set_clauses.append(f"{key} = {value}")
                        else:
                            set_clauses.append(f"{key} = '{value}'")
                    
                    sql = f"UPDATE asset_category SET {', '.join(set_clauses)} WHERE name = '{category_name}' AND is_deleted = 0"
                    result = db.session.execute(text(sql))
                    
                    if result.rowcount > 0:
                        print(f"✅ 更新类别: {category_name}")
                        updated_count += 1
                    else:
                        print(f"⚠️  类别 {category_name} 不存在，跳过")
                        
                except Exception as e:
                    print(f"❌ 更新类别 {category_name} 失败: {str(e)}")
            
            db.session.commit()
            print(f"✅ 网络设备类别配置完成，共更新 {updated_count} 个类别")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 初始化网络设备类别失败: {str(e)}")
            return False


def check_database_v2():
    """检查V2数据库结构"""
    app = create_app()
    
    with app.app_context():
        print("🔍 检查V2数据库结构...")
        
        try:
            # 检查 asset_category 表
            print("\n📋 asset_category 表结构:")
            columns = db.session.execute(text("DESCRIBE asset_category")).fetchall()
            for col in columns:
                field, type_, null, key, default, extra = col
                print(f"   {field:25} {type_:20} {'NULL' if null == 'YES' else 'NOT NULL':8}")
            
            # 检查 asset_port 表
            print("\n📋 asset_port 表结构:")
            try:
                columns = db.session.execute(text("DESCRIBE asset_port")).fetchall()
                for col in columns:
                    field, type_, null, key, default, extra = col
                    print(f"   {field:25} {type_:20} {'NULL' if null == 'YES' else 'NOT NULL':8}")
            except Exception as e:
                print("   ❌ asset_port 表不存在")
            
            # 检查 port_connection 表
            print("\n📋 port_connection 表结构:")
            try:
                columns = db.session.execute(text("DESCRIBE port_connection")).fetchall()
                for col in columns:
                    field, type_, null, key, default, extra = col
                    print(f"   {field:25} {type_:20} {'NULL' if null == 'YES' else 'NOT NULL':8}")
            except Exception as e:
                print("   ❌ port_connection 表不存在")
            
            # 检查网络设备类别配置
            print("\n🌐 网络设备类别配置:")
            network_categories = db.session.execute(text(
                "SELECT name, is_network_device, can_topology, is_terminal, default_port_count, device_icon "
                "FROM asset_category WHERE is_network_device = 1 AND is_deleted = 0"
            )).fetchall()
            
            if network_categories:
                for cat in network_categories:
                    name, is_net, can_topo, is_term, port_count, icon = cat
                    flags = []
                    if can_topo: flags.append("拓扑")
                    if is_term: flags.append("终端")
                    flag_str = "/".join(flags) if flags else "其他"
                    print(f"   {name:10} {icon or '📦':3} {flag_str:10} 端口:{port_count or 0:2}")
            else:
                print("   ⚠️  未找到网络设备类别配置")
            
            return True
            
        except Exception as e:
            print(f"❌ 检查数据库结构失败: {str(e)}")
            return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库V2升级工具')
    parser.add_argument('action', choices=['upgrade', 'check', 'init-categories'], 
                       help='操作类型')
    
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        success = upgrade_database_schema_v2()
        if success:
            init_network_device_categories()
    elif args.action == 'check':
        check_database_v2()
    elif args.action == 'init-categories':
        init_network_device_categories()