import sqlite3
import os

db_path = 'it_ops_system.db'
if os.path.exists(db_path):
    print(f"数据库文件存在: {os.path.abspath(db_path)}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("数据库表:", [table[0] for table in tables])
    
    # 检查资产数量
    try:
        cursor.execute('SELECT COUNT(*) FROM asset')
        asset_count = cursor.fetchone()[0]
        print(f'资产数量: {asset_count}')
        
        if asset_count > 0:
            cursor.execute('SELECT id, name, asset_type FROM asset LIMIT 5')
            assets = cursor.fetchall()
            print('前5个资产:', assets)
    except Exception as e:
        print(f'查询资产失败: {e}')
    
    # 检查端口数量
    try:
        cursor.execute('SELECT COUNT(*) FROM asset_port')
        port_count = cursor.fetchone()[0]
        print(f'端口数量: {port_count}')
        
        if port_count > 0:
            cursor.execute('SELECT id, asset_id, port_name, is_connected FROM asset_port LIMIT 5')
            ports = cursor.fetchall()
            print('前5个端口:', ports)
    except Exception as e:
        print(f'查询端口失败: {e}')
    
    conn.close()
else:
    print(f"数据库文件不存在: {os.path.abspath(db_path)}")