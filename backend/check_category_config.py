import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
print(f"数据库路径: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('SELECT name, can_topology, is_network_device, is_terminal FROM asset_category WHERE (is_deleted = 0 OR is_deleted IS NULL)')
    rows = cursor.fetchall()
    print('资产类别配置:')
    for row in rows:
        print(f'  {row[0]}: can_topology={row[1]}, is_network_device={row[2]}, is_terminal={row[3]}')
except Exception as e:
    print(f'查询失败: {e}')
    # 检查表结构
    cursor.execute('PRAGMA table_info(asset_category)')
    cols = cursor.fetchall()
    print('asset_category表结构:')
    for col in cols:
        print(f'  {col[1]} {col[2]}')

conn.close()