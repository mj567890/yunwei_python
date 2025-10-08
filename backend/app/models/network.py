"""
网络设备管理模型
"""
from app import db
from app.models.base import BaseModel


class NetworkDevice(BaseModel):
    """网络设备模型"""
    __tablename__ = 'network_device'
    
    # 基本信息
    name = db.Column(db.String(100), nullable=False, comment='设备名称')
    device_type = db.Column(db.String(50), nullable=False, comment='设备类型：交换机/路由器/防火墙/安全设备')
    brand = db.Column(db.String(50), nullable=True, comment='品牌')
    model = db.Column(db.String(100), nullable=True, comment='型号')
    
    # 网络信息
    ip_address = db.Column(db.String(15), nullable=True, comment='IP地址')
    mac_address = db.Column(db.String(17), nullable=True, comment='MAC地址')
    subnet_mask = db.Column(db.String(15), nullable=True, comment='子网掩码')
    gateway = db.Column(db.String(15), nullable=True, comment='网关')
    dns_servers = db.Column(db.String(255), nullable=True, comment='DNS服务器')
    
    # 位置信息
    building_id = db.Column(db.Integer, db.ForeignKey('building_info.id'), nullable=True, comment='楼宇ID')
    floor_id = db.Column(db.Integer, db.ForeignKey('floor_info.id'), nullable=True, comment='楼层ID')
    room_id = db.Column(db.Integer, db.ForeignKey('room_info.id'), nullable=True, comment='房间ID')
    location_detail = db.Column(db.String(255), nullable=True, comment='详细位置')
    
    # 设备状态
    status = db.Column(db.String(20), default='正常', nullable=False, comment='设备状态：正常/故障/维护/离线')
    is_managed = db.Column(db.Boolean, default=True, comment='是否纳管')
    
    # 拓扑信息
    x_position = db.Column(db.Float, nullable=True, comment='拓扑图X坐标')
    y_position = db.Column(db.Float, nullable=True, comment='拓扑图Y坐标')
    
    # 其他信息
    serial_number = db.Column(db.String(100), nullable=True, comment='序列号')
    firmware_version = db.Column(db.String(50), nullable=True, comment='固件版本')
    purchase_date = db.Column(db.Date, nullable=True, comment='采购日期')
    warranty_end_date = db.Column(db.Date, nullable=True, comment='保修结束日期')
    description = db.Column(db.Text, nullable=True, comment='设备描述')
    
    # 关联关系
    building = db.relationship('Building', backref=db.backref('network_devices', lazy='dynamic'))
    floor = db.relationship('Floor', backref=db.backref('network_devices', lazy='dynamic'))
    room = db.relationship('Room', backref=db.backref('network_devices', lazy='dynamic'))
    ports = db.relationship('DevicePort', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        
        # 添加位置信息
        if self.building:
            result['building_name'] = self.building.name
        if self.floor:
            result['floor_name'] = self.floor.name
        if self.room:
            result['room_name'] = self.room.name
            
        # 完整位置
        result['full_location'] = self.get_full_location()
        
        # 端口数量
        result['port_count'] = self.ports.filter_by(is_deleted=False).count()
        result['connected_port_count'] = self.ports.filter_by(is_deleted=False, is_connected=True).count()
        
        return result
    
    def get_full_location(self):
        """获取完整位置信息"""
        parts = []
        if self.building:
            parts.append(self.building.name)
        if self.floor:
            parts.append(self.floor.name)
        if self.room:
            parts.append(self.room.name)
        if self.location_detail:
            parts.append(self.location_detail)
        return '-'.join(parts) if parts else '未设置'
    
    def get_connected_devices(self):
        """获取连接的设备"""
        connected_devices = set()
        for port in self.ports:
            if port.is_connected and port.connected_device_id:
                connected_devices.add(port.connected_device_id)
        return list(connected_devices)
    
    def get_topology_data(self):
        """获取拓扑数据"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.device_type,
            'status': self.status,
            'ip': self.ip_address,
            'x': self.x_position or 0,
            'y': self.y_position or 0,
            'ports': [port.to_dict() for port in self.ports if not port.is_deleted]
        }


class DevicePort(BaseModel):
    """设备端口模型（兼容资产表）"""
    __tablename__ = 'device_port'
    
    # 兼容原有network_device和新的asset表
    device_id = db.Column(db.Integer, db.ForeignKey('network_device.id'), nullable=True, comment='网络设备ID（旧）')
    asset_device_id = db.Column(db.Integer, db.ForeignKey('it_asset.id'), nullable=True, comment='资产设备ID（新）')
    port_name = db.Column(db.String(50), nullable=False, comment='端口名称')
    port_type = db.Column(db.String(20), nullable=True, comment='端口类型：ethernet/fiber/console/management')
    port_speed = db.Column(db.String(20), nullable=True, comment='端口速率')
    
    # 连接信息
    is_connected = db.Column(db.Boolean, default=False, comment='是否连接')
    connected_device_id = db.Column(db.Integer, db.ForeignKey('network_device.id'), nullable=True, comment='连接的设备ID')
    connected_port_id = db.Column(db.Integer, db.ForeignKey('device_port.id'), nullable=True, comment='连接的端口ID')
    
    # 状态信息
    status = db.Column(db.String(20), default='未使用', comment='端口状态：使用中/未使用/故障')
    vlan_id = db.Column(db.Integer, nullable=True, comment='VLAN ID')
    description = db.Column(db.String(255), nullable=True, comment='端口描述')
    
    # 关联关系
    # 兼容旧的network_device和新的asset
    connected_device = db.relationship('NetworkDevice', foreign_keys=[connected_device_id], 
                                     backref=db.backref('connected_ports', lazy='dynamic'))
    connected_port = db.relationship('DevicePort', remote_side='DevicePort.id')
    
    # 新增与Asset的关联
    # asset_device 关联在 Asset 模型中定义
    
    # 添加联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('device_id', 'port_name', name='uk_device_port_name'),
    )
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        
        # 兼容旧的network_device和新的asset
        if self.device:
            result['device_name'] = self.device.name
            result['device_ip'] = self.device.ip_address
        elif self.asset_device_id:
            # 使用资产信息
            from app.models.asset import Asset
            asset = Asset.find_by_id(self.asset_device_id)
            if asset:
                result['device_name'] = asset.name
                result['device_ip'] = asset.ip_address
                result['asset_device'] = True
            
        if self.connected_device:
            result['connected_device_name'] = self.connected_device.name
            result['connected_device_ip'] = self.connected_device.ip_address
            
        if self.connected_port:
            result['connected_port_name'] = self.connected_port.port_name
            
        return result
    
    def connect_to_port(self, target_port):
        """连接到另一个端口"""
        # 断开当前连接
        self.disconnect()
        target_port.disconnect()
        
        # 建立新连接
        self.is_connected = True
        self.connected_device_id = target_port.device_id
        self.connected_port_id = target_port.id
        self.status = '使用中'
        
        target_port.is_connected = True
        target_port.connected_device_id = self.device_id
        target_port.connected_port_id = self.id
        target_port.status = '使用中'
        
        db.session.commit()
    
    def disconnect(self):
        """断开连接"""
        if self.connected_port:
            connected_port = self.connected_port
            connected_port.is_connected = False
            connected_port.connected_device_id = None
            connected_port.connected_port_id = None
            connected_port.status = '未使用'
        
        self.is_connected = False
        self.connected_device_id = None
        self.connected_port_id = None
        self.status = '未使用'
        
        db.session.commit()


class NetworkTopology(BaseModel):
    """网络拓扑模型"""
    __tablename__ = 'network_topology'
    
    name = db.Column(db.String(100), nullable=False, comment='拓扑名称')
    description = db.Column(db.Text, nullable=True, comment='拓扑描述')
    topology_data = db.Column(db.Text, nullable=True, comment='拓扑数据(JSON)')
    is_default = db.Column(db.Boolean, default=False, comment='是否默认拓扑')
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        if self.topology_data:
            import json
            try:
                result['topology_data'] = json.loads(self.topology_data)
            except:
                result['topology_data'] = None
        return result