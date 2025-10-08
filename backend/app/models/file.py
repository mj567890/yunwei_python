"""
文件管理模型
"""
from app import db
from app.models.base import BaseModel


class FileInfo(BaseModel):
    """文件信息模型"""
    __tablename__ = 'file_info'
    
    # 文件基本信息
    filename = db.Column(db.String(255), nullable=False, comment='文件名')
    original_filename = db.Column(db.String(255), nullable=False, comment='原始文件名')
    file_path = db.Column(db.String(500), nullable=False, comment='文件路径')
    file_size = db.Column(db.Integer, nullable=True, comment='文件大小(字节)')
    file_type = db.Column(db.String(50), nullable=True, comment='文件类型')
    mime_type = db.Column(db.String(100), nullable=True, comment='MIME类型')
    file_hash = db.Column(db.String(64), nullable=True, comment='文件哈希')
    
    # 关联信息
    related_type = db.Column(db.String(50), nullable=True, comment='关联类型：asset/device/maintenance/fault')
    related_id = db.Column(db.Integer, nullable=True, comment='关联对象ID')
    
    # 上传信息
    upload_time = db.Column(db.DateTime, nullable=True, comment='上传时间')
    uploader_id = db.Column(db.Integer, db.ForeignKey('sys_user.id'), nullable=True, comment='上传人ID')
    
    # 文件状态
    status = db.Column(db.String(20), default='正常', comment='文件状态：正常/损坏/已删除')
    download_count = db.Column(db.Integer, default=0, comment='下载次数')
    
    # 描述信息
    description = db.Column(db.String(255), nullable=True, comment='文件描述')
    tags = db.Column(db.String(255), nullable=True, comment='标签')
    
    # 关联关系
    uploader = db.relationship('User', backref=db.backref('uploaded_files', lazy='dynamic'))
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        result['file_size_mb'] = round(self.file_size / 1024 / 1024, 2) if self.file_size else 0
        
        if self.uploader:
            result['uploader_name'] = self.uploader.real_name or self.uploader.username
            
        # 获取关联对象信息
        result['related_info'] = self.get_related_info()
        
        return result
    
    def get_related_info(self):
        """获取关联对象信息"""
        if not self.related_type or not self.related_id:
            return None
        
        try:
            if self.related_type == 'asset':
                from app.models.asset import Asset
                obj = Asset.find_by_id(self.related_id)
                if obj:
                    return {'name': obj.name, 'code': obj.asset_code}
            elif self.related_type == 'device':
                from app.models.network import NetworkDevice
                obj = NetworkDevice.find_by_id(self.related_id)
                if obj:
                    return {'name': obj.name, 'ip': obj.ip_address}
            elif self.related_type == 'maintenance':
                from app.models.maintenance import MaintenanceRecord
                obj = MaintenanceRecord.find_by_id(self.related_id)
                if obj:
                    return {'title': obj.title, 'type': obj.record_type}
            elif self.related_type == 'fault':
                from app.models.fault import FaultRecord
                obj = FaultRecord.find_by_id(self.related_id)
                if obj:
                    return {'title': obj.title, 'code': obj.fault_code}
        except:
            pass
        
        return None