"""
位置管理模型：楼宇、楼层、房间
"""
from app import db
from app.models.base import BaseModel


class Building(BaseModel):
    """楼宇模型"""
    __tablename__ = 'building_info'
    
    name = db.Column(db.String(100), nullable=False, comment='楼宇名称')
    code = db.Column(db.String(50), unique=True, nullable=False, comment='楼宇编码')
    address = db.Column(db.String(255), nullable=True, comment='地址')
    description = db.Column(db.Text, nullable=True, comment='描述')
    status = db.Column(db.Integer, default=1, nullable=False, comment='状态：0-禁用，1-启用')
    
    # 关联关系
    floors = db.relationship('Floor', backref='building', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        result['floor_count'] = self.floors.filter_by(is_deleted=False).count()
        return result


class Floor(BaseModel):
    """楼层模型"""
    __tablename__ = 'floor_info'
    
    building_id = db.Column(db.Integer, db.ForeignKey('building_info.id'), nullable=False, comment='楼宇ID')
    name = db.Column(db.String(50), nullable=False, comment='楼层名称')
    code = db.Column(db.String(50), nullable=False, comment='楼层编码')
    floor_number = db.Column(db.Integer, nullable=False, comment='楼层号')
    description = db.Column(db.Text, nullable=True, comment='描述')
    status = db.Column(db.Integer, default=1, nullable=False, comment='状态：0-禁用，1-启用')
    
    # 关联关系
    rooms = db.relationship('Room', backref='floor', lazy='dynamic', cascade='all, delete-orphan')
    
    # 添加联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('building_id', 'code', name='uk_floor_building_code'),
    )
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        result['building_name'] = self.building.name if self.building else None
        result['room_count'] = self.rooms.filter_by(is_deleted=False).count()
        return result


class Room(BaseModel):
    """房间模型"""
    __tablename__ = 'room_info'
    
    floor_id = db.Column(db.Integer, db.ForeignKey('floor_info.id'), nullable=False, comment='楼层ID')
    name = db.Column(db.String(50), nullable=False, comment='房间名称')
    code = db.Column(db.String(50), nullable=False, comment='房间编码')
    room_type = db.Column(db.String(50), nullable=True, comment='房间类型')
    area = db.Column(db.Numeric(10, 2), nullable=True, comment='面积(平方米)')
    capacity = db.Column(db.Integer, nullable=True, comment='容纳人数')
    description = db.Column(db.Text, nullable=True, comment='描述')
    status = db.Column(db.Integer, default=1, nullable=False, comment='状态：0-禁用，1-启用')
    
    # 添加联合唯一约束
    __table_args__ = (
        db.UniqueConstraint('floor_id', 'code', name='uk_room_floor_code'),
    )
    
    def to_dict(self, exclude_fields=None):
        """转换为字典"""
        result = super().to_dict(exclude_fields)
        if self.floor:
            result['floor_name'] = self.floor.name
            result['building_name'] = self.floor.building.name if self.floor.building else None
            result['building_id'] = self.floor.building_id
        return result
    
    @property
    def full_location(self):
        """完整位置信息"""
        if self.floor and self.floor.building:
            return f"{self.floor.building.name}-{self.floor.name}-{self.name}"
        return self.name