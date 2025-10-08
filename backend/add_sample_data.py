#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加更多示例数据到数据库
包含维护记录、故障记录、网络设备等
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def add_sample_data():
    """添加示例数据"""
    
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'it_ops_system.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔧 开始添加示例数据...")
    
    # 创建维护记录表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        asset_id INTEGER,
        status VARCHAR(20) DEFAULT '待处理',
        priority VARCHAR(20) DEFAULT '中',
        assigned_to VARCHAR(50),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME
    )
    """)
    
    # 创建故障记录表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fault_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        fault_code VARCHAR(50),
        asset_id INTEGER,
        status VARCHAR(20) DEFAULT '未解决',
        severity VARCHAR(20) DEFAULT '中',
        reported_by VARCHAR(50),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        resolved_at DATETIME
    )
    """)
    
    # 创建网络设备表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS network_device (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        device_type VARCHAR(50),
        ip_address VARCHAR(45),
        mac_address VARCHAR(17),
        location VARCHAR(100),
        status VARCHAR(20) DEFAULT '在线',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 添加更多资产数据
    additional_assets = [
        ('AS20240004', 'Dell工作站02', 'Dell', 'Precision 3640', '工作站', 
         1, 2, 2, 'Dell中国', '2024-03-10', 8000.00, '2024-03-10', '2027-03-10', 
         36, '王五', '设计部', '2024-03-15', '在用', '良', 'DL002SN2024004'),
        ('AS20240005', 'Lenovo服务器01', 'Lenovo', 'ThinkServer RD550', '服务器', 
         2, 4, 4, 'Lenovo中国', '2024-02-20', 45000.00, '2024-02-20', '2027-02-20', 
         36, '系统管理员', 'IT部', '2024-02-25', '在用', '优', 'LN001SN2024005'),
        ('AS20240006', '打印机01', 'Canon', 'imageRUNNER 2630i', '办公设备', 
         1, 2, 2, 'Canon中国', '2024-01-30', 5500.00, '2024-01-30', '2027-01-30', 
         36, '办公室', '行政部', '2024-02-05', '在用', '良', 'CN001SN2024006'),
        ('AS20240007', 'UPS电源01', 'APC', 'Smart-UPS 3000VA', 'UPS', 
         2, 4, 4, 'APC中国', '2024-03-15', 12000.00, '2024-03-15', '2027-03-15', 
         36, '机房管理员', 'IT部', '2024-03-20', '在用', '优', 'APC001SN2024007'),
        ('AS20240008', '显示器01', 'Dell', 'UltraSharp U2720Q', '显示器', 
         1, 2, 2, 'Dell中国', '2024-04-10', 3200.00, '2024-04-10', '2027-04-10', 
         36, '赵六', '研发部', '2024-04-15', '在用', '优', 'DL003SN2024008'),
    ]
    
    for asset in additional_assets:
        cursor.execute("""
        INSERT INTO it_asset (asset_code, name, brand, model, category, building_id, floor_id, room_id,
                             supplier, purchase_date, purchase_price, warranty_start_date, warranty_end_date,
                             warranty_period, user_name, user_department, deploy_date, status,
                             condition_rating, serial_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, asset)
    
    # 添加网络设备数据
    network_devices = [
        ('核心交换机01', '交换机', '192.168.1.1', '00:1A:2B:3C:4D:01', '主机房', '在线'),
        ('汇聚交换机01', '交换机', '192.168.1.2', '00:1A:2B:3C:4D:02', '主机房', '在线'),
        ('边缘交换机01', '交换机', '192.168.1.10', '00:1A:2B:3C:4D:03', '办公区', '在线'),
        ('边缘交换机02', '交换机', '192.168.1.11', '00:1A:2B:3C:4D:04', '办公区', '离线'),
        ('防火墙01', '防火墙', '192.168.1.254', '00:1A:2B:3C:4D:05', '主机房', '在线'),
        ('路由器01', '路由器', '192.168.0.1', '00:1A:2B:3C:4D:06', '主机房', '在线'),
        ('无线AP01', '无线接入点', '192.168.1.20', '00:1A:2B:3C:4D:07', '办公区1层', '在线'),
        ('无线AP02', '无线接入点', '192.168.1.21', '00:1A:2B:3C:4D:08', '办公区2层', '在线'),
        ('无线AP03', '无线接入点', '192.168.1.22', '00:1A:2B:3C:4D:09', '会议室', '维护'),
        ('负载均衡器01', '负载均衡器', '192.168.1.100', '00:1A:2B:3C:4D:10', '主机房', '在线'),
    ]
    
    for device in network_devices:
        cursor.execute("""
        INSERT INTO network_device (name, device_type, ip_address, mac_address, location, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, device)
    
    # 添加维护记录数据
    maintenance_records = [
        ('服务器硬盘更换', '更换Dell服务器故障硬盘', 1, '已完成', '高', '张三', '2024-10-05 10:00:00', '2024-10-05 14:30:00'),
        ('交换机端口检修', '检查核心交换机所有端口状态', None, '进行中', '中', '李四', '2024-10-06 09:00:00', None),
        ('UPS电池更换', '机房UPS电源电池例行更换', 4, '待处理', '中', '王五', '2024-10-07 08:00:00', None),
        ('网络设备固件升级', '升级防火墙固件到最新版本', None, '计划中', '低', '赵六', '2024-10-08 18:00:00', None),
        ('服务器系统补丁', '安装Windows Server安全补丁', 2, '已完成', '高', '张三', '2024-10-03 20:00:00', '2024-10-04 02:00:00'),
        ('打印机维护', '清洁打印机并更换墨盒', 3, '已完成', '低', '行政人员', '2024-10-01 14:00:00', '2024-10-01 15:30:00'),
        ('机房温度检查', '检查机房空调系统运行状态', None, '待处理', '中', '机房管理员', '2024-10-08 10:00:00', None),
        ('网络性能优化', '优化网络配置提升性能', None, '计划中', '中', '网络工程师', '2024-10-10 16:00:00', None),
    ]
    
    for record in maintenance_records:
        cursor.execute("""
        INSERT INTO maintenance_record (title, description, asset_id, status, priority, assigned_to, created_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, record)
    
    # 添加故障记录数据
    fault_records = [
        ('服务器硬盘故障', 'Dell服务器出现硬盘SMART错误', 'FLT20241001', 1, '已解决', '高', '系统监控', '2024-10-01 09:30:00', '2024-10-05 14:30:00'),
        ('交换机端口异常', '边缘交换机端口2无法正常工作', 'FLT20241002', None, '未解决', '中', '网络管理员', '2024-10-02 11:15:00', None),
        ('打印机卡纸', '办公室打印机频繁出现卡纸问题', 'FLT20241003', 3, '已解决', '低', '用户报告', '2024-09-28 14:20:00', '2024-10-01 15:30:00'),
        ('网络连接中断', '研发部网络间歇性中断', 'FLT20241004', None, '调查中', '高', '用户报告', '2024-10-03 16:45:00', None),
        ('UPS电池老化', 'UPS电源电池容量下降', 'FLT20241005', 4, '待处理', '中', '设备巡检', '2024-10-04 08:00:00', None),
        ('显示器闪烁', '工作站显示器出现闪烁现象', 'FLT20241006', 5, '已解决', '低', '用户报告', '2024-10-05 10:30:00', '2024-10-05 11:00:00'),
        ('防火墙规则冲突', '防火墙配置存在规则冲突', 'FLT20241007', None, '未解决', '高', '安全审计', '2024-10-06 13:20:00', None),
        ('无线网络不稳定', '会议室无线网络信号不稳定', 'FLT20241008', None, '调查中', '中', '用户报告', '2024-10-07 09:15:00', None),
    ]
    
    for record in fault_records:
        cursor.execute("""
        INSERT INTO fault_record (title, description, fault_code, asset_id, status, severity, reported_by, created_at, resolved_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, record)
    
    # 提交事务
    conn.commit()
    conn.close()
    
    print("✅ 示例数据添加完成！")
    print("📊 数据统计:")
    print("   - 新增资产: 5个")
    print("   - 网络设备: 10个")
    print("   - 维护记录: 8个")
    print("   - 故障记录: 8个")

if __name__ == "__main__":
    add_sample_data()