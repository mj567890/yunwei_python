#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的网络端口管理模型
支持端口到端口的连接关系，用于拓扑图生成
"""

from app import db
from app.models.base import BaseModel
from datetime import datetime


class AssetPort(BaseModel):
    """资产端口模型（新的统一端口管理）"""
    __tablename__ = 'asset_port'
    
    # 基本信息
    asset_id = db.Column(db.Integer, db.ForeignKey('it_asset.id'), nullable=False, comment='资产ID')
    port_name = db.Column(db.String(50), nullable=False, comment='端口名称')
    port_type = db.Column(db.String(20), nullable=True, comment='端口类型：ethernet/fiber/console/management/power/usb')
    port_speed = db.Column(db.String(20), nullable=True, comment='端口速率：1G/10G/40G/100G')
    port_status = db.Column(db.String(20), default='unused', comment='端口状态：used/unused/error/disabled')
    
    # 物理特性
    port_index = db.Column(db.Integer, nullable=True, comment='端口序号')
    is_uplink = db.Column(db.Boolean, default=False, comment='是否为上联端口')
    duplex_mode = db.Column(db.String(10), nullable=True, comment='双工模式：full/half/auto')
    
    # 网络配置
    vlan_id = db.Column(db.Integer, nullable=True, comment='VLAN ID')
    ip_address = db.Column(db.String(15), nullable=True, comment='端口IP地址')
    mac_address = db.Column(db.String(17), nullable=True, comment='端口MAC地址')
    
    # 连接信息
    is_connected = db.Column(db.Boolean, default=False, comment='是否已连接')
    connected_port_id = db.Column(db.Integer, db.ForeignKey('asset_port.id'), nullable=True, comment='连接的端口ID')
    cable_type = db.Column(db.String(20), nullable=True, comment='线缆类型：copper/fiber/wireless')
    cable_length = db.Column(db.Float, nullable=True, comment='线缆长度(米)')
    
    # 其他信息
    description = db.Column(db.String(255), nullable=True, comment='端口描述')
    last_link_time = db.Column(db.DateTime, nullable=True, comment='最后连接时间')
    
    # 关联关系
    asset = db.relationship('Asset', backref=db.backref('ports', lazy='dynamic'))
    connected_port = db.relationship('AssetPort', remote_side='AssetPort.id', 
                                   backref=db.backref('connected_from_ports', lazy='dynamic'))
    
    # 联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('asset_id', 'port_name', name='uk_asset_port_name'),
    )
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        
        if self.asset:
            result['asset_name'] = self.asset.name
            result['asset_code'] = self.asset.asset_code
            result['asset_category'] = self.asset.category
            
        if self.connected_port:
            result['connected_asset_name'] = self.connected_port.asset.name if self.connected_port.asset else None
            result['connected_port_name'] = self.connected_port.port_name
            result['connected_asset_id'] = self.connected_port.asset_id
            
        return result
    
    def connect_to_port(self, target_port, cable_type='copper', cable_length=None):
        """连接到另一个端口"""
        if not isinstance(target_port, AssetPort):
            raise ValueError("target_port must be an AssetPort instance")
            
        if target_port.asset_id == self.asset_id:
            raise ValueError("Cannot connect to port on the same device")
        
        # 断开当前连接
        self.disconnect()
        target_port.disconnect()
        
        # 建立双向连接
        self.is_connected = True
        self.connected_port_id = target_port.id
        self.port_status = 'used'
        self.cable_type = cable_type
        self.cable_length = cable_length
        self.last_link_time = datetime.utcnow()
        
        target_port.is_connected = True
        target_port.connected_port_id = self.id
        target_port.port_status = 'used'
        target_port.cable_type = cable_type
        target_port.cable_length = cable_length
        target_port.last_link_time = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'success': True,
            'message': f'端口 {self.asset.name}:{self.port_name} 与 {target_port.asset.name}:{target_port.port_name} 连接成功',
            'connection': {
                'source': {'asset': self.asset.name, 'port': self.port_name},
                'target': {'asset': target_port.asset.name, 'port': target_port.port_name},
                'cable_type': cable_type,
                'cable_length': cable_length
            }
        }
    
    def disconnect(self):
        """断开连接"""
        if self.connected_port:
            connected_port = self.connected_port
            connected_port.is_connected = False
            connected_port.connected_port_id = None
            connected_port.port_status = 'unused'
            connected_port.cable_type = None
            connected_port.cable_length = None
        
        self.is_connected = False
        self.connected_port_id = None
        self.port_status = 'unused'
        self.cable_type = None
        self.cable_length = None
        
        db.session.commit()
        
        return {'success': True, 'message': '端口连接已断开'}
    
    def get_connection_info(self):
        """获取连接信息"""
        if not self.is_connected or not self.connected_port:
            return None
            
        return {
            'connected': True,
            'target_asset': {
                'id': self.connected_port.asset_id,
                'name': self.connected_port.asset.name,
                'category': self.connected_port.asset.category
            },
            'target_port': {
                'id': self.connected_port.id,
                'name': self.connected_port.port_name,
                'type': self.connected_port.port_type
            },
            'cable': {
                'type': self.cable_type,
                'length': self.cable_length
            },
            'connected_time': self.last_link_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_link_time else None
        }


class PortConnection(BaseModel):
    """端口连接关系记录（用于历史追踪）"""
    __tablename__ = 'port_connection'
    
    source_port_id = db.Column(db.Integer, db.ForeignKey('asset_port.id'), nullable=False, comment='源端口ID')
    target_port_id = db.Column(db.Integer, db.ForeignKey('asset_port.id'), nullable=False, comment='目标端口ID')
    
    # 连接信息
    cable_type = db.Column(db.String(20), nullable=True, comment='线缆类型')
    cable_length = db.Column(db.Float, nullable=True, comment='线缆长度')
    connection_date = db.Column(db.DateTime, default=datetime.utcnow, comment='连接时间')
    disconnection_date = db.Column(db.DateTime, nullable=True, comment='断开时间')
    
    # 操作信息
    connected_by = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='连接操作人')
    disconnected_by = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='断开操作人')
    notes = db.Column(db.Text, nullable=True, comment='备注')
    
    # 状态
    is_active = db.Column(db.Boolean, default=True, comment='是否为当前连接')
    
    # 关联关系
    source_port = db.relationship('AssetPort', foreign_keys=[source_port_id])
    target_port = db.relationship('AssetPort', foreign_keys=[target_port_id])
    connected_by_user = db.relationship('User', foreign_keys=[connected_by])
    disconnected_by_user = db.relationship('User', foreign_keys=[disconnected_by])
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        
        if self.source_port:
            result['source'] = {
                'asset_name': self.source_port.asset.name,
                'port_name': self.source_port.port_name
            }
            
        if self.target_port:
            result['target'] = {
                'asset_name': self.target_port.asset.name,
                'port_name': self.target_port.port_name
            }
            
        if self.connected_by_user:
            result['connected_by_name'] = self.connected_by_user.real_name or self.connected_by_user.username
            
        if self.disconnected_by_user:
            result['disconnected_by_name'] = self.disconnected_by_user.real_name or self.disconnected_by_user.username
        
        return result