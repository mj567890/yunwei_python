#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库表结构
"""

import sqlite3

def check_database():
    """检查数据库表结构"""
    conn = sqlite3.connect('it_ops_system.db')
    cursor = conn.cursor()
    
    try:
        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = cursor.fetchall()
        print("📋 数据库中的所有表:")
        for table in all_tables:
            print(f"  - {table[0]}")
        
        # 查看数据字典相关表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%dict%'")
        dict_tables = cursor.fetchall()
        print(f"\n📚 数据字典相关表:")
        for table in dict_tables:
            print(f"  - {table[0]}")
            
        # 检查具体表是否存在
        table_names = ['dict_maintenance_type', 'dict_maintenance_category', 'dict_department']
        print(f"\n🔍 检查数据字典表是否存在:")
        for table_name in table_names:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            result = cursor.fetchone()
            if result:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table_name} - 存在，包含 {count} 条数据")
            else:
                print(f"  ❌ {table_name} - 不存在")
        
    except Exception as e:
        print(f"❌ 检查数据库时出错: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    check_database()