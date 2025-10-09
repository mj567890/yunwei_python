#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加数据字典示例数据脚本
为运维记录类型、运维维护类别、组织机构添加实用的示例数据
"""

import sqlite3
from datetime import datetime

def add_sample_data():
    """添加示例数据到数据字典表"""
    conn = sqlite3.connect('it_ops_system.db')
    cursor = conn.cursor()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        print("🚀 开始添加数据字典示例数据...")
        
        # 1. 添加运维记录类型数据
        print("\n📋 添加运维记录类型数据...")
        maintenance_types = [
            # 主要类型（父级）
            ('HARDWARE', '硬件维护', '服务器、网络设备等硬件设备的维护工作', None, 1, True),
            ('SOFTWARE', '软件维护', '操作系统、应用软件、数据库等软件的维护工作', None, 2, True),
            ('NETWORK', '网络维护', '网络设备、线路、网络服务的维护工作', None, 3, True),
            ('SECURITY', '安全维护', '信息安全、数据安全相关的维护工作', None, 4, True),
            ('BACKUP', '备份维护', '数据备份、系统备份相关的维护工作', None, 5, True),
            ('MONITOR', '监控维护', '系统监控、网络监控、应用监控相关工作', None, 6, True),
        ]
        
        # 插入主要类型
        for code, name, desc, parent, sort, active in maintenance_types:
            cursor.execute('''
                INSERT OR IGNORE INTO dict_maintenance_type 
                (code, name, description, parent_id, sort_order, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, desc, parent, sort, active, current_time, current_time))
        
        # 获取父级ID用于添加子级
        cursor.execute('SELECT id, code FROM dict_maintenance_type WHERE parent_id IS NULL')
        parent_types = dict(cursor.fetchall())
        
        # 添加子级类型
        hardware_id = next((id for id, code in parent_types.items() if code == 'HARDWARE'), None)
        software_id = next((id for id, code in parent_types.items() if code == 'SOFTWARE'), None)
        network_id = next((id for id, code in parent_types.items() if code == 'NETWORK'), None)
        
        sub_types = []
        if hardware_id:
            sub_types.extend([
                ('SERVER_MAINT', '服务器维护', '服务器硬件检查、清洁、部件更换等', hardware_id, 11, True),
                ('STORAGE_MAINT', '存储维护', '存储设备维护、磁盘检查、阵列维护等', hardware_id, 12, True),
                ('UPS_MAINT', 'UPS维护', 'UPS电源维护、电池更换、供电检查等', hardware_id, 13, True),
            ])
        
        if software_id:
            sub_types.extend([
                ('OS_UPDATE', '系统更新', '操作系统补丁、更新、升级等', software_id, 21, True),
                ('APP_UPDATE', '应用更新', '应用软件升级、配置调整等', software_id, 22, True),
                ('DB_MAINT', '数据库维护', '数据库优化、备份、索引重建等', software_id, 23, True),
            ])
        
        if network_id:
            sub_types.extend([
                ('SWITCH_MAINT', '交换机维护', '交换机配置、端口检查、固件升级等', network_id, 31, True),
                ('ROUTER_MAINT', '路由器维护', '路由器配置、策略调整、性能优化等', network_id, 32, True),
                ('FIREWALL_MAINT', '防火墙维护', '防火墙规则调整、策略更新等', network_id, 33, True),
            ])
        
        for code, name, desc, parent, sort, active in sub_types:
            cursor.execute('''
                INSERT OR IGNORE INTO dict_maintenance_type 
                (code, name, description, parent_id, sort_order, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, desc, parent, sort, active, current_time, current_time))
        
        # 2. 添加运维维护类别数据
        print("📋 添加运维维护类别数据...")
        maintenance_categories = [
            # 主要类别
            ('PREVENTIVE', '预防性维护', '定期进行的预防性维护工作，防患于未然', None, 1, True),
            ('CORRECTIVE', '纠正性维护', '发现问题后进行的修复性维护工作', None, 2, True),
            ('EMERGENCY', '应急维护', '紧急情况下的快速响应维护工作', None, 3, True),
            ('UPGRADE', '升级维护', '系统、软件、硬件的升级改造工作', None, 4, True),
            ('INSPECTION', '巡检维护', '定期巡检、状态检查相关工作', None, 5, True),
        ]
        
        for code, name, desc, parent, sort, active in maintenance_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO dict_maintenance_category 
                (code, name, description, parent_id, sort_order, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, desc, parent, sort, active, current_time, current_time))
        
        # 添加子类别
        cursor.execute('SELECT id, code FROM dict_maintenance_category WHERE parent_id IS NULL')
        parent_categories = dict(cursor.fetchall())
        
        preventive_id = next((id for id, code in parent_categories.items() if code == 'PREVENTIVE'), None)
        corrective_id = next((id for id, code in parent_categories.items() if code == 'CORRECTIVE'), None)
        emergency_id = next((id for id, code in parent_categories.items() if code == 'EMERGENCY'), None)
        
        sub_categories = []
        if preventive_id:
            sub_categories.extend([
                ('SCHEDULED', '计划维护', '按计划进行的定期维护工作', preventive_id, 11, True),
                ('PERIODIC', '周期维护', '按周期进行的维护工作', preventive_id, 12, True),
                ('CONDITION_BASED', '状态维护', '基于设备状态进行的维护', preventive_id, 13, True),
            ])
        
        if corrective_id:
            sub_categories.extend([
                ('FAULT_REPAIR', '故障修复', '设备故障后的修复工作', corrective_id, 21, True),
                ('PERFORMANCE_FIX', '性能修复', '性能问题的修复优化工作', corrective_id, 22, True),
                ('CONFIG_FIX', '配置修复', '配置错误的修复工作', corrective_id, 23, True),
            ])
        
        if emergency_id:
            sub_categories.extend([
                ('CRITICAL_REPAIR', '紧急修复', '关键系统的紧急修复', emergency_id, 31, True),
                ('HOTFIX', '热修复', '生产环境的热修复工作', emergency_id, 32, True),
                ('DISASTER_RECOVERY', '灾难恢复', '灾难恢复相关工作', emergency_id, 33, True),
            ])
        
        for code, name, desc, parent, sort, active in sub_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO dict_maintenance_category 
                (code, name, description, parent_id, sort_order, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, desc, parent, sort, active, current_time, current_time))
        
        # 3. 添加组织机构数据
        print("📋 添加组织机构数据...")
        departments = [
            # 一级部门
            ('IT_DEPT', 'IT部', '信息技术部门，负责公司IT基础设施和信息系统', None, 1, True),
            ('OPS_DEPT', '运维部', '运维部门，负责系统运维和技术支持', None, 2, True),
            ('DEV_DEPT', '开发部', '软件开发部门，负责应用开发和维护', None, 3, True),
            ('SEC_DEPT', '安全部', '信息安全部门，负责网络安全和数据安全', None, 4, True),
        ]
        
        for code, name, desc, parent, sort, active in departments:
            cursor.execute('''
                INSERT OR IGNORE INTO dict_department 
                (code, name, description, parent_id, sort_order, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, desc, parent, sort, active, current_time, current_time))
        
        # 获取父级部门ID
        cursor.execute('SELECT id, code FROM dict_department WHERE parent_id IS NULL')
        parent_depts = dict(cursor.fetchall())
        
        it_id = next((id for id, code in parent_depts.items() if code == 'IT_DEPT'), None)
        ops_id = next((id for id, code in parent_depts.items() if code == 'OPS_DEPT'), None)
        dev_id = next((id for id, code in parent_depts.items() if code == 'DEV_DEPT'), None)
        sec_id = next((id for id, code in parent_depts.items() if code == 'SEC_DEPT'), None)
        
        # 添加二级部门
        sub_departments = []
        if it_id:
            sub_departments.extend([
                ('IT_INFRA', '基础设施组', '负责服务器、网络等基础设施管理', it_id, 11, True),
                ('IT_SUPPORT', '技术支持组', '负责用户技术支持和问题解决', it_id, 12, True),
                ('IT_PROJECT', '项目管理组', 'IT项目的规划和管理', it_id, 13, True),
            ])
        
        if ops_id:
            sub_departments.extend([
                ('OPS_SYS', '系统运维组', '负责操作系统和应用系统运维', ops_id, 21, True),
                ('OPS_NET', '网络运维组', '负责网络设备和网络服务运维', ops_id, 22, True),
                ('OPS_DB', '数据库运维组', '负责数据库系统运维和优化', ops_id, 23, True),
                ('OPS_MONITOR', '监控运维组', '负责系统监控和告警处理', ops_id, 24, True),
            ])
        
        if dev_id:
            sub_departments.extend([
                ('DEV_FRONTEND', '前端开发组', '负责前端应用开发', dev_id, 31, True),
                ('DEV_BACKEND', '后端开发组', '负责后端服务开发', dev_id, 32, True),
                ('DEV_TEST', '测试组', '负责软件测试和质量保证', dev_id, 33, True),
            ])
        
        if sec_id:
            sub_departments.extend([
                ('SEC_NET', '网络安全组', '负责网络安全防护', sec_id, 41, True),
                ('SEC_DATA', '数据安全组', '负责数据安全和隐私保护', sec_id, 42, True),
                ('SEC_AUDIT', '安全审计组', '负责安全审计和合规检查', sec_id, 43, True),
            ])
        
        for code, name, desc, parent, sort, active in sub_departments:
            cursor.execute('''
                INSERT OR IGNORE INTO dict_department 
                (code, name, description, parent_id, sort_order, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, desc, parent, sort, active, current_time, current_time))
        
        # 提交事务
        conn.commit()
        
        # 统计添加的数据
        cursor.execute('SELECT COUNT(*) FROM dict_maintenance_type')
        types_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM dict_maintenance_category') 
        categories_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM dict_department')
        departments_count = cursor.fetchone()[0]
        
        print(f"\n✅ 示例数据添加完成！")
        print(f"📊 数据统计:")
        print(f"   - 运维记录类型: {types_count} 条")
        print(f"   - 运维维护类别: {categories_count} 条") 
        print(f"   - 组织机构: {departments_count} 条")
        
        print(f"\n🎯 数据特点:")
        print(f"   - 采用层级结构设计，包含父子关系")
        print(f"   - 覆盖IT运维的主要场景和分类")
        print(f"   - 编码规范，便于程序调用")
        print(f"   - 描述详细，便于用户理解")
        
    except Exception as e:
        print(f"❌ 添加示例数据时出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    add_sample_data()