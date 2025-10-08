import sqlite3
import os

db_path = 'it_ops_system.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🔍 网络拓扑数据库诊断")
    print("=" * 60)
    
    # 0. 检查表结构
    print("\n📊 表结构:")
    cursor.execute("PRAGMA table_info(it_asset)")
    columns = cursor.fetchall()
    print("  it_asset表字段:", [col[1] for col in columns])
    
    # 1. 检查所有资产
    print("\n📊 所有资产列表:")
    cursor.execute('''
        SELECT id, name, category
        FROM it_asset 
        ORDER BY id
    ''')
    assets = cursor.fetchall()
    for asset in assets:
        print(f"  ID:{asset[0]} | 名称:{asset[1]} | 类别:{asset[2]}")
    
    print(f"\n🌐 网络设备 (交换机、路由器等):")
    cursor.execute('''
        SELECT id, name, category
        FROM it_asset 
        WHERE (category LIKE '%交换机%' OR category LIKE '%路由器%' OR category LIKE '%网络%')
        ORDER BY id
    ''')
    network_devices = cursor.fetchall()
    for device in network_devices:
        print(f"  ID:{device[0]} | 名称:{device[1]} | 类别:{device[2]}")
    
    # 3. 检查端口连接
    print(f"\n🔌 端口连接记录:")
    cursor.execute('''
        SELECT 
            pc.id,
            pc.source_port_id,
            pc.target_port_id,
            sp.port_name as source_port_name,
            sa.name as source_device_name,
            tp.port_name as target_port_name,
            ta.name as target_device_name,
            pc.cable_type,
            pc.created_at
        FROM port_connection pc
        LEFT JOIN asset_port sp ON pc.source_port_id = sp.id
        LEFT JOIN it_asset sa ON sp.asset_id = sa.id
        LEFT JOIN asset_port tp ON pc.target_port_id = tp.id
        LEFT JOIN it_asset ta ON tp.asset_id = ta.id
        ORDER BY pc.id
    ''')
    connections = cursor.fetchall()
    print(f"  总连接数: {len(connections)}")
    for conn_data in connections:
        print(f"  连接ID:{conn_data[0]} | {conn_data[4]}:{conn_data[3]} ↔ {conn_data[6]}:{conn_data[5]} | 线缆:{conn_data[7]}")
    
    # 4. 检查网络设备表
    print(f"\n📡 网络设备表 (network_device):")
    try:
        cursor.execute('''
            SELECT id, name, device_type, ip_address, status, x_position, y_position
            FROM network_device 
            ORDER BY id
        ''')
        network_devices_table = cursor.fetchall()
        print(f"  网络设备表记录数: {len(network_devices_table)}")
        for device in network_devices_table:
            print(f"  ID:{device[0]} | 名称:{device[1]} | 类型:{device[2]} | IP:{device[3]} | 位置:({device[5]},{device[6]})")
    except Exception as e:
        print(f"  网络设备表查询失败: {e}")
    
    print(f"\n🔍 查找特定设备:")
    search_names = ['测试交换机1', 'Cisco交换机01', 'Dell服务器01', 'HP工作站01']
    for name in search_names:
        cursor.execute('''
            SELECT id, name, category
            FROM it_asset 
            WHERE name LIKE ?
        ''', (f'%{name}%',))
        found = cursor.fetchall()
        if found:
            for device in found:
                print(f"  找到设备 '{name}': ID:{device[0]} | 完整名称:{device[1]} | 类别:{device[2]}")
        else:
            print(f"  ❌ 未找到设备: {name}")
    
    # 6. 检查端口详情
    print(f"\n🔌 相关端口详情:")
    for name in ['测试交换机1', 'Cisco交换机01', 'Dell服务器01', 'HP工作站01']:
        cursor.execute('''
            SELECT ap.id, ap.asset_id, ap.port_name, ap.is_connected, ia.name
            FROM asset_port ap
            JOIN it_asset ia ON ap.asset_id = ia.id
            WHERE ia.name LIKE ?
        ''', (f'%{name}%',))
        ports = cursor.fetchall()
        if ports:
            print(f"  {name} 的端口:")
            for port in ports:
                print(f"    端口ID:{port[0]} | 端口名:{port[2]} | 连接状态:{port[3]}")
    
    conn.close()
else:
    print(f"❌ 数据库文件不存在: {os.path.abspath(db_path)}")