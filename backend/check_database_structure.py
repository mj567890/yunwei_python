#!/usr/bin/env python3
"""检查数据库表结构"""

import sqlite3

def check_database_tables():
    """检查数据库中的表结构"""
    try:
        conn = sqlite3.connect('it_ops_system.db')
        cursor = conn.cursor()
        
        print("=" * 60)
        print("📊 数据库表结构检查")
        print("=" * 60)
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        print(f"数据库中共有 {len(tables)} 个表:")
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 表: {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_str = " (主键)" if pk else ""
                not_null_str = " NOT NULL" if not_null else ""
                default_str = f" DEFAULT {default_val}" if default_val else ""
                print(f"  - {col_name}: {col_type}{not_null_str}{default_str}{pk_str}")
        
        # 专门检查网络设备相关的表
        print("\n" + "=" * 60)
        print("🔍 网络设备相关表分析")
        print("=" * 60)
        
        network_related_tables = [table[0] for table in tables if 'network' in table[0].lower() or 'device' in table[0].lower()]
        
        if network_related_tables:
            print("发现的网络设备相关表:")
            for table in network_related_tables:
                print(f"  - {table}")
        else:
            print("❌ 没有发现专门的网络设备表")
        
        # 检查it_asset表中的网络设备数据
        print("\n🔍 检查it_asset表中的网络设备类型:")
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM it_asset 
            WHERE category IN ('交换机', '路由器', '防火墙', '服务器', '工作站', '台式机', '笔记本', '网络设备')
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        network_assets = cursor.fetchall()
        if network_assets:
            for category, count in network_assets:
                print(f"  - {category}: {count} 个")
        else:
            print("  ❌ 资产表中没有网络设备数据")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")

if __name__ == "__main__":
    check_database_tables()