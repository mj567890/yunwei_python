#!/usr/bin/env python3
"""
扩展IT资产表结构，增加缺失的字段
"""
import sqlite3
import os

def upgrade_asset_table():
    """升级it_asset表结构，添加缺失的字段"""
    db_path = 'd:/kaifa/yuwei_python/backend/it_ops_system.db'
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print("🔄 开始升级数据库表结构...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 定义需要添加的字段
        new_columns = [
            # 基本信息字段
            ('specification', 'TEXT', '规格参数'),
            ('serial_number', 'VARCHAR(100)', '序列号'),
            
            # 位置信息字段
            ('building_id', 'INTEGER', '楼宇ID'),
            ('floor_id', 'INTEGER', '楼层ID'),
            ('room_id', 'INTEGER', '房间ID'),
            ('location_detail', 'VARCHAR(255)', '详细位置'),
            
            # 采购信息字段
            ('supplier', 'VARCHAR(100)', '供应商'),
            ('purchase_date', 'DATE', '采购日期'),
            ('purchase_price', 'DECIMAL(12,2)', '采购价格'),
            ('purchase_order', 'VARCHAR(50)', '采购订单号'),
            
            # 使用信息字段
            ('deploy_date', 'DATE', '部署日期'),
            ('condition_rating', 'VARCHAR(20)', '状况评级'),
            
            # 网络信息字段
            ('ip_address', 'VARCHAR(15)', 'IP地址'),
            ('mac_address', 'VARCHAR(17)', 'MAC地址'),
            
            # 其他信息字段
            ('remark', 'TEXT', '备注')
        ]
        
        # 获取现有列信息
        cursor.execute('PRAGMA table_info(it_asset)')
        existing_columns = {col[1] for col in cursor.fetchall()}
        
        print(f"📋 当前表中已有 {len(existing_columns)} 个字段")
        
        # 添加缺失的字段
        added_count = 0
        for column_name, column_type, description in new_columns:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE it_asset ADD COLUMN {column_name} {column_type}"
                    cursor.execute(sql)
                    print(f"   ✅ 添加字段: {column_name} ({column_type}) - {description}")
                    added_count += 1
                except Exception as e:
                    print(f"   ❌ 添加字段失败 {column_name}: {e}")
            else:
                print(f"   ⏭️  字段已存在: {column_name}")
        
        # 提交更改
        conn.commit()
        
        # 验证表结构
        cursor.execute('PRAGMA table_info(it_asset)')
        all_columns = cursor.fetchall()
        
        print(f"\n📊 升级完成统计:")
        print(f"   ✅ 新增字段: {added_count}")
        print(f"   📋 表中总字段数: {len(all_columns)}")
        
        print(f"\n📋 升级后的完整表结构:")
        for col in all_columns:
            field_name = col[1]
            field_type = col[2]
            is_required = col[3] == 1
            default_value = col[4]
            print(f"   {field_name} ({field_type}) - 必填: {is_required}, 默认: {default_value}")
        
        conn.close()
        print(f"\n🎉 数据库表结构升级成功！")
        return True
        
    except Exception as e:
        print(f"❌ 升级数据库表结构失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 IT资产表结构升级工具")
    print("=" * 80)
    
    success = upgrade_asset_table()
    
    if success:
        print("\n✅ 数据库升级完成！现在可以保存完整的资产信息了。")
        print("💡 接下来需要更新后端代码以支持所有字段的保存。")
    else:
        print("\n❌ 数据库升级失败，请检查错误信息。")