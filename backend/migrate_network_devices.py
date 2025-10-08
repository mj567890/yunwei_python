#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络设备数据迁移脚本
将现有的 network_device 表数据迁移到 it_asset 表中
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.asset import Asset
from app.models.network import NetworkDevice, DevicePort
from app.utils.helpers import generate_asset_code


def migrate_network_devices():
    """迁移网络设备数据到资产表"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始迁移网络设备数据...")
        
        # 获取所有网络设备
        network_devices = NetworkDevice.query.filter_by(is_deleted=False).all()
        
        if not network_devices:
            print("❌ 没有找到需要迁移的网络设备数据")
            return
        
        print(f"📋 找到 {len(network_devices)} 台网络设备需要迁移")
        
        success_count = 0
        error_count = 0
        errors = []
        
        # 确保数据库表已更新
        print("🔧 检查数据库表结构...")
        try:
            # 这里可以添加数据库表结构检查或更新的逻辑
            db.create_all()
            print("✅ 数据库表结构检查完成")
        except Exception as e:
            print(f"❌ 数据库表结构检查失败: {str(e)}")
            return
        
        for device in network_devices:
            try:
                # 检查是否已经迁移过
                existing_asset = Asset.query.filter_by(
                    name=device.name,
                    device_type=device.device_type,
                    ip_address=device.ip_address,
                    is_deleted=False
                ).first()
                
                if existing_asset:
                    print(f"⚠️  设备 {device.name} 已存在于资产表中，跳过")
                    continue
                
                # 生成资产编码
                asset_code = generate_asset_code('网络设备', success_count)
                
                # 创建资产记录
                asset_data = {
                    'asset_code': asset_code,
                    'name': device.name,
                    'category': '网络设备',
                    'brand': device.brand,
                    'model': device.model,
                    'status': '在用' if device.status == '正常' else device.status,
                    
                    # 位置信息
                    'building_id': device.building_id,
                    'floor_id': device.floor_id,
                    'room_id': device.room_id,
                    'location_detail': device.location_detail,
                    
                    # 网络设备专用字段
                    'device_type': device.device_type,
                    'ip_address': device.ip_address,
                    'mac_address': device.mac_address,
                    'subnet_mask': device.subnet_mask,
                    'gateway': device.gateway,
                    'dns_servers': device.dns_servers,
                    'is_managed': device.is_managed,
                    'x_position': device.x_position,
                    'y_position': device.y_position,
                    
                    # 其他信息
                    'serial_number': device.serial_number,
                    'firmware_version': device.firmware_version,
                    'purchase_date': device.purchase_date,
                    'warranty_end_date': device.warranty_end_date,
                    'remark': device.description,
                    
                    # 创建时间继承
                    'created_at': device.created_at,
                    'updated_at': device.updated_at or datetime.utcnow()
                }
                
                # 计算端口数量
                port_count = device.ports.filter_by(is_deleted=False).count()
                if port_count > 0:
                    asset_data['port_count'] = port_count
                
                # 创建资产
                asset = Asset(**asset_data)
                asset.save()
                
                # 更新设备端口关联
                for port in device.ports.filter_by(is_deleted=False).all():
                    port.asset_device_id = asset.id
                    db.session.add(port)
                
                success_count += 1
                print(f"✅ 成功迁移设备: {device.name} -> 资产ID: {asset.id}")
                
            except Exception as e:
                error_count += 1
                error_msg = f"迁移设备 {device.name} 失败: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
                db.session.rollback()
        
        # 提交所有更改
        try:
            db.session.commit()
            print("💾 数据库更改已提交")
        except Exception as e:
            db.session.rollback()
            print(f"❌ 数据库提交失败: {str(e)}")
            return
        
        # 输出迁移结果
        print("\n" + "="*60)
        print("📊 迁移结果统计:")
        print(f"   ✅ 成功迁移: {success_count} 台设备")
        print(f"   ❌ 迁移失败: {error_count} 台设备")
        print(f"   📋 总计处理: {len(network_devices)} 台设备")
        
        if errors:
            print("\n⚠️ 错误详情:")
            for error in errors:
                print(f"   - {error}")
        
        print("\n🎉 网络设备数据迁移完成!")
        
        # 检查迁移后的数据
        network_assets = Asset.query.filter_by(category='网络设备', is_deleted=False).all()
        print(f"🔍 检查结果: 资产表中现有 {len(network_assets)} 台网络设备")


def rollback_migration():
    """回滚迁移（谨慎使用）"""
    app = create_app()
    
    with app.app_context():
        print("⚠️  开始回滚网络设备迁移...")
        response = input("这将删除所有迁移的网络设备资产，确认继续？(输入 'YES' 确认): ")
        
        if response != 'YES':
            print("❌ 回滚操作已取消")
            return
        
        try:
            # 删除所有网络设备类型的资产
            network_assets = Asset.query.filter_by(category='网络设备', is_deleted=False).all()
            count = len(network_assets)
            
            for asset in network_assets:
                # 清除端口关联
                DevicePort.query.filter_by(asset_device_id=asset.id).update({'asset_device_id': None})
                # 删除资产
                asset.delete()
            
            db.session.commit()
            print(f"✅ 成功回滚 {count} 台网络设备资产")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ 回滚失败: {str(e)}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='网络设备数据迁移工具')
    parser.add_argument('action', choices=['migrate', 'rollback'], help='操作类型')
    
    args = parser.parse_args()
    
    if args.action == 'migrate':
        migrate_network_devices()
    elif args.action == 'rollback':
        rollback_migration()