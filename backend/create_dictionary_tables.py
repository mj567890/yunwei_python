"""
数据字典数据库表创建脚本
"""
import sqlite3
import os
from datetime import datetime

def create_dictionary_tables():
    """创建数据字典相关表"""
    # 使用根目录的数据库文件
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'it_ops_system.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("开始创建数据字典表...")
    
    # 1. 运维记录类型字典表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dict_maintenance_type (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            parent_id INTEGER,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT 0,
            FOREIGN KEY (parent_id) REFERENCES dict_maintenance_type (id)
        )
    ''')
    
    # 2. 运维维护类别字典表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dict_maintenance_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            parent_id INTEGER,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT 0,
            FOREIGN KEY (parent_id) REFERENCES dict_maintenance_category (id)
        )
    ''')
    
    # 3. 组织机构字典表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dict_department (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            code VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            parent_id INTEGER,
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_deleted BOOLEAN DEFAULT 0,
            FOREIGN KEY (parent_id) REFERENCES dict_department (id)
        )
    ''')
    
    print("数据字典表创建完成！")
    
    # 插入初始数据
    print("开始插入初始数据...")
    
    now = datetime.now().isoformat()
    
    # 运维记录类型初始数据
    maintenance_types = [
        ('例行维护', 'ROUTINE_MAINTENANCE', '定期维护和保养', None, 1),
        ('硬件维护', 'HARDWARE_MAINTENANCE', '硬件设备维护', 1, 1),
        ('软件维护', 'SOFTWARE_MAINTENANCE', '软件系统维护', 1, 2),
        ('系统巡检', 'SYSTEM_INSPECTION', '系统状态巡检', 1, 3),
        
        ('故障处理', 'FAULT_HANDLING', '故障修复和处理', None, 2),
        ('硬件故障', 'HARDWARE_FAULT', '硬件故障修复', 2, 1),
        ('软件故障', 'SOFTWARE_FAULT', '软件故障修复', 2, 2),
        ('网络故障', 'NETWORK_FAULT', '网络故障修复', 2, 3),
        
        ('升级改造', 'UPGRADE_TRANSFORMATION', '系统升级和改造', None, 3),
        ('硬件升级', 'HARDWARE_UPGRADE', '硬件设备升级', 3, 1),
        ('软件升级', 'SOFTWARE_UPGRADE', '软件系统升级', 3, 2),
        ('系统改造', 'SYSTEM_TRANSFORMATION', '系统架构改造', 3, 3),
        
        ('应急处理', 'EMERGENCY_HANDLING', '紧急事件处理', None, 4),
        ('安全事件', 'SECURITY_INCIDENT', '安全事件处理', 4, 1),
        ('紧急故障', 'EMERGENCY_FAULT', '紧急故障处理', 4, 2),
        ('其他应急', 'OTHER_EMERGENCY', '其他应急事件', 4, 3)
    ]
    
    try:
        # 先检查是否已有数据
        cursor.execute('SELECT COUNT(*) FROM dict_maintenance_type')
        if cursor.fetchone()[0] == 0:
            for name, code, desc, parent_id, sort_order in maintenance_types:
                cursor.execute('''
                    INSERT INTO dict_maintenance_type (name, code, description, parent_id, sort_order, is_active, created_at, updated_at, is_deleted)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, 0)
                ''', (name, code, desc, parent_id, sort_order, now, now))
            print("✅ 运维记录类型初始数据插入完成")
        else:
            print("⚠️ 运维记录类型数据已存在，跳过插入")
    except Exception as e:
        print(f"❌ 插入运维记录类型数据失败: {e}")
    
    # 运维维护类别初始数据
    maintenance_categories = [
        ('硬件设备', 'HARDWARE_DEVICE', '硬件设备相关维护', None, 1),
        ('服务器', 'SERVER', '服务器维护', 1, 1),
        ('网络设备', 'NETWORK_DEVICE', '网络设备维护', 1, 2),
        ('存储设备', 'STORAGE_DEVICE', '存储设备维护', 1, 3),
        ('办公设备', 'OFFICE_DEVICE', '办公设备维护', 1, 4),
        
        ('软件系统', 'SOFTWARE_SYSTEM', '软件系统相关维护', None, 2),
        ('操作系统', 'OPERATING_SYSTEM', '操作系统维护', 2, 1),
        ('应用软件', 'APPLICATION_SOFTWARE', '应用软件维护', 2, 2),
        ('数据库', 'DATABASE', '数据库维护', 2, 3),
        ('安全软件', 'SECURITY_SOFTWARE', '安全软件维护', 2, 4),
        
        ('网络环境', 'NETWORK_ENVIRONMENT', '网络环境相关维护', None, 3),
        ('网络连接', 'NETWORK_CONNECTION', '网络连接维护', 3, 1),
        ('网络安全', 'NETWORK_SECURITY', '网络安全维护', 3, 2),
        ('网络配置', 'NETWORK_CONFIG', '网络配置维护', 3, 3),
        
        ('基础设施', 'INFRASTRUCTURE', '基础设施相关维护', None, 4),
        ('机房环境', 'COMPUTER_ROOM', '机房环境维护', 4, 1),
        ('电力系统', 'POWER_SYSTEM', '电力系统维护', 4, 2),
        ('空调系统', 'AIR_CONDITIONING', '空调系统维护', 4, 3)
    ]
    
    try:
        cursor.execute('SELECT COUNT(*) FROM dict_maintenance_category')
        if cursor.fetchone()[0] == 0:
            for name, code, desc, parent_id, sort_order in maintenance_categories:
                cursor.execute('''
                    INSERT INTO dict_maintenance_category (name, code, description, parent_id, sort_order, is_active, created_at, updated_at, is_deleted)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, 0)
                ''', (name, code, desc, parent_id, sort_order, now, now))
            print("✅ 运维维护类别初始数据插入完成")
        else:
            print("⚠️ 运维维护类别数据已存在，跳过插入")
    except Exception as e:
        print(f"❌ 插入运维维护类别数据失败: {e}")
    
    # 组织机构初始数据
    departments = [
        ('信息技术部', 'IT_DEPT', '信息技术部门', None, 1),
        ('运维中心', 'OPS_CENTER', '运维中心', 1, 1),
        ('网络中心', 'NETWORK_CENTER', '网络中心', 1, 2),
        ('系统中心', 'SYSTEM_CENTER', '系统中心', 1, 3),
        ('安全中心', 'SECURITY_CENTER', '安全中心', 1, 4),
        
        ('技术部', 'TECH_DEPT', '技术部门', None, 2),
        ('研发中心', 'RD_CENTER', '研发中心', 2, 1),
        ('测试中心', 'TEST_CENTER', '测试中心', 2, 2),
        ('产品中心', 'PRODUCT_CENTER', '产品中心', 2, 3),
        
        ('综合管理部', 'ADMIN_DEPT', '综合管理部门', None, 3),
        ('行政中心', 'ADMIN_CENTER', '行政中心', 3, 1),
        ('人事中心', 'HR_CENTER', '人事中心', 3, 2),
        ('财务中心', 'FINANCE_CENTER', '财务中心', 3, 3)
    ]
    
    try:
        cursor.execute('SELECT COUNT(*) FROM dict_department')
        if cursor.fetchone()[0] == 0:
            for name, code, desc, parent_id, sort_order in departments:
                cursor.execute('''
                    INSERT INTO dict_department (name, code, description, parent_id, sort_order, is_active, created_at, updated_at, is_deleted)
                    VALUES (?, ?, ?, ?, ?, 1, ?, ?, 0)
                ''', (name, code, desc, parent_id, sort_order, now, now))
            print("✅ 组织机构初始数据插入完成")
        else:
            print("⚠️ 组织机构数据已存在，跳过插入")
    except Exception as e:
        print(f"❌ 插入组织机构数据失败: {e}")
    
    conn.commit()
    conn.close()
    
    print("🎉 数据字典数据库初始化完成！")

if __name__ == '__main__':
    create_dictionary_tables()