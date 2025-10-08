#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库表结构升级脚本
为现有的 it_asset 表添加网络设备相关字段
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text


def upgrade_database_schema():
    """升级数据库表结构"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始升级数据库表结构...")
        
        # 需要添加的新字段
        new_columns = [
            # 网络设备专用字段
            "ADD COLUMN device_type VARCHAR(50) COMMENT '设备类型：交换机/路由器/防火墙/服务器等'",
            "ADD COLUMN subnet_mask VARCHAR(15) COMMENT '子网掩码'",
            "ADD COLUMN gateway VARCHAR(15) COMMENT '网关'",
            "ADD COLUMN dns_servers VARCHAR(255) COMMENT 'DNS服务器'",
            "ADD COLUMN firmware_version VARCHAR(50) COMMENT '固件版本'",
            "ADD COLUMN port_count INTEGER COMMENT '端口数量'",
            "ADD COLUMN is_managed BOOLEAN DEFAULT TRUE COMMENT '是否纳管'",
            
            # 拓扑信息
            "ADD COLUMN x_position FLOAT COMMENT '拓扑图X坐标'",
            "ADD COLUMN y_position FLOAT COMMENT '拓扑图Y坐标'"
        ]
        
        try:
            # 检查表是否存在
            result = db.session.execute(text("SHOW TABLES LIKE 'it_asset'")).fetchone()
            if not result:
                print("❌ it_asset 表不存在，请先创建基础表结构")
                return False
            
            # 获取现有列信息
            existing_columns = db.session.execute(text("DESCRIBE it_asset")).fetchall()
            existing_column_names = [col[0] for col in existing_columns]
            
            print(f"📋 现有列数量: {len(existing_column_names)}")
            
            # 添加缺失的列
            added_count = 0
            for column_def in new_columns:
                # 提取列名
                column_name = column_def.split()[2]  # ADD COLUMN column_name ...
                
                if column_name not in existing_column_names:
                    try:
                        sql = f"ALTER TABLE it_asset {column_def}"
                        db.session.execute(text(sql))
                        print(f"✅ 添加列: {column_name}")
                        added_count += 1
                    except Exception as e:
                        print(f"❌ 添加列 {column_name} 失败: {str(e)}")
                        # 继续处理其他列
                else:
                    print(f"⚠️  列 {column_name} 已存在，跳过")
            
            # 升级 device_port 表
            print("\n🔧 升级 device_port 表...")
            
            # 检查 device_port 表是否存在
            result = db.session.execute(text("SHOW TABLES LIKE 'device_port'")).fetchone()
            if result:
                # 检查是否已有 asset_device_id 字段
                port_columns = db.session.execute(text("DESCRIBE device_port")).fetchall()
                port_column_names = [col[0] for col in port_columns]
                
                if 'asset_device_id' not in port_column_names:
                    try:
                        db.session.execute(text(
                            "ALTER TABLE device_port ADD COLUMN asset_device_id INTEGER COMMENT '资产设备ID（新）'"
                        ))
                        print("✅ 添加 device_port.asset_device_id 字段")
                        added_count += 1
                    except Exception as e:
                        print(f"❌ 添加 device_port.asset_device_id 字段失败: {str(e)}")
                else:
                    print("⚠️  device_port.asset_device_id 字段已存在，跳过")
                
                # 修改 device_id 字段为可空
                try:
                    db.session.execute(text(
                        "ALTER TABLE device_port MODIFY COLUMN device_id INTEGER NULL COMMENT '网络设备ID（旧）'"
                    ))
                    print("✅ 修改 device_port.device_id 为可空")
                except Exception as e:
                    print(f"⚠️  修改 device_port.device_id 字段失败（可能已经是可空）: {str(e)}")
            else:
                print("⚠️  device_port 表不存在，跳过相关升级")
            
            # 提交更改
            db.session.commit()
            print(f"\n✅ 数据库表结构升级完成，共添加 {added_count} 个字段")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 数据库升级失败: {str(e)}")
            return False


def check_database_schema():
    """检查数据库表结构"""
    app = create_app()
    
    with app.app_context():
        print("🔍 检查数据库表结构...")
        
        try:
            # 检查 it_asset 表结构
            columns = db.session.execute(text("DESCRIBE it_asset")).fetchall()
            
            print(f"\n📋 it_asset 表结构 (共 {len(columns)} 列):")
            for col in columns:
                field, type_, null, key, default, extra = col
                print(f"   {field:20} {type_:15} {'NULL' if null == 'YES' else 'NOT NULL':8} {key:4} {default or '':10}")
            
            # 检查网络设备相关字段
            required_fields = ['device_type', 'subnet_mask', 'gateway', 'dns_servers', 
                             'firmware_version', 'port_count', 'is_managed', 'x_position', 'y_position']
            
            existing_fields = [col[0] for col in columns]
            missing_fields = [field for field in required_fields if field not in existing_fields]
            
            if missing_fields:
                print(f"\n⚠️  缺失字段: {', '.join(missing_fields)}")
                return False
            else:
                print("\n✅ 所有必需字段都已存在")
                return True
            
        except Exception as e:
            print(f"❌ 检查数据库表结构失败: {str(e)}")
            return False


def create_sample_network_categories():
    """创建网络设备相关的资产类别（使用新的分类体系）"""
    app = create_app()
    
    with app.app_context():
        print("🏷️  创建标准资产类别...")
        
        try:
            from app.models.asset import AssetCategory
            from app.utils.network_device_config import STANDARD_ASSET_CATEGORIES
            
            created_count = 0
            for cat_data in STANDARD_ASSET_CATEGORIES:
                existing = AssetCategory.query.filter_by(name=cat_data['name']).first()
                if not existing:
                    category = AssetCategory(**cat_data)
                    category.save()
                    print(f"✅ 创建类别: {cat_data['name']} ({cat_data['description']})")
                    created_count += 1
                else:
                    print(f"⚠️  类别 {cat_data['name']} 已存在，跳过")
            
            print(f"✅ 资产类别创建完成，共创建 {created_count} 个类别")
            
            # 显示类别统计
            from app.utils.network_device_config import NetworkDeviceConfig
            topology_count = len(NetworkDeviceConfig.get_topology_categories())
            terminal_count = len(NetworkDeviceConfig.get_terminal_categories())
            other_count = len(NetworkDeviceConfig.get_other_categories())
            
            print(f"
📊 类别统计:")
            print(f"   🌐 拓扑设备: {topology_count} 个")
            print(f"   💻 终端设备: {terminal_count} 个")
            print(f"   📦 其他设备: {other_count} 个")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建资产类别失败: {str(e)}")
            return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库表结构升级工具')
    parser.add_argument('action', choices=['upgrade', 'check', 'create-categories'], 
                       help='操作类型')
    
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        success = upgrade_database_schema()
        if success:
            create_sample_network_categories()
    elif args.action == 'check':
        check_database_schema()
    elif args.action == 'create-categories':
        create_sample_network_categories()