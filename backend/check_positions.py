#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查保存的设备位置信息
"""
import sqlite3
import os

db_path = 'it_ops_system.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== 检查设备位置信息 ===")

# 检查有位置信息的设备数量
cursor.execute('SELECT COUNT(*) FROM it_asset WHERE x_position IS NOT NULL AND y_position IS NOT NULL')
count = cursor.fetchone()[0]
print(f"有位置信息的设备数量: {count}")

if count > 0:
    print("\n保存的设备位置:")
    cursor.execute('SELECT id, name, x_position, y_position FROM it_asset WHERE x_position IS NOT NULL AND y_position IS NOT NULL LIMIT 10')
    rows = cursor.fetchall()
    for row in rows:
        print(f"  ID:{row[0]} {row[1]} -> ({row[2]}, {row[3]})")
else:
    print("❌ 数据库中没有保存的位置信息")
    
    # 检查是否有设备数据
    cursor.execute('SELECT COUNT(*) FROM it_asset')
    total_count = cursor.fetchone()[0]
    print(f"总设备数量: {total_count}")
    
    if total_count > 0:
        print("\n前5个设备信息:")
        cursor.execute('SELECT id, name, category, x_position, y_position FROM it_asset LIMIT 5')
        rows = cursor.fetchall()
        for row in rows:
            print(f"  ID:{row[0]} {row[1]} ({row[2]}) -> x:{row[3]} y:{row[4]}")

conn.close()