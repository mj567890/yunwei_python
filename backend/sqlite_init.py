#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite数据库初始化脚本
为开发环境快速创建SQLite数据库和测试数据
"""

import sqlite3
import os
import hashlib
from datetime import datetime

def create_sqlite_database():
    """创建SQLite数据库和初始数据"""
    
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
    
    # 如果数据库已存在，删除重建
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ 删除现有数据库: {db_path}")
    
    # 连接数据库（会自动创建）
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 开始创建数据表...")
    
    # 创建系统用户表
    cursor.execute("""
    CREATE TABLE sys_user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        email VARCHAR(100),
        real_name VARCHAR(50),
        phone VARCHAR(20),
        status INTEGER DEFAULT 1,
        last_login_time DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建角色表
    cursor.execute("""
    CREATE TABLE sys_role (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        code VARCHAR(50) UNIQUE NOT NULL,
        description TEXT,
        status INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建权限表
    cursor.execute("""
    CREATE TABLE sys_permission (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        code VARCHAR(50) UNIQUE NOT NULL,
        description TEXT,
        resource VARCHAR(50),
        action VARCHAR(50),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建用户角色关联表
    cursor.execute("""
    CREATE TABLE user_roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES sys_user (id),
        FOREIGN KEY (role_id) REFERENCES sys_role (id)
    )
    """)
    
    # 创建角色权限关联表
    cursor.execute("""
    CREATE TABLE role_permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (role_id) REFERENCES sys_role (id),
        FOREIGN KEY (permission_id) REFERENCES sys_permission (id)
    )
    """)
    
    # 创建楼宇信息表
    cursor.execute("""
    CREATE TABLE building_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        code VARCHAR(50) UNIQUE NOT NULL,
        address TEXT,
        description TEXT,
        status INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 创建楼层信息表
    cursor.execute("""
    CREATE TABLE floor_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        building_id INTEGER NOT NULL,
        name VARCHAR(50) NOT NULL,
        code VARCHAR(50) NOT NULL,
        floor_number INTEGER,
        description TEXT,
        status INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (building_id) REFERENCES building_info (id)
    )
    """)
    
    # 创建房间信息表
    cursor.execute("""
    CREATE TABLE room_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        floor_id INTEGER NOT NULL,
        name VARCHAR(50) NOT NULL,
        code VARCHAR(50) NOT NULL,
        room_type VARCHAR(50),
        area DECIMAL(10,2),
        capacity INTEGER,
        description TEXT,
        status INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (floor_id) REFERENCES floor_info (id)
    )
    """)
    
    # 创建资产类别表
    cursor.execute("""
    CREATE TABLE asset_category (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50) NOT NULL,
        code VARCHAR(50) UNIQUE NOT NULL,
        parent_id INTEGER,
        description TEXT,
        sort_order INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_id) REFERENCES asset_category (id)
    )
    """)
    
    # 创建IT资产表
    cursor.execute("""
    CREATE TABLE it_asset (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_code VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        brand VARCHAR(50),
        model VARCHAR(100),
        category VARCHAR(50),
        building_id INTEGER,
        floor_id INTEGER,
        room_id INTEGER,
        supplier VARCHAR(100),
        purchase_date DATE,
        purchase_price DECIMAL(15,2),
        warranty_start_date DATE,
        warranty_end_date DATE,
        warranty_period INTEGER,
        user_name VARCHAR(50),
        user_department VARCHAR(50),
        deploy_date DATE,
        status VARCHAR(20) DEFAULT '在用',
        condition_rating VARCHAR(10) DEFAULT '良',
        serial_number VARCHAR(100),
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (building_id) REFERENCES building_info (id),
        FOREIGN KEY (floor_id) REFERENCES floor_info (id),
        FOREIGN KEY (room_id) REFERENCES room_info (id)
    )
    """)
    
    print("✅ 数据表创建完成")
    
    # 插入初始数据
    print("📝 插入初始数据...")
    
    # 创建管理员用户 (密码: admin123)
    admin_password = hashlib.pbkdf2_hmac('sha256', b'admin123', b'salt', 100000).hex()
    cursor.execute("""
    INSERT INTO sys_user (username, password_hash, email, real_name, status)
    VALUES (?, ?, ?, ?, ?)
    """, ('admin', f'pbkdf2:sha256:100000$salt${admin_password}', 'admin@itops.com', '系统管理员', 1))
    
    # 创建角色
    roles = [
        ('系统管理员', 'ADMIN', '系统管理员，拥有所有权限'),
        ('运维员', 'OPERATOR', '运维人员，拥有操作权限'),
        ('查看员', 'VIEWER', '查看人员，只读权限')
    ]
    cursor.executemany("""
    INSERT INTO sys_role (name, code, description, status)
    VALUES (?, ?, ?, 1)
    """, roles)
    
    # 为管理员分配角色
    cursor.execute("""
    INSERT INTO user_roles (user_id, role_id)
    VALUES (1, 1)
    """)
    
    # 创建楼宇数据
    buildings = [
        ('总部大楼', 'HQ001', '北京市朝阳区XX路1号', '公司总部办公大楼'),
        ('研发中心', 'RD001', '北京市海淀区XX路2号', '研发中心大楼')
    ]
    cursor.executemany("""
    INSERT INTO building_info (name, code, address, description, status)
    VALUES (?, ?, ?, ?, 1)
    """, buildings)
    
    # 创建楼层数据
    floors = [
        (1, '1层', 'F01', 1, '大厅和接待区'),
        (1, '2层', 'F02', 2, '办公区域'),
        (1, '3层', 'F03', 3, '会议室和培训室'),
        (2, '1层', 'F01', 1, '服务器机房'),
        (2, '2层', 'F02', 2, '研发办公区')
    ]
    cursor.executemany("""
    INSERT INTO floor_info (building_id, name, code, floor_number, description, status)
    VALUES (?, ?, ?, ?, ?, 1)
    """, floors)
    
    # 创建房间数据
    rooms = [
        (1, '大厅', 'R001', '公共区域', 200.00, 100, '主大厅'),
        (2, '办公室201', 'R201', '办公室', 50.00, 10, '普通办公室'),
        (3, '会议室301', 'R301', '会议室', 30.00, 8, '小型会议室'),
        (4, '主机房', 'R101', '机房', 300.00, 10, '主要服务器机房'),
        (5, '研发部', 'R201', '办公室', 120.00, 20, '研发部门办公区')
    ]
    cursor.executemany("""
    INSERT INTO room_info (floor_id, name, code, room_type, area, capacity, description, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, rooms)
    
    # 创建资产类别
    categories = [
        ('计算机设备', 'COMPUTER', None, '各类计算机设备', 1),
        ('网络设备', 'NETWORK', None, '网络相关设备', 2),
        ('办公设备', 'OFFICE', None, '办公相关设备', 3),
        ('服务器', 'SERVER', 1, '各类服务器', 1),
        ('工作站', 'WORKSTATION', 1, '员工工作电脑', 2),
        ('交换机', 'SWITCH', 2, '网络交换机', 1),
        ('路由器', 'ROUTER', 2, '网络路由器', 2)
    ]
    cursor.executemany("""
    INSERT INTO asset_category (name, code, parent_id, description, sort_order)
    VALUES (?, ?, ?, ?, ?)
    """, categories)
    
    # 创建示例资产
    assets = [
        ('AS20240001', 'Dell服务器01', 'Dell', 'PowerEdge R740', '服务器', 
         2, 4, 4, 'Dell中国', '2024-01-15', 85000.00, '2024-01-15', '2027-01-15', 
         36, '张三', 'IT部', '2024-01-20', '在用', '优', 'DL001SN2024001'),
        ('AS20240002', 'HP工作站01', 'HP', 'Z4 G4', '工作站', 
         1, 2, 2, 'HP中国', '2024-02-10', 12000.00, '2024-02-10', '2027-02-10', 
         36, '李四', '研发部', '2024-02-15', '在用', '良', 'HP001SN2024002'),
        ('AS20240003', 'Cisco交换机01', 'Cisco', 'Catalyst 3850', '交换机', 
         2, 4, 4, 'Cisco中国', '2024-01-20', 25000.00, '2024-01-20', '2027-01-20', 
         36, '网络管理员', 'IT部', '2024-01-25', '在用', '优', 'CS001SN2024003')
    ]
    cursor.executemany("""
    INSERT INTO it_asset (asset_code, name, brand, model, category, building_id, floor_id, room_id,
                         supplier, purchase_date, purchase_price, warranty_start_date, warranty_end_date,
                         warranty_period, user_name, user_department, deploy_date, status,
                         condition_rating, serial_number)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, assets)
    
    # 提交事务
    conn.commit()
    conn.close()
    
    print("✅ SQLite数据库初始化完成！")
    print(f"📁 数据库文件: {db_path}")
    print(f"👤 管理员账户: admin / admin123")
    
    return db_path

if __name__ == "__main__":
    create_sqlite_database()