"""
运维记录管理模型
"""
from app import db
from app.models.base import BaseModel


class MaintenanceRecord(BaseModel):
    """运维记录模型"""
    __tablename__ = 'maintenance_record'
    
    # 基本信息
    title = db.Column(db.String(200), nullable=False, comment='记录标题')
    record_type = db.Column(db.String(50), nullable=False, comment='运维类型：例行维护/紧急处理/升级改造/故障修复/巡检')
    priority = db.Column(db.String(20), default='中', nullable=False, comment='优先级：低/中/高/紧急')
    status = db.Column(db.String(20), default='计划中', nullable=False, comment='状态：计划中/进行中/已完成/已取消')
    
    # 时间信息
    planned_start_time = db.Column(db.DateTime, nullable=True, comment='计划开始时间')
    planned_end_time = db.Column(db.DateTime, nullable=True, comment='计划结束时间')
    actual_start_time = db.Column(db.DateTime, nullable=True, comment='实际开始时间')
    actual_end_time = db.Column(db.DateTime, nullable=True, comment='实际结束时间')
    
    # 人员信息
    assignee_id = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='负责人ID')
    reporter_id = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='报告人ID')
    participants = db.Column(db.String(255), nullable=True, comment='参与人员')
    
    # 内容信息
    description = db.Column(db.Text, nullable=True, comment='详细描述')
    work_content = db.Column(db.Text, nullable=True, comment='工作内容')
    result_description = db.Column(db.Text, nullable=True, comment='工作结果')
    problem_description = db.Column(db.Text, nullable=True, comment='问题描述')
    solution_description = db.Column(db.Text, nullable=True, comment='解决方案')
    
    # 关联资源
    related_asset_ids = db.Column(db.String(255), nullable=True, comment='关联资产ID列表')
    related_device_ids = db.Column(db.String(255), nullable=True, comment='关联设备ID列表')
    
    # 位置信息
    building_id = db.Column(db.Integer, db.ForeignKey('building_info.id'), nullable=True, comment='楼宇ID')
    floor_id = db.Column(db.Integer, db.ForeignKey('floor_info.id'), nullable=True, comment='楼层ID')
    room_id = db.Column(db.Integer, db.ForeignKey('room_info.id'), nullable=True, comment='房间ID')
    location_detail = db.Column(db.String(255), nullable=True, comment='详细位置')
    
    # 成本信息
    estimated_cost = db.Column(db.Numeric(12, 2), nullable=True, comment='预估成本')
    actual_cost = db.Column(db.Numeric(12, 2), nullable=True, comment='实际成本')
    cost_items = db.Column(db.Text, nullable=True, comment='成本明细(JSON)')
    
    # 评估信息
    difficulty_level = db.Column(db.String(20), nullable=True, comment='难度等级：简单/中等/困难/复杂')
    risk_level = db.Column(db.String(20), nullable=True, comment='风险等级：低/中/高')
    impact_scope = db.Column(db.String(100), nullable=True, comment='影响范围')
    
    # 关联关系
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref=db.backref('assigned_records', lazy='dynamic'))
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref=db.backref('reported_records', lazy='dynamic'))
    building = db.relationship('Building', backref=db.backref('maintenance_records', lazy='dynamic'))
    floor = db.relationship('Floor', backref=db.backref('maintenance_records', lazy='dynamic'))
    room = db.relationship('Room', backref=db.backref('maintenance_records', lazy='dynamic'))
    
    # 一对多关系
    attachments = db.relationship('MaintenanceAttachment', backref='record', lazy='dynamic', cascade='all, delete-orphan')
    progress_logs = db.relationship('MaintenanceProgress', backref='record', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        
        # 添加关联信息
        if self.assignee:
            result['assignee_name'] = self.assignee.real_name or self.assignee.username
        if self.reporter:
            result['reporter_name'] = self.reporter.real_name or self.reporter.username
            
        # 位置信息
        if self.building:
            result['building_name'] = self.building.name
        if self.floor:
            result['floor_name'] = self.floor.name
        if self.room:
            result['room_name'] = self.room.name
        result['full_location'] = self.get_full_location()
        
        # 附件和进度
        result['attachment_count'] = self.attachments.filter_by(is_deleted=False).count()
        result['progress_count'] = self.progress_logs.filter_by(is_deleted=False).count()
        
        # 工期计算
        result['planned_duration'] = self.get_planned_duration()
        result['actual_duration'] = self.get_actual_duration()
        
        # 成本明细
        if self.cost_items:
            import json
            try:
                result['cost_items'] = json.loads(self.cost_items)
            except:
                result['cost_items'] = []
        
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
    
    def get_planned_duration(self):
        """获取计划工期(小时)"""
        if self.planned_start_time and self.planned_end_time:
            delta = self.planned_end_time - self.planned_start_time
            return round(delta.total_seconds() / 3600, 2)
        return None
    
    def get_actual_duration(self):
        """获取实际工期(小时)"""
        if self.actual_start_time and self.actual_end_time:
            delta = self.actual_end_time - self.actual_start_time
            return round(delta.total_seconds() / 3600, 2)
        return None
    
    def get_related_assets(self):
        """获取关联资产"""
        if not self.related_asset_ids:
            return []
        
        from app.models.asset import Asset
        asset_ids = [int(id.strip()) for id in self.related_asset_ids.split(',') if id.strip().isdigit()]
        return Asset.query.filter(Asset.id.in_(asset_ids), Asset.is_deleted == False).all()
    
    def get_related_devices(self):
        """获取关联设备"""
        if not self.related_device_ids:
            return []
        
        from app.models.network import NetworkDevice
        device_ids = [int(id.strip()) for id in self.related_device_ids.split(',') if id.strip().isdigit()]
        return NetworkDevice.query.filter(NetworkDevice.id.in_(device_ids), NetworkDevice.is_deleted == False).all()


class MaintenanceAttachment(BaseModel):
    """运维记录附件模型"""
    __tablename__ = 'maintenance_attachment'
    
    record_id = db.Column(db.Integer, db.ForeignKey('maintenance_record.id'), nullable=False, comment='运维记录ID')
    filename = db.Column(db.String(255), nullable=False, comment='文件名')
    original_filename = db.Column(db.String(255), nullable=False, comment='原始文件名')
    file_path = db.Column(db.String(500), nullable=False, comment='文件路径')
    file_size = db.Column(db.Integer, nullable=True, comment='文件大小(字节)')
    file_type = db.Column(db.String(50), nullable=True, comment='文件类型')
    upload_time = db.Column(db.DateTime, nullable=True, comment='上传时间')
    description = db.Column(db.String(255), nullable=True, comment='文件描述')
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        result['file_size_mb'] = round(self.file_size / 1024 / 1024, 2) if self.file_size else 0
        return result


class MaintenanceProgress(BaseModel):
    """运维进度记录模型"""
    __tablename__ = 'maintenance_progress'
    
    record_id = db.Column(db.Integer, db.ForeignKey('maintenance_record.id'), nullable=False, comment='运维记录ID')
    progress_time = db.Column(db.DateTime, nullable=False, comment='进度时间')
    progress_content = db.Column(db.Text, nullable=False, comment='进度内容')
    progress_type = db.Column(db.String(20), nullable=True, comment='进度类型：开始/进行中/暂停/完成/问题')
    operator_id = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='操作人ID')
    
    # 关联关系
    operator = db.relationship('User', backref=db.backref('maintenance_progress', lazy='dynamic'))
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        if self.operator:
            result['operator_name'] = self.operator.real_name or self.operator.username
        return result


class MaintenanceTemplate(BaseModel):
    """运维模板模型"""
    __tablename__ = 'maintenance_template'
    
    name = db.Column(db.String(100), nullable=False, comment='模板名称')
    template_type = db.Column(db.String(50), nullable=False, comment='模板类型')
    description = db.Column(db.Text, nullable=True, comment='模板描述')
    work_content_template = db.Column(db.Text, nullable=True, comment='工作内容模板')
    checklist_template = db.Column(db.Text, nullable=True, comment='检查清单模板(JSON)')
    estimated_duration = db.Column(db.Integer, nullable=True, comment='预估时长(小时)')
    difficulty_level = db.Column(db.String(20), nullable=True, comment='难度等级')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        if self.checklist_template:
            import json
            try:
                result['checklist_template'] = json.loads(self.checklist_template)
            except:
                result['checklist_template'] = []
        return result