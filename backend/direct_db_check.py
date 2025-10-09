#!/usr/bin/env python3
"""直接检查数据库中的位置数据"""

import sqlite3

def direct_db_check():
    """直接查询数据库"""
    try:
        conn = sqlite3.connect('it_ops_system.db')
        cursor = conn.cursor()
        
        print("=== 直接数据库检查 ===")
        
        # 检查所有设备的位置信息
        cursor.execute("""
            SELECT id, name, category, x_position, y_position
            FROM it_asset 
            ORDER BY id
        """)
        
        all_assets = cursor.fetchall()
        
        print(f"数据库中总共有 {len(all_assets)} 个资产:")
        
        has_position_count = 0
        for row in all_assets:
            asset_id, name, category, x_pos, y_pos = row
            if x_pos is not None or y_pos is not None:
                print(f"  ✅ ID:{asset_id} {name} ({category}) -> x:{x_pos} y:{y_pos}")
                has_position_count += 1
            else:
                print(f"  ❌ ID:{asset_id} {name} ({category}) -> x:None y:None")
        
        print(f"\n📊 统计: {has_position_count}/{len(all_assets)} 个设备有位置信息")
        
        # 专门检查前3个设备（我们刚刚测试的）
        print("\n=== 特别检查前3个设备 ===")
        cursor.execute("""
            SELECT id, name, x_position, y_position
            FROM it_asset 
            WHERE id IN (1, 2, 3)
            ORDER BY id
        """)
        
        test_assets = cursor.fetchall()
        for row in test_assets:
            asset_id, name, x_pos, y_pos = row
            print(f"ID:{asset_id} {name} -> x:{x_pos} y:{y_pos}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")

if __name__ == "__main__":
    direct_db_check()