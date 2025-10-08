"""
故障分析模型
"""
from datetime import datetime
from app import db
from app.models.base import BaseModel


class FaultRecord(BaseModel):
    """故障记录模型"""
    __tablename__ = 'fault_record'
    
    # 基本信息
    fault_code = db.Column(db.String(50), unique=True, nullable=False, comment='故障编号')
    title = db.Column(db.String(200), nullable=False, comment='故障标题')
    description = db.Column(db.Text, nullable=True, comment='故障描述')
    fault_type = db.Column(db.String(50), nullable=False, comment='故障类型：硬件故障/软件故障/网络故障/电源故障/其他')
    severity = db.Column(db.String(20), default='中', nullable=False, comment='严重程度：低/中/高/紧急')
    
    # 故障源
    source_type = db.Column(db.String(20), nullable=False, comment='故障源类型：asset/device')
    source_id = db.Column(db.Integer, nullable=False, comment='故障源ID')
    
    # 时间信息
    fault_time = db.Column(db.DateTime, nullable=False, comment='故障发生时间')
    report_time = db.Column(db.DateTime, default=datetime.utcnow, comment='故障报告时间')
    response_time = db.Column(db.DateTime, nullable=True, comment='响应时间')
    resolve_time = db.Column(db.DateTime, nullable=True, comment='解决时间')
    
    # 状态信息
    status = db.Column(db.String(20), default='待处理', nullable=False, comment='状态：待处理/处理中/已解决/已关闭')
    
    # 人员信息
    reporter_id = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='报告人ID')
    assignee_id = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='处理人ID')
    
    # 位置信息
    building_id = db.Column(db.Integer, db.ForeignKey('building_info.id'), nullable=True, comment='楼宇ID')
    floor_id = db.Column(db.Integer, db.ForeignKey('floor_info.id'), nullable=True, comment='楼层ID')
    room_id = db.Column(db.Integer, db.ForeignKey('room_info.id'), nullable=True, comment='房间ID')
    
    # 影响分析
    impact_scope = db.Column(db.Text, nullable=True, comment='影响范围')
    affected_users = db.Column(db.Integer, nullable=True, comment='影响用户数')
    business_impact = db.Column(db.String(20), nullable=True, comment='业务影响：无/轻微/中等/严重')
    
    # 处理结果
    cause_analysis = db.Column(db.Text, nullable=True, comment='原因分析')
    solution = db.Column(db.Text, nullable=True, comment='解决方案')
    prevention_measures = db.Column(db.Text, nullable=True, comment='预防措施')
    
    # 关联关系
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref=db.backref('reported_faults', lazy='dynamic'))
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref=db.backref('assigned_faults', lazy='dynamic'))
    building = db.relationship('Building', backref=db.backref('faults', lazy='dynamic'))
    floor = db.relationship('Floor', backref=db.backref('faults', lazy='dynamic'))
    room = db.relationship('Room', backref=db.backref('faults', lazy='dynamic'))
    
    # 一对多关系
    impact_analysis = db.relationship('FaultImpactAnalysis', backref='fault', uselist=False, cascade='all, delete-orphan')
    progress_logs = db.relationship('FaultProgress', backref='fault', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        
        # 添加关联信息
        if self.reporter:
            result['reporter_name'] = self.reporter.real_name or self.reporter.username
        if self.assignee:
            result['assignee_name'] = self.assignee.real_name or self.assignee.username
        
        # 位置信息
        if self.building:
            result['building_name'] = self.building.name
        if self.floor:
            result['floor_name'] = self.floor.name
        if self.room:
            result['room_name'] = self.room.name
        
        # 故障源信息
        result['source_info'] = self.get_source_info()
        
        # 时间计算
        result['response_duration'] = self.get_response_duration()
        result['resolve_duration'] = self.get_resolve_duration()
        
        # 影响分析
        if self.impact_analysis:
            result['impact_analysis'] = self.impact_analysis.to_dict()
        
        return result
    
    def get_source_info(self):
        """获取故障源信息"""
        if self.source_type == 'asset':
            from app.models.asset import Asset
            asset = Asset.find_by_id(self.source_id)
            if asset:
                return {
                    'type': 'asset',
                    'id': asset.id,
                    'name': asset.name,
                    'code': asset.asset_code,
                    'location': asset.get_full_location()
                }
        elif self.source_type == 'device':
            from app.models.network import NetworkDevice
            device = NetworkDevice.find_by_id(self.source_id)
            if device:
                return {
                    'type': 'device',
                    'id': device.id,
                    'name': device.name,
                    'ip': device.ip_address,
                    'location': device.get_full_location()
                }
        return None
    
    def get_response_duration(self):
        """获取响应时长(分钟)"""
        if self.response_time and self.report_time:
            delta = self.response_time - self.report_time
            return round(delta.total_seconds() / 60, 2)
        return None
    
    def get_resolve_duration(self):
        """获取解决时长(小时)"""
        if self.resolve_time and self.report_time:
            delta = self.resolve_time - self.report_time
            return round(delta.total_seconds() / 3600, 2)
        return None
    
    def auto_assign(self):
        """自动分配处理人"""
        # 这里可以实现自动分配逻辑
        # 例如根据故障类型、位置、人员负载等因素
        pass


class FaultImpactAnalysis(BaseModel):
    """故障影响分析模型"""
    __tablename__ = 'fault_impact_analysis'
    
    fault_id = db.Column(db.Integer, db.ForeignKey('fault_record.id'), nullable=False, comment='故障ID')
    
    # 影响设备分析
    affected_devices = db.Column(db.Text, nullable=True, comment='受影响设备列表(JSON)')
    device_count = db.Column(db.Integer, default=0, comment='受影响设备数量')
    
    # 影响资产分析
    affected_assets = db.Column(db.Text, nullable=True, comment='受影响资产列表(JSON)')
    asset_count = db.Column(db.Integer, default=0, comment='受影响资产数量')
    
    # 影响用户分析
    affected_user_count = db.Column(db.Integer, default=0, comment='受影响用户数')
    affected_departments = db.Column(db.String(255), nullable=True, comment='受影响部门')
    
    # 业务影响分析
    service_interruption = db.Column(db.Boolean, default=False, comment='是否导致服务中断')
    data_loss_risk = db.Column(db.Boolean, default=False, comment='是否有数据丢失风险')
    security_risk = db.Column(db.Boolean, default=False, comment='是否有安全风险')
    
    # 影响级别
    impact_level = db.Column(db.String(20), nullable=True, comment='影响级别：轻微/中等/严重/灾难')
    urgency_level = db.Column(db.String(20), nullable=True, comment='紧急程度：低/中/高/紧急')
    
    # 处理建议
    suggested_actions = db.Column(db.Text, nullable=True, comment='建议处理措施(JSON)')
    estimated_repair_time = db.Column(db.Integer, nullable=True, comment='预估修复时间(小时)')
    required_resources = db.Column(db.Text, nullable=True, comment='所需资源')
    
    # 分析时间
    analysis_time = db.Column(db.DateTime, default=datetime.utcnow, comment='分析时间')
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        
        # 解析JSON字段
        for field in ['affected_devices', 'affected_assets', 'suggested_actions']:
            if getattr(self, field):
                import json
                try:
                    result[field] = json.loads(getattr(self, field))
                except:
                    result[field] = []
        
        return result
    
    def analyze_impact(self):
        """执行影响分析"""
        fault = self.fault
        if not fault:
            return
        
        # 获取故障源
        source_info = fault.get_source_info()
        if not source_info:
            return
        
        # 分析受影响的设备和资产
        if source_info['type'] == 'device':
            self._analyze_network_impact(source_info['id'])
        elif source_info['type'] == 'asset':
            self._analyze_asset_impact(source_info['id'])
        
        # 生成处理建议
        self._generate_suggestions()
        
        # 保存分析结果
        self.save()
    
    def _analyze_network_impact(self, device_id):
        """分析网络设备故障影响"""
        from app.models.network import NetworkDevice
        
        device = NetworkDevice.find_by_id(device_id)
        if not device:
            return
        
        # 获取连接的设备
        affected_devices = []
        connected_device_ids = device.get_connected_devices()
        
        for connected_id in connected_device_ids:
            connected_device = NetworkDevice.find_by_id(connected_id)
            if connected_device:
                affected_devices.append({
                    'id': connected_device.id,
                    'name': connected_device.name,
                    'ip': connected_device.ip_address,
                    'type': connected_device.device_type
                })
        
        # 递归分析连接的设备的影响
        # 这里可以实现更复杂的网络拓扑分析算法
        
        import json
        self.affected_devices = json.dumps(affected_devices)
        self.device_count = len(affected_devices)
        
        # 根据影响范围确定影响级别
        if len(affected_devices) == 0:
            self.impact_level = '轻微'
        elif len(affected_devices) <= 5:
            self.impact_level = '中等'
        elif len(affected_devices) <= 20:
            self.impact_level = '严重'
        else:
            self.impact_level = '灾难'
    
    def _analyze_asset_impact(self, asset_id):
        """分析资产故障影响"""
        from app.models.asset import Asset
        
        asset = Asset.find_by_id(asset_id)
        if not asset:
            return
        
        # 分析同位置的其他资产
        affected_assets = []
        if asset.room_id:
            room_assets = Asset.query.filter_by(
                room_id=asset.room_id,
                is_deleted=False
            ).filter(Asset.id != asset_id).all()
            
            for room_asset in room_assets:
                affected_assets.append({
                    'id': room_asset.id,
                    'name': room_asset.name,
                    'code': room_asset.asset_code,
                    'category': room_asset.category
                })
        
        import json
        self.affected_assets = json.dumps(affected_assets)
        self.asset_count = len(affected_assets)
        
        # 评估影响级别
        if asset.category in ['服务器', '核心网络设备']:
            self.impact_level = '严重'
            self.service_interruption = True
        elif asset.category in ['工作站', '打印机']:
            self.impact_level = '中等'
        else:
            self.impact_level = '轻微'
    
    def _generate_suggestions(self):
        """生成处理建议"""
        suggestions = []
        
        # 根据影响级别生成建议
        if self.impact_level == '灾难':
            suggestions.extend([
                '立即启动应急响应程序',
                '通知所有相关部门和用户',
                '考虑启用备用系统',
                '联系厂商技术支持'
            ])
        elif self.impact_level == '严重':
            suggestions.extend([
                '优先处理，调配足够资源',
                '通知相关部门负责人',
                '准备临时替代方案'
            ])
        elif self.impact_level == '中等':
            suggestions.extend([
                '安排技术人员及时处理',
                '通知直接相关用户'
            ])
        else:
            suggestions.extend([
                '按正常流程处理',
                '记录问题便于后续分析'
            ])
        
        import json
        self.suggested_actions = json.dumps(suggestions)


class FaultProgress(BaseModel):
    """故障处理进度模型"""
    __tablename__ = 'fault_progress'
    
    fault_id = db.Column(db.Integer, db.ForeignKey('fault_record.id'), nullable=False, comment='故障ID')
    progress_time = db.Column(db.DateTime, default=datetime.utcnow, comment='进度时间')
    progress_type = db.Column(db.String(20), nullable=False, comment='进度类型：接受/分析/处理/测试/完成')
    description = db.Column(db.Text, nullable=False, comment='进度描述')
    operator_id = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='操作人ID')
    
    # 关联关系
    operator = db.relationship('User', backref=db.backref('fault_progress', lazy='dynamic'))
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        if self.operator:
            result['operator_name'] = self.operator.real_name or self.operator.username
        return result