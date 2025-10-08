"""
资产管理模型
"""
from datetime import datetime, timedelta
from app import db
from app.models.base import BaseModel


class Asset(BaseModel):
    """资产模型"""
    __tablename__ = 'it_asset'
    
    # 基本信息
    asset_code = db.Column(db.String(50), unique=True, nullable=False, comment='资产编码')
    name = db.Column(db.String(100), nullable=False, comment='资产名称')
    brand = db.Column(db.String(50), nullable=True, comment='品牌')
    model = db.Column(db.String(100), nullable=True, comment='型号')
    category = db.Column(db.String(50), nullable=False, comment='资产类别')
    specification = db.Column(db.Text, nullable=True, comment='规格参数')
    
    # 位置信息
    building_id = db.Column(db.Integer, db.ForeignKey('building_info.id'), nullable=True, comment='楼宇ID')
    floor_id = db.Column(db.Integer, db.ForeignKey('floor_info.id'), nullable=True, comment='楼层ID')
    room_id = db.Column(db.Integer, db.ForeignKey('room_info.id'), nullable=True, comment='房间ID')
    location_detail = db.Column(db.String(255), nullable=True, comment='详细位置')
    
    # 采购信息
    supplier = db.Column(db.String(100), nullable=True, comment='供应商')
    purchase_date = db.Column(db.Date, nullable=True, comment='采购日期')
    purchase_price = db.Column(db.Numeric(12, 2), nullable=True, comment='采购价格')
    purchase_order = db.Column(db.String(50), nullable=True, comment='采购订单号')
    
    # 保修信息
    warranty_start_date = db.Column(db.Date, nullable=True, comment='保修开始日期')
    warranty_end_date = db.Column(db.Date, nullable=True, comment='保修结束日期')
    warranty_period = db.Column(db.Integer, nullable=True, comment='保修期(月)')
    
    # 使用信息
    user_name = db.Column(db.String(50), nullable=True, comment='使用人')
    user_department = db.Column(db.String(50), nullable=True, comment='使用部门')
    deploy_date = db.Column(db.Date, nullable=True, comment='部署日期')
    
    # 状态信息
    status = db.Column(db.String(20), default='在用', nullable=False, comment='资产状态：在用/闲置/维修/报废')
    condition_rating = db.Column(db.String(20), nullable=True, comment='状况评级：优/良/中/差')
    
    # 其他信息
    serial_number = db.Column(db.String(100), nullable=True, comment='序列号')
    mac_address = db.Column(db.String(17), nullable=True, comment='MAC地址')
    ip_address = db.Column(db.String(15), nullable=True, comment='IP地址')
    qr_code = db.Column(db.String(255), nullable=True, comment='二维码')
    barcode = db.Column(db.String(255), nullable=True, comment='条形码')
    remark = db.Column(db.Text, nullable=True, comment='备注')
    
    # 网络设备专用字段
    device_type = db.Column(db.String(50), nullable=True, comment='设备类型：交换机/路由器/防火墙/服务器等')
    subnet_mask = db.Column(db.String(15), nullable=True, comment='子网掩码')
    gateway = db.Column(db.String(15), nullable=True, comment='网关')
    dns_servers = db.Column(db.String(255), nullable=True, comment='DNS服务器')
    firmware_version = db.Column(db.String(50), nullable=True, comment='固件版本')
    port_count = db.Column(db.Integer, nullable=True, comment='端口数量')
    is_managed = db.Column(db.Boolean, default=True, comment='是否纳管')
    
    # 拓扑信息
    x_position = db.Column(db.Float, nullable=True, comment='拓扑图X坐标')
    y_position = db.Column(db.Float, nullable=True, comment='拓扑图Y坐标')
    
    # 关联关系
    building = db.relationship('Building', backref=db.backref('assets', lazy='dynamic'))
    floor = db.relationship('Floor', backref=db.backref('assets', lazy='dynamic'))
    room = db.relationship('Room', backref=db.backref('assets', lazy='dynamic'))
    status_logs = db.relationship('AssetStatusLog', backref='asset', lazy='dynamic', cascade='all, delete-orphan')
    
    # 网络设备端口关联（只对网络设备类型有效）
    device_ports = db.relationship('DevicePort', backref='asset_device', lazy='dynamic', 
                                   foreign_keys='DevicePort.device_id', cascade='all, delete-orphan')
    
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
        
        # 保修状态
        result['warranty_status'] = self.get_warranty_status()
        result['warranty_days_left'] = self.get_warranty_days_left()
        
        # 使用天数
        result['usage_days'] = self.get_usage_days()
        
        # 网络设备专用信息
        if self.category in ['网络设备', '交换机', '路由器', '防火墙', '服务器']:
            result['is_network_device'] = True
            # 端口数量统计
            if hasattr(self, 'device_ports'):
                result['total_ports'] = self.device_ports.filter_by(is_deleted=False).count()
                result['connected_ports'] = self.device_ports.filter_by(is_deleted=False, is_connected=True).count()
        else:
            result['is_network_device'] = False
        
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
    
    def get_warranty_status(self):
        """获取保修状态"""
        if not self.warranty_end_date:
            return '未设置'
        
        today = datetime.now().date()
        if today <= self.warranty_end_date:
            return '保修中'
        else:
            return '已过保'
    
    def get_warranty_days_left(self):
        """获取保修剩余天数"""
        if not self.warranty_end_date:
            return None
        
        today = datetime.now().date()
        if today <= self.warranty_end_date:
            return (self.warranty_end_date - today).days
        else:
            return 0
    
    def get_usage_days(self):
        """获取使用天数"""
        if not self.deploy_date:
            return None
        
        today = datetime.now().date()
        return (today - self.deploy_date).days
    
    def is_warranty_expiring(self, days=30):
        """检查保修是否即将到期"""
        if not self.warranty_end_date:
            return False
        
        today = datetime.now().date()
        expiry_threshold = today + timedelta(days=days)
        
        return (today <= self.warranty_end_date <= expiry_threshold)
    
    def change_status(self, new_status, remark=None, user_id=None):
        """更改资产状态"""
        old_status = self.status
        self.status = new_status
        
        # 记录状态变更日志
        status_log = AssetStatusLog(
            asset_id=self.id,
            old_status=old_status,
            new_status=new_status,
            change_reason=remark,
            changed_by=user_id
        )
        db.session.add(status_log)
        
        self.save()
        return status_log
    
    def is_network_device(self):
        """判断是否为网络设备（基于数据库配置）"""
        # 优先检查类别表配置
        category = AssetCategory.query.filter_by(name=self.category, is_deleted=False).first()
        if category and category.is_network_device:
            return True
        # fallback到device_type字段
        return self.device_type is not None
    
    def is_topology_device(self):
        """判断是否为拓扑设备（可用于生成拓扑图）"""
        category = AssetCategory.query.filter_by(name=self.category, is_deleted=False).first()
        return category and category.can_topology
    
    def is_terminal_device(self):
        """判断是否为终端设备（作为拓扑连接端点）"""
        category = AssetCategory.query.filter_by(name=self.category, is_deleted=False).first()
        return category and category.is_terminal
    
    def get_category_config(self):
        """获取类别配置信息"""
        category = AssetCategory.query.filter_by(name=self.category, is_deleted=False).first()
        if category:
            return {
                'is_network_device': category.is_network_device,
                'can_topology': category.can_topology,
                'is_terminal': category.is_terminal,
                'default_port_count': category.default_port_count,
                'device_icon': category.device_icon or '📦',
                'device_color': category.device_color or '#909399'
            }
        return None
    
    def get_connected_devices(self):
        """获取连接的设备（网络设备专用）"""
        if not self.is_network_device():
            return []
        
        connected_devices = set()
        if hasattr(self, 'device_ports'):
            for port in self.device_ports.filter_by(is_deleted=False, is_connected=True).all():
                if port.connected_device_id:
                    connected_devices.add(port.connected_device_id)
        return list(connected_devices)
    
    def get_topology_data(self):
        """获取拓扑数据（网络设备专用）"""
        if not self.is_network_device():
            return None
        
        return {
            'id': self.id,
            'name': self.name,
            'type': self.device_type or self.category,
            'status': self.status,
            'ip': self.ip_address,
            'x': self.x_position or 0,
            'y': self.y_position or 0,
            'ports': [port.to_dict() for port in self.device_ports.filter_by(is_deleted=False).all()] if hasattr(self, 'device_ports') else []
        }


