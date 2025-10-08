#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('it_ops_system.db')
cursor = conn.cursor()

print('=== asset_category表结构 ===')
cursor.execute('PRAGMA table_info(asset_category)')
columns = cursor.fetchall()
for col in columns:
    nullable = "NULL" if col[3] == 0 else "NOT NULL"
    print(f'  {col[1]} ({col[2]}) - {nullable}')

print('\n=== asset_category数据 ===')
cursor.execute('SELECT * FROM asset_category LIMIT 10')
data = cursor.fetchall()
for row in data:
    print(f'  {row}')

conn.close()