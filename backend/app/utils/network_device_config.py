#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络设备配置管理工具
定义网络设备的分类和相关配置
"""

class NetworkDeviceConfig:
    """网络设备配置类"""
    
    # 网络设备分类配置
    DEVICE_CATEGORIES = {
        # 拓扑设备（用于生成拓扑图的核心网络设备）
        'topology_devices': {
            '交换机': {
                'icon': '🔀',
                'color': '#409eff',
                'description': '网络交换机设备',
                'can_topology': True,
                'default_ports': 24
            },
            '路由器': {
                'icon': '🌐', 
                'color': '#67c23a',
                'description': '网络路由器设备',
                'can_topology': True,
                'default_ports': 8
            },
            '防火墙': {
                'icon': '🛡️',
                'color': '#e6a23c',
                'description': '网络防火墙设备',
                'can_topology': True,
                'default_ports': 6
            },
            'BRAS': {
                'icon': '📡',
                'color': '#f56c6c',
                'description': '宽带接入服务器',
                'can_topology': True,
                'default_ports': 48
            },
            '网关': {
                'icon': '🚪',
                'color': '#909399',
                'description': '网络网关设备',
                'can_topology': True,
                'default_ports': 4
            },
            '负载均衡器': {
                'icon': '⚖️',
                'color': '#7c4dff',
                'description': '负载均衡设备',
                'can_topology': True,
                'default_ports': 8
            }
        },
        
        # 终端设备（作为拓扑的连接端点）
        'terminal_devices': {
            '服务器': {
                'icon': '🖥️',
                'color': '#606266',
                'description': '服务器设备',
                'can_topology': False,
                'is_terminal': True
            },
            '工作站': {
                'icon': '💻',
                'color': '#909399',
                'description': '工作站电脑',
                'can_topology': False,
                'is_terminal': True
            },
            '台式机': {
                'icon': '🖱️',
                'color': '#c0c4cc',
                'description': '台式电脑',
                'can_topology': False,
                'is_terminal': True
            },
            '笔记本': {
                'icon': '💾',
                'color': '#dcdfe6',
                'description': '笔记本电脑',
                'can_topology': False,
                'is_terminal': True
            }
        },
        
        # 其他IT设备（非网络设备）
        'other_devices': {
            '显示器': {
                'icon': '🖼️',
                'color': '#f5f7fa',
                'description': '显示器设备',
                'can_topology': False,
                'is_terminal': False
            },
            '打印机': {
                'icon': '🖨️',
                'color': '#ebeef5',
                'description': '打印机设备',
                'can_topology': False,
                'is_terminal': False
            },
            '办公设备': {
                'icon': '📱',
                'color': '#f4f4f5',
                'description': '其他办公设备',
                'can_topology': False,
                'is_terminal': False
            }
        }
    }
    
    @classmethod
    def get_all_network_categories(cls):
        """获取所有网络设备类别（大概念）"""
        topology_devices = list(cls.DEVICE_CATEGORIES['topology_devices'].keys())
        terminal_devices = list(cls.DEVICE_CATEGORIES['terminal_devices'].keys())
        return topology_devices + terminal_devices
    
    @classmethod
    def get_topology_categories(cls):
        """获取拓扑设备类别"""
        return list(cls.DEVICE_CATEGORIES['topology_devices'].keys())
    
    @classmethod  
    def get_terminal_categories(cls):
        """获取终端设备类别"""
        return list(cls.DEVICE_CATEGORIES['terminal_devices'].keys())
    
    @classmethod
    def get_other_categories(cls):
        """获取其他设备类别"""
        return list(cls.DEVICE_CATEGORIES['other_devices'].keys())
    
    @classmethod
    def is_network_device(cls, category):
        """判断是否为网络设备（大概念）"""
        return category in cls.get_all_network_categories()
    
    @classmethod
    def is_topology_device(cls, category):
        """判断是否为拓扑设备"""
        return category in cls.get_topology_categories()
    
    @classmethod
    def is_terminal_device(cls, category):
        """判断是否为终端设备"""
        return category in cls.get_terminal_categories()
    
    @classmethod
    def get_device_info(cls, category):
        """获取设备信息"""
        for device_type in cls.DEVICE_CATEGORIES.values():
            if category in device_type:
                return device_type[category]
        return None
    
    @classmethod
    def get_device_icon(cls, category):
        """获取设备图标"""
        info = cls.get_device_info(category)
        return info.get('icon', '📦') if info else '📦'
    
    @classmethod
    def get_device_color(cls, category):
        """获取设备颜色"""
        info = cls.get_device_info(category)
        return info.get('color', '#909399') if info else '#909399'


# 用于数据库初始化的标准分类数据
STANDARD_ASSET_CATEGORIES = [
    # 网络拓扑设备
    {'name': '交换机', 'code': 'SWITCH', 'description': '网络交换机设备', 'sort_order': 10},
    {'name': '路由器', 'code': 'ROUTER', 'description': '网络路由器设备', 'sort_order': 20},
    {'name': '防火墙', 'code': 'FIREWALL', 'description': '网络防火墙设备', 'sort_order': 30},
    {'name': 'BRAS', 'code': 'BRAS', 'description': '宽带接入服务器', 'sort_order': 40},
    {'name': '网关', 'code': 'GATEWAY', 'description': '网络网关设备', 'sort_order': 50},
    {'name': '负载均衡器', 'code': 'LOAD_BALANCER', 'description': '负载均衡设备', 'sort_order': 60},
    
    # 终端设备
    {'name': '服务器', 'code': 'SERVER', 'description': '服务器设备', 'sort_order': 70},
    {'name': '工作站', 'code': 'WORKSTATION', 'description': '工作站电脑', 'sort_order': 80},
    {'name': '台式机', 'code': 'DESKTOP', 'description': '台式电脑', 'sort_order': 90},
    {'name': '笔记本', 'code': 'LAPTOP', 'description': '笔记本电脑', 'sort_order': 100},
    
    # 其他设备
    {'name': '显示器', 'code': 'MONITOR', 'description': '显示器设备', 'sort_order': 110},
    {'name': '打印机', 'code': 'PRINTER', 'description': '打印机设备', 'sort_order': 120},
    {'name': '办公设备', 'code': 'OFFICE_EQUIPMENT', 'description': '其他办公设备', 'sort_order': 130}
]