class AssetStatusLog(BaseModel):
    """资产状态变更日志"""
    __tablename__ = 'asset_status_log'
    
    asset_id = db.Column(db.Integer, db.ForeignKey('it_asset.id'), nullable=False, comment='资产ID')
    old_status = db.Column(db.String(20), nullable=True, comment='原状态')
    new_status = db.Column(db.String(20), nullable=False, comment='新状态')
    change_reason = db.Column(db.Text, nullable=True, comment='变更原因')
    changed_by = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='变更人ID')
    
    # 关联关系
    changed_by_user = db.relationship('User', backref=db.backref('asset_status_changes', lazy='dynamic'))
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        if self.changed_by_user:
            result['changed_by_name'] = self.changed_by_user.real_name or self.changed_by_user.username
        if self.asset:
            result['asset_name'] = self.asset.name
            result['asset_code'] = self.asset.asset_code
        return result


class AssetCategory(BaseModel):
    """资产类别模型"""
    __tablename__ = 'asset_category'
    
    name = db.Column(db.String(50), unique=True, nullable=False, comment='类别名称')
    code = db.Column(db.String(20), unique=True, nullable=False, comment='类别编码')
    parent_id = db.Column(db.Integer, db.ForeignKey('asset_category.id'), nullable=True, comment='父类别ID')
    description = db.Column(db.Text, nullable=True, comment='描述')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    
    # 网络设备特征配置
    is_network_device = db.Column(db.Boolean, default=False, comment='是否为网络设备')
    can_topology = db.Column(db.Boolean, default=False, comment='是否可用于拓扑图')
    is_terminal = db.Column(db.Boolean, default=False, comment='是否为终端设备')
    default_port_count = db.Column(db.Integer, nullable=True, comment='默认端口数量')
    device_icon = db.Column(db.String(20), nullable=True, comment='设备图标')
    device_color = db.Column(db.String(20), nullable=True, comment='设备颜色')
    
    # 自关联
    children = db.relationship('AssetCategory', backref=db.backref('parent', remote_side='AssetCategory.id'))
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        result['parent_name'] = self.parent.name if self.parent else None
        result['children_count'] = len(self.children)
        return result