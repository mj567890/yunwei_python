"""
模型包初始化文件
导入所有模型以便Flask-Migrate自动发现
"""

# 导入基础模型
from .base import BaseModel

# 导入用户权限模型
from .user import User, Role, Permission, OperationLog

# 导入位置模型
from .location import Building, Floor, Room

# 导入资产模型
from .asset import Asset, AssetStatusLog, AssetCategory

# 导入网络设备模型
from .network import NetworkDevice, DevicePort, NetworkTopology

# 导入运维记录模型
from .maintenance import MaintenanceRecord, MaintenanceAttachment, MaintenanceProgress, MaintenanceTemplate

# 导入故障分析模型
from .fault import FaultRecord, FaultImpactAnalysis, FaultProgress

# 导入文件管理模型
from .file import FileInfo

# 导出所有模型类
__all__ = [
    'BaseModel',
    'User', 'Role', 'Permission', 'OperationLog',
    'Building', 'Floor', 'Room',
    'Asset', 'AssetStatusLog', 'AssetCategory',
    'NetworkDevice', 'DevicePort', 'NetworkTopology',
    'MaintenanceRecord', 'MaintenanceAttachment', 'MaintenanceProgress', 'MaintenanceTemplate',
    'FaultRecord', 'FaultImpactAnalysis', 'FaultProgress',
    'FileInfo'
]